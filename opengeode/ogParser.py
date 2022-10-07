#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE SDL parser

    This library builds the SDL AST (described in ogAST.py)
    The AST can then be used to build SDL backends such as the
    diagram editor (placing symbols in a graphical canvas for edition)
    or code generators, etc.

    The AST build is based on the ANTLR-grammar and generated lexer and parser
    (the grammar is in the file sdl92.g and requires antlr 3.1.3 for Python
    to be compiled and used).

    During the build of the AST this library makes a number of semantic
    checks on the SDL input model.

    Copyright (c) 2012-2022 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__author__ = 'Maxime Perrotin'

import sys
import os
import math
import operator
import logging
import traceback

from functools import partial
import codecs
from typing import Dict, Tuple
from inspect import currentframe, getframeinfo
import binascii
from textwrap import dedent
from itertools import chain, permutations, combinations
from collections import defaultdict, Counter

import antlr3
from antlr3 import tree

from . import sdl92Lexer as lexer
from . import sdl92Parser

from . import ogAST
from .Asn1scc import parse_asn1, ASN1, create_choice_determinant_types

LOG = logging.getLogger(__name__)

EXPR_NODE: Dict[int, ogAST.Expression] = {
    lexer.PLUS:     ogAST.ExprPlus,
    lexer.ASTERISK: ogAST.ExprMul,
    lexer.IMPLIES:  ogAST.ExprImplies,
    lexer.DASH:     ogAST.ExprMinus,
    lexer.OR:       ogAST.ExprOr,
    lexer.AND:      ogAST.ExprAnd,
    lexer.XOR:      ogAST.ExprXor,
    lexer.EQ:       ogAST.ExprEq,
    lexer.NEQ:      ogAST.ExprNeq,
    lexer.GT:       ogAST.ExprGt,
    lexer.GE:       ogAST.ExprGe,
    lexer.LT:       ogAST.ExprLt,
    lexer.LE:       ogAST.ExprLe,
    lexer.DIV:      ogAST.ExprDiv,
    lexer.MOD:      ogAST.ExprMod,
    lexer.APPEND:   ogAST.ExprAppend,
    lexer.IN:       ogAST.ExprIn,
    lexer.REM:      ogAST.ExprRem,
    lexer.NOT:      ogAST.ExprNot,
    lexer.NEG:      ogAST.ExprNeg,
    lexer.PRIMARY:  ogAST.Primary,
}

# Insert current path in the search list for importing modules
sys.path.insert(0, '.')

DV = None  # type: module

# Code generator backends may need some intermediate variables to process
# expressions. For convenience and to avoid multiple pass parsing, the parser
# tries to guess where they may be useful, and adds a hint in the AST.
TMPVAR = 0  # type: int

# ASN.1 types used to support the signature of special operators
INTEGER      = type('IntegerType',    (object,), {'kind': 'IntegerType',
                                                  'Min' : str(-(2 ** 63)),
                                                  'Max' : str(2 ** 63 - 1)})
UNSIGNED     = type('IntegerType',    (object,), {'kind': 'IntegerType',
                                                  'Min' : "0",
                                                  'Max' : str(2 ** 64 - 1)})
INT32        = type('Integer32Type',  (object,), {'kind': 'Integer32Type',
                                                  'Min' : '-2147483648',
                                                  'Max' : '2147483647'})
UINT8        = type('IntegerU8Type',  (object,), {'kind': 'IntegerU8Type',
                                                  'Min' : '0',
                                                  'Max' : '255'})
NUMERICAL    = type('NumericalType',  (object,), {'kind': 'Numerical',
                                                  'Min' : '0',
                                                  'Max' : '0'})
TIMER        = type('TimerType',      (object,), {'kind': 'TimerType'})
REAL         = type('RealType',       (object,), {'kind': 'RealType',
                                                  'Min' : str(-1.0e308),
                                                  'Max' : str(1.0e308)})
LIST         = type('ListType',       (object,), {'kind': 'ListType'})
ANY_TYPE     = type('AnyType',        (object,), {'kind': 'AnyType'})
CHOICE       = type('ChoiceType',     (object,), {'kind': 'ChoiceType'})
BOOLEAN      = type('BooleanType',    (object,), {'kind': 'BooleanType'})
RAWSTRING    = type('RawString',      (object,), {'kind': 'StandardStringType',
                                                  'Min' : '0',
                                                  'Max' : '255'})
OCTETSTRING  = type('OctetString',    (object,), {'kind': 'OctetStringType'})
ENUMERATED   = type('EnumeratedType', (object,), {'kind': 'EnumeratedType'})
UNKNOWN_TYPE = type('UnknownType',    (object,), {'kind': 'UnknownType'})

NewInteger = lambda tMin, tMax: type('IntegerType', (INTEGER,), {
    'kind': 'IntegerType', 'Min': str(tMin), 'Max': str(tMax)})

SPECIAL_OPERATORS = {
    'abs'        : [{'type': NUMERICAL,  'direction': 'in'}],
    'ceil'       : [{'type': REAL,       'direction': 'in'}],
    'cos'        : [{'type': REAL,       'direction': 'in'}],
    'fix'        : [{'type': NUMERICAL,  'direction': 'in'}],
    'float'      : [{'type': NUMERICAL,  'direction': 'in'}],
    'floor'      : [{'type': REAL,       'direction': 'in'}],
    'length'     : [{'type': LIST,       'direction': 'in'}],
    'num'        : [{'type': ENUMERATED, 'direction': 'in'}],
    'power'      : [
                    {'type': NUMERICAL,  'direction': 'in'},
                    {'type': NUMERICAL,  'direction': 'in'}
                   ],
    'present'    : [{'type': CHOICE,     'direction': 'in'}],
    'exist'      : [{'type': ANY_TYPE,   'direction': 'in'}],
    'reset_timer': [{'type': TIMER,      'direction': 'in'}],
    'round'      : [{'type': REAL,       'direction': 'in'}],
    'set_timer'  : [
                    {'type': UNSIGNED,   'direction': 'in'},
                    {'type': TIMER,      'direction': 'in'}
                   ],
    'sin'        : [{'type': REAL,       'direction': 'in'}],
    'sqrt'       : [{'type': REAL,       'direction': 'in'}],
    'trunc'      : [{'type': REAL,       'direction': 'in'}],
    'write'      : [{'type': ANY_TYPE,   'direction': 'in'}],
    'writeln'    : [{'type': ANY_TYPE,   'direction': 'in'}],
    'to_selector': [  #  to convert an enum to a choice discriminant
                    {'type': ENUMERATED, 'direction': 'in'},
                    {'type': ANY_TYPE,   'direction': 'in'}
                   ],
    'to_enum'    : [  #  to convert a choice discriminant to an enum
                    {'type': ENUMERATED, 'direction': 'in'},
                    {'type': ANY_TYPE,   'direction': 'in'}
                   ],
    'val'    : [  #  to convert a number to an enumerated type value
                    {'type': UNSIGNED,   'direction': 'in'},  # eg. 1
                    {'type': ANY_TYPE,   'direction': 'in'}   # eg. MyChoice
                   ],
    'choice_to_int' : [  #  to return the value of a numerical choice item
                    {'type': CHOICE,     'direction': 'in'},  # choice variable
                    {'type': NUMERICAL,  'direction': 'in'}   # default value
                   ],
    'shift_left' : [ # logical shift -> return an unsigned
                    {'type': UNSIGNED,   'direction': 'in'},
                    {'type': UNSIGNED,   'direction': 'in'}
                   ],
    'shift_right' : [ # logical shift -> return an unsigned
                     {'type': UNSIGNED,   'direction': 'in'},
                     {'type': UNSIGNED,   'direction': 'in'}
                    ],
    'observer_status' :  # observer-only procedure returning the kind of state
                   [],
    'chr'        :       # return an octet (element of octet string)
                 [{'type': UINT8,  'direction': 'in'}],
}

# Container to keep a list of types mapped from ANTLR Tokens
# (Used with singledispatch/visitor pattern)
ANTLR_TOKEN_TYPES = {a: type(a, (antlr3.tree.CommonTree,), {})
                    for a, b in lexer.__dict__.items() if type(b) == int}


# Shortcut to create a new referenced ASN.1 type
new_ref_type = lambda refname: \
        type(str(refname), (object,),
                {'kind': 'ReferenceType',
                 'ReferencedTypeName': refname.replace('_', '-')})

# Shortcut to return a type name (Reference name or basic type)
def type_name(t):
    if t:
        return t.kind if t.kind != 'ReferenceType' else t.ReferencedTypeName
    else:
        return "UNDEFINED TYPE"

# return the line number of this python module, useful for debugging
lineno = lambda : currentframe().f_back.f_lineno

# user may create SDL (non-asn1) types with the newtype keyword
# they are stored in a dedicated dictionary with the same structure
# as the ASN1SCC generated python AST
USER_DEFINED_TYPES = dict()
CHOICE_SELECTORS = dict()


def types():
    ''' Return all ASN.1 and user defined types '''
    ret = getattr(DV, 'types', {}).copy()
    ret.update(USER_DEFINED_TYPES)
    return ret


def set_global_DV(asn1_filenames):
    # type: (List[str]) -> None
    ''' Call ASN.1 parser and set the global dataview AST entry (DV) '''
    global DV
    global USER_DEFINED_TYPES
    if '--toC' in sys.argv:
        rename_policy = ASN1.SystematicRenameAllEnumerants
    else:
        rename_policy = ASN1.NoRename
    try:
        DV = parse_asn1(tuple(asn1_filenames),
                        ast_version=ASN1.UniqueEnumeratedNames,
                        rename_policy=rename_policy,
                        flags=[ASN1.AstOnly],
                        pretty_print=True)
        # Create new types corresponding to CHOICE determinants as enum
        choice_selectors = create_choice_determinant_types (DV)
        #  Add to user defined types, so that they will be generated
        #  as explicit ASN.1 types
        CHOICE_SELECTORS.update(choice_selectors)
        USER_DEFINED_TYPES=CHOICE_SELECTORS.copy()
        # Add placeholder for SDL constants
        DV.SDL_Constants = {}
    except (ImportError, NameError) as err:
        # Can happen if DataView.py is not there
        LOG.error('Error loading ASN.1 model')
        LOG.debug(str(err))
    except TypeError as err:
        LOG.debug(traceback.format_exc())
        raise TypeError('ASN.1 compiler failed - {}'.format(str(err)))


def substring_range(substring: ogAST.PrimSubstring) -> Tuple[str, str]:
    ''' Return the range of a substring '''
    left, right = substring.value[1]['substring']
    left_bty = find_basic_type(left.exprType)
    right_bty = find_basic_type(right.exprType)
    return left_bty.Min, right_bty.Max


def is_number(basic_ty) -> bool:
    ''' Return true if basic type is a raw number (i.e. not a variable) '''
    return basic_ty.__name__ in ('Universal_Integer', 'PrReal')


def is_integer(ty) -> bool:
    ''' Return true if a type is an Integer Type '''
    return find_basic_type(ty).kind in (
        'IntegerType',
        'Integer32Type',
        'IntegerU8Type'
    )


def is_real(ty) -> bool:
    ''' Return true if a type is a Real Type '''
    return find_basic_type(ty).kind == 'RealType'


def is_numeric(ty, pool=None) -> bool:
    ''' Return true if a type is a Numeric Type '''
    return find_basic_type(ty, pool).kind in (
        'IntegerType',
        'Integer32Type',
        'IntegerU8Type',
        'Numerical',
        'RealType'
    )


def is_boolean(ty) -> bool:
    ''' Return true if a type is a Boolean Type '''
    return find_basic_type(ty).kind == 'BooleanType'


def is_null(ty) -> bool:
    ''' Return true if a type is a NULL Type '''
    return find_basic_type(ty).kind == 'NullType'


def is_string(ty, pool=None) -> bool:
    ''' Return true if a type is a String Type '''
    return find_basic_type(ty, pool).kind in (
        'StandardStringType',
        'OctetStringType',
        'StringType',
        'IA5StringType'
    )


def is_sequenceof(ty, pool=None) -> bool:
    ''' Return true if a type is a SequenceOf Type '''
    return find_basic_type(ty, pool).kind == 'SequenceOfType'


def is_list(ty) -> bool:
    ''' Return true if a type is a List Type '''
    return is_string(ty) or is_sequenceof(ty) or ty == LIST


def is_enumerated(ty) -> bool:
    ''' Return true if a type is an Enumerated Type '''
    return find_basic_type(ty).kind == 'EnumeratedType' or ty == ENUMERATED


def is_sequence(ty) -> bool:
    ''' Return true if a type is a Sequence Type '''
    return find_basic_type(ty).kind == 'SequenceType'


def is_choice(ty) -> bool:
    ''' Return true if a type is a Choice Type '''
    return find_basic_type(ty).kind == 'ChoiceType' or ty == CHOICE


def is_timer(ty) -> bool:
    ''' Return true if a type is a Timer Type '''
    return find_basic_type(ty).kind == 'TimerType'


def sdl_to_asn1(sort: str):
    '''
        Convert case insensitive type reference to the actual type as found
        in the ASN.1 datamodel
    '''
    for asn1_type in types().keys():
        if sort.replace('_', '-').lower() == asn1_type.lower():
            break
    else:
        raise TypeError('Type {} not found in ASN.1 model'.format(sort))
    return new_ref_type(asn1_type)


def node_filename(node):
    ''' Return the filename associated to the stream of this node '''
    parent = node
    while parent:
        try:
            return parent.getToken().getInputStream().fileName
        except AttributeError:
            parent = parent.getParent()
    return None


def token_stream(node):
    '''
        Return the token stream associated to a tree node
        It is set at the root of the tree by the parser
    '''
    parent = node
    while parent:
        try:
            return parent.token_stream
        except AttributeError:
            parent = parent.getParent()


def signals_in_system(ast):
    ''' Recursively find signal definitions in a nested SDL model '''
    all_signals = []
    for block in ast.blocks:
        all_signals.extend(signals_in_system(block))
    all_signals.extend(ast.signals)
    return all_signals


def find_process_declaration(ast, process_name):
    ''' Recursively search for a process declaration in a nested SDL model '''
    for block in ast.blocks:
        result = find_process_declaration(block, process_name)
        if result:
            return result
    try:
        for process in ast.processes:
            if process.processName.lower() == process_name.lower():
                return process
            elif process.instance_of_name.lower() == process_name.lower():
                return process
    except AttributeError:
        return None
    return None


def valid_output(scope):
    '''
        Yields the output, procedures, and operators names,
        that is all the elements that can be valid in an OUTPUT symbol
        (does not mean it IS valid - caller still has to check it)
    '''
    for out_sig in scope.output_signals:
        yield out_sig['name']
    for proc in scope.procedures:
        yield proc.inputString
    for special_op in SPECIAL_OPERATORS:
        yield special_op


def get_interfaces(ast, process_name):
    '''
        Search for the list of input and output signals (async PI/RI)
        and procedures (sync RI) of a process in a given top-level AST
        process_name can be the name of a process type, in which case the
        interfaces can only be found by looking at an instance of the type
        that is actually connected in the system
    '''
    all_signals, async_signals, errors = [], [], set()
    system = ast

    # Move up to the system level, in case process is nested in a block
    # and not defined at root level as it is the case when it is referenced
    while hasattr(system, 'parent'):
        system = system.parent

    # If we are at AST level, check in all systems, otherwise in current one
    iterator = ast.systems if hasattr(ast, 'systems') else (system,)

    for system in iterator:
        all_signals.extend(signals_in_system(system))
        process_ref = find_process_declaration(system, process_name)
        # Update process name with the name of the instance if we are parsing
        # a process type.
        if process_ref:
            process_name = process_ref.processName
            # Go to the block where the process is defined
            process_parent = process_ref.parent
            break
    else:
        if isinstance(ast, ogAST.Block):
            process_parent = ast
        else:
            raise TypeError('Process ' + process_name +
                        ' is defined but not declared in a system')
    # Find in and out signals names using the signalroutes
    undeclared_signals = []
    for each in process_parent.signalroutes:
        for route in each['routes']:
            if route['source'] == process_name:
                direction = 'out'
            elif route['dest'] == process_name:
                direction = 'in'
            else:
                continue
            for sig_id in route['signals']:
                # Copy the signal to the result dict
                try:
                    found, = [dict(sig) for sig in all_signals
                              if sig['name'].lower() == sig_id.lower()]
                    found['direction'] = direction
                    async_signals.append(found)
                except ValueError:
                    undeclared_signals.append(sig_id)
                except (KeyError, AttributeError) as err:
                    # Exceptions raised if a signal is not defined, i.e. there
                    # if an empty signal entry in the list. This can happen
                    # if the name of the signal is a reserved keyword, such as
                    # "stop", "reset"...
                    errors.add('Check the names of your signals against'
                               ' reserved keywords')
    if undeclared_signals:
        errors.add('Missing declaration for signal(s) {}'
                   .format(', '.join(undeclared_signals)))
    return async_signals, system.procedures, errors


def get_input_string(root):
    ''' Return the input string of a tree node '''
    try:
       res = token_stream(root).toString(root.getTokenStartIndex(),
                root.getTokenStopIndex())
       return res
    except AttributeError as err:
        # in case there is no token_strem(root)
        return ""


def error(root, msg: str) -> str:
    ''' Return an error message '''
    return '{} - "{}"'.format(msg, get_input_string(root))


def warning(root, msg: str) -> str:
    ''' Return a warning message '''
    return '{} - "{}"'.format(msg, get_input_string(root))


def check_syntax(node: antlr3.tree.CommonTree,
                 recursive:bool = False,
                 filename:str = "",
                 input_string:str = "") -> None:
    ''' Check if the ANTLR node is valid, otherwise raise an exception,
    meaning there is a syntax error, and report the string that could not be
    parsed '''
    def check(root: antlr3.tree.CommonTree,
              parent: antlr3.tree.CommonTree,
              rec: bool) -> None:
        if rec:
            for child in root.getChildren():
                check(child, parent, rec)
        if isinstance(root, antlr3.tree.CommonErrorNode):  #  in tree.py
            exc = root.trappedException    # in exceptions.py
            token = exc.token
            token_str = token.text
            line = token.line
            pos = token.charPositionInLine + 1
            if filename:
                text = open(filename, 'r').readlines()
            else:
                text = input_string.split('\n')
            if isinstance(exc, antlr3.exceptions.MismatchedTokenException):
                err_msg = f'{" "*(pos-1)}^__ Expected ' \
                          f'"{lexer.tokenNamesMap[exc.expecting]}", ' \
                          f'got "{token_str}"'
            else:
                err_msg = f'{" "*(pos-1)}^__ Unexpected "{token_str}"'
            if len(text) >= line:
                syntax_error = f'{text[line-1]}\n{err_msg}'
            else:
                LOG.error("Unrecoverable Error with text input")
                syntax_error = f'{err_msg} (line {line} offset {pos}) {len(text)} {text} {str(exc)}'
            se_exc          = SyntaxError(syntax_error)
            se_exc.filename = filename
            se_exc.lineno   = line
            se_exc.offset   = pos
            se_exc.text     = syntax_error
            raise se_exc
            #raise SyntaxError(syntax_error)
    check(node, parent=node, rec=recursive)


def tmp() -> int:
    ''' Return a temporary variable name '''
    global TMPVAR
    varname = TMPVAR
    TMPVAR += 1
    return varname


def get_state_list(process_root):
    ''' Return the list of states of a process '''
    # 1) get all STATE statements
    states = (child for child in process_root.getChildren()
            if child.type == lexer.STATE)
    # 2) keep only the ones containing a STATELIST token (i.e. no ASTERISK)
    relevant = (child for state in states for child in state.getChildren()
            if child.type == lexer.STATELIST)
    # 3) extract the state list from each of them
    state_list = [s.text.lower() for r in relevant for s in r.getChildren()]
    # state_list.append('START')
    # 4) create a set to remove duplicates
    return set(state_list)


def find_basic_type(a_type, pool=None):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type or UNKNOWN_TYPE
    pool = pool or types()
    while basic_type.kind == 'ReferenceType':
        Min = getattr(basic_type, "Min", None)
        Max = getattr(basic_type, "Max", None)

        # Find type with proper case in the data view
        for typename in pool.keys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = pool[typename].type
                if Min is not None and Max is not None \
                        and (is_numeric(basic_type, pool)
                                or is_string(basic_type, pool)
                                or is_sequenceof(basic_type, pool)):
                    # Subtypes may have defined subranges
                    new_type = type('Subtype',  basic_type.__bases__,
                            dict (basic_type.__dict__))
                    new_type.Min = Min
                    new_type.Max = Max
                    basic_type = new_type
                break
        else:
            raise TypeError('Type "' + type_name(basic_type) +
                            '" was not found in Dataview')
    return basic_type

def find_type_name(a_type, pool=None) -> str:
    ''' A Type may be an alias of another type, if it has a ReferencedTypeName
    and the same constraints as the referenced type. This function finds the
    name of the original type definition '''
    if a_type.kind != 'ReferenceType':
        raise TypeError('Not a referenced type')
    pool = pool or types()
    refname = a_type.ReferencedTypeName
    Min = getattr(a_type, "Min", None)
    Max = getattr(a_type, "Max", None)
    for typename in pool.keys():
        # Find the referenced type in the dataview
        if refname.lower() == typename.lower():
            parent = pool[typename].type
            parent_Min = getattr(parent, "Min", None)
            parent_Max = getattr(parent, "Max", None)
            if((Min != None and parent_Min != Min)
                    or (Max != None and parent_Max != Max)
                    or parent.kind != 'ReferenceType'):
                # Parent has different constraints or is a basic type
                return refname
            else:
                return find_type_name(parent)

def signature(name, context):
    ''' Return the signature of a procedure/output/operator '''
    name = name.lower()
    if name in SPECIAL_OPERATORS:
        return SPECIAL_OPERATORS[name]

    for out_sig in context.output_signals:
        if out_sig['name'].lower() == name:
            signature = []
            if out_sig.get('type'):
                # output signals: one single parameter
                signature.append({
                    'type': out_sig.get('type'),
                    'name': out_sig.get('param_name') or '',
                    'direction': 'in',
                })
            return signature

    for inner_proc in context.procedures:
        proc_name = inner_proc.inputString
        if proc_name.lower() == name:
            return inner_proc.fpar

    raise AttributeError('Operator/output/procedure not found: ' + name)


def check_call(name, params, context):
    ''' Check the parameter types of a procedure/output/operator call,
        returning the type of its result (value-returning functions only,
        i.e not signal sending
        Returns tuple: (expression type, warnings)
        '''
    warnings = []

    # Special case for write/writeln functions
    if name.lower() in ('write', 'writeln'):
        def check_one_param(p, name):
            p_ty = p.exprType
            if is_numeric(p_ty) or is_boolean(p_ty) or is_string(p_ty) or \
                    is_enumerated(p_ty):
                return (UNKNOWN_TYPE, warnings)
            raise TypeError('Type {} not supported in call to {}'.
                format(type_name(p.exprType), name))
        for p in params:
            if not isinstance(p, ogAST.PrimConditional):
                check_one_param(p, name)
            else:
                for each in (p.value['then'], p.value['else']):
                    check_one_param(each, name)
                # check that both "then" and "else" are of a similar type
                # (string, int, or enumerated), this is necessary for the
                # backends
                if (is_numeric(p.value['then'].exprType) ==
                   is_numeric(p.value['else'].exprType) == True) or \
                   (is_boolean(p.value['then'].exprType) ==
                   is_boolean(p.value['else'].exprType) == True) or \
                   (is_string(p.value['then'].exprType) ==
                   is_string(p.value['else'].exprType) == True) or \
                   (is_enumerated(p.value['then'].exprType) ==
                   is_enumerated(p.value['else'].exprType) == True):
                      p.exprType = p.value['then'].exprType
                else:
                    raise TypeError('{}: both options must have the same type.'
                                    .format(name))
        return (UNKNOWN_TYPE, warnings)

    # Special case for "exist" function
    elif name == 'exist':
        # "exist" shall return true if an optional SEQUENCE field is present
        # We have to check that the parameter is actually an optional field
        # So we check first that there is only one param
        # then that this is a PrimSelector (at least "a.b")
        # Then we analyse from the variable to the last field if that is
        # actually an optional field, using the ASN.1 data model
        if len(params) != 1:
            raise TypeError('"exist" operator takes only one parameter')
        param, = params
        if not isinstance(param, ogAST.PrimSelector):
            raise TypeError('"exist" operator only works on optional fields')
        left = param.value[0] # Can be a variable or another PrimSelector
        field_list = [param.value[1]] # string of the field name
        while isinstance(left, ogAST.PrimSelector):
            field_list.append(left.value[1])
            left = left.value[0]
        sort = find_basic_type(left.exprType)  # must have Children
        if sort.kind == 'UnknownType':
            raise TypeError('Variable not found in call to "exist" operator')
        # At this point we know that the expression is correct, so we will
        # not miss any child in the dataview. We can follow the children
        # in the ASN.1 model until we reach the last one, which shall be
        # optional
        while field_list:
            child_name = field_list.pop().replace('_', '-').lower()
            for child in sort.Children.keys():
                if child.lower() == child_name:
                    break
            optional = sort.Children[child].Optional
            sort = sort.Children[child].type
            if sort.kind == 'ReferenceType':
                sort = find_basic_type (sort)
        # At this point we should have found the last type
        if optional != "True":
            raise TypeError('Field is not optional in call to "exist"')
        return (type('Exist', (object,), {
            'kind': 'BooleanType'
        }), warnings)
    elif name == 'val':
        # val converts a positive number to a enumeration literal
        # the first parameter is the number and the second is the type name
        # of the enumeration. It is equivalent in Ada to EnumType'Val(number)
        if len(params) != 2:
            raise TypeError(name + " takes 2 parameters: number, type")
        variable, target_type = params
        variable_sort = find_basic_type(variable.exprType)
        if variable_sort.kind != 'IntegerType':
            raise TypeError(name + ': First parameter is not an number')
        sort_name = target_type.value[0]  #  raw string of the type to cast
        for sort in types().keys():
            if sort.lower().replace('-', '_') == \
                    sort_name.lower().replace('-', '_'):
                break
        else:
            raise TypeError(name + ': type ' + sort_name + 'not found')
        # we could check if the range of the number is compatible with the
        # number of values...
        return_type = types()[sort].type
        return (return_type, warnings)

    elif name in ('to_selector', 'to_enum'):
        if len(params) != 2:
            raise TypeError(name + " takes 2 parameters: variable, type")
        variable, target_type = params
        variable_sort = find_basic_type(variable.exprType)
        if variable_sort.kind == 'UnknownType':
            raise TypeError(name + ': variable not found (parameter 1)')
        if variable_sort.kind != 'EnumeratedType':
            raise TypeError(name + ': First parameter is not an enumerated')
        sort_name = target_type.value[0]  #  raw string of the type to cast
        for sort in types().keys():
            if sort.lower().replace('-', '_') == \
                    sort_name.lower().replace('-', '_'):
                break
        else:
            raise TypeError(name + ': type ' + sort_name + 'not found')
        # check that the list of enumerants are identical. unfortunately we
        # cannot check the ordering, as it is an unordered dict
        if name == 'to_selector':
            # if the sort is a subtype, it may not have a -selection suffix
            # and an exception may be raised. FIXME : check "present" operator
            # as the issue is already fixed there
            return_type = types()[sort.title() + '-selection'].type
        else:
            return_type = types()[sort].type
        if return_type.kind != 'EnumeratedType':
            raise TypeError(name + ': Second parameter is incorrect')
        return_type_keys = return_type.EnumValues.keys()
        variable_sort_keys = variable_sort.EnumValues.keys()
        if return_type_keys != variable_sort_keys:
            raise TypeError(name + ': Enumerated type are not equivalent')
        return (return_type, warnings)
    elif name == 'observer_status':
        if len(params) != 0:
            raise TypeError(f'{name} does not take any parameter')
        if 'Observer-State-Kind' not in types().keys():
            raise TypeError(f'{name} can only be used in observers')
        return (types()['Observer-State-Kind'].type, warnings)

    # (1) Find the signature of the function
    # signature will hold the list of parameters for the function
    sign = signature(name, context)

    # (2) Check that the number of given parameters matches the signature
    if len(sign) != len(params):
        raise TypeError('Expected {} arguments in call to {} ({} received)'.
            format(len(sign), name, len(params)))

    # (3) Check each individual parameter type
    for idx, param in enumerate(params):
        expr               = ogAST.ExprAssign()
        expr.left          = ogAST.PrimVariable(debugLine=lineno())
        expr.left.exprType = sign[idx]['type']
        expr.right         = param

        try:
            basic_left  = find_basic_type(expr.left.exprType)
            basic_right = find_basic_type(expr.right.exprType)
            try:
                param_warnings = fix_expression_types(expr, context)
                w = Assign_Check_Range (expr)
                if w is not None:
                    warnings.append(w)
                for warn in param_warnings:
                    warnings.append(f'Parameter {idx+1} of call to "{name}": {warn}')
            except AttributeError:
                # If the parameter has no proper type we may have an exception
                raise TypeError ("Could not parse this expression")
            except Warning as warn:
                warnings.append(f'Parameter {idx+1} of call to "{name}": {warn}')
            params[idx] = expr.right
        except TypeError as err:
            expected = type_name(sign[idx]['type'])
            received = type_name(expr.right.exprType)
            raise TypeError(f'In call to {name}: Type of parameter {idx+1} is incorrect'
                            f' ({received}) - {str(err)}')
#       if warnings:
#           expected = type_name(sign[idx]['type'])
#           received = type_name(expr.right.exprType)
#           raise Warning('Expected type {} in call to {} ({} received)'.
#               format(expected, name, received))

        if sign[idx].get('direction') != 'in' \
                and not isinstance(expr.right, (ogAST.PrimVariable,
                                                ogAST.PrimIndex,
                                                ogAST.PrimSelector)):
            # out parameters base must be a variable
            raise TypeError('Parameter "{}" does not qualify as an OUT parameter'
                .format(expr.right.inputString))

    # (4) Compute the type of the result
    param_btys = [find_basic_type(p.exprType) for p in params]
    if name == 'abs':
        # The implementation of abs in *all* programming languages returns
        # a type that is the same as the type of the parameter. The returned
        # value is *not* unsigned. abs(integer'Min) returns a NEGATIVE number
        # this is an issue in an assign statement, if the recipient is
        # unsigned .. A cast is necessary if the parameter of abs is negative
        Min = float(param_btys[0].Min)
        Max = float(param_btys[0].Max)
        if params[0].exprType.kind != 'ReferenceType' and Min == Max:
            # if param is a raw number, return a positive range
            # otherwise return the same type as the variable
            return (type('Universal_Integer', (param_btys[0],), {
               'Min': str(max(Min, 0)),
               'Max': str(max(Max, 0))
           }), warnings)
        else:
            return (type('Abs', (param_btys[0],), {}), warnings)

    elif name == 'ceil':
        return (type('Ceil', (REAL,), {
            'Min': str(math.ceil(float(param_btys[0].Min))),
            'Max': str(math.ceil(float(param_btys[0].Max)))
        }), warnings)

    elif name == 'cos':
        return (type('Cos', (REAL,), {
            'Min': str(-1.0),
            'Max': str(1.0)
        }), warnings)

    elif name == 'fix':
        return (type('Fix', (INTEGER,), {
            'Min': param_btys[0].Min,
            'Max': param_btys[0].Max
        }), warnings)

    elif name == 'chr':
        # First check that parameter is in range [0..255]
        # The parameter may be an octet string literal. In that case we
        # have to check the actual number rather than the Min/Max attribute.
        param = params[0]
        if isinstance(param, ogAST.PrimOctetStringLiteral):
            Min = Max = param.numeric_value
        else:
            Min, Max = float(param_btys[0].Min), float(param_btys[0].Max)
        if Min < 0 or Min > 255 or Max < 0 or Max > 255:
            raise TypeError('Parameter is not within range [0 .. 255]')
        return (UINT8, warnings)

    elif name == 'float':
        return (type('Float', (REAL,), {
            'Min': param_btys[0].Min,
            'Max': param_btys[0].Max
        }), warnings)

    elif name == 'floor':
        return (type('Floor', (REAL,), {
            'Min': str(math.floor(float(param_btys[0].Min))),
            'Max': str(math.floor(float(param_btys[0].Max)))
        }), warnings)

    elif name == 'length':
        return (type('Length', (INT32,), {
            'Min': param_btys[0].Min,
            'Max': param_btys[0].Max
        }), warnings)

    elif name == 'num':
        enum_values = [int(each.IntValue)
                       for each in param_btys[0].EnumValues.values()]
        return (type('Num', (INTEGER,), {
            'Min': str(min(enum_values)),
            'Max': str(max(enum_values))
        }), warnings)

    elif name == 'power':
        return (type('Power', (param_btys[0],), {
            'Min': str(pow(float(param_btys[0].Min),
                           float(param_btys[1].Min))),
            'Max': str(pow(float(param_btys[0].Max),
                           float(param_btys[1].Max)))
        }), warnings)

    elif name == 'present':
        p, = params
        # When we get there, the parameter has been checked already and we
        # know it is a CHOICE type.
        # However it may be a subtype, and in the AST the choices are defined
        # in the supertype, so we must find it and add the -selection suffix
        # This suffix is added by the Asn1scc module.
        sort = p.exprType
        sort_name = type_name (sort)
        try:
            while sort.kind == "ReferenceType":
                sort_name = sort.ReferencedTypeName
                sort = types()[sort.ReferencedTypeName].type
        except AttributeError:
            # Native choice types don't have the kind field here
            pass
        return (types()[sort_name.title() + "-selection"].type, warnings)

    # choice_to_int: returns an integer corresponding to either the currently
    # selected choice value (e.g. foo in CHOICE { foo INTEGER (..), ... } when
    # foo is the current choice). or a default, user-defined value if the
    # current choice is not numerical. The first parameter is an instance of
    # a CHOICE type, and the second parameter is the default value.
    elif name == 'choice_to_int':
        p1, _ = params
        #sort = type_name (p1.exprType)
        return (type('choice_to_int', (INTEGER,), {}), warnings)

    elif name in ('shift_right', 'shift_left'):
        p1, _ = params
        return (type('shift', (p1.exprType,), {}), warnings)

    elif name == 'round':
        return (type('Round', (REAL,), {
            'Min': str(round(float(param_btys[0].Min))),
            'Max': str(round(float(param_btys[0].Max)))
        }), warnings)

    elif name == 'sin':
        return (type('Sin', (REAL,), {
            'Min': str(-1.0),
            'Max': str(1.0)
        }), warnings)

    elif name == 'sqrt':
        return (type('Sqrt', (REAL,), {
            'Min': str(0.0),
            'Max': str(math.sqrt(float(param_btys[0].Max)))
        }), warnings)

    elif name == 'trunc':
        return (type('Trunc', (REAL,), {
            'Min': str(math.trunc(float(param_btys[0].Min))),
            'Max': str(math.trunc(float(param_btys[0].Max)))
        }), warnings)

    else:
        # check if procedure is declared to return a type
        for inner_proc in context.procedures:
            proc_name = inner_proc.inputString
            if proc_name.lower() == name.lower() and inner_proc.return_type:
                return (inner_proc.return_type, warnings)

    return (UNKNOWN_TYPE, warnings)


def check_range(typeref, type_to_check):
    ''' Verify the that the Min/Max bounds of two types are compatible
        Called to test that assignments are withing allowed range
        both types assumed to be basic types
    '''
    try:
        if type_to_check.kind == "StringType" and type_to_check.NumericValue != -1:
            # OctetStringLiteral, BitStringLiteral assigned to integer
            min1 = max1 = type_to_check.NumericValue
        else:
            min1, max1 = float(type_to_check.Min), float(type_to_check.Max)
        min2, max2 = float(typeref.Min), float(typeref.Max)
        error   = min1 > max2 or max1 < min2
        warning = min1 < min2 or max1 > max2
        if min1 == max1:
            first_part = f'Expression value {min1}'
        else:
            first_part = f'Expression in range ({min1}..{max1})'
        if error:
            raise TypeError(f'{first_part} is outside range ({min2}..{max2})')
        # Warning is the case of a variable that is incremented. The resulting
        # range may be outside the ranger of the recipient, but it is not
        # always an error (if the user code contains a check)
        if warning:
            return f'{first_part} could be outside range ({min2}..{max2})'
        else:
            return None
        #elif warning:
        # Disabled because raising an exception for a warning is wrong, it
        # can prevent code to execute if not caught at the right place
        #    raise Warning(f'{first_part} could be outside range ({min2}..{max2})')
    except (AttributeError, ValueError):
        raise TypeError('Missing range')


def Assign_Check_Range(expr : ogAST.ExprAssign):
    ''' If the assignment is numerical, check the range. '''
    basic = find_basic_type (expr.left.exprType)
    if basic.kind.startswith(('Integer', 'Real')):
        if isinstance(expr.right, ogAST.PrimOctetStringLiteral):
            rType = NewInteger(expr.right.numeric_value,
                               expr.right.numeric_value)
            return check_range(basic, rType)
        else:
            return check_range(basic, find_basic_type(expr.right.exprType))


def fix_append_expression_type(expr, expected_type):
    ''' In an Append expression, all components must be of the same type,
        which is the type expected by the user of the append, for example
        the left part of an assign expression.
        We must recursively fix the Append type, in case we have a//b//c
        that is handled as (a//b)//c
        Inputs:
           expr: the append expression (possibly recursive)
           expected_type : the type to assign to the expression
    '''
    LOG.debug(f"fix_append_expression: {expr.inputString}, {str(expected_type)}")
    basic = find_basic_type(expected_type)
    def rec_append(inner_expr):
        elements = []
        for each in (inner_expr.left, inner_expr.right):

            # One side of the expression is a ternary: we must check both the
            # "then" and the "else" expressions against the expected type.
            if isinstance(each, ogAST.PrimConditional):
                # We must check both 'then' and 'else' branches
                elements.append(each.value['then'])
                elements.append(each.value['else'])
                # Set the type of the ternary to the expected type
                # Individual elements will be checked below
                each.exprType = expected_type
            else:
                elements.append(each)

            # now we have a list of individual elements for one side of the //
            for elem in elements:
                if isinstance(elem, ogAST.ExprAppend):
                    # Go recursive if this is an inner append expression
                    rec_append(elem)
                elem.expected_type = expected_type
                # Find the basic type of the element for compatibility check
                # The various cases are:
                # string = string // string
                # seqOf = seqOf // seqOf
                # string = string // mkstring(chr(...))
                # the last case requires a special treatment because mkstring
                # returns a PrimSequenceOf and not a string. so this makes the
                # expression appear inconsistent. it is checked and fixed here
                elem_bty = find_basic_type(elem.exprType)
                if basic.kind == 'OctetStringType' and elem_bty.kind == 'SequenceOfType':
                    # Check if the element is a single chr() or octet string instance
                    soElemType = find_basic_type(elem.exprType.type)
                    if soElemType.kind in ('IntegerU8Type', 'OctetStringType') \
                            and elem.exprType.Max =='1':
                       pass
                    else:
                        raise TypeError ("Element of the array is incompatible with the expected type")
                elif basic.kind == 'SequenceOfType' and elem_bty.kind != basic.kind:
                    # Expecting a sequence of but got an octet string
                    raise TypeError ("Use the mkstring operator to append to an array")
                if isinstance(elem, ogAST.PrimSequenceOf):
                    # If a part of the APPEND is a raw sequence of ( { 1, 3 } )
                    # then a range check of the individual elements has to be done
                    # against expected type
                    check_expr = ogAST.ExprAssign()
                    check_expr.left = ogAST.PrimVariable(debugLine=lineno())
                    # At least one element must be appended and at most the
                    # max size of the recipient minus its min size
                    # (this limits the risks of overflows)
                    newMax = int(basic.Max) - int(basic.Min)
                    check_expr.left.exprType = type("JustChecking",
                            (basic,), {"Min":"1", "Max":str(newMax)})
                    check_expr.right = elem
                    fix_expression_types(check_expr, context=None)
    rec_append(expr)
    expr.exprType      = expected_type
    expr.expected_type = expected_type


def check_type_compatibility(primary, type_ref, context):
    '''
        Check if an ogAST.Primary (raw value, enumerated, ASN.1 Value...)
        is compatible with a given type (type_ref is an ASN1Scc type)
        Possibly returns a list of warnings; can raise TypeError
    '''
    warnings = []    # function returns a list of warnings
    # assert type_ref is not None
    if type_ref is UNKNOWN_TYPE or type_ref is None:
        #print(traceback.print_stack())
        raise TypeError('Type reference is unknown')

    basic_type = find_basic_type(type_ref)
    # watch out: type_ref may be a subtype of basic_type with different
    # min/max constraint, in particular in case of substrings
    if type_ref.__name__ == 'SubStr':
        minR, maxR = type_ref.Min, type_ref.Max
    else:
        try:
            minR, maxR = basic_type.Min, basic_type.Max
        except AttributeError:
            # some types do not have Min/Max ranges
            pass

    if (isinstance(primary, ogAST.PrimEnumeratedValue)
            and basic_type.kind.endswith('EnumeratedType')):
        # If type ref is an enumeration, check that the value is valid
        # Note, when using the "present" operator of a CHOICE type, the
        # resulting value is actually an EnumeratedType
        enumerant = primary.inputString.replace('_', '-').lower()
        for each in basic_type.EnumValues.keys():
            if each.lower() == enumerant:
                # Found -> all OK
                return warnings
        else:
            err = ('Value "' + primary.inputString +
                   '" not in this enumeration: ' +
                   str(basic_type.EnumValues.keys()))
            raise TypeError(err)
    elif isinstance(primary, ogAST.PrimConditional):
        then_expr = primary.value['then']
        else_expr = primary.value['else']

        for expr in (then_expr, else_expr):
            if expr.is_raw:
                warnings.extend(check_type_compatibility(expr,
                                                         type_ref,
                                                         context))
        return warnings

    elif isinstance(primary, (ogAST.PrimVariable, ogAST.PrimSelector)):
        try:
            warnings.extend(compare_types(primary.exprType, type_ref))
        except TypeError as err:
            raise TypeError('{expr} should be of type {ty} - {err}'
                            .format(expr=primary.inputString,
                                    ty=type_name(type_ref),
                                    err=str(err)))
        return warnings

    elif isinstance(primary, (ogAST.PrimInteger, ogAST.ExprMod)) \
            and (is_integer(type_ref) or type_ref == NUMERICAL):
        # We do not check range here because we do not know if it
        # is relevant - range should be checked when value is assigned
        return warnings

    elif isinstance(primary, ogAST.PrimReal) \
            and (is_real(type_ref) or type_ref == NUMERICAL):
        return warnings

    elif isinstance(primary, ogAST.ExprNeg):
        warnings.extend(check_type_compatibility(primary.expr,
                                                 type_ref,
                                                 context))

    elif isinstance(primary, ogAST.PrimBoolean) and is_boolean(type_ref):
        return warnings

    elif isinstance(primary, ogAST.PrimNull) and is_null(type_ref):
        return warnings

    elif isinstance(primary, ogAST.PrimEmptyString):
        # Empty strings ("{ }") can be used for arrays and empty records
        if basic_type.kind == 'SequenceOfType':
            if int(minR) == 0:
                return warnings
            else:
                raise TypeError('SEQUENCE OF has a minimum size of '
                                + minR + ')')
        elif basic_type.kind == 'SequenceType':
            if len(basic_type.Children.keys()) > 0:
                raise TypeError('SEQUENCE is not empty, wrong "{}" syntax')
        else:
            raise TypeError('Not a type compatible with empty string syntax')
    elif isinstance(primary, ogAST.PrimSequenceOf) \
            and basic_type.kind == 'SequenceOfType':
        #  left is a sequenceof, but we check it is not an append
        if type_ref.__name__ not in ('Apnd') and \
                (len(primary.value) < int(minR) or
                len(primary.value) > int(maxR)):
            #print traceback.print_stack()
            raise TypeError(str(len(primary.value)) +
                      ' element(s) in SEQUENCE OF, while constraint is [' +
                      str(minR) + ' .. ' + str(maxR) + ']')
        for elem in primary.value:
            warnings.extend(check_type_compatibility(elem,
                                                     basic_type.type,
                                                     context))
        if not hasattr(primary, 'expected_type') \
               and type_ref.__name__ not in ('Apnd', 'SubStr'):
            primary.expected_type = type_ref
        return warnings
    elif isinstance(primary, ogAST.PrimSequenceOf) \
            and basic_type.kind == 'OctetStringType':
        # mkstring expressions are of of type SequenceOf, but they may be
        # assigned to an octet string in an append expression. We must check
        # the type of the element of the sequence of to make sure.
        for elem in primary.value:
            if elem.exprType != UINT8:
                raise TypeError("Use only integers in range 0..255 to assign octet strings")
        return warnings

    elif isinstance(primary, ogAST.PrimSequence) \
            and basic_type.kind == 'SequenceType':
        user_nb_elem = len(primary.value.keys())
        type_nb_elem = len(basic_type.Children.keys())
        optional_fields = [field.lower().replace('-', '_')
                           for field, val in basic_type.Children.items()
                           if val.Optional == 'True']
        user_fields = [field.lower() for field in primary.value.keys()]
        for field, fd_data in basic_type.Children.items():
            ufield = field.replace('-', '_')
            if ufield.lower() not in optional_fields \
                    and ufield.lower() not in user_fields:
                raise TypeError('Missing mandatory field {field} in SEQUENCE'
                                ' of type {t1} '
                                .format(field=ufield,
                                        t1=type_name(type_ref)))
            elif ufield.lower() not in user_fields:
                # Optional field not set - OK
                continue
            else:
                # If the user field is a raw value
                casefield = ufield
                for each in primary.value:
                    if each.lower() == ufield.lower():
                        casefield = each
                        break
                if primary.value[casefield].is_raw:
                    warnings.extend(check_type_compatibility
                                         (primary.value[casefield],
                                          fd_data.type,
                                          context))
                else:
                    # Compare the types for semantic equivalence
                    try:
                        warnings.extend(compare_types
                                       (primary.value[casefield].exprType,
                                        fd_data.type))
                    except TypeError as err:
                        raise TypeError('Field "' + ufield + '" not of type ' +
                                    type_name(fd_data.type) +
                                    ' - ' + str(err))
        return warnings
    elif isinstance(primary, ogAST.PrimChoiceItem) \
                              and basic_type.kind.startswith('Choice'):
        for choicekey, choice in basic_type.Children.items():
            if choicekey.lower().replace('-', '_') == \
                    primary.value['choice'].lower().replace('-', '_'):
                break
        else:
            raise TypeError('Non-existent choice "{choice}" in type {t1}'
                            .format(choice=primary.value['choice'],
                            t1=type_name(type_ref)))
        # compare primary.value['value']
        # with basic_type['Children'][primary.choiceItem['choice']]
        value = primary.value['value']
        choice_field_type = choice.type
        # if the user field is a raw value:
        if value.is_raw:
            warnings.extend(check_type_compatibility(value,
                                                     choice_field_type,
                                                     context))
        # Compare the types for semantic equivalence:
        else:
            try:
                warnings.extend(compare_types(value.exprType,
                                              choice_field_type))
            except TypeError as err:
                raise TypeError(
                            'Field {field} in CHOICE is not of type {t1} - {e}'
                            .format(field=primary.value['choice'],
                                    t1=type_name(choice_field_type),
                                    e=str(err)))
        value.exprType = choice_field_type         # XXX
        return warnings
    elif isinstance(primary, ogAST.PrimChoiceDeterminant) \
                and basic_type.kind.startswith('Choice'):
        for choicekey, choice in basic_type.EnumValues.items():
            if choicekey.replace('-', '_').lower() == \
                    primary.inputString.lower():
                break
        else:
            raise TypeError('Non-existent choice "{choice}" in type {t1}'
                            .format(choice=primary.inputString,
                            t1=type_name(type_ref)))

    elif isinstance(primary, (ogAST.PrimBitStringLiteral, ogAST.PrimOctetStringLiteral)) \
            and is_integer(type_ref) or type_ref == NUMERICAL:
        return warnings
    elif isinstance(primary, ogAST.PrimStringLiteral):
        # Octet strings
        basic_type = find_basic_type(type_ref)
        if basic_type.kind == 'StandardStringType':
            # raw string
            return warnings
        elif basic_type.kind.endswith('StringType'):
            # all strings including IA5String, BitString, OctetString
            try:
                ok = True
                # value is in hex form for both octet and bit string literals
                if basic_type.kind == 'OctetStringType':
                    # recipient is an OCTET STRING of some size [minR..maxR]
                    # The length check will depend  on the user string kind:
                    lenOfInput = len(primary.value[1:-1])

                    if primary.exprType.kind == 'OctetStringType':
                        # user entered an hex string ('ABC'H)
                        # => 2 input characters = 1 element of the string
                        ok = int(minR) * 2 <= lenOfInput <= int(maxR) * 2

                    elif primary.exprType.kind == 'BitStringType':
                        # user entered a bit string ('011'B)
                        # a padding has been added and it ws converted to hex
                        # (the primary.value is an hex string already)
                        # => length must be compatible with recipient length
                        ok = int(minR) * 2 <= lenOfInput <= int(maxR) * 2
                    else:
                        # user entered a text => each char is 1 octet
                        ok = int(minR) <= lenOfInput <= int(maxR)

                    if ok:
                        return warnings
                    else:
                        raise TypeError(f'Invalid string literal {primary.value}H:'
                                    ' Length check failed (Octet String) ')

                elif basic_type.kind == 'BitStringType':
                    # recipient is a BIT STRING of some size [minR..maxR]
                    # The length check will depend  on the user string kind:

                    if primary.exprType.kind == 'OctetStringType':
                        # user entered an hex string ('ABC'H)
                        # => each character is 4 bits
                        ok = int(minR) <= len(primary.value[1:-1]) * 4 <= int(maxR)

                    elif primary.exprType.kind == 'BitStringType':
                        # user entered a bit string ('011'B)
                        # a padding has been added and it ws converted to hex
                        # (the primary.value is an hex string already)
                        # but the original number of bits is known
                        ok = int(minR) <= primary.exprType.NumberOfBits <= int(maxR)
                    else:
                        # user entered a text => each character is 8 bits
                        ok = int(minR) <= len(primary.value[1:-1]) * 8 <= int(maxR)

                    if ok:
                        return warnings
                    else:
                        raise TypeError(f'Invalid string literal {primary.value}H:'
                                    ' Length check failed (Bit String) ')

                elif int(minR) <= len(primary.value[1:-1]) <= int(maxR):
                    return warnings
                else:
                    #print traceback.print_stack()
                    raise TypeError('Invalid string literal'
                                    ' - check that length is '
                                    'within the bound limits {Min}..{Max}'
                                    .format(Min=str(minR),
                                            Max=str(maxR)))
            except ValueError:
                # No size constraint (or MIN/MAX)
                LOG.debug('String literal size constraint discarded')
                return warnings
        else:
            raise TypeError(f'String literal not expected')
    elif (isinstance(primary, ogAST.PrimMantissaBaseExp) and
                                            basic_type.kind == 'RealType'):
        LOG.debug('PROBABLY (it is a float but I did not check'
                  'if values are compatible)')
        return warnings
    elif isinstance(primary, ogAST.PrimIndex):
        if primary.exprType != type_ref:
            raise TypeError(f'Type of array element {primary.inputString} '
                    f'does not match expected type "{type_name(type_ref)}"')
    elif isinstance(primary, ogAST.PrimSubstring):
        primSort = type_name(primary.exprType)
        refSort  = type_name(type_ref)
        if type_name(primary.exprType) != type_name(type_ref):
            raise TypeError(f'{prim} resolves to sort "{primSort}" while "{refSort} was expected')
    else:
        raise TypeError('{prim} does not match type {t1}'
                        .format(prim=primary.inputString,
                                t1=type_name(type_ref)))
    return warnings


def compare_types(type_a, type_b):   # type -> [warnings]
    '''
       Compare two types, return if they are semantically equivalent,
       otherwise raise TypeError
    '''
    warnings = []
    mismatch = ''
    if not type_a or not type_b:
        raise TypeError("Missing type definition")
    if type_a.kind == 'ReferenceType' and type_b.kind == 'ReferenceType':
        # The type names may be different but the types may still be
        # the same, eg : TypeB ::= TypeA
        # In that case TypeB is just an alias (renaming) of TypeA and it
        # is correct to assign value of one to the other
        # We must find the lowest common type name denominator before
        # concluding that there is a mismatch
        # The check must verify that the constraints are strictly the same, too
        ref_a = type_a.ReferencedTypeName
        ref_b = type_b.ReferencedTypeName
        lowest_a = find_type_name (type_a)
        lowest_b = find_type_name (type_b)
        if lowest_a != lowest_b:
            mismatch = '"{}" is not "{}"'.format(type_a.ReferencedTypeName,
                                                 type_b.ReferencedTypeName)
    type_a = find_basic_type(type_a)
    type_b = find_basic_type(type_b)

    if type_a == type_b:
        return warnings
    elif NUMERICAL in (type_a, type_b) and is_numeric(type_a) \
            and is_numeric(type_b):
        return warnings
    elif LIST in (type_a, type_b) and is_list(type_a) and is_list(type_b):
        return warnings
    elif ENUMERATED in (type_a, type_b) and is_enumerated(type_a) \
            and is_enumerated(type_b):
        return warnings
    elif CHOICE in (type_a, type_b) and is_choice(type_a) and is_choice(type_b):
        return warnings

    # Check if both types have basic compatibility
    if type_a.kind == type_b.kind:
        if type_a.kind == 'SequenceOfType':
            if mismatch:
                raise TypeError(mismatch)
            if type_a.Min == type_a.Max:
                if type_a.Min == type_b.Min == type_b.Max:
                    warnings.extend(compare_types(type_a.type, type_b.type))
                    return warnings
                else:
                    raise TypeError('Incompatible sizes - size of {} can vary'
                                    .format(type_name(type_b)))
            elif(float(type_b.Min) >= float(type_a.Min)
                 and float(type_b.Max) <= float(type_a.Max)):
                warnings.extend(compare_types(type_a.type, type_b.type))
                return warnings
            else:
                warnings.extend(compare_types(type_a.type, type_b.type))
                warnings.append('Size constraints mismatch - risk of overflow')
                return warnings
        # TODO: Check that OctetString types have compatible range
        elif type_a.kind == 'SequenceType' and mismatch:
            raise TypeError(mismatch)
        elif type_a.kind == 'IntegerType':
            # Detect Signed/Unsigned type mismatch
            try:
                min_a = float(type_a.Min)
            except ValueError:
                # "MIN" instead of a number
                # Since we only want to check sign compatibility, set -1
                min_a = -1
            try:
                min_b = float(type_b.Min)
            except ValueError:
                min_b = -1
            if (min_a >= 0) != (min_b >= 0) \
                    and not (is_number(type_a) or is_number(type_b)):
                raise TypeError("Signed vs Unsigned type mismatch " +
                        mismatch)
            elif mismatch:
                warnings.append(mismatch)
        elif mismatch:
            warnings.append(mismatch)
        #print traceback.print_stack()
        return warnings
    elif is_string(type_a) and is_string(type_b):
        return warnings
    elif is_integer(type_a) and is_integer(type_b):
        if mismatch:
            warnings.append(mismatch)
        return warnings
    elif is_real(type_a) and is_real(type_b):
        if mismatch:
            warnings.append(mismatch)
        return warnings
    elif is_integer(type_a) and type_b.kind == 'OctetStringType' \
            or is_integer(type_b) and type_a.kind == 'OctetStringType':
        if mismatch:
            warnings.append(mismatch)
        return warnings

    else:
        raise TypeError('Incompatible types {} and {}'.format(
            type_name(type_a),
            type_name(type_b)
        ))

def find_variable_type(var, context):
    ''' Look for a variable name in the context and return its type '''

    # all DCL-variables
    all_visible_variables = dict(context.global_variables)
    all_visible_variables.update(context.variables)
    all_visible_variables.update(context.monitors)
    all_visible_variables.update(context.global_monitors)

    # First check locally, i.e. in FPAR
    try:
        for variable in context.fpar:
            if variable['name'].lower() == var.lower():
                return variable['type']
    except AttributeError:
        # No FPAR section
        pass

    for varname, (vartype, _) in all_visible_variables.items():
        # Case insensitive comparison with variables
        if var.lower() == varname.lower():
            return vartype

    for timer in chain(context.timers, context.global_timers):
        if var.lower() == timer.lower():
            return TIMER

    # check if it is an ASN.1 constant
    for varname, vartype in chain(DV.variables.items(),
                                  DV.SDL_Constants.items()):
        if var.lower() == varname.lower().replace('-', '_'):
            return vartype.type

    raise AttributeError('Variable {var} not defined'.format(var=var))


def fix_enumerated_and_choice(expr_enum, context):
    ''' If left side of the expression is of Enumerated or Choice type,
        check if right side is a literal of that sort, and update type '''
    warnings = []
    kind = find_basic_type(expr_enum.left.exprType).kind
    if kind in ('EnumeratedType', 'StateEnumeratedType'):
        LOG.debug ("Fix raw enumerated type: " + expr_enum.right.inputString)
        prim = ogAST.PrimEnumeratedValue(primary=expr_enum.right,
                                         debugLine=lineno())
        try:
            warnings.extend(check_type_compatibility(prim,
                                                     expr_enum.left.exprType,
                                                     context))
            expr_enum.right = prim
            expr_enum.right.exprType = expr_enum.left.exprType
        except (UnboundLocalError, AttributeError, TypeError) as err:
            LOG.debug ("Failed: " + str(err))
            LOG.debug(traceback.format_exc())
            pass
    return warnings


def fix_expression_types(expr, context):
    ''' Check/ensure type consistency in binary expressions '''
    warnings = []
    for _ in range(2):
        # Check if a raw enumerated value is of a reference type
        warnings.extend(fix_enumerated_and_choice(expr, context))
        expr.right, expr.left = expr.left, expr.right

    for side in (expr.right, expr.left):
        if side.is_raw:
            raw_expr = side
        else:
            typed_expr = side
            ref_type = typed_expr.exprType

    if isinstance(expr, ogAST.ExprAppend):
        return warnings

    # If a side is a raw Sequence Of with unknown type, try to resolve it
    for side_a, side_b in permutations(('left', 'right')):
        value = getattr(expr, side_a)  # get expr.left then expr.right
        if not isinstance(value, ogAST.PrimSequenceOf):
            continue
        other = getattr(expr, side_b)  # other side
        basic = find_basic_type(value.exprType)
        if basic.kind == 'SequenceOfType':
            # Make a type check of each element of the sequence of
            asn_type = find_basic_type(other.exprType)
            if asn_type.kind == 'SequenceOfType':
                asn_type = asn_type.type
                for idx, elem in enumerate(value.value):
                    check_expr = ogAST.ExprAssign()
                    check_expr.left = ogAST.PrimVariable(debugLine=lineno())
                    check_expr.left.exprType = asn_type
                    check_expr.right = elem
                    warnings.extend(fix_expression_types(check_expr, context))
                    w = Assign_Check_Range(check_expr)
                    if w is not None:
                        warnings.append(w)
                    value.value[idx] = check_expr.right
            # the type of the raw PrimSequenceOf can be set now
            value.exprType.type = asn_type

    if isinstance(expr, ogAST.ExprIn):
        return warnings

    if not expr.right.is_raw and not expr.left.is_raw:
        unknown = [uk_expr for uk_expr in (expr.right, expr.left)
                   if uk_expr.exprType == UNKNOWN_TYPE]
        if unknown:
            #LOG.debug("right: " + expr.right.inputString)
            #LOG.debug("left: " + expr.left.inputString)
            #LOG.debug(traceback.print_stack())
            raise TypeError('Cannot resolve type of "{}"'
                            .format(unknown[0].inputString))

    # In Sequence, Choice and SEQUENCE OF expressions,
    # we must fix missing inner types
    # (due to similarities, the following should be refactored FIXME)
    if isinstance(expr.right, ogAST.PrimSequence):
        #print "Left:", type_name(expr.left.exprType), "Right:", expr.right.inputString
        #print traceback.print_stack()

        # left side must have a known type
        asn_type = find_basic_type(expr.left.exprType)
        if asn_type.kind != 'SequenceType':
            raise TypeError('left side must be a SEQUENCE type')
        for field, fd_expr in expr.right.value.items():
            try:
                for spelling in asn_type.Children:
                    if field.lower().replace('_', '-') == spelling.lower():
                        break
                expected_type = asn_type.Children[spelling].type
            except AttributeError:
                raise TypeError('Field not found: ' + field)
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable(debugLine=lineno())
            check_expr.left.exprType = expected_type
            check_expr.right = fd_expr
            warnings.extend(fix_expression_types(check_expr, context))
            w = Assign_Check_Range(check_expr)
            if w is not None:
                warnings.append(w)
            # Id of fd_expr may have changed (enumerated, choice)
            expr.right.value[field] = check_expr.right
    elif isinstance(expr.right, ogAST.PrimChoiceItem):
        asn_type = find_basic_type(expr.left.exprType)
        field = expr.right.value['choice'].replace('_', '-')
        if asn_type.kind != 'ChoiceType' \
                or field.lower() not in [key.lower()
                                  for key in asn_type.Children.keys()]:
            raise TypeError('Field is not valid in CHOICE:' + field)
        key, = [key for key in asn_type.Children.keys()
                if key.lower() == field.lower()]
        # The type of the value may be known already but if it's
        # a number we need to do a range check.
        #if expr.right.value['value'].exprType == UNKNOWN_TYPE:
        try:
            expected_type = asn_type.Children.get(key).type
        except AttributeError:
            raise TypeError('Field not found in CHOICE: ' + field)
        check_expr = ogAST.ExprAssign()
        check_expr.left = ogAST.PrimVariable(debugLine=lineno())
        check_expr.left.exprType = expected_type
        check_expr.right = expr.right.value['value']
        warnings.extend(fix_expression_types(check_expr, context))
        w = Assign_Check_Range(check_expr)
        if w is not None:
            warnings.append(w)
        expr.right.value['value'] = check_expr.right
    elif isinstance(expr.right, ogAST.PrimConditional):
        # in principle it could also be the left side that is a ternary
        # in which case, its type would be unknown and would need to be
        # set according to the right type.
        # print "[DEBUG] Conditional left = ", expr.left.inputString, ' and right =', expr.right.inputString
        for det in ('then', 'else'):
            # Recursively fix possibly missing types in the expression
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable(debugLine=lineno())
            check_expr.left.inputString = expr.left.inputString  # for debug
            check_expr.left.exprType = expr.left.exprType
            check_expr.right = expr.right.value[det]
            warnings.extend(fix_expression_types(check_expr, context))
            try:
                w = Assign_Check_Range(check_expr)
                if w is not None:
                    warnings.append(w)
            except TypeError as err:
                # If we are just comparing numbers (no assignment), only
                # raise a warning.
                if isinstance(expr, (ogAST.ExprEq, ogAST.ExprNeq)):
                    warnings.append(err)
                else:
                    raise
            expr.right.value[det] = check_expr.right
            # Set the type of "then" and "else" to the reference type:
            expr.right.value[det].exprType = expr.left.exprType
        # We must also set the type of the overall expression to the same
        expr.right.exprType = expr.left.exprType

    elif isinstance(expr.right, ogAST.ExprAppend):
        fix_append_expression_type(expr.right, expr.left.exprType)

    if expr.right.is_raw != expr.left.is_raw:
        warnings.extend(check_type_compatibility(raw_expr, ref_type, context))
        if not raw_expr.exprType.kind.startswith(('Integer',
                                                  'Real',
                                                  'SequenceOf',
                                                  'String')):
            # Raw int/real must keep their type because of the range
            # that can be computed
            # Also true for raw SEQOF and String - Min/Max must not change
            # Substrings: CHECKME XXX
            # EDIT: Size of raw SeqOf and Strings is known from looking at
            # the number of elements. Min/Max are irrelevant. In principle
            # removing SequenceOf and String from here should be OK.
            raw_expr.exprType = ref_type
    else:
        warnings.extend(compare_types(expr.left.exprType,
                                      expr.right.exprType))
    return list(set(warnings))


def expression_list(root, context):
    ''' Parse a list of expression parameters '''
    errors = []
    warnings = []
    result = []
    for param in root.getChildren():
        exp, err, warn = expression(param, context)
        errors.extend(err)
        warnings.extend(warn)
        result.append(exp)
    return result, errors, warnings


def primary_variable(root, context):
    ''' Primary Variable analysis '''
    name = getattr(root.getChild(0), 'text', 'error')
    errors, warnings = [], []
    # Detect reserved keywords
    if name.lower() in ('integer', 'real', 'procedure', 'begin', 'end',
                        'for', 'in', 'out', 'loop'):
        errors.append(f"Use of forbidden keyword for a variable name : {name}")

    possible_constant = is_asn1constant(name)
    if possible_constant is not None:
        prim = ogAST.PrimConstant()
        prim.constant_c_name = possible_constant.varName
        prim.constant_value = possible_constant.value
    elif is_fpar(name, context):
        prim = ogAST.PrimFPAR()
        prim.exprType = find_variable_type(name, context)
    else:
        # We create a variable reference , but it may be a enumerated value,
        # it will be replaced later during type resolution
        prim = ogAST.PrimVariable(debugLine=lineno())
        prim.exprType = UNKNOWN_TYPE

    prim.value = [name]
    prim.inputString = get_input_string(root)
    prim.tmpVar = tmp()

    try:
        prim.exprType = find_variable_type(name, context)
    except AttributeError:
        pass

    return prim, errors, warnings


def is_fpar(name, context):
    name = name.lower()
    if isinstance(context, ogAST.Procedure):
        for each in context.fpar:
            if each['name'].lower() == name.lower():
                return True
    return False


def is_asn1constant(name):
    name = name.lower().replace('-', '_')
    try:
        for varname, vartype in chain(DV.variables.items(),
                                      DV.SDL_Constants.items()):
            if varname.lower().replace('-', '_') == name:
                return vartype
    except AttributeError:
        # Ignore - No DV - e.g. in syntax check mode
        pass
    return None


def binary_expression(root, context):
    ''' Binary expression analysis '''
    errors, warnings = [], []

    ExprNode = EXPR_NODE[root.type]
    expr = ExprNode(
        get_input_string(root),
        root.getLine(),
        root.getCharPositionInLine()
    )
    expr.exprType = UNKNOWN_TYPE
    expr.tmpVar = tmp()

    left, right = root.children
    expr.left,  err_left,  warn_left  = expression(left, context)
    expr.right, err_right, warn_right = expression(right, context)

    errors.extend(err_left)
    warnings.extend(warn_left)
    errors.extend(err_right)
    warnings.extend(warn_right)

    try:
        warnings.extend(fix_expression_types(expr, context))
    except (AttributeError, TypeError) as err:
        errors.append(error(root, str(err)))

    return expr, errors, warnings


def unary_expression(root, context):
    ''' Unary expression analysis
    (NOT and NEG, i.e. "not bar" and "-4" or "-foo" '''
    ExprNode = EXPR_NODE[root.type]
    expr = ExprNode(
        get_input_string(root),
        root.getLine(),
        root.getCharPositionInLine()
    )
    expr.exprType = UNKNOWN_TYPE
    expr.tmpVar   = tmp()

    expr.expr, errors, warnings = expression(root.children[0], context)

    return expr, errors, warnings


def parse_io_expression(root, context):
    ''' Extract all parts of an IO expression (see io_expression below) '''
    result = {
       'inputString': get_input_string(root),
       'kind'    : root.type == lexer.INPUT_EXPRESSION and "input" or "output",
       'msgName'   : None,
       'from'      : None,
       'to'        : None,
       'paramName' : None
       }

    for child in root.getChildren():
        if child.type == lexer.ID:
            result['msgName'] = child.text

        elif child.type == lexer.FROM:
            result['from'] = child.getChild(0).text

        elif child.type == lexer.TO:
            result['to'] = child.getChild(0).text

        elif child.type == lexer.IOPARAM:
            # optional parameter
            result['paramName'] = child.getChild(0).text
        elif child.type == lexer.UNHANDLED:
            # unhandled input refers to a lost message, in the sense of a
            # message received in a SDL state where it is not expected
            result['kind'] = "unhandled_input"
        else:
            raise NotImplementedError("Parsing error in io_expression")

    return result


def io_expression(root, context, io_expr=None):
    ''' Expressions used in the context of observers (for model checking):
        [false] input
        [false] input x [from P] to F
        output
        output X from P [to F]

        Since this is syntactic sugar, we transform these expression into the
        regular form based on the known structure of events: Observable_Event
        type that is generated by kazoo.

        Optional parameter io_expr allows to pass a pre-parsed string
        (format: result of function parse_io_expression defined just above)
    '''
    errors, warnings = [], []

    inputString = get_input_string(root)
    event_kind = "{kind}_event"
    target_option = " and then event.{kind}.{target} = {function}"
    msg_name = " and then present(event.{kind}.event.{function}.msg_{direction}) = {msg}"

    string = "present(event) = "

    if io_expr == None:
        io_expr = parse_io_expression(root, context)  # extract name, source, dest, etc.
    direction = ('input' in io_expr['kind']) and 'in' or 'out'
    kind = io_expr['kind']
    if kind == 'input' or kind == 'output':
        kind = kind + '_event'
    string += kind
    if io_expr['from'] is not None:
        string += target_option.format(kind=kind,
                                       target="source",
                                       function=io_expr['from'])
    if io_expr['to'] is not None:
        string += target_option.format(kind=kind,
                                       target="dest",
                                       function=io_expr['to'])

    func = io_expr['from'] if direction == "out" else io_expr['to']

    if io_expr['msgName'] and not func:
        # When input or output specify a message there must be a source or destination
        if direction == "out":
            errors.append(f"FROM clause is missing in output expression '{inputString}'")
        else:
            errors.append(f"TO clause is missing in input expression '{inputString}'")

    elif io_expr['msgName']:
        string += msg_name.format(kind=kind,
                                  function=func,
                                  direction=direction,
                                  msg=io_expr['msgName'])

    parser = parser_init (string=string)
    new_root = parser.expression()
    tree = new_root.tree
    tree.token_stream = parser.getTokenStream()

    expr, errs, warns = expression(tree, context)
    errors.extend(errs)
    warnings.extend(warns)
    expr.inputString = inputString

    # Now address the optional parameter: if set, we will create an implicit
    # alias definition to the event structure where the parameter is actually
    # present. If an alias of the same type already exists, raise an error
    if io_expr['paramName']:
        path=f"event.{kind}.event.{func}.msg_{direction}.{io_expr['msgName']}"
        parser = parser_init (string=path)
        new_root = parser.expression()
        tree = new_root.tree
        tree.token_stream = parser.getTokenStream()
        param_expr, errs, warns = expression(tree, context)
        errors.extend(errs)
        warnings.extend(warns)
        # We then need to find the parameter name and get its type
        # this is a SEQUENCE by construction (generated by kazoo)
        # and since only one parameter is supported, it has only one field
        if not errs:
            try:
                pname, ptype = list(find_basic_type(param_expr.exprType).Children.items())[0]
                pname = pname.replace('-', '_')
            except (IndexError, AttributeError):
                errors.append(f"No parameter expected for message {io_expr['msgName']}")
            else:
                path += f".{pname}"
                # We must re-parse the expression with the field name
                parser = parser_init (string=path)
                new_root = parser.expression()
                tree = new_root.tree
                tree.token_stream = parser.getTokenStream()
                param_expr, errs, warns = expression(tree, context)
                errors.extend(errs)
                warnings.extend(warns)

                # The type of the parameter is:
                ptype = ptype.type
                for var, (sort, _) in context.variables.items():
                    if var.lower() == io_expr['paramName'].lower():
                        # variable already defined, does it have the same type?
                        if type_name(sort) != type_name(ptype):
                            errors.append(f"Duplicate/incompatible definition"
                                          f" of variable '{io_expr['paramName']}'")
                        elif var.lower() in context.aliases.keys():
                            # Check if already defined variable is an alias,
                            # and if so, if it points to the same element
                            _, alias_expr = context.aliases[var.lower()]
                            if alias_expr.inputString != param_expr.inputString:
                                errors.append(f"Parameter name '{io_expr['paramName']}' "
                                        "is used in another context, but not "
                                        f"pointing to the same content")
                        else:
                            # A variable shall not be declared for this
                            # implicit parameter, as it is actually pointing
                            # to the event.
                            errors.append("A variable declaration with the "
                                    f"same name as parameter '{io_expr['paramName']}' "
                                    "exists and shall be removed or renamed")
                            break
                else:
                    # not found a duplicate definition -> Add an alias
                    context.variables[io_expr['paramName'].lower()] = (ptype, None)
                    context.aliases[io_expr['paramName'].lower()]   = (ptype, param_expr)
    return expr, errors, warnings

def expression(root, context, pos='right'):
    ''' Expression analysis (e.g. 5+5*hello(world)!foo) '''
    logic = (lexer.OR, lexer.AND, lexer.XOR, lexer.IMPLIES)
    arithmetic = (lexer.PLUS, lexer.ASTERISK, lexer.DASH,
                  lexer.DIV, lexer.MOD, lexer.REM)
    relational = (lexer.EQ, lexer.NEQ, lexer.GT, lexer.GE, lexer.LT, lexer.LE)

    if root.type in logic:
        return logic_expression(root, context)
    elif root.type in arithmetic:
        return arithmetic_expression(root, context)
    elif root.type in relational:
        return relational_expression(root, context)
    elif root.type == lexer.IN:
        return in_expression(root, context)
    elif root.type == lexer.APPEND:
        return append_expression(root, context)
    elif root.type == lexer.NOT:
        return not_expression(root, context)
    elif root.type == lexer.NEG:
        return neg_expression(root, context)
    elif root.type == lexer.PAREN:
        return expression(root.children[0], context)
    elif root.type == lexer.CONDITIONAL:
        return conditional_expression(root, context)
    elif root.type == lexer.PRIMARY:
        return primary(root.children[0], context)
    elif root.type == lexer.CALL:
        return call_expression(root, context)
    elif root.type == lexer.SELECTOR:
        return selector_expression(root, context, pos)
    elif root.type == lexer.PROCEDURE_CALL:
        pc, err, warn = procedure_call(root, parent=None, context=context)
        # when used as an expression, the error coordinates must be stripped
        # as they are set for standalone PROCEDURE CALL symbols
        errs = [each[0] for each in err]
        warns = [each[0] for each in warn]
        # Transform the into a PrimCall
        prim = ogAST.PrimCall()
        prim.exprType = pc.exprType
        prim.inputString = pc.inputString
        prim.tmpVar = tmp()
        procedureName = pc.output[0]['outputName']
        prim.value = [procedureName,
                     {'procParams': pc.output[0]['params']}]
        # If the procedure is not defined with a return value, a TypeError
        # has been raised in compare_type, so no need to check it again here
        return prim, errs, warns
    elif root.type == lexer.INPUT_EXPRESSION:
        return io_expression(root, context)
    elif root.type == lexer.OUTPUT_EXPRESSION:
        return io_expression(root, context)
    else:
        raise NotImplementedError(sdl92Parser.tokenNamesMap[root.type] +
                                ' - line ' + str(root.getLine()))


def logic_expression(root, context):
    ''' Logic expression analysis '''
    shortcircuit = ''
    # detect optional THEN in AND/OR expressions, indicating that the
    # short-circuit version of the operator is needed, to prevent the
    # evaluation of the right part if the left part does not evaluate
    # to true.
    if root.type in (lexer.OR, lexer.AND) and len(root.children) == 3:
        if root.children[1].type in (lexer.THEN, lexer.ELSE):
            root.children.pop(1)
            shortcircuit = ' else' if root.type == lexer.OR else ' then'

    expr, errors, warnings = binary_expression(root, context)
    expr.shortcircuit = shortcircuit

    left_bty = find_basic_type(expr.left.exprType)
    right_bty = find_basic_type(expr.right.exprType)

    # If one side of the expression is numeric (not an array of bits), flag it
    # as this will be used to determine the range of the bitwise operation
    # (e.g. "someUnsigned and 'FF'H" has a range of 0..255)
    numeric_bitwise = False

    for bty in left_bty, right_bty:
        if shortcircuit and bty.kind != 'BooleanType':
            msg = 'Shortcircuit operators only work with type Boolean'
            errors.append(error(root, msg))
            break

        if bty.kind == 'BooleanType':
            continue
        elif bty.kind in ('BitStringType', 'OctetStringType') and bty.Min == bty.Max:
            continue
        elif bty.kind == 'SequenceOfType' and bty.Min == bty.Max \
                and find_basic_type(bty.type).kind == 'BooleanType':
            continue
        elif bty.kind.startswith('Integer') and float(bty.Min) >= 0.0:
            # Unsigned types can work for bitwise operations
            numeric_bitwise = True
            continue
        else:
            msg = 'Bitwise operators only work with Booleans, unsigned integers,' \
                  'fixed size SequenceOf Booleans or fixed size BIT/OCTET STRINGs'
            errors.append(error(root, msg))
            break

    if numeric_bitwise:
        # Collect the range of both sides of the expression
        if isinstance(expr.left, (ogAST.PrimBitStringLiteral,
                                  ogAST.PrimOctetStringLiteral)):
            leftMin = leftMax = float(expr.left.numeric_value)
        elif left_bty.kind.startswith('Integer'):
            leftMin, leftMax = float(left_bty.Min), float(left_bty.Max)
        else:
            # Not a number: can be an octet/bit string type
            leftMin = leftMax = None
        if isinstance(expr.right, (ogAST.PrimBitStringLiteral,
                                   ogAST.PrimOctetStringLiteral)):
            rightMin = rightMax = float(expr.right.numeric_value)
        elif right_bty.kind.startswith('Integer'):
            rightMin, rightMax = float(right_bty.Min), float(right_bty.Max)
        else:
            rightMin = rightMax = None

    if left_bty.kind == right_bty.kind == 'BooleanType':
        expr.exprType = BOOLEAN
    # Else: we must define the range of the result if one side is numeric
    if not numeric_bitwise or rightMin is None:
        expr.exprType = expr.left.exprType
    elif leftMin is None:
        expr.exprType = expr.right.exprType
    elif root.type == lexer.AND:
        resMin = min(leftMin, rightMin)
        resMax = min(leftMax, rightMax)
    elif root.type in (lexer.OR, lexer.XOR):
        resMin = min(leftMin, rightMin)
        resMax = max(leftMax, rightMax)

    if numeric_bitwise and leftMin is not None and rightMin is not None:
        expr.exprType = NewInteger (resMin, resMax)

    return expr, errors, warnings

def get_asn1_constant_value(const_val):
    # Return the numerical value of an ASN.1 constant
    # value may be a reference to another constant. In that case we
    # must find the actual value by following the path until we find it
    # however, stop after 20 trials to avoid looping forever in case
    # there is some circular dependency or other weird asn1 construct
    first_str = const_val
    retry = 0
    while retry < 20:
        try:
            return float(const_val)
        except ValueError:
            possible_constant = is_asn1constant(const_val)
            if possible_constant is not None:
                const_val = possible_constant.value
            else:
                # Exceptional case - should be caught by asn1scc
                raise ValueError(str(first_str) + " could not be resolved")
            retry += 1
    raise ValueError(str(first_str) + " actual value not found" )


def arithmetic_expression(root, context):
    ''' Arithmetic expression (+ * - / mod rem) analysis '''
    # Call order is: expression -> arithmetic_expression -> binary_expression
    # the latter calls fix_expression_types to determine the type of each side
    # of the expression. The type of the expression should still be unknown
    # at this point (expr.exprType).
    op = None
    def find_bounds(op, minL, maxL, minR, maxR):
        # op must be an arithmetic operator from python
        candidates = [op(float(l), float(r))
                      for l in [minL, maxL]
                      for r in [minR, maxR]]
        return { 'Min': min(candidates),
                 'Max': max(candidates)}

    #print ("[DEBUG] Arithmetic expression:", get_input_string(root))
    expr, errors, warnings = binary_expression(root, context)

    # Get the basic types to have the ranges
    # If a value is in hex form, use its integer value
    # (this allows to write "x := someVar + 'FF'H")
    if isinstance(expr.left, (ogAST.PrimOctetStringLiteral,
                              ogAST.PrimBitStringLiteral)):
        tMin = tMax = expr.left.numeric_value
        basic_left = NewInteger (tMin, tMax)
    else:
        basic_left  = find_basic_type(expr.left.exprType)

    if isinstance(expr.right, (ogAST.PrimOctetStringLiteral,
                               ogAST.PrimBitStringLiteral)):
        tMin = tMax = expr.right.numeric_value
        basic_right = NewInteger (tMin, tMax)
    else:
        basic_right = find_basic_type(expr.right.exprType)

    try:
        minL = float(basic_left.Min)
        maxL = float(basic_left.Max)
        minR = float(basic_right.Min)
        maxR = float(basic_right.Max)
        # Constants defined in ASN.1 : take their value for the range
        if isinstance(expr.left, ogAST.PrimConstant):
            minL = maxL = get_asn1_constant_value(expr.left.constant_value)
        if isinstance(expr.right, ogAST.PrimConstant):
            minR = maxR = get_asn1_constant_value(expr.right.constant_value)

        #print( "...left/right [{} .. {}]   [{} .. {}]".format(minL, maxL, minR, maxR))

        # compute the bounds, independently from anything else
        bounds = {"Min" : 0, "Max": 0}
        if isinstance(expr, ogAST.ExprDiv) and (minR == 0 or maxR == 0):
            if minR == maxR == 0:
                msg = 'Division by zero is not allowed'
                errors.append(error(root, msg))
            else:
                msg = "Range of right operand may trigger division by zero"
                warnings.append(warning(root, msg))
                bounds = find_bounds(expr.op, minL, maxL, minR or 1, maxR or 1)
        elif isinstance(expr, (ogAST.ExprRem, ogAST.ExprMod)):
            # modulo returns an positive number, however it may not be
            # unsigned, it returns a number of the same sign as its
            # parameter (i.e. the left side of the expression)
            # unless the left side is a universal number, in which case
            # the type has to be deduced from the user of the expression
            # (e.g. the left side of an assignment)
            if minR < 0 or minL < 0:
                msg = "Negative ranges and modulo don't fit well. " \
                        "Use with caution (check Wikipedia for details)"
                warnings.append(warning(root, msg))
            if minR == 0 or maxR == 0:
                msg = f'Modulo: range [{minR} .. {maxR}] allows division by zero'
                errors.append(error(root, msg))
            else:
                possible_values = [minL % minR, minL % maxR, maxL % minR, maxL % maxR]
                bounds["Min"] = min(possible_values)
                bounds["Max"] = max(possible_values)
        else:
            bounds = find_bounds(expr.op, minL, maxL, minR, maxR)

        if is_number(basic_right) or is_number(basic_left):
            is_signed = (not is_number(basic_right))   and minR < 0.0 \
                        or (not is_number(basic_left)) and minL < 0.0

            # create a primary to replace the original expression
            # in case both sides are raw number (int or float)
            if is_integer(basic_right) == is_integer(basic_left) == True:
                prim = ogAST.PrimInteger()
                sort = 'Universal_Integer'
                kind = 'IntegerType'
                op   = int
            elif is_real(basic_right) == is_real(basic_left) == True:
                prim = ogAST.PrimReal()
                sort = 'PrReal'
                kind = 'RealType'
                op   = float
            else:
                # default : signed type
                kind = 'Integer32Type'

            if op is None:
                raise TypeError(
                        error(root, "Invalid operator was used in expression"))

            # cast the result to the resulting type and make it a string
            bound_min = str(op(bounds['Min']))
            bound_max = str(op(bounds['Max']))

            if is_number(basic_right) == is_number(basic_left) == True:
                # two numbers: replace the expression with the computed result
                prim.value = [bound_min]
                prim.exprType = type(sort, (object,), {
                   'kind': kind,
                   'Min' : bound_min,
                   'Max' : bound_max
                })
                expr = prim
            # Check and possibly set result as signed if one side had an ASN.1
            # type that was signed. Don't set to unsigned if the result of the
            # In the other case: unsigned number Minus something, the result
            # may be negative and therefore go out of range. We have to respect
            # the type of the unsigned type and can't emit an error, but
            # we have to raise a warning to let the user know that the
            # operation may result in a negative number
            # example: x := x - 1 with range of x being [0 .. i]
            elif is_number(basic_right) != is_number(basic_left):
                if is_signed and float(bound_min) >= 0:
                    bound_min = str(minR) \
                            if not is_number(basic_right) else str(minL)
                elif not is_signed and float(bound_min) < 0:
                    bound_min = str(minR) \
                            if not is_number(basic_right) else str(minL)
                    msg = "This expression may result in a negative (signed) "\
                          "number while type of operand is unsigned"
                    warnings.append(warning(root, msg))
                if (not is_number(basic_left)
                    and basic_left.kind == 'Integer32Type') or (not is_number
                    (basic_right) and basic_right.kind == 'Integer32Type'):
                    # One of the operands is a loop index (SIGNED)
                    kind = 'Integer32Type'
                expr.exprType = type("Computed_Range",
                        (basic_right if not is_number(basic_right)
                            else basic_left,), {
                   'kind': kind,
                   'Min' : bound_min,
                   'Max' : bound_max
                   })
        # case 3:
        # no numbers, two ASN.1 types. raise an error if there is a
        # signed/unsigned mismatch
        # otherwise (sign ok), set the computed bounds
        # before concluding on the mismatch, check that one side is not
        # a forloop index with positive values (it is signed!)
        else:
            sign_mismatch = False
            if (minL < 0) != (minR < 0):
                sign_mismatch = \
                        (minL >= 0 and basic_left.kind  != 'Integer32Type')\
                     or (minR >= 0 and basic_right.kind != 'Integer32Type')
            if sign_mismatch:
                msg = '"' + expr.left.inputString + '" is ' + ("un"
                      if minL >= 0 else "") + 'signed while "' \
                              + expr.right.inputString + '" is not'
                errors.append(error(root, msg))
            else:  #  sign is consistent on both sides
                bound_min = str(float(bounds['Min']))
                # Must check that sign of resulting bound is still compatible
                # with the sign of the two sides, and fix it in case
                if (minL < 0 or minR < 0) and bounds['Min'] >= 0:
                    bound_min = str(minL) if minL < 0 else str(minR)
                elif (minL >= 0 and minR >=0) and bounds['Min'] < 0:
                    bound_min = "0"

                bound_max = str(float(bounds['Max']))
                attrs = {'Min': bound_min, 'Max': bound_max}
                # If a side is an Integer32 and the other side a Integer64
                # then the base type should be Integer64
                if (basic_right.kind == basic_left.kind
                        or basic_right.kind == "IntegerType"):
                    base_type = basic_right   # Any is ok
                else:
                    base_type = basic_left
                expr.exprType = type('Computed_Range_2', (base_type,), attrs)

        if expr.exprType is not UNKNOWN_TYPE:
            expr.expected_type = expr.exprType

    except (ValueError, AttributeError):
        msg = 'Check that all your numerical data types '\
              'have a range constraint'
        errors.append(error(root, msg))
    except TypeError as err:
        errors.append(str(err))

    if root.type in (lexer.REM, lexer.MOD) and not isinstance(expr,
                                                              ogAST.Primary):
        for ty in (expr.left.exprType, expr.right.exprType):
            if not is_integer(ty):
                msg = 'Mod/Rem expressions can only applied to Integer types'
                errors.append(error(root, msg))
                break
    return expr, errors, warnings


def relational_expression(root, context):
    ''' Relational expression analysis '''
    expr, errors, warnings = binary_expression(root, context)

    if root.type not in (lexer.EQ, lexer.NEQ):
        for ty in (expr.left.exprType, expr.right.exprType):
            if not is_numeric(ty):
                errors.append(error(root,
                    'Operands in relational expressions must be numerical'))
                break

    expr.exprType = BOOLEAN

    return expr, errors, warnings


def in_expression(root, context):
    ''' In expression analysis '''
    # WARNING: Left and right are reversed for IN operator
    root.children[0], root.children[1] = root.children[1], root.children[0]

    expr, errors, warnings = binary_expression(root, context)
    expr.exprType = BOOLEAN

    # check that left part is a SEQUENCE OF or a string
    left_type = expr.left.exprType
    container_basic_type = find_basic_type(expr.left.exprType)
    if container_basic_type.kind == 'SequenceOfType':
        ref_type = container_basic_type.type
    elif container_basic_type.kind.endswith('StringType'):
        ref_type = container_basic_type
    else:
        msg = 'IN expression: right part must be a list'
        errors.append(error(root, msg))
        return expr, errors, warnings

    expr.left.exprType = ref_type

    if find_basic_type(ref_type).kind == 'EnumeratedType':
        fix_enumerated_and_choice(expr, context)

    expr.left.exprType = left_type

    # if left is raw we must check each element with the type on the right
    # in "foo in {enum1, enum2}" we must check that enum1 and enum2 are both
    # of the same type as foo
    if expr.left.is_raw and not expr.right.is_raw:
        # we must check that all entries are compatible with the other side
        # and if they were variables, but are in fact raw enumerants, they
        # must be changed from ogAST.PrimVariable to ogAST.PrimEnumeratedValue
        for idx, value in enumerate(expr.left.value):
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable(debugLine=lineno())
            check_expr.left.exprType = expr.right.exprType
            check_expr.right = value
            try:
                warnings.extend(fix_expression_types(check_expr, context))
                w = Assign_Check_Range(check_expr)
                if w is not None:
                    warnings.append(w)
            except TypeError as err:
                errors.append(error(root, str(err)))
            expr.left.value[idx] = check_expr.right

    try:
        warnings.extend(compare_types(expr.right.exprType, ref_type))
    except TypeError as err:
        errors.append(error(root, str(err)))

    if expr.right.is_raw and expr.left.is_raw:
        # If both sides are raw (e.g. "3 in {1,2,3}"), evaluate expression
        bool_expr = ogAST.PrimBoolean()
        bool_expr.inputString = expr.inputString
        bool_expr.line = expr.line
        bool_expr.charPositionInLine = expr.charPositionInLine
        bool_expr.exprType = type('PrBool', (object,), {'kind': 'BooleanType'})
        if expr.right.value in [each.value for each in expr.left.value]:
            bool_expr.value = ['true']
            warnings.append('Expression {} is always true'
                            .format(expr.inputString))
        else:
            bool_expr.value = ['false']
            warnings.append('Expression {} is always false'
                            .format(expr.inputString))
        expr = bool_expr

    return expr, errors, warnings


def append_expression(root, context):
    ''' Append expression analysis '''
    expr, errors, warnings = binary_expression(root, context)


    #  LOG.debug('append_expression:', expr.left.inputString, 'APPEND', expr.right.inputString)
    if not any(isinstance(each, ogAST.PrimConditional)
            for each in (expr.left, expr.right)):
        left  = find_basic_type(expr.left.exprType)
        right = find_basic_type(expr.right.exprType)
        try:
            warnings.extend(compare_types(left.type, right.type))
        except TypeError as err:
            errors.append(error(root, str(err)))
        except AttributeError:
            # The above only applies to Sequence of, not strings
            # (strings do not have a .type attribute)
            pass

        try:
            attrs = {'Min': str(int(right.Min) + int(left.Min)),
                     'Max': str(int(right.Max) + int(left.Max))}
        except AttributeError:
            # when parsing in standalone mode (eg for copy-paste)
            # the types may not be resolved properly due to lack of context
            # and therefore no Min/Max attributes may be found
            attrs = {'Min': '0', 'Max': '0'}
        # It is wrong to set the type as inheriting from the left side FIXME
        # (only the computed range counts)
        expr.exprType = type('Apnd', (left,), attrs)
    else:
        # If one of the sides is a ternary, how should we know the range?
        expr.exprType = expr.left.exprType
    return expr, errors, warnings


def not_expression(root, context):
    ''' Not expression analysis '''
    expr, errors, warnings = unary_expression(root, context)

    bty = find_basic_type(expr.expr.exprType)
    if bty.kind in ('BooleanType', ):
        if expr.expr.is_raw:
            expr.expr.value = ['true'] \
                    if expr.expr.value == ['false'] else ['false']
            warnings.append(warning
                    (root, 'Expression is always '+ expr.expr.value[0]))
            expr = expr.expr
        else:
            expr.exprType = BOOLEAN
    elif bty.kind in ('BitStringType', 'OctetStringType'):
        expr.exprType = expr.expr.exprType
    elif bty.kind == 'SequenceOfType' and \
            find_basic_type(bty.type).kind == 'BooleanType':
        expr.exprType = expr.expr.exprType
    elif 'IntegerType' in bty.kind and float(bty.Min) >= 0.0:
        # unsigned integers also support the NOT operator
        expr.exprType = expr.expr.exprType
    else:
        msg = 'Bitwise operators only work with booleans, unsigned integers'\
              'sequence of booleans, bit strings and octet strings'
        errors.append(error(root, msg))

    return expr, errors, warnings


def neg_expression(root, context):
    ''' Negative expression analysis (root.type == lexer.NEG)'''
    expr, errors, warnings = unary_expression(root, context)

    basic = find_basic_type(expr.expr.exprType)
    if not is_numeric(basic):
        msg = 'Negative expressions can only be applied to numeric types'
        errors.append(error(root, msg))
        return expr, errors, warnings

    if is_number(basic):
        # If the parameter is a raw number, no need for an Neg expression
        if is_real(basic):
            kind = 'RealType'
            sort = 'PrReal'
        else:
            kind = 'IntegerType'
            sort = 'Universal_Integer'
        expr.expr.value[0] = u'-{}'.format(expr.expr.value[0])
        attrs = {'Min' : str(-float(basic.Max)),
                 'Max' : str(-float(basic.Min)),
                 'kind': kind}
        expr.expr.exprType = type(sort, (object,), attrs)
        return expr.expr, errors, warnings

    try:
        attrs = {'Min': str(-float(basic.Max)), 'Max': str(-float(basic.Min))}
        expr.exprType = type('Neg', (basic,), attrs)
    except (ValueError, AttributeError):
        msg = 'Check that all your numerical data types '\
              'have a range constraint'
        errors.append(error(root, msg))

    return expr, errors, warnings


def conditional_expression(root, context):
    ''' Conditional expression analysis '''
    errors, warnings = [], []

    expr = ogAST.PrimConditional(
        get_input_string(root),
        root.getLine(),
        root.getCharPositionInLine()
    )
    expr.exprType = UNKNOWN_TYPE
    expr.tmpVar   = tmp()

    if_part, then_part, else_part = root.getChildren()

    if_expr, err, warn = expression(if_part, context)
    errors.extend(err)
    warnings.extend(warn)

    then_expr, err, warn = expression(then_part, context)
    errors.extend(err)
    warnings.extend(warn)

    else_expr, err, warn = expression(else_part, context)
    errors.extend(err)
    warnings.extend(warn)

    if find_basic_type(if_expr.exprType).kind != 'BooleanType':
        msg = 'Conditions in conditional expressions must be of type Boolean'
        errors.append(error(root, msg))

    expr.value = {
        'if'    : if_expr,
        'then'  : then_expr,
        'else'  : else_expr,
        'tmpVar': expr.tmpVar
    }
    # at the end, expr.exprType is still UNKNOWN TYPE
    # it can only be resolved by from the context
    # But do we care about expr.exprType? What counts is expr.value['then']
    # and expr.value['else']  .exprType...
    #print traceback.format_stack (limit=2)
    return expr, errors, warnings


def call_expression(root, context, pos="right"):
    ''' Call expression analysis '''
    # contains "pos" because it can be on the left side of an "assign"
    # therefore this has to be propagated, in particular to check
    # if the root (which has not been analysed before) is a choice field
    # (this being not permitted - choice must be set via asn1 notation)
    errors, warnings = [], []
    #print("call expression", get_input_string(root))

    if root.children[0].type == lexer.PRIMARY:
        # check if it is a call to a special operator or procedure
        primary = root.children[0]
        if primary.children[0].type == lexer.VARIABLE:
            variable = primary.children[0]
            ident = variable.children[0].text.lower()
            for each in valid_output (context):
                if ident == each.lower():
                    return primary_call(root, context)

    # not a call to a special operator or procedure
    # => it is either an index or a substring

    num_params = len(root.children[1].children)

    if num_params == 1:
        res = primary_index(root, context, pos)
        return res

    elif num_params == 2:
        return primary_substring(root, context, pos)

    #  more than 2 parameters? that does not correspond to anything -> error
    else:
        node = ogAST.PrimCall()  # Use error node instead?
        node.inputString = get_input_string(root)
        node.exprType = UNKNOWN_TYPE
        errors.append(error(root, 'Wrong number of parameters'))
        return node, errors, warnings


def primary_call(root, context):
    ''' Primary call analysis (procedure or special operator) '''
    node, errors, warnings = ogAST.PrimCall(), [], []

    node.exprType = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar = tmp()

    nameLower = root.children[0].children[0].children[0].text.lower()
    # Retrieve the right casing from the declaration
    for name in valid_output (context):
        if nameLower == name.lower():
            break
    else:
        name = nameLower

    params, params_errors, param_warnings = \
                                expression_list(root.children[1], context)
    errors.extend(params_errors)
    warnings.extend(param_warnings)

    node.value = [name, {'procParams': params}]

    try:
        node.exprType, warns = check_call(nameLower, params, context)
        for w in warns:
            warnings.append(warning(root, w))
    except (TypeError, ValueError) as err:
        errors.append(error(root, str(err)))
    except OverflowError:
        errors.append(error(root, 'Result can exceeds 64-bits'))

    return node, errors, warnings


def primary_index(root, context, pos):
    ''' Primary index analysis '''

    # root.children[0] is the variable (with possible selector)
    # pos is either right or left. left if it is an assigned variable
    # root.children[1] is the index

    # if pos is left, we check here if the type is mutable or not
    # an array of variable size is immutable and must be assigned
    # with an ASN.1 Value notation (to set the size) or append
    # an array of fixed size is mutable - individual values can be updated

    node, errors, warnings = ogAST.PrimIndex(), [], []

    node.exprType    = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar      = tmp()

    receiver, receiver_err, receiver_warn = \
                                expression(root.children[0], context, pos)

    receiver_bty = find_basic_type(receiver.exprType)

    errors.extend(receiver_err)
    warnings.extend(receiver_warn)

    params, params_errors, param_warnings = \
                                expression_list(root.children[1], context)
    errors.extend(params_errors)
    warnings.extend(param_warnings)

    node.value = [receiver, {'index': params}]

    if receiver_bty.kind in ('SequenceOfType', 'OctetStringType', 'BitStringType'):
        # Range of the receiver (SEQUENCE(SIZE(N)) - check N
        if isinstance(receiver, ogAST.PrimSubstring):
            r_min, r_max = substring_range(receiver)
        else:
            r_min, r_max = receiver_bty.Min, receiver_bty.Max

        # check if the type is mutable (explanation above)
        mutable_type = (pos == "right") or (r_min == r_max)

        if not mutable_type:
            errors.append(error(root, "Variable-length type is immutable, "
                "you must assign all values at once to set the size "
                "(syntax: variable := {3, 14, 15})"))

        if receiver_bty.kind == 'SequenceOfType':
            # receiver_bty.type is the type of the array elements
            node.exprType = receiver_bty.type
        elif receiver_bty.kind == 'OctetStringType':
            # Octet string elements = unsigned integer
            node.exprType = UINT8
        elif receiver_bty.kind == 'BitStringType':
            # Bit string elements = boolean
            node.exprType = type('Bit',
                                  BOOLEAN.__bases__,
                                  dict(BOOLEAN.__dict__))

        idx_bty = find_basic_type(params[0].exprType)
        if not is_integer(idx_bty):
            errors.append(error(root, 'Index is not an integer'))
        #elif is_number(idx_bty):
            # Check range only if index is given as a raw number
            # EDIT: why? the variable used for indexing must be checked
        if float(idx_bty.Max) >= float(r_max) \
                or float(idx_bty.Min) < 0:
            msg = f'Range of index is [{idx_bty.Min} .. {idx_bty.Max}] '\
                   ': risk of overflow (expected range: [0 .. {int(r_max)-1}])'
            if is_number(idx_bty):
                # index is a raw numer => raise an error
                errors.append(error(root, msg))
            else:
                # index is a variable => raise a warning
                warnings.append(warning(root, msg))
        elif float(idx_bty.Min) > float(r_min):
            warnings.append(warning(root,
                                    'Index higher than range min value'))
    else:
        msg = 'Index can only be applied to type SequenceOf'
        errors.append(error(root, msg))

    return node, errors, warnings


def primary_substring(root, context, pos):
    ''' Primary substring analysis '''
    # Check documentation of primary_index
    # Substring parameters should be ground expression : var (3, 5)
    # and not var (a, b), because allowing a and b to have a range does
    # not allow to compute a fixed size for the substring
    # It is only reported as a warning but this is questionable

    node, errors, warnings = ogAST.PrimSubstring(), [], []

    node.exprType    = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar      = tmp()

    receiver, receiver_err, receiver_warn = \
                                    expression(root.children[0], context, pos)
    receiver_bty = find_basic_type(receiver.exprType)
    errors.extend(receiver_err)
    warnings.extend(receiver_warn)

    params, params_errors, param_warnings = \
                                    expression_list(root.children[1], context)
    errors.extend(params_errors)
    warnings.extend(param_warnings)

    node.value = [receiver, {'substring': params, 'tmpVar': tmp()}]

    if receiver_bty.kind == 'SequenceOfType' or \
            receiver_bty.kind.endswith('StringType'):
        # min0/max0 and min1/max1 are the values of the substring bounds
        try:
            min0 = float(find_basic_type(params[0].exprType).Min)
            max0 = float(find_basic_type(params[0].exprType).Max)
        except AttributeError as err:
            msg = 'First parameter of substring: could not resolve type'
            errors.append(error(root, msg))
            LOG.debug('In primary_substring: ' + str(err))
            min0, max0 = 0, 0
        try:
            min1 = float(find_basic_type(params[1].exprType).Min)
            max1 = float(find_basic_type(params[1].exprType).Max)
        except AttributeError as err:
            msg = 'Second parameter of substring: could not resolve type'
            errors.append(error(root, msg))
            LOG.debug('In primary_substring: ' + str(err))
            min1, max1 = 0, 0

        if min0 != max0 or min1 != max1:
            msg = 'Substring bounds should be ground expressions'
            warnings.append(warning(root, msg))

        if min0 < 0 or min1 < 0:
            msg = 'Substring bounds cannot be negative'
            errors.append(error(root, msg))
            min1, max1 = 0, 0

        # Range of the receiver (SEQUENCE(SIZE(XXX)) - check XXX
        if isinstance(receiver, ogAST.PrimSubstring):
            r_min, r_max = substring_range(receiver)
        else:
            r_min, r_max = receiver_bty.Min, receiver_bty.Max

        # check if the type is mutable if user tries to assign value
        mutable_type = (pos == "right") or (r_min == r_max)

        if not mutable_type:
            errors.append(error(root, "Variable-length type is immutable, "
                "you must assign all values at once to set the size "
                "(syntax: variable := {3, 14, 15})"))

        #node.exprType = type('SubStr', (receiver_bty,),
        # The substring has to be subtyping the original type to get its name
        # This is needed to support expressions such as "a(1,2) := {1,1}"
        # -> assigning a raw expression to a substring requires the type
        # of the recipient to be known
        node.exprType = type('SubStr', (receiver.exprType,),
                             {'Min': str(int(min1) - int(max0) + 1),
                              'Max': str(int(max1) - int(min0) + 1)})
        basic = find_basic_type(node.exprType)
        if int(min0) > int(min1):
            # right value lower range smaller than left value lower bound
            msg = ('Substring end range could be lower than start range'
                   ' ({}>{})'.format(min0, min1))
            warnings.append(warning(root, msg))
        if int(max0) > int(max1):
            # left value upper bound can be bigger than right value upper bound
            msg = ('Substring start range could be higher than end range'
                   ' ({}>{})'.format(max0, max1))
            warnings.append(warning(root, msg))
        if int(min0) > int(receiver_bty.Max):
            # real error: range starts with a clearly out of range value
            msg = 'Substring left bounds ({}) bigger than index higher bound '\
                  '({})'.format(min0, receiver_bty.Max)
            errors.append(error(root, msg))
        if  int(max1) > int(receiver_bty.Max):
            msg = 'Substring right bound ({}) bigger than index higher bound '\
                  '({})'.format(max1, receiver_bty.Max)
            warnings.append(warning(root, msg))
    else:
        msg = 'Substring can only be applied to types SequenceOf or String'
        errors.append(error(root, msg))

    return node, errors, warnings


def selector_expression(root, context, pos="right"):
    ''' Selector expression analysis '''
    errors, warnings = [], []

    node = ogAST.PrimSelector()
    node.exprType = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar = tmp()
    #print "selector expression"
    #print traceback.print_stack()
    receiver, receiver_err, receiver_warn = \
                                expression(root.children[0], context, pos)
    receiver_bty = find_basic_type(receiver.exprType)
    errors.extend(receiver_err)
    warnings.extend(receiver_warn)

    field_name = root.children[1].text.replace('_', '-').lower()
    try:
        if receiver_bty.kind == 'ChoiceType' and pos == "left":
            # Error if this is the left part of an assignment
            errors.append(warning(root, 'Choice assignment: '
                                      'use "var := {field}: value" instead of '
                                      '"var.{field} := value"'
                                      .format(field=field_name)))
        for n, f in receiver_bty.Children.items():
            if n.lower() == field_name:
                node.exprType = f.type
                break
        else:
            msg = f'Field "{field_name}" not found in expression {receiver.inputString}'
            errors.append(error(root, msg))
    except AttributeError:
        # When parsing for syntax or copy-paste, receiver_bty may
        # not be found
        # CHECKME: but then we don't detect nonexistent variable in a function
        # call?!?!
        pass

    node.value = [receiver, field_name.replace('-', '_').lower()]

    return node, errors, warnings


def primary(root, context):
    ''' Literal expression analysis '''
    prim, errors, warnings = None, [], []

    if root.type == lexer.VARIABLE:
        return primary_variable(root, context)
    elif root.type == lexer.INT:
        prim = ogAST.PrimInteger()
        prim.value = [root.text.lower()]
        prim.exprType = type('Universal_Integer', (object,), {
            'kind': 'IntegerType',
            'Min' : root.text,
            'Max' : root.text
        })
    elif root.type in (lexer.TRUE, lexer.FALSE):
        prim          = ogAST.PrimBoolean()
        prim.value    = [root.text.lower()]
        prim.exprType = type('PrBool', (object,), {'kind': 'BooleanType'})
#   elif root.type == lexer.NULL:
#       prim = ogAST.PrimNull()
#       prim.value = [root.text.lower()]
#       prim.exprType = type('PrNull', (object,), {'kind': 'NullType'})
    elif root.type == lexer.FLOAT:
        prim = ogAST.PrimReal()
        prim.value = [root.text]
        prim.exprType = type('PrReal', (object,), {
            'kind': 'RealType',
            'Min':  prim.value[0],
            'Max':  prim.value[0]
        })
    elif root.type == lexer.STRING:
        if root.text[-1] in ('B', 'b'):
            prim = ogAST.PrimBitStringLiteral()
            try:
                # Transform to a hex string
                as_number = int(root.text[1:-2], 2)
                # transform to a string with padding zeros to have an even
                # number of bytes in the hexadecimal representation
                as_bytes  = binascii.b2a_hex(
                        as_number.to_bytes(
                            (as_number.bit_length() + 7) // 8, 'big'))
                as_hex    = binascii.unhexlify(as_bytes)
                prim.value = f"'{as_hex.hex()}'"
                prim.numeric_value = as_number
                prim.printable_string = root.text
                prim.exprType = type('PrStr', (object,), {
                    'kind': 'BitStringType',
                    'Min': str(len(prim.value) - 2),
                    'Max': str(len(prim.value) - 2),
                    'NumericValue': prim.numeric_value,
                    'NumberOfBits': len(root.text[1:-2])  # in user string
                })
            except (ValueError, TypeError) as err:
                errors.append(error
                        (root, 'Bit string literal: {}'.format(err)))
                prim.value = "''"
        elif root.text[-1] in ('H', 'h'):
            prim = ogAST.PrimOctetStringLiteral()
            try:
                # hexstring is the converted from hex to numbers
                octets = root.text[1:-2]  # just keep the hex numbers
                if len(octets) % 2 != 0:
                    # make sure there is an even number of bytes
                    octets = f'0{octets}'
                hexstring = codecs.decode(octets, 'hex')  # -> bytes
                prim.hexstring = hexstring
                as_hex = hexstring.hex()   # -> string
                as_number = int(as_hex, 16)
                try:
                    # In case the HEX value only contains ascii characters
                    prim.printable_string = hexstring.decode('utf-8')
                    #prim.value = (f"'{prim.printable_string}'")
                    # We must keep the HEX value for the length to be correct
                    prim.value = f"'{as_hex}'"
                except:
                    prim.printable_string = root.text
                    prim.value = f"'{as_hex}'"
                # store the integer number corresponding to the hex representation
                prim.numeric_value = as_number
                prim.exprType = type('PrStr', (object,), {
                    'kind': 'OctetStringType',
                    'Min': str(len(prim.value) - 2),
                    'Max': str(len(prim.value) - 2),
                    'NumericValue': prim.numeric_value
                })
            except (ValueError, TypeError) as err:
                errors.append(error
                        (root, 'Octet string literal: {}'.format(err)))
                prim.value = "''"
        else:
            prim = ogAST.PrimStringLiteral()
            prim.value = root.text
            prim.exprType = type('PrStr', (object,), {
                'kind': 'StringType',
                'Min': str(len(prim.value) - 2),
                'Max': str(len(prim.value) - 2),
                'NumericValue': -1
            })
    elif root.type == lexer.FLOAT2:
        prim = ogAST.PrimMantissaBaseExp()
        mant = float(root.getChild(0).toString())
        base = int(root.getChild(1).toString())
        exp = int(root.getChild(2).toString())
        # Compute mantissa * base**exponent to get the value type range
        value = float(mant * pow(base, exp))
        prim.value = {'mantissa': mant, 'base': base, 'exponent': exp}
        prim.exprType = type('PrMantissa', (object,), {
            'kind': 'RealType',
            'Min': str(value),
            'Max': str(value)
        })
    elif root.type == lexer.EMPTYSTR:
        # Primary "{ }" used in empty SEQUENCE OF (i.e. "{}")
        # and also in value notation of SEQUENCEs that have no fields
        prim = ogAST.PrimEmptyString()
        prim.value = []
        prim.exprType = UNKNOWN_TYPE
        # Let fix_expression_type resolve this type
    elif root.type == lexer.CHOICE:
        prim = ogAST.PrimChoiceItem()
        choice = root.getChild(0).toString()
        expr, err, warn = expression(root.getChild(1), context)
        errors.extend(err)
        warnings.extend(warn)
        prim.value = {'choice': choice, 'value': expr}
        prim.exprType = UNKNOWN_TYPE
    elif root.type == lexer.SEQUENCE:
        prim = ogAST.PrimSequence()
        prim.value = {}
        for elem in root.getChildren():
            if elem.type == lexer.ID:
                field_name = elem.text
            else:
                prim.value[field_name], err, warn = expression(elem, context)
                errors.extend(err)
                warnings.extend(warn)
        prim.exprType = UNKNOWN_TYPE
    elif root.type == lexer.SEQOF:
        prim = ogAST.PrimSequenceOf()
        prim.value = []
        for elem in root.getChildren():
            prim_elem, prim_elem_errors, prim_elem_warnings = \
                                                      expression(elem, context)
            errors += prim_elem_errors
            warnings += prim_elem_warnings
            prim_elem.inputString = get_input_string(elem)
            prim_elem.line = elem.getLine()
            prim_elem.charPositionInLine = elem.getCharPositionInLine()
            prim.value.append(prim_elem)
        prim.exprType = type('PrSO', (object,), {
            'kind': 'SequenceOfType',
            'Min': str(len(root.children)),
            'Max': str(len(root.children)),
            'type': prim_elem.exprType
        })
    elif root.type == lexer.STATE:
        prim = ogAST.PrimStateReference()
        prim.exprType = type ("StateEnumeratedType", (ENUMERATED,), {})
        prim.exprType.kind = 'StateEnumeratedType'
        prim.exprType.EnumValues = {value: type('',
                                               (object,),
                                               {'EnumID': value})
                                    for value in context.mapping.keys()}
    else:
        errors.append('Parsing error (token {}, line {}, "{}")'
                      .format(sdl92Parser.tokenNamesMap[root.type],
                              root.getLine(),
                              get_input_string(root)))
        prim = ogAST.Primary()

    prim.inputString = get_input_string(root)
    prim.tmpVar = tmp()

    return prim, errors, warnings


def variables(root, ta_ast, context, monitor=False):
    ''' Process declarations of variables (dcl a,b Type := 5)
        if monitor is True, the result will be placed in the
        "monitors" dictionary of the context, instead of the
        variables. this is for use in the context of observers
        for model checking.
        variable can be defined as an alias to a field of a structure,
        in that case the syntax is "dcl variable type renames path.to.field;"
        '''
    var = []
    errors = []
    warnings = []
    asn1_sort, def_value = UNKNOWN_TYPE, None
    for child in root.getChildren():
        if child.type == lexer.ID:
            renames = False
            var.append(child.text)
        elif child.type == lexer.SORT:
            sort = child.getChild(0).text
            # Find corresponding type in ASN.1 model
            try:
                asn1_sort = sdl_to_asn1(sort)
            except TypeError as err:
                errors.append(error(root, str(err)))
        elif child.type == lexer.RENAMES:
            if monitor:
                errors.append(f'{var[-1]}: aliasing on monitors is not allowed')
            else:
                context._aliases_ast.append((var[-1].lower(),
                                             asn1_sort,
                                             child.getChild(0),
                                             ta_ast))
        elif child.type == lexer.GROUND:
            # Default value for a variable - needs to be a ground expression
            def_value, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
            expr = ogAST.ExprAssign()
            expr.left = ogAST.PrimVariable(debugLine=lineno())
            expr.left.inputString = var[-1]
            expr.left.exprType = asn1_sort
            expr.right = def_value
            try:
                warnings.extend(fix_expression_types(expr, context))
                w = Assign_Check_Range(expr)
                if w is not None:
                    warnings.append(w)
                def_value = expr.right
                # Once we have resolved the expression we must check that
                # it does not contain any reference to a variable, as
                # it would mean it is not a ground expression. We must
                # search the "default value" expression recursively
                def rec_find_ref_to_variable(some_expr):
                    if isinstance(some_expr,
                            (ogAST.PrimVariable,
                             ogAST.PrimIndex,
                             ogAST.PrimSelector)):
                        return some_expr.inputString
                    elif isinstance(some_expr, ogAST.PrimSequence):
                        for _, field_expr in some_expr.value.items():
                            f = rec_find_ref_to_variable(field_expr)
                            if f is not None:
                                return f
                    elif isinstance(some_expr, ogAST.PrimChoiceItem):
                        f = rec_find_ref_to_variable(some_expr.value['value'])
                        if f is not None:
                            return f
                    elif isinstance(some_expr, ogAST.PrimSequenceOf):
                        for field_expr in some_expr.value:
                            f = rec_find_ref_to_variable(field_expr)
                            if f is not None:
                                return f
                    elif isinstance(some_expr, ogAST.ExprNeg):
                        f = rec_find_ref_to_variable(some_expr.expr)
                        if f is not None:
                            return f
                    else:
                        return None
                faulty_field = rec_find_ref_to_variable(expr.right)
                if faulty_field is not None:
                    errors.append(f"Variable {var[-1]}:"
                            " default value is not a ground expression -"
                            f" remove reference to variable {faulty_field}")
            except(AttributeError, TypeError, Warning) as err:
                #print (traceback.format_exc())
                errors.append('Types are incompatible in DCL assignment: '
                    'left (' +
                    expr.left.inputString + ', type= ' +
                    type_name(expr.left.exprType) + '), right (' +
                    expr.right.inputString + ', type= ' +
                    type_name(expr.right.exprType) + ') ' + str(err))
            else:
                if def_value.exprType == UNKNOWN_TYPE or not \
                         isinstance(def_value, (ogAST.ExprAppend,
                                                ogAST.PrimSequenceOf,
                                                ogAST.PrimStringLiteral)):
                    def_value.exprType = asn1_sort
                def_value.expected_type = asn1_sort

            if not def_value.is_raw and \
                    not isinstance(def_value, ogAST.PrimConstant):
                errors.append(f'In variable declaration {var[-1]}: default'
                              ' value is not a valid ground expression')
            if monitor:
                errors.append(f'In monitor declaration {var[-1]}: default'
                              ' value is not allowed')
        else:
            warnings.append('Unsupported variables construct type: ' +
                    str(child.type))
    for variable in var:
        # note: aliases are added to the variables list. code generator have
        # to be careful to make the link with the actual field
        if not hasattr(context, 'variables'):
            errors.append('Variables/monitors shall not be declared here')
        # Add to the context and text area AST entries
        elif(not monitor and (variable.lower() in context.variables
                  or variable.lower() in ta_ast.variables)):
            errors.append('Variable "{}" is declared more than once'
                          .format(variable))
        elif (monitor and (variable.lower() in context.monitors
                  or variable.lower() in ta_ast.monitors)):
            errors.append('Monitor "{}" is declared more than once'
                          .format(variable))

        elif not monitor:
            context.variables[variable.lower()] = (asn1_sort, def_value)
            ta_ast.variables[variable.lower()] = (asn1_sort, def_value)
        else:
            context.monitors[variable.lower()] = (asn1_sort, def_value)
            ta_ast.monitors[variable.lower()] = (asn1_sort, def_value)
    if not DV:
        errors.append('No visible dataview to make semantic checks on variable declarations')
    return errors, warnings


def dcl(root, ta_ast, context, monitor=False):
    ''' Process a set of variable declarations '''
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.VARIABLES:
            err, warn = variables(child, ta_ast, context, monitor)
            errors.extend(err)
            warnings.extend(warn)
        else:
            warnings.append(
                    'Unsupported dcl construct, type: ' + str(child.type))
    return errors, warnings


def fpar(root):
    ''' Process a formal parameter declaration '''
    errors = []
    warnings = []
    params = []
    asn1_sort = UNKNOWN_TYPE
    for param in root.getChildren():
        param_names = []
        sort = ''
        direction = 'in'
        assert param.type == lexer.PARAM
        for child in param.getChildren():
            if child.type in (lexer.INOUT, lexer.OUT):
                direction = 'out'
            elif child.type == lexer.IN:
                pass
            elif child.type == lexer.ID:
                # variable name
                param_names.append(child.text)
            elif child.type == lexer.SORT:
                sort = child.getChild(0).text
                try:
                    asn1_sort = sdl_to_asn1(sort)
                except TypeError as err:
                    errors.append(str(err) +
                            '(line ' + str(child.getLine()) + ')')
                for name in param_names:
                    params.append({'name': name, 'direction': direction,
                                   'type': asn1_sort})
            else:
                warnings.append(
                        'Unsupported construct in FPAR, type: ' +
                        str(child.type))
    return params, errors, warnings


def composite_state(root, parent=None, context=None):
    ''' Parse a composite state (incl. state aggregation) definition '''
    if root.type == lexer.COMPOSITE_STATE:
        comp = ogAST.CompositeState()
    elif root.type == lexer.STATE_AGGREGATION:
        comp = ogAST.StateAggregation()
    errors, warnings = [], []
    # Create a list of all inherited data
    try:
        comp.global_variables = dict(context.variables)
        comp.global_variables.update(context.global_variables)
        comp.global_monitors = dict(context.monitors)
        comp.global_monitors.update(context.global_monitors)
        comp.global_timers = list(context.timers)
        comp.global_timers.extend(list(context.global_timers))
        comp.input_signals = context.input_signals
        comp.output_signals = context.output_signals
        comp.procedures = context.procedures
        comp.operators = dict(context.operators)
    except AttributeError:
        LOG.debug('Procedure context is undefined')
    inner_proc = []

    # Gather the list of states defined in the composite state
    # and map a list of transitions to each state
    comp.mapping = {name: [] for name in get_state_list(root)}
    # Same for continuous signal mapping
    comp.cs_mapping = {name: [] for name in get_state_list(root)}
    # Same for CONNECT transitions
    comp.connect_mapping = {name: [] for name in get_state_list(root)}

    inner_composite, states, floatings, starts = [], [], [], []
    for child in root.getChildren():
        if child.type == lexer.ID:
            comp.line = child.getLine()
            comp.charPositionInLine = child.getCharPositionInLine()
            comp.statename = child.toString().lower()
            # Set the path of so that elements inside the state will be
            # easy to locate for error reporting
            comp.path = context.path + [f'STATE {comp.statename}']
        elif child.type == lexer.COMMENT:
            comp.comment, _, _ = end(child)
        elif child.type == lexer.IN:
            # state entry point
            for point in child.getChildren():
                comp.state_entrypoints.add(point.toString().lower())
        elif child.type == lexer.OUT:
            # state exit point
            for point in child.getChildren():
                comp.state_exitpoints.add(point.toString().lower())
        elif child.type == lexer.TEXTAREA:
            textarea, err, warn = text_area(child, context=comp)
            if textarea.signals:
                msg = "Signals shall not be declared in a state"
                errors.append([msg, [textarea.pos_y, textarea.pos_y], []])
                textarea.errors.append(msg)
            errors.extend(err)
            warnings.extend(warn)
            comp.content.textAreas.append(textarea)
        elif child.type == lexer.PROCEDURE:
            new_proc, content, err, warn = procedure_pre(child, context=comp)
            inner_proc.append((new_proc, content))
            errors.extend(err)
            warnings.extend(warn)
            if new_proc.inputString.strip().lower() == 'entry':
                comp.entry_procedure = new_proc
            elif new_proc.inputString.strip().lower() == 'exit':
                comp.exit_procedure = new_proc
            # check for duplicate declaration
            dupl_errs = []
            check_duplicate_procedures(comp, new_proc, dupl_errs)
            for err_str in dupl_errs:
                errors.append([err_str, [new_proc.pos_x, new_proc.pos_y], []])
                new_proc.errors.append(err_str)
            # Add procedure to the context, to make it visible at scope level
            comp.content.inner_procedures.append(new_proc)
            context.procedures.append(new_proc)
        elif child.type in (lexer.COMPOSITE_STATE, lexer.STATE_AGGREGATION):
            inner_composite.append(child)
        elif child.type == lexer.STATE:
            states.append(child)
        elif child.type == lexer.FLOATING_LABEL:
            floatings.append(child)
        elif child.type == lexer.START:
            starts.append(child)
        elif child.type == lexer.STATE_PARTITION_CONNECTION:
            # TODO (see section 11.11.2)
            warnings.append(['Ignoring state partition connections',
                            [0, 0], []])
        else:
            warnings.append(['Unsupported construct in nested state, type: {}'
                             '- line {} - State name: {}'
                             .format(str(child.type),
                                     str(child.getLine()),
                                     str(comp.statename)),
                             [0 , 0],   # No graphical position
                             []])
    if (floatings or starts) and isinstance(comp, ogAST.StateAggregation):
        msg = 'State aggregation can only contain composite state(s)'
        errors.append([msg, [0, 0], []])
        comp.errors.append(msg)
    for each in inner_composite:
        # Parse inner composite states after the text areas to make sure
        # that all variables are propagated to the inner scope
        inner, err, warn = composite_state(each, parent=None, context=comp)
        if isinstance(comp, ogAST.StateAggregation):
            # State aggregation contain only composite states, so we must
            # add empty mapping information since there are no transitions
            comp.mapping[inner.statename.lower()] = []
            comp.cs_mapping[inner.statename.lower()] = []
            comp.connect_mapping[inner.statename.lower()] = []
        errors.extend(err)
        warnings.extend(warn)
        comp.composite_states.append(inner)
    # Parse other elements after the nested states
    for each in starts:
         # START transition (fills the mapping structure)
        st, err, warn = start(each, context=comp)
        errors.extend(err)
        warnings.extend(warn)
        if st.inputString:
            comp.content.named_start.append(st)
        elif not comp.content.start:
            comp.content.start = st
        else:
            msg = 'Only one unnamed START transition is allowed'
            errors.append([msg, [st.pos_x, st.pos_y], []])
            st.errors.append(msg)
        if not comp.terminators:
            msg = 'Transition is incomplete'
            errors.append([msg, [st.pos_x, st.pos_y], []])
            st.errors.append(msg)
    for each in floatings:
        lab, err, warn = floating_label(each, parent=None, context=comp)
        errors.extend(err)
        warnings.extend(warn)
        comp.content.floating_labels.append(lab)
    for proc, content in inner_proc:
        # parse content of procedures - all scopes are set
        err, warn = procedure_post(proc, content, context=comp)
        errors.extend(err)
        warnings.extend(warn)
    for each in states:
        # And parse the states after inner states to make sure all CONNECTS
        # are properly defined.
        # Fill up the 'mapping' structure.
        newstate, err, warn = state(each, parent=None, context=comp)
        errors.extend(err)
        warnings.extend(warn)
        comp.content.states.append(newstate)
    # Post-processing: check that all RETURNS of the composite state have a
    # corresponding CONNECT in the outer state
    context=comp
    for each in context.content.states:
        if each.composite:
            for exitpt in each.composite.state_exitpoints:
                if exitpt not in context.connect_mapping[each.composite.statename]:
                    msg = (f'State "{each.composite.statename}":'
                           f' missing CONNECT for exitpoint "{exitpt}"')
                    errors.append([msg, [each.pos_x, each.pos_y], []])

    # Post-processing: check that all NEXTSTATEs have a corresponding STATE
    for t in comp.terminators:
        if t.kind != "next_state":
            continue
        ns = t.inputString.lower()
        if not ns in [s.lower() for s in comp.mapping.keys()] + ['-', '-*']:
            msg = f'In composite state {comp.statename}: missing definition'\
                  f'of substate "{ns.upper()}"'
            errors.append([msg, [t.pos_x or 0, t.pos_y or 0], []])
            t.errors.append(msg)
    for each in chain(errors, warnings):
        each[2].insert(0, 'STATE {}'.format(comp.statename))
    return comp, errors, warnings


def procedure_pre(root, parent=None, context=None):
    ''' Parse a procedure interface - the content has to be parsed after
        all procedure interfaces are known, to prevent missing references '''
    errors = []
    warnings = []
    proc = ogAST.Procedure()
    content = []

    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            proc.pos_x, proc.pos_y, proc.width, proc.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            proc.pos_x = symbolid(child)
        elif child.type == lexer.ID:
            proc.line = child.getLine()
            proc.charPositionInLine = child.getCharPositionInLine()
            proc.inputString = child.toString()
            # Update the path for locating symbol associated to errors
            proc.path = context.path + [f'PROCEDURE {proc.inputString}']
        elif child.type == lexer.COMMENT:
            # there can be two comments in a procedure declaration
            # keep only one and concatenate strings
            comment, _, _ = end(child)
            if not proc.comment:
                proc.comment = comment
            else:
                proc.comment.inputString += ' {}'.format(comment.inputString)
        elif child.type == lexer.TEXTAREA:
            textarea, err, warn = text_area(child, context=proc)
            if textarea.signals:
                msg = f'In procedure {proc.inputString}:' \
                    ' signals shall not be declared in a procedure'
                errors.append([msg, [textarea.pos_x or 0, textarea.pos_y or 0], []])
                textarea.errors.append(msg)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.textAreas.append(textarea)
        elif child.type == lexer.EXTERNAL:
            proc.external = True
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            # convert error strings to the proper list
            for each in err:
                msg = f'In procedure {proc.inputString}: {each}'
                errors.append([msg, [0, 0], []])
            for each in warn:
                msg = f'In procedure {proc.inputString}: {each}'
                warnings.append([msg, [0, 0], []])
            proc.fpar = params
        elif child.type == lexer.RETURNS:
            #  Declaration not in a text area...
            if proc.return_type is not None:
                errors.append([f'In procedure {proc.inputString}: '
                        'duplicate "returns" statement', [0, 0], []])
            try:
                proc.return_type, proc.return_var = procedure_returns(child)
            except TypeError as err:
                errors.append([f"In procedure {proc.inputString}: {str(err)}",
                    [0, 0], []])
            if proc.return_var:
                warnings.append([f'Procedure {proc.inputString}:'
                    ' return variable not supported', [0, 0], []])
        elif child.type in (lexer.PROCEDURE, lexer.START,
                            lexer.STATE, lexer.FLOATING_LABEL):
            content.append(child)
        elif child.type == lexer.EXPORTED:
            proc.exported = True
        elif child.type == lexer.REFERENCED:
            proc.referenced = True
        else:
            warnings.append([
                    'Unsupported construct in procedure, type: ' +
                    sdl92Parser.tokenNamesMap[child.type] +
                    ' - line ' + str(child.getLine()) +
                    ' - in procedure ' + proc.inputString, [0, 0], []])
    for each in chain(errors, warnings):
        each[2].insert(0, f'PROCEDURE {proc.inputString}')
    return proc, content, errors, warnings


def procedure_returns(root):
    ''' Returns the (optional) variable name and the sort of the return '''
    if len(root.children) == 1:
        return sdl_to_asn1(root.getChild(0).getChild(0).text), None
    else:
        return sdl_to_asn1(root.getChild(1).getChild(0).text),\
               root.getChild(0).text

def check_duplicate_procedures(ctxt, proc, errors=[]):
    ''' Check for duplicates procedure declarations in a given context
        and recursively in contexts above
        If the procedure in the context is declared as referenced,
        then report an error only if the signature is different
        Procedure named "entry" and "exit" are ignored
        '''
    name = proc.inputString.lower()
    if not isinstance(ctxt, ogAST.System) and ctxt.parent != None:
        check_duplicate_procedures(ctxt.parent, proc, errors)
    if isinstance(ctxt, ogAST.AST):
        # If we are at AST top level there are no declarations -> ignore
        return
    if name in ('entry', 'exit'):
        # ignore special entry/exit procedures
        return
    try:
        content = ctxt.content.inner_procedures
    except AttributeError:
        content = []
    for each in chain(content, ctxt.procedures):
        if each.inputString.lower() == name:
            if not each.referenced and not proc.referenced:
                errors.append('Duplicate procedure declaration: {}'
                          .format(name))
            else:
                mismatch = False
                # at least one is referenced -> compare signatures
                left, right = proc.fpar, each.fpar
                if len(left) != len(right):
                    mismatch = True
                    issue = "not the same number of parameters"
                rt1 = proc.return_type and type_name(proc.return_type)
                rt2 = each.return_type and type_name(each.return_type)
                if rt1 != rt2:
                    issue = "inconsistent return types"
                    mismatch = True
                for idx, val in enumerate(left):
                    if(right[idx]['name'].lower() != val['name'].lower()
                     or type_name(right[idx]['type']) != type_name(val['type'])
                     or right[idx]['direction'] != val['direction']):
                        mismatch = True
                        issue = f"parameter {idx+1} inconsistency (name or type)"
                        break
                if mismatch:
                    errors.append(f'Procedure {proc.inputString}: '
                      f'declaration and definition interface mismatch ({issue})')

                if proc.exported != each.exported:
                    # If declared exported, definition must be exported too
                    # Setting the flag here, this will ease code generators
                    proc.exported = each.exported = True

def procedure_post(proc, content, parent=None, context=None):
    ''' Parse the content of a procedure '''
    errors = []
    warnings = []
    # Create a list of all inherited data
    try:
        proc.global_variables = dict(context.variables)
        proc.global_variables.update(context.global_variables)
        proc.global_monitors = dict(context.monitors)
        proc.global_monitors.update(context.global_monitors)
        proc.global_timers = list(context.timers)
        proc.global_timers.extend(list(context.global_timers))
        proc.input_signals = context.input_signals
        proc.output_signals = context.output_signals
        proc.procedures = context.procedures
        proc.operators = dict(context.operators)
    except AttributeError:
        LOG.debug('Procedure context is undefined')
    # Gather the list of states defined in the procedure
    # and create a mapping of transitions to each state
    # (Note, procedures in OG currently do NOT support states)
    # proc.mapping = {name: [] for name in get_state_list(root)}
    inner_proc = []
    for child in content:
        if child.type == lexer.PROCEDURE:
            new_proc, content, err, warn = procedure_pre(child, context=proc)
            inner_proc.append((new_proc, content))
            errors.extend(err)
            warnings.extend(warn)
            # check for duplicate declaration
            dupl_errs = []
            check_duplicate_procedures(context, new_proc, dupl_errs)
            # Add procedure to the context, to make it visible at scope level
            context.procedures.append(new_proc)
            proc.content.inner_procedures.append(new_proc)
            for err_str in dupl_errs:
                errors.append([err_str, [0, 0], []])
                new_proc.errors.append(err_str)
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            proc.content.start, err, warn = start(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(child, parent=None, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.floating_labels.append(lab)
    for new_proc, content in inner_proc:
        # parse content of procedures
        err, warn = procedure_post(new_proc, content, context=proc)
        errors.extend(err)
        warnings.extend(warn)
    for each in proc.terminators:
        # check that RETURN statements type is correct
        if not proc.return_type and each.return_expr:
            msg = f'No return value expected in procedure {proc.inputString}'
            errors.append([msg, [each.pos_x, each.pos_y], []])
            each.errors.append(msg)
        elif proc.return_type and each.return_expr:
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable(debugLine=lineno())
            check_expr.left.exprType = proc.return_type
            check_expr.right = each.return_expr
            try:
                warns = fix_expression_types(check_expr, context)
                w = Assign_Check_Range(check_expr)
                if w is not None:
                    warnings.append([w, [each.pos_x, each.pos_y], []])
                for warn in warns:
                    each.warnings.append(warn)
                    warnings.append([warn, [each.pos_x, each.pos_y], []])
            except (TypeError, AttributeError) as err:
                msg = f"In procedure {proc.inputString}: {str(err)}"
                errors.append([msg,[each.pos_x, each.pos_y], []])
                each.errors.append(msg)
            # Id of fd_expr may have changed (enumerated, choice)
            each.return_expr = check_expr.right
        elif proc.return_type and each.kind == 'return' and not each.return_expr:
            msg = f'Missing return value in procedure {proc.inputString}'
            errors.append([msg, [each.pos_x, each.pos_y], []])
            each.errors.append(msg)
        else:
            continue
    for each in chain(errors, warnings):
        each[2].insert(0, f'PROCEDURE {proc.inputString}')
    return errors, warnings


def procedure(root, parent=None, context=None):
    ''' Parse a procedure - call sequentially the pre- and post- functions
        This function is called by the syntax checker only '''
    proc, content, errors, warnings = procedure_pre(root, parent, context)
    err, warn = procedure_post(proc, content, parent, context)
    errors.extend(err)
    warnings.extend(warn)
    return proc, errors, warnings


def floating_label(root, parent, context):
    ''' Floating label: name and optional transition '''
    errors = []
    warnings = []
    lab = ogAST.Floating_label()
    # Set the location in the model where the label appears
    lab.path = context.path
    lab_x, lab_y = 0, 0
    # Keep track of the number of terminator statements following the label
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.ID:
            lab.inputString = child.text
            lab.line = child.getLine()
            lab.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.CIF:
            # Get symbol coordinates
            lab.pos_x, lab.pos_y, lab.width, lab.height = cif(child)
            lab_x, lab_y = lab.pos_x, lab.pos_y
        elif child.type == lexer.SYMBOLID:
            lab.pos_x = symbolid(child)
        elif child.type == lexer.HYPERLINK:
            lab.hyperlink = child.getChild(0).text[1:-1]
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(child, parent=lab, context=context)
            errors.extend(err)
            warnings.extend(warn)
            lab.transition = trans
        else:
            msg = f'Unsupported construct in floating label: {str(child.type)}'
            warnings.append([msg, [lab_x, lab_y], []])
            lab.warnings.append(msg)
    if not lab.transition:
        msg = f'Floating labels not followed by a transition: {str(lab.inputString)}'
        warnings.append([msg, [lab_x, lab_y], []])
        lab.warnings.append(msg)
    # At the end of the label parsing, get the list of terminators that
    # the transition contains by making a diff with the list at context
    # level (we counted the number of terminators before parsing the item)
    lab.terminators = list(context.terminators[terminators:])
    return lab, errors, warnings


def newtype_gettype(root, ta_ast, context):
    ''' Returns the name of the new type created by a NEWTYPE construction '''
    errors = []
    warnings = []
    newtypename = ""
    if (root.getChild(0).type != lexer.SORT):
        warnings.append("Expected SORT in newtype identifier, got type:"
                        + str(root.type))
        return newtypename, errors, warnings

    newtypename = root.getChild(0).getChild(0).text.capitalize()
    return newtypename, errors, warnings


def get_array_type(newtypename, root):
    ''' Returns the subtype associated to an NEWTYPE ARRAY construction '''
    # root contains two sort names, the indexing one and the element
    indexSortName = root.getChild(0).getChild(0).text
    elementSort = root.getChild(1).getChild(0).text
    typeSortLine = root.getChild(1).getLine()
    typeSortChar = root.getChild(1).getCharPositionInLine()

    # we must look for indexSortName and elementSort in the AST of
    # asn1scc and check if they are valid for this construct
    indexSort = sdl_to_asn1(indexSortName)
    refSort   = sdl_to_asn1(elementSort)

    # Check if indexSort is a numerical type
    # it is not possible to index with enumerated or string in asn1
    # (the type must be equivalent to a SEQUENCE (SIZE ...) OF)
    if not is_numeric(indexSort):
        raise TypeError("Array indexing type must be numerical")

    basicIndex = find_basic_type(indexSort)
    # Constructing ASN.1 AST subtype
    minValue = basicIndex.Min
    maxValue = basicIndex.Max
    newtype = type(str(newtypename), (object,), {
        "Line": typeSortLine,
        "CharPositionInLine": typeSortChar,
        "AddedType": "False",
        "type": type ("SeqOf_type", (object,), {
            "Line": typeSortLine,
            "CharPositionInLine": typeSortChar,
            "kind": "SequenceOfType",
            "Min": minValue,
            "Max": maxValue,
            "type": refSort
        })
    })

    return newtype


def get_struct_children(root):
    ''' Returns the fields of a STRUCT as a dictionary '''
    children = {}
    fieldlist = root.getChild(0)
    fieldname = ""
    typename = ""
    if (fieldlist.type != lexer.FIELDS):
        return children

    for field in fieldlist.getChildren():
        if (field.type == lexer.FIELD):
            fieldname = field.getChild(0).text.lower()
            typename = field.getChild(1).getChild(0).text
            typename = typename.capitalize().replace('_', '-')

            line = field.getChild(0).getLine()
            charpos = field.getChild(0).getCharPositionInLine()

            children[fieldname] = type(str(fieldname), (object,), {
                "Optional": "False", "Line": line,
                "CharPositionInLine": charpos,
                "type": type(str(fieldname + "_type"), (object,), {
                    "Line": line, "CharPositionInLine": charpos,
                    "kind": "ReferenceType", "ReferencedTypeName": typename
                })
            })
    return children


def syntype(root, ta_ast, context):
    ''' Parse a SYNTYPE definition and inject it in ASN1 AST'''
    errors = []
    warnings = []
    newtype = ""
    reftype = ""

    newtypename = root.getChild(0).getChild(0).text.capitalize()
    # reftypename = root.getChild(1).getChild(0).text
    newtype = type(str(newtypename), (object,), {
        "Line": root.getChild(0).getLine(),
        "CharPositionInLine": root.getChild(0).getCharPositionInLine(),
    })
    newtype.type = type(str(newtypename) + "_type", (object,), {
        "Line": root.getChild(1).getLine(),
        "CharPositionInLine": root.getChild(1).getCharPositionInLine(),
        "kind": reftype + "Type"
    })

    #types()[str(newtypename)] = newtype
    LOG.debug("Found new SYNTYPE " + newtypename)
    return errors, warnings


def newtype(root, ta_ast, context):
    ''' Parse a NEWTYPE definition and inject it in ASN1 AST'''
    errors = []
    warnings = []

    # type name gets capitalized with this call:
    newtypename, errors, warnings = newtype_gettype(root, ta_ast, context)
    if (newtypename == ""):
        return errors, warnings

    if len(root.children) < 2:
        errors.append('Use newtype definitions for arrays and records only')
    elif (root.getChild(1).type == lexer.ARRAY):
        try:
            newType = get_array_type(newtypename, root.getChild(1))
            USER_DEFINED_TYPES.update({str(newtypename): newType})
        except TypeError as err:
            errors.append(str(err))
        LOG.debug("Found new ARRAY type " + newtypename)
    elif (root.getChild(1).type == lexer.STRUCT):
        errors.append('Use newtype definitions for arrays only')
        #newType.kind = "SequenceType"
        #newType.Children = get_struct_children(root.getChild(1))
        #types()[str(newtypename)] = newType
        LOG.debug("Found new STRUCT type " + newtypename)
    else:
        warnings.append(
                    'Unsupported type definition in newtype, type: ' +
                    str(root.type))
    if isinstance(context, ogAST.Process):
        context.user_defined_types = USER_DEFINED_TYPES
    return errors, warnings


def synonym(root, ta_ast, context):
    ''' Parse a list of SYNONYMs definition (SDL constants) '''
    errors = []
    warnings = []

    def parse_synonym(syn):
        name, sort, ground = None, None, None
        for child in syn.getChildren():
            if child.type == lexer.ID:
                name = child.text
            elif child.type == lexer.SORT:
                sort = child.getChild(0).text
            elif child.type == lexer.GROUND:
                ground, err, warn = expression(child.getChild(0), context)
                errors.extend(err)
                warnings.extend(warn)
            elif child.type == lexer.EXTERNAL:
                errors.append("External synonyms are not supported")
            else:
                warnings.append(
                    'Unsupported synonym construct' +
                    sdl92Parser.tokenNamesMap[child.type])
        return name, sort, ground

    for child in root.getChildren():
        if child.type == lexer.SYNONYM:
            name, sort, value = parse_synonym(child)

        if name and sort and value:
            nameDash = name.replace('_', '-')
            sortDash = sort.replace('_', '-')

            # The value field will depend on the type..If the constant is a
            # numerical value then we transform it to a number, because it
            # can be used by the parser for range checks
            # Same for booleans and enumerated. But complex types are kept as
            # expressions
            if isinstance(value, (ogAST.PrimOctetStringLiteral,
                                  ogAST.PrimBitStringLiteral)):
                concrete_val = value.numeric_value
            elif is_numeric(value.exprType) or is_enumerated(value.exprType) or is_boolean(value.exprType):
                # value.value is an array of one element
                concrete_val, = value.value
            else:
                concrete_val = value

            DV.SDL_Constants[nameDash] = type (nameDash, (), {
                   "varName" : name,
                   "type": type (f"{name}_type", (), {
                       "AsnFile": None,
                       "Line": 0,
                       "CharPositionInLine": 0,
                       "CName": sort,
                       "AdaName": sort,
                       "HasEncDec": False,
                       "kind": "ReferenceType",
                       "ReferencedTypeName": sortDash
                    }),
                   "value": concrete_val
                })
    return errors, warnings


def text_area_content(root, ta_ast, context):
    ''' Content of a text area: DCL, NEWTYPES, SYNTYPES, SYNONYMS, operators,
        procedures  '''
    errors = []
    warnings = []
    signals, procedures = [], []
    for child in root.getChildren():
        if child.type == lexer.DCL:
            err, warn = dcl(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.MONITOR:
            err, warn = dcl(child, ta_ast, context, monitor=True)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.ERRORSTATES:  # used in observers only
            try:
                for each in child.getChildren():
                    context.errorstates.append(each.text.lower())
                    ta_ast.observer_states.append(each.text.lower())
            except AttributeError:
                errors.append("Error states cannot be declared here")
        elif child.type == lexer.IGNORESTATES:
            try:
                for each in child.getChildren():
                    context.ignorestates.append(each.text.lower())
                    ta_ast.observer_states.append(each.text.lower())
            except AttributeError:
                errors.append("Ignore states cannot be declared here")
        elif child.type == lexer.SUCCESSSTATES:
            try:
                for each in child.getChildren():
                    context.successstates.append(each.text.lower())
                    ta_ast.observer_states.append(each.text.lower())
            except AttributeError:
                errors.append("Success states cannot be declared here")
        elif child.type == lexer.SYNONYM_LIST:
            err, warn = synonym(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.NEWTYPE:
            err, warn = newtype(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.SYNTYPE:
            err, warn = syntype(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.PROCEDURE:
            procedures.append(child)
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            try:
                if context.fpar:
                    errors.append('Duplicate declaration of FPAR section')
                else:
                    context.fpar = params
                    ta_ast.fpar = params
            except AttributeError:
                errors.append('Entity cannot have an FPAR section')
        elif child.type == lexer.RETURNS:
            # When parser called standalone (syntax check) the context is a Process
            # which normally has no "return_type". To avoid an exception we check
            # it before accessing it
            if hasattr(context, "return_type") and context.return_type is not None:
                errors.append('Duplicate "returns" statement')
            try:
                context.return_type, context.return_var =\
                        procedure_returns(child)
            except TypeError as err:
                errors.append(str(err))
            if hasattr(context, "return_var") and context.return_var:
                warnings.append('Procedure return variable not supported')
        elif child.type == lexer.TIMER:
            # Don't lowercase the timer name, keep it as declared
            # otherwise the code generator cannot make the connection with
            # the corresponding functions in C to set/reset the timer.
            # timers = [timer.text.lower() for timer in child.children]
            try:
                timers = [timer.text for timer in child.children]
                context.timers.extend(timers)
                ta_ast.timers = timers
            except AttributeError:
                errors.append('Timers can be defined only inside a process')
        elif child.type == lexer.SIGNAL:
            # Signals can be declared at system level, but that must be parsed
            # AFTER possible "USE Datamodel COMMENT 'asn1_filename';"
            # in order to have the types properly defined
            signals.append(child)
        elif child.type == lexer.USE:
            entities = []
            # USE clauses can contain a CIF comment with the ASN.1 filename
            for each in child.getChildren():
                if each.type == lexer.ASN1:
                    errors.append('There shall be no CIF in text areas')
                elif each.type == lexer.COMMENT:
                    # Comment: better way to specify ASN.1 filename
                    use_cmt, _, _ = end(each)
                    ta_ast.asn1_files.append(use_cmt.inputString)
                else:
                    entities.append(each.text)
            if len(entities) == 1:
                ta_ast.use_clauses.append(entities[0])
            elif len(entities) > 1:
                ta_ast.use_clauses.extend('{}/{}'
                           .format(entities[0], each) for each in entities[1:])

        else:
            warnings.append(
                    'Unsupported construct in text area content, type: ' +
                    sdl92Parser.tokenNamesMap[child.type])
    if ta_ast.asn1_files:
        # Parse ASN.1 files that are referenced in USE clauses
        try:
            set_global_DV(ta_ast.asn1_files)
        except TypeError as err:
            errors.append(str(err))
    for each in procedures:
        # Procedure textual declarations need ASN.1 types
        proc, err, warn = procedure(each, context=context)
        # set the flag to avoid rendering a graphical procedure
        proc.textual_procedure = True
        errors.extend(err)
        warnings.extend(warn)
        try:
            content = context.content.inner_procedures
        except AttributeError:
            # May not be any content in current context (eg System)
            content = []
        check_duplicate_procedures(context, proc, errors)
        # Add procedure to the container (process or procedure) if any
        content.append(proc)
        # Add to context to make it visible at scope level
        context.procedures.append(proc)
        # And add it to the TextArea AST for the text autocompletion
        ta_ast.procedures.append(proc)
    for each in signals:
        # Parse signals now - ASN.1 types should have been set
        sig, err, warn = signal(each)
        errors.extend(err)
        warnings.extend(warn)
        ta_ast.signals.append(sig)
    return errors, warnings


def text_area(root, parent=None, context=None):
    ''' Process a text area (DCL, procedure, operators declarations '''
    errors = []
    warnings = []
    ta = ogAST.TextArea()
    ta.path=context.path
    for child in root.getChildren():
        if child.type == lexer.CIF:
            userTextStartIndex = child.getTokenStopIndex() + 1
            ta.pos_x, ta.pos_y, ta.width, ta.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            ta.pos_x = symbolid(child)
        elif child.type == lexer.TEXTAREA_CONTENT:
            ta.line = child.getLine()
            ta.charPositionInLine = child.getCharPositionInLine()
            # Go update the process-level list of variables
            # (TODO: also ops and procedures)
            err, warn = text_area_content(child, ta, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.ENDTEXT:
            userTextStopIndex = child.getTokenStartIndex() - 1
            string = token_stream(child).toString(userTextStartIndex,
                                                  userTextStopIndex)
            ta.inputString = dedent(string).strip()
        elif child.type == lexer.HYPERLINK:
            ta.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported construct in text area, type: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    clean_errs, clean_warns = [], []
    # some errors and warnings may already have the list structure because
    # they were parsed by a rule that added them (e.g. procedures)
    # in that case we must reuse this structure. otherwise, we add the
    # missing parts
    for err in errors:
        if type(err) == list:
            err[1] = [ta.pos_x or 0, ta.pos_y or 0]
            clean_errs.append(err)
            ta.errors.append(err[0])
        else: # string
            clean_errs.append([err, [ta.pos_x or 0, ta.pos_y or 0], []])
            ta.errors.append(err)
    for warn in warnings:
        if type(warn) == list:
            warn[1] = [ta.pos_x or 0, ta.pos_y or 0]
            clean_warns.append(warn)
            ta.warnings.append(warn[0])
        else: # string
            clean_warns.append([warn, [ta.pos_x or 0, ta.pos_y or 0], []])
            ta.warnings.append(warn)
    return ta, clean_errs, clean_warns


def signal(root):
    ''' SIGNAL definition: name and optional list of types '''
    errors, warnings = [], []
    new_signal = {}
    for child in root.getChildren():
        if child.type == lexer.ID:
            new_signal['name'] = child.text
        elif child.type == lexer.PARAMNAMES:
            try:
                param_name, = [par.text for par in child.getChildren()]
                new_signal['param_name'] = param_name
            except ValueError:
                # Will be raised and reported at PARAMS token
                pass
        elif child.type == lexer.PARAMS:
            try:
                param, = [par.text for par in child.getChildren()]
                new_signal['type'] = sdl_to_asn1(param)
            except ValueError:
                errors.append(new_signal['name'] + ' cannot have more' +
                  ' than one parameter. Check signal declaration.')
            except TypeError as err:
                errors.append(str(err))
        elif child.type == lexer.INTERCEPT:
            # signal foo renames input bar to function1
            # used for observer to intercept signals with the input symbol
            # instead of the continuous signal symbol
            new_signal['renames'] = child.getChild(0)
    if not new_signal:
        # Signal was not parsed properly, report it
        faulty_name = get_input_string(root)[slice(7,-1)]
        errors.append('Signal name "{}" is a reserved keyword'
                       .format(faulty_name))
        new_signal['name'] = faulty_name
    return new_signal, errors, warnings


def single_route(root):
    ''' Route (from id to id with [signal id] '''
    # sig.text can be None if the lexer failed on the token, for example if
    # the signal name is a reserved keyword
    route = {'source': root.getChild(0).text,
             'dest': root.getChild(1).text,
             'signals': [sig.text for sig in root.getChildren()[2:] if
                         sig.text]}
    return route


def signalroute(root, parent=None, context=None):
    ''' Channel/signalroute definition (connections) '''
    # no AST entry for edges - a simple dict is sufficient
    # (name, [route])
    edge = {'routes': []}
    for child in root.getChildren():
        if child.type == lexer.ID:
            edge['name'] = child.text
        elif child.type == lexer.ROUTE:
            edge['routes'].append(single_route(child))
    return edge, [], []


def block_definition(root, parent):
    ''' BLOCK entity definition '''
    errors, warnings = [], []
    block = ogAST.Block()
    block.parent = parent
    parent.blocks.append(block)
    # blocks have signalroutes but since we have systems with a single
    # block and a single process, it is better to set the routes with the
    # same values as the channels from the system-level channels
    # The reason is that some signals may have added to the channels to
    # support RPCs' transitions
    block.signalroutes = parent.channels
    for child in root.getChildren():
        if child.type == lexer.ID:
            block.name = child.text
        elif child.type == lexer.SIGNAL:
            sig, err, warn = signal(child)
            errors.extend(err)
            warnings.extend(warn)
            block.signals.append(sig)
        elif child.type == lexer.CONNECTION:
            block.connections.append({'channel': cnx[0].text,
              'signalroute': cnx[1].text} for cnx in child.getChildren())
        elif child.type == lexer.BLOCK:
            block, err, warn = block_definition(child, parent=block)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.PROCESS:
            proc, err, warn = process_definition(child, parent=block)
            block.processes.append(proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.dataview = types()
            proc.asn1Modules = DV.asn1Modules
            proc.dv = DV
        elif child.type == lexer.SIGNALROUTE:
            sigroute, _, _ = signalroute(child)
            # ignored (see comment above)
            #block.signalroutes.append(sigroute)
        else:
            warnings.append('Unsupported block child type: ' +
                str(child.type))
    return block, errors, warnings


def system_definition(root, parent):
    ''' SYSTEM part - contains blocks, procedures and channels '''
    errors, warnings = [], []
    system = ogAST.System()
    system.path = []
    # Store the name of the file where the system is defined
    system.filename = node_filename(root)
    system.ast = parent
    #system.parent = parent
    asn1_files = []
    signals, procedures, blocks = [], [], []
    for child in root.getChildren():
        if child.type == lexer.ID:
            system.name = child.text
        elif child.type == lexer.SIGNAL:
            signals.append(child)
        elif child.type == lexer.PROCEDURE:
            procedures.append(child)
        elif child.type == lexer.CHANNEL:
            channel, _, _ = signalroute(child)
            system.channels.append(channel)
        elif child.type == lexer.BLOCK:
            blocks.append(child)
        elif child.type == lexer.TEXTAREA:
            # Text zone where signals can be declared
            textarea, err, warn = text_area(child, context=system)
            system.signals.extend(textarea.signals)
            if textarea.fpar:
                errors.append('FPAR cannot be declared at system level')
            if textarea.timers:
                errors.append('Timers shall be declared only in a process')
            # Update list of ASN.1 files - if any
            if not asn1_files:
                asn1_files = textarea.asn1_files
            elif textarea.asn1_files:
                errors.append('ASN.1 Files must be set in a single text area')
            errors.extend(err)
            warnings.extend(warn)
            system.text_areas.append(textarea)
        else:
            warnings.append('Unsupported construct in system: ' +
                    str(child.type))
        if asn1_files:
            system.ast.asn1Modules = DV.asn1Modules
            system.ast.asn1_filenames = []
            for each in asn1_files:
                # check presence of ASN.1 file and store absolute path
                # so that further parsing is insensitive to os.chdir calls
                if not os.path.isfile(each):
                    errors.append("File not found: " + each)
                else:
                    system.ast.asn1_filenames.append(os.path.abspath(each))
            #system.ast.asn1_filenames = asn1_files
    for each in signals:
        sig, err, warn = signal(each)
        errors.extend(err)
        warnings.extend(warn)
        # Ignore duplicate signal definitions when they are defined at
        # system level (only taste can do that)
        for sys_sig in system.signals:
            if sys_sig['name'].lower() == sig['name'].lower():
                break
        else:
            system.signals.append(sig)


    # if there are no channels defined or no route
    # add an empty one as a placeholder to add signals
    from_env_route = {'source' : 'env', 'dest': system.name, 'signals': []}
    to_env_route = {'source' : system.name, 'dest': 'env', 'signals': []}
    has_from_env, has_to_env = False, False
    for each in system.channels:
        for route in each['routes']:
            if route['source'] == 'env':
                has_from_env = True
            elif route['dest'] == 'env':
                has_to_env = True
        if not has_from_env:
            each['routes'].append(from_env_route)
        if not has_to_env:
            each['routes'].append(to_env_route)

    if not system.channels:
        system.channels.append({'name': 'c', 'routes':[from_env_route,
            to_env_route]})

    # in observers, we may have renamed signals
    # add them to signal routes
    for each in system.signals:
        if each['renames'] is not None:
            #  Parse the expression, so that if the intercepted signal is
            #  an output, it is also added to the route towards env
            ioExpr = parse_io_expression(each['renames'], context=None)
            isOut = ioExpr['kind'] == 'output'
            for channel in system.channels:
                for route in channel['routes']:
                    if route['dest'].lower() != "env" or isOut:
                        if each['name'] not in route['signals']:
                            route['signals'].append(each['name'])


    exported_procedures = []
    for each in procedures:
        proc, err, warn = procedure(
                each, parent=None, context=system)
        # Procedure defined at system level are only textual
        proc.textual_procedure = True
        errors.extend(err)
        warnings.extend(warn)
        system.procedures.append(proc)
    for proc in system.procedures:
        # list contains also procedures defined in text ares
        # form a list of exported procedures to update channels and routes
        if proc.exported:
            exported_procedures.append(proc.inputString)

    # Add signals for transitions of RPC visible to blocks/processes
    # Add them also to the channels of the system
    for proc in exported_procedures:
        system.signals.append({'name' : proc})
        for channel in system.channels:
            if 'routes' not in channel:
                channel['routes'] = [{'dest': system.name, 'signals': []}]
            for route in channel['routes']:
                if route['dest'].lower() != "env":
                    if proc not in route['signals']:
                        route['signals'].append(proc)

    for each in blocks:
        block, err, warn = block_definition(each, parent=system)
        errors.extend(err)
        warnings.extend(warn)

    # If there are exported procedures update signalroutes of the blocks
    if exported_procedures:
        for block in system.blocks:
            block.signalroutes = system.channels

    return system, errors, warnings


def process_definition(root, parent=None, context=None):
    ''' Process definition analysis '''
    errors, warnings, perr, pwarn = [], [], [], []
    process = ogAST.Process()
    process.filename = node_filename(root)
    process.parent = parent
    proc_x, proc_y = 0, 0
    inner_proc = []

    # first look for all text areas to find NEWTYPE declarations
    USER_DEFINED_TYPES = CHOICE_SELECTORS.copy()
    process.user_defined_types = USER_DEFINED_TYPES
    tas = (x for x in root.getChildren() if x.type == lexer.TEXTAREA)
    for child in tas:
        content = (x for x in child.getChildren()
                   if x.type == lexer.TEXTAREA_CONTENT)
        for each in content:
            newtypes = (x for x in each.getChildren()
                        if x.type == lexer.NEWTYPE)
            for sort in newtypes:
                # ignore errors, warnings here
                # we just need the types to be visible
                _, _ = newtype(sort, None, context)

    # then parse procedures, so that their signature is set in the ast
    procedures = (x for x in root.getChildren() if x.type == lexer.PROCEDURE)
    for child in procedures:
        proc, content, err, warn = procedure_pre(
                child, parent=None, context=process)
        inner_proc.append((proc, content))
        errors.extend(err)
        warnings.extend(warn)
        # check for duplicate declaration
        dupl_errs = []
        check_duplicate_procedures(process, proc, dupl_errs)
        for err_str in dupl_errs:
            errors.append([err_str, [proc.pos_x, proc.pos_y], []])
            proc.errors.append(err_str)
        # Add it at process level so that it is in the scope
        process.content.inner_procedures.append(proc)
        process.procedures.append(proc)

    state_list = get_state_list(root)
    # Prepare the transition/state mapping
    process.mapping    = {name: [] for name in state_list}
    process.cs_mapping = {name: [] for name in state_list}
    process.connect_mapping = {name: [] for name in state_list}
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            process.pos_x, process.pos_y, process.width, process.height =\
                    cif(child)
            proc_x, proc_y = process.pos_x, process.pos_y
        elif child.type == lexer.SYMBOLID:
            process.pos_x = symbolid(child)
        elif child.type == lexer.ID:
            # Get process name
            process.processName = child.text
            process.path = [f'PROCESS {process.processName}']
            try:
                # Retrieve process interface (PI/RI)
                asyncI, procedures, err = get_interfaces(parent, child.text)
                process.input_signals.extend([sig for sig in asyncI
                                             if sig['direction'] == 'in'])
                process.output_signals.extend([sig for sig in asyncI
                                              if sig['direction'] == 'out'])
                process.procedures.extend(procedures)
                perr.extend(err)
            except AttributeError as exc:
                # No interface because process is defined standalone
                LOG.debug('Discarding process ' + child.text + ' ' + str(exc))
            except TypeError as exc:
                perr.append(str(exc))
            clean_err = []
            for e in perr:
                clean_err.append([e, [proc_x, proc_y], []])
                process.errors.append(e)
        elif child.type == lexer.TEXTAREA:
            # Text zone where variables and operators are declared
            textarea, err, warn = text_area(child, context=process)
            if textarea.signals:
                msg = 'Signals shall not be declared in a process'
                errors.append([msg, [textarea.pos_x, textarea.pos_y], []])
                textarea.errors.append(msg)
            errors.extend(err)
            warnings.extend(warn)
            process.content.textAreas.append(textarea)
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            process.content.start, err, warn = start(child, context=process)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.STATE:
            # STATE - fills up the 'mapping' structures.
            statedef, err, warn = state(child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.states.append(statedef)
        elif child.type == lexer.NUMBER_OF_INSTANCES:
            # Number of instances - discarded (working on a single process)
            pass
        elif child.type == lexer.PFPAR:
            # Process formal parameters
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            process.fpar = params
        elif child.type == lexer.PROCEDURE:
            continue
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.floating_labels.append(lab)
        elif child.type in (lexer.COMPOSITE_STATE, lexer.STATE_AGGREGATION):
            comp, err, warn = composite_state(child,
                                              parent=None,
                                              context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.composite_states.append(comp)
        elif child.type == lexer.REFERENCED:
            process.referenced = True
        elif child.type == lexer.TYPE:
            process.process_type = True
        elif child.type == lexer.TYPE_INSTANCE:
            # PROCESS Toto:ParentType;
            process.instance_of_name = child.children[0].text
        elif child.type == lexer.COMMENT:
            process.comment, _, _ = end(child)
        else:
            warnings.append(['Unsupported process definition child: ' +
                             sdl92Parser.tokenNamesMap[child.type] +
                            ' - line ' + str(child.getLine()),
                            [proc_x, proc_y], []])
    for proc, content in inner_proc:
        err, warn = procedure_post(proc, content, context=process)
        errors.extend(err)
        warnings.extend(warn)
    # once all text areas have been parsed, we must parse the aliases
    # (e.g. dcl variable type renames field.foo.bar). this could not be done
    # before all regular DCL/Monitor variables were parsed.
    for (alias_name, alias_sort, alias_ast, ta_ast) in process._aliases_ast:
        expr, err, warn = expression(alias_ast, context=process)
        for each in err:
            msg =f"In alias '{alias_name}': {each}"
            errors.append([msg, [ta_ast.pos_x or 0, ta_ast.pos_y or 0], []])
            ta_ast.errors.append(msg)
        for each in warn:
            msg =f"In alias '{alias_name}': {each}"
            warnings.append([msg, [ta_ast.pos_x or 0, ta_ast.pos_y or 0], []])
            ta_ast.warnings.append(msg)
        t1 = type_name(alias_sort)
        t2 = type_name(expr.exprType)
        if t1 != t2:
            msg = f"In alias '{alias_name}': type mismatch ({t1} vs {t2})"
            errors.append([msg,[ta_ast.pos_x or 0, ta_ast.pos_y or 0], []])
            ta_ast.errors.append(msg)
        else:
            # alias_name is already in lowercase
            process.aliases[alias_name] = (alias_sort, expr)

    # Verify that special states for observers are defined:
    for each in chain(process.errorstates,
                      process.ignorestates,
                      process.successstates):
        if each not in (st.lower() for st in state_list):
            # retrieve the text area that contained the declaration
            # to get the coordinates for error localization
            for ta_ast in process.content.textAreas:
                if each in ta_ast.observer_states:
                    msg = f"Observer state {each} is not defined"
                    errors.append([msg, [ta_ast.pos_x, ta_ast.pos_y], []])
                    ta_ast.errors.append(msg)
                    break

    if not process.referenced and not process.instance_of_name \
                              and (not process.content.start or
                                   not process.content.start.terminators):
        # detect missing START transition
        msg = f'Mandatory START transition is missing in process {process.processName}'
        errors.append([msg, [process.pos_x, process.pos_y], []])
        process.errors.append(msg)

    # Post-processing: check that all RETURNS of composite states have a
    # corresponding CONNECT in the outer state
    context=process
    for each in context.content.states:
        if each.composite:
            for exitpt in each.composite.state_exitpoints:
                if exitpt not in context.connect_mapping[each.composite.statename]:
                    msg = (f'State "{each.composite.statename}":'
                           f' missing CONNECT for exitpoint "{exitpt}"')
                    errors.append([msg, [each.pos_x, each.pos_y], []])

    for each in chain(errors, warnings):
        try:
            each[2].insert(0, 'PROCESS {}'.format(process.processName))
        except AttributeError as err:
            LOG.error('Internal error - please report "{}" - "{}"'.format(
                str(each), str(err)))
    errors.extend(perr)
    process.DV = DV
    return process, errors, warnings


def continuous_signal(root, parent, context):
    ''' Parse a PROVIDED clause in a continuous signal '''
    i = ogAST.ContinuousSignal()
    i.path = context.path
    dec = ogAST.Decision()
    ans = ogAST.Answer()
    warnings, errors = [], []
    # Flag the continuous signal if we are in an observer (model checking)
    # (useful to render the symbol a bit differently)
    if 'Observer-State-Kind' in types().keys():
        i.observer = True
    # Keep track of the number of terminator statements in the transition
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    dec.question, exp_err, exp_warn = expression(root.getChild(0), context)
    dec.inputString = dec.question.inputString
    dec.line = dec.question.line
    dec.charPositionInLine = dec.question.charPositionInLine
    dec.kind = 'question'
    ans.inputString = 'true'
    constant_expr = ogAST.PrimBoolean()
    constant_expr.value = ['true']
    constant_expr.exprType = BOOLEAN
    ans.answers = [{'kind': 'constant', 'content': (ogAST.ExprEq, constant_expr)}]
    dec.answers = [ans]
    i.trigger = dec
    i.inputString = dec.inputString
    for child in root.children[1:]:
        if child.type == lexer.CIF:
            # Get symbol coordinates
            i.pos_x, i.pos_y, i.width, i.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            i.pos_x = symbolid(child)
        elif child.type == lexer.INT:
            # Priority
            i.priority = int(child.text)
            i.inputString += f';\npriority {get_input_string(child)}'
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(child, parent=i, context=context)
            errors.extend(err)
            warnings.extend(warn)
            i.transition = trans
            ans.transition = trans
            # Associate a reference to the transition to the list of inputs
            # The reference is an index to process.transitions table
            context.transitions.append(trans)
            i.transition_id = len(context.transitions) - 1
        elif child.type == lexer.COMMENT:
            i.comment, _, _ = end(child)
            dec.comment = i.comment
        elif child.type == lexer.HYPERLINK:
            i.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == 0:
            # Syntax error caught by the parser, no need to report again
            pass
        else:
            warnings.append('Unsupported INPUT child type: {}'
                           .format(child.type))
    # Report errors in the expression with symbol coordinates
    errors.extend([[e, [i.pos_x or 0, i.pos_y or 0], []] for e in exp_err])
    warnings.extend([[w, [i.pos_x or 0, i.pos_y or 0], []] for w in exp_warn])
    for e in errors:
        i.errors.append(e[0])
    for w in warnings:
        i.warnings.append(w[0])
    # At the end of the input parsing, get the list of terminators that
    # follow the input transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the input)
    i.terminators = list(context.terminators[terminators:])
    return i, errors, warnings


def input_part(root, parent, context):
    ''' Parse an INPUT - set of TASTE provided interfaces '''
    # parent is a State
    i = ogAST.Input()
    i.path = context.path
    cs = None
    warnings, errors = [], []
    # Keep track of the number of terminator statements follow the input
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            i.pos_x, i.pos_y, i.width, i.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            i.pos_x = symbolid(child)
        elif child.type == lexer.INPUTLIST:
            i.inputString = get_input_string(child)
            i.line = child.getLine()
            i.charPositionInLine = child.getCharPositionInLine()
            # get input name and parameters (support for one parameter only)
            sig_param_type, user_param_type = None, None
            inputnames = [c for c in child.getChildren()
                                                  if c.type != lexer.PARAMS]
            for inputname in inputnames:
                if inputname.text is None:
                    # syntax error (CommonErrorNode) - already caught
                    continue
                for inp_sig in context.input_signals:
                    # process RENAMES clause at signal level
                    if inp_sig['name'].lower() == inputname.text.lower():
                        i.inputlist.append(inp_sig['name'])
                        sig_param_type = inp_sig.get('type')
                        if 'renames' in inp_sig and inp_sig['renames'] is not None:
                            # renames are used in observers only
                            # create a continuous signal
                            cs = ogAST.ContinuousSignal()
                            cs.path = context.path
                            dec = ogAST.Decision()
                            ans = ogAST.Answer()
                            # inp_sig['renames'] is the AST entry
                            # (e.g. "input foo to bar")
                            # extract all parts:
                            io_expr = parse_io_expression(inp_sig['renames'], context)
                            if io_expr['paramName'] is not None:
                                # io expressions cannot have a parameter when they rename a signal
                                # the parameter can be specified in the INPUT part only
                                errors.append('Renamed expression for signals cannot have a named parameter in declaration')
                            # Check here is there is a parameter to the input
                            # If so, add it to the io expression so that when
                            # it is processed, an implicit variable will be
                            # declared for it
                            inputparams = [c.getChildren() for c in child.getChildren()
                                                     if c.type == lexer.PARAMS]
                            if len(inputparams) == 1 and len(inputparams[0]) == 1:
                                user_param, = inputparams[0]
                                io_expr['paramName'] = user_param.text
                            dec.question, errs, warns = io_expression(inp_sig['renames'], context, io_expr)
                            # possible errors: if user declared a variable for the parameter
                            # in observers, variables are always implicit, as they are
                            # in fact a field in the event structure
                            errors.extend(errs)
                            warnings.extend(warns)
                            #dec.inputString = dec.question.inputString
                            dec.inputString = i.inputString
                            dec.line = i.line
                            dec.charPositionInLine = i.charPositionInLine
                            dec.kind = 'question'
                            ans.inputString = 'true'
                            constant_expr = ogAST.PrimBoolean()
                            constant_expr.value = ['true']
                            constant_expr.exprType = BOOLEAN
                            ans.answers = [{'kind': 'constant',
                                            'content': (ogAST.ExprEq, constant_expr)}]
                            dec.answers = [ans]
                            cs.trigger = dec
                            cs.inputString = dec.question.inputString
                            parent.continuous_signals.append(cs)
                            # must also be added to mapping at context level
                            # (see PROVIDED clause for details)
                            for statename in parent.statelist:
                                existing = context.cs_mapping.get(statename.lower(), [])
                                for each in existing:
                                    if ''.join(each.inputString.lower().split()) == \
                                            ''.join(cs.inputString.lower().split()):
                                        errors.append('Trigger for observer already defined '
                                            'below state "{}"'.format(statename.lower()))
                                        break
                                else:
                                    context.cs_mapping[statename.lower()].append(cs)
                        break
                else:
                    for timer in chain(context.timers, context.global_timers):
                        if timer.lower() == inputname.text.lower():
                            i.inputlist.append(timer.lower())
                            break
                    else:
                        errors.append('Input signal or timer not declared: '
                            + inputname.toString() +
                            ' (line ' + str(i.line) + ')')
            if len(inputnames) > 1 and sig_param_type is not None:
                errors.append('Inputs in a list shall not expect parameters')

            # Parse all parameters (then check that there is only one)
            inputparams = [c.getChildren() for c in child.getChildren()
                                                     if c.type == lexer.PARAMS]
            if len(inputparams) > 1:
                # user entered e.g. INPUT a(x), b(y) instead of INPUT a,b
                errors.append('Only one input can have a parameter')
            elif len(inputparams) == 1 and sig_param_type is not None and \
                    len(inputparams[0]) == 1:
                user_param, = inputparams[0]
                try:
                    user_param_type = find_variable_type(user_param.text,
                                                         context)
                    try:
                        warnings.extend(compare_types(sig_param_type,
                                                      user_param_type))
                    except TypeError as err:
                        errors.append('Parameter type does not match with '
                                      'signal declaration (expecting '
                                      'a variable of type ' +
                                      sig_param_type.ReferencedTypeName + ') -'
                                      + str(err))
                    else:
                        # Store parameter only if everything is OK
                        i.parameters = [user_param.text.lower()]
                except AttributeError as err:
                    errors.append(str(err))
            elif inputparams or sig_param_type:
                errors.append('Wrong number of parameters or type mismatch')

            # Report errors with symbol coordinates
            errors = [[e, [i.pos_x or 0, i.pos_y or 0], []] for e in errors]
            warnings = [[w, [i.pos_x or 0, i.pos_y or 0], []]
                         for w in warnings]
            for e in errors:
                i.errors.append(e[0])
            for w in warnings:
                i.warnings.append(w[0])
        elif child.type == lexer.ASTERISK:
            # Asterisk means: all inputs not processed explicitly
            # Here we do not set the input list - it is set after
            # all other inputs are processed (see state function)
            i.inputString = get_input_string(child)
            i.line = child.getLine()
            i.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.PROVIDED:
            warnings.append('"PROVIDED" expressions not supported')
            i.provided = 'Provided'
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(child, parent=i, context=context)
            errors.extend(err)
            warnings.extend(warn)
            i.transition = trans
            # Associate a reference to the transition to the list of inputs
            # The reference is an index to process.transitions table
            context.transitions.append(trans)
            i.transition_id = len(context.transitions) - 1
            if cs:
                cs.transition = trans
                cs.transition_id = i.transition_id
        elif child.type == lexer.COMMENT:
            i.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            i.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == 0:
            # Syntax error caught by the parser, no need to report again
            pass
        else:
            warnings.append('Unsupported INPUT child type: {}'
                            .format(child.type))
    # At the end of the input parsing, get the list of terminators that
    # follow the input transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the input)
    i.terminators = list(context.terminators[terminators:])
    if cs:
        cs.terminators = i.terminators
        cs.comment = i.comment
        dec.comment = i.comment
        cs.artificial = True # needed for graphical rendering
        i.replaced_with_continuous_signal = True
        # Store the parsed input too, for backends that don't support CS
        cs.observer_input = i

    return i, errors, warnings


def state(root, parent, context):
    '''
        Parse a STATE.
        "parent" is used to compute absolute coordinates
        "context" is the AST used to store global data (process/procedure)
    '''
    errors, warnings, sterr, stwarn = [], [], [], []
    state_def = ogAST.State()
    state_def.path = context.path
    asterisk_state = False
    asterisk_input = None
    st_x, st_y = 0, 0
    via_stop, inst_stop = None, None
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            (state_def.pos_x, state_def.pos_y,
            state_def.width, state_def.height) = cif(child)
            st_x, st_y = state_def.pos_x, state_def.pos_y
        elif child.type == lexer.SYMBOLID:
            state_def.pos_x = symbolid(child)
            st_x = state_def.pos_x
        elif child.type == lexer.ID:
            # a single ID is only for state instances
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            state_def.statelist = [state_def.inputString]
            inst_stop = child.getTokenStopIndex()
            via_stop = inst_stop # in case there is also a via clause
        elif child.type == lexer.TYPE_INSTANCE:
            #  Extract the complete string "state: instance"
            start = inst_stop
            stop = child.getTokenStopIndex()
            state_def.inputString = token_stream(root).toString(start, stop)
            state_def.instance_of = child.getChild(0).toString()
        elif child.type == lexer.STATELIST:
            # State name(state_def)
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            for statename in child.getChildren():
                state_def.statelist.append(statename.toString())
            via_stop = child.getTokenStopIndex()
        elif child.type == lexer.ASTERISK:
            asterisk_state = True
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            exceptions = [c.toString().lower() for c in child.getChildren()]
            for st in context.mapping:
                if st not in exceptions + ['START']:
                    state_def.statelist.append(st)
        elif child.type == lexer.INPUT:
            # A transition triggered by an INPUT
            inp, err, warn = \
                    input_part(child, parent=state_def, context=context)
            errors.extend(err)
            warnings.extend(warn)
            def gather_inputlist(state_ast):
                ''' List all the inputs consumed by a given composite state
                in any substate - used to check that an input consumed at level
                N is not already consumed at N-1, causing conflicts '''
                res = []
                for lists in (inps for inps in state_ast.mapping.values()
                              if not isinstance(inps, int)):
                    res.extend(li for i in lists for li in i.inputlist)
                subinputs = map(gather_inputlist, state_ast.composite_states)
                for each in subinputs:
                    res.extend(each)
                return res
            for comp in context.composite_states:
                # if the current state is a composite state, check that none of
                # the inputs from the list is already consumed in a substate
                if any(st.lower() == comp.statename.lower()
                        for st in state_def.statelist):
                    subinputs = [res.lower() for res in gather_inputlist(comp)]
                    for each in inp.inputlist:
                        if each.lower() in subinputs:
                            sterr.append('Input "{}" is already consumed '
                                         'in substate "{}"'
                                         .format(each, comp.statename.lower()))
            try:
                # Use the statelist unless the state is an instance
                if not state_def.instance_of:
                    statelist = state_def.statelist
                else:
                    statelist = [state_def.instance_of]
                for statename in statelist:
                    context.mapping[statename.lower()].append(inp)
            except KeyError as err:
                # missing state definition is caught at other places, no
                # need to report here
                pass
                #stwarn.append(f'State definition missing - {str(err)}')
            state_def.inputs.append(inp)
            if inp.inputString.strip() == '*':
                asterisk_input = inp
        elif child.type == lexer.CONNECT:
            comp_states = (comp.statename for comp in context.composite_states)
            if asterisk_state or len(state_def.statelist) != 1 \
                    or state_def.statelist[0].lower() not in comp_states:
                sterr.append('State {} is not a composite state and cannot '
                             'be followed by a connect statement'
                             .format(state_def.statelist[0]))
            conn_part, err, warn = connect_part(child, state_def, context)
            state_def.connects.append(conn_part)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == lexer.COMMENT:
            state_def.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            state_def.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == lexer.PROVIDED:
            # Continuous signal
            provided_part, err, warn = continuous_signal(child, state_def,
                                                         context)
            state_def.continuous_signals.append(provided_part)
            # Add the continuous signal to a mapping at context level,
            # useful for code generation. Also check for duplicates.
            for statename in state_def.statelist:
                existing = context.cs_mapping.get(statename.lower(), [])
                for each in existing:
                   if ''.join(each.inputString.lower().split()) == \
                           ''.join(provided_part.inputString.lower().split()):
                #if provided_part in \
                #        context.cs_mapping.get(statename.lower(), []):
                      sterr.append('Continuous signal is defined more than once '
                                  'below state "{}"'.format(statename.lower()))
                else:
                    context.cs_mapping[statename.lower()].append(provided_part)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == lexer.VIA:
            # case of a state to be merged with a NEXTSTATE having a via clause
            # in the via field we keep "state via entrypoint"
            start = via_stop
            stop = child.getTokenStopIndex()
            state_def.via = token_stream(root).toString(start, stop)
        elif child.type == 0:
            # Parser error, already caught
            pass
        else:
            stwarn.append('Unsupported STATE definition child type: ' +
                            sdl92Parser.tokenNamesMap[child.type])
    # post-processing: if state is followed by an ASTERISK input, the exact
    # list of inputs can be updated. Possible only if context has signals
    if context.input_signals and asterisk_input:
        explicit_inputs = set()
        for inp in state_def.inputs:
            explicit_inputs |= set(inp.inputlist)
        # Keep only inputs that are not explicitly defined
        input_signals = (sig['name'] for sig in context.input_signals)
        remaining_inputs = set(input_signals) - explicit_inputs
        asterisk_input.inputlist = list(remaining_inputs)
    # post-processing: check for duplicate inputs
    if not state_def.instance_of:
        statelist = state_def.statelist
    else:
        statelist = [state_def.instance_of]
    for statename in statelist:
        inputs = context.mapping.get(statename.lower(), [])
        dupl = set()
        for a, b in combinations(inputs, 2):
            duplicates = set(a.inputlist).intersection(set(b.inputlist))
            #print(a.inputlist, " vs ", b.inputlist, " -> ", duplicates)

            if a.inputString.strip() != "*" and b.inputString.strip() != "*":
                # Duplicates in non ASTERISK inputs
                dupl.update(duplicates)
                continue

            if a.inputString.strip() == "*" and b.inputString.strip() == "*":
                dupl.add("*")
                continue

            for each in (a, b):
                if each.inputString.strip() == "*":
                    # update the input list of the asterisk input
                    for d in duplicates:
                        each.inputlist.remove(d)
        for each in dupl:
            sterr.append('Input "{}" is defined more '
                         'than once for state "{}"'
                         .format(each, statename.lower()))

    # post-processing: if state is composite, add link to the content
    if len(state_def.statelist) == 1 and not asterisk_state:
        for each in context.composite_states:
            if each.statename.lower() == state_def.statelist[0].lower():
                state_def.composite = each
    for each in sterr:
        errors.append([each, [st_x, st_y], []])
        state_def.errors.append(each)
    for each in stwarn:
        warnings.append([each, [st_x, st_y], []])
        state_def.warnings.append(each)
    return state_def, errors, warnings


def connect_part(root, parent, context):
    ''' Connection of a nested state exit point with a transition
        Very similar to INPUT '''
    errors, warnings = [], []
    conn = ogAST.Connect()
    conn.path = context.path
    try:
        statename = parent.statelist[0].lower()
    except AttributeError:
        # Ignore missing parent/statelist to allow local syntax check
        statename = ''
    id_token = []
    # Keep track of the number of terminator statements following the input
    # useful if we want to render graphs from the SDL model
    terms = len(context.terminators)
    # Retrieve composite state
    try:
        nested, = (comp for comp in context.composite_states
                   if comp.statename.lower() == statename.lower())
    except ValueError:
        # Ignore unexisting state - to allow local syntax check
        nested = ogAST.CompositeState()

    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            conn.pos_x, conn.pos_y, conn.width, conn.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            conn.pos_x = symbolid(child)
        elif child.type == lexer.ID:
            id_token.append(child)
            conn.connect_list.append(child.toString().lower())
        elif child.type == lexer.ASTERISK:
            id_token.append(child)
            conn.connect_list = nested.state_exitpoints
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(child, parent=conn, context=context)
            errors.extend(err)
            warnings.extend(warn)
            context.transitions.append(trans)
            trans_id = len(context.transitions) - 1
            conn.transition_id = trans_id
            conn.transition = trans
        elif child.type == lexer.HYPERLINK:
            conn.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == lexer.COMMENT:
            conn.comment, _, _ = end(child)
        else:
            warnings.append('Unsupported CONNECT PART child type: ' +
                            sdl92Parser.tokenNamesMap[child.type])
    if not conn.connect_list:
        conn.connect_list.append('')
    if not id_token:
        conn.inputString = ''
        conn.line = root.getLine()
        conn.charPositionInLine = root.getCharPositionInLine()
    else:
        conn.line = id_token[0].getLine()
        conn.charPositionInLine = id_token[0].getCharPositionInLine()
        conn.inputString = token_stream(id_token[0]).toString(
                                        id_token[0].getTokenStartIndex(),
                                        id_token[-1].getTokenStopIndex())
    for exitp in conn.connect_list:
        if exitp != '' and not exitp in nested.state_exitpoints:
            msg = f'Exit point {exitp} not defined in state {statename}'
            errors.append([msg, [conn.pos_x or 0, conn.pos_y or 0], []])
            conn.errors.append(msg)
        def check_terminators(comp):
            terminators = [term for term in comp.terminators
                           if term.kind == 'return'
                           and term.inputString.lower() == exitp]
            if not terminators:
                msg = f'No {exitp} return statement in nested state {comp.statename.lower()}'
                errors.append([msg, [conn.pos_x or 0, conn.pos_y or 0], []])
                conn.errors.append(msg)
            return terminators

        if not isinstance(nested, ogAST.StateAggregation):
            terminators = check_terminators(nested)
        else:
            # State aggregation: we must check that all parallel states
            # contain indeed a return statement of the given name
            def siblings(aggregate):
                for comp in aggregate.composite_states:
                    if not isinstance(comp, ogAST.StateAggregation):
                        yield comp
                    else:
                        for each in siblings(comp()):
                            yield each
            all_terms = map(check_terminators, siblings(nested))
            terminators = []
            for each in all_terms:
                terminators.extend(each)
        for each in terminators:
            # Set next transition, exact id to be found in postprocessing
            each.next_trans = trans
    # Find duplicate CONNECT statements
    if statename:
        existing = context.connect_mapping.get(statename, [])
        for each in existing:
            if each.lower() in (a.lower() for a in conn.connect_list):
                msg = (f'CONNECT: trigger {each} already specified '
                        f'for state {statename}')
                errors.append([msg, [conn.pos_x or 0, conn.pos_y or 0], []])
                break
        else:
            context.connect_mapping[statename].extend(conn.connect_list)

    # Set list of terminators
    conn.terminators = list(context.terminators[terms:])
    return conn, errors, warnings


def cif(root):
    ''' Return the CIF coordinates '''
    result = []
    neg = False
    for child in root.getChildren():
        if child.type == lexer.DASH:
            neg = True
        else:
            val = int(child.toString())
            val = -val if neg else val
            result.append(val)
            neg = False
    return result

def symbolid(root):
    ''' Return the symbol ID, allowing to retrieve a symbol already present
    on the scene after re-parsing the model for semantic checks '''
    return root.getChild(0).toString()

def start(root, parent=None, context=None):
    ''' Parse the START transition '''
    errors = []
    warnings = []
    if isinstance(context, ogAST.Procedure):
        s = ogAST.Procedure_start()
    elif isinstance(context, ogAST.CompositeState):
        s = ogAST.CompositeState_start()
    else:
        s = ogAST.Start()
    s.path = context.path
    # Keep track of the number of terminator statements following the start
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            s.pos_x, s.pos_y, s.width, s.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            s.pos_x = symbolid(child)
        elif child.type == lexer.ID:
            # in nested states, START can be followed by the entry point name
            s.inputString = child.toString().lower() + '_START'
        elif child.type == lexer.TRANSITION:
            s.transition, err, warn = transition(
                                        child, parent=s, context=context)
            errors.extend(err)
            warnings.extend(warn)
            context.transitions.append(s.transition)
            context.mapping[s.inputString or 'START'] = \
                                                   len(context.transitions) - 1
        elif child.type == lexer.COMMENT:
            s.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            s.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append(['START unsupported child type: ' +
                    str(child.type), [s.pos_x, s.pos_y], []])
    # At the end of the START parsing, get the list of terminators that
    # follow the START transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the START)
    s.terminators = list(context.terminators[terminators:])
    return s, errors, warnings


def end(root, parent=None, context=None):
    ''' Parse a comment symbol '''
    c = ogAST.Comment()
    c.line = root.getLine()
    c.charPositionInLine = root.getCharPositionInLine()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            c.pos_x, c.pos_y, c.width, c.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            c.pos_x = symbolid(child)
        elif child.type == lexer.STRING:
            c.inputString = child.toString()[1:-1]
        elif child.type == lexer.HYPERLINK:
            c.hyperlink = child.getChild(0).toString()[1:-1]
    return c, [], []


def procedure_call(root: antlr3.tree.CommonTree,
                  parent,
                  context: ogAST.Process):
    ''' Parse a PROCEDURE CALL '''
    out_ast = ogAST.ProcedureCall()
    out_ast.path = context.path
    _, err, warn = output(root, parent, out_ast, context)
    # Check if the procedure exists, and assign an exprType to
    # the procedure call in case it has a Return statement
    call_name = out_ast.output[0]['outputName'].lower()
    for each in context.procedures:
        if each.inputString.lower() == call_name:
            out_ast.exprType = each.return_type
            # Take the right casing from procedure declaration - always useful
            # for case-sensitive backends like C code generators
            out_ast.output[0]['outputName'] = each.inputString
            break
    else:
        # Procedure not found, perhaps a special operator
        # in principle internal operators are not invoked with the "call"
        # keyword, they can be called directly. However if they have no
        # parameter, they can be confused with a variable and would not be
        # resolved properly without the explicit "call" unless it uses
        # empty parenthesis : funcWithNoParam().
        # here we only try to get the return type. if check_call returns
        # an exception due to the parameters of the call, we ignore, as this
        # will be resolved at a different place
        if call_name in SPECIAL_OPERATORS.keys():
            try:
                out_ast.exprType, warns = check_call (call_name,
                         out_ast.output[0]['params'], context)
                warn.extend(warns)
                if out_ast.exprType == UNKNOWN_TYPE:
                    # if type of operator was not found, set to no type at all
                    out_ast.exprType = None
                else:
                    # If there is a return, we are not in a procedure call
                    # symbol, so the input string must keep the "call" keyword
                    # (for example if the call is in a RETURN symbol)
                    out_ast.inputString = get_input_string(root)
            except TypeError as errn:
                if parent is None:
                    # If parent is none we are in an expression, not in 
                    # a procedure call symbol, so we must keep the full
                    # string that may contain the "call" keyword
                    out_ast.inputString = get_input_string(root)
                pass
    return out_ast, err, warn


def outputbody(root, context):
    ''' Parse an output body (the content excluding the CIF statement) '''
    errors = []
    warnings = []
    body = {'outputName': '', 'params': [], 'toDest': ''}
    for child in root.getChildren():
        if child.type == lexer.ID:
            for each in valid_output(context):
                if each.lower() == child.text.lower():
                    # Take the right casing from the declaration
                    body['outputName'] = each
                    break
            else:
                errors.append(f'"{child.text}" is not defined or not visible')
        elif child.type == lexer.PARAMS:
            body['params'], err, warn = expression_list(child, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.TO:
            dest = child.getChild(0).toString()
            # Check that (1) there is a PID type defined
            # and (2) the given name in the TO clause is part of it
            if 'PID' not in types().keys():
                errors.append("No PID type is defined or visible")
            else:
                PID_Values = types()['PID'].type.EnumValues.keys()
                for pid in PID_Values:
                    if pid.lower() == dest.lower().replace('_', '-'):
                        # Get proper casing,etc.
                        body['toDest'] = pid
                        break
                else:
                    errors.append(f"PID not found: {dest}")
        elif child.type == 0:
            # syntax error already caught by the parser
            pass
        else:
            warnings.append('Unsupported child type: {}'.format(child.type))
    # Check/set the type of each param
    try:
        _, _ = check_call(body.get('outputName', '').lower(),
                   body.get('params', []),
                   context)
    except (AttributeError, TypeError) as op_err:
        errors.append(str(op_err) + ' - ' + get_input_string(root))
        LOG.debug('[outputbody] call check_and_fix_op_params : '
                    + get_input_string(root) + str(op_err))
        LOG.debug(str(traceback.format_exc()))
    except Warning as warn:
        warnings.append('{} - {}'.format(str(warn), get_input_string(root)))
    if body['params']:
        body['tmpVars'] = []
        for _ in body['params']:
            body['tmpVars'].append(tmp())
    return body, errors, warnings


def output(root, parent, out_ast=None, context=None):
    ''' Parse an OUTPUT :  set of asynchronous required interface(s) '''
    errors = []
    warnings = []
    out_ast = out_ast or ogAST.Output()  # syntax checker passes no ast
    out_ast.path = context.path
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            out_ast.pos_x, out_ast.pos_y, out_ast.width, out_ast.height = \
                    cif(child)
        elif child.type == lexer.SYMBOLID:
            out_ast.pos_x = symbolid(child)
        elif child.type == lexer.OUTPUT_BODY:
            out_ast.inputString = get_input_string(child)
            out_ast.line = child.getLine()
            out_ast.charPositionInLine = child.getCharPositionInLine()
            body, err, warn = outputbody(child, context)
            errors.extend(err)
            warnings.extend(warn)
            out_ast.output.append(body)
        elif child.type == lexer.COMMENT:
            out_ast.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            out_ast.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == 0:
            pass
        else:
            warnings.append('Unsupported child type: {}'.format(child.type))
    # Report errors with symbol coordinates
    errors = [[e, [out_ast.pos_x or 0, out_ast.pos_y or 0], []]
                for e in errors]
    warnings = [[w, [out_ast.pos_x or 0, out_ast.pos_y or 0], []]
                for w in warnings]
    for e in errors:
        out_ast.errors.append(e[0])
    for w in warnings:
        out_ast.warnings.append(w[0])
    return out_ast, errors, warnings


def alternative_part(root, parent, context):
    ''' Parse a decision answer '''
    errors = []
    warnings = []
    ans = ogAST.Answer()
    ans.path = context.path
    startIndex, stopIndex = None, None
    if root.type == lexer.ELSE:
        # used when copy-pasting
        ans.inputString = root.text
    for child in root.getChildren():
        # There can be multiple answers in one (comma-separated)
        # so instead of storing a single kind and only one answer,
        # we should store them in arrays

        if child.type in (lexer.CLOSED_RANGE,
                          lexer.CONSTANT,
                          lexer.OPEN_RANGE,
                          lexer.INFORMAL_TEXT):
            # We must get the full string for the renderer
            if not startIndex:
                startIndex = child.getTokenStartIndex()
            stopIndex = child.getTokenStopIndex()

        if child.type == lexer.CIF:
            # Get symbol coordinates
            ans.pos_x, ans.pos_y, ans.width, ans.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            ans.pos_x = symbolid(child)
        elif child.type == lexer.CLOSED_RANGE:
            # ans.kinds.append('closed_range')
            cl0, err0, warn0 = expression(child.getChild(0), context)
            cl1, err1, warn1 = expression(child.getChild(1), context)
            errors.extend(err0)
            errors.extend(err1)
            warnings.extend(warn0)
            warnings.extend(warn1)
            ans.answers.append({'kind': 'closed_range', 'content':  [cl0, cl1]})
        elif child.type == lexer.CONSTANT:
            constant_expr, err, warn = expression(child.getChild(0), context)
            ans.answers.append({'kind': 'constant', 'content': (ogAST.ExprEq, constant_expr)})
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.OPEN_RANGE:
            #ans.kinds.append('open_range')
            op = None
            for c in child.getChildren():
                if c.type == lexer.CONSTANT:
                    constant_expr, err, warn = expression(c.getChild(0), context)
                    #ans.constants.append(constant_expr)
                    errors.extend(err)
                    warnings.extend(warn)
                    if not op:
                        op = ogAST.ExprEq
                    ans.answers.append({'kind': 'open_range', 'content': (op, constant_expr)})
                else:
                    op = EXPR_NODE[c.type]
        elif child.type == lexer.INFORMAL_TEXT:
            ans.answers.append({'kind': 'informal_text',
                                'content':  child.getChild(0).toString()[1:-1]})
        elif child.type == lexer.TRANSITION:
            ans.transition, err, warn = transition(
                                        child, parent=ans, context=context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.HYPERLINK:
            ans.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported answer type: ' +
                            sdl92Parser.tokenNamesMap[child.type])

        if child.type in (lexer.CLOSED_RANGE, lexer.CONSTANT,
                          lexer.OPEN_RANGE, lexer.INFORMAL_TEXT):
            #ans.inputString = get_input_string(child)
            ans.inputString = token_stream(child).toString(startIndex, stopIndex)
            ans.line = child.getLine()
            ans.charPositionInLine = child.getCharPositionInLine()
            # Report errors with symbol coordinates
            x, y = (ans.pos_x or 0, ans.pos_y or 0)
            errors = [[e, [x, y], []] for e in errors]
            warnings = [[w, [x, y], []] for w in warnings]
            for e in errors:
                ans.errors.append(e[0])
            for w in warnings:
                ans.warnings.append(w[0])
    return ans, errors, warnings


def decision(root, parent, context):
    ''' Parse a DECISION '''
    errors, warnings, qerr, qwarn = [], [], [], []
    dec = ogAST.Decision()
    dec.path = context.path
    dec.tmpVar = tmp()
    has_else = False
    dec_x, dec_y = 0, 0
    # To support the "decision any" construct:
    need_random_generator = False
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            dec.pos_x, dec.pos_y, dec.width, dec.height = cif(child)
            dec_x, dec_y = dec.pos_x, dec.pos_y
        elif child.type == lexer.SYMBOLID:
            dec.pos_x = symbolid(child)
            dec_x = dec.pos_x
        elif child.type == lexer.QUESTION:
            dec.kind = 'question'
            dec.question, qerr, qwarn = expression(child.getChild(0), context)
            dec.inputString = get_input_string(child.getChild(0))
            #dec.inputString = dec.question.inputString
            dec.line = dec.question.line
            dec.charPositionInLine = dec.question.charPositionInLine
        elif child.type == lexer.INFORMAL_TEXT:
            dec.kind = 'informal_text'
            dec.inputString = get_input_string(child)
            dec.informalText = child.getChild(0).toString()[1:-1]
            dec.line = child.getLine()
            dec.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.ANY:
            msg = 'Use of "ANY" introduces non-determinism'
            warnings.append([msg, [dec.pos_x, dec.pos_y], []])
            dec.warnings.append(msg)
            dec.kind = 'any'
            need_random_generator = True
            dec.inputString = get_input_string(child)
            dec.question = ogAST.PrimStringLiteral()
            dec.question.value = 'ANY'
            dec.question.exprType = RAWSTRING
        elif child.type == lexer.COMMENT:
            dec.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            dec.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == lexer.ANSWER:
            ans, err, warn = alternative_part(child, parent, context)
            errors.extend(err)
            warnings.extend(warn)
            dec.answers.append(ans)
        elif child.type == lexer.ELSE:
            ans = ogAST.Answer()
            ans.path = context.path
            ans.inputString = child.toString()
            for c in child.getChildren():
                if c.type == lexer.CIF:
                    ans.pos_x, ans.pos_y, ans.width, ans.height = cif(c)
                elif c.type == lexer.SYMBOLID:
                    ans.pos_x = symbolid(c)
                elif c.type == lexer.TRANSITION:
                    ans.transition, err, warn = transition(
                                            c, parent=ans, context=context)
                    errors.extend(err)
                    warnings.extend(warn)
                elif child.type == lexer.HYPERLINK:
                    ans.hyperlink = child.getChild(0).toString()[1:-1]
            ans.answers.append({'kind': 'else', 'content': None})
            dec.answers.append(ans)
            has_else = True
        else:
            msg = f'Unsupported DECISION child type: {str(child.type)}'
            warnings.append([msg, [dec.pos_x, dec.pos_y], []])
            dec.warnings.append(msg)
    if need_random_generator:
        # If there are N answers, code generators will need a random
        # number from 0 to N.
        context.random_generator.add(len(dec.answers))
    # Make type checks to be sure that question and answers are compatible
    covered_ranges = defaultdict(list)
    qmin, qmax = 0, 0
    need_else = False
    is_enum, is_bool = False, False
    for ans in dec.answers:
        for element in ans.answers:
            # Each answer branch can have multiple answers (comma-separated)
            ans_kind    = element['kind']
            ans_content = element['content']

            if dec.kind in ('informal_text', 'any'):
                break # break from inner loop only, but that will do
            ans_x, ans_y = ans.pos_x, ans.pos_y

            if ans_kind in ('constant', 'open_range'):
                # asn_content is a tuple  (operator, constant)
                op, constant = ans_content # get the constant

                expr = op()  # instantiate the type, e.g. ExprEq
                expr.left = dec.question
                expr.right = constant

                try:
                    answarn = fix_expression_types(expr, context)
                    answarn = [[w, [ans_x, ans_y], []] for w in answarn]
                    for w in answarn:
                        ans.warnings.append(w[0])
                    warnings.extend(answarn)
                    if dec.question.exprType == UNKNOWN_TYPE:
                        dec.question = expr.left

                    # Update the type of the constant
                    constant = expr.right
                    element['content'] = (op, constant)

                    q_basic = find_basic_type(dec.question.exprType)
                    a_basic = find_basic_type(constant.exprType)

                    if q_basic.kind.endswith('EnumeratedType'):
                        if not constant.is_raw:
                            # Ref to a variable -> can't guarantee coverage
                            need_else = True
                            continue
                        covered_ranges[ans].append(constant.inputString.lower())
                        is_enum = True
                    elif q_basic.kind == 'BooleanType':
                        covered_ranges[ans].append(constant.value[0])
                        is_bool = True
                        if not constant.is_raw:
                            need_else = True
                            continue
                    if not q_basic.kind.startswith(('Integer', 'Real')):
                        # Check numeric questions - ignore others
                        continue
                    # If the answer is an ASN.1 constant we must not use
                    # the range of its type when we check the decision branches
                    if isinstance(constant, ogAST.PrimConstant):
                        a_basic_Min = a_basic_Max = \
                              get_asn1_constant_value (constant.constant_value)
                    elif isinstance(constant, (ogAST.PrimOctetStringLiteral,
                                              ogAST.PrimBitStringLiteral)):
                        a_basic_Min = a_basic_Max = constant.numeric_value
                    else:
                        a_basic_Min, a_basic_Max = a_basic.Min, a_basic.Max

                    delta = 1 if q_basic.kind.startswith('Integer') else 1e-10
                    # numeric type -> find the range covered by this answer
                    if a_basic_Min != a_basic_Max:
                        # Not a constant or a raw number, range is not fix
                        need_else = True
                        continue
                    val_a = float(a_basic_Min)
                    qmin, qmax = float(q_basic.Min), float(q_basic.Max)
                    # Check the operator to compute the range
                    reachable = True
                    if op == ogAST.ExprLe:
                        # answer <= X means covered range is [min; X]
                        if qmin <= val_a:
                            covered_ranges[ans].append((qmin, val_a))
                        else:
                            reachable = False
                    elif op == ogAST.ExprLt:
                        # answer < X means covered range is [min; X[
                        if qmin < val_a:
                            covered_ranges[ans].append((qmin, val_a - delta))
                        else:
                            reachable = False
                    elif op == ogAST.ExprGt:
                        # answer > X means covered range is ]X; max]
                        if qmax > val_a:
                            covered_ranges[ans].append((val_a + delta, qmax))
                        else:
                            reachable = False
                    elif op == ogAST.ExprGe:
                        # answer >= X means covered range is [X; max]
                        if qmax >= val_a:
                            covered_ranges[ans].append((val_a, qmax))
                        else:
                            reachable = False
                    elif op == ogAST.ExprEq:
                        if qmin <= val_a <= qmax:
                            covered_ranges[ans].append((val_a, val_a))
                        else:
                            reachable = False
                    elif op == ogAST.ExprNeq:
                        # answer != X means covered range is [min; X[;]X; max]
                        if qmin == val_a:
                            covered_ranges[ans].append((qmin + delta, qmax))
                        elif qmax == val_a:
                            covered_ranges[ans].append((qmin, qmax - delta))
                        elif qmin < val_a < qmax:
                            covered_ranges[ans].append((qmin, val_a - delta))
                            covered_ranges[ans].append((val_a + delta, qmax))
                        else:
                            msg = f'Condition is always true: {dec.inputString} /= {ans.inputString}'
                            warnings.append([msg, [ans_x, ans_y], []])
                            ans.warnings.append(msg)
                    else:
                        msg = 'Unsupported range expression'
                        warnings.append([msg, [ans_x, ans_y], []])
                        ans.warnings.append(msg)
                    if not reachable:
                        msg = f'Decision "{dec.inputString}": Unreachable branch "{ans.inputString}"'
                        warnings.append([msg, [ans_x, ans_y], []])
                        ans.warnings.append(msg)
                except (AttributeError, TypeError) as err:
                    LOG.debug('ogParser:\n' + str(traceback.format_exc()))
                    msg = f'Type mismatch: question ({expr.left.inputString}, type={type_name(expr.left.exprType)}'\
                          f'), answer ({expr.right.inputString}, type={type_name(expr.right.exprType)}) {str(err)}'
                    errors.append([msg, [ans_x, ans_y], []])
                    ans.errors.append(msg)
                except Warning as warn:
                    msg = 'Type mismatch: ' + str(warn)
                    warnings.append([msg, [ans_x, ans_y], []])
                    ans.warnings.append(msg)
            elif ans_kind == 'closed_range':
                if not is_numeric(dec.question.exprType):
                    msg = 'Closed range are only for numerical types'
                    errors.append([msg, [ans_x, ans_y], []])
                    ans.errors.append(msg)
                    continue
                closedRange = ans_content
                for ast_type, idx in zip((ogAST.ExprGe, ogAST.ExprLe), (0, 1)):
                    expr = ast_type()
                    expr.left = dec.question
                    #expr.right = ans.closedRange[idx]
                    expr.right = closedRange[idx]
                    try:
                        warnings.extend(fix_expression_types(expr, context))
                        if dec.question.exprType == UNKNOWN_TYPE:
                            dec.question = expr.left
                        #ans.closedRange[idx] = expr.right
                        element['content'][idx] = expr.right
                        closedRange = element['content']
                    except (AttributeError, TypeError) as err:
                        msg = ('Type mismatch in decision: '
                            'question (' + expr.left.inputString + ', type= ' +
                            type_name(expr.left.exprType) + '), answer (' +
                            expr.right.inputString + ', type= ' +
                            type_name(expr.right.exprType) + ') ' + str(err))
                        errors.append([msg, [ans_x, ans_y], []])
                        ans.errors.append(msg)

                q_basic = find_basic_type(dec.question.exprType)
                if not q_basic.kind.startswith(('Integer', 'Real')):
                    continue
                delta = 1 if q_basic.kind.startswith('Integer') else 1e-10
                # numeric type -> find the range covered by this answer
                # If answers are OctetStringLiteral, user their integer value
                if isinstance(closedRange[0], (ogAST.PrimOctetStringLiteral,
                                               ogAST.PrimBitStringLiteral)):
                    a0_val = float(closedRange[0].numeric_value)
                else:
                    a0_basic = find_basic_type(closedRange[0].exprType)
                    if not hasattr(a0_basic, "Min") or a0_basic.Min != a0_basic.Max:
                        # Not a constant or a raw number, range is not fix
                        need_else = True
                        continue
                    a0_val = float(a0_basic.Min)

                if isinstance(closedRange[1], (ogAST.PrimOctetStringLiteral,
                                               ogAST.PrimBitStringLiteral)):
                    a1_val = float(closedRange[1].numeric_value)
                else:
                    a1_basic = find_basic_type(closedRange[1].exprType)
                    if not hasattr(a1_basic, "Min") or a1_basic.Min != a1_basic.Max:
                        # Not a constant or a raw number, range is not fix
                        need_else = True
                        continue
                    a1_val = float(a1_basic.Max)

                qmin, qmax = float(q_basic.Min), float(q_basic.Max)
                if a0_val < qmin:
                    qwarn.append('Decision "{dec}": '
                                    'Range {a0} .. {qmin} is unreachable'
                                    .format(a0=a0_val, qmin=round(qmin - delta, 9),
                                            dec=dec.inputString))
                if a1_val > qmax:
                    qwarn.append('Decision "{dec}": '
                                    'Range {qmax} .. {a1} is unreachable'
                                    .format(qmax=round(qmax + delta), a1=a1_val,
                                            dec=dec.inputString))
                if (a0_val < qmin and a1_val < qmin) or (a0_val > qmax and
                                                         a1_val > qmax):
                    msg = f'Decision "{dec.inputString}": Unreachable branch {a0_val}:{a1_val}'
                    warnings.append([msg, [ans_x, ans_y], []])
                    ans.warnings.append(msg)
                covered_ranges[ans].append((a0_val, a1_val))
    # Check the following
    # (1) no overlap between covered ranges in decision answers
    # (2) no gap in the coverage of the decision possible values
    # (3) ELSE branch, if present, can be reached
    # (4) if an answer uses a non-ground expression an ELSE is there
    # (5) boolean expressions are fully covered
    # (6) present() operator and enumerated question are fully covered

    # (1) no overlap between covered ranges in decision answers
    q_ranges = [(qmin, qmax)] if dec.question \
                              and is_numeric(dec.question.exprType) else []
    for each in combinations(covered_ranges.items(), 2):
        if not q_ranges:
            continue
        for comb in combinations(
                chain.from_iterable(val[1] for val in each), 2):
            comb_overlap = (max(comb[0][0], comb[1][0]),
                            min(comb[0][1], comb[1][1]))
            if comb_overlap[0] <= comb_overlap[1]:
                # (1) - check for overlaps
                qerr.append('Decision "{d}": answers {a1} and {a2} '
                              'are overlapping in range {o1} .. {o2}'
                              .format(d=dec.inputString,
                                      a1=each[0][0].inputString,
                                      a2=each[1][0].inputString,
                                      o1=comb_overlap[0],
                                      o2=comb_overlap[1]))
    new_q_ranges = []
    # (2) Check that decision range is fully covered
    for ans_ref, ranges in covered_ranges.items():
        if is_enum or is_bool:
            continue
        for mina, maxa in ranges:
            for minq, maxq in q_ranges:
                left = (minq, min(maxq, mina - delta))
                right = (max(minq, maxa + delta), maxq)
                if mina > minq and maxa < maxq:
                    new_q_ranges.extend([left, right])
                elif mina <= minq and maxa >= maxq:
                    pass
                elif mina <= minq:
                    new_q_ranges.append(right)
                elif maxa >= maxq:
                    new_q_ranges.append(left)
            q_ranges, new_q_ranges = new_q_ranges, []
    if not has_else:
        for minq, maxq in q_ranges:
            low, high = round(minq, 9), round(maxq, 9)
            if low == high:
                txt = f"value {low}"
            else:
                txt = f"range {low} .. {high}"
            qerr.append(f'Decision "{dec.inputString}": No answer to cover {txt}')

    elif has_else and is_numeric(dec.question.exprType) and not q_ranges:
        # (3) Check that ELSE branch is reachable
        qwarn.append(f'Decision "{dec.inputString}": ELSE branch is unreachable')

    if need_else and not has_else:
        # (4) Answers use non-ground expression -> there should be an ELSE
        qwarn.append(f'Decision "{dec.inputString}": Missing ELSE branch')

    if need_else and has_else and len(dec.answers) != 2:
        # At least one branch has a non-ground expression answer, therefore
        # there can be at most one additional answer: the ELSE branch,
        # otherwise there is a risk that branches overlap due to variables
        qerr.append(f'Answers of decision "{dec.inputString}" could overlap')

    # (5) check coverage of boolean types
    # Rules:
    # a. exactly 2 answers
    # b. if one answer is not ground expression, other branch must be ELSE
    # c. if there is a ground expression G in a branch, the other branch
    #    must evaluate to non-G or be ELSE

    # (6) check coverage of enumerated types
    if is_enum or is_bool:
        # check duplicate answers
        answers = [a.lower()
                   for a in chain.from_iterable(covered_ranges.values())]
        dupl = [a for a, v in Counter(answers).items() if v > 1]
        if dupl:
            qerr.append('Decision "{}": duplicate answers "{}"'
                          .format(dec.inputString, '", "'.join(dupl)))
        if is_bool:
            enumerants = ['true', 'false']
            if len(answers) + (1 if has_else else 0) != 2:
                qerr.append('Boolean decision "{}" must have exactly 2 answers'
                           .format(dec.inputString))
        else:
            enumerants = [en.replace('-', '_').lower()
                      for en in q_basic.EnumValues.keys()]
        # check for missing answers
        if set(answers) != set(enumerants) and not has_else:
            qerr.append('Decision "{}": Missing branches for answer(s) "{}"'
                          .format(dec.inputString,
                                  '", "'.join(set(enumerants) - set(answers))))
    qerr = [[e, [dec_x, dec_y], []] for e in qerr]
    qwarn = [[w, [dec_x, dec_y], []] for w in qwarn]
    for e in qerr:
        dec.errors.append(e[0])
    for w in qwarn:
        dec.warnings.append(w[0])
    errors.extend(qerr)
    warnings.extend(qwarn)
    return dec, errors, warnings


def nextstate(root, context):
    ''' Parse a NEXTSTATE [: type] [VIA State_Entry_Point]
        detect various kinds of errors when trying to enter a nested state '''
    next_state_id, via, entrypoint, instance_of = '', None, None, None
    errors = []
    for child in root.getChildren():
        if child.type == lexer.ID:
            next_state_id = child.text
        elif child.type == lexer.DASH:
            next_state_id = '-'
        elif child.type == lexer.HISTORY_NEXTSTATE:
            next_state_id = '-*'
        elif child.type == lexer.VIA:
            if next_state_id.strip() not in ('-', '-*'):
                via = get_input_string(root).replace(
                                                'NEXTSTATE', '', 1).strip()
                entrypoint = child.getChild(0).text
            else:
                errors.append('"History" NEXTSTATE cannot have a "via" clause')
        elif child.type == lexer.TYPE_INSTANCE:
            instance_of = child.getChild(0).text
            via = get_input_string(root).replace(
                                                'NEXTSTATE', '', 1).strip()
        else:
            errors.append('NEXTSTATE undefined construct: ' +
                            sdl92Parser.tokenNamesMap[child.type])

    # Checks on the NEXTSTATE
    if via:  # instance and/or via clause
        state_id = instance_of or next_state_id
        try:
            composite, = (comp for comp in context.composite_states
                          if comp.statename.lower() == state_id.lower())
        except ValueError:
            errors.append(f'State {state_id} is not a composite state')
        else:
            if entrypoint is None:
                pass
            elif entrypoint.lower() not in composite.state_entrypoints:
                errors.append(
                        f'State {state_id} has no "{entrypoint}" entrypoint')
            # The test below seems identical to the one just done
#           for each in composite.content.named_start:
#               if not entrypoint or \
#                       each.inputString == entrypoint.lower() + '_START':
#                   break
#           else:
#               errors.append(f'Entrypoint {entrypoint} in state'
#                       f' {state_id} is declared but not defined')
    else: # not via and/or instance
        # check that if the nextstate is nested, it has a START symbol
        try:
            composite, = (comp for comp in context.composite_states
                      if comp.statename.lower() == next_state_id.lower())
            if not isinstance(composite, ogAST.StateAggregation) \
                    and not composite.content.start:
                errors.append('Composite state "{}" has no unnamed '
                              'START symbol'.format(composite.statename))
        except ValueError:
            pass
    return next_state_id, via, entrypoint, instance_of, errors


def terminator_statement(root, parent, context):
    ''' Parse a terminator (NEXTSTATE, JOIN, STOP) '''
    errors = []
    warnings = []
    t = ogAST.Terminator()
    t.path = context.path
    t.context = context
    for term in root.getChildren():
        if term.type == lexer.CIF:
            t.pos_x, t.pos_y, t.width, t.height = cif(term)
        elif term.type == lexer.SYMBOLID:
            t.pos_x = symbolid(term)
        elif term.type == lexer.LABEL:
            lab, err, warn = label(term, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            t.label = lab
            context.labels.append(lab)
            lab.terminators = [t]
        elif term.type == lexer.NEXTSTATE:
            t.kind = 'next_state'
            t.inputString, t.via, t.entrypoint, t.instance_of, err = \
                    nextstate(term, context)
            if err:
                errors.extend(err)
            t.line = term.getChild(0).getLine()
            t.charPositionInLine = term.getChild(0).getCharPositionInLine()
            # Add next state infos at process level
            # Used in rendering backends to merge a NEXTSTATE with a STATE
            context.terminators.append(t)
            # post-processing: if nextatate is nested, add link to the content
            # (normally handled at state level, but if state is not defined
            # standalone, the nextstate must hold the composite content)
            if t.inputString not in ('-', '-*'):
                for each in context.composite_states:
                    if each.statename.lower() == t.inputString.lower():
                        t.composite = each
        elif term.type == lexer.JOIN:
            t.kind = 'join'
            t.inputString = term.getChild(0).toString()
            t.line = term.getChild(0).getLine()
            t.charPositionInLine = term.getChild(0).getCharPositionInLine()
            context.terminators.append(t)
        elif term.type == lexer.STOP:
            t.kind = 'stop'
            context.terminators.append(t)
        elif term.type == lexer.RETURN:
            t.kind = 'return'
            if term.children:
                t.return_expr, err, warn = expression(
                        term.getChild(0), context)
                t.inputString = t.return_expr.inputString
                errors.extend(err)
                warnings.extend(warn)
            context.terminators.append(t)
        elif term.type == lexer.COMMENT:
            t.comment, _, _ = end(term)
        elif term.type == lexer.HYPERLINK:
            t.hyperlink = term.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported terminator type: ' +
                    str(term.type))
    # Report errors with symbol coordinates
    errors = [[e, [t.pos_x or 0, t.pos_y or 0], []] for e in errors]
    warnings = [[w, [t.pos_x or 0, t.pos_y or 0], []] for w in warnings]
    for e in errors:
        t.errors.append(e[0])
    for w in warnings:
        t.warnings.append(w[0])
    return t, errors, warnings


def transition(root, parent, context):
    ''' Parse a transition '''
    errors = []
    warnings = []
    trans = ogAST.Transition()
    trans.path = context.path
    # Used to list terminators in this transition
    terminators = {'trans': len(context.terminators)}
    #terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.PROCEDURE_CALL:
            proc_call, err, warn = procedure_call(
                            child, parent=parent, context=context)
            # Check if the procedure call has a return type
            # In that case it is an error, it must be called from
            # a TASK to assign the result to a variable
            if proc_call.exprType is not None:
                call_name = proc_call.output[0]['outputName']
                msg = (f"A procedure with a return type must be called"
                    f" from a TASK symbol (syntax: ret := call {call_name}"
                    " (params))")
                err.append([msg, [proc_call.pos_x or 0, proc_call.pos_y or 0], []])
                proc_call.errors.append(msg)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(proc_call)
            parent = proc_call
        elif child.type == lexer.LABEL:
            term_count       = len(context.terminators)
            lab, err, warn   = label(child, parent=parent, context=context)
            terminators[lab] = term_count
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(lab)
            parent = lab
            context.labels.append(lab)
        elif child.type == lexer.TASK:
            tas, err, warn = task(child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(tas)
            parent = tas
        elif child.type == lexer.TASK_BODY:
            t, err, warn = task_body(child, context)
            t.inputString = get_input_string(child)
            t.line = child.getLine()
            t.charPositionInLine = child.getCharPositionInLine()
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(t)
            parent = t
        elif child.type == lexer.OUTPUT:
            out_ast = ogAST.Output()
            out_ast.path = context.path
            _, err, warn = output(child,
                               parent=parent,
                               out_ast=out_ast,
                               context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(out_ast)
            parent = out_ast
        elif child.type == lexer.DECISION:
            dec, err, warn = decision(child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(dec)
            parent = dec
        elif child.type == lexer.TERMINATOR:
            term, err, warn = terminator_statement(child,
                    parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.terminator = term
        else:
            warnings.append('Unsupported symbol in transition, type: ' +
                    str(child.type))
    # At the end of the transition parsing, get the list of terminators
    # the transition contains by making a diff with the list at context
    # level (we counted the number of terminators before parsing the item)
    trans.terminators = list(context.terminators[terminators.pop('trans'):])
    # Also update the list of terminators of each label in the transition
    for lab, term_count in terminators.items():
        lab.terminators = list(context.terminators[term_count:])
    return trans, errors, warnings


def assign(root, context):
    ''' Parse an assignment (a := b) in a task symbol '''
    errors = []
    warnings = []
    expr = ogAST.ExprAssign(
        get_input_string(root),
        root.getLine(),
        root.getCharPositionInLine()
    )
    expr.kind = 'assign'

    if len(root.children) != 2:
        errors.append('Syntax error: {}'.format(expr.inputString))

    if root.children[0].type == lexer.CALL:
        # usually index or substring, should not be a procedure call
        # on the left side of the expression
        #print("Call expression:", expr.inputString)
        expr.left, err, warn = call_expression(root.children[0], context,
                                               pos="left")
    elif root.children[0].type == lexer.SELECTOR:
        expr.left, err, warn = selector_expression(root.children[0], context,
                                                   pos="left")
    else:
        expr.left, err, warn = primary_variable(root.children[0], context)
    warnings.extend(warn)
    errors.extend(err)

    try:
        expr.right, err, warn = expression(root.children[1], context)
    except NotImplementedError as nie:
        errors.append(str(nie))
    else:
        errors.extend(err)
        warnings.extend(warn)

    # Check if left side is a FPAR IN parameter. They are read-only.
    left = expr.left
    while isinstance(left, (ogAST.PrimIndex, ogAST.PrimSubstring, ogAST.PrimSelector)):
        left = left.value[0]
    if isinstance(left, ogAST.PrimFPAR):
        fpar = left.value[0]
        for each in context.fpar:
            if each['name'].lower() == fpar.lower():
                if each['direction'] == 'in':
                    errors.append(f'"{fpar}" is an IN parameter (read-only)')
                break;
    elif left.exprType.__name__ == 'for_range':
        # Check that user does does try to write the forloop iterator (range)
        errors.append(f'Assignment to loop parameter "{left.value[0]}" is not allowed')

    try:
        warnings.extend(fix_expression_types(expr, context))
        # If assignment with numerical value: check range
        w = Assign_Check_Range (expr)
        if w is not None:
            warnings.append(w)
    except(AttributeError, TypeError) as err:
        LOG.debug(str(traceback.format_exc()))
        errors.append(u'In "{exp}": Type mismatch ({lty} vs {rty} - {errstr})'
                      .format(exp=expr.inputString,
                              lty=type_name(expr.left.exprType) if
                                expr.left and expr.left.exprType
                                else 'Undefined',
                              rty=type_name(expr.right.exprType) if
                                expr.right and expr.right.exprType
                                else 'Undefined',
                              errstr=str(err)))
    except Warning as warn:
        warnings.append(str(warn))
    if not errors:
        if expr.right.exprType == UNKNOWN_TYPE or not \
                isinstance(expr.right, (ogAST.ExprAppend,
                                        ogAST.ExprMod,
                                        ogAST.PrimSequenceOf,
                                        ogAST.PrimStringLiteral)):
            if isinstance(expr.right, ogAST.PrimCall) \
                    and expr.right.value[0]  in ('abs', 'length'):
                pass
            else:
                basic_right = find_basic_type(expr.right.exprType)
                if not basic_right.kind.startswith('Integer'):
                    expr.right.exprType = expr.left.exprType
        # XXX I don't understand why we don't set the type of right
        # to the same value as left in case of ExprAppend
        # Setting it - I did not see any place in the Ada backend where
        # this could cause a bug (and regression is OK)
#       if isinstance(expr.right, ogAST.ExprAppend):
#           fix_append_expression_type(expr.right, expr.left.exprType)
#           # all append components must be of the same type, which is the
#           # type of the left part of the expression. we must recursively
#           # fix the right type, in case we have the for a//b//c
#           # that is handled as (a//b)//c
#           def rec_append(inner_expr, set_type):
#               for each in (inner_expr.left, inner_expr.right):
#                   if isinstance(each, ogAST.ExprAppend):
#                       rec_append(each, set_type)
#                   each.expected_type = set_type
#           rec_append(expr.right, expr.left.exprType)
#           expr.right.exprType      = expr.left.exprType
#           expr.right.expected_type = expr.left.exprType
#           #print 'here in assign', expr.right.inputString
        if isinstance(expr.right, (ogAST.PrimSequenceOf,
                                   ogAST.PrimStringLiteral)):
            # Set the expected type on the right, this is needed to know
            # if the expected size is variable or fixed in backends
            expr.right.expected_type = expr.left.exprType
    return expr, errors, warnings


def for_range(root, context):
    ''' Parse a RANGE statement (in a FOR loop) '''
    errors = []
    warnings = []
    # start and stop are expressions
    result = {'start': None, 'stop': None, 'step': 1}
    expr = []
    for child in root.getChildren():
        if child.type == lexer.GROUND:
            ground, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
            expr.append(ground)
        elif child.type == lexer.INT:
            result['step'] = int(child.text)
        else:
            warnings.append('Unsupported child type in RANGE: ' +
                            str(child.type))
    for range_item in expr:
        if not range_item:
            errors.append('Range must use a ground expression: '
                          + range_item.inputString)
    if len(expr) == 2:
        result['start'], result['stop'] = expr
    elif len(expr) == 1:
        result['stop'] = expr[0]
    else:
        errors.append('Incorrect range expression')
    # Basic check that range element basic types are all integers
    for each in expr:
        basic = find_basic_type(each.exprType)
        if not basic.kind.startswith("Integer"):
            errors.append(u"Expression {} is not evaluated to integer"
                          .format(each.inputString))
    return result, errors, warnings


def for_loop(root, context):
    ''' Parse a FOR LOOP in a task symbol '''
    errors = []
    warnings = []
    forloop = {'var': '', 'type': None,
               'list': '', 'range': None,
               'transition': None}
    for child in root.getChildren():
        if child.type == lexer.ID:
            forloop['var'] = child.text
            # Implicit variable declaration for the iterator
            context_scope = dict(context.variables)
            context_scope.update(context.monitors)
            if child.text.lower() in (var.lower()
                      for var in chain (context.variables.keys(),
                                        context.global_variables.keys(),
                                        context.monitors.keys(),
                                        context.global_monitors.keys())):
                errors.append("FOR variable '{}' is already declared in the"
                              " scope (shadow variable). Please rename it."
                              .format(child.text))
        elif child.type == lexer.VARIABLE:
            forloop['list'], err, warn = primary_variable(child, context)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == lexer.CALL:
            forloop['list'], err, warn = call_expression(child, context)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == lexer.SELECTOR:
            forloop['list'], err, warn = selector_expression(child, context)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == lexer.RANGE:
            forloop['range'], err, warn = for_range(child, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.TRANSITION:
            # First we need to define the type of the iterator (and check it)
            if forloop['list']:
                basic_type = find_basic_type(forloop['list'].exprType)
                if basic_type.kind != 'SequenceOfType':
                    errors.append('Variable {} is not iterable'
                                  .format(forloop['list'].inputString))
                else:
                    forloop['type'] = basic_type.type
                    # Set the type of the iterator
                    context.variables[forloop['var']] = (forloop['type'], 0)
            elif forloop['range']:
                # Using a range - set type of iterator to standard integer
                start_expr, stop_expr = forloop['range']['start'], \
                                        forloop['range']['stop']
                if not start_expr:
                    r_min = '0'
                else:
                    basic = find_basic_type(start_expr.exprType)
                    # ASN.1 constant -> use the constant value
                    if isinstance(start_expr, ogAST.PrimConstant):
                       basic.Min = \
                             get_asn1_constant_value(start_expr.constant_value)
                    r_min = basic.Min if basic != UNKNOWN_TYPE else '0'
                basic = find_basic_type(stop_expr.exprType)
                # ASN.1 constant -> get the value in place of the type's Max
                if isinstance(stop_expr, ogAST.PrimConstant):
                   basic.Max = \
                           get_asn1_constant_value(stop_expr.constant_value)
                r_max = str(int(float(basic.Max) - 1)) \
                        if basic != UNKNOWN_TYPE else '4294967295'
                result_type = type('for_range', (INT32,), {'Min': r_min,
                                                           'Max': r_max})
                forloop['type'] = result_type
                context.variables[forloop['var']] = (result_type, 0)

            forloop['transition'], err, warn = transition(
                                    child, parent=for_loop, context=context)
            # if the transition contains tasks or other constructs that are
            # normally inside a graphical symbol, the errors and warnings will
            # contain coordinates. Remove them, they will be replaced by those
            # of the TASK symbol that contains the for loop
            errors.extend(e[0] if type(e) is list else e for e in err)
            warnings.extend(w[0] if type(w) is list else w for w in warn)
        else:
            warnings.append('Unsupported child type in FOR body' +
                            str(child.type))
    context.variables = context_scope
    return forloop, errors, warnings


def task_body(root, context):
    ''' Parse the body of a task (excluding CIF and TASK tokens) '''
    errors = []
    warnings = []
    body = None
    for child in root.getChildren():
        if child.type == lexer.ASSIGN:
            if not body:
                body = ogAST.TaskAssign()
                body.path = context.path
            assig, err, warn = assign(child, context)
            errors.extend(err)
            warnings.extend(warn)
            body.elems.append(assig)
        elif child.type == lexer.INFORMAL_TEXT:
            if not body:
                body = ogAST.TaskInformalText()
                body.path = context.path
            body.elems.append(child.getChild(0).toString()[1:-1])
        elif child.type == lexer.FOR:
            if not body:
                body = ogAST.TaskForLoop()
                body.path = context.path
            forloop, err, warn = for_loop(child, context)
            errors.extend(err)
            warnings.extend(warn)
            body.elems.append(forloop)
        elif child.type == 0:
            pass
        else:
            warnings.append('Unsupported task child: {}'.format(child.type))
    if not body:
        body = ogAST.TaskAssign()
        body.path = context.path
    return body, errors, warnings


def task(root, parent=None, context=None):
    ''' Parse a TASK symbol (assignment or informal text) '''
    errors = []
    warnings = []
    coord = False
    comment, body = None, None
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            pos_x, pos_y, width, height = cif(child)
            coord = True
        elif child.type == lexer.SYMBOLID:
            coord = True
            pos_x = symbolid(child)
            pos_y, width, height = 0, 0, 0
        elif child.type == lexer.TASK_BODY:
            body, task_err, task_warn = task_body(child, context)
            body.inputString = get_input_string(child)
            body.line = child.getLine()
            body.charPositionInLine = child.getCharPositionInLine()
            errors.extend(task_err)
            warnings.extend(task_warn)
        elif child.type == lexer.COMMENT:
            comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            body.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported child type in task definition: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    if coord and body:
        body.pos_x, body.pos_y, body.width, body.height = \
                pos_x, pos_y, width, height
        errors = [[e, [pos_x, pos_y], []] for e in errors]
        warnings = [[w, [pos_x, pos_y], []] for w in warnings]
    else:
        errors = [[e, [0, 0], []] for e in errors]
        warnings = [[w, [0, 0], []] for w in warnings]
    if body:
        body.comment = comment
    else:
        warnings.append(['TASK missing content', [pos_x or 0, pos_y or 0], []])
        body = ogAST.TaskAssign()
        body.path = context.path
    for e in errors:
        body.errors.append(e[0])
    for w in warnings:
        body.warnings.append(w[0])
    return body, errors, warnings


def label(root, parent, context=None):
    ''' Parse a LABEL symbol '''
    errors = []
    warnings = []
    lab = ogAST.Label()
    lab.path = context.path
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            lab.pos_x, lab.pos_y, lab.width, lab.height = cif(child)
        elif child.type == lexer.SYMBOLID:
            lab.pos_x = symbolid(child)
        elif child.type == lexer.ID:
            lab.inputString = get_input_string(child)
            lab.line = child.getLine()
            lab.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.HYPERLINK:
            lab.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append(
                    'Unsupported child type in label definition: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    errors = [[e, [lab.pos_x or 0, lab.pos_y or 0], []] for e in errors]
    warnings = [[w, [lab.pos_x or 0, lab.pos_y or 0], []] for w in warnings]
    for e in errors:
        lab.errors.append(e[0])
    for w in warnings:
        lab.warnings.append(w[0])
    return lab, errors, warnings


def stop_if(root, parent, context=None):
    ''' Parse a set of stop conditions - Return an list of expressions
        Can be used in simulators to cut off paths
        ** This is an extension of the SDL grammar **
    '''
    expressions, errors, warnings = [], [], []
    for each in root.getChildren():
        expr, err, warn = expression(each, context)
        expr.exprType = BOOLEAN
        expressions.append(expr)
        errors.extend(err)
        warnings.extend(warn)
    errors = [[e, [0, 0], []] for e in errors]
    warnings = [[w, [0, 0], []] for w in warnings]
    return expressions, errors, warnings


def pr_file(root):
    ''' Complete PR model - can be made up from several files/strings '''
    errors = []
    warnings = []
    ast = ogAST.AST()
    global DV

    # In case no ASN.1 files are parsed, the DV structure is pre-initialised
    # This to allow SDL types and constant injection in ASN1 ASTs
    DV = type("ASNParseTree", (object, ),
              {"types": {}, "exportedVariables": {}, "asn1Modules": [],
                  "exportedTypes": {}, "variables": {}, "SDL_Constants": {}})

    # Re-order the children of the AST to make sure system and use clauses
    # are parsed before process definition - to get signal definitions
    # and data types references.
    processes, uses, systems = [], [], []

    for child in root.getChildren():
        if node_filename(child) is not None:
            ast.pr_files.add(node_filename(child))
        if child.type == lexer.PROCESS:
            processes.append(child)
        elif child.type == lexer.USE:
            uses.append(child)
        elif child.type == lexer.SYSTEM:
            systems.append(child)
        else:
            LOG.error('Unsupported construct in PR:' + str(child.type))
            LOG.error(str(child))
    LOG.debug(f"Parsed {len(processes)} process(es), "
             f" {len(uses)} use statement(s), "
             f" and {len(systems)} systems")
    for child in uses:
        # USE clauses can contain a CIF comment with the ASN.1 filename
        use_clause_subs = child.getChildren()
        asn1_filename = None
        for clause in use_clause_subs:
            entities = []
            if clause.type == lexer.ASN1:
                asn1_filename = clause.getChild(0).text[1:-1]
                if not os.path.isfile(asn1_filename):
                    errors.append("File not found: " + asn1_filename)
                else:
                    ast.asn1_filenames.append(os.path.abspath(asn1_filename))
                #ast.asn1_filenames.append(asn1_filename)
            else:
                entities.append(clause.text)
            if len(entities) == 1:
                ast.use_clauses.append(entities[0])
            elif len(entities) > 1:
                ast.use_clauses.extend('{}/{}'
                           .format(entities[0], each) for each in entities[1:])
#       if not asn1_filename:
#           # Look for case insensitive pr file and add it to AST
#           search = fnmatch.translate(clause.text + '.pr')
#           searchobj = re.compile(search, re.IGNORECASE)
#           for each in os.listdir('.'):
#               if searchobj.match(each):
#                   print 'found', each
    if ast.asn1_filenames:
        # Parse ASN.1 files before the rest of the system
        try:
            set_global_DV(ast.asn1_filenames)
        except TypeError as err:
            errors.append(str(err))

    ast.asn1Modules = DV.asn1Modules
    ref_p_with_fpar = []

    for child in systems:
        system, err, warn = system_definition(child, parent=ast)
        errors.extend(err)
        warnings.extend(warn)
        ast.systems.append(system)

        def find_processes(block):
            ''' Recursively find non-referenced processes in a system '''
            try:
                non_ref_processes = [proc for proc in block.processes
                                     if not proc.referenced]
                process_types = block.process_types
            except AttributeError:
                non_ref_processes, process_types = [], []
            for nested in block.blocks:
                add_p, add_t = find_processes(nested)
                non_ref_processes.extend(add_p)
                process_types.extend(add_t)
            return non_ref_processes, process_types
        non_ref_p, p_types = find_processes(system)

        def find_ref_processes_with_fpar(block):
            ''' Recursively find referenced processes having FPAR '''
            # They may contain FPAR sections that must not be lost...
            try:
                ref_processes = [proc for proc in block.processes
                        if proc.referenced and proc.fpar]
            except AttributeError:
                ref_processes = []
            for nested in block.blocks:
                add_p = find_ref_processes_with_fpar(nested)
                ref_processes.extend(add_p)
            return ref_processes
        ref_p_with_fpar = find_ref_processes_with_fpar(system)

        ast.processes.extend(non_ref_p)
        ast.process_types.extend(p_types)
    for child in processes:
        # process definition at root level (can be a process type)
        # parse the process name to find the scope in which it is declared
        for node in child.getChildren():
            if node.type == lexer.ID:
                processName = node.text
        def rec_find_process_parent(block, proc_name : str):
            # to define the parent of the process, find the block where it is
            # specified with a "referenced" flag.
            res = None
            for nested in block.blocks:
                res = rec_find_process_parent(nested, proc_name)
                if res:
                    return nested
            if isinstance(block, ogAST.Block):
                for proc in block.processes:
                    if proc.processName.lower() == proc_name.lower():
                        return block
            return None
        proc_parent = None
        for system in ast.systems:
            proc_parent = rec_find_process_parent(system, processName)
            if proc_parent:
                break
        process, err, warn = process_definition(child, parent=proc_parent or ast)
        # check if the process was declared as referenced with FPAR
        for each in ref_p_with_fpar:
            if each.processName == process.processName:
                process.fpar = each.fpar
        ast.processes.append(process)
        process.dataview = types()
        process.asn1Modules = ast.asn1Modules
        process.dv = DV
        errors.extend(err)
        warnings.extend(warn)
    # Check that process instance/types match
    process_instances = []
    process_types     = []
    to_be_deleted     = []
    for each in ast.processes:
        if each.instance_of_name is not None or not each.process_type:
            # standalone process or instance of a process type
            process_instances.append(each)
        elif each.process_type:
            process_types.append(each)
            ast.process_types.append(each)
    for each in process_instances:
        if each.instance_of_name is not None:
            # Find corresponding process type definition
            for p_type in process_types:
                if p_type.processName.lower() == each.instance_of_name.lower():
                    each.instance_of_ref = p_type
                    to_be_deleted.append(p_type)
                    break
            else:
                warnings.append('"{}" PROCESS TYPE definition not found'
                                .format(each.instance_of_name))
    for each in to_be_deleted:
        ast.processes.remove(each)
        process_types.remove(each)
    for each in process_types:
        ast.processes.remove(each)
        warnings.append('No instance of PROCESS TYPE "{}" found'
                        .format(each.processName))

    # Since SDL type declarations are injected in ASN.1 ast,
    # The ASN.1 ASTs needs to be copied at the end of PR parsing process
    # and not just after the ASN1 specific parsing
    ast.dataview = types()
    ast.asn1_constants = DV.variables
    ast.DV = DV
    return ast, errors, warnings


def add_to_ast(ast, filename=None, string=None):
    ''' Parse a file or string and add it to an AST '''
    errors, warnings = [], []
    try:
        parser = parser_init(filename=filename, string=string)
    except IOError as err:
        LOG.error('Parser initialization error: ' + str(err))
        raise
    tree_rule_return_scope = parser.pr_file()
    for each in parser.error_list:
        LOG.error(each)
    for each in lexer.sdl92Lexer.error_list:
        LOG.error(each)
    # Root of the AST is of type antlr3.tree.CommonTree
    # Add it as a child of the common tree
    subtree = tree_rule_return_scope.tree
    check_syntax(node=subtree, recursive=True, filename=filename or "")
    token_str = parser.getTokenStream()
    children_before = set(ast.children)
    # addChild does not simply add the subtree - it flattens it if necessary
    # this means that possibly SEVERAL subtrees can be added. We must set
    # the token_stream reference to all of them.
    ast.addChild(subtree)
    for tree in set(ast.children) - children_before:
        tree.token_stream = token_str
    return errors, warnings


def parse_pr(files=None, string=None):
    ''' Parse SDL files (.pr) and/or string '''
    warnings = []
    errors = []
    files = files or []
    # define a common tree to combine several PR inputs
    common_tree = antlr3.tree.CommonTree(None)
    for filename in files:
        sys.path.insert(0, os.path.dirname(filename))
    try:
        for filename in files:
            err, warn = add_to_ast(common_tree, filename=filename)
            errors.extend(err)
            warnings.extend(warn)
        if string:
            err, warn = add_to_ast(common_tree, string=string)
            errors.extend(err)
            warnings.extend(warn)
    except SyntaxError as err:
        if err.filename:
            msg = f"{err.filename}:{err.lineno}:{err.offset} Syntax error"\
                  f"\n{err.text}"
        else:
            msg=f"Syntax error\n{str(err)}"
        errors.append([msg,
                      [0, 0],
                      ['- -']])

    # If syntax errors were found, raise an alarm and try to continue anyway
    if errors:
        errors.append(['You should fix the syntax errors to make sure '
            'no information is lost when loading the model', [0, 0], ['- -']])
        #og_ast = ogAST.AST()

    # At the end when common tree is complete, perform the parsing
    og_ast, err, warn = pr_file(common_tree)
    for error in err:
        errors.append([error] if type(error) is not list else error)
    for warning in warn:
        warnings.append([warning]
                        if type(warning) is not list else warning)
    # Post-parsing: additional semantic checks
    # check that all NEXTSTATEs have a correspondingly defined STATE
    # (except the '-' state, which means "stay in the same state' and
    # the '-*' (history nextstate) that recovers parallel states
    for process in og_ast.processes:
        for t in process.terminators:
            if t.kind != 'next_state':
                continue
            ns = t.instance_of or t.inputString.lower()
            if not ns in [s.lower() for s in process.mapping.keys()] + ['-', '-*']:
                t_x, t_y = t.pos_x or 0, t.pos_y or 0
                msg = 'State definition missing: ' + ns.upper()
                errors.append([msg,[t_x, t_y], ['PROCESS {}'.format(process.processName)]])
                process.errors.append(msg)
        # TODO: do the same with JOIN/LABEL

        # Check that all floating state instances (foo:bar) have a corresponding
        # nested state defined.
        state_types = set(st.instance_of.lower()
                for st in process.content.states if st.instance_of)
        comp_states = set(comp.statename.lower()
                for comp in process.composite_states)
        for missing in state_types - comp_states:
            errors.append([f'Nested state definition missing : {missing}',
                [0, 0],
                ['PROCESS {}'.format(process.processName)]])
    return og_ast, warnings, errors


def n7s_scl_always(root, parent, context=None):
    errors, warnings = [], []
    return root, errors, warnings


def n7s_scl_never(root, parent, context=None):
    errors, warnings = [], []
    return root, errors, warnings


def n7s_scl_eventually(root, parent, context=None):
    errors, warnings = [], []
    return root, errors, warnings


def n7s_scl_filter_out(root, parent, context=None):
    errors, warnings = [], []
    return root, errors, warnings


def n7s_scl(root, parent, context=None):
    expressions, errors, warnings = [], [], []
    for each in root.getChildren():
        if each.type == lexer.ALWAYS:
            expr, err, warn = n7s_scl_always(each, parent, context)
            expressions.append(expr)
            errors.append(err)
            warnings.append(warn)
        elif each.type == lexer.NEVER:
            expr, err, warn = n7s_scl_never(each, parent, context)
            expressions.append(expr)
            errors.append(err)
            warnings.append(warn)
        elif each.type == lexer.EVENTUALLY:
            expr, err, warn = n7s_scl_eventually(each, parent, context)
            expressions.append(expr)
            errors.append(err)
            warnings.append(warn)
        elif each.type == lexer.FILTER_OUT:
            expr, err, warn = n7s_scl_eventually(each, parent, context)
            expressions.append(expr)
            errors.append(err)
            warnings.append(warn)
    errors = [[e, [0, 0], []] for e in errors]
    warnings = [[w, [0, 0], []] for w in warnings]
    return expressions, errors, warnings


def parseSingleElement(elem:str='', string:str='', context=None):
    '''
        Parse any symbol and return syntax error and AST entry
        Used for on-the-fly checks when user edits text
        and for copy/cut to create a new object
    '''
    assert(elem in
            ('input_part',
             'output',
             'decision',
             'alternative_part',
             'terminator_statement',
             'label',
             'task',
             'procedure_call',
             'end',
             'text_area',
             'state',
             'start',
             'procedure',
             'floating_label',
             'connect_part',
             'process_definition',
             'proc_start',
             'state_start',
             'signalroute',
             'stop_if',
             'continuous_signal',
             'composite_state',
             'n7s_scl'))
    # Create a dummy context, needed to place context data
    if elem == 'proc_start':
        elem = 'start'
        context = ogAST.Procedure()
    elif elem == 'state_start':
        elem = 'start'
        context = ogAST.CompositeState()
    else:
        context = context or ogAST.Process()
    context.path = ['PROCESS og']  # Set a dummy context for syntax check
    LOG.debug('Parsing string: ' + string + ' with elem ' + elem)

    # some syntax errors are only displayed on screen by ANTLR and never
    # reported otherwise. Override the function to collect the messages
    def catchErrors(self, e):
        # Overriding the function from recognizers.py
        if self._state.errorRecovery:
            return

        self._state.syntaxErrors += 1 # don't count spurious
        self._state.errorRecovery = True

        hdr = self.getErrorHeader(e)
        msg = self.getErrorMessage(e)
        self._state.syntaxErrorMsgs.append(f"{hdr} {msg}")
        #super(sdl92Parser.sdl92Parser, self).reportError(e)

    parser = parser_init(string=string)
    parser.reportError = partial(catchErrors, parser)
    parser._state.syntaxErrorMsgs = []

    parser_ptr = getattr(parser, elem)
    assert parser_ptr is not None
    syntax_errors = []
    semantic_errors = []
    warnings = []
    t = None
    if parser:
        # we get there twice in a row, both from focusOutEvent:
        # first by the call to check_syntax
        # then by the call to update_completion_list
        # this could be improved..
        #print (traceback.print_stack())
        r = parser_ptr()
        # Get the root of the Antlr-AST to build our own AST entry
        root = r.tree
        #print (isinstance(tree, antlr3.tree.CommonErrorNode))
        root.token_stream = parser.getTokenStream()
        backend_ptr = eval(elem)
        try:
            check_syntax(node=root, recursive=True, input_string=string)
            t, semantic_errors, warnings = backend_ptr(
                                root=root, parent=None, context=context)
        except AttributeError as err:
            # When this happens, it's a good idea to debug...
            print (">>", str(err))
            # print (traceback.format_exc())
            # Syntax checker has no visibility on variables and types
            # so we have to discard exceptions sent by e.g. find_variable
            pass
        except NotImplementedError as err:
            syntax_errors.append('Expression syntax not supported.')
        except SyntaxError as err:
            syntax_errors.append(err.text)
        # Check that the whole string has been consumed (ANTLR may stop parsing
        # after the last expected token, leaving invisible syntax errors)
        moreToken = parser.getTokenStream().LT(1).start
        if moreToken != None and moreToken < len(string):
            syntax_errors.append (f"Issue at character {moreToken}:"
                    f" {string[moreToken]}")
        # Add syntax errors from ANTLR recognizer
        if parser._state.syntaxErrors:
            syntax_errors.extend(parser._state.syntaxErrorMsgs)
    return(t, syntax_errors, semantic_errors, warnings,
            context.terminators)


def parser_init(filename=None, string=None):
    ''' Initialize the parser (to be called first) '''
    if filename is not None:
        try:
            # encoding not available in python3 runtime, seems to default ok
            char_stream = antlr3.ANTLRFileStream(filename) #, encoding='utf-8')
        except (IOError, TypeError) as err:
            LOG.debug(str(traceback.format_exc()))
            raise
    if string is not None:
        try:
            char_stream = antlr3.ANTLRStringStream(string)
        except TypeError as err:
            raise IOError('String parsing error: ' + str(err))
    lex = lexer.sdl92Lexer(char_stream)
    tokens = antlr3.CommonTokenStream(lex)
    parser = sdl92Parser.sdl92Parser(tokens)
    # bug in the antlr3.5 runtime for python3 - attribute "error_list"
    # is missing - we have to add it manually here
    parser.error_list=[]
    lexer.sdl92Lexer.error_list=[]
    return parser


if __name__ == '__main__':
    print ('This module is not callable')
