#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module is a template for backends such as code generators

    Entry point:
    The AST of the model that is parsed is described in ogAST.py

    A Visitor Pattern using Python's "singledispatch" mechanism is used
    to go through the AST and generate code for each SDL construct.

    There is a single function called "generate", decorated with the
    singledispatch mechanism, that needs to be called to generate the code
    of any AST element.

    Copyright (c) 2012-2014 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from singledispatch import singledispatch

import ogAST

LOG = logging.getLogger(__name__)

__all__ = ['generate']


@singledispatch
def generate(ast):
    ''' Generate the code for an item of the AST '''
    raise TypeError('[Backend] Unsupported AST construct')

# Processing of the AST

@generate.register(ogAST.Process)
def _process(process):
    ''' Generate the code for a complete process (AST Top level) '''
    pass

def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    pass

@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output):
    ''' Generate the code of a set of output or procedure call statement '''
    pass


@generate.register(ogAST.TaskAssign)
def _task_assign(task):
    ''' A list of assignments in a task symbol '''
    pass


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task):
    ''' Generate comments for informal text '''
    pass


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task):
    '''
        Return the code corresponding to a for loop. Two forms are possible:
        for x in range ([start], stop [, step])
        for x in iterable (a SEQUENCE OF)
    '''
    pass


@generate.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Single variable reference '''
    pass


@generate.register(ogAST.PrimPath)
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
    pass


@generate.register(ogAST.ExprPlus)
@generate.register(ogAST.ExprMul)
@generate.register(ogAST.ExprMinus)
@generate.register(ogAST.ExprEq)
@generate.register(ogAST.ExprNeq)
@generate.register(ogAST.ExprGt)
@generate.register(ogAST.ExprGe)
@generate.register(ogAST.ExprLt)
@generate.register(ogAST.ExprLe)
@generate.register(ogAST.ExprDiv)
@generate.register(ogAST.ExprMod)
@generate.register(ogAST.ExprRem)
@generate.register(ogAST.ExprAssign)
def _basic_operators(expr):
    ''' Expressions with two sides '''
    pass


@generate.register(ogAST.ExprOr)
@generate.register(ogAST.ExprAnd)
@generate.register(ogAST.ExprXor)
def _bitwise_operators(expr):
    ''' Logical operators '''
    pass


@generate.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    pass


@generate.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' IN expressions: check if item is in a SEQUENCE OF '''
    pass


@generate.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    pass


@generate.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    pass


@generate.register(ogAST.PrimInteger)
@generate.register(ogAST.PrimReal)
@generate.register(ogAST.PrimBoolean)
def _integer(primary):
    ''' Generate code for a raw integer/real/boolean value  '''
    pass


@generate.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    pass


@generate.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    pass


@generate.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    pass


@generate.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    pass


@generate.register(ogAST.PrimIfThenElse)
def _if_then_else(ifThenElse):
    ''' Return string and statements for ternary operator '''
    pass


@generate.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    pass


@generate.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    pass


@generate.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Return the Ada code for a CHOICE expression '''
    pass


@generate.register(ogAST.Decision)
def _decision(dec):
    ''' generate the code for a decision '''
    pass


@generate.register(ogAST.Label)
def _label(tr):
    ''' Transition following labels are generated in a separate section
        for visibility reasons (see Ada scope)
    '''
    pass


@generate.register(ogAST.Transition)
def _transition(tr):
    ''' generate the code for a transition '''
    pass


@generate.register(ogAST.Floating_label)
def _floating_label(label):
    ''' Generate the code for a floating label (Ada label + transition) '''
    pass


@generate.register(ogAST.Procedure)
def _inner_procedure(proc):
    ''' Generate the code for a procedure '''
    pass
