#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    OpenGEODE SDL92 parser

    This library builds the SDL AST (described in ogAST.py)
    The AST can then be used to build SDL backends such as the
    diagram editor (placing symbols in a graphical canvas for editition)
    or code generators, etc.

    The AST build is based on the ANTLR-grammar and generated lexer and parser
    (the grammar is in the file sdl92.g and requires antlr 3.1.3 for Python
    to be compiled and used).

    During the build of the AST this library makes a number of semantic
    checks on the SDL input mode.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__author__ = 'Maxime Perrotin'

import sys
import os
import math
import logging
import traceback
import binascii
from itertools import chain, permutations, combinations
from collections import defaultdict, Counter
import antlr3
import antlr3.tree

import sdl92Lexer as lexer
from sdl92Parser import sdl92Parser

import samnmax
import ogAST
from Asn1scc import parse_asn1, ASN1

LOG = logging.getLogger(__name__)

EXPR_NODE = {
    lexer.PLUS: ogAST.ExprPlus,
    lexer.ASTERISK: ogAST.ExprMul,
    lexer.IMPLIES: ogAST.ExprImplies,
    lexer.DASH: ogAST.ExprMinus,
    lexer.OR: ogAST.ExprOr,
    lexer.AND: ogAST.ExprAnd,
    lexer.XOR: ogAST.ExprXor,
    lexer.EQ: ogAST.ExprEq,
    lexer.NEQ: ogAST.ExprNeq,
    lexer.GT: ogAST.ExprGt,
    lexer.GE: ogAST.ExprGe,
    lexer.LT: ogAST.ExprLt,
    lexer.LE: ogAST.ExprLe,
    lexer.DIV: ogAST.ExprDiv,
    lexer.MOD: ogAST.ExprMod,
    lexer.APPEND: ogAST.ExprAppend,
    lexer.IN: ogAST.ExprIn,
    lexer.REM: ogAST.ExprRem,
    lexer.NOT: ogAST.ExprNot,
    lexer.NEG: ogAST.ExprNeg,
    lexer.PRIMARY: ogAST.Primary,
}

# Insert current path in the search list for importing modules
sys.path.insert(0, '.')

DV = None

# Code generator backends may need some intemediate variables to process
# expressions. For convenience and to avoid multiple pass parsing, the parser
# tries to guess where they may be useful, and adds a hint in the AST.
TMPVAR = 0

# ASN.1 types used to support the signature of special operators
INTEGER = type('IntegerType', (object,), {'kind': 'IntegerType',
                                          'Min': str(-(2 ** 63)),
                                          'Max': str(2 ** 63 - 1)})
INT32 = type('Integer32Type', (object,), {'kind': 'Integer32Type',
                                          'Min': '-2147483648',
                                          'Max': '2147483647'})
NUMERICAL = type('NumericalType', (object,), {'kind': 'Numerical'})
TIMER = type('TimerType', (object,), {'kind': 'TimerType'})
REAL = type('RealType', (object,), {'kind': 'RealType',
                                    'Min': str(1e-308),
                                    'Max': str(1e308)})
LIST = type('ListType', (object,), {'kind': 'ListType'})
ANY_TYPE = type('AnyType', (object,), {'kind': 'AnyType'})
CHOICE = type('ChoiceType', (object,), {'kind': 'ChoiceType'})
BOOLEAN = type('BooleanType', (object,), {'kind': 'BooleanType'})
RAWSTRING = type('RawString', (object,), {'kind': 'StandardStringType',
                                          'Min': '0', 'Max': '255'})
OCTETSTRING = type('OctetString', (object,), {'kind': 'OctetStringType'})
ENUMERATED = type('EnumeratedType', (object,), {'kind': 'EnumeratedType'})

UNKNOWN_TYPE = type('UnknownType', (object,), {'kind': 'UnknownType'})

SPECIAL_OPERATORS = {
    'abs': [{'type': NUMERICAL, 'direction': 'in'}],
    'ceil': [{'type': REAL, 'direction': 'in'}],
    'cos': [{'type': REAL, 'direction': 'in'}],
    'fix': [{'type': NUMERICAL, 'direction': 'in'}],
    'float': [{'type': NUMERICAL, 'direction': 'in'}],
    'floor': [{'type': REAL, 'direction': 'in'}],
    'length': [{'type': LIST, 'direction': 'in'}],
    'num': [{'type': ENUMERATED, 'direction': 'in'}],
    'power': [
        {'type': NUMERICAL, 'direction': 'in'},
        {'type': INTEGER, 'direction': 'in'}
    ],
    'present': [{'type': CHOICE, 'direction': 'in'}],
    'reset_timer': [{'type': TIMER, 'direction': 'in'}],
    'round': [{'type': REAL, 'direction': 'in'}],
    'set_timer': [
        {'type': INTEGER, 'direction': 'in'},
        {'type': TIMER, 'direction': 'in'}
    ],
    'sin': [{'type': REAL, 'direction': 'in'}],
    'sqrt': [{'type': REAL, 'direction': 'in'}],
    'trunc': [{'type': REAL, 'direction': 'in'}],
    'write': [{'type': ANY_TYPE, 'direction': 'in'}],
    'writeln': [{'type': ANY_TYPE, 'direction': 'in'}],
}

# Container to keep a list of types mapped from ANTLR Tokens
# (Used with singledispatch/visitor pattern)
ANTLR_TOKEN_TYPES = {a: type(a, (antlr3.tree.CommonTree,), {})
                    for a, b in lexer.__dict__.viewitems() if type(b) == int}


# Shortcut to create a new referenced ASN.1 type
new_ref_type = lambda refname: \
        type(str(refname), (object,),
                {'kind': 'ReferenceType',
                 'ReferencedTypeName': refname.replace('_', '-')})

# Shortcut to return a type name (Reference name or basic type)
type_name = lambda t: \
                t.kind if t.kind != 'ReferenceType' else t.ReferencedTypeName

types = lambda: getattr(DV, 'types', {})


def set_global_DV(asn1_filenames):
    ''' Call ASN.1 parser and set the global dataview AST entry (DV) '''
    global DV
    if '--toC' in sys.argv:
        rename_policy = ASN1.RenameOnlyConflicting
    else:
        rename_policy = ASN1.NoRename
    try:
        DV = parse_asn1(tuple(asn1_filenames),
                        ast_version=ASN1.UniqueEnumeratedNames,
                        rename_policy=rename_policy,
                        flags=[ASN1.AstOnly])
    except (ImportError, NameError) as err:
        # Can happen if DataView.py is not there
        LOG.error('Error loading ASN.1 model')
        LOG.debug(str(err))
    except TypeError as err:
        LOG.debug(traceback.format_exc())
        raise TypeError('ASN.1 compiler failed - {}'.format(str(err)))


def substring_range(substring):
    ''' Return the range of a substring '''
    left, right = substring.value[1]['substring']
    left_bty = find_basic_type(left.exprType)
    right_bty = find_basic_type(right.exprType)
    return left_bty.Min, right_bty.Max


def is_integer(ty):
    ''' Return true if a type is an Integer Type '''
    return find_basic_type(ty).kind in (
        'IntegerType',
        'Integer32Type'
    )


def is_real(ty):
    ''' Return true if a type is a Real Type '''
    return find_basic_type(ty).kind == 'RealType'


def is_numeric(ty):
    ''' Return true if a type is a Numeric Type '''
    return find_basic_type(ty).kind in (
        'IntegerType',
        'Integer32Type',
        'Numerical',
        'RealType'
    )


def is_boolean(ty):
    ''' Return true if a type is a Boolean Type '''
    return find_basic_type(ty).kind == 'BooleanType'


def is_null(ty):
    ''' Return true if a type is a NULL Type '''
    return find_basic_type(ty).kind == 'NullType'


def is_string(ty):
    ''' Return true if a type is a String Type '''
    return find_basic_type(ty).kind in (
        'StandardStringType',
        'OctetStringType',
        'StringType'
    )


def is_sequenceof(ty):
    ''' Return true if a type is a SequenceOf Type '''
    return find_basic_type(ty).kind == 'SequenceOfType'


def is_list(ty):
    ''' Return true if a type is a List Type '''
    return is_string(ty) or is_sequenceof(ty) or ty == LIST


def is_enumerated(ty):
    ''' Return true if a type is an Enumerated Type '''
    return find_basic_type(ty).kind == 'EnumeratedType' or ty == ENUMERATED


def is_sequence(ty):
    ''' Return true if a type is a Sequence Type '''
    return find_basic_type(ty).kind == 'SequenceType'


def is_choice(ty):
    ''' Return true if a type is a Choice Type '''
    return find_basic_type(ty).kind == 'ChoiceType' or ty == CHOICE


def is_timer(ty):
    ''' Return true if a type is a Timer Type '''
    return find_basic_type(ty).kind == 'TimerType'


def sdl_to_asn1(sort):
    '''
        Convert case insensitive type reference to the actual type as found
        in the ASN.1 datamodel
    '''
    for asn1_type in types().viewkeys():
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
            if process.processName == process_name:
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
        yield out_sig['name'].lower()
    for proc in scope.procedures:
        yield proc.inputString.lower()
    for special_op in SPECIAL_OPERATORS:
        yield special_op.lower()


def get_interfaces(ast, process_name):
    '''
        Search for the list of input and output signals (async PI/RI)
        and procedures (sync RI) of a process in a given top-level AST
    '''
    all_signals, async_signals, errors = [], [], set()
    system = None

    # Move up to the system level, in case process is nested in a block
    # and not defined at root level as it is the case when it is referenced
    system = ast
    while hasattr(system, 'parent'):
        system = system.parent

    # If we are at AST level, check in all systems, otherwise in current one
    iterator = ast.systems if hasattr(ast, 'systems') else (system,)

    for system in iterator:
        all_signals.extend(signals_in_system(system))
        process_ref = find_process_declaration(system, process_name)
        if process_ref:
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
    return token_stream(root).toString(root.getTokenStartIndex(),
            root.getTokenStopIndex())


def error(root, msg):
    ''' Return an error message '''
    return '{} - "{}"'.format(msg, get_input_string(root))


def warning(root, msg):
    ''' Return a warning message '''
    return '{} - "{}"'.format(msg, get_input_string(root))


def tmp():
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
        # Find type with proper case in the data view
        for typename in pool.viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = pool[typename].type
                break
        else:
            raise TypeError('Type "' + type_name(basic_type) +
                            '" was not found in Dataview')
    return basic_type


def signature(name, context):
    ''' Return the signature of a procecure/output/operator '''
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
                    'name': out_sig.get('param_name' or ''),
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
        returning the type of its result '''

    # Special case for write/writeln functions
    if name.lower() in ('write', 'writeln'):
        for p in params:
            p_ty = p.exprType
            if is_numeric(p_ty) or is_boolean(p_ty) or is_string(p_ty) or \
                    is_enumerated(p_ty):
                continue
            raise TypeError('Type {} not supported in call to {}'.
                format(type_name(p.exprType), name))
        return

    # (1) Find the signature of the function
    # signature will hold the list of parameters for the function
    sign = signature(name, context)

    # (2) Check that the number of given parameters matches the signature
    if len(sign) != len(params):
        raise TypeError('Expected {} arguments in call to {} ({} received)'.
            format(len(sign), name, len(params)))

    # (3) Check each individual parameter type
    for idx, param in enumerate(params):
        expr = ogAST.ExprAssign()
        expr.left = ogAST.PrimVariable()
        expr.left.exprType = sign[idx]['type']
        expr.right = param

        try:
            fix_expression_types(expr, context)
            params[idx] = expr.right
        except TypeError:
            expected = type_name(sign[idx]['type'])
            received = type_name(expr.right.exprType)
            raise TypeError('Expected type {} in call to {} ({} received)'.
                format(expected, name, received))

        if sign[idx].get('direction') != 'in' \
                and not isinstance(expr.right, ogAST.PrimVariable):
            raise TypeError('OUT parameter "{}" is not a variable'
                .format(expr.right.inputString))

    # (4) Compute the type of the result
    param_btys = [find_basic_type(p.exprType) for p in params]
    if name == 'abs':
        return type('Abs', (param_btys[0],), {
            'Min': str(max(float(param_btys[0].Min), 0)),
            'Max': str(max(float(param_btys[0].Max), 0))
        })

    elif name == 'ceil':
        return type('Ceil', (REAL,), {
            'Min': str(math.ceil(float(param_btys[0].Min))),
            'Max': str(math.ceil(float(param_btys[0].Max)))
        })

    elif name == 'cos':
        return type('Cos', (REAL,), {
            'Min': str(-1.0),
            'Max': str(1.0)
        })

    elif name == 'fix':
        return type('Fix', (INTEGER,), {
            'Min': param_btys[0].Min,
            'Max': param_btys[0].Max
        })

    elif name == 'float':
        return type('Float', (REAL,), {
            'Min': param_btys[0].Min,
            'Max': param_btys[0].Max
        })

    elif name == 'floor':
        return type('Floor', (REAL,), {
            'Min': str(math.floor(float(param_btys[0].Min))),
            'Max': str(math.floor(float(param_btys[0].Max)))
        })

    elif name == 'length':
        return type('Length', (INT32,), {
            'Min': param_btys[0].Min,
            'Max': param_btys[0].Max
        })

    elif name == 'num':
        enum_values = [int(each.IntValue)
                       for each in param_btys[0].EnumValues.viewvalues()]

        return type('Num', (INTEGER,), {
            'Min': str(min(enum_values)),
            'Max': str(max(enum_values))
        })

    elif name == 'power':
        return type('Power', (param_btys[0],), {
            'Min': str(pow(float(param_btys[0].Min),
                           float(param_btys[1].Min))),
            'Max': str(pow(float(param_btys[0].Max),
                           float(param_btys[1].Max)))
        })

    elif name == 'present':
        return type('Present', (object,), {
            'kind': 'ChoiceEnumeratedType',
            'EnumValues': param_btys[0].Children
        })

    elif name == 'round':
        return type('Round', (REAL,), {
            'Min': str(round(float(param_btys[0].Min))),
            'Max': str(round(float(param_btys[0].Max)))
        })

    elif name == 'sin':
        return type('Sin', (REAL,), {
            'Min': str(-1.0),
            'Max': str(1.0)
        })

    elif name == 'sqrt':
        return type('Sqrt', (REAL,), {
            'Min': str(0.0),
            'Max': str(math.sqrt(float(param_btys[0].Max)))
        })

    elif name == 'trunc':
        return type('Trunc', (REAL,), {
            'Min': str(math.trunc(float(param_btys[0].Min))),
            'Max': str(math.trunc(float(param_btys[0].Max)))
        })

    else:
        # check if procedure is declared to return a type
        for inner_proc in context.procedures:
            proc_name = inner_proc.inputString
            if proc_name.lower() == name.lower() and inner_proc.return_type:
                return inner_proc.return_type

    return UNKNOWN_TYPE


def check_range(typeref, type_to_check):
    ''' Verify the that the Min/Max bounds of two types are compatible
        Called to test that assignments are withing allowed range
        both types assumed to be basic types
    '''
    try:
        if float(type_to_check.Min) < float(typeref.Min) \
                or float(type_to_check.Max) > float(typeref.Max):
            raise Warning('Expression evaluation in range [{}..{}], '
                          'could be outside expected range [{}..{}]'
                    .format(type_to_check.Min, type_to_check.Max,
                            typeref.Min, typeref.Max))
    except (AttributeError, ValueError):
        raise TypeError('Missing range')


def check_type_compatibility(primary, type_ref, context):
    '''
        Check if an ogAST.Primary (raw value, enumerated, ASN.1 Value...)
        is compatible with a given type (type_ref is an ASN1Scc type)
        Does not return anything if OK, otherwise raises TypeError
    '''
    assert type_ref is not None
    if type_ref is UNKNOWN_TYPE:
        #print traceback.print_stack()
        raise TypeError('Type reference is unknown')

    basic_type = find_basic_type(type_ref)

    if (isinstance(primary, ogAST.PrimEnumeratedValue)
            and basic_type.kind.endswith('EnumeratedType')):
        # If type ref is an enumeration, check that the value is valid
        # Note, when using the "present" operator of a CHOICE type, the
        # resulting value is actually an EnumeratedType
        enumerant = primary.inputString.replace('_', '-').lower()
        for each in basic_type.EnumValues.keys():
            if each.lower() == enumerant:
                # Found -> all OK
                return
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
                check_type_compatibility(expr, type_ref, context)
        return

    elif isinstance(primary, ogAST.PrimVariable):
        try:
            compare_types(primary.exprType, type_ref)
        except TypeError as err:
            raise TypeError('{expr} should be of type {ty} - {err}'
                            .format(expr=primary.inputString,
                                    ty=type_name(type_ref),
                                    err=str(err)))
        return

    elif isinstance(primary, ogAST.PrimInteger) \
            and (is_integer(type_ref) or type_ref == NUMERICAL):
        return

    elif isinstance(primary, ogAST.PrimReal) \
            and (is_real(type_ref) or type_ref == NUMERICAL):
        return

    elif isinstance(primary, ogAST.ExprNeg):
        check_type_compatibility(primary.expr, type_ref, context)

    elif isinstance(primary, ogAST.PrimBoolean) and is_boolean(type_ref):
        return

    elif isinstance(primary, ogAST.PrimNull) and is_null(type_ref):
        return

    elif isinstance(primary, ogAST.PrimEmptyString):
        # Empty strings ("{ }") can be used for arrays and empty records
        if basic_type.kind == 'SequenceOfType':
            if int(basic_type.Min) == 0:
                return
            else:
                raise TypeError('SEQUENCE OF has a minimum size of '
                                + basic_type.Min + ')')
        elif basic_type.kind == 'SequenceType':
            if len(basic_type.Children.keys()) > 0:
                raise TypeError('SEQUENCE is not empty, wrong "{}" syntax')
        else:
            raise TypeError('Not a type compatible with empty string syntax')
    elif isinstance(primary, ogAST.PrimSequenceOf) \
            and basic_type.kind == 'SequenceOfType':
        if type_ref.__name__ != 'Apnd' and \
                (len(primary.value) < int(basic_type.Min) or
                len(primary.value) > int(basic_type.Max)):
            raise TypeError(str(len(primary.value)) +
                      ' elements in SEQUENCE OF, while constraint is [' +
                      str(basic_type.Min) + '..' + str(basic_type.Max) + ']')
        for elem in primary.value:
            check_type_compatibility(elem, basic_type.type, context)
        if not hasattr(primary, 'expected_type') \
               and type_ref.__name__ not in ('Apnd', 'SubStr'):
            primary.expected_type = type_ref
        return
    elif isinstance(primary, ogAST.PrimSequence) \
            and basic_type.kind == 'SequenceType':
        user_nb_elem = len(primary.value.keys())
        type_nb_elem = len(basic_type.Children.keys())
        optional_fields = [field.lower().replace('-', '_')
                           for field, val in basic_type.Children.viewitems()
                           if val.Optional == 'True']
        user_fields = [field.lower() for field in primary.value.keys()]
        for field, fd_data in basic_type.Children.viewitems():
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
                    check_type_compatibility(primary.value[casefield],
                                             fd_data.type, context)
                else:
                    # Compare the types for semantic equivalence
                    try:
                        compare_types(
                            primary.value[casefield].exprType, fd_data.type)
                    except TypeError as err:
                        raise TypeError('Field ' + ufield +
                                    ' is not of the proper type, i.e. ' +
                                    type_name(fd_data.type) +
                                    ' - ' + str(err))
        return
    elif isinstance(primary, ogAST.PrimChoiceItem) \
                              and basic_type.kind.startswith('Choice'):
        for choicekey, choice in basic_type.Children.viewitems():
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
            check_type_compatibility(value, choice_field_type, context)
        # Compare the types for semantic equivalence:
        else:
            try:
                compare_types(value.exprType, choice_field_type)
            except TypeError as err:
                raise TypeError(
                            'Field {field} in CHOICE is not of type {t1} - {e}'
                            .format(field=primary.value['choice'],
                                    t1=type_name(choice_field_type),
                                    e=str(err)))
        value.exprType = choice_field_type         # XXX
        return
    elif isinstance(primary, ogAST.PrimChoiceDeterminant) \
                and basic_type.kind.startswith('Choice'):
        for choicekey, choice in basic_type.EnumValues.viewitems():
            if choicekey.replace('-', '_').lower() == \
                    primary.inputString.lower():
                break
        else:
            raise TypeError('Non-existent choice "{choice}" in type {t1}'
                            .format(choice=primary.inputString,
                            t1=type_name(type_ref)))

    elif isinstance(primary, ogAST.PrimStringLiteral):
        # Octet strings
        basic_type = find_basic_type(type_ref)
        if basic_type.kind == 'StandardStringType':
            return
        elif basic_type.kind.endswith('StringType'):
            try:
                if int(basic_type.Min) <= len(
                        primary.value[1:-1]) <= int(basic_type.Max):
                    return
                else:
                    raise TypeError('Invalid string literal'
                                    ' - check that length is'
                                    'within the bound limits {Min}..{Max}'
                                    .format(Min=str(basic_type.Min),
                                            Max=str(basic_type.Max)))
            except ValueError:
                # No size constraint (or MIN/MAX)
                LOG.debug('String literal size constraint discarded')
                return
        else:
            raise TypeError('String literal not expected')
    elif (isinstance(primary, ogAST.PrimMantissaBaseExp) and
                                            basic_type.kind == 'RealType'):
        LOG.debug('PROBABLY (it is a float but I did not check'
                  'if values are compatible)')
        return
    else:
        raise TypeError('{prim} does not match type {t1}'
                        .format(prim=primary.inputString,
                                t1=type_name(type_ref)))


def compare_types(type_a, type_b):
    '''
       Compare two types, return if they are semantically equivalent,
       otherwise raise TypeError
    '''

    type_a = find_basic_type(type_a)
    type_b = find_basic_type(type_b)

    if type_a == type_b:
        return
    elif NUMERICAL in (type_a, type_b) and is_numeric(type_a) \
            and is_numeric(type_b):
        return
    elif LIST in (type_a, type_b) and is_list(type_a) and is_list(type_b):
        return
    elif ENUMERATED in (type_a, type_b) and is_enumerated(type_a) \
            and is_enumerated(type_b):
        return
    elif CHOICE in (type_a, type_b) and is_choice(type_a) and is_choice(type_b):
        return

    # Check if both types have basic compatibility

    if type_a.kind == type_b.kind:
        if type_a.kind == 'SequenceOfType':
            if type_a.Min == type_a.Max:
                if type_a.Min == type_b.Min == type_b.Max:
                    compare_types(type_a.type, type_b.type)
                    return
                else:
                    raise TypeError('Incompatible sizes - size of {} can vary'
                                    .format(type_name(type_b)))
            elif(int(type_b.Min) >= int(type_a.Min)
                 and int(type_b.Max) <= int(type_a.Max)):
                compare_types(type_a.type, type_b.type)
                return
            else:
                compare_types(type_a.type, type_b.type)
                raise Warning('Size constraints mismatch - risk of overflow')
        # TODO: Check that OctetString types have compatible range
        return
    elif is_string(type_a) and is_string(type_b):
        return
    elif is_integer(type_a) and is_integer(type_b):
        return
    elif is_real(type_a) and is_real(type_b):
        return
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

    # First check locally, i.e. in FPAR
    try:
        for variable in context.fpar:
            if variable['name'].lower() == var.lower():
                return variable['type']
    except AttributeError:
        # No FPAR section
        pass

    for varname, (vartype, _) in all_visible_variables.viewitems():
        # Case insensitive comparison with variables
        if var.lower() == varname.lower():
            return vartype

    for timer in chain(context.timers, context.global_timers):
        if var.lower() == timer.lower():
            return TIMER

    # check if is a ASN.1 constant
    for varname, vartype in DV.variables.viewitems():
        if var.lower() == varname.lower().replace('-', '_'):
            return vartype.type

    raise AttributeError('Variable {var} not defined'.format(var=var))


def fix_enumerated_and_choice(expr_enum, context):
    ''' If left side of the expression is of Enumerated or Choice type,
        check if right side is a literal of that sort, and update type '''
    kind = find_basic_type(expr_enum.left.exprType).kind
    if kind in ('EnumeratedType', 'StateEnumeratedType'):
        prim = ogAST.PrimEnumeratedValue(primary=expr_enum.right)
    elif kind == 'ChoiceEnumeratedType':
        prim = ogAST.PrimChoiceDeterminant(primary=expr_enum.right)
    try:
        check_type_compatibility(prim, expr_enum.left.exprType, context)
        expr_enum.right = prim
        expr_enum.right.exprType = expr_enum.left.exprType
    except (UnboundLocalError, AttributeError, TypeError):
        pass


def fix_expression_types(expr, context):
    ''' Check/ensure type consistency in binary expressions '''
    for _ in range(2):
        # Check if an raw enumerated value is of a reference type
        fix_enumerated_and_choice(expr, context)
        expr.right, expr.left = expr.left, expr.right

    for side in (expr.right, expr.left):
        if side.is_raw:
            raw_expr = side
        else:
            typed_expr = side
            ref_type = typed_expr.exprType


    # If a side is a raw Sequence Of with unknown type, try to resolve it
    for side_a, side_b in permutations(('left', 'right')):
        value = getattr(expr, side_a)  # get expr.left then expr.right
        if not isinstance(value, ogAST.PrimSequenceOf):
            continue
        other = getattr(expr, side_b)  # other side
        basic = find_basic_type(value.exprType)
        if basic.kind == 'SequenceOfType' and basic.type == UNKNOWN_TYPE:
            asn_type = find_basic_type(other.exprType)
            if asn_type.kind == 'SequenceOfType':
                asn_type = asn_type.type
                for idx, elem in enumerate(value.value):
                    check_expr = ogAST.ExprAssign()
                    check_expr.left = ogAST.PrimVariable()
                    check_expr.left.exprType = asn_type
                    check_expr.right = elem
                    fix_expression_types(check_expr, context)
                    value.value[idx] = check_expr.right
            # the type of the raw PrimSequenceOf can be set now
            value.exprType.type = asn_type

    if isinstance(expr, ogAST.ExprIn):
        return

    if not expr.right.is_raw and not expr.left.is_raw:
        unknown = [uk_expr for uk_expr in expr.right, expr.left
                   if uk_expr.exprType == UNKNOWN_TYPE]
        if unknown:
            #print traceback.print_stack()
            raise TypeError('Cannot resolve type of "{}"'
                            .format(unknown[0].inputString))

    # In Sequence, Choice and SEQUENCE OF expressions,
    # we must fix missing inner types
    # (due to similarities, the following should be refactored FIXME)
    if isinstance(expr.right, ogAST.PrimSequence):
        # left side must have a known type
        asn_type = find_basic_type(expr.left.exprType)
        if asn_type.kind != 'SequenceType':
            raise TypeError('left side must be a SEQUENCE type')
        for field, fd_expr in expr.right.value.viewitems():
            if fd_expr.exprType == UNKNOWN_TYPE:
                try:
                    expected_type = asn_type.Children.get(
                            field.replace('_', '-')).type
                except AttributeError:
                    raise TypeError('Field not found: ' + field)
                check_expr = ogAST.ExprAssign()
                check_expr.left = ogAST.PrimVariable()
                check_expr.left.exprType = expected_type
                check_expr.right = fd_expr
                fix_expression_types(check_expr, context)
                # Id of fd_expr may have changed (enumerated, choice)
                expr.right.value[field] = check_expr.right
    elif isinstance(expr.right, ogAST.PrimChoiceItem):
        asn_type = find_basic_type(expr.left.exprType)
        field = expr.right.value['choice'].replace('_', '-')
        if asn_type.kind != 'ChoiceType' \
                or field.lower() not in [key.lower()
                                  for key in asn_type.Children.viewkeys()]:
            raise TypeError('Field is not valid in CHOICE:' + field)
        key, = [key for key in asn_type.Children.viewkeys()
                if key.lower() == field.lower()]
        if expr.right.value['value'].exprType == UNKNOWN_TYPE:
            try:
                expected_type = asn_type.Children.get(key).type
            except AttributeError:
                raise TypeError('Field not found in CHOICE: ' + field)
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable()
            check_expr.left.exprType = expected_type
            check_expr.right = expr.right.value['value']
            fix_expression_types(check_expr, context)
            expr.right.value['value'] = check_expr.right
    elif isinstance(expr.right, ogAST.PrimConditional):
        for det in ('then', 'else'):
            # Recursively fix possibly missing types in the expression
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable()
            check_expr.left.exprType = expr.left.exprType
            check_expr.right = expr.right.value[det]
            fix_expression_types(check_expr, context)
            expr.right.value[det] = check_expr.right
            # Set the type of "then" and "else" to the reference type:
            expr.right.value[det].exprType = expr.left.exprType

    if expr.right.is_raw != expr.left.is_raw:
        check_type_compatibility(raw_expr, ref_type, context)
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
        compare_types(expr.left.exprType, expr.right.exprType)


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

    if is_asn1constant(name):
        prim = ogAST.PrimConstant()
    elif is_fpar(name, context):
        prim = ogAST.PrimFPAR()
    else:
        prim = ogAST.PrimVariable()

    prim.value = [name]
    prim.exprType = UNKNOWN_TYPE
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
        for varname, vartype in DV.variables.viewitems():
            if varname.lower().replace('-', '_') == name:
                return True
    except AttributeError:
        # Ignore - No DV - e.g. in syntax check mode
        pass
    return False


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
    expr.left, err_left, warn_left = expression(left, context)
    expr.right, err_right, warn_right = expression(right, context)
    errors.extend(err_left)
    warnings.extend(warn_left)
    errors.extend(err_right)
    warnings.extend(warn_right)

    try:
        fix_expression_types(expr, context)
    except (AttributeError, TypeError) as err:
        errors.append(error(root, str(err)))
    except Warning as warn:
        warnings.append(warning(root, str(warn)))

    return expr, errors, warnings


def unary_expression(root, context):
    ''' Unary expression analysis '''
    ExprNode = EXPR_NODE[root.type]
    expr = ExprNode(
        get_input_string(root),
        root.getLine(),
        root.getCharPositionInLine()
    )
    expr.exprType = UNKNOWN_TYPE
    expr.tmpVar = tmp()

    expr.expr, errors, warnings = expression(root.children[0], context)

    return expr, errors, warnings


def expression(root, context):
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
        return selector_expression(root, context)
    else:
        raise NotImplementedError(sdl92Parser.tokenNames[root.type] +
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

    for bty in left_bty, right_bty:
        if shortcircuit and bty.kind != 'BooleanType':
            msg = 'Shortcircuit operators only work with type Boolean'
            errors.append(error(root, msg))
            break

        if bty.kind == 'BooleanType':
            continue
        elif bty.kind == 'BitStringType' and bty.Min == bty.Max:
            continue
        elif bty.kind == 'SequenceOfType' and bty.Min == bty.Max \
                and find_basic_type(bty.type).kind == 'BooleanType':
            continue
        else:
            msg = 'Bitwise operators only work with Booleans, ' \
                  'fixed size SequenceOf Booleans or fixed size BitStrings'
            errors.append(error(root, msg))
            break

    if left_bty.kind == right_bty.kind == 'BooleanType':
        expr.exprType = BOOLEAN
    else:
        expr.exprType = expr.left.exprType

    return expr, errors, warnings


def arithmetic_expression(root, context):
    ''' Arithmetic expression analysis '''
    expr, errors, warnings = binary_expression(root, context)

    # Expressions returning a numerical type must have their range defined
    # accordingly with the kind of opration used between operand:
    basic = find_basic_type(expr.left.exprType)
    left = find_basic_type(expr.left.exprType)
    right = find_basic_type(expr.right.exprType)
    try:
        if isinstance(expr, ogAST.ExprPlus):
            attrs = {'Min': str(float(left.Min) + float(right.Min)),
                     'Max': str(float(left.Max) + float(right.Max))}
            expr.exprType = type('Plus', (basic,), attrs)
        elif isinstance(expr, ogAST.ExprMul):
            attrs = {'Min': str(float(left.Min) * float(right.Min)),
                     'Max': str(float(left.Max) * float(right.Max))}
            expr.exprType = type('Mul', (basic,), attrs)
        elif isinstance(expr, ogAST.ExprMinus):
            attrs = {'Min': str(float(left.Min) - float(right.Max)),
                     'Max': str(float(left.Max) - float(right.Min))}
            expr.exprType = type('Minus', (basic,), attrs)
        elif isinstance(expr, ogAST.ExprDiv):
            attrs = {'Min': str(float(left.Min) / (float(right.Max) or 1)),
                     'Max': str(float(left.Max) / (float(right.Min) or 1))}
            expr.exprType = type('Div', (basic,), attrs)
        elif isinstance(expr, (ogAST.ExprMod, ogAST.ExprRem)):
            attrs = {'Min': right.Min, 'Max': right.Max}
            expr.exprType = type('Mod', (basic,), attrs)
    except (ValueError, AttributeError):
        msg = 'Check that all your numerical data types '\
              'have a range constraint'
        errors.append(error(root, msg))

    if root.type in (lexer.REM, lexer.MOD):
        for ty in (expr.left.exprType, expr.right.exprType):
            if not is_integer(ty):
                msg = 'Mod/Rem expressions can only applied to Integer types'
                errors.append(error(root, msg))
                break

    return expr, errors, warnings


def relational_expression(root, context):
    ''' Relational expression analysys '''
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
    # Left and right are reversed for IN operator
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

    try:
        compare_types(expr.right.exprType, ref_type)
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

    left = find_basic_type(expr.left.exprType)
    right = find_basic_type(expr.right.exprType)

    for bty in (left, right):
        if bty.kind != 'SequenceOfType' and not is_string(bty):
            msg = 'Append can only be applied to types SequenceOf or String'
            errors.append(error(root, msg))
            break
    else:
        attrs = {'Min': str(int(right.Min) + int(left.Min)),
                 'Max': str(int(right.Max) + int(left.Max))}
        # It is wrong to set the type as inheriting from the left side FIXME
        expr.exprType = type('Apnd', (left,), attrs)
    #expr.exprType = expr.left.exprType

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
    elif bty.kind == 'BitStringType':
        expr.exprType = expr.expr.exprType
    elif bty.kind == 'SequenceOfType' and \
            find_basic_type(bty.type).kind == 'BooleanType':
        expr.exprType = expr.expr.exprType
    else:
        msg = 'Bitwise operators only work with booleans '\
              'and arrays of booleans'
        errors.append(error(root, msg))

    return expr, errors, warnings


def neg_expression(root, context):
    ''' Negative expression analysis '''
    expr, errors, warnings = unary_expression(root, context)

    basic = find_basic_type(expr.expr.exprType)
    if not is_numeric(basic):
        msg = 'Negative expressions can only be applied to numeric types'
        errors.append(error(root, msg))
        return expr, errors, warnings

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
    expr.tmpVar = tmp()

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

    # TODO: Refactor this
    try:
        expr.left = then_expr
        expr.right = else_expr
        fix_expression_types(expr, context)
        expr.exprType = then_expr.exprType
    except (AttributeError, TypeError) as err:
        if UNKNOWN_TYPE not in (then_expr.exprType, else_expr.exprType):
            errors.append(error(root, str(err)))

    expr.value = {
        'if': if_expr,
        'then': then_expr,
        'else': else_expr,
        'tmpVar': expr.tmpVar
    }

    return expr, errors, warnings


def call_expression(root, context):
    ''' Call expression analysis '''
    errors, warnings = [], []

    if root.children[0].type == lexer.PRIMARY:
        primary = root.children[0]
        if primary.children[0].type == lexer.VARIABLE:
            variable = primary.children[0]
            ident = variable.children[0].text.lower()
            proc_list = [proc.inputString.lower()
                         for proc in context.procedures]
            if ident in (SPECIAL_OPERATORS.keys() + proc_list):
                return primary_call(root, context)

    num_params = len(root.children[1].children)

    if num_params == 1:
        return primary_index(root, context)

    elif num_params == 2:
        return primary_substring(root, context)

    else:
        node = ogAST.PrimCall()  # Use error node instead?
        node.inputString = get_input_string(root)
        node.exprType = UNKNOWN_TYPE
        errors.append(error(root, 'Wrong number of parameters'))
        return node, errors, warnings


def primary_call(root, context):
    ''' Primary call analysis '''
    node, errors, warnings = ogAST.PrimCall(), [], []

    node.exprType = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar = tmp()

    name = root.children[0].children[0].children[0].text.lower()

    params, params_errors, param_warnings = \
                                expression_list(root.children[1], context)
    errors.extend(params_errors)
    warnings.extend(param_warnings)

    node.value = [name, {'procParams': params}]

    try:
        node.exprType = check_call(name, params, context)
    except (TypeError, ValueError) as err:
        errors.append(error(root, str(err)))
    except OverflowError:
        errors.append(error(root, 'Result can exceeds 64-bits'))

    return node, errors, warnings


def primary_index(root, context):
    ''' Primary index analysis '''
    node, errors, warnings = ogAST.PrimIndex(), [], []

    node.exprType = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar = tmp()

    receiver, receiver_err, receiver_warn = \
                                expression(root.children[0], context)
    receiver_bty = find_basic_type(receiver.exprType)
    errors.extend(receiver_err)
    warnings.extend(receiver_warn)

    params, params_errors, param_warnings = \
                                expression_list(root.children[1], context)
    errors.extend(params_errors)
    warnings.extend(param_warnings)

    node.value = [receiver, {'index': params}]

    if receiver_bty.kind == 'SequenceOfType':
        # Range check
        if isinstance(receiver, ogAST.PrimSubstring):
            r_min, r_max = substring_range(receiver)
        else:
            r_min, r_max = receiver_bty.Min, receiver_bty.Max
        node.exprType = receiver_bty.type
        idx_bty = find_basic_type(params[0].exprType)
        if not is_integer(idx_bty):
            errors.append(error(root, 'Index is not an integer'))
        else:
            if float(idx_bty.Max) >= float(r_max):
                errors.append(error(root,
                                    'Index range [{id1} .. {id2}] '
                                    'outside of range [{r1} .. {r2}]'
                                    .format(id1=idx_bty.Min, id2=idx_bty.Max,
                                        r1=int(r_min) - 1,
                                        r2=int(r_max) - 1)))
            elif float(idx_bty.Min) > float(r_min):
                warnings.append(warning(root,
                                        'Index higher than range min value'))
    else:
        msg = 'Index can only be applied to type SequenceOf'
        errors.append(error(root, msg))

    return node, errors, warnings


def primary_substring(root, context):
    ''' Primary substring analysis '''
    node, errors, warnings = ogAST.PrimSubstring(), [], []

    node.exprType = UNKNOWN_TYPE
    node.inputString = get_input_string(root)
    node.tmpVar = tmp()

    receiver, receiver_err, receiver_warn = \
                                    expression(root.children[0], context)
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
        min0 = float(find_basic_type(params[0].exprType).Min)
        min1 = float(find_basic_type(params[1].exprType).Min)
        max0 = float(find_basic_type(params[0].exprType).Max)
        max1 = float(find_basic_type(params[1].exprType).Max)
        node.exprType = type('SubStr', (receiver_bty,),
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
        if int(min0) > int(receiver_bty.Max) \
                or int(max1) > int(receiver_bty.Max):
            msg = 'Substring bounds [{}..{}] outside range [{}..{}]'.format(
                    min0, max1, receiver_bty.Min, receiver_bty.Max)
            errors.append(error(root, msg))
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

    receiver, receiver_err, receiver_warn = \
                                expression(root.children[0], context)
    receiver_bty = find_basic_type(receiver.exprType)
    errors.extend(receiver_err)
    warnings.extend(receiver_warn)

    field_name = root.children[1].text.replace('_', '-').lower()
    try:
        if receiver_bty.kind == 'ChoiceType' and pos == "left":
            # Error if this is the left part of an assignment
            errors.append(warning(root, 'Choice assignment: '
                                      'use "var := {field}: value" instead of '
                                      '"var!{field} := value"'
                                      .format(field=field_name)))
        for n, f in receiver_bty.Children.viewitems():
            if n.lower() == field_name:
                node.exprType = f.type
                break
        else:
            msg = 'Field "{}" not found in expression {}'.format(field_name,
                    receiver.inputString)
            errors.append(error(root, msg))
    except AttributeError:
        # When parsing for syntax or copy-paste, receiver_bty may
        # not be found
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
        prim.exprType = type('PrInt', (object,), {
            'kind': 'IntegerType',
            'Min': root.text,
            'Max': root.text
        })
    elif root.type in (lexer.TRUE, lexer.FALSE):
        prim = ogAST.PrimBoolean()
        prim.value = [root.text.lower()]
        prim.exprType = type('PrBool', (object,), {'kind': 'BooleanType'})
    elif root.type == lexer.NULL:
        prim = ogAST.PrimNull()
        prim.value = [root.text.lower()]
        prim.exprType = type('PrNull', (object,), {'kind': 'NullType'})
    elif root.type == lexer.FLOAT:
        prim = ogAST.PrimReal()
        prim.value = [root.text]
        prim.exprType = type('PrReal', (object,), {
            'kind': 'RealType',
            'Min': prim.value[0],
            'Max': prim.value[0]
        })
    elif root.type == lexer.STRING:
        prim = ogAST.PrimStringLiteral()
        if root.text[-1] in ('B', 'b'):
            try:
                prim.value = "'{}'".format(
                        binascii.unhexlify('%x' % int(root.text[1:-2], 2)))
            except (ValueError, TypeError) as err:
                errors.append(error
                        (root, 'Bit string literal: {}'.format(err)))
                prim.value = "''"
        elif root.text[-1] in ('H', 'h'):
            try:
                prim.value = "'{}'".format(root.text[1:-2].decode('hex'))
            except (ValueError, TypeError) as err:
                errors.append(error
                        (root, 'Octet string literal: {}'.format(err)))
                prim.value = "''"
        else:
            prim.value = root.text
        prim.exprType = type('PrStr', (object,), {
            'kind': 'StringType',
            'Min': str(len(prim.value) - 2),
            'Max': str(len(prim.value) - 2)
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
        prim.exprType = type('PrES', (object,), {
            'kind': 'SequenceOfType',
            'Min': '0',
            'Max': '0'
        })
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
                prim.value[field_name], err, warn = (expression(elem, context))
                errors.extend(err)
                warnings.extend(warn)
        prim.exprType = UNKNOWN_TYPE
    elif root.type == lexer.SEQOF:
        prim = ogAST.PrimSequenceOf()
        prim.value = []
        for elem in root.getChildren():
            # SEQUENCE OF elements cannot have fieldnames/indexes
            prim_elem, prim_elem_errors, prim_elem_warnings = \
                                                        primary(elem, context)
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
        prim.exprType = ENUMERATED()
        prim.exprType.kind = 'StateEnumeratedType'
        prim.exprType.EnumValues = {value: type('', (object,),
                                               {'EnumID': value})
                                    for value in context.mapping.viewkeys()}
    else:
        errors.append('Parsing error (token {}, line {}, "{}")'
                      .format(sdl92Parser.tokenNames[root.type],
                              root.getLine(),
                              get_input_string(root)))
        prim = ogAST.Primary()

    prim.inputString = get_input_string(root)
    prim.tmpVar = tmp()

    return prim, errors, warnings


def variables(root, ta_ast, context):
    ''' Process declarations of variables (dcl a,b Type := 5) '''
    var = []
    errors = []
    warnings = []
    asn1_sort, def_value = UNKNOWN_TYPE, None
    for child in root.getChildren():
        if child.type == lexer.ID:
            var.append(child.text)
        elif child.type == lexer.SORT:
            sort = child.getChild(0).text
            # Find corresponding type in ASN.1 model
            try:
                asn1_sort = sdl_to_asn1(sort)
            except TypeError as err:
                errors.append(error(root, str(err)))
        elif child.type == lexer.GROUND:
            # Default value for a variable - needs to be a ground expression
            def_value, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
            expr = ogAST.ExprAssign()
            expr.left = ogAST.PrimVariable()
            expr.left.inputString = var[-1]
            expr.left.exprType = asn1_sort
            expr.right = def_value
            try:
                fix_expression_types(expr, context)
                def_value = expr.right
                basic = find_basic_type(asn1_sort)
                if basic.kind.startswith(('Integer', 'Real')):
                    check_range(basic, find_basic_type(def_value.exprType))
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
                errors.append('In variable declaration {}: default'
                              ' value is not a valid ground expression'.
                              format(var[-1]))
        else:
            warnings.append('Unsupported variables construct type: ' +
                    str(child.type))
    for variable in var:
        if not hasattr(context, 'variables'):
            errors.append('Variables shall not be declared here')
        # Add to the context and text area AST entries
        elif(variable.lower() in context.variables
                  or variable.lower() in ta_ast.variables):
            errors.append('Variable "{}" is declared more than once'
                          .format(variable))
        else:
            context.variables[variable.lower()] = (asn1_sort, def_value)
        ta_ast.variables[variable.lower()] = (asn1_sort, def_value)
    if not DV:
        errors.append('Cannot do semantic checks on variable declarations')
    return errors, warnings


def dcl(root, ta_ast, context):
    ''' Process a set of variable declarations '''
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.VARIABLES:
            err, warn = variables(child, ta_ast, context)
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
    # and map a list of transitionsi to each state
    comp.mapping = {name: [] for name in get_state_list(root)}
    inner_composite, states, floatings, starts = [], [], [], []
    for child in root.getChildren():
        if child.type == lexer.ID:
            comp.line = child.getLine()
            comp.charPositionInLine = child.getCharPositionInLine()
            comp.statename = child.toString().lower()
        elif child.type == lexer.COMMENT:
            comp.comment, _, _ = end(child)
        elif child.type == lexer.IN:
            # state entry point
            for point in child.getChildren():
                comp.state_entrypoints.append(point.toString().lower())
        elif child.type == lexer.OUT:
            # state exit point
            for point in child.getChildren():
                comp.state_exitpoints.append(point.toString().lower())
        elif child.type == lexer.TEXTAREA:
            textarea, err, warn = text_area(child, context=comp)
            if textarea.signals:
                errors.append(['Signals shall not be declared in a state',
                               [textarea.pos_y, textarea.pos_y], []])
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
            comp.content.inner_procedures.append(new_proc)
            # Add procedure to the context, to make it visible at scope level
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
        errors.append(['State aggregation can only contain composite state(s)',
                      [0, 0], []])
    for each in inner_composite:
        # Parse inner composite states after the text areas to make sure
        # that all variables are propagated to the the inner scope
        inner, err, warn = composite_state(each, parent=None,
                                           context=comp)
        if isinstance(comp, ogAST.StateAggregation):
            # State aggregation contain only composite states, so we must
            # add empty mapping information since there are no transitions
            comp.mapping[inner.statename.lower()] = []
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
            errors.append(['Only one unnamed START transition is allowed',
                           [st.pos_x, st.pos_y], []])
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
    # Post-processing: check that all NEXTSTATEs have a corresponding STATE
    for ns in [t.inputString.lower() for t in comp.terminators
            if t.kind == 'next_state']:
        if not ns in [s.lower() for s in
                comp.mapping.viewkeys()] + ['-']:
            errors.append(['In composite state "{}": missing definition '
                           'of substate "{}"'
                           .format(comp.statename, ns.upper()),
                           [0, 0], []])
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
        elif child.type == lexer.ID:
            proc.line = child.getLine()
            proc.charPositionInLine = child.getCharPositionInLine()
            proc.inputString = child.toString()
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
                errors.append('Signals shall not be declared in a procedure')
            errors.extend(err)
            warnings.extend(warn)
            proc.content.textAreas.append(textarea)
        elif child.type == lexer.EXTERNAL:
            proc.external = True
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            proc.fpar = params
        elif child.type == lexer.RETURNS:
            try:
                proc.return_type, proc.return_var = procedure_returns(child)
            except TypeError as err:
                errors.append(str(err))
            if proc.return_var:
                warnings.append('Procedure return variable not supported')
        elif child.type in (lexer.PROCEDURE, lexer.START,
                            lexer.STATE, lexer.FLOATING_LABEL):
            content.append(child)
        else:
            warnings.append(
                    'Unsupported construct in procedure, type: ' +
                    sdl92Parser.tokenNames[child.type] +
                    ' - line ' + str(child.getLine()) +
                    ' - in procedure ' + str(proc.inputString))
    return proc, content, errors, warnings


def procedure_returns(root):
    ''' Returns the (optional) variable name and the sort of the return '''
    if len(root.children) == 1:
        return sdl_to_asn1(root.getChild(0).getChild(0).text), None
    else:
        return sdl_to_asn1(root.getChild(1).getChild(0).text),\
               root.getChild(0).text


def procedure_post(proc, content, parent=None, context=None):
    ''' Parse the content of a procedure '''
    errors = []
    warnings = []
    # Create a list of all inherited data
    try:
        proc.global_variables = dict(context.variables)
        proc.global_variables.update(context.global_variables)
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
            proc.content.inner_procedures.append(new_proc)
            # Add procedure to the context, to make it visible at scope level
            context.procedures.append(new_proc)
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            proc.content.start, err, warn = start(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
#       elif child.type == lexer.STATE:
#           # STATE - fills up the 'mapping' structure.
#           newstate, err, warn = state(child, parent=None, context=proc)
#           errors.extend(err)
#           warnings.extend(warn)
#           proc.content.states.append(newstate)
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
            errors.append(['No return value expected in procedure {}'
                           .format(proc.inputString),
                           [0, 0], []])
        elif proc.return_type and each.return_expr:
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimVariable()
            check_expr.left.exprType = proc.return_type
            check_expr.right = each.return_expr
            try:
                fix_expression_types(check_expr, context)
            except (TypeError, AttributeError) as err:
                errors.append(str(err))
            # Id of fd_expr may have changed (enumerated, choice)
            each.return_expr = check_expr.right
        elif proc.return_type and not each.return_expr:
            errors.append(['Missing return value in procedure {}'
                           .format(proc.inputString),
                           [0, 0], []])
        else:
            continue
    for each in chain(errors, warnings):
        each[2].insert(0, 'PROCEDURE {}'.format(proc.inputString))

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
        elif child.type == lexer.HYPERLINK:
            lab.hyperlink = child.getChild(0).text[1:-1]
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(
                                    child, parent=lab, context=context)
            errors.extend(err)
            warnings.extend(warn)
            lab.transition = trans
        else:
            warnings.append(
                    ['Unsupported construct in floating label: ' +
                    str(child.type), [lab_x, lab_y], []])
    if not lab.transition:
        warnings.append(['Floating labels not followed by a transition: ' +
                        str(lab.inputString), [lab_x, lab_y], []])
    # At the end of the label parsing, get the the list of terminators that
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

    newtypename = root.getChild(0).getChild(0).text
    return newtypename, errors, warnings


def get_array_type(root):
    ''' Returns the subtype associated to an NEWTYPE ARRAY construction '''
    # indexSort = root.getChild(0).text
    typeSort = root.getChild(1).text
    typeSortLine = root.getChild(1).getLine()
    typeSortChar = root.getChild(1).getCharPositionInLine()

    # Constructing ASN.1 AST subtype
    newtype = type("SeqOf_type", (object,), {
        "Line": typeSortLine, "CharPositionInLine": typeSortChar,
        "Kind": "ReferenceType", "ReferencedTypeName": typeSort
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
            fieldname = field.getChild(0).text
            typename = field.getChild(1).getChild(0).text
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

    newtypename = root.getChild(0).getChild(0).text
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

    DV.types[str(newtypename)] = newtype
    LOG.debug("Found new SYNTYPE " + newtypename)
    return errors, warnings


def newtype(root, ta_ast, context):
    ''' Parse a NEWTYPE definition and inject it in ASN1 AST'''
    errors = []
    warnings = []

    newtypename, errors, warnings = newtype_gettype(root, ta_ast, context)
    if (newtypename == ""):
        return errors, warnings

    newtype = type(str(newtypename), (object,), {
                   "Line": root.getLine(),
                   "CharPositionInLine": root.getCharPositionInLine()})
    if len(root.children) < 2:
        warnings.append('Use newtype definitions for arrays and records only')
        newtype.kind = "BooleanType"
        DV.types[str(newtypename)] = newtype
        LOG.debug("Boolean newtype " + newtypename)
    elif (root.getChild(1).type == lexer.ARRAY):
        newtype.kind = "SequenceOfType"
        newtype.type = get_array_type(root.getChild(1))
        newtype.Min = "Min"
        newtype.Max = "Max"
        DV.types[str(newtypename)] = newtype
        LOG.debug("Found new ARRAY type " + newtypename)
    elif (root.getChild(1).type == lexer.STRUCT):
        newtype.kind = "SequenceType"
        newtype.Children = get_struct_children(root.getChild(1))
        DV.types[str(newtypename)] = newtype
        LOG.debug("Found new STRUCT type " + newtypename)
    else:
        warnings.append(
                    'Unsupported type definition in newtype, type: ' +
                    str(root.type))
     # STRUCT CASE
    return errors, warnings


def synonym(root, ta_ast, context):
    ''' Parse a SYNONYM definition and inject it in ASN1 exported variables'''
    errors = []
    warnings = []

    if not "SDL-Constants" in DV.asn1Modules:
        DV.asn1Modules.append("SDL-Constants")
        DV.exportedVariables["SDL-Constants"] = []

    for child in root.getChildren():
        if child.getChild(0).type == lexer.SORT:
            DV.exportedVariables["SDL-Constants"].append(
                                            child.getChild(0).getChild(0).text)
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
            try:
                context.return_type, context.return_var =\
                        procedure_returns(child)
            except TypeError as err:
                errors.append(str(err))
            if context.return_var:
                warnings.append('Procedure return variable not supported')
        elif child.type == lexer.TIMER:
            timers = [timer.text.lower() for timer in child.children]
            context.timers.extend(timers)
            ta_ast.timers = timers
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
                    str(child.type))
    if ta_ast.asn1_files:
        # Parse ASN.1 files that are referenced in USE clauses
        try:
            set_global_DV(ta_ast.asn1_files)
        except TypeError as err:
            errors.append(str(err))
    for each in procedures:
        # Procedure textual declarations need ASN.1 types
        proc, err, warn = procedure(each, context=context)
        errors.extend(err)
        warnings.extend(warn)
        try:
            # Add procedure to the container (process or procedure)
            context.content.inner_procedures.append(proc)
        except AttributeError:
            # May not be any content in current context (eg System)
            pass
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
    for child in root.getChildren():
        if child.type == lexer.CIF:
            userTextStartIndex = child.getTokenStopIndex() + 1
            ta.pos_x, ta.pos_y, ta.width, ta.height = cif(child)
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
            ta.inputString = token_stream(child).toString(
                    userTextStartIndex, userTextStopIndex).strip()
        elif child.type == lexer.HYPERLINK:
            ta.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported construct in text area, type: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    errors = [[e, [ta.pos_x or 0, ta.pos_y or 0], []] for e in errors]
    warnings = [[w, [ta.pos_x or 0, ta.pos_y or 0], []] for w in warnings]
    return ta, errors, warnings


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
            block.signalroutes.append(sigroute)
        else:
            warnings.append('Unsupported block child type: ' +
                str(child.type))
    return block, errors, warnings


def system_definition(root, parent):
    ''' SYSTEM part - contains blocks, procedures and channels '''
    errors, warnings = [], []
    system = ogAST.System()
    # Store the name of the file where the system is defined
    system.filename = node_filename(root)
    system.ast = parent
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
            else:
                errors.append('ASN.1 Files must be set in a single text area')
            errors.extend(err)
            warnings.extend(warn)
            system.text_areas.append(textarea)
        else:
            warnings.append('Unsupported construct in system: ' +
                    str(child.type))
#   if asn1_files:
#       # parse ASN.1 files before parsing the rest of the system
#       try:
#           set_global_DV(asn1_files)
#       except TypeError as err:
#           errors.append(str(err))
        if asn1_files:
            system.ast.asn1Modules = DV.asn1Modules
            system.ast.asn1_filenames = asn1_files
    for each in signals:
        sig, err, warn = signal(each)
        errors.extend(err)
        warnings.extend(warn)
        system.signals.append(sig)
    for each in procedures:
        proc, err, warn = procedure(
                each, parent=None, context=system)
        errors.extend(err)
        warnings.extend(warn)
        system.procedures.append(proc)
    for each in blocks:
        block, err, warn = block_definition(each, parent=system)
        errors.extend(err)
        warnings.extend(warn)
    return system, errors, warnings


def process_definition(root, parent=None, context=None):
    ''' Process definition analysis '''
    errors, warnings, perr, pwarn = [], [], [], []
    process = ogAST.Process()
    process.filename = node_filename(root)
    process.parent = parent
    proc_x, proc_y = 0, 0
    inner_proc = []
    # Prepare the transition/state mapping
    process.mapping = {name: [] for name in get_state_list(root)}
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            process.pos_x, process.pos_y, process.width, process.height =\
                    cif(child)
            proc_x, proc_y = process.pos_x, process.pos_y
        elif child.type == lexer.ID:
            # Get process name
            process.processName = child.text
            try:
                # Retrieve process interface (PI/RI)
                async, procedures, err = get_interfaces(parent, child.text)
                process.input_signals.extend([sig for sig in async
                                             if sig['direction'] == 'in'])
                process.output_signals.extend([sig for sig in async
                                              if sig['direction'] == 'out'])
                process.procedures.extend(procedures)
                perr.extend(err)
            except AttributeError as exc:
                # No interface because process is defined standalone
                LOG.debug('Discarding process ' + child.text + ' ' + str(exc))
            except TypeError as exc:
                perr.append(str(exc))
            perr = [[e, [proc_x, proc_y], []] for e in perr]
        elif child.type == lexer.TEXTAREA:
            # Text zone where variables and operators are declared
            textarea, err, warn = text_area(child, context=process)
            if textarea.signals:
                errors.append(['Signals shall not be declared in a process',
                              [textarea.pos_x, textarea.pos_y], []])
            errors.extend(err)
            warnings.extend(warn)
            process.content.textAreas.append(textarea)
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            process.content.start, err, warn = start(
                    child, context=process)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.STATE:
            # STATE - fills up the 'mapping' structure.
            statedef, err, warn = state(
                    child, parent=None, context=process)
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
            proc, content, err, warn = procedure_pre(
                    child, parent=None, context=process)
            inner_proc.append((proc, content))
            errors.extend(err)
            warnings.extend(warn)
            process.content.inner_procedures.append(proc)
            # Add it at process level so that it is in the scope
            process.procedures.append(proc)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(
                    child, parent=None, context=process)
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
        elif child.type == lexer.TYPE_INSTANCE:
            # PROCESS Toto:ParentType; Not supported
            pass
        elif child.type == lexer.COMMENT:
            process.comment, _, _ = end(child)
        else:
            warnings.append(['Unsupported process definition child: ' +
                             sdl92Parser.tokenNames[child.type] +
                            ' - line ' + str(child.getLine()),
                            [proc_x, proc_y], []])
    for proc, content in inner_proc:
        err, warn = procedure_post(proc, content, context=process)
        errors.extend(err)
        warnings.extend(warn)
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
    dec = ogAST.Decision()
    ans = ogAST.Answer()
    warnings, errors = [], []
    # Keep track of the number of terminator statements in the transition
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    dec.question, exp_err, exp_warn = expression(root.getChild(0), context)
    dec.inputString = dec.question.inputString
    dec.line = dec.question.line
    dec.charPositionInLine = dec.question.charPositionInLine
    dec.kind = 'question'
    ans.inputString = 'true'
    ans.openRangeOp = ogAST.ExprEq
    ans.kind = 'constant'
    ans.constant = ogAST.PrimBoolean()
    ans.constant.value = ['true']
    ans.constant.exprType = BOOLEAN
    dec.answers = [ans]
    i.trigger = dec
    i.inputString = dec.inputString
    for child in root.children[1:]:
        if child.type == lexer.CIF:
            # Get symbol coordinates
            i.pos_x, i.pos_y, i.width, i.height = cif(child)
        elif child.type == lexer.INT:
            # Priority
            i.priority = int(child.text)
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
    # At the end of the input parsing, get the the list of terminators that
    # follow the input transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the input)
    i.terminators = list(context.terminators[terminators:])
    return i, errors, warnings


def input_part(root, parent, context):
    ''' Parse an INPUT - set of TASTE provided interfaces '''
    i = ogAST.Input()
    warnings, errors = [], []
    # Keep track of the number of terminator statements follow the input
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            i.pos_x, i.pos_y, i.width, i.height = cif(child)
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
                    if inp_sig['name'].lower() == inputname.text.lower():
                        i.inputlist.append(inp_sig['name'])
                        sig_param_type = inp_sig.get('type')
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
                        compare_types(sig_param_type, user_param_type)
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
        elif child.type == lexer.ASTERISK:
            # Asterisk means: all inputs not processed explicitely
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
    # At the end of the input parsing, get the the list of terminators that
    # follow the input transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the input)
    i.terminators = list(context.terminators[terminators:])
    return i, errors, warnings


def state(root, parent, context):
    '''
        Parse a STATE.
        "parent" is used to compute absolute coordinates
        "context" is the AST used to store global data (process/procedure)
    '''
    errors, warnings, sterr, stwarn = [], [], [], []
    state_def = ogAST.State()
    asterisk_state = False
    asterisk_input = None
    st_x, st_y = 0, 0
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            (state_def.pos_x, state_def.pos_y,
            state_def.width, state_def.height) = cif(child)
            st_x, st_y = state_def.pos_x, state_def.pos_y
        elif child.type == lexer.STATELIST:
            # State name(state_def)
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            for statename in child.getChildren():
                state_def.statelist.append(statename.toString())
        elif child.type == lexer.ASTERISK:
            asterisk_state = True
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            exceptions = [c.toString() for c in child.getChildren()]
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
                for lists in (inps for inps in state_ast.mapping.viewvalues()
                              if not isinstance(inps, int)):
                    res.extend(li for i in lists for li in i.inputlist)
                subinputs = map(gather_inputlist, state_ast.composite_states)
                map(res.extend, subinputs)
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
                for statename in state_def.statelist:
                    # check that input is not already defined
                    existing = context.mapping.get(statename.lower(), [])
                    dupl = set()
                    for each in inp.inputlist:
                        for ex_input in (name for i in existing
                                         for name in i.inputlist):
                            if unicode(each) == unicode(ex_input):
                                dupl.add(each)
                    for each in dupl:
                        sterr.append('Input "{}" is defined more '
                                     'than once for state "{}"'
                                     .format(each, statename.lower()))
                    # then update the mapping state-input
                    context.mapping[statename.lower()].append(inp)
            except KeyError:
                stwarn.append('State definition missing')
            state_def.inputs.append(inp)
            if inp.inputString.strip() == '*':
                if asterisk_input:
                    sterr.append('Multiple asterisk inputs under state ' +
                                  str(state_def.inputString))
                else:
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
                if provided_part in \
                        context.cs_mapping.get(statename.lower(), []):
                    sterr.append('Continous signal is defined more than once '
                                 'below state "{}"'.format(statename.lower()))
                else:
                    context.cs_mapping[statename.lower()].append(provided_part)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == 0:
            # Parser error, already caught
            pass
        else:
            stwarn.append('Unsupported STATE definition child type: ' +
                            sdl92Parser.tokenNames[child.type])
    # post-processing: if state is followed by an ASTERISK input, the exact
    # list of inputs can be updated. Possible only if context has signals
    if context.input_signals and asterisk_input:
        explicit_inputs = set()
        for inp in state_def.inputs:
            explicit_inputs |= set(inp.inputlist)
        # Keep only inputs that are not explicitely defined
        input_signals = (sig['name'] for sig in context.input_signals)
        remaining_inputs = set(input_signals) - explicit_inputs
        asterisk_input.inputlist = list(remaining_inputs)
    # post-processing: if state is composite, add link to the content
    if len(state_def.statelist) == 1 and not asterisk_state:
        for each in context.composite_states:
            if each.statename.lower() == state_def.statelist[0].lower():
                state_def.composite = each
    for each in sterr:
        errors.append([each, [st_x, st_y], []])
    for each in stwarn:
        warnings.append([each, [st_x, st_y], []])
    return state_def, errors, warnings


def connect_part(root, parent, context):
    ''' Connection of a nested state exit point with a transition
        Very similar to INPUT '''
    errors, warnings = [], []
    conn = ogAST.Connect()
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
                            sdl92Parser.tokenNames[child.type])
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
            errors.append([u'Exit point {ep} not defined in state {st}'
                          .format(ep=exitp, st=statename),
                          [conn.pos_x or 0, conn.pos_y or 0], []])
        def check_terminators(comp):
            terminators = [term for term in comp.terminators
                           if term.kind == 'return'
                           and term.inputString.lower() == exitp]
            if not terminators:
                errors.append([u'No {rs} return statement in nested state {st}'
                              .format(rs=exitp or u'default (unnamed)',
                                      st=comp.statename.lower()),
                              [conn.pos_x or 0, conn.pos_y or 0], []])
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
            map(terminators.extend, all_terms)
        for each in terminators:
            # Set next transition, exact id to be found in postprocessing
            each.next_trans = trans
    # Set list of terminators
    conn.terminators = list(context.terminators[terms:])
    return conn, errors, warnings


def cif(root):
    ''' Return the CIF coordinates '''
    result = []
    for child in root.getChildren():
        neg = False
        if child.type == lexer.DASH:
            neg = True
        else:
            val = int(child.toString())
            val = -val if neg else val
            result.append(val)
    return result


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
    # Keep track of the number of terminator statements following the start
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            s.pos_x, s.pos_y, s.width, s.height = cif(child)
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
            warnings.append('START unsupported child type: ' +
                    str(child.type))
    # At the end of the START parsing, get the the list of terminators that
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
        elif child.type == lexer.STRING:
            c.inputString = child.toString()[1:-1]
        elif child.type == lexer.HYPERLINK:
            c.hyperlink = child.getChild(0).toString()[1:-1]
    return c, [], []


def procedure_call(root, parent, context):
    ''' Parse a PROCEDURE CALL (synchronous required interface) '''
    # Same as OUTPUT for external procedures
    out_ast = ogAST.ProcedureCall()
    _, err, warn = output(root, parent, out_ast, context)
    return out_ast, err, warn


def outputbody(root, context):
    ''' Parse an output body (the content excluding the CIF statement) '''
    errors = []
    warnings = []
    body = {'outputName': '', 'params': []}
    for child in root.getChildren():
        if child.type == lexer.ID:
            body['outputName'] = child.text
            if child.text.lower() not in valid_output(context):
                errors.append('"' + child.text +
                              '" is not defined in the current scope')
        elif child.type == lexer.PARAMS:
            body['params'], err, warn = expression_list(
                                                    child, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.TO:
            pass
        # TODO: better support of TO primitive
        elif child.type == 0:
            # syntax error already caught by the parser
            pass
        else:
            warnings.append('Unsupported child type: {}'.format(child.type))
    # Check/set the type of each param
    try:
        check_call(body.get('outputName', '').lower(),
                   body.get('params', []),
                   context)
    except (AttributeError, TypeError) as op_err:
        errors.append(str(op_err) + ' - ' + get_input_string(root))
        LOG.debug('[outputbody] call check_and_fix_op_params : '
                    + get_input_string(root) + str(op_err))
        LOG.debug(str(traceback.format_exc()))
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
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            out_ast.pos_x, out_ast.pos_y, out_ast.width, out_ast.height = \
                    cif(child)
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
    return out_ast, errors, warnings


def alternative_part(root, parent, context):
    ''' Parse a decision answer '''
    errors = []
    warnings = []
    ans = ogAST.Answer()
    if root.type == lexer.ELSE:
        # used when copy-pasting
        ans.inputString = root.text
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            ans.pos_x, ans.pos_y, ans.width, ans.height = cif(child)
        elif child.type == lexer.CLOSED_RANGE:
            ans.kind = 'closed_range'
            cl0, err0, warn0 = expression(child.getChild(0), context)
            cl1, err1, warn1 = expression(child.getChild(1), context)
            errors.extend(err0)
            errors.extend(err1)
            warnings.extend(warn0)
            warnings.extend(warn1)
            ans.closedRange = [cl0, cl1]
        elif child.type == lexer.CONSTANT:
            ans.kind = 'constant'
            ans.constant, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
            ans.openRangeOp = ogAST.ExprEq
        elif child.type == lexer.OPEN_RANGE:
            ans.kind = 'open_range'
            for c in child.getChildren():
                if c.type == lexer.CONSTANT:
                    ans.constant, err, warn = expression(
                            c.getChild(0), context)
                    errors.extend(err)
                    warnings.extend(warn)
                    if not ans.openRangeOp:
                        ans.openRangeOp = ogAST.ExprEq
                else:
                    ans.openRangeOp = EXPR_NODE[c.type]
        elif child.type == lexer.INFORMAL_TEXT:
            ans.kind = 'informal_text'
            ans.informalText = child.getChild(0).toString()[1:-1]
        elif child.type == lexer.TRANSITION:
            ans.transition, err, warn = transition(
                                        child, parent=ans, context=context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.HYPERLINK:
            ans.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported answer type: ' + str(child.type))
        if child.type in (lexer.CLOSED_RANGE, lexer.CONSTANT,
                          lexer.OPEN_RANGE, lexer.INFORMAL_TEXT):
            ans.inputString = get_input_string(child)
            ans.line = child.getLine()
            ans.charPositionInLine = child.getCharPositionInLine()
            # Report errors with symbol coordinates
            x, y = (ans.pos_x or 0, ans.pos_y or 0)
            errors = [[e, [x, y], []] for e in errors]
            warnings = [[w, [x, y], []] for w in warnings]
    return ans, errors, warnings


def decision(root, parent, context):
    ''' Parse a DECISION '''
    errors, warnings, qerr, qwarn = [], [], [], []
    dec = ogAST.Decision()
    dec.tmpVar = tmp()
    has_else = False
    dec_x, dec_y = 0, 0
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            dec.pos_x, dec.pos_y, dec.width, dec.height = cif(child)
            dec_x, dec_y = dec.pos_x, dec.pos_y
        elif child.type == lexer.QUESTION:
            dec.kind = 'question'
            dec.question, qerr, qwarn = expression(child.getChild(0), context)
            dec.inputString = dec.question.inputString
            dec.line = dec.question.line
            dec.charPositionInLine = dec.question.charPositionInLine
        elif child.type == lexer.INFORMAL_TEXT:
            dec.kind = 'informal_text'
            dec.inputString = get_input_string(child)
            dec.informalText = child.getChild(0).toString()[1:-1]
            dec.line = child.getLine()
            dec.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.ANY:
            warnings.append(['Use of "ANY" introduces non-determinism ',
                            [dec.pos_x, dec.pos_y], []])
            dec.kind = 'any'
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
            a = ogAST.Answer()
            a.inputString = child.toString()
            for c in child.getChildren():
                if c.type == lexer.CIF:
                    a.pos_x, a.pos_y, a.width, a.height = cif(c)
                elif c.type == lexer.TRANSITION:
                    a.transition, err, warn = transition(
                                            c, parent=a, context=context)
                    errors.extend(err)
                    warnings.extend(warn)
                elif child.type == lexer.HYPERLINK:
                    a.hyperlink = child.getChild(0).toString()[1:-1]
            a.kind = 'else'
            dec.answers.append(a)
            has_else = True
        else:
            warnings.append(['Unsupported DECISION child type: ' +
                str(child.type), [dec.pos_x, dec.pos_y], []])
    # Make type checks to be sure that question and answers are compatible
    covered_ranges = defaultdict(list)
    qmin, qmax = 0, 0
    need_else = False
    is_enum, is_bool = False, False
    for ans in dec.answers:
        if dec.kind in ('informal_text', 'any'):
            break
        ans_x, ans_y = ans.pos_x, ans.pos_y
        if ans.kind in ('constant', 'open_range'):
            expr = ans.openRangeOp()
            expr.left = dec.question
            expr.right = ans.constant
            try:
                fix_expression_types(expr, context)
                if dec.question.exprType == UNKNOWN_TYPE:
                    dec.question = expr.left
                ans.constant = expr.right
                q_basic = find_basic_type(dec.question.exprType)
                a_basic = find_basic_type(ans.constant.exprType)
                if q_basic.kind.endswith('EnumeratedType'):
                    if not ans.constant.is_raw:
                        # Ref to a variable -> can't guarantee coverage
                        need_else = True
                        continue
                    covered_ranges[ans].append(ans.inputString)
                    is_enum = True
                elif q_basic.kind == 'BooleanType':
                    covered_ranges[ans].append(ans.constant.value[0])
                    is_bool = True
                    if not ans.constant.is_raw:
                        need_else = True
                        continue
                if not q_basic.kind.startswith(('Integer', 'Real')):
                    # Check numeric questions - ignore others
                    continue
                delta = 1 if q_basic.kind.startswith('Integer') else 1e-10
                # numeric type -> find the range covered by this answer
                if a_basic.Min != a_basic.Max:
                    # Not a constant or a raw number, range is not fix
                    need_else = True
                    continue
                val_a = float(a_basic.Min)
                qmin, qmax = float(q_basic.Min), float(q_basic.Max)
                # Check the operator to compute the range
                reachable = True
                if ans.openRangeOp == ogAST.ExprLe:
                    # answer <= X means covered range is [min; X]
                    if qmin <= val_a:
                        covered_ranges[ans].append((qmin, val_a))
                    else:
                        reachable = False
                elif ans.openRangeOp == ogAST.ExprLt:
                    # answer < X means covered range is [min; X[
                    if qmin < val_a:
                        covered_ranges[ans].append((qmin, val_a - delta))
                    else:
                        reachable = False
                elif ans.openRangeOp == ogAST.ExprGt:
                    # answer > X means covered range is ]X; max]
                    if qmax > val_a:
                        covered_ranges[ans].append((val_a + delta, qmax))
                    else:
                        reachable = False
                elif ans.openRangeOp == ogAST.ExprGe:
                    # answer >= X means covered range is [X; max]
                    if qmax >= val_a:
                        covered_ranges[ans].append((val_a, qmax))
                    else:
                        reachable = False
                elif ans.openRangeOp == ogAST.ExprEq:
                    if qmin <= val_a <= qmax:
                        covered_ranges[ans].append((val_a, val_a))
                    else:
                        reachable = False
                elif ans.openRangeOp == ogAST.ExprNeq:
                    # answer != X means covered range is [min; X[;]X; max]
                    if qmin == val_a:
                        covered_ranges[ans].append((qmin + delta, qmax))
                    elif qmax == val_a:
                        covered_ranges[ans].append((qmin, qmax - delta))
                    elif qmin < val_a < qmax:
                        covered_ranges[ans].append((qmin, val_a - delta))
                        covered_ranges[ans].append((val_a + delta, qmax))
                    else:
                        warnings.append(['Condition is always true: {} /= {}'
                                        .format(dec.inputString,
                                                ans.inputString),
                                        [ans_x, ans_y], []])
                else:
                    warnings.append(['Unsupported range expression',
                                     [ans_x, ans_y], []])
                if not reachable:
                        warnings.append(['Decision "{}": '
                                        'Unreachable branch "{}"'
                                        .format(dec.inputString,
                                                ans.inputString),
                                        [ans_x, ans_y], []])
            except (AttributeError, TypeError) as err:
                errors.append(['Type mismatch: '
                    'question (' + expr.left.inputString + ', type= ' +
                    type_name(expr.left.exprType) + '), answer (' +
                    expr.right.inputString + ', type= ' +
                    type_name(expr.right.exprType) + ') ' + str(err),
                    [ans_x, ans_y], []])
        elif ans.kind == 'closed_range':
            if not is_numeric(dec.question.exprType):
                errors.append(['Closed range are only for numerical types',
                              [ans_x, ans_y], []])
                continue
            for ast_type, idx in zip((ogAST.ExprGe, ogAST.ExprLe), (0, 1)):
                expr = ast_type()
                expr.left = dec.question
                expr.right = ans.closedRange[idx]
                try:
                    fix_expression_types(expr, context)
                    if dec.question.exprType == UNKNOWN_TYPE:
                        dec.question = expr.left
                    ans.closedRange[idx] = expr.right
                except (AttributeError, TypeError) as err:
                    errors.append(['Type mismatch in decision: '
                        'question (' + expr.left.inputString + ', type= ' +
                        type_name(expr.left.exprType) + '), answer (' +
                        expr.right.inputString + ', type= ' +
                        type_name(expr.right.exprType) + ') ' + str(err),
                        [ans_x, ans_y], []])
            q_basic = find_basic_type(dec.question.exprType)
            if not q_basic.kind.startswith(('Integer', 'Real')):
                continue
            delta = 1 if q_basic.kind.startswith('Integer') else 1e-10
            # numeric type -> find the range covered by this answer
            a0_basic = find_basic_type(ans.closedRange[0].exprType)
            a1_basic = find_basic_type(ans.closedRange[1].exprType)
            if not hasattr(a0_basic, "Min") or not hasattr(a1_basic, "Min") \
                    or a0_basic.Min != a0_basic.Max \
                    or a1_basic.Min != a1_basic.Max:
                # Not a constant or a raw number, range is not fix
                need_else = True
                continue
            qmin, qmax = float(q_basic.Min), float(q_basic.Max)
            a0_val = float(a0_basic.Min)
            a1_val = float(a1_basic.Max)
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
                warnings.append(['Decision "{dec}": Unreachable branch {l}:{h}'
                                .format(dec=dec.inputString,
                                        l=a0_val, h=a1_val),
                                [ans_x, ans_y], []])
            covered_ranges[ans].append((float(a0_basic.Min),
                                        float(a1_basic.Max)))
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
    for each in combinations(covered_ranges.viewitems(), 2):
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
    for ans_ref, ranges in covered_ranges.viewitems():
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
                txt = "value {}".format(low)
            else:
                txt = "range {} .. {}".format(low, high)
            qerr.append('Decision "{}": No answer to cover {}'
                        .format(dec.inputString, txt))
    elif has_else and is_numeric(dec.question.exprType) and not q_ranges:
        # (3) Check that ELSE branch is reachable
        qwarn.append('Decision "{}": ELSE branch is unreachable'
                        .format(dec.inputString))

    if need_else and not has_else:
        # (4) Answers use non-ground expression -> there should be an ELSE
        qwarn.append('Decision "{}": Missing ELSE branch'
                        .format(dec.inputString))

    if need_else and has_else and len(dec.answers) != 2:
        # At least one branch has a non-ground expression answer, therefore
        # there can be at most one additional answer: the ELSE branch,
        # otherwise there is a risk that branches overlap due to variables
        qerr.append('Answers of decision "{}" could overlap'
                    .format(dec.inputString))

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
                   for a in chain.from_iterable(covered_ranges.viewvalues())]
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
    errors.extend(qerr)
    warnings.extend(qwarn)
    return dec, errors, warnings


def nextstate(root, context):
    ''' Parse a NEXTSTATE [VIA State_Entry_Point] - detect various kinds of
        errors when trying to enter a nested state '''
    next_state_id, via, entrypoint = '', None, None
    errors = []
    for child in root.getChildren():
        if child.type == lexer.ID:
            next_state_id = child.text
        elif child.type == lexer.DASH:
            next_state_id = '-'
        elif child.type == lexer.VIA:
            if next_state_id.strip() != '-':
                via = get_input_string(root).replace(
                                                'NEXTSTATE', '', 1).strip()
                entrypoint = child.getChild(0).text
                try:
                    composite, = (comp for comp in context.composite_states
                                  if comp.statename.lower()
                                                == next_state_id.lower())
                except ValueError:
                    errors.append('State {} is not a composite state'
                                    .format(next_state_id))
                else:
                    if entrypoint.lower() not in composite.state_entrypoints:
                        errors.append('State {s} has no "{p}" entrypoint'
                                       .format(s=next_state_id, p=entrypoint))
                    for each in composite.content.named_start:
                        if each.inputString == entrypoint.lower() + '_START':
                            break
                    else:
                        errors.append('Entrypoint {p} in state {s} is '
                                      'declared but not defined'.format
                                      (s=next_state_id, p=entrypoint))
            else:
                errors.append('"History" NEXTSTATE cannot have a "via" clause')
        else:
            errors.append('NEXTSTATE undefined construct')
        if not via:
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
    return next_state_id, via, entrypoint, errors


def terminator_statement(root, parent, context):
    ''' Parse a terminator (NEXTSTATE, JOIN, STOP) '''
    errors = []
    warnings = []
    t = ogAST.Terminator()
    for term in root.getChildren():
        if term.type == lexer.CIF:
            t.pos_x, t.pos_y, t.width, t.height = cif(term)
        elif term.type == lexer.LABEL:
            lab, err, warn = label(term, parent=parent)
            errors.extend(err)
            warnings.extend(warn)
            t.label = lab
            context.labels.append(lab)
            lab.terminators = [t]
        elif term.type == lexer.NEXTSTATE:
            t.kind = 'next_state'
            t.inputString, t.via, t.entrypoint, err = nextstate(term, context)
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
            if t.inputString != '-':
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
    return t, errors, warnings


def transition(root, parent, context):
    ''' Parse a transition '''
    errors = []
    warnings = []
    trans = ogAST.Transition()
    # Used to list terminators in this transition
    terminators = {'trans': len(context.terminators)}
    #terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.PROCEDURE_CALL:
            proc_call, err, warn = procedure_call(
                            child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(proc_call)
            parent = proc_call
        elif child.type == lexer.LABEL:
            term_count = len(context.terminators)
            lab, err, warn = label(child, parent=parent)
            terminators[lab] = term_count
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(lab)
            parent = lab
            context.labels.append(lab)
        elif child.type == lexer.TASK:
            tas, err, warn = task(
                            child, parent=parent, context=context)
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
            _, err, warn = output(child,
                               parent=parent,
                               out_ast=out_ast,
                               context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(out_ast)
            parent = out_ast
        elif child.type == lexer.DECISION:
            dec, err, warn = decision(
                            child, parent=parent, context=context)
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
    # At the end of the transition parsing, get the the list of terminators
    # the transition contains by making a diff with the list at context
    # level (we counted the number of terminators before parsing the item)
    trans.terminators = list(context.terminators[terminators.pop('trans'):])
    # Also update the list of terminators of each label in the transition
    for lab, term_count in terminators.viewitems():
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
        expr.left, err, warn = call_expression(root.children[0], context)
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

    try:
        fix_expression_types(expr, context)
        # Assignment with numerical value: check range
        basic = find_basic_type(expr.left.exprType)
        if basic.kind.startswith(('Integer', 'Real')):
            check_range(basic, find_basic_type(expr.right.exprType))
    except(AttributeError, TypeError) as err:
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
        warnings.append('Expression "{}": {}'
                        .format(expr.inputString, str(warn)))
    if not errors:
        if expr.right.exprType == UNKNOWN_TYPE or not \
                isinstance(expr.right, (ogAST.ExprAppend,
                                        ogAST.PrimSequenceOf,
                                        ogAST.PrimStringLiteral)):
            expr.right.exprType = expr.left.exprType
        # XXX I don't understand why we don't set the type of right
        # to the same value as left in case of ExprAppend
        # Setting it - I did not see any place in the Ada backend where
        # this could cause a bug (and regression is OK)
        if isinstance(expr.right, ogAST.ExprAppend):
            expr.right.exprType = expr.left.exprType
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
                    r_min = basic.Min if basic != UNKNOWN_TYPE else '0'
                basic = find_basic_type(stop_expr.exprType)
                r_max = str(int(float(basic.Max) - 1)) \
                        if basic != UNKNOWN_TYPE else '4294967295'
                # basic may be UNKNOWN_TYPE if the expression is a
                # reference to an ASN.1 constant - their values are not
                # currently visible to the SDL parser
                result_type = type('for_range', (INTEGER,), {'Min': r_min,
                                                             'Max': r_max})
                context.variables[forloop['var']] = (result_type, 0)

            forloop['transition'], err, warn = transition(
                                    child, parent=for_loop, context=context)
            errors.extend(err)
            warnings.extend(warn)
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
            assig, err, warn = assign(child, context)
            errors.extend(err)
            warnings.extend(warn)
            body.elems.append(assig)
        elif child.type == lexer.INFORMAL_TEXT:
            if not body:
                body = ogAST.TaskInformalText()
            body.elems.append(child.getChild(0).toString()[1:-1])
        elif child.type == lexer.FOR:
            if not body:
                body = ogAST.TaskForLoop()
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
    return body, errors, warnings


def label(root, parent, context=None):
    ''' Parse a LABEL symbol '''
    errors = []
    warnings = []
    lab = ogAST.Label()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            lab.pos_x, lab.pos_y, lab.width, lab.height = cif(child)
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
    # This to allow SDL types injection in ASN1 ASTs
    DV = type("ASNParseTree", (object, ),
              {"types": {}, "exportedVariables": {}, "asn1Modules": [],
               "variables": {}})

    # Re-order the children of the AST to make sure system and use clauses
    # are parsed before process definition - to get signal definitions
    # and data typess references.
    processes, uses, systems = [], [], []
    for child in root.getChildren():
        ast.pr_files.add(node_filename(child))
        if child.type == lexer.PROCESS:
            processes.append(child)
        elif child.type == lexer.USE:
            uses.append(child)
        elif child.type == lexer.SYSTEM:
            systems.append(child)
        else:
            LOG.error('Unsupported construct in PR:' + str(child.type))
    for child in uses:
        # USE clauses can contain a CIF comment with the ASN.1 filename
        use_clause_subs = child.getChildren()
        asn1_filename = None
        for clause in use_clause_subs:
            entities = []
            if clause.type == lexer.ASN1:
                asn1_filename = clause.getChild(0).text[1:-1]
                ast.asn1_filenames.append(asn1_filename)
            else:
                entities.append(clause.text)
            if len(entities) == 1:
                ast.use_clauses.append(entities[0])
            elif len(entities) > 1:
                ast.use_clauses.extend('{}/{}'
                           .format(entities[0], each) for each in entities[1:])
#       if not asn1_filename:
#           # Look for case insentitive pr file and add it to AST
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

    for child in systems:
        system, err, warn = system_definition(child, parent=ast)
        errors.extend(err)
        warnings.extend(warn)
        ast.systems.append(system)

        def find_processes(block):
            ''' Recursively find processes in a system '''
            try:
                result = [proc for proc in block.processes
                          if not proc.referenced]
            except AttributeError:
                result = []
            for nested in block.blocks:
                result.extend(find_processes(nested))
            return result
        ast.processes.extend(find_processes(system))
    for child in processes:
        # process definition at root level (must be referenced in a system)
        process, err, warn = process_definition(child, parent=ast)
        ast.processes.append(process)
        process.dataview = types()
        process.asn1Modules = ast.asn1Modules
        process.dv = DV
        errors.extend(err)
        warnings.extend(warn)

    # Since SDL type declarations are injected in ASN.1 ast,
    # The ASN.1 ASTs needs to be copied at the end of PR parsing process
    # and not just after the ASN1 specific parsing
    ast.dataview = types()
    ast.asn1_constants = DV.variables
    return ast, errors, warnings


def add_to_ast(ast, filename=None, string=None):
    ''' Parse a file or string and add it to an AST '''
    errors, warnings = [], []
    try:
        parser = parser_init(filename=filename, string=string)
    except IOError as err:
        LOG.error('Parser error: ' + str(err))
        raise
    # Use Sam & Max output capturer to get errors from ANTLR parser
    with samnmax.capture_ouput() as (stdout, stderr):
        tree_rule_return_scope = parser.pr_file()
    for e in stderr:
        errors.append([e.strip()])
    for w in stdout:
        warnings.append([w.strip()])
    # Root of the AST is of type antlr3.tree.CommonTree
    # Add it as a child of the common tree
    subtree = tree_rule_return_scope.tree
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
    for filename in files:
        err, warn = add_to_ast(common_tree, filename=filename)
        errors.extend(err)
        warnings.extend(warn)
    if string:
        err, warn = add_to_ast(common_tree, string=string)
        errors.extend(err)
        warnings.extend(warn)

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
    # (except the '-' state, which means "stay in the same state')
    for process in og_ast.processes:
        for ns in [t.inputString.lower() for t in process.terminators
                if t.kind == 'next_state']:
            if not ns in [s.lower() for s in
                    process.mapping.viewkeys()] + ['-']:
                t_x, t_y = t.pos_x or 0, t.pos_y or 0
                errors.append(['State definition missing: ' + ns.upper(),
                              [t_x, t_y],
                              ['PROCESS {}'.format(process.processName)]])
        # TODO: do the same with JOIN/LABEL
    return og_ast, warnings, errors


def parseSingleElement(elem='', string='', context=None):
    '''
        Parse any symbol and return syntax error and AST entry
        Used for on-the-fly checks when user edits text
        and for copy/cut to create a new object
    '''
    assert(elem in ('input_part', 'output', 'decision', 'alternative_part',
            'terminator_statement', 'label', 'task', 'procedure_call', 'end',
            'text_area', 'state', 'start', 'procedure', 'floating_label',
            'connect_part', 'process_definition', 'proc_start', 'state_start',
            'signalroute', 'stop_if', 'continuous_signal'))
    # Create a dummy context, needed to place context data
    if elem == 'proc_start':
        elem = 'start'
        context = ogAST.Procedure()
    elif elem == 'state_start':
        elem = 'start'
        context = ogAST.CompositeState()
    else:
        context = context or ogAST.Process()
    LOG.debug('Parsing string: ' + string + ' with elem ' + elem)
    parser = parser_init(string=string)
    parser_ptr = getattr(parser, elem)
    assert parser_ptr is not None
    syntax_errors = []
    semantic_errors = []
    warnings = []
    t = None
    if parser:
        with samnmax.capture_ouput() as (stdout, stderr):
            r = parser_ptr()
        for e in stderr:
            syntax_errors.append(e.strip())
        for w in stdout:
            syntax_errors.append(w.strip())
        # Get the root of the Antlr-AST to build our own AST entry
        root = r.tree
        root.token_stream = parser.getTokenStream()
        backend_ptr = eval(elem)
        try:
            t, semantic_errors, warnings = backend_ptr(
                                root=root, parent=None, context=context)
        except AttributeError as err:
            #print str(err)
            #print (traceback.format_exc())
            # Syntax checker has no visibility on variables and types
            # so we have to discard exceptions sent by e.g. find_variable
            pass
        except NotImplementedError as err:
            syntax_errors.append('Syntax error in expression - Fix it.')
    return(t, syntax_errors, semantic_errors, warnings,
            context.terminators)


def parser_init(filename=None, string=None):
    ''' Initialize the parser (to be called first) '''
    if filename is not None:
        try:
            char_stream = antlr3.ANTLRFileStream(filename, encoding='utf-8')
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
    parser = sdl92Parser(tokens)
    return parser


if __name__ == '__main__':
    print 'This module is not callable'
