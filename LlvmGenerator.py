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
from llvm import core, ee

import ogAST
import Helper

LOG = logging.getLogger(__name__)

__all__ = ['generate']


# Global context
ctx = None


class Context():
    def __init__(self, process):
        self.name = str(process.processName)
        self.module = core.Module.new(self.name)
        self.target_data = ee.TargetData.new(self.module.data_layout)
        self.dataview = process.dataview

        self.scope = Scope()
        self.global_scope = self.scope
        self.states = {}
        self.enums = {}
        self.structs = {}
        self.unions = {}
        self.strings = {}
        self.funcs = {}
        self.lltypes = {}

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

        # Initialize common constants
        self.zero = core.Constant.int(self.i32, 0)
        self.one = core.Constant.int(self.i32, 1)

        # Intialize built-in functions
        ty = core.Type.function(self.void, [self.i8_ptr], True)
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

    def open_scope(self):
        ''' Open a scope '''
        self.scope = Scope(self.scope)

    def close_scope(self):
        ''' Close the current scope '''
        self.scope = self.scope.parent

    def type_of(self, asn1ty):
        ''' Return the LL type of a ASN.1 type '''
        try:
            name = asn1ty.ReferencedTypeName.replace('-', '_')
        except AttributeError:
            name = None

        if name and name in self.lltypes:
            return self.lltypes[name]

        basic_asn1ty = find_basic_type(asn1ty)

        if basic_asn1ty.kind == 'IntegerType':
            llty = ctx.i64
        elif basic_asn1ty.kind == 'Integer32Type':
            llty = ctx.i32
        elif basic_asn1ty.kind == 'BooleanType':
            llty = ctx.i1
        elif basic_asn1ty.kind == 'RealType':
            llty = ctx.double
        elif basic_asn1ty.kind == 'SequenceOfType':
            llty = self._type_of_sequenceof(name, basic_asn1ty)
        elif basic_asn1ty.kind == 'SequenceType':
            llty = self._type_of_sequence(name, basic_asn1ty)
        elif basic_asn1ty.kind == 'EnumeratedType':
            llty = ctx.i32
        elif basic_asn1ty.kind == 'ChoiceType':
            llty = self._type_of_choice(name, basic_asn1ty)
        elif basic_asn1ty.kind == 'OctetStringType':
            llty = self._type_of_octetstring(name, basic_asn1ty)
        elif basic_asn1ty.kind in ('StringType', 'StandardStringType'):
            llty = ctx.i8_ptr
        else:
            raise NotImplementedError

        if name:
            self.lltypes[name] = llty

        return llty

    def _type_of_sequenceof(self, name, sequenceof_ty):
        ''' Return the LL type of a SequenceOf ASN.1 type '''
        min_size = int(sequenceof_ty.Min)
        max_size = int(sequenceof_ty.Max)
        is_variable_size = min_size != max_size

        elem_ty = self.type_of(sequenceof_ty.type)
        array_ty = core.Type.array(elem_ty, max_size)

        if is_variable_size:
            struct = self.decl_struct(['nCount', 'arr'], [ctx.i32, array_ty], name)
        else:
            struct = self.decl_struct(['arr'], [array_ty], name)

        struct_ptr = core.Type.pointer(struct.ty)
        self.decl_func("%s_Equal" % name, self.i1, [struct_ptr, struct_ptr])

        return struct.ty

    def _type_of_sequence(self, name, sequence_ty):
        ''' Return the LL type of a Sequence ASN.1 type '''
        field_names = []
        field_types = []

        for field_name in Helper.sorted_fields(sequence_ty):
            field_names.append(field_name.replace('-', '_'))
            field_types.append(self.type_of(sequence_ty.Children[field_name].type))

        struct = self.decl_struct(field_names, field_types, name)

        struct_ptr = core.Type.pointer(struct.ty)
        self.decl_func("%s_Equal" % name, self.i1, [struct_ptr, struct_ptr])

        return struct.ty

    def _type_of_choice(self, name, choice_ty):
        ''' Return the equivalent LL type of a Choice ASN.1 type '''
        field_names = []
        field_types = []

        for idx, field_name in enumerate(Helper.sorted_fields(choice_ty)):
            # enum values used in choice determinant/present
            self.enums[field_name.replace('-', '_')] = core.Constant.int(self.i32, idx)

            field_names.append(field_name.replace('-', '_'))
            field_types.append(self.type_of(choice_ty.Children[field_name].type))

        union = self.decl_union(field_names, field_types, name)

        union_ptr = core.Type.pointer(union.ty)
        self.decl_func("%s_Equal" % name, self.i1, [union_ptr, union_ptr])

        return union.ty

    def _type_of_octetstring(self, name, octetstring_ty):
        ''' Return the equivalent LL type of a OcterString ASN.1 type '''
        min_size = int(octetstring_ty.Min)
        max_size = int(octetstring_ty.Max)
        is_variable_size = min_size != max_size

        array_ty = core.Type.array(ctx.i8, max_size)

        if is_variable_size:
            struct = self.decl_struct(['nCount', 'arr'], [ctx.i32, array_ty], name)
        else:
            struct = self.decl_struct(['arr'], [array_ty], name)

        struct_ptr = core.Type.pointer(struct.ty)
        self.decl_func("%s_Equal" % name, self.i1, [struct_ptr, struct_ptr])

        return struct.ty

    def string_ptr(self, str):
        ''' Returns a pointer to a global string with the given value '''
        if str in self.strings:
            return self.strings[str].gep([self.zero, self.zero])

        str_val = core.Constant.stringz(str)
        var_name = '.str%s' % len(self.strings)
        var_ptr = self.module.add_global_variable(str_val.type, var_name)
        var_ptr.initializer = str_val
        self.strings[str] = var_ptr
        return var_ptr.gep([self.zero, self.zero])

    def decl_func(self, name, return_ty, param_tys, extern=False):
        ''' Declare a function '''
        func_ty = core.Type.function(return_ty, param_tys)
        func_name = ("%s_RI_%s" % (self.name, name)) if extern else name
        func = core.Function.new(self.module, func_ty, func_name)
        self.funcs[name.lower()] = func
        return func

    def decl_struct(self, field_names, field_types, name=None):
        ''' Declare a struct '''
        name = name if name else "struct.%s" % len(self.structs)
        name = name.replace('-', '_')
        struct = StructType(name, field_names, field_types)
        self.structs[name] = struct
        return struct

    def resolve_struct(self, name):
        ''' Return the struct associated to a name '''
        return self.structs[name.replace('-', '_')]

    def decl_union(self, field_names, field_types, name=None):
        name = name if name else "union.%s" % len(self.structs)
        name = name.replace('-', '_')
        union = UnionType(name, field_names, field_types)
        self.unions[name] = union
        return union

    def resolve_union(self, name):
        ''' Return the union associated to a name '''
        return self.unions[name.replace('-', '_')]


class StructType():
    def __init__(self, name, field_names, field_types):
        self.name = name
        self.field_names = field_names
        self.ty = core.Type.struct(field_types, self.name)

    def idx(self, field_name):
        return self.field_names.index(field_name)


class UnionType():
    def __init__(self, name, field_names, field_types):
        self.name = name
        self.field_names = field_names
        self.field_types = field_types
        # Unions are represented a struct with a field indicating the index of its type
        # and a byte array with the size of the biggest type in the union
        self.size = max([ctx.target_data.size(ty) for ty in field_types])
        self.ty = core.Type.struct([ctx.i32, core.Type.array(ctx.i8, self.size)], name)

    def kind(self, name):
        idx = self.field_names.index(name)
        return (idx, self.field_types[idx])


class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.labels = {}
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
            raise NameError("name '%s' is not defined" % name)

    def label(self, name):
        name = name.lower()
        label_block = self.labels.get(name)
        if not label_block:
            func = ctx.builder.basic_block.function
            label_block = func.append_basic_block(name)
            self.labels[name] = label_block
        return label_block


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

    global ctx
    ctx = Context(process)

    # In case model has nested states, flatten everything
    Helper.flatten(process)

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    # Initialize states
    for name, val in process.mapping.viewitems():
        if not name.endswith('START'):
            cons_val = core.Constant.int(ctx.i32, len(ctx.states))
            ctx.states[name.lower()] = cons_val
        elif name != 'START':
            cons_val = core.Constant.int(ctx.i32, val)
            ctx.states[name.lower()] = cons_val

    # Generate state var
    state_cons = ctx.module.add_global_variable(ctx.i32, '.state')
    state_cons.initializer = core.Constant.int(ctx.i32, -1)
    ctx.scope.define('.state', state_cons)

    # Generare process-level vars
    for name, (ty, expr) in process.variables.viewitems():
        var_ty = ctx.type_of(ty)
        global_var = ctx.module.add_global_variable(var_ty, str(name))
        global_var.initializer = core.Constant.null(var_ty)
        ctx.scope.define(str(name).lower(), global_var)

    # Declare set/reset timer functions
    for timer in process.timers:
        # TODO: Should be uint?
        ctx.decl_func("set_%s" % str(timer), ctx.void, [ctx.i64_ptr], True)
        ctx.decl_func("reset_%s" % str(timer), ctx.void, [], True)

    # Declare output signal functions
    for signal in process.output_signals:
        if 'type' in signal:
            param_tys = [core.Type.pointer(ctx.type_of(signal['type']))]
        else:
            param_tys = []
        ctx.decl_func(str(signal['name']), ctx.void, param_tys, True)

    # Declare external procedures functions
    for proc in [proc for proc in process.procedures if proc.external]:
        param_tys = [core.Type.pointer(ctx.type_of(p['type'])) for p in proc.fpar]
        ctx.decl_func(str(proc.inputString), ctx.void, param_tys, True)

    # Generate internal procedures
    for proc in process.content.inner_procedures:
        generate(proc)

    # Generate process functions
    generate_runtr_func(process)
    generate_startup_func(process)

    # Generate input signals
    for signal in process.input_signals:
        generate_input_signal(signal, mapping[signal['name']])

    # Generate timer signal
    for timer in process.timers:
        generate_input_signal({'name': timer.lower()}, mapping[timer])

    ctx.module.verify()

    with open(ctx.name + '.ll', 'w') as ll_file:
        ll_file.write(str(ctx.module))


def generate_runtr_func(process):
    ''' Generate code for the run_transition function '''
    func = ctx.decl_func('run_transition', ctx.void, [ctx.i32])

    ctx.open_scope()

    entry_block = func.append_basic_block('entry')
    cond_block = func.append_basic_block('cond')
    body_block = func.append_basic_block('body')
    exit_block = func.append_basic_block('exit')

    ctx.builder = core.Builder.new(entry_block)

    # entry
    id_ptr = ctx.builder.alloca(ctx.i32, None, 'id')
    ctx.scope.define('id', id_ptr)
    ctx.builder.store(func.args[0], id_ptr)
    ctx.builder.branch(cond_block)

    # cond
    ctx.builder.position_at_end(cond_block)
    no_tr_cons = core.Constant.int(ctx.i32, -1)
    id_val = ctx.builder.load(id_ptr)
    cond_val = ctx.builder.icmp(core.ICMP_NE, id_val, no_tr_cons, 'cond')
    ctx.builder.cbranch(cond_val, body_block, exit_block)

    # body
    ctx.builder.position_at_end(body_block)
    switch = ctx.builder.switch(id_val, exit_block)

    # transitions
    for idx, tr in enumerate(process.transitions):
        tr_block = func.append_basic_block('tr%d' % idx)
        const = core.Constant.int(ctx.i32, idx)
        switch.add_case(const, tr_block)
        ctx.builder.position_at_end(tr_block)
        generate(tr)
        if not ctx.builder.basic_block.terminator:
            ctx.builder.branch(cond_block)

    # exit
    ctx.builder.position_at_end(exit_block)
    ctx.builder.ret_void()

    Helper.inner_labels_to_floating(process)
    for label in process.content.floating_labels:
        generate(label)

    # TODO: Use defined cond_block instead?
    next_tr_label_block = ctx.scope.label('next_transition')
    ctx.builder.position_at_end(next_tr_label_block)
    ctx.builder.branch(cond_block)

    ctx.close_scope()

    func.verify()
    return func


def generate_startup_func(process):
    ''' Generate code for the startup function '''
    func = ctx.decl_func(ctx.name + '_startup', ctx.void, [])

    ctx.open_scope()

    entry_block = func.append_basic_block('entry')
    ctx.builder = core.Builder.new(entry_block)

    # Initialize process level variables
    for name, (ty, expr) in process.variables.viewitems():
        if expr:
            global_var = ctx.scope.resolve(str(name))
            generate_assign(global_var, expression(expr))

    ctx.builder.call(ctx.funcs['run_transition'], [core.Constant.int(ctx.i32, 0)])
    ctx.builder.ret_void()

    ctx.close_scope()

    func.verify()
    return func


def generate_input_signal(signal, inputs):
    ''' Generate code for an input signal '''
    func_name = ctx.name + "_" + str(signal['name'])
    param_tys = []
    if 'type' in signal:
        param_tys.append(core.Type.pointer(ctx.type_of(signal['type'])))

    func = ctx.decl_func(func_name, ctx.void, param_tys)

    ctx.open_scope()

    entry_block = func.append_basic_block('entry')
    exit_block = func.append_basic_block('exit')
    ctx.builder = core.Builder.new(entry_block)

    g_state_val = ctx.builder.load(ctx.global_scope.resolve('.state'))
    switch = ctx.builder.switch(g_state_val, exit_block)

    for state_name, state_id in ctx.states.iteritems():
        if state_name.endswith('start'):
            continue
        state_block = func.append_basic_block('state_%s' % str(state_name))
        switch.add_case(state_id, state_block)
        ctx.builder.position_at_end(state_block)

        # TODO: Nested states

        input = inputs.get(state_name)
        if input:
            for var_name in input.parameters:
                var_ptr = ctx.scope.resolve(str(var_name))
                if is_struct_ptr(var_ptr) or is_array_ptr(var_ptr):
                    generate_assign(var_ptr, func.args[0])
                else:
                    generate_assign(var_ptr, ctx.builder.load(func.args[0]))
            if input.transition:
                id_val = core.Constant.int(ctx.i32, input.transition_id)
                ctx.builder.call(ctx.funcs['run_transition'], [id_val])

        ctx.builder.ret_void()

    ctx.builder.position_at_end(exit_block)
    ctx.builder.ret_void()

    ctx.close_scope()

    func.verify()


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output):
    ''' Generate the code of a set of output or procedure call statement '''
    for out in output.output:
        name = out['outputName'].lower()

        if name == 'write':
            generate_write(out['params'])
            continue
        elif name == 'writeln':
            generate_writeln(out['params'])
            continue
        elif name == 'reset_timer':
            generate_reset_timer(out['params'])
            continue
        elif name == 'set_timer':
            generate_set_timer(out['params'])
            continue

        func = ctx.funcs[str(name).lower()]

        params = []
        for p in out.get('params', []):
            p_val = expression(p)
            # Pass by reference
            if p_val.type.kind != core.TYPE_POINTER:
                p_var = ctx.builder.alloca(p_val.type, None)
                ctx.builder.store(p_val, p_var)
                params.append(p_var)
            else:
                params.append(p_val)

        ctx.builder.call(func, params)


def generate_write(params):
    ''' Generate the code for the write operator '''
    for param in params:
        basic_ty = find_basic_type(param.exprType)
        expr_val = expression(param)

        if basic_ty.kind in ['IntegerType', 'Integer32Type']:
            fmt_str_ptr = ctx.string_ptr('% d')
            ctx.builder.call(ctx.funcs['printf'], [fmt_str_ptr, expr_val])
        elif basic_ty.kind == 'RealType':
            fmt_str_ptr = ctx.string_ptr('% .14E')
            ctx.builder.call(ctx.funcs['printf'], [fmt_str_ptr, expr_val])
        elif basic_ty.kind == 'BooleanType':
            true_str_ptr = ctx.string_ptr('TRUE')
            false_str_ptr = ctx.string_ptr('FALSE')
            str_ptr = ctx.builder.select(expr_val, true_str_ptr, false_str_ptr)
            ctx.builder.call(ctx.funcs['printf'], [str_ptr])
        elif basic_ty.kind in ('StringType', 'StandardStringType'):
            fmt_str_ptr = ctx.string_ptr('%s')
            ctx.builder.call(ctx.funcs['printf'], [fmt_str_ptr, expr_val])
        elif basic_ty.kind == 'OctetStringType':
            fmt_str_ptr = ctx.string_ptr('%.*s')
            if basic_ty.Min == basic_ty.Max:
                arr_ptr = ctx.builder.gep(expr_val, [ctx.zero, ctx.zero])
                count_val = core.Constant.int(ctx.i32, arr_ptr.type.pointee.count)
            else:
                count_val = ctx.builder.load(ctx.builder.gep(expr_val, [ctx.zero, ctx.zero]))
                arr_ptr = ctx.builder.gep(expr_val, [ctx.zero, ctx.one])
            ctx.builder.call(ctx.funcs['printf'], [fmt_str_ptr, count_val, arr_ptr])
        else:
            raise NotImplementedError


def generate_writeln(params):
    ''' Generate the code for the writeln operator '''
    generate_write(params)

    str_ptr = ctx.string_ptr('\n')
    ctx.builder.call(ctx.funcs['printf'], [str_ptr])


def generate_reset_timer(params):
    ''' Generate the code for the reset timer operator '''
    timer_id = params[0]
    reset_func_name = 'reset_%s' % timer_id.value[0]
    reset_func = ctx.funcs[reset_func_name.lower()]

    ctx.builder.call(reset_func, [])


def generate_set_timer(params):
    ''' Generate the code for the set timer operator '''
    timer_expr, timer_id = params
    set_func_name = 'set_%s' % timer_id.value[0]
    set_func = ctx.funcs[set_func_name.lower()]

    expr_val = expression(timer_expr)

    tmp_ptr = ctx.builder.alloca(expr_val.type)
    ctx.builder.store(expr_val, tmp_ptr)

    ctx.builder.call(set_func, [tmp_ptr])


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
            generate_for_range(loop)
        else:
            generate_for_iterable(loop)


def generate_for_range(loop):
    ''' Generate the code for a for x in range loop '''
    func = ctx.builder.basic_block.function
    cond_block = func.append_basic_block('for:cond')
    body_block = func.append_basic_block('for:body')
    inc_block = func.append_basic_block('for:inc')
    end_block = func.append_basic_block('')

    ctx.open_scope()

    loop_var = ctx.builder.alloca(ctx.i64, None, str(loop['var']))
    ctx.scope.define(str(loop['var']), loop_var)

    if loop['range']['start']:
        start_val = expression(loop['range']['start'])
        ctx.builder.store(start_val, loop_var)
    else:
        ctx.builder.store(core.Constant.int(ctx.i64, 0), loop_var)

    stop_val = expression(loop['range']['stop'])
    ctx.builder.branch(cond_block)

    ctx.builder.position_at_end(cond_block)
    loop_val = ctx.builder.load(loop_var)
    cond_val = ctx.builder.icmp(core.ICMP_SLT, loop_val, stop_val)
    ctx.builder.cbranch(cond_val, body_block, end_block)

    ctx.builder.position_at_end(body_block)
    generate(loop['transition'])
    ctx.builder.branch(inc_block)

    ctx.builder.position_at_end(inc_block)
    step_val = core.Constant.int(ctx.i64, loop['range']['step'])
    loop_val = ctx.builder.load(loop_var)
    temp_val = ctx.builder.add(loop_val, step_val)
    ctx.builder.store(temp_val, loop_var)
    ctx.builder.branch(cond_block)

    ctx.builder.position_at_end(end_block)

    ctx.close_scope()


def generate_for_iterable(loop):
    ''' Generate the code for a for x in iterable loop'''
    seqof_asn1ty = find_basic_type(loop['list'].exprType)
    is_variable_size = seqof_asn1ty.Min != seqof_asn1ty.Max

    func = ctx.builder.basic_block.function

    # block for loading the value from the secuence
    # at the current index, incrementing the index afterwards
    load_block = func.append_basic_block('forin:load')
    # block for the body of the loop
    body_block = func.append_basic_block('forin:body')
    # block for checking if should loop again or terminate
    cond_block = func.append_basic_block('forin:cond')
    end_block = func.append_basic_block('')

    ctx.open_scope()

    idx_ptr = ctx.builder.alloca(ctx.i32)
    ctx.builder.store(core.Constant.int(ctx.i32, 0), idx_ptr)
    seqof_struct_ptr = expression(loop['list'])

    if is_variable_size:
        # In variable size SequenceOfs the array values are in the second field
        array_ptr = ctx.builder.gep(seqof_struct_ptr, [ctx.zero, ctx.one])
    else:
        array_ptr = ctx.builder.gep(seqof_struct_ptr, [ctx.zero, ctx.zero])

    element_typ = array_ptr.type.pointee.element

    if is_variable_size:
        # load the current number of elements that is on the first field
        end_idx = ctx.builder.load(ctx.builder.gep(seqof_struct_ptr, [ctx.zero, ctx.zero]))
    else:
        end_idx = core.Constant.int(ctx.i32, array_ptr.type.pointee.count)

    var_ptr = ctx.builder.alloca(element_typ, None, str(loop['var']))
    ctx.scope.define(str(loop['var']), var_ptr)

    ctx.builder.branch(load_block)

    # load block
    ctx.builder.position_at_end(load_block)
    idx_var = ctx.builder.load(idx_ptr)
    if element_typ.kind == core.TYPE_STRUCT:
        generate_assign(var_ptr, ctx.builder.gep(array_ptr, [ctx.zero, idx_var]))
    else:
        generate_assign(var_ptr, ctx.builder.load(ctx.builder.gep(array_ptr, [ctx.zero, idx_var])))
    ctx.builder.branch(body_block)

    # body block
    ctx.builder.position_at_end(body_block)
    generate(loop['transition'])
    ctx.builder.branch(cond_block)

    # cond block
    ctx.builder.position_at_end(cond_block)
    tmp_val = ctx.builder.add(idx_var, ctx.one)
    ctx.builder.store(tmp_val, idx_ptr)
    cond_val = ctx.builder.icmp(core.ICMP_SLT, tmp_val, end_idx)
    ctx.builder.cbranch(cond_val, load_block, end_block)

    ctx.builder.position_at_end(end_block)

    ctx.close_scope()


@singledispatch
def reference(prim):
    ''' Generate a reference '''
    raise TypeError('Unsupported reference: ' + str(prim))


@reference.register(ogAST.PrimVariable)
def _prim_var_reference(prim):
    ''' Generate a variable reference '''
    return ctx.scope.resolve(str(prim.value[0]))


@reference.register(ogAST.PrimSelector)
def _prim_selector_reference(prim):
    ''' Generate a field selector referece '''
    receiver_ptr = reference(prim.value[0])
    field_name = prim.value[1]

    if receiver_ptr.type.pointee.name in ctx.structs:
        struct = ctx.structs[receiver_ptr.type.pointee.name]
        field_idx_cons = core.Constant.int(ctx.i32, struct.idx(field_name))
        return ctx.builder.gep(receiver_ptr, [ctx.zero, field_idx_cons])

    else:
        union = ctx.unions[receiver_ptr.type.pointee.name]
        _, field_ty = union.kind(field_name)
        field_ptr = ctx.builder.gep(receiver_ptr, [ctx.zero, ctx.one])
        return ctx.builder.bitcast(field_ptr, core.Type.pointer(field_ty))


@reference.register(ogAST.PrimIndex)
def _prim_index_reference(prim):
    ''' Generate an index reference '''
    receiver_ptr = reference(prim.value[0])
    idx_val = expression(prim.value[1]['index'][0])

    array_ptr = ctx.builder.gep(receiver_ptr, [ctx.zero, ctx.zero])

    # TODO: Refactor this
    if array_ptr.type.pointee.kind != core.TYPE_ARRAY:
        # If is not an array this is a pointer to a variable size SeqOf
        # The array is in the second field of the struct
        return ctx.builder.gep(receiver_ptr, [ctx.zero, ctx.one, idx_val])
    else:
        return ctx.builder.gep(receiver_ptr, [ctx.zero, ctx.zero, idx_val])


@singledispatch
def expression(expr):
    ''' Generate the code for Expression-classes '''
    raise TypeError('Unsupported expression: ' + str(expr))


@expression.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Generate the code for a variable expression '''
    var_ptr = reference(prim)
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimSelector)
def _primary_selector(prim):
    ''' Generate the code for a Selector expression '''
    var_ptr = reference(prim)
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimIndex)
def _primary_index(prim):
    ''' Generate the code for an Index expression '''
    var_ptr = reference(prim)
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimSubstring)
def _primary_substring(prim):
    ''' Generate the code for a Substring expression '''
    bty = find_basic_type(prim.exprType)
    if bty.Min == bty.Max:
        raise NotImplementedError

    range_l_val = expression(prim.value[1]['substring'][0])
    range_r_val = expression(prim.value[1]['substring'][1])
    len_val = ctx.builder.sub(range_r_val, range_l_val)

    recvr_ptr = expression(prim.value[0])
    recvr_arr_ptr = ctx.builder.gep(recvr_ptr, [ctx.zero, ctx.one, range_l_val])

    recvr_ty = recvr_ptr.type.pointee
    elem_ty = recvr_ty.elements[1].element

    res_ptr = ctx.builder.alloca(recvr_ty)
    res_len_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero])
    res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.one])

    ctx.builder.store(ctx.builder.trunc(len_val, ctx.i32), res_len_ptr)

    elem_size_val = core.Constant.sizeof(elem_ty)

    size = ctx.builder.mul(elem_size_val, len_val)
    align = core.Constant.int(ctx.i32, 0)
    volatile = core.Constant.int(ctx.i1, 0)

    recvr_arr_ptr = ctx.builder.bitcast(recvr_arr_ptr, ctx.i8_ptr)
    res_arr_ptr = ctx.builder.bitcast(res_arr_ptr, ctx.i8_ptr)

    ctx.builder.call(ctx.funcs['memcpy'], [res_arr_ptr, recvr_arr_ptr, size, align, volatile])

    return res_ptr


@expression.register(ogAST.PrimCall)
def _primary_call(prim):
    ''' Generate the code for a builtin call expression '''
    name = prim.value[0].lower()
    args = prim.value[1]['procParams']

    if name == 'length':
        return generate_length(args)
    elif name == 'present':
        return generate_present(args)
    elif name == 'abs':
        return generate_abs(args)
    elif name == 'fix':
        return generate_fix(args)
    elif name == 'float':
        return generate_float(args)
    elif name == 'power':
        return generate_power(args)
    elif name == 'num':
        return generate_num(args)


def generate_length(params):
    ''' Generate the code for the built-in length operation'''
    seq_ptr = reference(params[0])
    arr_ty = seq_ptr.type.pointee.elements[0]
    if arr_ty.kind != core.TYPE_ARRAY:
        # If is not an array this is a pointer to a variable size SeqOf
        # The array is in the second field of the struct
        arr_ty = seq_ptr.type.pointee.elements[1]
    return core.Constant.int(ctx.i64, arr_ty.count)


def generate_present(params):
    ''' Generate the code for the built-in present operation'''
    expr_val = expression(params[0])
    kind_ptr = ctx.builder.gep(expr_val, [ctx.zero, ctx.zero])
    return ctx.builder.load(kind_ptr)


def generate_abs(params):
    ''' Generate the code for the built-in abs operation'''
    expr_val = expression(params[0])

    if expr_val.type.kind == core.TYPE_INTEGER:
        expr_conv = ctx.builder.sitofp(expr_val, ctx.double)
        res_val = ctx.builder.call(ctx.funcs['fabs'], [expr_conv])
        return ctx.builder.fptosi(res_val, ctx.i64)
    else:
        return ctx.builder.call(ctx.funcs['fabs'], [expr_val])


def generate_fix(params):
    ''' Generate the code for the built-in fix operation'''
    expr_val = expression(params[0])
    return ctx.builder.fptosi(expr_val, ctx.i64)


def generate_float(params):
    ''' Generate the code for the built-in float operation'''
    expr_val = expression(params[0])
    return ctx.builder.sitofp(expr_val, ctx.double)


def generate_power(params):
    ''' Generate the code for the built-in power operation'''
    left_val = expression(params[0])
    right_val = expression(params[1])
    right_conv = ctx.builder.trunc(right_val, ctx.i32)
    if left_val.type.kind == core.TYPE_INTEGER:
        left_conv = ctx.builder.sitofp(left_val, ctx.double)
        res_val = ctx.builder.call(ctx.funcs['powi'], [left_conv, right_conv])
        return ctx.builder.fptosi(res_val, ctx.i64)
    else:
        return ctx.builder.call(ctx.funcs['powi'], [left_val, right_conv])


def generate_num(params):
    ''' Generate the code for the built-in num operation'''
    enum_val = expression(params[0])
    return ctx.builder.sext(enum_val, ctx.i64)


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
            return ctx.builder.add(lefttmp, righttmp, 'addtmp')
        elif expr.operand == '-':
            return ctx.builder.sub(lefttmp, righttmp, 'subtmp')
        elif expr.operand == '*':
            return ctx.builder.mul(lefttmp, righttmp, 'multmp')
        elif expr.operand == '/':
            return ctx.builder.sdiv(lefttmp, righttmp, 'divtmp')
        elif expr.operand == 'mod':
            # l mod r == (((l rem r) + r) rem r)
            remtmp = ctx.builder.srem(lefttmp, righttmp)
            addtmp = ctx.builder.add(remtmp, righttmp)
            return ctx.builder.srem(addtmp, righttmp, 'modtmp')
        elif expr.operand == 'rem':
            return ctx.builder.srem(lefttmp, righttmp, 'remtmp')
        elif expr.operand == '<':
            return ctx.builder.icmp(core.ICMP_SLT, lefttmp, righttmp, 'lttmp')
        elif expr.operand == '<=':
            return ctx.builder.icmp(core.ICMP_SLE, lefttmp, righttmp, 'letmp')
        elif expr.operand == '=':
            return ctx.builder.icmp(core.ICMP_EQ, lefttmp, righttmp, 'eqtmp')
        elif expr.operand == '/=':
            return ctx.builder.icmp(core.ICMP_NE, lefttmp, righttmp, 'netmp')
        elif expr.operand == '>=':
            return ctx.builder.icmp(core.ICMP_SGE, lefttmp, righttmp, 'getmp')
        elif expr.operand == '>':
            return ctx.builder.icmp(core.ICMP_SGT, lefttmp, righttmp, 'gttmp')
        else:
            raise NotImplementedError
    elif lefttmp.type.kind == core.TYPE_DOUBLE:
        if expr.operand == '+':
            return ctx.builder.fadd(lefttmp, righttmp, 'addtmp')
        elif expr.operand == '-':
            return ctx.builder.fsub(lefttmp, righttmp, 'subtmp')
        elif expr.operand == '*':
            return ctx.builder.fmul(lefttmp, righttmp, 'multmp')
        elif expr.operand == '/':
            return ctx.builder.fdiv(lefttmp, righttmp, 'divtmp')
        elif expr.operand == '<':
            return ctx.builder.fcmp(core.FCMP_OLT, lefttmp, righttmp, 'lttmp')
        elif expr.operand == '<=':
            return ctx.builder.fcmp(core.FCMP_OLE, lefttmp, righttmp, 'letmp')
        elif expr.operand == '=':
            return ctx.builder.fcmp(core.FCMP_OEQ, lefttmp, righttmp, 'eqtmp')
        elif expr.operand == '/=':
            return ctx.builder.fcmp(core.FCMP_ONE, lefttmp, righttmp, 'netmp')
        elif expr.operand == '>=':
            return ctx.builder.fcmp(core.FCMP_OGE, lefttmp, righttmp, 'getmp')
        elif expr.operand == '>':
            return ctx.builder.fcmp(core.FCMP_OGT, lefttmp, righttmp, 'gttmp')
        else:
            raise NotImplementedError
    elif is_struct_ptr(lefttmp):
        if expr.operand in ['=', '/=']:
            type_name = expr.left.exprType.ReferencedTypeName.replace('-', '_').lower()
            func = ctx.funcs["%s_equal" % type_name]
            res_val = ctx.builder.call(func, [lefttmp, righttmp])
            return ctx.builder.not_(res_val) if expr.operand == '/=' else res_val
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


@expression.register(ogAST.ExprNeg)
def _neg(expr):
    ''' Generate the code for a negative expression '''
    expr_val = expression(expr.expr)
    if expr_val.type.kind == core.TYPE_INTEGER:
        zero_val = core.Constant.int(ctx.i64, 0)
        return ctx.builder.sub(zero_val, expr_val)
    else:
        zero_val = core.Constant.real(ctx.double, 0)
        return ctx.builder.fsub(zero_val, expr_val)


@expression.register(ogAST.ExprAssign)
def _assign(expr):
    ''' Generate the code for an assign expression '''
    generate_assign(reference(expr.left), expression(expr.right))


def generate_assign(left, right):
    ''' Generate code for an assign from two LLVM values'''
    # This is extracted as an standalone function because is used by
    # multiple generation rules
    if is_struct_ptr(left) or is_array_ptr(left):
        size = core.Constant.sizeof(left.type.pointee)
        align = core.Constant.int(ctx.i32, 0)
        volatile = core.Constant.int(ctx.i1, 0)

        right_ptr = ctx.builder.bitcast(right, ctx.i8_ptr)
        left_ptr = ctx.builder.bitcast(left, ctx.i8_ptr)

        ctx.builder.call(ctx.funcs['memcpy'], [left_ptr, right_ptr, size, align, volatile])
    else:
        ctx.builder.store(right, left)


@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
def _logic(expr):
    ''' Generate the code for a logic expression '''
    if expr.shortcircuit:
        func = ctx.builder.basic_block.function

        right_block = func.append_basic_block('')
        end_block = func.append_basic_block('')

        res_ptr = ctx.builder.alloca(ctx.i1)
        left_val = expression(expr.left)
        ctx.builder.store(left_val, res_ptr)

        if expr.operand == 'and':
            ctx.builder.cbranch(left_val, right_block, end_block)
        elif expr.operand == 'or':
            ctx.builder.cbranch(left_val, end_block, right_block)
        else:
            raise NotImplementedError

        ctx.builder.position_at_end(right_block)
        right_val = expression(expr.right)
        ctx.builder.store(right_val, res_ptr)
        ctx.builder.branch(end_block)

        ctx.builder.position_at_end(end_block)
        return ctx.builder.load(res_ptr)

    else:
        bty = find_basic_type(expr.exprType)

        if bty.kind == 'BooleanType':
            left_val = expression(expr.left)
            right_val = expression(expr.right)
            if expr.operand == 'and':
                return ctx.builder.and_(left_val, right_val)
            elif expr.operand == 'or':
                return ctx.builder.or_(left_val, right_val)
            else:
                return ctx.builder.xor(left_val, right_val)

        elif bty.kind == 'SequenceOfType' and bty.Min == bty.Max:
            func = ctx.builder.basic_block.function

            body_block = func.append_basic_block('%s:body' % expr.operand)
            next_block = func.append_basic_block('%s:next' % expr.operand)
            end_block = func.append_basic_block('%s:end' % expr.operand)

            left_ptr = expression(expr.left)
            right_ptr = expression(expr.right)
            res_ptr = ctx.builder.alloca(left_ptr.type.pointee)

            array_ty = res_ptr.type.pointee.elements[0]
            len_val = core.Constant.int(ctx.i32, array_ty.count)

            idx_ptr = ctx.builder.alloca(ctx.i32)
            ctx.builder.store(core.Constant.int(ctx.i32, 0), idx_ptr)

            ctx.builder.branch(body_block)

            # body block
            ctx.builder.position_at_end(body_block)
            idx_val = ctx.builder.load(idx_ptr)

            left_elem_ptr = ctx.builder.gep(left_ptr, [ctx.zero, ctx.zero, idx_val])
            left_elem_val = ctx.builder.load(left_elem_ptr)

            right_elem_ptr = ctx.builder.gep(right_ptr, [ctx.zero, ctx.zero, idx_val])
            right_elem_val = ctx.builder.load(right_elem_ptr)

            if expr.operand == 'and':
                res_elem_val = ctx.builder.and_(left_elem_val, right_elem_val)
            elif expr.operand == 'or':
                res_elem_val = ctx.builder.or_(left_elem_val, right_elem_val)
            else:
                res_elem_val = ctx.builder.xor(left_elem_val, right_elem_val)

            res_elem_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero, idx_val])
            ctx.builder.store(res_elem_val, res_elem_ptr)

            ctx.builder.branch(next_block)

            # next block
            ctx.builder.position_at_end(next_block)
            idx_tmp_val = ctx.builder.add(idx_val, ctx.one)
            ctx.builder.store(idx_tmp_val, idx_ptr)
            end_cond_val = ctx.builder.icmp(core.ICMP_SGE, idx_tmp_val, len_val)
            ctx.builder.cbranch(end_cond_val, end_block, body_block)

            # end block
            ctx.builder.position_at_end(end_block)
            return res_ptr

        else:
            raise NotImplementedError


@expression.register(ogAST.ExprNot)
def _not(expr):
    ''' Generate the code for a not expression '''
    bty = find_basic_type(expr.exprType)

    if bty.kind == 'BooleanType':
        return ctx.builder.not_(expression(expr.expr))

    elif bty.kind == 'SequenceOfType':
        func = ctx.builder.basic_block.function

        not_block = func.append_basic_block('not:not')
        next_block = func.append_basic_block('not:next')
        end_block = func.append_basic_block('not:end')

        idx_ptr = ctx.builder.alloca(ctx.i32)
        ctx.builder.store(core.Constant.int(ctx.i32, 0), idx_ptr)

        struct_ptr = expression(expr.expr)
        res_struct_ptr = ctx.builder.alloca(struct_ptr.type.pointee)

        if bty.Min != bty.Max:
            len_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero])
            len_val = ctx.builder.load(len_ptr)
            res_len_ptr = ctx.builder.gep(res_struct_ptr, [ctx.zero, ctx.zero])
            ctx.builder.store(len_val, res_len_ptr)
        else:
            array_ty = struct_ptr.type.pointee.elements[0]
            len_val = core.Constant.int(ctx.i32, array_ty.count)

        ctx.builder.branch(not_block)

        ctx.builder.position_at_end(not_block)
        idx_val = ctx.builder.load(idx_ptr)

        if bty.Min != bty.Max:
            elem_idxs = [ctx.zero, ctx.one, idx_val]
        else:
            elem_idxs = [ctx.zero, ctx.zero, idx_val]

        elem_ptr = ctx.builder.gep(struct_ptr, elem_idxs)
        elem_val = ctx.builder.load(elem_ptr)
        res_elem_val = ctx.builder.not_(elem_val)
        res_elem_ptr = ctx.builder.gep(res_struct_ptr, elem_idxs)
        ctx.builder.store(res_elem_val, res_elem_ptr)

        ctx.builder.branch(next_block)

        ctx.builder.position_at_end(next_block)
        idx_tmp_val = ctx.builder.add(idx_val, ctx.one)
        ctx.builder.store(idx_tmp_val, idx_ptr)
        end_cond_val = ctx.builder.icmp(core.ICMP_SGE, idx_tmp_val, len_val)
        ctx.builder.cbranch(end_cond_val, end_block, not_block)

        ctx.builder.position_at_end(end_block)
        return res_struct_ptr

    else:
        raise NotImplementedError


@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    bty = find_basic_type(expr.exprType)

    if bty.kind in ('SequenceOfType', 'OctetStringType'):
        res_ty = ctx.type_of(expr.exprType)
        elem_ty = res_ty.elements[1].element
        elem_size_val = core.Constant.sizeof(elem_ty)

        res_ptr = ctx.builder.alloca(res_ty)
        res_len_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero])
        res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.one])

        left_ptr = expression(expr.left)
        left_len_ptr = ctx.builder.gep(left_ptr, [ctx.zero, ctx.zero])
        left_arr_ptr = ctx.builder.gep(left_ptr, [ctx.zero, ctx.one])
        left_len_val = ctx.builder.load(left_len_ptr)

        right_ptr = expression(expr.right)
        right_len_ptr = ctx.builder.gep(right_ptr, [ctx.zero, ctx.zero])
        right_arr_ptr = ctx.builder.gep(right_ptr, [ctx.zero, ctx.one])
        right_len_val = ctx.builder.load(right_len_ptr)

        res_len_val = ctx.builder.add(left_len_val, right_len_val)
        ctx.builder.store(res_len_val, res_len_ptr)

        ctx.builder.call(ctx.funcs['memcpy'], [
            ctx.builder.bitcast(res_arr_ptr, ctx.i8_ptr),
            ctx.builder.bitcast(left_arr_ptr, ctx.i8_ptr),
            ctx.builder.mul(elem_size_val, ctx.builder.zext(left_len_val, ctx.i64)),
            core.Constant.int(ctx.i32, 0),
            core.Constant.int(ctx.i1, 0)
        ])

        res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.one, left_len_val])

        ctx.builder.call(ctx.funcs['memcpy'], [
            ctx.builder.bitcast(res_arr_ptr, ctx.i8_ptr),
            ctx.builder.bitcast(right_arr_ptr, ctx.i8_ptr),
            ctx.builder.mul(elem_size_val, ctx.builder.zext(right_len_val, ctx.i64)),
            core.Constant.int(ctx.i32, 0),
            core.Constant.int(ctx.i1, 0)
        ])

        return res_ptr

    else:
        raise NotImplementedError


@expression.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' Generate the code for an in expression '''
    func = ctx.builder.basic_block.function

    next_block = func.append_basic_block('in:next')
    check_block = func.append_basic_block('in:check')
    end_block = func.append_basic_block('in:end')

    seq_asn1_ty = find_basic_type(expr.left.exprType)

    is_variable_size = seq_asn1_ty.Min != seq_asn1_ty.Max

    idx_ptr = ctx.builder.alloca(ctx.i32)
    ctx.builder.store(core.Constant.int(ctx.i32, 0), idx_ptr)

    # TODO: Should be 'left' in 'right'?
    value_val = expression(expr.right)
    struct_ptr = expression(expr.left)

    if is_variable_size:
        # load the current number of elements from the first field
        end_idx = ctx.builder.load(ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero]))
    else:
        array_ty = struct_ptr.type.pointee.elements[0]
        end_idx = core.Constant.int(ctx.i32, array_ty.count)

    ctx.builder.branch(check_block)

    ctx.builder.position_at_end(check_block)
    idx_val = ctx.builder.load(idx_ptr)

    if is_variable_size:
        # The array values are in the second field in variable size arrays
        elem_val = ctx.builder.load(ctx.builder.gep(struct_ptr, [ctx.zero, ctx.one, idx_val]))
    else:
        elem_val = ctx.builder.load(ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero, idx_val]))

    if value_val.type.kind == core.TYPE_INTEGER:
        cond_val = ctx.builder.icmp(core.ICMP_EQ, value_val, elem_val)
    elif value_val.type.kind == core.TYPE_DOUBLE:
        cond_val = ctx.builder.fcmp(core.FCMP_OEQ, value_val, elem_val)
    else:
        raise NotImplementedError
    ctx.builder.cbranch(cond_val, end_block, next_block)

    ctx.builder.position_at_end(next_block)
    idx_tmp_val = ctx.builder.add(idx_val, ctx.one)
    ctx.builder.store(idx_tmp_val, idx_ptr)
    end_cond_val = ctx.builder.icmp(core.ICMP_SGE, idx_tmp_val, end_idx)
    ctx.builder.cbranch(end_cond_val, end_block, check_block)

    ctx.builder.position_at_end(end_block)
    return cond_val


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    enumerant = primary.value[0].replace('_', '-')
    basic_ty = find_basic_type(primary.exprType)
    return core.Constant.int(ctx.i32, basic_ty.EnumValues[enumerant].IntValue)


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    enumerant = primary.value[0].replace('-', '_')
    return ctx.enums[enumerant]


@expression.register(ogAST.PrimInteger)
def _integer(primary):
    ''' Generate code for a raw integer value  '''
    return core.Constant.int(ctx.i64, primary.value[0])


@expression.register(ogAST.PrimReal)
def _real(primary):
    ''' Generate code for a raw real value  '''
    return core.Constant.real(ctx.double, primary.value[0])


@expression.register(ogAST.PrimBoolean)
def _boolean(primary):
    ''' Generate code for a raw boolean value  '''
    if primary.value[0].lower() == 'true':
        return core.Constant.int(ctx.i1, 1)
    else:
        return core.Constant.int(ctx.i1, 0)


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    # TODO: Why is this named string if it's not an string?
    struct_ty = ctx.type_of(primary.exprType)
    struct_ptr = ctx.builder.alloca(struct_ty)
    ctx.builder.store(core.Constant.null(struct_ty), struct_ptr)
    return struct_ptr


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string'''
    bty = find_basic_type(primary.exprType)

    str_len = len(str(primary.value[1:-1]))
    str_ptr = ctx.string_ptr(str(primary.value[1:-1]))

    if bty.kind in ('StringType', 'StandardStringType'):
        return str_ptr

    llty = ctx.type_of(primary.exprType)
    octectstr_ptr = ctx.builder.alloca(llty)

    if bty.Min == bty.Max:
        arr_ptr = ctx.builder.gep(octectstr_ptr, [ctx.zero, ctx.zero])
    else:
        arr_ptr = ctx.builder.gep(octectstr_ptr, [ctx.zero, ctx.one])

        # Copy length
        str_len_val = core.Constant.int(ctx.i32, str_len)
        count_ptr = ctx.builder.gep(octectstr_ptr, [ctx.zero, ctx.zero])
        ctx.builder.store(str_len_val, count_ptr)

    # Copy constant string
    casted_arr_ptr = ctx.builder.bitcast(arr_ptr, ctx.i8_ptr)
    casted_str_ptr = ctx.builder.bitcast(str_ptr, ctx.i8_ptr)

    size = core.Constant.int(ctx.i64, str_len)
    align = core.Constant.int(ctx.i32, 0)
    volatile = core.Constant.int(ctx.i1, 0)

    ctx.builder.call(ctx.funcs['memcpy'], [casted_arr_ptr, casted_str_ptr, size, align, volatile])

    return octectstr_ptr


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    raise NotImplementedError


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    raise NotImplementedError


@expression.register(ogAST.PrimConditional)
def _if_then_else(ifthen):
    ''' Generate the code for ternary operator '''
    func = ctx.builder.basic_block.function

    if_block = func.append_basic_block('ternary:if')
    else_block = func.append_basic_block('ternary:else')
    end_block = func.append_basic_block('')

    res_ptr = ctx.builder.alloca(ctx.type_of(ifthen.exprType))
    cond_val = expression(ifthen.value['if'])
    ctx.builder.cbranch(cond_val, if_block, else_block)

    ctx.builder.position_at_end(if_block)
    generate_assign(res_ptr, expression(ifthen.value['then']))
    ctx.builder.branch(end_block)

    ctx.builder.position_at_end(else_block)
    generate_assign(res_ptr, expression(ifthen.value['else']))
    ctx.builder.branch(end_block)

    ctx.builder.position_at_end(end_block)

    if is_struct_ptr(res_ptr) or is_array_ptr(res_ptr):
        return res_ptr
    else:
        return ctx.builder.load(res_ptr)


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Generate the code for an ASN.1 SEQUENCE '''
    struct = ctx.resolve_struct(seq.exprType.ReferencedTypeName)
    struct_ptr = ctx.builder.alloca(struct.ty)

    seq_asn1ty = ctx.dataview[seq.exprType.ReferencedTypeName]

    for field_name, field_expr in seq.value.viewitems():
        # Workarround for unknown types in nested sequences
        field_expr.exprType = seq_asn1ty.type.Children[field_name.replace('_', '-')].type

        field_idx_cons = core.Constant.int(ctx.i32, struct.idx(field_name))
        field_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, field_idx_cons])
        generate_assign(field_ptr, expression(field_expr))

    return struct_ptr


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Generate the code for an ASN.1 SEQUENCE OF '''
    basic_ty = find_basic_type(seqof.exprType)
    ty = ctx.type_of(seqof.exprType)
    struct_ptr = ctx.builder.alloca(ty)

    is_variable_size = basic_ty.Min != basic_ty.Max

    if is_variable_size:
        size_val = core.Constant.int(ctx.i32, len(seqof.value))
        ctx.builder.store(size_val, ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero]))
        array_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.one])
    else:
        array_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero])

    for idx, expr in enumerate(seqof.value):
        idx_cons = core.Constant.int(ctx.i32, idx)
        expr_val = expression(expr)
        pos_ptr = ctx.builder.gep(array_ptr, [ctx.zero, idx_cons])
        generate_assign(pos_ptr, expr_val)

    return struct_ptr


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Generate the code for a CHOICE expression '''
    union = ctx.resolve_union(choice.exprType.ReferencedTypeName)
    union_ptr = ctx.builder.alloca(union.ty)

    expr_val = expression(choice.value['value'])
    kind_idx, field_ty = union.kind(choice.value['choice'])

    kind_ptr = ctx.builder.gep(union_ptr, [ctx.zero, ctx.zero])
    ctx.builder.store(core.Constant.int(ctx.i32, kind_idx), kind_ptr)

    field_ptr = ctx.builder.gep(union_ptr, [ctx.zero, ctx.one])
    field_ptr = ctx.builder.bitcast(field_ptr, core.Type.pointer(field_ty))
    generate_assign(field_ptr, expr_val)

    return union_ptr


@generate.register(ogAST.Decision)
def _decision(dec):
    ''' Generate the code for a decision '''
    func = ctx.builder.basic_block.function

    ans_cond_blocks = [func.append_basic_block('dec:ans:cond') for ans in dec.answers]
    end_block = func.append_basic_block('dec:end')

    ctx.builder.branch(ans_cond_blocks[0])

    for idx, ans in enumerate(dec.answers):
        ans_cond_block = ans_cond_blocks[idx]
        true_block = func.append_basic_block('dec:ans:tr') if ans.transition else end_block
        false_block = ans_cond_blocks[idx + 1] if idx < len(ans_cond_blocks) - 1 else end_block

        ctx.builder.position_at_end(ans_cond_block)

        if ans.kind in ['constant', 'open_range']:
            expr = ans.openRangeOp()
            expr.left = dec.question
            expr.right = ans.constant
            expr_val = expression(expr)

            ctx.builder.cbranch(expr_val, true_block, false_block)

        elif ans.kind == 'closed_range':
            question_val = expression(dec.question)
            range_l_val = expression(ans.closedRange[0])
            range_r_val = expression(ans.closedRange[1])

            if question_val.type.kind == core.TYPE_INTEGER:
                range_l_cond_val = ctx.builder.icmp(core.ICMP_SGE, question_val, range_l_val)
                range_r_cond_val = ctx.builder.icmp(core.ICMP_SLE, question_val, range_r_val)
            else:
                range_l_cond_val = ctx.builder.fcmp(core.FCMP_OLE, question_val, range_l_val)
                range_r_cond_val = ctx.builder.fcmp(core.FCMP_OGE, question_val, range_r_val)

            ans_cond_val = ctx.builder.and_(range_l_cond_val, range_r_cond_val)
            ctx.builder.cbranch(ans_cond_val, true_block, false_block)

        elif ans.kind == 'else':
            ctx.builder.branch(true_block)

        else:
            raise NotImplementedError

        if ans.transition:
            ctx.builder.position_at_end(true_block)
            generate(ans.transition)
            if not ctx.builder.basic_block.terminator:
                ctx.builder.branch(end_block)

    ctx.builder.position_at_end(end_block)


@generate.register(ogAST.Label)
def _label(label):
    ''' Generate the code for a Label '''
    label_block = ctx.scope.label(str(label.inputString))
    ctx.builder.branch(label_block)


@generate.register(ogAST.Transition)
def _transition(tr):
    ''' Generate the code for a transition '''
    for action in tr.actions:
        generate(action)
        if isinstance(action, ogAST.Label):
            return
    if tr.terminator:
        generate_terminator(tr.terminator)


def generate_terminator(term):
    ''' Generate the code for a transition terminator '''
    if term.label:
        raise NotImplementedError

    if term.kind == 'next_state':
        generate_next_state_terminator(term)
    elif term.kind == 'join':
        generate_join_terminator(term)
    elif term.kind == 'stop':
        generate_stop_terminator(term)
    elif term.kind == 'return':
        generate_return_terminator(term)


def generate_next_state_terminator(term):
    ''' Generate the code for a next state transition terminator '''
    state = term.inputString.lower()
    if state.strip() != '-':
        if type(term.next_id) is int:
            next_id_val = core.Constant.int(ctx.i32, term.next_id)
            if term.next_id == -1:
                ctx.builder.store(ctx.states[state.lower()], ctx.global_scope.resolve('.state'))
        else:
            next_id_val = ctx.states[term.next_id.lower()]
        ctx.builder.store(next_id_val, ctx.scope.resolve('id'))
    else:
        nexts = [(n, s) for (n, s) in term.candidate_id.viewitems() if n != -1]
        if nexts:
            # Calculate next transition id in base of the current state
            func = ctx.builder.basic_block.function
            curr_state_val = ctx.builder.load(ctx.global_scope.resolve('.state'))
            default_case_block = func.append_basic_block('')
            end_block = func.append_basic_block('')
            switch = ctx.builder.switch(curr_state_val, default_case_block)

            for next_state, states in nexts:
                next_id_val = ctx.states[next_state.lower()]
                for state in states:
                    case_block = func.append_basic_block('')
                    switch.add_case(ctx.states[state.lower()], case_block)
                    ctx.builder.position_at_end(case_block)
                    ctx.builder.store(next_id_val, ctx.scope.resolve('id'))
                    ctx.builder.branch(end_block)

            ctx.builder.position_at_end(default_case_block)
            next_id_val = core.Constant.int(ctx.i32, -1)
            ctx.builder.store(next_id_val, ctx.scope.resolve('id'))
            ctx.builder.branch(end_block)

            ctx.builder.position_at_end(end_block)
        else:
            next_id_cons = core.Constant.int(ctx.i32, -1)
            ctx.builder.store(next_id_cons, ctx.scope.resolve('id'))

    ctx.builder.branch(ctx.scope.label('next_transition'))


def generate_join_terminator(term):
    ''' Generate the code for a join transition terminator '''
    label_block = ctx.scope.label(str(term.inputString))
    ctx.builder.branch(label_block)


def generate_stop_terminator(term):
    ''' Generate the code for a stop transition terminator '''
    raise NotImplementedError


def generate_return_terminator(term):
    ''' Generate the code for a return transition terminator '''
    if term.next_id == -1 and term.return_expr:
        ctx.builder.ret(expression(term.return_expr))
    elif term.next_id == -1:
        ctx.builder.ret_void()
    else:
        next_id_cons = core.Constant.int(ctx.i32, term.next_id)
        ctx.builder.store(next_id_cons, ctx.scope.resolve('id'))
        ctx.builder.branch(ctx.scope.label('next_transition'))


@generate.register(ogAST.Floating_label)
def _floating_label(label):
    ''' Generate the code for a floating label '''
    label_block = ctx.scope.label(str(label.inputString))
    if not ctx.builder.basic_block.terminator:
        ctx.builder.branch(label_block)
    ctx.builder.position_at_end(label_block)

    if label.transition:
        generate(label.transition)
    else:
        ctx.builder.ret_void()


@generate.register(ogAST.Procedure)
def _inner_procedure(proc):
    ''' Generate the code for a procedure '''
    param_tys = [core.Type.pointer(ctx.type_of(p['type'])) for p in proc.fpar]
    func = ctx.decl_func(str(proc.inputString), ctx.void, param_tys)

    if proc.external:
        return

    ctx.open_scope()

    for arg, param in zip(func.args, proc.fpar):
        ctx.scope.define(str(param['name']), arg)

    entry_block = func.append_basic_block('entry')
    ctx.builder = core.Builder.new(entry_block)

    for name, (ty, expr) in proc.variables.viewitems():
        var_ty = ctx.type_of(ty)
        var_ptr = ctx.builder.alloca(var_ty)
        ctx.scope.define(name, var_ptr)
        if expr:
            expr_val = expression(expr)
            generate_assign(var_ptr, expr_val)
        else:
            ctx.builder.store(core.Constant.null(var_ty), var_ptr)

    Helper.inner_labels_to_floating(proc)

    generate(proc.content.start.transition)

    for label in proc.content.floating_labels:
        generate(label)

    ctx.close_scope()

    if not ctx.builder.basic_block.terminator:
        ctx.builder.ret_void()

    func.verify()


def is_struct_ptr(val):
    return val.type.kind == core.TYPE_POINTER and val.type.pointee.kind == core.TYPE_STRUCT


def is_array_ptr(val):
    return val.type.kind == core.TYPE_POINTER and val.type.pointee.kind == core.TYPE_ARRAY


# TODO: Refactor this into the helper module
def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in ctx.dataview.viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = ctx.dataview[typename].type
                break
    return basic_type
