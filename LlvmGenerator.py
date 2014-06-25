#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates LLVM IR code from SDL process models, allowing
    generation of a binary application without an intermediate language.
    LLVM also allows for various code verification, analysis, and optimization.

    The design is based on the Ada code generator. Check it for details.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import logging

from singledispatch import singledispatch
from llvm import core

import ogAST
import Helper

LOG = logging.getLogger(__name__)

__all__ = ['generate']


# Global state
g = None


class GlobalState():
    def __init__(self, process):
        self.name = str(process.processName)
        self.module = core.Module.new(self.name)
        self.dataview = process.dataview

        self.scope = Scope()
        self.global_scope = self.scope
        self.states = {}
        self.structs = {}
        self.strings = {}
        self.funcs = {}

        # Initialize built-in types
        self.i1 = core.Type.int(1)
        self.i8 = core.Type.int(8)
        self.i32 = core.Type.int(32)
        self.i64 = core.Type.int(64)
        self.void = core.Type.void()
        self.double = core.Type.double()
        self.i1_ptr = core.Type.pointer(self.i1)
        self.i8_ptr = core.Type.pointer(self.i8)
        self.i32_ptr = core.Type.pointer(self.i32)
        self.i64_ptr = core.Type.pointer(self.i64)
        self.double_ptr = core.Type.pointer(self.double)

        # Intialize built-in functions
        ty = core.Type.function(self.void, [core.Type.pointer(self.i8)], True)
        self.funcs['printf'] = self.module.add_function(ty, 'printf')

        self.funcs['memcpy'] = core.Function.intrinsic(
            self.module,
            core.INTR_MEMCPY,
            [self.i8_ptr, self.i8_ptr, self.i64]
        )

        self.funcs['powi'] = core.Function.intrinsic(
            self.module,
            core.INTR_POWI,
            [self.double]
        )

        self.funcs['fabs'] = core.Function.intrinsic(
            self.module,
            core.INTR_FABS,
            [self.double]
        )


class StructType():
    def __init__(self, name, field_names, field_types):
        self.name = name
        self.field_names = field_names
        self.ty = core.Type.struct(field_types, self.name)

    def idx(self, field_name):
        return self.field_names.index(field_name)


class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name, var):
        self.vars[name.lower()] = var

    def resolve(self, name):
        var = self.vars.get(name.lower())
        if var:
            return var
        if self.parent:
            return self.parent.resolve(name)
        else:
            print name
            raise NameError


@singledispatch
def generate(ast):
    ''' Generate the code for an item of the AST '''
    raise TypeError('[Backend] Unsupported AST construct')


# Processing of the AST
@generate.register(ogAST.Process)
def _process(process):
    ''' Generate LLVM IR code '''
    process_name = str(process.processName)
    LOG.info('Generating LLVM IR code for process ' + process_name)

    global g
    g = GlobalState(process)

    # In case model has nested states, flatten everything
    Helper.flatten(process)

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    # Initialize states enum
    for name in process.mapping.iterkeys():
        if not name.endswith('START'):
            cons = core.Constant.int(g.i32, len(g.states))
            g.states[name] = cons

    # Generate state var
    state_cons = g.module.add_global_variable(g.i32, 'state')
    state_cons.initializer = core.Constant.int(g.i32, -1)
    g.scope.define('state', state_cons)

    # Generare process-level vars
    for name, (ty, expr) in process.variables.viewitems():
        var_ty = _generate_type(ty)
        global_var = g.module.add_global_variable(var_ty, str(name))
        global_var.initializer = core.Constant.null(var_ty)
        g.scope.define(str(name).lower(), global_var)

    # Declare timer set/reset functions
    for timer in process.timers:
        # TODO: Should be uint?
        decl_func("set_%s" % str(timer), g.void, [g.i32_ptr], True)
        decl_func("reset_%s" % str(timer), g.void, [], True)

    # Declare output signal functions
    for signal in process.output_signals:
        if 'type' in signal:
            param_tys = [core.Type.pointer(_generate_type(signal['type']))]
        else:
            param_tys = []
        decl_func(str(signal['name']), g.void, param_tys, True)

    # Declare external procedures functions
    for proc in [proc for proc in process.procedures if proc.external]:
        param_tys = [core.Type.pointer(_generate_type(p['type'])) for p in proc.fpar]
        decl_func(str(proc.inputString), g.void, param_tys, True)

    # Generate internal procedures
    for proc in process.content.inner_procedures:
        generate(proc)

    # Generate process functions
    _generate_runtr_func(process)
    _generate_startup_func(process)

    # Generate input signals
    for signal in process.input_signals:
        _generate_input_signal(signal, mapping[signal['name']])

    g.module.verify()

    with open(g.name + '.ll', 'w') as ll_file:
        ll_file.write(str(g.module))


def _generate_runtr_func(process):
    ''' Generate code for the run_transition function '''
    func = decl_func('run_transition', g.void, [g.i32])

    _push_scope()

    entry_block = func.append_basic_block('entry')
    cond_block = func.append_basic_block('cond')
    body_block = func.append_basic_block('body')
    exit_block = func.append_basic_block('exit')

    g.builder = core.Builder.new(entry_block)

    # entry
    id_ptr = g.builder.alloca(g.i32, None, 'id')
    g.scope.define('id', id_ptr)
    g.builder.store(func.args[0], id_ptr)
    g.builder.branch(cond_block)

    # cond
    g.builder.position_at_end(cond_block)
    no_tr_cons = core.Constant.int(g.i32, -1)
    id_val = g.builder.load(id_ptr)
    cond_val = g.builder.icmp(core.ICMP_NE, id_val, no_tr_cons, 'cond')
    g.builder.cbranch(cond_val, body_block, exit_block)

    # body
    g.builder.position_at_end(body_block)
    switch = g.builder.switch(func.args[0], exit_block)

    # transitions
    for idx, tr in enumerate(process.transitions):
        tr_block = func.append_basic_block('tr%d' % idx)
        const = core.Constant.int(g.i32, idx)
        switch.add_case(const, tr_block)
        g.builder.position_at_end(tr_block)
        generate(tr)
        g.builder.branch(cond_block)

    # exit
    g.builder.position_at_end(exit_block)
    g.builder.ret_void()

    _pop_scope()

    func.verify()
    return func


def _generate_startup_func(process):
    ''' Generate code for the startup function '''
    func = decl_func(g.name + '_startup', g.void, [])

    _push_scope()

    entry_block = func.append_basic_block('entry')
    g.builder = core.Builder.new(entry_block)

    # Initialize process level variables
    for name, (ty, expr) in process.variables.viewitems():
        if expr:
            global_var = g.scope.resolve(str(name))
            generate_assign(global_var, expression(expr))

    g.builder.call(g.funcs['run_transition'], [core.Constant.int(g.i32, 0)])
    g.builder.ret_void()

    _pop_scope()

    func.verify()
    return func


def _generate_input_signal(signal, inputs):
    ''' Generate code for an input signal '''
    func_name = g.name + "_" + str(signal['name'])
    param_tys = []
    if 'type' in signal:
        param_tys.append(core.Type.pointer(_generate_type(signal['type'])))

    func = decl_func(func_name, g.void, param_tys)

    _push_scope()

    entry_block = func.append_basic_block('entry')
    exit_block = func.append_basic_block('exit')
    g.builder = core.Builder.new(entry_block)

    g_state_val = g.builder.load(g.global_scope.resolve('state'))
    switch = g.builder.switch(g_state_val, exit_block)

    for state_name, state_id in g.states.iteritems():
        state_block = func.append_basic_block('state_%s' % str(state_name))
        switch.add_case(state_id, state_block)
        g.builder.position_at_end(state_block)

        # TODO: Nested states

        input = inputs.get(state_name)
        if input:
            for var_name in input.parameters:
                var_ptr = g.scope.resolve(str(var_name))
                if is_struct_ptr(var_ptr):
                    generate_assign(var_ptr, func.args[0])
                else:
                    generate_assign(var_ptr, g.builder.load(func.args[0]))
            if input.transition:
                id_val = core.Constant.int(g.i32, input.transition_id)
                g.builder.call(g.funcs['run_transition'], [id_val])

        g.builder.ret_void()

    g.builder.position_at_end(exit_block)
    g.builder.ret_void()

    _pop_scope()

    func.verify()


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output):
    ''' Generate the code of a set of output or procedure call statement '''
    for out in output.output:
        name = out['outputName'].lower()

        if name == 'write':
            _generate_write(out['params'])
            continue
        elif name == 'writeln':
            _generate_writeln(out['params'])
            continue
        elif name == 'reset_timer':
            _generate_reset_timer(out['params'])
            continue
        elif name == 'set_timer':
            _generate_set_timer(out['params'])
            continue

        func = g.funcs[str(name).lower()]

        params = []
        for p in out.get('params', []):
            p_val = expression(p)
            # Pass by reference
            if p_val.type.kind != core.TYPE_POINTER:
                p_var = g.builder.alloca(p_val.type, None)
                g.builder.store(p_val, p_var)
                params.append(p_var)
            else:
                params.append(p_val)

        g.builder.call(func, params)


def _generate_write(params):
    ''' Generate the code for the write operator '''
    zero = core.Constant.int(g.i32, 0)
    for param in params:
        basic_ty = find_basic_type(param.exprType)
        expr_val = expression(param)

        if basic_ty.kind == 'IntegerType':
            fmt_val = _get_string_cons('% d')
            fmt_ptr = g.builder.gep(fmt_val, [zero, zero])
            g.builder.call(g.funcs['printf'], [fmt_ptr, expr_val])
        elif basic_ty.kind == 'RealType':
            fmt_val = _get_string_cons('% .14E')
            fmt_ptr = g.builder.gep(fmt_val, [zero, zero])
            g.builder.call(g.funcs['printf'], [fmt_ptr, expr_val])
        elif basic_ty.kind == 'BooleanType':
            true_str_val = _get_string_cons('TRUE')
            true_str_ptr = g.builder.gep(true_str_val, [zero, zero])
            false_str_val = _get_string_cons('FALSE')
            false_str_ptr = g.builder.gep(false_str_val, [zero, zero])
            str_ptr = g.builder.select(expr_val, true_str_ptr, false_str_ptr)
            g.builder.call(g.funcs['printf'], [str_ptr])
        elif basic_ty.kind == 'StringType':
            expr_ptr = g.builder.gep(expr_val, [zero, zero])
            g.builder.call(g.funcs['printf'], [expr_ptr])
        else:
            raise NotImplementedError


def _generate_writeln(params):
    ''' Generate the code for the writeln operator '''
    _generate_write(params)

    zero = core.Constant.int(g.i32, 0)
    str_cons = _get_string_cons('\n')
    str_ptr = g.builder.gep(str_cons, [zero, zero])
    g.builder.call(g.funcs['printf'], [str_ptr])


def _generate_reset_timer(params):
    ''' Generate the code for the reset timer operator '''
    timer_id = params[0]
    reset_func_name = 'reset_%s' % timer_id.value[0]
    reset_func = g.funcs[reset_func_name.lower()]

    g.builder.call(reset_func, [])


def _generate_set_timer(params):
    ''' Generate the code for the set timer operator '''
    timer_expr, timer_id = params
    set_func_name = 'set_%s' % timer_id.value[0]
    set_func = g.funcs[set_func_name.lower()]

    expr_val = expression(timer_expr)

    tmp_ptr = g.builder.alloca(expr_val.type)
    g.builder.store(expr_val, tmp_ptr)

    g.builder.call(set_func, [tmp_ptr])


@generate.register(ogAST.TaskAssign)
def _task_assign(task):
    ''' Generate the code of a list of assignments '''
    for expr in task.elems:
        expression(expr)


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task):
    ''' Generate comments for informal text '''
    pass


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task):
    ''' Generate the code for a for loop '''
    for loop in task.elems:
        if loop['range']:
            _generate_for_range(loop)
        else:
            _generate_for_iterable(loop)


def _generate_for_range(loop):
    ''' Generate the code for a for x in range loop '''
    func = g.builder.basic_block.function
    cond_block = func.append_basic_block('for:cond')
    body_block = func.append_basic_block('for:body')
    inc_block = func.append_basic_block('for:inc')
    end_block = func.append_basic_block('')

    _push_scope()

    loop_var = g.builder.alloca(g.i32, None, str(loop['var']))
    g.scope.define(str(loop['var']), loop_var)

    if loop['range']['start']:
        start_val = expression(loop['range']['start'])
        g.builder.store(start_val, loop_var)
    else:
        g.builder.store(core.Constant.int(g.i32, 0), loop_var)

    stop_val = expression(loop['range']['stop'])
    g.builder.branch(cond_block)

    g.builder.position_at_end(cond_block)
    loop_val = g.builder.load(loop_var)
    cond_val = g.builder.icmp(core.ICMP_SLT, loop_val, stop_val)
    g.builder.cbranch(cond_val, body_block, end_block)

    g.builder.position_at_end(body_block)
    generate(loop['transition'])
    g.builder.branch(inc_block)

    g.builder.position_at_end(inc_block)
    step_val = core.Constant.int(g.i32, loop['range']['step'])
    loop_val = g.builder.load(loop_var)
    temp_val = g.builder.add(loop_val, step_val)
    g.builder.store(temp_val, loop_var)
    g.builder.branch(cond_block)

    g.builder.position_at_end(end_block)

    _pop_scope()


def _generate_for_iterable(loop):
    ''' Generate the code for a for x in iterable loop'''
    raise NotImplementedError


@singledispatch
def reference(prim):
    ''' Generate a variable reference '''
    raise TypeError('Unsupported reference: ' + str(expr))


@reference.register(ogAST.PrimVariable)
def _prim_var_reference(prim):
    ''' Generate a primary variable reference '''
    return g.scope.resolve(str(prim.value[0]))


@reference.register(ogAST.PrimPath)
def _prim_path_reference(prim):
    ''' Generate a primary path reference '''
    var_name = prim.value.pop(0).lower()
    var_ptr = g.scope.resolve(str(var_name))

    if not prim.value:
        return var_ptr

    zero_cons = core.Constant.int(g.i32, 0)

    for field_name in prim.value:
        var_ty = var_ptr.type
        struct = g.structs[var_ty.pointee.name]
        field_idx_cons = core.Constant.int(g.i32, struct.idx(field_name.lower()))
        field_ptr = g.builder.gep(var_ptr, [zero_cons, field_idx_cons])
        var_ptr = field_ptr

    return var_ptr


@singledispatch
def expression(expr):
    ''' Generate the code for Expression-classes '''
    raise TypeError('Unsupported expression: ' + str(expr))


@expression.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Generate the code for a variable expression '''
    var_ptr = reference(prim)
    return var_ptr if is_struct_ptr(var_ptr) else g.builder.load(var_ptr)


@expression.register(ogAST.PrimPath)
def _prim_path(prim):
    ''' Generate the code for an of path expression '''
    specops_generators = {
        'length': generate_length,
        'present': generate_present,
        'abs': generate_abs,
        'fix': generate_fix,
        'float': generate_float,
        'power': generate_power
    }

    specop_generator = specops_generators.get(prim.value[0].lower())
    if specop_generator:
        return specop_generator(prim.value[1]['procParams'])

    var_ptr = reference(prim)
    return var_ptr if is_struct_ptr(var_ptr) else g.builder.load(var_ptr)


def generate_length(params):
    ''' Generate the code for the built-in length operation'''
    raise NotImplementedError


def generate_present(params):
    ''' Generate the code for the built-in present operation'''
    raise NotImplementedError


def generate_abs(params):
    ''' Generate the code for the built-in abs operation'''
    expr_val = expression(params[0])

    if expr_val.type.kind == core.TYPE_INTEGER:
        expr_conv = g.builder.sitofp(expr_val, g.double)
        res_val = g.builder.call(g.funcs['fabs'], [expr_conv])
        return g.builder.fptosi(res_val, g.i32)
    else:
        return g.builder.call(g.funcs['fabs'], [expr_val])


def generate_fix(params):
    ''' Generate the code for the built-in fix operation'''
    expr_val = expression(params[0])
    return g.builder.fptosi(expr_val, g.i32)


def generate_float(params):
    ''' Generate the code for the built-in float operation'''
    expr_val = expression(params[0])
    return g.builder.sitofp(expr_val, g.double)


def generate_power(params):
    ''' Generate the code for the built-in power operation'''
    left_val = expression(params[0])
    right_val = expression(params[1])

    if left_val.type.kind == core.TYPE_INTEGER:
        left_conv = g.builder.sitofp(left_val, g.double)
        res_val = g.builder.call(g.funcs['powi'], [left_conv, right_val])
        return g.builder.fptosi(res_val, g.i32)
    else:
        return g.builder.call(g.funcs['powi'], [left_val, right_val])


@expression.register(ogAST.ExprPlus)
@expression.register(ogAST.ExprMul)
@expression.register(ogAST.ExprMinus)
@expression.register(ogAST.ExprEq)
@expression.register(ogAST.ExprNeq)
@expression.register(ogAST.ExprGt)
@expression.register(ogAST.ExprGe)
@expression.register(ogAST.ExprLt)
@expression.register(ogAST.ExprLe)
@expression.register(ogAST.ExprDiv)
@expression.register(ogAST.ExprMod)
@expression.register(ogAST.ExprRem)
def _basic(expr):
    ''' Generate the code for an arithmetic of relational expression '''
    lefttmp = expression(expr.left)
    righttmp = expression(expr.right)

    if lefttmp.type.kind == core.TYPE_INTEGER:
        if expr.operand == '+':
            return g.builder.add(lefttmp, righttmp, 'addtmp')
        elif expr.operand == '-':
            return g.builder.sub(lefttmp, righttmp, 'subtmp')
        elif expr.operand == '*':
            return g.builder.mul(lefttmp, righttmp, 'multmp')
        elif expr.operand == '/':
            return g.builder.sdiv(lefttmp, righttmp, 'divtmp')
        elif expr.operand == 'mod':
            # l mod r == (((l rem r) + r) rem r)
            remtmp = g.builder.srem(lefttmp, righttmp)
            addtmp = g.builder.add(remtmp, righttmp)
            return g.builder.srem(addtmp, righttmp, 'modtmp')
        elif expr.operand == 'rem':
            return g.builder.srem(lefttmp, righttmp, 'remtmp')
        elif expr.operand == '<':
            return g.builder.icmp(core.ICMP_SLT, lefttmp, righttmp, 'lttmp')
        elif expr.operand == '<=':
            return g.builder.icmp(core.ICMP_SLE, lefttmp, righttmp, 'letmp')
        elif expr.operand == '=':
            return g.builder.icmp(core.ICMP_EQ, lefttmp, righttmp, 'eqtmp')
        elif expr.operand == '/=':
            return g.builder.icmp(core.ICMP_NE, lefttmp, righttmp, 'netmp')
        elif expr.operand == '>=':
            return g.builder.icmp(core.ICMP_SGE, lefttmp, righttmp, 'getmp')
        elif expr.operand == '>':
            return g.builder.icmp(core.ICMP_SGT, lefttmp, righttmp, 'gttmp')
        else:
            raise NotImplementedError
    elif lefttmp.type.kind == core.TYPE_DOUBLE:
        if expr.operand == '+':
            return g.builder.fadd(lefttmp, righttmp, 'addtmp')
        elif expr.operand == '-':
            return g.builder.fsub(lefttmp, righttmp, 'subtmp')
        elif expr.operand == '*':
            return g.builder.fmul(lefttmp, righttmp, 'multmp')
        elif expr.operand == '/':
            return g.builder.fdiv(lefttmp, righttmp, 'divtmp')
        elif expr.operand == '<':
            return g.builder.fcmp(core.FCMP_OLT, lefttmp, righttmp, 'lttmp')
        elif expr.operand == '<=':
            return g.builder.fcmp(core.FCMP_OLE, lefttmp, righttmp, 'letmp')
        elif expr.operand == '=':
            return g.builder.fcmp(core.FCMP_OEQ, lefttmp, righttmp, 'eqtmp')
        elif expr.operand == '/=':
            return g.builder.fcmp(core.FCMP_ONE, lefttmp, righttmp, 'netmp')
        elif expr.operand == '>=':
            return g.builder.fcmp(core.FCMP_OGE, lefttmp, righttmp, 'getmp')
        elif expr.operand == '>':
            return g.builder.fcmp(core.FCMP_OGT, lefttmp, righttmp, 'gttmp')
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


@expression.register(ogAST.ExprAssign)
def _assign(expr):
    ''' Generate the code for an assign expression '''
    generate_assign(reference(expr.left), expression(expr.right))


def generate_assign(left, right):
    ''' Generate code for an assign from two LLVM values'''
    # This is extracted as an standalone function because is used by
    # multiple generation rules
    if is_struct_ptr(left):
        size = core.Constant.sizeof(left.type.pointee)
        align = core.Constant.int(g.i32, 0)
        volatile = core.Constant.int(g.i1, 0)

        right_ptr = g.builder.bitcast(right, g.i8_ptr)
        left_ptr = g.builder.bitcast(left, g.i8_ptr)

        g.builder.call(g.funcs['memcpy'], [left_ptr, right_ptr, size, align, volatile])
    else:
        g.builder.store(right, left)


@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
def _logical(expr):
    ''' Generate the code for a logical expression '''
    lefttmp = expression(expr.left)
    righttmp = expression(expr.right)

    ty = find_basic_type(expr.exprType)
    if ty.kind != 'BooleanType':
        raise NotImplementedError

    if expr.operand == 'and':
        return g.builder.and_(lefttmp, righttmp, 'andtmp')
    elif expr.operand == 'or':
        return g.builder.or_(lefttmp, righttmp, 'ortmp')
    else:
        return g.builder.xor(lefttmp, righttmp, 'xortmp')


@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    raise NotImplementedError


@expression.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' Generate the code for an in expression '''
    raise NotImplementedError


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    enumerant = primary.value[0].replace('_', '-')
    basic_ty = find_basic_type(primary.exprType)
    return core.Constant.int(g.i32, basic_ty.EnumValues[enumerant].IntValue)


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    raise NotImplementedError


@expression.register(ogAST.PrimInteger)
def _integer(primary):
    ''' Generate code for a raw integer value  '''
    return core.Constant.int(g.i32, primary.value[0])


@expression.register(ogAST.PrimReal)
def _real(primary):
    ''' Generate code for a raw real value  '''
    return core.Constant.real(g.double, primary.value[0])


@expression.register(ogAST.PrimBoolean)
def _boolean(primary):
    ''' Generate code for a raw boolean value  '''
    if primary.value[0].lower() == 'true':
        return core.Constant.int(g.i1, 1)
    else:
        return core.Constant.int(g.i1, 0)


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    raise NotImplementedError


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    return _get_string_cons(str(primary.value[1:-1]))


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    raise NotImplementedError


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    raise NotImplementedError


@expression.register(ogAST.PrimIfThenElse)
def _if_then_else(ifthen):
    ''' Generate the code for ternary operator '''
    raise NotImplementedError


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Generate the code for an ASN.1 SEQUENCE '''
    struct = g.structs[seq.exprType.ReferencedTypeName]
    struct_ptr = g.builder.alloca(struct.ty)
    zero_cons = core.Constant.int(g.i32, 0)

    for field_name, field_expr in seq.value.viewitems():
        field_val = expression(field_expr)
        field_idx_cons = core.Constant.int(g.i32, struct.idx(field_name))
        field_ptr = g.builder.gep(struct_ptr, [zero_cons, field_idx_cons])
        g.builder.store(field_val, field_ptr)

    return struct_ptr


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Generate the code for an ASN.1 SEQUENCE OF '''
    ty = _generate_type(seqof.exprType)
    struct_ptr = g.builder.alloca(ty)
    zero_cons = core.Constant.int(g.i32, 0)
    array_ptr = g.builder.gep(struct_ptr, [zero_cons, zero_cons])

    for idx, expr in enumerate(seqof.value):
        idx_cons = core.Constant.int(g.i32, idx)
        expr_val = expression(expr)
        pos_ptr = g.builder.gep(array_ptr, [zero_cons, idx_cons])
        g.builder.store(expr_val, pos_ptr)

    return struct_ptr


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Generate the code for a CHOICE expression '''
    raise NotImplementedError


@generate.register(ogAST.Decision)
def _decision(dec):
    ''' Generate the code for a decision '''
    func = g.builder.basic_block.function

    ans_cond_blocks = [func.append_basic_block('ans_cond') for ans in dec.answers]
    end_block = func.append_basic_block('end')

    g.builder.branch(ans_cond_blocks[0])

    for idx, ans in enumerate(dec.answers):
        ans_cond_block = ans_cond_blocks[idx]
        if ans.transition:
            ans_tr_block = func.append_basic_block('ans_tr')
        g.builder.position_at_end(ans_cond_block)

        if ans.kind == 'constant':
            next_block = ans_cond_blocks[idx+1] if idx < len(ans_cond_blocks)-1 else end_block

            expr = ans.openRangeOp()
            expr.left = dec.question
            expr.right = ans.constant
            expr_val = expression(expr)

            true_cons = core.Constant.int(g.i1, 1)
            cond_val = g.builder.icmp(core.ICMP_EQ, expr_val, true_cons)
            g.builder.cbranch(cond_val, ans_tr_block if ans.transition else end_block, next_block)
        elif ans.kind == 'else':
            if ans.transition:
                g.builder.branch(ans_tr_block)
            else:
                g.builder.branch(end_block)
        else:
            raise NotImplementedError

        if ans.transition:
            g.builder.position_at_end(ans_tr_block)
            generate(ans.transition)
            g.builder.branch(end_block)

    g.builder.position_at_end(end_block)


@generate.register(ogAST.Label)
def _label(tr):
    ''' TGenerate the code for a Label '''
    raise NotImplementedError


@generate.register(ogAST.Transition)
def _transition(tr):
    ''' Generate the code for a transition '''
    for action in tr.actions:
        generate(action)
        if isinstance(action, ogAST.Label):
            return
    if tr.terminator:
        _generate_terminator(tr.terminator)


def _generate_terminator(term):
    ''' Generate the code for a transition termiantor '''
    if term.label:
        raise NotImplementedError
    if term.kind == 'next_state':
        state = term.inputString.lower()
        if state.strip() != '-':
            next_id_cons = core.Constant.int(g.i32, term.next_id)
            g.builder.store(next_id_cons, g.scope.resolve('id'))
            if term.next_id == -1:
                state_ptr = g.global_scope.resolve('state')
                state_id_cons = g.states[state]
                g.builder.store(state_id_cons, state_ptr)
        else:
            raise NotImplementedError
    elif term.kind == 'join':
        raise NotImplementedError
    elif term.kind == 'stop':
        raise NotImplementedError
    elif term.kind == 'return':
        if term.next_id == -1 and term.return_expr:
            g.builder.ret(expression(term.return_expr))
        elif term.next_id == -1:
            g.builder.ret_void()
        else:
            next_id_cons = core.Constant.int(g.i32, term.next_id)
            g.builder.store(next_id_cons, g.scope.resolve('id'))
            g.builder.ret_void()


@generate.register(ogAST.Floating_label)
def _floating_label(label):
    ''' Generate the code for a floating label '''
    raise NotImplementedError


@generate.register(ogAST.Procedure)
def _inner_procedure(proc):
    ''' Generate the code for a procedure '''
    param_tys = [core.Type.pointer(_generate_type(p['type'])) for p in proc.fpar]
    func = decl_func(str(proc.inputString), g.void, param_tys)

    _push_scope()

    for arg, param in zip(func.args, proc.fpar):
        g.scope.define(str(param['name']), arg)

    entry_block = func.append_basic_block('entry')
    g.builder = core.Builder.new(entry_block)

    for name, (ty, expr) in proc.variables.viewitems():
        raise NotImplementedError

    generate(proc.content.start.transition)

    for label in proc.content.floating_labels:
        raise NotImplementedError

    _pop_scope()

    func.verify()


def _generate_type(ty):
    ''' Generate the equivalent LLVM type of a ASN.1 type '''
    basic_ty = find_basic_type(ty)
    if basic_ty.kind == 'IntegerType':
        return g.i32
    elif basic_ty.kind == 'BooleanType':
        return g.i1
    elif basic_ty.kind == 'RealType':
        return g.double
    elif basic_ty.kind == 'SequenceOfType':
        if ty.ReferencedTypeName in g.structs:
            return g.structs[ty.ReferencedTypeName].ty

        min_size = int(basic_ty.Max)
        max_size = int(basic_ty.Min)
        if min_size != max_size:
            raise NotImplementedError

        elem_ty = _generate_type(basic_ty.type)
        array_ty = core.Type.array(elem_ty, max_size)
        struct = StructType(ty.ReferencedTypeName, ['_'], [array_ty])
        g.structs[ty.ReferencedTypeName] = struct
        return struct.ty
    elif basic_ty.kind == 'SequenceType':
        if ty.ReferencedTypeName in g.structs:
            return g.structs[ty.ReferencedTypeName].ty

        field_names = []
        field_types = []
        for field_name in Helper.sorted_fields(basic_ty):
            field_names.append(field_name.replace('-', '_'))
            field_types.append(_generate_type(basic_ty.Children[field_name].type))

        struct = StructType(ty.ReferencedTypeName, field_names, field_types)
        g.structs[ty.ReferencedTypeName] = struct
        return struct.ty
    elif basic_ty.kind == 'EnumeratedType':
        return g.i32
    else:
        raise NotImplementedError


def _push_scope():
    ''' Push a new scope '''
    g.scope = Scope(g.scope)


def _pop_scope():
    ''' Pop the current scope '''
    g.scope = g.scope.parent


def _get_string_cons(str):
    ''' Returns a reference to a global string constant with the given value '''
    if str in g.strings:
        return g.strings[str]

    str_val = core.Constant.stringz(str)
    gvar_name = '.str%s' % len(g.strings)
    gvar_val = g.module.add_global_variable(str_val.type, gvar_name)
    gvar_val.initializer = str_val
    g.strings[str] = gvar_val
    return gvar_val


def decl_func(name, return_ty, param_tys, extern=False):
    ''' Declare a function '''
    func_ty = core.Type.function(return_ty, param_tys)
    func_name = ("%s_RI_%s" % (g.name, name)) if extern else name
    func = core.Function.new(g.module, func_ty, func_name)
    g.funcs[name.lower()] = func
    return func


def is_struct_ptr(val):
    return val.type.kind == core.TYPE_POINTER and val.type.pointee.kind == core.TYPE_STRUCT


# TODO: Refactor this into the helper module
def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in g.dataview.viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = g.dataview[typename].type
                break
    return basic_type
