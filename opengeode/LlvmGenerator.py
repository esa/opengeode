#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates LLVM IR code from SDL process models, allowing
    generation of a binary application without an intermediate language.
    LLVM also allows for various code verification, analysis, and optimization.

    The design is based on the Ada code generator. Check it for details.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Diego Barbera 

    Contact: maxime.perrotin@esa.int
"""

import logging

from singledispatch import singledispatch

from llvm import core as lc
from llvm import ee as le
from llvm import passes
from llvm import LLVMException

import ogAST
import Helper

LOG = logging.getLogger(__name__)

__all__ = ['generate']


class Context():
    def __init__(self, process):
        self.name = str(process.processName)
        self.process = process
        self.module = lc.Module.new(self.name)
        self.target_data = le.TargetData.new(self.module.data_layout)
        self.dataview = process.dataview

        self.procedures = process.procedures

        self.scope = Scope(self)
        self.global_scope = self.scope
        self.states = {}
        self.enums = {}
        self.structs = {}
        self.unions = {}
        self.strings = {}
        self.funcs = {}
        self.lltypes = {}
        self.basic_asn1types = {}

        # Initialize built-in types
        self.i1 = lc.Type.int(1)
        self.i8 = lc.Type.int(8)
        self.i32 = lc.Type.int(32)
        self.i64 = lc.Type.int(64)
        self.void = lc.Type.void()
        self.double = lc.Type.double()
        self.i1_ptr = lc.Type.pointer(self.i1)
        self.i8_ptr = lc.Type.pointer(self.i8)
        self.i32_ptr = lc.Type.pointer(self.i32)
        self.i64_ptr = lc.Type.pointer(self.i64)
        self.double_ptr = lc.Type.pointer(self.double)

        # Initialize common constants
        self.zero = lc.Constant.int(self.i32, 0)
        self.one = lc.Constant.int(self.i32, 1)

        # Intialize built-in functions
        ty = lc.Type.function(self.void, [self.i8_ptr], True)
        self.funcs['printf'] = self.module.add_function(ty, 'printf')

        ty = lc.Type.function(self.double, [self.double])
        self.funcs['round'] = self.module.add_function(ty, 'round')

        self.funcs['memcpy'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_MEMCPY,
            [self.i8_ptr, self.i8_ptr, self.i64]
        )

        self.funcs['powi'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_POWI,
            [self.double]
        )

        self.funcs['ceil'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_CEIL,
            [self.double]
        )

        self.funcs['cos'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_COS,
            [self.double]
        )

        self.funcs['fabs'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_FABS,
            [self.double]
        )

        self.funcs['floor'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_FLOOR,
            [self.double]
        )

        self.funcs['sin'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_SIN,
            [self.double]
        )

        self.funcs['sqrt'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_SQRT,
            [self.double]
        )

        self.funcs['trunc'] = lc.Function.intrinsic(
            self.module,
            lc.INTR_TRUNC,
            [self.double]
        )

    def open_scope(self):
        ''' Open a scope '''
        self.scope = Scope(self, self.scope)

    def close_scope(self):
        ''' Close the current scope '''
        self.scope = self.scope.parent

    def basic_asn1type_of(self, asn1ty):
        ''' Return the ASN.1 basic type of a type '''
        if asn1ty.kind != 'ReferenceType':
            return asn1ty

        asn1ty_name = asn1ty.ReferencedTypeName.lower()

        # return the basic type if its cached
        if asn1ty_name in self.basic_asn1types:
            return self.basic_asn1types[asn1ty_name]

        basic_asn1ty = asn1ty
        while basic_asn1ty.kind == 'ReferenceType':
            for typename in self.dataview.viewkeys():
                if typename.lower() == basic_asn1ty.ReferencedTypeName.lower():
                    basic_asn1ty = self.dataview[typename].type
                    break

        # cache the basic type
        self.basic_asn1types[asn1ty_name] = basic_asn1ty

        return basic_asn1ty

    def lltype_of(self, asn1ty):
        ''' Return the LL type of a ASN.1 type '''
        try:
            name = asn1ty.ReferencedTypeName.replace('-', '_')
        except AttributeError:
            name = None

        if name and name in self.lltypes:
            return self.lltypes[name]

        basic_asn1ty = self.basic_asn1type_of(asn1ty)

        if basic_asn1ty.kind == 'IntegerType':
            llty = self.i64
        elif basic_asn1ty.kind == 'Integer32Type':
            llty = self.i32
        elif basic_asn1ty.kind == 'BooleanType':
            llty = self.i1
        elif basic_asn1ty.kind == 'RealType':
            llty = self.double
        elif basic_asn1ty.kind == 'SequenceOfType':
            llty = self._lltype_of_sequenceof(name, basic_asn1ty)
        elif basic_asn1ty.kind == 'SequenceType':
            llty = self._lltype_of_sequence(name, basic_asn1ty)
        elif basic_asn1ty.kind == 'EnumeratedType':
            llty = self.i32
        elif basic_asn1ty.kind == 'ChoiceType':
            llty = self._lltype_of_choice(name, basic_asn1ty)
        elif basic_asn1ty.kind == 'OctetStringType':
            llty = self._lltype_of_octetstring(name, basic_asn1ty)
        elif basic_asn1ty.kind in ('StringType', 'StandardStringType'):
            llty = self.i8_ptr
        else:
            raise CompileError('Unknown basic ASN.1 type "%s"' % basic_asn1ty.kind)

        if name:
            self.lltypes[name] = llty

        return llty

    def _lltype_of_sequenceof(self, name, asn1ty):
        ''' Return the LL type of a SequenceOf ASN.1 type '''
        min_size = int(asn1ty.Min)
        max_size = int(asn1ty.Max)
        is_variable_size = min_size != max_size

        elem_llty = self.lltype_of(asn1ty.type)
        array_llty = lc.Type.array(elem_llty, max_size)

        if is_variable_size:
            struct = self.decl_struct(['nCount', 'arr'], [self.i32, array_llty], name)
        else:
            struct = self.decl_struct(['arr'], [array_llty], name)

        struct_ptr = lc.Type.pointer(struct.llty)
        self.decl_func("asn1Scc%s_Equal" % name, self.i1, [struct_ptr, struct_ptr])

        return struct.llty

    def _lltype_of_sequence(self, name, asn1ty):
        ''' Return the LL type of a Sequence ASN.1 type '''
        field_names = []
        field_lltys = []

        for field_name in Helper.sorted_fields(asn1ty):
            field_names.append(field_name.replace('-', '_'))
            field_lltys.append(self.lltype_of(asn1ty.Children[field_name].type))

        struct = self.decl_struct(field_names, field_lltys, name)

        struct_ptr = lc.Type.pointer(struct.llty)
        self.decl_func("asn1Scc%s_Equal" % name, self.i1, [struct_ptr, struct_ptr])

        return struct.llty

    def _lltype_of_choice(self, name, asn1ty):
        ''' Return the equivalent LL type of a Choice ASN.1 type '''
        field_names = []
        field_lltys = []

        for idx, field_name in enumerate(Helper.sorted_fields(asn1ty)):
            # enum values used in choice determinant/present
            self.enums[field_name.replace('-', '_').lower()] = lc.Constant.int(self.i32, idx)

            field_names.append(field_name.replace('-', '_'))
            field_lltys.append(self.lltype_of(asn1ty.Children[field_name].type))

        union = self.decl_union(field_names, field_lltys, name)

        union_ptr = lc.Type.pointer(union.llty)
        self.decl_func("asn1Scc%s_Equal" % name, self.i1, [union_ptr, union_ptr])

        return union.llty

    def _lltype_of_octetstring(self, name, asn1ty):
        ''' Return the equivalent LL type of a OctetString ASN.1 type '''
        min_size = int(asn1ty.Min)
        max_size = int(asn1ty.Max)
        is_variable_size = min_size != max_size

        array_llty = lc.Type.array(self.i8, max_size)

        if is_variable_size:
            struct = self.decl_struct(['nCount', 'arr'], [self.i32, array_llty], name)
        else:
            struct = self.decl_struct(['arr'], [array_llty], name)

        struct_ptr = lc.Type.pointer(struct.llty)
        self.decl_func("asn1Scc%s_Equal" % name, self.i1, [struct_ptr, struct_ptr])

        return struct.llty

    def string_ptr(self, str):
        ''' Returns a pointer to a global string with the given value '''
        if str in self.strings:
            return self.strings[str].gep([self.zero, self.zero])

        str_val = lc.Constant.stringz(str)
        var_name = '.str%s' % len(self.strings)
        var_ptr = self.module.add_global_variable(str_val.type, var_name)
        var_ptr.initializer = str_val
        self.strings[str] = var_ptr
        return var_ptr.gep([self.zero, self.zero])

    def decl_func(self, name, return_llty, param_lltys, extern=False):
        ''' Declare a function '''
        func_llty = lc.Type.function(return_llty, param_lltys)
        func_name = ("%s_RI_%s" % (self.name, name)) if extern else name
        func = lc.Function.new(self.module, func_llty, func_name)
        self.funcs[name.lower()] = func
        return func

    def decl_struct(self, field_names, field_lltys, name=None):
        ''' Declare a struct '''
        name = name if name else "struct.%s" % len(self.structs)
        name = name.replace('-', '_')
        struct = StructType(name, field_names, field_lltys)
        self.structs[name] = struct
        return struct

    def resolve_struct(self, name):
        ''' Return the struct associated to a name '''
        return self.structs[name.replace('-', '_')]

    def decl_union(self, field_names, field_lltys, name=None):
        name = name if name else "union.%s" % len(self.structs)
        name = name.replace('-', '_')
        union = UnionType(name, field_names, field_lltys, self)
        self.unions[name] = union
        return union

    def resolve_union(self, name):
        ''' Return the union associated to a name '''
        return self.unions[name.replace('-', '_')]


class StructType():
    def __init__(self, name, field_names, field_lltys):
        self.name = name
        self.field_names = field_names
        self.llty = lc.Type.struct(field_lltys, self.name)

    def idx(self, field_name):
        return self.field_names.index(field_name)


class UnionType():
    def __init__(self, name, field_names, field_lltys, ctx):
        self.name = name
        self.field_names = field_names
        self.field_lltys = field_lltys
        # Unions are represented a struct with a field indicating the index of its type
        # and a byte array with the size of the biggest type in the union
        self.size = max([ctx.target_data.size(ty) for ty in field_lltys])
        self.llty = lc.Type.struct([ctx.i32, lc.Type.array(ctx.i8, self.size)], name)

    def kind(self, name):
        idx = self.field_names.index(name)
        return (idx, self.field_lltys[idx])


class Scope:
    def __init__(self, ctx, parent=None):
        self.ctx = ctx
        self.vars = {}
        self.labels = {}
        self.parent = parent

    def define(self, name, var):
        self.vars[name.lower().replace('-', '_')] = var

    def resolve(self, name):
        var = self.vars.get(name.lower().replace('-', '_'))
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
            func = self.ctx.builder.basic_block.function
            label_block = func.append_basic_block('label:%s' % name)
            self.labels[name] = label_block
        return label_block


class CompileError(Exception):
    pass


@singledispatch
def generate(ast, ctx=None, options=None):
    ''' Generate the IR for an AST node '''
    raise CompileError('Unsupported AST construct "%s"' % ast.__class__.__name__)


# Processing of the AST
@generate.register(ogAST.Process)
def _process(process, ctx=None, options=None):
    ''' Generate the IR for a process '''
    process_name = str(process.processName)
    LOG.info('Generating LLVM IR code for process ' + process_name)

    ctx = Context(process)

    # In case model has nested states, flatten everything
    Helper.flatten(process, '.')

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    # Initialize states
    for name, val in process.mapping.viewitems():
        if not name.endswith('START'):
            cons_val = lc.Constant.int(ctx.i32, len(ctx.states))
            ctx.states[name.lower()] = cons_val
        elif name != 'START':
            cons_val = lc.Constant.int(ctx.i32, val)
            ctx.states[name.lower()] = cons_val

    # Generate state var
    state_cons = ctx.module.add_global_variable(ctx.i32, '.state')
    state_cons.initializer = lc.Constant.int(ctx.i32, -1)
    ctx.scope.define('.state', state_cons)

    # Generate ASN.1 constants
    for name, t in process.dv.variables.viewitems():
        var_llty = ctx.lltype_of(t.type)
        name = str(name).replace('-', '_').lower()
        global_var = ctx.module.add_global_variable(var_llty, name)
        ctx.scope.define(name, global_var)

    # Generare process-level vars
    for name, (asn1ty, expr) in process.variables.viewitems():
        var_llty = ctx.lltype_of(asn1ty)
        global_var = ctx.module.add_global_variable(var_llty, str(name))
        global_var.initializer = lc.Constant.null(var_llty)
        ctx.scope.define(str(name).lower(), global_var)

    # Declare set/reset timer functions
    for timer in process.timers:
        # TODO: Should be uint?
        ctx.decl_func("set_%s" % str(timer), ctx.void, [ctx.i64_ptr], True)
        ctx.decl_func("reset_%s" % str(timer), ctx.void, [], True)

    # Declare output signal functions
    for signal in process.output_signals:
        if 'type' in signal:
            param_lltys = [lc.Type.pointer(ctx.lltype_of(signal['type']))]
        else:
            param_lltys = []
        ctx.decl_func(str(signal['name']), ctx.void, param_lltys, True)

    # Declare external procedures functions
    for proc in [proc for proc in process.procedures if proc.external]:
        param_lltys = [lc.Type.pointer(ctx.lltype_of(p['type'])) for p in proc.fpar]
        ctx.decl_func(str(proc.inputString), ctx.void, param_lltys, True)

    # Generate internal procedures
    for proc in process.content.inner_procedures:
        generate(proc, ctx)

    # Generate process functions
    generate_runtr_func(process, ctx)
    generate_startup_func(process, ctx)

    # Generate input signals
    for signal in process.input_signals:
        generate_input_signal(signal, mapping[signal['name']], ctx)

    # Generate timer signal
    for timer in process.timers:
        generate_input_signal({'name': timer.lower()}, mapping[timer], ctx)

    try:
        ctx.module.verify()
    except LLVMException as err:
        LOG.error(str(err))

    if options and options.optimization:
        LOG.info('Optimizing generated LLVM IR code for process %s at level %d'
            % (ctx.name, options.optimization))
        pm = passes.PassManager.new()

        pmb = passes.PassManagerBuilder.new()
        pmb.opt_level = options.optimization
        pmb.populate(pm)

        pm.run(ctx.module)

    with open(ctx.name + '.ll', 'w') as ll_file:
        ll_file.write(str(ctx.module))


def generate_runtr_func(process, ctx):
    ''' Generate the IR for the run_transition function '''
    func = ctx.decl_func('run_transition', ctx.void, [ctx.i32])

    ctx.open_scope()

    entry_block = func.append_basic_block('runtr:entry')
    cond_block = func.append_basic_block('runtr:cond')
    body_block = func.append_basic_block('runtr:body')
    exit_block = func.append_basic_block('runtr:exit')

    ctx.builder = lc.Builder.new(entry_block)

    # entry
    id_ptr = ctx.builder.alloca(ctx.i32, None, 'id')
    ctx.scope.define('id', id_ptr)
    ctx.builder.store(func.args[0], id_ptr)
    ctx.builder.branch(cond_block)

    # cond
    ctx.builder.position_at_end(cond_block)
    no_tr_cons = lc.Constant.int(ctx.i32, -1)
    id_val = ctx.builder.load(id_ptr)
    cond_val = ctx.builder.icmp(lc.ICMP_NE, id_val, no_tr_cons, 'cond')
    ctx.builder.cbranch(cond_val, body_block, exit_block)

    # body
    ctx.builder.position_at_end(body_block)
    switch = ctx.builder.switch(id_val, exit_block)

    # transitions
    for idx, tr in enumerate(process.transitions):
        tr_block = func.append_basic_block('runtr:tr%d' % idx)
        const = lc.Constant.int(ctx.i32, idx)
        switch.add_case(const, tr_block)
        ctx.builder.position_at_end(tr_block)
        generate(tr, ctx)
        if not ctx.builder.basic_block.terminator:
            ctx.builder.branch(cond_block)

    # exit
    ctx.builder.position_at_end(exit_block)
    ctx.builder.ret_void()

    Helper.inner_labels_to_floating(process)
    for label in process.content.floating_labels:
        generate(label, ctx)

    next_tr_label_block = ctx.scope.label('next_transition')
    ctx.builder.position_at_end(next_tr_label_block)
    ctx.builder.branch(cond_block)

    ctx.close_scope()

    try:
        func.verify()
    except LLVMException as err:
        LOG.error('LLVM Verify: {}'.format(str(err)))
    return func


def generate_startup_func(process, ctx):
    ''' Generate the IR for the startup function '''
    func = ctx.decl_func(ctx.name + '_startup', ctx.void, [])

    ctx.open_scope()

    entry_block = func.append_basic_block('startup:entry')
    ctx.builder = lc.Builder.new(entry_block)

    # Initialize process level variables
    for name, (ty, expr) in process.variables.viewitems():
        if expr:
            global_var = ctx.scope.resolve(str(name))
            right = expression(expr, ctx)
            if isinstance(right, (SDLStringLiteral, SDLSequenceOf,
                                  SDLAppendValue, SDLSubstringValue)):
                # Propagate left type before processing the right side
                right.typeof = ty
            sdl_assign(global_var, right, ctx)

    sdl_call('run_transition', [lc.Constant.int(ctx.i32, 0)], ctx)
    ctx.builder.ret_void()

    ctx.close_scope()

    func.verify()
    return func


def generate_input_signal(signal, inputs, ctx):
    ''' Generate the IR for an input signal '''
    func_name = ctx.name + "_" + str(signal['name'])
    param_lltys = []
    if 'type' in signal:
        param_lltys.append(lc.Type.pointer(ctx.lltype_of(signal['type'])))

    func = ctx.decl_func(func_name, ctx.void, param_lltys)

    ctx.open_scope()

    entry_block = func.append_basic_block('input:entry')
    exit_block = func.append_basic_block('input:exit')
    ctx.builder = lc.Builder.new(entry_block)

    g_state_val = ctx.builder.load(ctx.global_scope.resolve('.state'))
    switch = ctx.builder.switch(g_state_val, exit_block)

    for state_name, state_id in ctx.states.iteritems():
        if state_name.endswith('start'):
            continue

        state_block = func.append_basic_block('input:state_%s' % str(state_name))
        switch.add_case(state_id, state_block)
        ctx.builder.position_at_end(state_block)

        state_input = inputs.get(state_name)
        if not state_input:
            ctx.builder.ret_void()
            continue

        trans = state_input.transition

        for exit_func_name in exit_list(state_name, ctx.process):
            if trans and all(exit_func_name.startswith(trans_st)
                             for trans_st in trans.possible_states):
                sdl_call(exit_func_name, [], ctx)

        for var_name in state_input.parameters:
            var_ptr = ctx.scope.resolve(str(var_name))
            if is_struct_ptr(var_ptr) or is_array_ptr(var_ptr):
                sdl_assign(var_ptr, func.args[0], ctx)
            else:
                sdl_assign(var_ptr, ctx.builder.load(func.args[0]), ctx)

        if trans:
            id_val = lc.Constant.int(ctx.i32, state_input.transition_id)
            sdl_call('run_transition', [id_val], ctx)

        ctx.builder.ret_void()

    ctx.builder.position_at_end(exit_block)
    ctx.builder.ret_void()

    ctx.close_scope()

    func.verify()


def exit_list(state_name, process):
    ''' Calculate the exit call list of a state '''
    context = process
    exitlist = []
    current = ''
    state_tree = state_name.split('.')

    while state_tree:
        current = current + state_tree.pop(0)
        for comp in context.composite_states:
            if current.lower() == comp.statename.lower():
                if comp.exit_procedure:
                    exitlist.append(current + '.exit')
                context = comp
                current = current + '.'
                break

    return reversed(exitlist)


@generate.register(ogAST.Output)
def _output(output, ctx):
    ''' Generate the IR for an output '''
    for out in output.output:
        name = out['outputName'].lower()
        args = out.get('params', [])

        arg_vals = []
        for arg in args:
            arg_val = expression(arg, ctx)
            if isinstance(arg_val, SDLStringLiteral):
                arg_val = sdl_stringliteral(arg_val.string, arg_val.typeof, ctx)
            elif isinstance(arg_val, SDLSequenceOf):
                arg_val = sdl_sequenceof(arg_val, ctx)
            # XXX Add SDLSubstring and SDLAppendValue, no?
            # Pass by reference
            if arg_val.type.kind != lc.TYPE_POINTER:
                arg_var = ctx.builder.alloca(arg_val.type, None)
                ctx.builder.store(arg_val, arg_var)
                arg_vals.append(arg_var)
            else:
                arg_vals.append(arg_val)

        sdl_call(str(name).lower(), arg_vals, ctx)


@generate.register(ogAST.ProcedureCall)
def _proc_call(proc_call, ctx):
    ''' Generate the IR for a procedure call '''
    output = proc_call.output[0]

    name = output['outputName'].lower()
    args = output.get('params', [])

    if name == 'write' or name == 'writeln':
        def flatten_append(arg):
            ''' Transform "write(a//b//...)" to "write(a, b, ...)" '''
            if isinstance(arg, ogAST.ExprAppend):
                res = flatten_append(arg.left)
                res.extend(flatten_append(arg.right))
                return res
            return [arg]
        flat_args = []
        for each in args:
            flat_args.extend(flatten_append(each))
        arg_vals = [expression(a, ctx) for a in flat_args]
        arg_asn1tys = [a.exprType for a in flat_args]
        sdl_write(arg_vals, arg_asn1tys, ctx, name == 'writeln')
        return
    elif name == 'reset_timer':
        sdl_reset_timer(args[0].value[0], ctx)
        return
    elif name == 'set_timer':
        timer_expr, timer_id = args
        sdl_set_timer(timer_id.value[0], expression(timer_expr, ctx), ctx)
        return

    proc = None
    for p in ctx.procedures:
        if p.inputString.lower() == name:
            proc = p
            break
    else:
        raise CompileError('Procedure "%s" not found' % name)

    arg_vals = []
    for arg, param in zip(args, proc.fpar):
        if param['direction'] == 'out':
            arg_vals.append(reference(arg, ctx))
        else:
            arg_val = expression(arg, ctx)
            if isinstance(arg_val, SDLStringLiteral):
                arg_val = sdl_stringliteral(arg_val.string, arg_val.typeof, ctx)
            # Pass by reference
            if arg_val.type.kind != lc.TYPE_POINTER:
                arg_var = ctx.builder.alloca(arg_val.type, None)
                ctx.builder.store(arg_val, arg_var)
                arg_vals.append(arg_var)
            else:
                arg_vals.append(arg_val)

    sdl_call(str(name).lower(), arg_vals, ctx)


@generate.register(ogAST.TaskAssign)
def _task_assign(task, ctx):
    ''' Generate the IR for a list of assignments '''
    for expr in task.elems:
        expression(expr, ctx)


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task, ctx):
    ''' Generate comments for informal text '''
    pass


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task, ctx):
    ''' Generate the IRfor a for loop '''
    for loop in task.elems:
        if loop['range']:
            generate_for_range(loop, ctx)
        else:
            generate_for_iterable(loop, ctx)


def generate_for_range(loop, ctx):
    ''' Generate the IR for a for x in range loop '''
    func = ctx.builder.basic_block.function
    cond_block = func.append_basic_block('for:cond')
    body_block = func.append_basic_block('for:body')
    inc_block = func.append_basic_block('for:inc')
    end_block = func.append_basic_block('for:end')

    ctx.open_scope()

    loop_var = ctx.builder.alloca(ctx.i64, None, str(loop['var']))
    ctx.scope.define(str(loop['var']), loop_var)

    if loop['range']['start']:
        start_val = expression(loop['range']['start'], ctx)
        ctx.builder.store(start_val, loop_var)
    else:
        ctx.builder.store(lc.Constant.int(ctx.i64, 0), loop_var)

    stop_val = expression(loop['range']['stop'], ctx)
    ctx.builder.branch(cond_block)

    ctx.builder.position_at_end(cond_block)
    loop_val = ctx.builder.load(loop_var)
    cond_val = ctx.builder.icmp(lc.ICMP_SLT, loop_val, stop_val)
    ctx.builder.cbranch(cond_val, body_block, end_block)

    ctx.builder.position_at_end(body_block)
    generate(loop['transition'], ctx)
    ctx.builder.branch(inc_block)

    ctx.builder.position_at_end(inc_block)
    step_val = lc.Constant.int(ctx.i64, loop['range']['step'])
    loop_val = ctx.builder.load(loop_var)
    temp_val = ctx.builder.add(loop_val, step_val)
    ctx.builder.store(temp_val, loop_var)
    ctx.builder.branch(cond_block)

    ctx.builder.position_at_end(end_block)

    ctx.close_scope()


def generate_for_iterable(loop, ctx):
    ''' Generate the IR for a for x in iterable loop '''
    seqof_asn1ty = ctx.basic_asn1type_of(loop['list'].exprType)
    is_variable_size = seqof_asn1ty.Min != seqof_asn1ty.Max

    func = ctx.builder.basic_block.function

    # block for loading the value from the secuence
    # at the current index, incrementing the index afterwards
    load_block = func.append_basic_block('forin:load')
    # block for the body of the loop
    body_block = func.append_basic_block('forin:body')
    # block for checking if should loop again or terminate
    cond_block = func.append_basic_block('forin:cond')
    end_block = func.append_basic_block('forin:end')

    ctx.open_scope()

    idx_ptr = ctx.builder.alloca(ctx.i32)
    ctx.builder.store(lc.Constant.int(ctx.i32, 0), idx_ptr)
    seqof_val = expression(loop['list'], ctx)

    if isinstance(seqof_val, SDLSubstringValue):
        array_ptr = seqof_val.arr_ptr
    elif is_variable_size:
        array_ptr = ctx.builder.gep(seqof_val, [ctx.zero, ctx.one])
    else:
        array_ptr = ctx.builder.gep(seqof_val, [ctx.zero, ctx.zero])

    elem_llty = array_ptr.type.pointee.element

    if isinstance(seqof_val, SDLSubstringValue):
        end_idx = seqof_val.count_val
    elif is_variable_size:
        # load the current number of elements that is on the first field
        end_idx = ctx.builder.load(ctx.builder.gep(seqof_val, [ctx.zero, ctx.zero]))
    else:
        end_idx = lc.Constant.int(ctx.i32, array_ptr.type.pointee.count)

    var_ptr = ctx.builder.alloca(elem_llty, None, str(loop['var']))
    ctx.scope.define(str(loop['var']), var_ptr)

    ctx.builder.branch(load_block)

    # load block
    ctx.builder.position_at_end(load_block)
    idx_var = ctx.builder.load(idx_ptr)
    if elem_llty.kind == lc.TYPE_STRUCT:
        elem_ptr = ctx.builder.gep(array_ptr, [ctx.zero, idx_var])
        sdl_assign(var_ptr, elem_ptr, ctx)
    else:
        elem_val = ctx.builder.load(ctx.builder.gep(array_ptr, [ctx.zero, idx_var]))
        sdl_assign(var_ptr, elem_val, ctx)
    ctx.builder.branch(body_block)

    # body block
    ctx.builder.position_at_end(body_block)
    generate(loop['transition'], ctx)
    ctx.builder.branch(cond_block)

    # cond block
    ctx.builder.position_at_end(cond_block)
    tmp_val = ctx.builder.add(idx_var, ctx.one)
    ctx.builder.store(tmp_val, idx_ptr)
    cond_val = ctx.builder.icmp(lc.ICMP_SLT, tmp_val, end_idx)
    ctx.builder.cbranch(cond_val, load_block, end_block)

    ctx.builder.position_at_end(end_block)

    ctx.close_scope()


@singledispatch
def reference(prim, ctx):
    ''' Generate the IR for a reference '''
    raise CompileError('Unsupported reference "%s"' % prim.__class__.__name__)


@reference.register(ogAST.PrimVariable)
def _prim_var_reference(prim, ctx):
    ''' Generate the IR for a variable reference '''
    return ctx.scope.resolve(str(prim.value[0]))


@reference.register(ogAST.PrimSelector)
def _prim_selector_reference(prim, ctx):
    ''' Generate the IR for a field selector referece '''
    receiver_ptr = reference(prim.value[0], ctx)
    field_name = prim.value[1]

    if receiver_ptr.type.pointee.name in ctx.structs:
        struct = ctx.structs[receiver_ptr.type.pointee.name]
        field_idx_cons = lc.Constant.int(ctx.i32, struct.idx(field_name))
        return ctx.builder.gep(receiver_ptr, [ctx.zero, field_idx_cons])

    else:
        union = ctx.unions[receiver_ptr.type.pointee.name]
        _, field_llty = union.kind(field_name)
        field_ptr = ctx.builder.gep(receiver_ptr, [ctx.zero, ctx.one])
        return ctx.builder.bitcast(field_ptr, lc.Type.pointer(field_llty))


@reference.register(ogAST.PrimIndex)
def _prim_index_reference(prim, ctx):
    ''' Generate the IR for an index reference '''
    receiver_val = reference(prim.value[0], ctx)
    idx_val = expression(prim.value[1]['index'][0], ctx)

    basic_asn1ty = ctx.basic_asn1type_of(prim.value[0].exprType)

    if isinstance(receiver_val, SDLSubstringValue):
        return ctx.builder.gep(receiver_val.arr_ptr, [ctx.zero, idx_val])
    elif basic_asn1ty.Min == basic_asn1ty.Max:
        return ctx.builder.gep(receiver_val, [ctx.zero, ctx.zero, idx_val])
    else:
        return ctx.builder.gep(receiver_val, [ctx.zero, ctx.one, idx_val])


@reference.register(ogAST.PrimSubstring)
def _prim_substring_reference(prim, ctx):
    ''' Generate the IR for a substring reference '''
    return SDLSubstringValue(prim, ctx)
#
#   asn1ty = prim.exprType
#   basic_asn1ty = ctx.basic_asn1type_of(asn1ty)
#
#   seqof_val = expression(prim.value[0], ctx)
#
#   low_val = expression(prim.value[1]['substring'][0], ctx)
#   high_val = expression(prim.value[1]['substring'][1], ctx)
#   count_val = ctx.builder.sub(high_val, low_val)
#   count_val = ctx.builder.add(count_val, lc.Constant.int(ctx.i64, 1))
#   count_val = ctx.builder.trunc(count_val, ctx.i32)
#
#   if isinstance(seqof_val, SDLSubstringValue):
#       arr_ptr = seqof_val.arr_ptr
#   elif basic_asn1ty.Min == basic_asn1ty.Max:
#       print 'Here'
#       arr_ptr = ctx.builder.gep(seqof_val, [ctx.zero, ctx.zero])
#   else:
#       print 'Non-Fixed size'
#       arr_ptr = ctx.builder.gep(seqof_val, [ctx.zero, ctx.one])
#
#   arr_ptr_llty = arr_ptr.type
#   print 'will crash?', arr_ptr
#   arr_ptr = ctx.builder.gep(arr_ptr, [ctx.zero, low_val])
#   print 'no!'
#   arr_ptr = ctx.builder.bitcast(arr_ptr, arr_ptr_llty)
#
#   return SDLSubstringValue(arr_ptr, count_val, asn1ty)


@reference.register(ogAST.PrimSequenceOf)
def _prim_sequence_of_reference(prim, ctx):
    ''' Generate the IR for an ASN.1 SEQUENCE OF reference '''
    return SDLSequenceOf(prim)


@reference.register(ogAST.ExprAppend)
def _expr_append_reference(expr, ctx):
    ''' Generate the IR for an append reference '''
    apnd = SDLAppendValue()
    # Append expressions can be recursive -> Flatten them
    if isinstance(expr.left, ogAST.ExprAppend):
        # Get an SDLAppendValue for recursive Append constructs
        inner_left = expression(expr.left, ctx)
        apnd.apnd_list.extend(inner_left.apnd_list)
    else:
        apnd.apnd_list.append(expr.left)
    if isinstance(expr.right, ogAST.ExprAppend):
        inner_right = expression(expr.right, ctx)
        apnd.apnd_list.extend(inner_right.apnd_list)
    else:
        apnd.apnd_list.append(expr.right)

    apnd.exprType = expr.exprType
    return apnd


@reference.register(ogAST.PrimStringLiteral)
def _prim_str_literal_reference(prim, ctx):
    ''' Generate the IR for a raw string reference '''
    return SDLStringLiteral(str(prim.value[1:-1]),
                            len(str(prim.value[1:-1])),
                            prim.exprType)


@singledispatch
def expression(expr, ctx):
    ''' Generate the IR for an expression node '''
    raise CompileError('Unsupported expression "%s"' % expr.__class__.__name__)


@expression.register(ogAST.ExprPlus)
@expression.register(ogAST.ExprMul)
@expression.register(ogAST.ExprMinus)
@expression.register(ogAST.ExprDiv)
@expression.register(ogAST.ExprMod)
@expression.register(ogAST.ExprRem)
def _expr_arith(expr, ctx):
    ''' Generate the IR for an arithmetic expression '''
    left_val = expression(expr.left, ctx)
    right_val = expression(expr.right, ctx)

    basic_asn1ty = ctx.basic_asn1type_of(expr.exprType)

    if basic_asn1ty.kind in ('IntegerType', 'Integer32Type'):
        if isinstance(expr, ogAST.ExprPlus):
            return ctx.builder.add(left_val, right_val)
        elif isinstance(expr, ogAST.ExprMinus):
            return ctx.builder.sub(left_val, right_val)
        elif isinstance(expr, ogAST.ExprMul):
            return ctx.builder.mul(left_val, right_val)
        elif isinstance(expr, ogAST.ExprDiv):
            return ctx.builder.sdiv(left_val, right_val)
        elif isinstance(expr, ogAST.ExprMod):
            # l mod r == (((l rem r) + r) rem r)
            rem_val = ctx.builder.srem(left_val, right_val)
            add_val = ctx.builder.add(rem_val, right_val)
            return ctx.builder.srem(add_val, right_val)
        elif isinstance(expr, ogAST.ExprRem):
            return ctx.builder.srem(left_val, right_val)
        raise CompileError(
            'Expression "%s" not supported for Integer types'
            % expr.__class__.__name__)

    elif basic_asn1ty.kind == 'RealType':
        if isinstance(expr, ogAST.ExprPlus):
            return ctx.builder.fadd(left_val, right_val)
        elif isinstance(expr, ogAST.ExprMinus):
            return ctx.builder.fsub(left_val, right_val)
        elif isinstance(expr, ogAST.ExprMul):
            return ctx.builder.fmul(left_val, right_val)
        elif isinstance(expr, ogAST.ExprDiv):
            return ctx.builder.fdiv(left_val, right_val)
        raise CompileError(
            'Expression "%s" not supported for Real types'
            % expr.__class__.__name__)

    raise CompileError(
        'Type "%s" not supported in arithmetic expressions' % basic_asn1ty.kind)


@expression.register(ogAST.ExprLt)
@expression.register(ogAST.ExprLe)
@expression.register(ogAST.ExprGe)
@expression.register(ogAST.ExprGt)
def _expr_rel(expr, ctx):
    ''' Generate the IR for a relational expression '''
    left_val = expression(expr.left, ctx)
    right_val = expression(expr.right, ctx)

    basic_asn1ty = ctx.basic_asn1type_of(expr.left.exprType)

    if basic_asn1ty.kind in ('IntegerType', 'Integer32Type'):
        if isinstance(expr, ogAST.ExprLt):
            return ctx.builder.icmp(lc.ICMP_SLT, left_val, right_val)
        elif isinstance(expr, ogAST.ExprLe):
            return ctx.builder.icmp(lc.ICMP_SLE, left_val, right_val)
        elif isinstance(expr, ogAST.ExprGe):
            return ctx.builder.icmp(lc.ICMP_SGE, left_val, right_val)
        elif isinstance(expr, ogAST.ExprGt):
            return ctx.builder.icmp(lc.ICMP_SGT, left_val, right_val)
        raise CompileError(
            'Expression "%s" not supported for Integer types'
            % expr.__class__.__name__)

    elif basic_asn1ty.kind == 'RealType':
        if isinstance(expr, ogAST.ExprLt):
            return ctx.builder.fcmp(lc.FCMP_OLT, left_val, right_val)
        elif isinstance(expr, ogAST.ExprLe):
            return ctx.builder.fcmp(lc.FCMP_OLE, left_val, right_val)
        elif isinstance(expr, ogAST.ExprGe):
            return ctx.builder.fcmp(lc.FCMP_OGE, left_val, right_val)
        elif isinstance(expr, ogAST.ExprGt):
            return ctx.builder.fcmp(lc.FCMP_OGT, left_val, right_val)
        raise CompileError(
            'Expression "%s" not supported for Real types'
            % expr.__class__.__name__)

    raise CompileError(
        'Expression "%s" not supported for type "%s"'
        % (expr.__class__.__name__, basic_asn1ty.kind))


@expression.register(ogAST.ExprEq)
@expression.register(ogAST.ExprNeq)
def _expr_eq(expr, ctx):
    ''' Generate the code for a equality expression '''
    left_val = expression(expr.left, ctx)
    right_val = expression(expr.right, ctx)
    asn1ty = expr.left.exprType
    if isinstance(right_val, (SDLStringLiteral, SDLSequenceOf,
                              SDLAppendValue, SDLSubstringValue)):
        # Propagate left type before processing the right side
        right_val.typeof = asn1ty

    if isinstance(expr, ogAST.ExprEq):
        return sdl_equals(left_val, right_val, asn1ty, ctx)
    else:
        return sdl_not_equals(left_val, right_val, asn1ty, ctx)


@expression.register(ogAST.ExprNeg)
def _expr_neg(expr, ctx):
    ''' Generate the IR for a negative expression '''
    expr_val = expression(expr.expr, ctx)
    if expr_val.type.kind == lc.TYPE_INTEGER:
        zero_val = lc.Constant.int(ctx.i64, 0)
        return ctx.builder.sub(zero_val, expr_val)
    else:
        zero_val = lc.Constant.real(ctx.double, 0)
        return ctx.builder.fsub(zero_val, expr_val)


@expression.register(ogAST.ExprAssign)
def _expr_assign(expr, ctx):
    ''' Generate the IR for an assign expression '''
    right = expression(expr.right, ctx)
    if isinstance(right, (SDLStringLiteral, SDLSequenceOf,
                          SDLAppendValue, SDLSubstringValue)):
        # Propagate left type before processing the right side
        right.typeof = expr.left.exprType
    sdl_assign(reference(expr.left, ctx), right, ctx)


@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
@expression.register(ogAST.ExprImplies)
def _expr_logic(expr, ctx):
    ''' Generate the IR for a logic expression '''
    basic_asn1ty = ctx.basic_asn1type_of(expr.exprType)

    if expr.shortcircuit:
        if basic_asn1ty.kind != 'BooleanType':
            raise CompileError('Type "%s" not supported in shortcircuit expressions'
                % basic_asn1ty.kind)

        func = ctx.builder.basic_block.function

        right_block = func.append_basic_block('%s:right' % expr.operand)
        end_block = func.append_basic_block('%s:end' % expr.operand)

        res_ptr = ctx.builder.alloca(ctx.i1)
        left_val = expression(expr.left, ctx)
        ctx.builder.store(left_val, res_ptr)

        if isinstance(expr, ogAST.ExprAnd):
            ctx.builder.cbranch(left_val, right_block, end_block)
        elif isinstance(expr, ogAST.ExprOr):
            ctx.builder.cbranch(left_val, end_block, right_block)
        else:
            raise CompileError('Unknown shortcircuit operator "%s"' % expr.operand)

        ctx.builder.position_at_end(right_block)
        right_val = expression(expr.right, ctx)
        ctx.builder.store(right_val, res_ptr)
        ctx.builder.branch(end_block)

        ctx.builder.position_at_end(end_block)
        return ctx.builder.load(res_ptr)

    elif basic_asn1ty.kind == 'BooleanType':
        left_val = expression(expr.left, ctx)
        right_val = expression(expr.right, ctx)

        if isinstance(expr, ogAST.ExprAnd):
            return ctx.builder.and_(left_val, right_val)
        elif isinstance(expr, ogAST.ExprOr):
            return ctx.builder.or_(left_val, right_val)
        elif isinstance(expr, ogAST.ExprXor):
            return ctx.builder.xor(left_val, right_val)
        else:
            tmp_val = ctx.builder.and_(left_val, right_val)
            return ctx.builder.or_(tmp_val, ctx.builder.not_(left_val))

    elif basic_asn1ty.kind == 'SequenceOfType' and basic_asn1ty.Min == basic_asn1ty.Max:
        func = ctx.builder.basic_block.function

        body_block = func.append_basic_block('bitwise:body')
        next_block = func.append_basic_block('bitwise:next')
        end_block = func.append_basic_block('bitwise:end')

        left_ptr = expression(expr.left, ctx)
        right_ptr = expression(expr.right, ctx)
        res_ptr = ctx.builder.alloca(left_ptr.type.pointee)

        array_llty = res_ptr.type.pointee.elements[0]
        len_val = lc.Constant.int(ctx.i32, array_llty.count)

        idx_ptr = ctx.builder.alloca(ctx.i32)
        ctx.builder.store(lc.Constant.int(ctx.i32, 0), idx_ptr)

        ctx.builder.branch(body_block)

        # body block
        ctx.builder.position_at_end(body_block)
        idx_val = ctx.builder.load(idx_ptr)

        left_elem_ptr = ctx.builder.gep(left_ptr, [ctx.zero, ctx.zero, idx_val])
        left_elem_val = ctx.builder.load(left_elem_ptr)

        right_elem_ptr = ctx.builder.gep(right_ptr, [ctx.zero, ctx.zero, idx_val])
        right_elem_val = ctx.builder.load(right_elem_ptr)

        if isinstance(expr, ogAST.ExprAnd):
            res_elem_val = ctx.builder.and_(left_elem_val, right_elem_val)
        elif isinstance(expr, ogAST.ExprOr):
            res_elem_val = ctx.builder.or_(left_elem_val, right_elem_val)
        elif isinstance(expr, ogAST.ExprXor):
            res_elem_val = ctx.builder.xor(left_elem_val, right_elem_val)
        else:
            tmp_val = ctx.builder.and_(left_elem_val, right_elem_val)
            res_elem_val = ctx.builder.or_(tmp_val, ctx.builder.not_(left_elem_val))

        res_elem_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero, idx_val])
        ctx.builder.store(res_elem_val, res_elem_ptr)

        ctx.builder.branch(next_block)

        # next block
        ctx.builder.position_at_end(next_block)
        idx_tmp_val = ctx.builder.add(idx_val, ctx.one)
        ctx.builder.store(idx_tmp_val, idx_ptr)
        end_cond_val = ctx.builder.icmp(lc.ICMP_SGE, idx_tmp_val, len_val)
        ctx.builder.cbranch(end_cond_val, end_block, body_block)

        # end block
        ctx.builder.position_at_end(end_block)
        return res_ptr

    raise CompileError('Type "%s" not supported in bitwise expressions'
        % basic_asn1ty.kind)


@expression.register(ogAST.ExprNot)
def _expr_not(expr, ctx):
    ''' Generate the IR for a not expression '''
    basic_asn1ty = ctx.basic_asn1type_of(expr.exprType)

    if isinstance(expr.expr, ogAST.PrimSequenceOf):
        # Raw sequence of boolean (e.g. not "{true, false}") -> flip values
        for each in expr.expr.value:
            each.value[0] = 'true' if each.value[0] == 'false' else 'false'
        return expression(expr.expr, ctx)

    if basic_asn1ty.kind == 'BooleanType':
        return ctx.builder.not_(expression(expr.expr, ctx))

    elif basic_asn1ty.kind == 'SequenceOfType': # and basic_asn1ty.Min == basic_asn1ty.Max:
        func = ctx.builder.basic_block.function

        body_block = func.append_basic_block('not:body')
        next_block = func.append_basic_block('not:next')
        end_block = func.append_basic_block('not:end')

        idx_ptr = ctx.builder.alloca(ctx.i32)
        ctx.builder.store(lc.Constant.int(ctx.i32, 0), idx_ptr)

        struct_ptr = expression(expr.expr, ctx)
        if basic_asn1ty.Min != basic_asn1ty.Max:
            len_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero])
            len_val = ctx.builder.load(len_ptr)
        else:
            array_llty = struct_ptr.type.pointee.elements[0]
            len_val = lc.Constant.int(ctx.i32, array_llty.count)
        res_struct_ptr = ctx.builder.alloca(struct_ptr.type.pointee)

        ctx.builder.branch(body_block)

        ctx.builder.position_at_end(body_block)
        idx_val = ctx.builder.load(idx_ptr)

        elem_idxs = [ctx.zero, ctx.zero if basic_asn1ty.Min == basic_asn1ty.Max else ctx.one, idx_val]

        elem_ptr = ctx.builder.gep(struct_ptr, elem_idxs)
        elem_val = ctx.builder.load(elem_ptr)
        res_elem_val = ctx.builder.not_(elem_val)
        res_elem_ptr = ctx.builder.gep(res_struct_ptr, elem_idxs)
        ctx.builder.store(res_elem_val, res_elem_ptr)

        ctx.builder.branch(next_block)

        ctx.builder.position_at_end(next_block)
        idx_tmp_val = ctx.builder.add(idx_val, ctx.one)
        ctx.builder.store(idx_tmp_val, idx_ptr)
        end_cond_val = ctx.builder.icmp(lc.ICMP_SGE, idx_tmp_val, len_val)
        ctx.builder.cbranch(end_cond_val, end_block, body_block)

        ctx.builder.position_at_end(end_block)
        return res_struct_ptr

    raise CompileError('Type "%s" not supported in bitwise expressions'
        % basic_asn1ty.kind)


@expression.register(ogAST.ExprAppend)
def _expr_append(expr, ctx):
    ''' Generate the IR for an append expression '''
    return reference(expr, ctx)

#@expression.register(ogAST.ExprAppend)
#def _expr_append(expr, ctx):
#   ''' Generate the IR for a append expression '''
#   basic_asn1ty = ctx.basic_asn1type_of(expr.exprType)
#
#   if basic_asn1ty.kind in ('SequenceOfType', 'OctetStringType'):
#       res_llty = ctx.lltype_of(expr.exprType)
#       elem_llty = res_llty.elements[1].element
#       elem_size_val = lc.Constant.sizeof(elem_llty)
#
#       res_ptr = ctx.builder.alloca(res_llty)
#       res_len_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero])
#       res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.one])
#
#       left_ptr = expression(expr.left, ctx)
#       if isinstance(left_ptr, SDLSubstringValue):
#           left_arr_ptr = left_ptr.arr_ptr
#           left_count_val = left_ptr.count_val
#       else:
#           left_len_ptr = ctx.builder.gep(left_ptr, [ctx.zero, ctx.zero])
#           left_arr_ptr = ctx.builder.gep(left_ptr, [ctx.zero, ctx.one])
#           left_count_val = ctx.builder.load(left_len_ptr)
#
#       right_ptr = expression(expr.right, ctx)
#       if isinstance(right_ptr, SDLSubstringValue):
#           right_arr_ptr = right_ptr.arr_ptr
#           right_count_val = right_ptr.count_val
#       else:
#           right_len_ptr = ctx.builder.gep(right_ptr, [ctx.zero, ctx.zero])
#           right_arr_ptr = ctx.builder.gep(right_ptr, [ctx.zero, ctx.one])
#           right_count_val = ctx.builder.load(right_len_ptr)
#
#       res_len_val = ctx.builder.add(left_count_val, right_count_val)
#       ctx.builder.store(res_len_val, res_len_ptr)
#
#       sdl_call('memcpy', [
#           ctx.builder.bitcast(res_arr_ptr, ctx.i8_ptr),
#           ctx.builder.bitcast(left_arr_ptr, ctx.i8_ptr),
#           ctx.builder.mul(elem_size_val, ctx.builder.zext(left_count_val, ctx.i64)),
#           lc.Constant.int(ctx.i32, 0),
#           lc.Constant.int(ctx.i1, 0)
#       ], ctx)
#
#       res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.one, left_count_val])
#
#       sdl_call('memcpy', [
#           ctx.builder.bitcast(res_arr_ptr, ctx.i8_ptr),
#           ctx.builder.bitcast(right_arr_ptr, ctx.i8_ptr),
#           ctx.builder.mul(elem_size_val, ctx.builder.zext(right_count_val, ctx.i64)),
#           lc.Constant.int(ctx.i32, 0),
#           lc.Constant.int(ctx.i1, 0)
#       ], ctx)
#
#       return res_ptr
#
#   raise CompileError('Type "%s" not supported in append expressions'
#       % basic_asn1ty.kind)


@expression.register(ogAST.ExprIn)
def _expr_in(expr, ctx):
    ''' Generate the IR for an in expression '''
    func = ctx.builder.basic_block.function

    next_block = func.append_basic_block('in:next')
    check_block = func.append_basic_block('in:check')
    end_block = func.append_basic_block('in:end')

    seqof_basic_asn1ty = ctx.basic_asn1type_of(expr.left.exprType)
    elem_asn1ty = seqof_basic_asn1ty.type

    is_variable_size = seqof_basic_asn1ty.Min != seqof_basic_asn1ty.Max

    idx_ptr = ctx.builder.alloca(ctx.i32)
    ctx.builder.store(lc.Constant.int(ctx.i32, 0), idx_ptr)

    value_val = expression(expr.right, ctx)
    seqof_val = expression(expr.left, ctx)

    if isinstance(seqof_val, SDLSubstringValue):
        end_idx = seqof_val.count_val
    elif is_variable_size:
        # load the current number of elements from the first field
        end_idx = ctx.builder.load(ctx.builder.gep(seqof_val, [ctx.zero, ctx.zero]))
    else:
        array_llty = seqof_val.type.pointee.elements[0]
        end_idx = lc.Constant.int(ctx.i32, array_llty.count)

    ctx.builder.branch(check_block)

    ctx.builder.position_at_end(check_block)
    idx_val = ctx.builder.load(idx_ptr)

    if isinstance(seqof_val, SDLSubstringValue):
        elem_ptr = ctx.builder.gep(seqof_val.arr_ptr, [ctx.zero, idx_val])
    elif is_variable_size:
        elem_ptr = ctx.builder.gep(seqof_val, [ctx.zero, ctx.one, idx_val])
    else:
        elem_ptr = ctx.builder.gep(seqof_val, [ctx.zero, ctx.zero, idx_val])

    if is_struct_ptr(elem_ptr):
        cond_val = sdl_equals(value_val, elem_ptr, elem_asn1ty, ctx)
    else:
        elem_val = ctx.builder.load(elem_ptr)
        cond_val = sdl_equals(value_val, elem_val, elem_asn1ty, ctx)

    ctx.builder.cbranch(cond_val, end_block, next_block)

    ctx.builder.position_at_end(next_block)
    idx_tmp_val = ctx.builder.add(idx_val, ctx.one)
    ctx.builder.store(idx_tmp_val, idx_ptr)
    end_cond_val = ctx.builder.icmp(lc.ICMP_SGE, idx_tmp_val, end_idx)
    ctx.builder.cbranch(end_cond_val, end_block, check_block)

    ctx.builder.position_at_end(end_block)
    return cond_val


@expression.register(ogAST.PrimVariable)
def _prim_variable(prim, ctx):
    ''' Generate the IR for a variable expression '''
    var_ptr = reference(prim, ctx)
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimSelector)
def _prim_selector(prim, ctx):
    ''' Generate the IR for a selector expression '''
    var_ptr = reference(prim, ctx)
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimIndex)
def _prim_index(prim, ctx):
    ''' Generate the IR for an index expression '''
    var_ptr = reference(prim, ctx)
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimSubstring)
def _prim_substring(prim, ctx):
    ''' Generate the IR for a substring expression '''
    return reference(prim, ctx)


@expression.register(ogAST.PrimCall)
def _prim_call(prim, ctx):
    ''' Generate the IR for a call expression '''
    name = prim.value[0].lower()
    args = prim.value[1]['procParams']
    arg_vals = [expression(arg, ctx) for arg in args]

    if name == 'abs':
        return sdl_abs(arg_vals[0], ctx)
    elif name == 'ceil':
        return sdl_ceil(arg_vals[0], ctx)
    elif name == 'cos':
        return sdl_cos(arg_vals[0], ctx)
    elif name == 'fix':
        return sdl_fix(arg_vals[0], ctx)
    elif name == 'float':
        return sdl_float(arg_vals[0], ctx)
    elif name == 'floor':
        return sdl_floor(arg_vals[0], ctx)
    elif name == 'length':
        return sdl_length(arg_vals[0], args[0].exprType, ctx)
    elif name == 'num':
        return sdl_num(arg_vals[0], ctx)
    elif name == 'power':
        return sdl_power(arg_vals[0], arg_vals[1], ctx)
    elif name == 'present':
        return sdl_present(arg_vals[0], ctx)
    elif name == 'round':
        return sdl_round(arg_vals[0], ctx)
    elif name == 'sin':
        return sdl_sin(arg_vals[0], ctx)
    elif name == 'sqrt':
        return sdl_sqrt(arg_vals[0], ctx)
    elif name == 'trunc':
        return sdl_trunc(arg_vals[0], ctx)

    raise CompileError('Unknown operator %s' % name)


@expression.register(ogAST.PrimEnumeratedValue)
def _prim_enumerated_value(prim, ctx):
    ''' Generate the IR for an enumerated value '''
    enumerant = prim.value[0].replace('_', '-').lower()
    basic_asn1ty = ctx.basic_asn1type_of(prim.exprType)
    for each in basic_asn1ty.EnumValues:
        if each.lower() == enumerant:
            break
    return lc.Constant.int(ctx.i32, basic_asn1ty.EnumValues[each].IntValue)


@expression.register(ogAST.PrimChoiceDeterminant)
def _prim_choice_determinant(prim, ctx):
    ''' Generate the IR for a choice determinant (enumerated) '''
    enumerant = prim.value[0].replace('-', '_')
    return ctx.enums[enumerant.lower()]


@expression.register(ogAST.PrimInteger)
def _prim_integer(prim, ctx):
    ''' Generate the IR for a raw integer value '''
    return lc.Constant.int(ctx.i64, prim.value[0])


@expression.register(ogAST.PrimReal)
def _prim_real(prim, ctx):
    ''' Generate the IR for a raw real value '''
    return lc.Constant.real(ctx.double, prim.value[0])


@expression.register(ogAST.PrimBoolean)
def _prim_boolean(prim, ctx):
    ''' Generate the IR for a raw boolean value '''
    if prim.value[0].lower() == 'true':
        return lc.Constant.int(ctx.i1, 1)
    else:
        return lc.Constant.int(ctx.i1, 0)


@expression.register(ogAST.PrimEmptyString)
def _prim_empty_string(prim, ctx):
    ''' Generate the IR for an empty SEQUENCE OF '''
    struct_llty = ctx.lltype_of(prim.exprType)
    struct_ptr = ctx.builder.alloca(struct_llty)
    ctx.builder.store(lc.Constant.null(struct_llty), struct_ptr)
    return struct_ptr


@expression.register(ogAST.PrimStringLiteral)
def _prim_string_literal(prim, ctx):
    ''' Generate the IR for a string'''
    return reference(prim, ctx)


@expression.register(ogAST.PrimConstant)
def _prim_constant(prim, ctx):
    ''' Generate the IR for a reference to an ASN.1 constant '''
    var_ptr = ctx.global_scope.resolve(prim.value[0])
    return var_ptr if is_struct_ptr(var_ptr) else ctx.builder.load(var_ptr)


@expression.register(ogAST.PrimMantissaBaseExp)
def _prim_mantissa_base_exp(prim, ctx):
    ''' Generate the IR for a Real with Mantissa-Base-Exponent representation '''
    mantissa = int(prim.value['mantissa'])
    base = int(prim.value['base'])
    exponent = int(prim.value['exponent'])

    return lc.Constant.real(ctx.double, (mantissa * base) ** exponent)


@expression.register(ogAST.PrimConditional)
def _prim_conditional(prim, ctx):
    ''' Generate the IR for conditional expression '''
    func = ctx.builder.basic_block.function

    true_block = func.append_basic_block('cond:true')
    false_block = func.append_basic_block('cond:false')
    end_block = func.append_basic_block('cond:end')

    res_ptr = ctx.builder.alloca(ctx.lltype_of(prim.exprType))
    cond_val = expression(prim.value['if'], ctx)
    ctx.builder.cbranch(cond_val, true_block, false_block)

    ctx.builder.position_at_end(true_block)
    sdl_assign(res_ptr, expression(prim.value['then'], ctx), ctx)
    ctx.builder.branch(end_block)

    ctx.builder.position_at_end(false_block)
    sdl_assign(res_ptr, expression(prim.value['else'], ctx), ctx)
    ctx.builder.branch(end_block)

    ctx.builder.position_at_end(end_block)

    if is_struct_ptr(res_ptr) or is_array_ptr(res_ptr):
        return res_ptr
    else:
        return ctx.builder.load(res_ptr)


@expression.register(ogAST.PrimSequence)
def _prim_sequence(prim, ctx):
    ''' Generate the IR for an ASN.1 SEQUENCE '''
    struct = ctx.resolve_struct(prim.exprType.ReferencedTypeName)
    struct_ptr = ctx.builder.alloca(struct.llty)

    seq_asn1ty = ctx.dataview[prim.exprType.ReferencedTypeName]

    for field_name, field_expr in prim.value.viewitems():
        # Workaround for unknown types in nested sequences
        #field_expr.exprType = seq_asn1ty.type.Children[field_name.replace('_', '-')].type
        field_expr.exprType = ctx.basic_asn1type_of(prim.exprType).Children[\
                                            field_name.replace('_', '-')].type

        field_idx_cons = lc.Constant.int(ctx.i32, struct.idx(field_name))
        field_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, field_idx_cons])
        right = expression(field_expr, ctx)
        if isinstance(right, (SDLStringLiteral, SDLSequenceOf,
                              SDLAppendValue, SDLSubstringValue)):
            # Propagate left type before processing the right side
            right.typeof = field_expr.exprType
        sdl_assign(field_ptr, right, ctx)

    return struct_ptr


@expression.register(ogAST.PrimSequenceOf)
def _prim_sequence_of(prim, ctx):
    ''' Generate the IR for an ASN.1 SEQUENCE OF '''
    return reference(prim, ctx)


@expression.register(ogAST.PrimChoiceItem)
def _prim_choiceitem(prim, ctx):
    ''' Generate the IR for a CHOICE expression '''
    union = ctx.resolve_union(prim.exprType.ReferencedTypeName)
    union_ptr = ctx.builder.alloca(union.llty)

    expr_val = expression(prim.value['value'], ctx)
    kind_idx, field_llty = union.kind(prim.value['choice'])

    kind_ptr = ctx.builder.gep(union_ptr, [ctx.zero, ctx.zero])
    ctx.builder.store(lc.Constant.int(ctx.i32, kind_idx), kind_ptr)

    field_ptr = ctx.builder.gep(union_ptr, [ctx.zero, ctx.one])
    field_ptr = ctx.builder.bitcast(field_ptr, lc.Type.pointer(field_llty))
    sdl_assign(field_ptr, expr_val, ctx)

    return union_ptr


@generate.register(ogAST.Decision)
def _decision(dec, ctx):
    ''' Generate the IR for a decision '''
    if dec.kind == 'any':
        LOG.warning('LLVM backend does not support the "ANY" statement')
        return
    func = ctx.builder.basic_block.function

    ans_cond_blocks = [func.append_basic_block('dec:ans:cond') for _ in dec.answers]
    end_block = func.append_basic_block('dec:end')

    ctx.builder.branch(ans_cond_blocks[0])

    for idx, ans in enumerate(dec.answers):
        ans_cond_block = ans_cond_blocks[idx]

        if ans.transition:
            true_block = func.append_basic_block('dec:ans:tr')
        else:
            true_block = end_block

        if idx < len(ans_cond_blocks) - 1:
            false_block = ans_cond_blocks[idx + 1]
        else:
            false_block = end_block

        ctx.builder.position_at_end(ans_cond_block)

        if ans.kind in ['constant', 'open_range']:
            expr = ans.openRangeOp()
            expr.left = dec.question
            expr.right = ans.constant
            expr_val = expression(expr, ctx)

            ctx.builder.cbranch(expr_val, true_block, false_block)

        elif ans.kind == 'closed_range':
            q_val = expression(dec.question, ctx)
            low_val = expression(ans.closedRange[0], ctx)
            high_val = expression(ans.closedRange[1], ctx)

            if q_val.type.kind == lc.TYPE_INTEGER:
                low_cond_val = ctx.builder.icmp(lc.ICMP_SGE, q_val, low_val)
                high_cond_val = ctx.builder.icmp(lc.ICMP_SLE, q_val, high_val)
            else:
                low_cond_val = ctx.builder.fcmp(lc.FCMP_OLE, q_val, low_val)
                high_cond_val = ctx.builder.fcmp(lc.FCMP_OGE, q_val, high_val)

            ans_cond_val = ctx.builder.and_(low_cond_val, high_cond_val)
            ctx.builder.cbranch(ans_cond_val, true_block, false_block)

        elif ans.kind == 'else':
            ctx.builder.branch(true_block)

        else:
            raise NotImplementedError

        if ans.transition:
            ctx.builder.position_at_end(true_block)
            generate(ans.transition, ctx)
            if not ctx.builder.basic_block.terminator:
                ctx.builder.branch(end_block)

    ctx.builder.position_at_end(end_block)


@generate.register(ogAST.Label)
def _label(label, ctx):
    ''' Generate the IR for a label '''
    label_block = ctx.scope.label(str(label.inputString))
    ctx.builder.branch(label_block)


@generate.register(ogAST.Transition)
def _transition(tr, ctx):
    ''' Generate the IR for a transition '''
    for action in tr.actions:
        generate(action, ctx)
        if isinstance(action, ogAST.Label):
            return
    if tr.terminator:
        generate_terminator(tr.terminator, ctx)


def generate_terminator(term, ctx):
    ''' Generate the IR for a transition terminator '''
    if term.label:
        raise NotImplementedError

    if term.kind == 'next_state':
        generate_next_state_terminator(term, ctx)
    elif term.kind == 'join':
        generate_join_terminator(term, ctx)
    elif term.kind == 'stop':
        generate_stop_terminator(term, ctx)
    elif term.kind == 'return':
        generate_return_terminator(term, ctx)


def generate_next_state_terminator(term, ctx):
    ''' Generate the IR for a next state transition terminator '''
    state = term.inputString.lower()
    if state.strip() != '-':
        if type(term.next_id) is int:
            next_id_val = lc.Constant.int(ctx.i32, term.next_id)
            if term.next_id == -1:
                global_state_ptr = ctx.global_scope.resolve('.state')
                ctx.builder.store(ctx.states[state.lower()], global_state_ptr)
        else:
            next_id_val = ctx.states[term.next_id.lower()]
        ctx.builder.store(next_id_val, ctx.scope.resolve('id'))
    else:
        nexts = [(n, s) for (n, s) in term.candidate_id.viewitems() if n != -1]
        if nexts:
            # Calculate next transition id in base of the current state
            func = ctx.builder.basic_block.function
            curr_state_val = ctx.builder.load(ctx.global_scope.resolve('.state'))
            default_case_block = func.append_basic_block('term:default')
            end_block = func.append_basic_block('term:end')
            switch = ctx.builder.switch(curr_state_val, default_case_block)

            for next_state, states in nexts:
                next_id_val = ctx.states[next_state.lower()]
                for state in states:
                    case_block = func.append_basic_block('term:case:%s' % str(state))
                    switch.add_case(ctx.states[state.lower()], case_block)
                    ctx.builder.position_at_end(case_block)
                    ctx.builder.store(next_id_val, ctx.scope.resolve('id'))
                    ctx.builder.branch(end_block)

            ctx.builder.position_at_end(default_case_block)
            next_id_val = lc.Constant.int(ctx.i32, -1)
            ctx.builder.store(next_id_val, ctx.scope.resolve('id'))
            ctx.builder.branch(end_block)

            ctx.builder.position_at_end(end_block)
        else:
            next_id_cons = lc.Constant.int(ctx.i32, -1)
            ctx.builder.store(next_id_cons, ctx.scope.resolve('id'))

    ctx.builder.branch(ctx.scope.label('next_transition'))


def generate_join_terminator(term, ctx):
    ''' Generate the IR for a join transition terminator '''
    label_block = ctx.scope.label(str(term.inputString))
    ctx.builder.branch(label_block)


def generate_stop_terminator(term, ctx):
    ''' Generate the IR for a stop transition terminator '''
    raise NotImplementedError


def generate_return_terminator(term, ctx):
    ''' Generate the IR for a return transition terminator '''
    if term.next_id == -1 and term.return_expr:
        ctx.builder.ret(expression(term.return_expr, ctx))
    elif term.next_id == -1:
        ctx.builder.ret_void()
    else:
        next_id_cons = lc.Constant.int(ctx.i32, term.next_id)
        ctx.builder.store(next_id_cons, ctx.scope.resolve('id'))
        ctx.builder.branch(ctx.scope.label('next_transition'))


@generate.register(ogAST.Floating_label)
def _floating_label(label, ctx):
    ''' Generate the IR for a floating label '''
    label_block = ctx.scope.label(str(label.inputString))
    if not ctx.builder.basic_block.terminator:
        ctx.builder.branch(label_block)
    ctx.builder.position_at_end(label_block)

    if label.transition:
        generate(label.transition, ctx)
    else:
        ctx.builder.ret_void()


@generate.register(ogAST.Procedure)
def _procedure(proc, ctx):
    ''' Generate the IR for a procedure '''
    param_lltys = [lc.Type.pointer(ctx.lltype_of(p['type'])) for p in proc.fpar]
    func = ctx.decl_func(str(proc.inputString), ctx.void, param_lltys)

    if proc.external:
        return

    ctx.open_scope()

    for arg, param in zip(func.args, proc.fpar):
        ctx.scope.define(str(param['name']), arg)

    entry_block = func.append_basic_block('proc:entry')
    ctx.builder = lc.Builder.new(entry_block)

    for name, (ty, expr) in proc.variables.viewitems():
        var_llty = ctx.lltype_of(ty)
        var_ptr = ctx.builder.alloca(var_llty)
        ctx.scope.define(name, var_ptr)
        if expr:
            expr_val = expression(expr, ctx)
            sdl_assign(var_ptr, expr_val, ctx)
        else:
            ctx.builder.store(lc.Constant.null(var_llty), var_ptr)

    Helper.inner_labels_to_floating(proc)

    generate(proc.content.start.transition, ctx)

    for label in proc.content.floating_labels:
        generate(label, ctx)

    ctx.close_scope()

    if not ctx.builder.basic_block.terminator:
        ctx.builder.ret_void()

    func.verify()


def is_struct_ptr(val):
    return val.type.kind == lc.TYPE_POINTER and \
        val.type.pointee.kind == lc.TYPE_STRUCT


def is_array_ptr(val):
    return val.type.kind == lc.TYPE_POINTER and \
        val.type.pointee.kind == lc.TYPE_ARRAY


###############################################################################
# Values


class SDLSubstringValue(object):
    #def __init__(self, arr_ptr, count_val, asn1ty):
    def __init__(self, substring, ctx):
        self.substring = substring
        #self.arr_ptr = arr_ptr
        #self.count_val = count_val
        #self.asn1ty = asn1ty
        self.typeof = None
        self.ctx = ctx
        self.seqof_val = expression(self.substring.value[0], self.ctx)

        self.low_val = expression(self.substring.value[1]['substring'][0], self.ctx)
        high_val = expression(self.substring.value[1]['substring'][1], self.ctx)
        count_val = self.ctx.builder.sub(high_val, self.low_val)
        count_val = self.ctx.builder.add(count_val,
                                         lc.Constant.int(self.ctx.i64, 1))
        self.count_val = self.ctx.builder.trunc(count_val, self.ctx.i32)

    @property
    def arr_ptr(self):
        basic_asn1ty = self.ctx.basic_asn1type_of(self.substring.exprType)
        if self.typeof:
            # When the destination field has a known type
            typeof_bty = self.ctx.basic_asn1type_of(self.typeof)
            Min, Max = typeof_bty.Min, typeof_bty.Max
        else:
            # Unknown, e.g. in a write statement
            # Take the basic type of the variable used in the substring
            typeof_var = self.substring.value[0].exprType
            typeof_bty = self.ctx.basic_asn1type_of(typeof_var)
            Min, Max = typeof_bty.Min, typeof_bty.Max

        if isinstance(self.seqof_val, SDLSubstringValue):
            _arr_ptr = self.seqof_val.arr_ptr
        elif Min == Max:
            _arr_ptr = self.ctx.builder.gep(self.seqof_val, [self.ctx.zero, self.ctx.zero])
        else:
            _arr_ptr = self.ctx.builder.gep(self.seqof_val, [self.ctx.zero, self.ctx.one])
        arr_ptr_llty = _arr_ptr.type
        _arr_ptr = self.ctx.builder.gep(_arr_ptr, [self.ctx.zero, self.low_val])
        _arr_ptr = self.ctx.builder.bitcast(_arr_ptr, arr_ptr_llty)
        return _arr_ptr

class SDLAppendValue(object):
    ''' Store an array concatenation value (e.g. "a//b") '''
    def __init__(self):
        self.apnd_list = []
        self.exprType = None

class SDLStringLiteral(object):
    ''' Store a literal string and its length '''
    def __init__(self, string, length, typeof):
        self.string = string
        self.length = length
        self.typeof = typeof

class SDLSequenceOf(object):
    ''' Store a SEQUENCE OF reference '''
    def __init__(self, seqof):
        self.seqof = seqof
        self.typeof = None
        self.length = len(seqof.value)


###############################################################################
# Operators


def sdl_abs(x_val, ctx):
    ''' Generate the IR for an abs operation '''
    if x_val.type.kind == lc.TYPE_INTEGER:
        expr_conv = ctx.builder.sitofp(x_val, ctx.double)
        res_val = sdl_call('fabs', [expr_conv], ctx)
        return ctx.builder.fptosi(res_val, ctx.i64)
    else:
        return sdl_call('fabs', [x_val], ctx)


def sdl_stringliteral(string, oftype, ctx):
    ''' Return the IR for a string literal, knowing the expected type '''
    basic_asn1ty = ctx.basic_asn1type_of(oftype)

    str_len = len(string)
    str_ptr = ctx.string_ptr(string)

    if basic_asn1ty.kind in ('StringType', 'StandardStringType'):
        return str_ptr

    llty = ctx.lltype_of(oftype)
    octectstr_ptr = ctx.builder.alloca(llty)

    if basic_asn1ty.Min == basic_asn1ty.Max:
        arr_ptr = ctx.builder.gep(octectstr_ptr, [ctx.zero, ctx.zero])
    else:
        arr_ptr = ctx.builder.gep(octectstr_ptr, [ctx.zero, ctx.one])

        # Copy length
        str_len_val = lc.Constant.int(ctx.i32, str_len)
        count_ptr = ctx.builder.gep(octectstr_ptr, [ctx.zero, ctx.zero])
        ctx.builder.store(str_len_val, count_ptr)

    # Copy constant string
    casted_arr_ptr = ctx.builder.bitcast(arr_ptr, ctx.i8_ptr)
    casted_str_ptr = ctx.builder.bitcast(str_ptr, ctx.i8_ptr)

    size = lc.Constant.int(ctx.i64, str_len)
    align = lc.Constant.int(ctx.i32, 0)
    volatile = lc.Constant.int(ctx.i1, 0)

    sdl_call('memcpy', [casted_arr_ptr, casted_str_ptr, size, align, volatile], ctx)

    return octectstr_ptr


def sdl_sequenceof(seqof, ctx):
    ''' Return the IR of a SEQUENCE OF, knowing the expected type '''
    basic_asn1ty = ctx.basic_asn1type_of(seqof.typeof)
    llty = ctx.lltype_of(seqof.typeof)
    struct_ptr = ctx.builder.alloca(llty)

    is_variable_size = basic_asn1ty.Min != basic_asn1ty.Max

    if is_variable_size:
        count_val = lc.Constant.int(ctx.i32, seqof.length)
        count_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero])
        ctx.builder.store(count_val, count_ptr)
        array_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.one])
    else:
        array_ptr = ctx.builder.gep(struct_ptr, [ctx.zero, ctx.zero])

    for idx, expr in enumerate(seqof.seqof.value):
        idx_cons = lc.Constant.int(ctx.i32, idx)
        expr_val = expression(expr, ctx)
        pos_ptr = ctx.builder.gep(array_ptr, [ctx.zero, idx_cons])
        sdl_assign(pos_ptr, expr_val, ctx)

    return struct_ptr


def sdl_assign(a_ptr, b_val, ctx):
    ''' Generate the IR for an Assign operation '''
    if isinstance(b_val, SDLSubstringValue):
        basic_asn1ty = ctx.basic_asn1type_of(b_val.typeof) #asn1ty)

        size = ctx.builder.zext(b_val.count_val, ctx.i64)
        align = lc.Constant.int(ctx.i32, 0)
        volatile = lc.Constant.int(ctx.i1, 0)

        a_count_ptr = ctx.builder.gep(a_ptr, [ctx.zero, ctx.zero])
        if basic_asn1ty.Min == basic_asn1ty.Max:
            a_arr_ptr = ctx.builder.gep(a_ptr, [ctx.zero, ctx.zero])
        else:
            a_arr_ptr = ctx.builder.gep(a_ptr, [ctx.zero, ctx.one])

        a_arr_ptr = ctx.builder.bitcast(a_arr_ptr, ctx.i8_ptr)
        b_arr_ptr = ctx.builder.bitcast(b_val.arr_ptr, ctx.i8_ptr)

        sdl_call('memcpy', [a_arr_ptr, b_arr_ptr, size, align, volatile], ctx)
        if basic_asn1ty.Min != basic_asn1ty.Max:
            ctx.builder.store(b_val.count_val, a_count_ptr)

    elif isinstance(b_val, SDLAppendValue):
        #bty = ctx.basic_asn1type_of(b_val.exprType)
        #res_llty = ctx.lltype_of(b_val.exprType)
        bty = ctx.basic_asn1type_of(b_val.typeof)
        res_llty = ctx.lltype_of(b_val.typeof)
        res_ptr = a_ptr
        total_size = lc.Constant.int(ctx.i32, 0)
        # Get pointer to data and nCount (if any) fields
        if bty.Min != bty.Max:
            res_len_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero])
            res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.one])
            elem_llty = res_llty.elements[1].element
        else:
            # Fixed-size
            res_len_ptr = None
            res_arr_ptr = ctx.builder.gep(res_ptr, [ctx.zero, ctx.zero])
            elem_llty = res_llty.elements[0].element

        # Size of a single element (needed for memcpy):
        elem_size_val = lc.Constant.sizeof(elem_llty)

        # Append (memcpy) each of the elements of the append list
        for each in b_val.apnd_list:
            each_ptr = expression(each, ctx)
            if isinstance(each_ptr, SDLSubstringValue):
                each_arr_ptr = each_ptr.arr_ptr
                each_count_val = each_ptr.count_val
            elif isinstance(each_ptr, SDLStringLiteral):
                each_arr_ptr = ctx.string_ptr(each_ptr.string)
                each_count_val = lc.Constant.int(ctx.i32, int(each_ptr.length))
            elif isinstance(each_ptr, SDLSequenceOf):
                if not each_ptr.typeof:
                    each_ptr.typeof = b_val.typeof #exprType
                each_arr_ptr = sdl_sequenceof(each_ptr, ctx)
                each_count_val = lc.Constant.int(ctx.i32, each_ptr.length)
                if bty.Min != bty.Max:
                    each_arr_ptr = ctx.builder.gep(each_arr_ptr,
                                                   [ctx.zero, ctx.one])
            else:
                each_bty = ctx.basic_asn1type_of(each.exprType)
                if each_bty.Min != each_bty.Max:
                    # Non-fixed size, get pointer to array of element
                    each_len_ptr = ctx.builder.gep(each_ptr,
                                                   [ctx.zero, ctx.zero])
                    each_arr_ptr = ctx.builder.gep(each_ptr,
                                                   [ctx.zero, ctx.one])
                    each_count_val = ctx.builder.load(each_len_ptr)
                else:
                    # Fixed size
                    each_arr_ptr = each_ptr
                    each_count_val = lc.Constant.int(ctx.i32,
                                                     int(each_bty.Min))
            total_size = ctx.builder.add(total_size, each_count_val)
            sdl_call('memcpy', [
                 ctx.builder.bitcast(res_arr_ptr, ctx.i8_ptr),
                 ctx.builder.bitcast(each_arr_ptr, ctx.i8_ptr),
                 ctx.builder.mul(elem_size_val,
                                 ctx.builder.zext(each_count_val, ctx.i64)),
                 lc.Constant.int(ctx.i32, 0),
                 lc.Constant.int(ctx.i1, 0)
             ], ctx)
            # Move pointer to the end of the string for the next element
            res_arr_ptr = ctx.builder.gep(res_ptr,
                                         [ctx.zero,
                                          ctx.one if res_len_ptr else ctx.zero,
                                          total_size])
        if res_len_ptr:
            # Store the resulting size of the concatenation, if needed (nCount)
            ctx.builder.store(total_size, res_len_ptr)

    elif is_struct_ptr(a_ptr) or is_array_ptr(a_ptr):
        size = lc.Constant.sizeof(a_ptr.type.pointee)
        align = lc.Constant.int(ctx.i32, 0)
        volatile = lc.Constant.int(ctx.i1, 0)

        a_ptr = ctx.builder.bitcast(a_ptr, ctx.i8_ptr)
        if isinstance(b_val, SDLStringLiteral):
            b_val = sdl_stringliteral(b_val.string, b_val.typeof, ctx)
        elif isinstance(b_val, SDLSequenceOf):
            b_val = sdl_sequenceof(b_val, ctx)
        b_ptr = ctx.builder.bitcast(b_val, ctx.i8_ptr)

        sdl_call('memcpy', [a_ptr, b_ptr, size, align, volatile], ctx)

    else:
        if isinstance(b_val, SDLStringLiteral):
            b_val = sdl_stringliteral(b_val.string, b_val.typeof, ctx)
        elif isinstance(b_val, SDLSequenceOf):
            b_val = sdl_sequenceof(b_val, ctx)
        ctx.builder.store(b_val, a_ptr)


def sdl_call(name, arg_vals, ctx):
    ''' Generate the IR for a call operation '''
    try:
        return ctx.builder.call(ctx.funcs[name], arg_vals)
    except TypeError as err:
        LOG.error('[sdl_call] - {}'.format(str(err)))


def sdl_ceil(x_val, ctx):
    ''' Generate the IR for a ceil operation '''
    return sdl_call('ceil', [x_val], ctx)


def sdl_cos(x_val, ctx):
    ''' Generate the IR for a cos operation '''
    return sdl_call('cos', [x_val], ctx)


def sdl_equals(a_val, b_val, asn1ty, ctx):
    ''' Generate the code for an Equal operation '''
    basic_asn1ty = ctx.basic_asn1type_of(asn1ty)

    if basic_asn1ty.kind in ('IntegerType', 'Integer32Type', 'BooleanType',
            'EnumeratedType', 'ChoiceEnumeratedType'):
        return ctx.builder.icmp(lc.ICMP_EQ, a_val, b_val)

    elif basic_asn1ty.kind == 'RealType':
        return ctx.builder.fcmp(lc.FCMP_OEQ, a_val, b_val)

    if isinstance(b_val, SDLStringLiteral):
        b_val = sdl_stringliteral(b_val.string, b_val.typeof, ctx)
    elif isinstance(b_val, SDLSequenceOf):
        b_val = sdl_sequenceof(b_val, ctx)

    # XXX add isinstance(b_val, SDLAppend) and SDLSubstring, no?
    # Also in _equals a_val should also be evaluated against special types

    try:
        type_name = asn1ty.ReferencedTypeName.replace('-', '_').lower()
    except AttributeError:
        raise CompileError(
            'Equals operator not supported for type "%s"' % basic_asn1ty.kind)

    return sdl_call("asn1scc%s_equal" % type_name, [a_val, b_val], ctx)


def sdl_fix(x_val, ctx):
    ''' Generate the IR for a fix operation '''
    return ctx.builder.fptosi(x_val, ctx.i64)


def sdl_float(x_val, ctx):
    ''' Generate the IR for a float operation '''
    return ctx.builder.sitofp(x_val, ctx.double)


def sdl_floor(x_val, ctx):
    ''' Generate the IR for a floor operation '''
    return sdl_call('floor', [x_val], ctx)


def sdl_length(s_ptr, s_asn1ty, ctx):
    ''' Generate the IR for a length operation '''
    s_basic_asn1ty = ctx.basic_asn1type_of(s_asn1ty)

    if isinstance(s_ptr, SDLSubstringValue):
        return ctx.builder.zext(s_ptr.count_val, ctx.i64)
    elif s_basic_asn1ty.Min != s_basic_asn1ty.Max:
        len_ptr = ctx.builder.gep(s_ptr, [ctx.zero, ctx.zero])
        return ctx.builder.zext(ctx.builder.load(len_ptr), ctx.i64)
    else:
        arr_llty = s_ptr.type.pointee.elements[0]
        return lc.Constant.int(ctx.i64, arr_llty.count)


def sdl_not_equals(a_val, b_val, asn1ty, ctx):
    ''' Generate the code for a Not Equal operation '''
    return ctx.builder.not_(sdl_equals(a_val, b_val, asn1ty, ctx))


def sdl_num(enum_val, ctx):
    ''' Generate the IR for a num operation'''
    return ctx.builder.sext(enum_val, ctx.i64)


def sdl_power(x_val, y_val, ctx):
    ''' Generate the IR for a power operation '''
    y_val = ctx.builder.trunc(y_val, ctx.i32)
    if x_val.type.kind == lc.TYPE_INTEGER:
        x_val = ctx.builder.sitofp(x_val, ctx.double)
        res_val = sdl_call('powi', [x_val, y_val], ctx)
        return ctx.builder.fptosi(res_val, ctx.i64)
    else:
        return sdl_call('powi', [x_val, y_val], ctx)


def sdl_present(s_ptr, ctx):
    ''' Generate the IR for a present operation '''
    kind_ptr = ctx.builder.gep(s_ptr, [ctx.zero, ctx.zero])
    return ctx.builder.load(kind_ptr)


def sdl_reset_timer(name, ctx):
    ''' Generate the IR a reset timer operation '''
    reset_func_name = 'reset_%s' % name.lower()

    sdl_call(reset_func_name, [], ctx)


def sdl_round(x_val, ctx):
    ''' Generate the IR for a float operation '''
    return sdl_call('round', [x_val], ctx)


def sdl_set_timer(name, val, ctx):
    ''' Generate the IR for a set timer operation '''
    set_func_name = 'set_%s' % name.lower()

    tmp_ptr = ctx.builder.alloca(val.type)
    ctx.builder.store(val, tmp_ptr)

    sdl_call(set_func_name, [tmp_ptr], ctx)


def sdl_sin(x_val, ctx):
    ''' Generate the IR for a sin operation '''
    return sdl_call('sin', [x_val], ctx)


def sdl_sqrt(x_val, ctx):
    ''' Generate the IR for a sqrt operation '''
    return sdl_call('sqrt', [x_val], ctx)


def sdl_trunc(x_val, ctx):
    ''' Generate the IR for a cos operation '''
    return sdl_call('trunc', [x_val], ctx)


def sdl_write(arg_vals, arg_asn1tys, ctx, newline=False):
    ''' Generate the IR for a write operation '''
    fmt = ""
    arg_values = []

    for arg_val, arg_asn1ty in zip(arg_vals, arg_asn1tys):
        basic_asn1ty = ctx.basic_asn1type_of(arg_asn1ty)

        if basic_asn1ty.kind in ['IntegerType', 'Integer32Type']:
            fmt += '% lld'
            arg_values.append(arg_val)

        elif basic_asn1ty.kind == 'RealType':
            fmt += '% .14E'
            arg_values.append(arg_val)

        elif basic_asn1ty.kind == 'BooleanType':
            fmt += '%s'

            true_str_ptr = ctx.string_ptr('TRUE')
            false_str_ptr = ctx.string_ptr('FALSE')
            str_ptr = ctx.builder.select(arg_val, true_str_ptr, false_str_ptr)

            arg_values.append(str_ptr)

        elif basic_asn1ty.kind in ('StringType', 'StandardStringType'):
            fmt += '%s'
            if isinstance(arg_val, SDLStringLiteral):
                arg_val = ctx.string_ptr(arg_val.string)
            arg_values.append(arg_val)

        elif basic_asn1ty.kind == 'OctetStringType':
            fmt += '%.*s'

            if isinstance(arg_val, SDLSubstringValue):
                arr_ptr = arg_val.arr_ptr
                count_val = arg_val.count_val
            elif isinstance(arg_val, SDLStringLiteral):
                arr_ptr = ctx.string_ptr(arg_val.string)
                count_val = lc.Constant.int(ctx.i32, int(arg_val.length))
            elif basic_asn1ty.Min == basic_asn1ty.Max:
                arr_ptr = ctx.builder.gep(arg_val, [ctx.zero, ctx.zero])
                count_val = lc.Constant.int(ctx.i32, arr_ptr.type.pointee.count)
            else:
                arr_ptr = ctx.builder.gep(arg_val, [ctx.zero, ctx.one])
                count_ptr = ctx.builder.gep(arg_val, [ctx.zero, ctx.zero])
                count_val = ctx.builder.load(count_ptr)

            arg_values.append(count_val)
            arg_values.append(arr_ptr)

        else:
            raise CompileError('Type "%s" not supported in write/writeln operators')

    if newline:
        fmt += '\n'

    arg_values.insert(0, ctx.string_ptr(fmt))
    sdl_call('printf', arg_values, ctx)
