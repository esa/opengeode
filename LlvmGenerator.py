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
from llvm import core, passes, ee

import ogAST
import Helper

LOG = logging.getLogger(__name__)

__all__ = ['generate']


# LLVM Global variable - Initialized when the generator is invoked
LLVM = {
    # The LLVM module, which holds all the IR code.
    'module': None,
    # Dictionary that keeps track of which values are defined in the current
    # scope and what their LLVM representation is.
    'named_values': {},
    # Dictionary that keeps track of the defined states and its integer
    # constant representation
    'states': {},
    # The builder used for the current function generation.
    'builder': None,
    # The function optimization passes manager.
    'pass_manager': None,
    # The LLVM execution engine.
    'executor': None
}

@singledispatch
def generate(ast):
    ''' Generate the code for an item of the AST '''
    raise TypeError('[Backend] Unsupported AST construct')

# Processing of the AST

@generate.register(ogAST.Process)
def _process(process):
    ''' Generate LLVM IR code (incomplete) '''

    process_name = str(process.processName)
    LOG.info('Generating LLVM IR code for process ' + str(process_name))

    # In case model has nested states, flatten everything
    Helper.flatten(process)

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    # Initialise LLVM global structure
    LLVM['module'] = core.Module.new(process_name)
    LLVM['pass_manager'] = passes.FunctionPassManager.new(LLVM['module'])
    LLVM['executor'] = ee.ExecutionEngine.new(LLVM['module'])
    LLVM['types'] = process.dataview
    # Set up the optimizer pipeline.
    # Start with registering info about how the
    # target lays out data structures.
#   LLVM['pass_manager'].add(LLVM['executor'].target_data)
#   # Do simple "peephole" optimizations and bit-twiddling optzns.
#   LLVM['pass_manager'].add(passes.PASS_INSTRUCTION_COMBINING)
#   # Reassociate expressions.
#   LLVM['pass_manager'].add(passes.PASS_REASSOCIATE)
#   # Eliminate Common SubExpressions.
#   LLVM['pass_manager'].add(passes.PASS_GVN)
#   # Simplify the control flow graph (deleting unreachable blocks, etc).
#   LLVM['pass_manager'].add(passes.PASS_CFG_SIMPLIFICATION)
#   LLVM['pass_manager'].initialize()

    # Initialize states enum
    for name in process.mapping.iterkeys():
        if not name.endswith('START'):
            cons = core.Constant.int(core.Type.int(), len(LLVM['states']))
            LLVM['states'][name] = cons

    # Generate state var
    LLVM['module'].add_global_variable(core.Type.int(), 'state')

    # Generare process-level vars
    for var_name, (var_asn1_type, def_value) in process.variables.viewitems():
        var_type = _generate_type(find_basic_type(var_asn1_type))
        var_ptr = LLVM['module'].add_global_variable(var_type, str(var_name))
        if def_value:
            raise NotImplementedError

    # Generate process functions
    runtr_func = _generate_runtr_func(process)
    _generate_startup_func(process, process_name, runtr_func)

    print LLVM['module']


def _generate_runtr_func(process):
    '''Generate code for the run_transition function'''
    func_name = 'run_transition'
    func_type = core.Type.function(core.Type.void(), [core.Type.int()])
    func = core.Function.new(LLVM['module'], func_type, func_name)

    entry_block = func.append_basic_block('entry')
    cond_block = func.append_basic_block('cond')
    body_block = func.append_basic_block('body')
    exit_block = func.append_basic_block('exit')

    builder = core.Builder.new(entry_block)
    LLVM['builder'] = builder

    # entry
    id_ptr = builder.alloca(core.Type.int(), None, 'id')
    LLVM['named_values']['id'] = id_ptr
    builder.store(func.args[0], id_ptr)
    builder.branch(cond_block)

    # cond
    builder.position_at_end(cond_block)
    id_ptr = func.args[0]
    no_tr_cons = core.Constant.int(core.Type.int(), -1)
    cond_val = builder.icmp(core.ICMP_NE, id_ptr, no_tr_cons, 'cond')
    builder.cbranch(cond_val, body_block, exit_block)

    # body
    builder.position_at_end(body_block)
    switch = builder.switch(func.args[0], exit_block)

    # transitions
    for idx, tr in enumerate(process.transitions):
        tr_block = func.append_basic_block('tr%d' % idx)
        const = core.Constant.int(core.Type.int(), idx)
        switch.add_case(const, tr_block)
        builder.position_at_end(tr_block)
        generate(tr)
        builder.branch(cond_block)

    # exit
    builder.position_at_end(exit_block)
    builder.ret_void()

    func.verify()
    LLVM['named_values'].clear()
    return func


def _generate_startup_func(process, process_name, runtr_func):
    '''Generate code for the startup function'''
    func_name = process_name + '_startup'
    func_type = core.Type.function(core.Type.void(), [])
    func = core.Function.new(LLVM['module'], func_type, func_name)

    entry_block = func.append_basic_block('entry')
    builder = core.Builder.new(entry_block)
    LLVM['builder'] = builder

    # entry
    builder.call(runtr_func, [core.Constant.int(core.Type.int(), 0)])
    builder.ret_void()

    func.verify()
    return func


def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    raise NotImplementedError

@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output):
    ''' Generate the code of a set of output or procedure call statement '''
    raise NotImplementedError


@generate.register(ogAST.TaskAssign)
def _task_assign(task):
    ''' A list of assignments in a task symbol '''
    for expr in task.elems:
        expression(expr)


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task):
    ''' Generate comments for informal text '''
    raise NotImplementedError


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task):
    '''
        Return the code corresponding to a for loop. Two forms are possible:
        for x in range ([start], stop [, step])
        for x in iterable (a SEQUENCE OF)
    '''
    raise NotImplementedError

# ------ expressions --------

@singledispatch
def expression(expr):
    ''' Generate the code for Expression-classes, returning 3 things:
        - list of statements
        - useable string corresponding to the evaluation of the expression,
        - list of local declarations
        (API can differ depending on the backend)
    '''
    raise TypeError('Unsupported expression: ' + str(expr))



@expression.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Single variable reference '''
    return LLVM['module'].get_global_variable_named(str(prim.value[0]))


@expression.register(ogAST.PrimPath)
def _prim_path(primaryId):
    '''
        Return the string of an element list (path)
        cases: a => 'l_a' (reference to a variable)
        a_timer => 'a_timer'  (reference to a timer)
        a!b => a.b (field of a structure)
        a!b if a is a CHOICE => TypeOfa_b_get(a)
        a(Expression) => a(ExpressionSolver) (array index)
        Expression can be complex (if-then-else-fi..)
    '''
    raise NotImplementedError


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
def _basic_operators(expr):
    ''' Expressions with two sides '''
    builder = LLVM['builder']
    lefttmp = expression(expr.left)
    righttmp = expression(expr.right)

    # load the value of the expression if it is a pointer
    if lefttmp.type.kind == core.TYPE_POINTER:
        lefttmp = builder.load(lefttmp, 'lefttmp')
    if righttmp.type.kind == core.TYPE_POINTER:
        righttmp = builder.load(righttmp, 'lefttmp')

    if lefttmp.type.kind != righttmp.type.kind:
        raise NotImplementedError

    if lefttmp.type.kind == core.TYPE_INTEGER:
        if expr.operand == '+':
            return builder.add(lefttmp, righttmp, 'addtmp')
        elif expr.operand == '-':
            return builder.sub(lefttmp, righttmp, 'subtmp')
        elif expr.operand == '*':
            return builder.mul(lefttmp, righttmp, 'multmp')
        elif expr.operand == '/':
            return builder.sdiv(lefttmp, righttmp, 'divtmp')
        elif expr.operand == 'mod':
            # l mod r == (((l rem r) + r) rem r)
            remtmp = builder.srem(lefttmp, righttmp)
            addtmp = builder.add(remtmp, righttmp)
            return builder.srem(addtmp, righttmp, 'modtmp')
        elif expr.operand == 'rem':
            return builder.srem(lefttmp, righttmp, 'remtmp')
        else:
            raise NotImplementedError
    elif lefttmp.type.kind == core.TYPE_DOUBLE:
        if expr.operand == '+':
            return builder.fadd(lefttmp, righttmp, 'addtmp')
        elif expr.operand == '-':
            return builder.fsub(lefttmp, righttmp, 'subtmp')
        elif expr.operand == '*':
            return builder.fmul(lefttmp, righttmp, 'multmp')
        elif expr.operand == '/':
            return builder.fdiv(lefttmp, righttmp, 'divtmp')
        elif expr.operand == 'mod':
            # l mod r == (((l rem r) + r) rem r)
            remtmp = builder.frem(lefttmp, righttmp)
            addtmp = builder.fadd(remtmp, righttmp)
            return builder.frem(addtmp, righttmp, 'modtmp')
        elif expr.operand == 'rem':
            return builder.frem(lefttmp, righttmp, 'remtmp')
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


@expression.register(ogAST.ExprAssign)
def _assign(expr):
    '''Assign expression'''
    builder = LLVM['builder']
    left = expression(expr.left)
    right = expression(expr.right)

    builder.store(right, left)
    return left


@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
def _bitwise_operators(expr):
    ''' Logical operators '''
    builder = LLVM['builder']
    func = builder.basic_block.function

    lefttmp = expression(expr.left)
    righttmp = expression(expr.right)

    ty = find_basic_type(expr.exprType)
    if ty.kind != 'BooleanType':
        raise NotImplementedError

    # load the value of the expression if it is a pointer
    if lefttmp.type.kind == core.TYPE_POINTER:
        lefttmp = builder.load(lefttmp, 'lefttmp')
    if righttmp.type.kind == core.TYPE_POINTER:
        righttmp = builder.load(righttmp, 'lefttmp')

    if expr.operand == '&&':
        return builder.and_(lefttmp, righttmp, 'ortmp')
    elif expr.operand == '||':
        return builder.or_(lefttmp, righttmp, 'ortmp')
    else:
        return builder.xor(lefttmp, righttmp, 'xortmp')



@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    raise NotImplementedError


@expression.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' IN expressions: check if item is in a SEQUENCE OF '''
    raise NotImplementedError


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    raise NotImplementedError


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    raise NotImplementedError


@expression.register(ogAST.PrimInteger)
def _integer(primary):
    ''' Generate code for a raw integer value  '''
    return core.Constant.int(core.Type.int(), primary.value[0])


@expression.register(ogAST.PrimReal)
def _real(primary):
    ''' Generate code for a raw real value  '''
    return core.Constant.real(core.Type.double(), primary.value[0])


@expression.register(ogAST.PrimBoolean)
def _boolean(primary):
    ''' Generate code for a raw boolean value  '''
    if primary.value[0].lower() == 'true':
        return core.Constant.int(core.Type.int(1), 1)
    else:
        return core.Constant.int(core.Type.int(1), 0)


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    raise NotImplementedError


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    raise NotImplementedError


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    raise NotImplementedError


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    raise NotImplementedError


@expression.register(ogAST.PrimIfThenElse)
def _if_then_else(ifThenElse):
    ''' Return string and statements for ternary operator '''
    raise NotImplementedError


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    raise NotImplementedError


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    raise NotImplementedError


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Return the Ada code for a CHOICE expression '''
    raise NotImplementedError


@generate.register(ogAST.Decision)
def _decision(dec):
    ''' generate the code for a decision '''
    raise NotImplementedError


@generate.register(ogAST.Label)
def _label(tr):
    ''' Transition following labels are generated in a separate section
        for visibility reasons (see Ada scope)
    '''
    raise NotImplementedError


@generate.register(ogAST.Transition)
def _transition(tr):
    ''' generate the code for a transition '''
    for action in tr.actions:
        generate(action)
        if isinstance(action, ogAST.Label):
            return
    if tr.terminator:
        _generate_terminator(tr.terminator)


def _generate_terminator(term):
    builder = LLVM['builder']
    id_ptr = LLVM['named_values']['id']
    if term.label:
        raise NotImplementedError
    if term.kind == 'next_state':
        state = term.inputString.lower()
        if state.strip() != '-':
            next_id_cons = core.Constant.int(core.Type.int(), term.next_id)
            builder.store(next_id_cons, id_ptr)
            if term.next_id == -1:
                state_ptr = LLVM['module'].get_global_variable_named('state')
                state_id_cons = LLVM['states'][state]
                builder.store(state_id_cons, state_ptr)
        else:
            raise NotImplementedError
    elif term.kind == 'join':
        raise NotImplementedError
    elif term.kind == 'stop':
        raise NotImplementedError
    elif term.kind == 'return':
        raise NotImplementedError


@generate.register(ogAST.Floating_label)
def _floating_label(label):
    ''' Generate the code for a floating label (Ada label + transition) '''
    raise NotImplementedError


@generate.register(ogAST.Procedure)
def _inner_procedure(proc):
    ''' Generate the code for a procedure '''
    raise NotImplementedError


def _generate_type(ty):
    '''Generate the equivalent LLVM type of a ASN.1 type'''
    basic_ty = find_basic_type(ty)
    if basic_ty.kind == 'IntegerType':
        return core.Type.int()
    elif basic_ty.kind == 'BooleanType':
        return core.Type.int(1)
    elif basic_ty.kind == 'RealType':
        return core.Type.double()
    else:
        raise NotImplementedError


# TODO: Refactor this into the helper module
def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in LLVM['types'].viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = LLVM['types'][typename].type
                break
    return basic_type
