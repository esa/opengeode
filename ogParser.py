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
import importlib
import logging
import traceback
import antlr3
import antlr3.tree

from singledispatch import singledispatch

import sdl92Lexer as lexer
from sdl92Parser import sdl92Parser

import samnmax
import ogAST

LOG = logging.getLogger(__name__)

OPKIND = {lexer.PLUS: ogAST.ExprPlus,
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
          lexer.PRIMARY: ogAST.Primary}

# Insert current path in the search list for importing modules
sys.path.insert(0, '.')

DV = None

# Code generator backends may need some intemediate variables to process
# expressions. For convenience and to avoid multiple pass parsing, the parser
# tries to guess where they may be useful, and adds a hint in the AST.
TMPVAR = 0

# ASN.1 types used to support the signature of special operators
INTEGER = type('IntegerType', (object,), {'kind': 'IntegerType'})
INT32 = type('Integer32Type', (object,), {'kind': 'Integer32Type'})
NUMERICAL = type('NumericalType', (object,), {'kind': 'Numerical'})
TIMER = type('TimerType', (object,), {'kind': 'TimerType'})
REAL = type('RealType', (object,), {'kind': 'RealType'})
LIST = type('ListType', (object,), {'kind': 'ListType'})
ANY_TYPE = type('AnyType', (object,), {'kind': 'AnyType'})
CHOICE = type('ChoiceType', (object,), {'kind': 'ChoiceType'})
BOOLEAN = type('BooleanType', (object,), {'kind': 'BooleanType'})

UNKNOWN_TYPE = type('UnknownType', (object,), {'kind': 'UnknownType'})


# Special SDL operators and signature
SPECIAL_OPERATORS = {'length': [LIST],
                     'write': [ANY_TYPE],
                     'writeln': [ANY_TYPE],
                     'present': [CHOICE],
                     'set_timer': [INTEGER, TIMER],
                     'reset_timer': [TIMER],
                     'abs': [NUMERICAL]}

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
    for inner_proc in scope.content.inner_procedures:
        yield inner_proc.inputString.lower()


def get_interfaces(ast, process_name):
    '''
        Search for the list of input and output signals (async PI/RI)
        and procedures (sync RI) of a process in a given top-level AST
    '''
    all_signals = []
    async_signals = []
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
            break
    else:
        if isinstance(ast, ogAST.Block):
            process_ref = ast
        else:
            raise TypeError('Process ' + process_name +
                        ' is defined but not not declared in a system')
    # Go to the block where the process is defined
    process_parent = process_ref.parent
    # Find in and out signals names using the signalroutes
    for signalroute in process_parent.signalroutes:
        for route in signalroute['routes']:
            if route['source'] == process_name:
                direction = 'out'
            elif route['dest'] == process_name:
                direction = 'in'
            else:
                continue
            for sig_id in route['signals']:
                # Copy the signal to the result dict
                found, = [dict(sig) for sig in all_signals
                          if sig['name'] == sig_id]
                found['direction'] = direction
                async_signals.append(found)
    return async_signals, system.procedures


def get_input_string(root):
    ''' Return the input string of a tree node '''
    return token_stream(root).toString(root.getTokenStartIndex(),
            root.getTokenStopIndex())


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


def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type or UNKNOWN_TYPE
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in types().viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = types()[typename].type
                break
        else:
            raise TypeError('Type "' + type_name(basic_type) +
                            '" was not found in Dataview')
    return basic_type


def is_constant(var):
    ''' Check in ASN.1 modules if var (Primary) is declared as a constant '''
    if var is None:
        return False
    if isinstance(var, ogAST.PrimConstant):
        return True
    if DV and isinstance(var, ogAST.PrimPath):
        for mod in DV.asn1Modules:
            for constant in DV.exportedVariables[mod]:
                if(constant.lower() == var.value[0].lower().replace('_', '-')):
                    LOG.debug('Constant ' + var.inputString + ' found')
                    return True
    return False


def fix_special_operators(op_name, expr_list, context):
    ''' Verify/fix type of special operators parameters '''
    if op_name.lower() in ('length', 'present', 'abs'):
        if len(expr_list) != 1:
            raise AttributeError('Only one parameter for the {} operator'
                                 .format(op_name))
        expr = expr_list[0]
        if expr.exprType is UNKNOWN_TYPE:
            expr.exprType = find_variable(expr.inputString, context)
            # XXX don't use inputString, there can be brackets
            # XXX should change type to PrimVariable
        basic = find_basic_type(expr.exprType)
        if op_name.lower() == 'length' and basic.kind != 'SequenceOfType' \
                                 and not basic.kind.endswith('StringType'):
            raise TypeError('Length operator works only on strings/lists')
        elif op_name.lower() == 'present' and basic.kind != 'ChoiceType':
            raise TypeError('Present operator works only on CHOICE types')
    elif op_name.lower() in ('write', 'writeln'):
        for param in expr_list:
            if param.exprType is UNKNOWN_TYPE:
                param.exprType = find_variable(param.inputString, context)
            basic = find_basic_type(param.exprType)
            if basic.kind not in ('IntegerType', 'Integer32Type',
                                  'RealType', 'BooleanType') \
                                and not basic.kind.endswith('StringType'):
                # Currently supported printable types
                raise TypeError('Write operator does not support type')
    elif op_name.lower() == 'set_timer':
        if len(expr_list) != 2:
            raise TypeError('SET_TIMER has 2 parameters: (int, timer_name)')
        basic = find_basic_type(expr_list[0].exprType)
        if not basic.kind.startswith('Integer'):
            raise TypeError('SET_TIMER first parameter is not an integer')
        timer = expr_list[1].inputString
        for each in context.timers:
            if each.lower() == timer.lower():
                break
        else:
            raise TypeError('Timer {} is not defined'.format(timer))
    elif op_name.lower == 'reset_timer':
        if len(expr_list) != 1:
            raise TypeError('RESET_TIMER has 1 parameter: timer_name')
        timer = expr_list[0].inputString
        for each in context.timers:
            if each.lower() == timer.lower():
                break
        else:
            raise TypeError('Timer {} is not defined'.format(timer))
    else:
        # TODO: other operators
        return


def check_and_fix_op_params(op_name, expr_list, context):
    '''
        Verify and/or set the type of a procedure/output parameters
        TODO: when supported, add operators
    '''
    # (1) Find the signature of the function
    # signature will hold the list of parameters for the function
    LOG.debug('[check_and_fix_op_params] ' + op_name + ' - ' + str(expr_list))
    signature = []
    key = ''

    for out_sig in context.output_signals:
        if out_sig['name'].lower() == op_name.lower():
            if out_sig.get('type'):
                # output signals: one single parameter
                signature = [{'type': out_sig.get('type'),
                              'name': out_sig.get('param_name' or ''),
                              'direction': 'in'}]
            break
    else:
        # Procedures (inner and external)
        for inner_proc in (context.content.inner_procedures
                           + context.procedures):
            key = inner_proc.inputString
            if key.lower() == op_name.lower():
                signature = inner_proc.fpar
                break
        else:
            if op_name.lower() not in SPECIAL_OPERATORS:
                raise AttributeError('Operator/output/procedure not found: '
                    + op_name)
            else:
                # Special operators: parameters are context dependent
                fix_special_operators(op_name, expr_list, context)
                return
    # (2) Check that the number of given parameters matches the signature
    if signature is not None and len(signature) != len(expr_list):
        raise TypeError('Wrong number of parameters')
    # (3) Check each individual parameter type
    for idx, param in enumerate(expr_list):
        if signature is None:
            break
        # Get parameter type name from the function signature:
        param_type = type_name(signature[idx].get('type'))
        # Retrieve the type (or None if it is a sepecial operator)
        dataview_entry = types().get(param_type) or UNKNOWN_TYPE
        if dataview_entry is not UNKNOWN_TYPE:
            dataview_type = new_ref_type(param_type)
        else:
            dataview_type = UNKNOWN_TYPE

        expr = ogAST.ExprAssign()
        expr.left = ogAST.PrimPath()
        expr.left.exprType = dataview_type
        expr.right = param
        fix_expression_types(expr, context)
        expr_list[idx] = expr.right
        if signature[idx].get('direction') != 'in' \
                and not isinstance(expr.right, ogAST.PrimVariable):
            raise TypeError('OUT parameter "{}" is not a variable'
                            .format(expr.right.inputString))


def check_type_compatibility(primary, typeRef, context):
    '''
        Check if an ogAST.Primary (raw value, enumerated, ASN.1 Value...)
        is compatible with a given type (typeRef is an ASN1Scc type)
        Does not return anything if OK, otherwise raises TypeError
    '''
    assert typeRef is not None
    if typeRef is UNKNOWN_TYPE:
        raise TypeError('Type reference is unknown')
    if isinstance(primary, ogAST.PrimConstant):
        # ASN.1 constants type is unknown (Asn1 backend to be completed)
        return
    actual_type = find_basic_type(typeRef)
    LOG.debug("[check_type_compatibility] "
              "checking if {value} is of type {typeref}: "
              .format(value=primary.inputString, typeref=type_name(typeRef)))

    if (isinstance(primary, ogAST.PrimEnumeratedValue)
            and actual_type.kind.endswith('EnumeratedType')):
        # If type ref is an enumeration, check that the value is valid
        # Note, when using the "present" operator of a CHOICE type, the
        # resulting value is actually an EnumeratedType
        enumerant = primary.inputString.replace('_', '-')
        corr_type = actual_type.EnumValues.get(enumerant)
        if corr_type:
            return
        else:
            err = ('Value "' + primary.value[0] +
                   '" not in this enumeration: ' +
                   str(actual_type.EnumValues.keys()))
            raise TypeError(err)
    elif isinstance(primary, ogAST.PrimIfThenElse):
        # check that IF expr returns BOOL, and that Then and Else expressions
        # are compatible with actual_type
        if_expr = primary.value['if']
        then_expr = primary.value['then']
        else_expr = primary.value['else']
        if if_expr.exprType.kind != 'BooleanType':
            raise TypeError('IF expression does not return a boolean')
        else:
            for expr in (then_expr, else_expr):
                if expr.is_raw:
                    check_type_compatibility(expr, typeRef, context)
                # compare the types for semantic equivalence:
                else:
                    compare_types(expr.exprType, typeRef)
        return
    elif isinstance(primary, ogAST.PrimVariable):
        try:
            compare_types(primary.exprType, typeRef)
        except TypeError as err:
            raise TypeError('{expr} should be of type {ty} - {err}'
                            .format(expr=primary.inputString,
                                    ty=type_name(typeRef),
                                    err=str(err)))
        return
    elif isinstance(primary, ogAST.PrimInteger) \
            and actual_type.kind.startswith('Integer'):
        return
    elif isinstance(primary, ogAST.PrimReal) \
            and actual_type.kind.startswith('Real'):
        return
    elif isinstance(primary, ogAST.PrimBoolean) \
            and actual_type.kind.startswith('Boolean'):
        return
    elif (isinstance(primary, ogAST.PrimEmptyString) and
                                         actual_type.kind == 'SequenceOfType'):
        if int(actual_type.Min) == 0:
            return
        else:
            raise TypeError('SEQUENCE OF has a minimum size of '
                            + actual_type.Min + ')')
    elif isinstance(primary, ogAST.PrimSequenceOf) \
            and actual_type.kind == 'SequenceOfType':
        if (len(primary.value) < int(actual_type.Min) or
                len(primary.value) > int(actual_type.Max)):
            raise TypeError(str(len(primary.value)) +
                      ' elements in SEQUENCE OF, while constraint is [' +
                      str(actual_type.Min) + '..' + str(actual_type.Max) + ']')
        for elem in primary.value:
            check_type_compatibility(elem, actual_type.type, context)
        return
    elif isinstance(primary, ogAST.PrimSequence) \
            and actual_type.kind == 'SequenceType':
        user_nb_elem = len(primary.value.keys())
        type_nb_elem = len(actual_type.Children.keys())
        if user_nb_elem != type_nb_elem:
            raise TypeError('Wrong number of fields in SEQUENCE of type {}'
                            .format(type_name(typeRef)))
        else:
            for field, fd_data in actual_type.Children.viewitems():
                ufield = field.replace('-', '_')
                if ufield not in primary.value:
                    raise TypeError('Missing field {field} in SEQUENCE'
                                    ' of type {t1} '
                                    .format(field=ufield,
                                            t1=type_name(typeRef)))
                else:
                    # If the user field is a raw value
                    if primary.value[ufield].is_raw:
                        check_type_compatibility(primary.value[ufield],
                                                 fd_data.type, context)
                    else:
                        # Compare the types for semantic equivalence
                        try:
                            compare_types\
                              (primary.value[ufield].exprType, fd_data.type)
                        except TypeError as err:
                            raise TypeError('Field ' + ufield +
                                        ' is not of the proper type, i.e. ' +
                                        type_name(fd_data.type) +
                                        ' - ' + str(err))
        return
    elif isinstance(primary, ogAST.PrimChoiceItem) \
                              and actual_type.kind.startswith('Choice'):
        for choicekey, choice in actual_type.Children.viewitems():
            if choicekey.lower() == primary.value['choice'].lower():
                break
        else:
            raise TypeError('Non-existent choice "{choice}" in type {t1}'
                            .format(choice=primary.value['choice'],
                            t1=type_name(typeRef)))
        # compare primary.value['value']
        # with actual_type['Children'][primary.choiceItem['choice']]
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
                raise TypeError\
                           ('Field {field} in CHOICE is not of type {t1} - {e}'
                            .format(field=primary.value['choice'],
                                    t1=type_name(choice_field_type),
                                    e=str(err)))
        value.exprType = choice_field_type         # XXX
        return
    elif isinstance(primary, ogAST.PrimChoiceDeterminant) \
                                     and actual_type.kind.startswith('Choice'):
        for choicekey, choice in actual_type.EnumValues.viewitems():
            if choicekey.replace('-', '_').lower() == \
                                                   primary.inputString.lower():
                break
        else:
            raise TypeError('Non-existent choice "{choice}" in type {t1}'
                            .format(choice=primary.inputString,
                            t1=type_name(typeRef)))

    elif isinstance(primary, ogAST.PrimStringLiteral):
        # Octet strings
        basic_type = find_basic_type(typeRef)
        if(basic_type.kind.endswith('StringType') and
           int(basic_type.Min) <= len(
                          primary.value[1:-1]) <= int(basic_type.Max)):
            return
        else:
            raise TypeError('Invalid string literal - check that lenght is'
                            'within the bound limits {Min}..{Max}'.format
                            (Min=str(basic_type.Min), Max=str(basic_type.Max)))
    elif (isinstance(primary, ogAST.PrimMantissaBaseExp) and
                                            actual_type.kind == 'RealType'):
        LOG.debug('PROBABLY (it is a float but I did not check'
                  'if values are compatible)')
        return
    else:
        raise TypeError('{prim} does not match type {t1}'
                        .format(prim=primary.inputString,
                                t1=type_name(typeRef)))

def compare_types(type_a, type_b):
    '''
       Compare two types, return if they are semantically equivalent,
       otherwise raise TypeError
    '''
    LOG.debug('[compare_types]' + str(type_a) + ' and ' + str(type_b) + ': ')
    type_a = find_basic_type(type_a)
    type_b = find_basic_type(type_b)
    if type_a == type_b:
        return
    # Check if both types have basic compatibility
    simple_types = [elem for elem in (type_a, type_b) if elem.kind in
                       ('IntegerType', 'BooleanType', 'RealType', 'StringType',
                        'SequenceOfType', 'Integer32Type', 'OctetStringType')]
    if len(simple_types) < 2:
        # Either A or B is not a basic type - cannot be compatible
        raise TypeError('One of the types is not a basic type: '
                + type_name(type_a) + ' or ' + type_name(type_b))
    elif type_a.kind == type_b.kind:
        if type_a.kind == 'SequenceOfType':
            if type_a.Min == type_b.Min and type_a.Max == type_b.Max:
                compare_types(type_a.type, type_b.type)
                return
            else:
                raise TypeError('Incompatible arrays')
        return
    elif type_a.kind.endswith('StringType') and type_b.kind.endswith(
                                                                 'StringType'):
        # Allow Octet String values to be printable strings.. for convenience
        return
    elif not(type_a.kind in ('IntegerType', 'Integer32Type', 'RealType') and
             type_b.kind in ('IntegerType', 'Integer32Type', 'RealType')):
        raise TypeError('Int/Real mismatch')
    else:
        return


def find_variable(var, context):
    ''' Look for a variable name in the context and return its type '''
    result = UNKNOWN_TYPE
    LOG.debug('[find_variable] checking if ' + str(var) + ' is defined')
    # all DCL-variables
    all_visible_variables = dict(context.global_variables)
    all_visible_variables.update(context.variables)
    # First check locally, i.e. in FPAR
    try:
        for variable in context.fpar:
            if variable['name'].lower() == var.lower():
                LOG.debug(str(var) + ' is defined')
                return variable['type']
    except AttributeError:
        # No FPAR section
        pass
    for varname, (vartype, _) in all_visible_variables.viewitems():
        # Case insensitive comparison with variables
        if var.lower() == varname.lower():
            result = vartype
            LOG.debug(str(var) + ' is defined')
            return result
    for timer in context.timers:
        if var.lower() == timer.lower():
            LOG.debug(str(var) + ' is defined')
            return result

    LOG.debug('[find_variable] result: not found, raising exception')
    raise AttributeError('Variable {var} not defined'.format(var=var))


def find_type(path, context):
    '''
        Determine the type of an element using the data model,
        and the list of variables, operators and procedures
        path must contain either an index or parameters, it is not possible
        with this function to find the type of a single variable, because
        it is context-dependent (the name of a variable may conflict with the
        name of a enumeration item or a choice determinant)
    '''
    result = UNKNOWN_TYPE
    assert len(path) > 1, str(path)
    if not DV:
        raise AttributeError('Dataview is required to process types')
    LOG.debug('[find_type] ' + str(path))
    # First, find the type of the main element
    main = path[0]
    v, o = None, None
    # Try to find the name in the variables list
    try:
        result = find_variable(main, context)
    except AttributeError:
        for o in context.operators.viewkeys():
            # Case insensitive comparison with operators
            if main.lower() == o.lower():
                result = new_ref_type(context.operators[o])
                break
        else:
            if main.lower() in SPECIAL_OPERATORS:
                # Special operators require type elaboration
                if main.lower() == 'present':
                    result = type('present', (object,),
                                   {'kind': 'ChoiceEnumeratedType',
                                   'EnumValues': {}})
                    # present(choiceType): must return an enum
                    # with elements being the choice options
                    param, = path[1].get('procParams') or [None]
                    if not param:
                        raise TypeError('Missing parameter in PRESENT clause')
                    else:
                        check_type = find_variable(param.inputString, context)\
                                if param.exprType == UNKNOWN_TYPE else \
                                param.exprType
                        param_type = find_basic_type(check_type)
                        if param_type.kind != 'ChoiceType':
                            raise TypeError('PRESENT parameter'
                                         ' must be a CHOICE type:' + str(path))
                        else:
                            result.EnumValues = param_type.Children
                elif main.lower() in ('length', 'abs'):
                    # XXX length et abs: we must set Min and Max
                    # and abs may return a RealType, not always integer
                    result = type('lenabs', (object,), {'kind': 'IntegerType'})
                else: # write and writeln return void
                    pass
    if result.kind == 'ReferenceType':
        # We have more than one element and the first one is of type 'result'
        # Iterate over the path to get the type of the last element
        for elem in path[1:]:
            basic = find_basic_type(result)
            if 'procParams' in elem:
                # Discard operator parameters: they do not change the type
                continue
            # Sequence, Choice (case insensitive)
            if basic.kind in ('SequenceType', 'ChoiceType'):
                if 'index' in elem:
                    raise TypeError('Element {} cannot have an index'
                                    .format(path[0]))
                elem_asn1 = elem.replace('_', '-').lower()
                type_idx = [c for c in basic.Children
                            if c.lower() == elem_asn1]
                if type_idx:
                    result = basic.Children[type_idx[0]].type
                else:
                    raise TypeError('Field ' + elem
                                     + ' not found in expression '
                                     + '!'.join(path))
                    break
            # Sequence of
            elif basic.kind == 'SequenceOfType':
                # Can be an index or a substring
                if 'index' in elem:
                    # Index - change to the type of the Seqof elements
                    result = basic.type
                elif 'substring' in elem:
                    # Don't change the type, still a SEQUENCE OF
                    # XXX Size may differ
                    pass
            elif basic.kind == 'EnumeratedType':
                pass
            elif basic.kind.endswith('StringType'):
                # Can be an index or a substring
                if 'index' in elem:
                    raise TypeError('Index on a string is not supported')
                elif 'substring' in elem:
                    # don't change type, returns a string
                    # XXX Size may differ
                    pass
            else:
                raise TypeError('Incorrect field or index')
    return result


def fix_expression_types(expr, context):
    ''' Check/ensure type consistency in expressions having two sides '''
    if isinstance(expr, ogAST.Primary):
        return

    for side in ('left', 'right'):
        # Determine if the expression is a variable
        uk_expr = getattr(expr, side)
        if uk_expr.exprType == UNKNOWN_TYPE \
                and isinstance(uk_expr, ogAST.PrimPath) \
                and len(uk_expr.value) == 1:
            try:
                #exprType = find_variable(uk_expr.inputString, context)
                exprType = find_variable(uk_expr.value[0], context)
                # Differentiate DCL and FPAR variables
                use_type = ogAST.PrimVariable
                if isinstance(context, ogAST.Procedure):
                    for each in context.fpar:
                        if each['name'].lower() == uk_expr.value[0].lower():
                            use_type = ogAST.PrimFPAR
                            break
                setattr(expr, side, use_type(primary=uk_expr))
                getattr(expr, side).exprType = exprType
            except AttributeError:
                pass

    # If a side of the expression is of Enumerated of Choice type, check if
    # the other side is a literal of that sort, and change type accordingly
    for side in (('left', 'right'), ('right', 'left')):
        side_type = find_basic_type(getattr(expr, side[0]).exprType).kind
        if side_type == 'EnumeratedType':
            prim = ogAST.PrimEnumeratedValue(primary=getattr(expr, side[1]))
        elif side_type == 'ChoiceEnumeratedType':
            prim = ogAST.PrimChoiceDeterminant(primary=getattr(expr, side[1]))
        try:
            check_type_compatibility(prim, getattr(expr, side[0]).exprType,
                                     context)
            setattr(expr, side[1], prim)
            getattr(expr, side[1]).exprType = getattr(expr, side[0]).exprType
        except (UnboundLocalError, AttributeError, TypeError):
            pass

    # If a side type remains unknown, check if it is an ASN.1 constant
    for side in (('left', 'right'), ('right', 'left')):
        value = getattr(expr, side[0])
        if value.exprType == UNKNOWN_TYPE and is_constant(value):
            setattr(expr, side[0], ogAST.PrimConstant(primary=value))
            getattr(expr, side[0]).exprType = getattr(expr, side[1]).exprType

    for side in (expr.right, expr.left):
        if side.is_raw:
            raw_expr = side
        else:
            typed_expr = side
            ref_type = typed_expr.exprType

    # Type check that is specific to IN expressions
    if isinstance(expr, ogAST.ExprIn):
        # check that left part is a SEQUENCE OF or a string
        container_basic_type = find_basic_type(expr.left.exprType)
        if container_basic_type.kind == 'SequenceOfType':
            ref_type = container_basic_type.type
        elif container_basic_type.kind.endswith('StringType'):
            ref_type = container_basic_type
        else:
            raise TypeError('IN expression: right part must be a list')
        compare_types(expr.right.exprType, ref_type)
        return

    if expr.right.is_raw == expr.left.is_raw == False:
        unknown = [uk_expr for uk_expr in expr.right, expr.left
                   if uk_expr.exprType == UNKNOWN_TYPE]
        if unknown:
            raise TypeError('Cannot resolve type of "{}"'
                            .format(unknown[0].inputString))

    # In Sequence, Choice, SEQUENCE OF, and IfThenElse expressions,
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
                check_expr.left = ogAST.PrimPath()
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
            check_expr.left = ogAST.PrimPath()
            check_expr.left.exprType = expected_type
            check_expr.right = expr.right.value['value']
            fix_expression_types(check_expr, context)
            expr.right.value['value'] = check_expr.right
    elif isinstance(expr.right, ogAST.PrimIfThenElse):
        for det in ('then', 'else'):
            if expr.right.value[det].exprType == UNKNOWN_TYPE:
                expr.right.value[det].exprType = expr.left.exprType
            # Recursively fix possibly missing types in the expression
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimPath()
            check_expr.left.exprType = expr.left.exprType
            check_expr.right = expr.right.value[det]
            fix_expression_types(check_expr, context)
            expr.right.value[det] = check_expr.right
    elif isinstance(expr.right, ogAST.PrimSequenceOf):
        asn_type = find_basic_type(expr.left.exprType).type
        for idx, elem in enumerate(expr.right.value):
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimPath()
            check_expr.left.exprType = asn_type
            check_expr.right = elem
            fix_expression_types(check_expr, context)
            expr.right.value[idx] = check_expr.right
        # the type of the raw PrimSequenceOf can be set now
        expr.right.exprType.type = asn_type

    if isinstance(expr, (ogAST.ExprAnd, ogAST.ExprOr, ogAST.ExprXor)):
        # Bitwise operators: check that both sides are booleans
        for side in expr.left, expr.right:
            basic_type = find_basic_type(side.exprType)
            if basic_type.kind in ('BooleanType', 'BitStringType'):
                continue
            elif basic_type.kind == 'SequenceOfType':
                if find_basic_type(side.exprType).type.kind == 'BooleanType':
                    continue
            else:
                raise TypeError('Bitwise operators only work with '
                                'booleans and arrays of booleans')
    if expr.right.is_raw != expr.left.is_raw:
        check_type_compatibility(raw_expr, ref_type, context)
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

def primary_value(root, context=None):
    '''
        Process a primary expression such as a!b(4)!c(hello)
        or { x 1, y a:2 } (ASN.1 Value Notation)
        Try to determine the type of the primary when possible
        There are three cases where the type cannot be determined at all:
        (1) if the primary is a single literal (can be a var, enum or choice)
        (2) if the primary is a sequence literal
        (3) if the type is a choice literal
        In case of a SEQUENCE OF, the Min/Max values are set
    '''
    warnings = []
    errors = []
    prim = None
    global TMPVAR
    def primary_elem(child):
        ''' Process a single token '''
        prim = None
        if child.type == lexer.ID:
            prim = ogAST.PrimPath()
            prim.value = [child.text]
            prim.exprType = UNKNOWN_TYPE
        elif child.type == lexer.INT:
            prim = ogAST.PrimInteger()
            prim.value = [child.text.lower()]
            prim.exprType = type('PrInt', (object,),
                 {'kind': 'IntegerType', 'Min': child.text, 'Max': child.text})
        elif child.type in (lexer.TRUE, lexer.FALSE):
            prim = ogAST.PrimBoolean()
            prim.value = [child.text.lower()]
            prim.exprType = type('PrBool', (object,), {'kind': 'BooleanType'})
        elif child.type == lexer.FLOAT:
            prim = ogAST.PrimReal()
            prim.value = [child.getChild(0).text]
            prim.exprType = type('PrReal', (object,),
                 {'kind': 'RealType',
                  'Min': prim.value[0], 'Max': prim.value[0]})
        elif child.type == lexer.STRING:
            prim = ogAST.PrimStringLiteral()
            prim.value = child.getChild(0).text
            prim.exprType = type('PrStr', (object,),
                          {'kind': 'StringType', 'Min': str(len(prim.value)-2),
                           'Max': str(len(prim.value)-2)})
        elif child.type == lexer.FLOAT2:
            prim = ogAST.PrimMantissaBaseExp()
            mant = float(child.getChild(0).toString())
            base = int(child.getChild(1).toString())
            exp = int(child.getChild(2).toString())
            # Compute mantissa * base**exponent to get the value type range
            value = float(mant * pow(base, exp))
            prim.value = {'mantissa': mant, 'base': base, 'exponent': exp}
            prim.exprType = type('PrMantissa', (object,),
                 {'kind': 'RealType',
                  'Min': str(value), 'Max': str(value)})
        elif child.type == lexer.EMPTYSTR:
            # Empty SEQUENCE OF (i.e. "{}")
            prim = ogAST.PrimEmptyString()
            prim.exprType = type('PrES', (object,), {'kind': 'SequenceOfType',
                'Min': '0', 'Max': '0'})
        elif child.type == lexer.CHOICE:
            prim = ogAST.PrimChoiceItem()
            choice = child.getChild(0).toString()
            expr, err, warn = expression(child.getChild(1), context)
            errors.extend(err)
            warnings.extend(warn)
            prim.value = {'choice': choice, 'value': expr}
            prim.exprType = UNKNOWN_TYPE
        elif child.type == lexer.SEQUENCE:
            prim = ogAST.PrimSequence()
            prim.value = {}
            for elem in child.getChildren():
                if elem.type == lexer.ID:
                    field_name = elem.text
                else:
                    prim.value[field_name], err, warn = (
                                                     expression(elem, context))
                    errors.extend(err)
                    warnings.extend(warn)
            prim.exprType = UNKNOWN_TYPE
        elif child.type == lexer.SEQOF:
            prim = ogAST.PrimSequenceOf()
            prim.value = []
            for elem in child.getChildren():
                # SEQUENCE OF elements cannot have fieldnames/indexes
                prim_elem = primary_elem(elem)
                prim_elem.inputString = get_input_string(elem)
                prim_elem.line = elem.getLine()
                prim_elem.charPositionInLine = elem.getCharPositionInLine()
                prim.value.append(prim_elem)
            prim.exprType = type('PrSO', (object,), {'kind': 'SequenceOfType',
             'Min': str(len(child.children)), 'Max': str(len(child.children))})
        elif child.type == lexer.BITSTR:
            prim = ogAST.PrimBitStringLiteral()
            warnings.append('Bit string literal not supported yet')
        elif child.type == lexer.OCTSTR:
            prim = ogAST.PrimOctetStringLiteral()
            warnings.append('Octet string literal not supported yet')
        else:
            warnings.append('Unsupported primary construct, type:' +
                    str(child.type) +
                    ' (line ' + str(child.getLine()) + ')')
        return prim

    prim = primary_elem(root.getChild(0))

    # Process fields or params, if any
    for child in root.children[slice(1, len(root.children))]:
        if not isinstance(prim, ogAST.PrimPath):
            errors.append('Ground expression cannot have index or params: ' +
                           get_input_string(root))
        if child.type == lexer.PARAMS:
            # Cover parameters of operator calls within a task
            # but not parameters of output or procedure calls
            # (Except procedure calls embedded in a task)
            expr_list, err, warn = expression_list(child, context)
            errors.extend(err)
            warnings.extend(warn)
            procedures_list = [proc.inputString.lower() for proc in
                    context.procedures]
            if prim.value[0].lower() in (SPECIAL_OPERATORS.keys()
                                         + procedures_list):
                # here we must check/set the type of each param
                try:
                    check_and_fix_op_params(
                            prim.value[0].lower(), expr_list, context)
                except (AttributeError, TypeError) as err:
                    errors.append(str(err) + '- ' + get_input_string(root))
                prim.value.append({'procParams': expr_list})
            else:
                if len(expr_list) == 1:
                    # Index (only one param)
                    prim.value.append({'index': expr_list})
                elif len(expr_list) == 2:
                    # Substring (range, two params)
                    prim.value.append(
                            {'substring': expr_list, 'tmpVar': TMPVAR})
                    TMPVAR += 1
                else:
                    errors.append('Wrong number of parameters')
        elif child.type == lexer.FIELD_NAME:
            prim.value.append(child.getChild(0).text)

    # If there were parameters or index, try to determine the type of
    # the expression
    if isinstance(prim, ogAST.PrimPath) and len(prim.value) > 1:
        try:
            prim.exprType = find_type(prim.value, context)
        except TypeError as err:
            errors.append('Type of expression "'
                           + get_input_string(root)
                           + '" not found: ' +str(err))
        except AttributeError as err:
            LOG.debug('[find_types] ' + str(err))
    if prim:
        prim.inputString = get_input_string(root)
    else:
        prim = ogAST.PrimPath()
    return prim, errors, warnings


def primary(root, context):
    ''' Process a primary (-/NOT value) '''
    warnings = []
    errors = []
    op_not, op_minus = False, False
    prim = None
    for child in root.getChildren():
        if child.type == lexer.NOT:
            op_not = True
        elif child.type == lexer.MINUS:
            op_minus = True
        elif child.type == lexer.PRIMARY_ID:
            # Variable reference, indexed values, or ASN.1 value notation
            prim, err, warn = primary_value(child, context=context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.EXPRESSION:
            prim, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.IFTHENELSE:
            prim = ogAST.PrimIfThenElse()
            if_part, then_part, else_part = child.getChildren()
            if_expr, err, warn = expression(if_part, context)
            errors.extend(err)
            warnings.extend(warn)
            then_expr, err, warn = expression(then_part, context)
            errors.extend(err)
            warnings.extend(warn)
            else_expr, err, warn = expression(else_part, context)
            errors.extend(err)
            warnings.extend(warn)
            global TMPVAR
            prim.value = {'if': if_expr,
                          'then': then_expr,
                          'else': else_expr,
                          'tmpVar': TMPVAR}
            prim.exprType = UNKNOWN_TYPE
            TMPVAR += 1
        else:
            warnings.append('Unsupported primary child type:' +
                    str(child.type) + ' (line ' +
                    str(child.getLine()) + ')')
    if prim:
        prim.inputString = get_input_string(root)
        prim.line = root.getLine()
        prim.charPositionInLine = root.getCharPositionInLine()
    return prim, errors, warnings

def expression(root, context):
    ''' Expression analysis (e.g. 5+5*hello(world)!foo) '''
    errors = []
    warnings = []
    global TMPVAR
    if root.type != lexer.PRIMARY:
        expr = OPKIND[root.type](get_input_string(root), root.getLine(),
                                 root.getCharPositionInLine())
        expr.exprType = UNKNOWN_TYPE

    if root.type in (lexer.PLUS,
                     lexer.ASTERISK,
                     lexer.DASH,
                     lexer.APPEND,
                     lexer.IMPLIES,
                     lexer.OR,
                     lexer.XOR,
                     lexer.AND,
                     lexer.EQ,
                     lexer.NEQ,
                     lexer.GT,
                     lexer.GE,
                     lexer.LT,
                     lexer.LE,
                     lexer.IN,
                     lexer.DIV,
                     lexer.MOD,
                     lexer.REM):

        left, right = root.getChildren()

        if root.type == lexer.IN:
            # Left and right are reversed for IN operator
            left, right = right, left

        expr.left, err_left, warn_left = expression(left, context)
        expr.right, err_right, warn_right = expression(right, context)
        errors.extend(err_left)
        warnings.extend(warn_left)
        errors.extend(err_right)
        warnings.extend(warn_right)

        try:
            fix_expression_types(expr, context)
        except (AttributeError, TypeError) as err:
            errors.append('Types are incompatible in expression: left (' +
                expr.left.inputString + ', type= ' +
                type_name(expr.left.exprType) + '), right (' +
                expr.right.inputString + ', type= ' +
                type_name(expr.right.exprType) + ') ' + str(err))

    if root.type in (lexer.EQ,
                     lexer.NEQ,
                     lexer.GT,
                     lexer.GE,
                     lexer.LT,
                     lexer.LE,
                     lexer.IN):
        expr.exprType = BOOLEAN
#    elif root.type == lexer.PLUS:
        # Adjust type constraint upper range with sum of expressions
        # Create a new type to store the new constraint
        # INCORRECT TO DO IT HERE - we must check right and left types FIRST
#       expr.exprType = type('Plus_Type',
#                           (find_basic_type(expr.left.exprType),), {})
#       expr.exprType.Max = str(int(find_basic_type(expr.left.exprType).Max) +
#                        int(find_basic_type(expr.right.exprType).Max))
    elif root.type in (lexer.OR, lexer.AND, lexer.XOR):
        # in the case of bitwise operators, if both sides are arrays,
        # then the result is an array too
        basic_left = find_basic_type(expr.left.exprType)
        basic_right = find_basic_type(expr.right.exprType)
        if basic_left.kind == basic_right.kind == 'BooleanType':
            expr.exprType = BOOLEAN
        else:
            expr.exprType = expr.left.exprType

    elif root.type in (lexer.PLUS,
                       lexer.ASTERISK,
                       lexer.DASH,
                       lexer.APPEND,
                       lexer.REM,
                       lexer.MOD):
        expr.exprType = expr.left.exprType

    if root.type == lexer.PRIMARY:
        expr, err, warn = primary(root, context)
        expr.inputString = get_input_string(root)
        expr.line = root.getLine()
        expr.charPositionInLine = root.getCharPositionInLine()
        errors.extend(err)
        warnings.extend(warn)

    # Expressions may need intermediate storage for code generation
    expr.tmpVar = TMPVAR
    TMPVAR += 1
    return expr, errors, warnings

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
                errors.append(str(err) + '(line ' + str(child.getLine()) + ')')
        elif child.type == lexer.GROUND:
            # Default value for a variable - needs to be a ground expression
            def_value, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
            ground_error = False

            expr = ogAST.ExprAssign()
            expr.left = ogAST.PrimPath()
            expr.left.inputString = var[-1]
            expr.left.exprType = asn1_sort
            expr.right = def_value
            try:
                fix_expression_types(expr, context)
                def_value = expr.right
            except(AttributeError, TypeError) as err:
                #print (traceback.format_exc())
                errors.append('Types are incompatible in DCL assignment: '
                    'left (' +
                    expr.left.inputString + ', type= ' +
                    type_name(expr.left.exprType) + '), right (' +
                    expr.right.inputString + ', type= ' +
                    type_name(expr.right.exprType) + ') ' + str(err))
            else:
                def_value.exprType = asn1_sort

            if not def_value.is_raw and not is_constant(def_value):
                errors.append('In variable declaration {}: default'
                              ' value is not a valid ground expression'.
                              format(var[-1]))
        else:
            warnings.append('Unsupported variables construct type: ' +
                    str(child.type))
    for variable in var:
        # Add to the context and text area AST entries
        context.variables[variable] = (asn1_sort, def_value)
        ta_ast.variables[variable] = (asn1_sort, def_value)
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
            if child.type == lexer.INOUT:
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
    ''' Parse a composite state definition '''
    comp = ogAST.CompositeState()
    errors, warnings = [], []
    # Create a list of all inherited data
    try:
        comp.global_variables = dict(context.variables)
        comp.global_variables.update(context.global_variables)
        comp.input_signals = context.input_signals
        comp.output_signals = context.output_signals
        comp.procedures = context.procedures
        comp.operators = dict(context.operators)
    except AttributeError:
        LOG.debug('Procedure context is undefined')
    # Gather the list of states defined in the composite state
    # and map a list of transitions to each state
    comp.mapping = {name: [] for name in get_state_list(root)}
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
            errors.extend(err)
            warnings.extend(warn)
            comp.content.textAreas.append(textarea)
        elif child.type == lexer.PROCEDURE:
            new_proc, err, warn = procedure(child, context=comp)
            errors.extend(err)
            warnings.extend(warn)
            if new_proc.inputString.strip().lower() == 'entry':
                comp.entry_procedure = new_proc
            elif new_proc.inputString.strip().lower() == 'exit':
                comp.exit_procedure = new_proc
            comp.content.inner_procedures.append(new_proc)
        elif child.type == lexer.COMPOSITE_STATE:
            inner_comp, err, warn = composite_state(child,
                                                    parent=None,
                                                    context=comp)
            errors.extend(err)
            warnings.extend(warn)
            comp.composite_states.append(inner_comp)
        elif child.type == lexer.STATE:
            # STATE - fills up the 'mapping' structure.
            newstate, err, warn = state(child, parent=None, context=comp)
            errors.extend(err)
            warnings.extend(warn)
            comp.content.states.append(newstate)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(child, parent=None, context=comp)
            errors.extend(err)
            warnings.extend(warn)
            comp.content.floating_labels.append(lab)
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            st, err, warn = start(child, context=comp)
            errors.extend(err)
            warnings.extend(warn)
            if st.inputString:
                comp.content.named_start.append(st)
            elif not comp.content.start:
                comp.content.start = st
            else:
                errors.append('Only one unnamed START transition is allowed')
        else:
            warnings.append(
                    'Unsupported construct in nested state, type: ' +
                    str(child.type) + ' - line ' + str(child.getLine()) +
                    ' - state name: ' + str(comp.statename))
    return comp, errors, warnings


def procedure(root, parent=None, context=None):
    ''' Parse a procedure definition '''
    proc = ogAST.Procedure()
    errors = []
    warnings = []
    # Create a list of all inherited data
    try:
        proc.global_variables = dict(context.variables)
        proc.global_variables.update(context.global_variables)
        proc.input_signals = context.input_signals
        proc.output_signals = context.output_signals
        proc.procedures = context.procedures
        proc.operators = dict(context.operators)
    except AttributeError:
        LOG.debug('Procedure context is undefined')
    # Gather the list of states defined in the procedure
    # and create a mapping of transitions to each state
    # (Note, procedures in OG currently do NOT support states)
    proc.mapping = {name: [] for name in get_state_list(root)}
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            proc.pos_x, proc.pos_y, proc.width, proc.height = cif(child)
        elif child.type == lexer.ID:
            proc.line = child.getLine()
            proc.charPositionInLine = child.getCharPositionInLine()
            proc.inputString = child.toString()
        elif child.type == lexer.COMMENT:
            proc.comment, _, ___ = end(child)
        elif child.type == lexer.TEXTAREA:
            textarea, err, warn = text_area(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.textAreas.append(textarea)
        elif child.type == lexer.PROCEDURE:
            new_proc, err, warn = procedure(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.inner_procedures.append(new_proc)
        elif child.type == lexer.EXTERNAL:
            proc.external = True
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            proc.fpar = params
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            proc.content.start, err, warn = start(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.STATE:
            # STATE - fills up the 'mapping' structure.
            newstate, err, warn = state(child, parent=None, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.states.append(newstate)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(child, parent=None, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.floating_labels.append(lab)
        else:
            warnings.append(
                    'Unsupported construct in procedure, type: ' +
                    str(child.type) + ' - line ' + str(child.getLine()) +
                    ' - string: ' + str(proc.inputString))
    for each in proc.terminators:
        # check that RETURN statements type is correct
        if not proc.return_type and each.return_expr:
            errors.append('No return value expected in procedure '
                          + proc.inputString)
        elif proc.return_type and each.return_expr:
            check_expr = ogAST.ExprAssign()
            check_expr.left = ogAST.PrimPath()
            check_expr.left.exprType = proc.return_type
            check_expr.right = each.return_expr
            try:
                fix_expression_types(check_expr, context)
            except (TypeError, AttributeError) as err:
                errors.append(str(err))
            # Id of fd_expr may have changed (enumerated, choice)
            each.return_expr = check_expr.right
        elif proc.return_type and not each.return_expr:
            errors.append('Missing return value in procedure '
                          + proc.inputString)
        else:
            continue
    return proc, errors, warnings


def floating_label(root, parent, context):
    ''' Floating label: name and optional transition '''
    _ = parent
    errors = []
    warnings = []
    lab = ogAST.Floating_label()
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
                    'Unsupported construct in floating label: ' +
                    str(child.type))
    if not lab.transition:
        warnings.append('Floating labels not followed by a transition: ' +
                        str(lab.inputString))
    # At the end of the label parsing, get the the list of terminators that
    # the transition contains by making a diff with the list at context
    # level (we counted the number of terminators before parsing the item)
    lab.terminators = list(context.terminators[terminators:])
    return lab, errors, warnings


def text_area_content(root, ta_ast, context):
    ''' Content of a text area: DCL, operators, procedures  '''
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.DCL:
            err, warn = dcl(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.PROCEDURE:
            proc, err, warn = procedure(child, context=context)
            errors.extend(err)
            warnings.extend(warn)
            # Add procedure to the container (process or procedure)
            context.content.inner_procedures.append(proc)
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            try:
                if context.fpar:
                    errors.append('Duplicate declaration of FPAR section')
                else:
                    context.fpar = params
            except AttributeError:
                errors.append('Only procedures can have an FPAR section')
        elif child.type == lexer.TIMER:
            context.timers.extend(timer.text.lower()
                                            for timer in child.children)
        else:
            warnings.append(
                    'Unsupported construct in text area content, type: ' +
                    str(child.type))
    return errors, warnings

def text_area(root, parent=None, context=None):
    ''' Process a text area (DCL, procedure, operators declarations '''
    errors = []
    warnings = []
    ta = ogAST.TextArea()
    coord = False
    for child in root.getChildren():
        if child.type == lexer.CIF:
            userTextStartIndex = child.getTokenStopIndex() + 1
            ta.pos_x, ta.pos_y, ta.width, ta.height = cif(child)
            coord = True
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
    if coord:
        errors = [[e, [ta.pos_x, ta.pos_y]] for e in errors]
        warnings = [[w, [ta.pos_x, ta.pos_y]] for w in warnings]
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
    return new_signal, errors, warnings

def single_route(root):
    ''' Route (from id to id with [signal id] '''
    route = {'source': root.getChild(0).text,
             'dest': root.getChild(1).text,
             'signals': [sig.text for sig in root.getChildren()[2:]]}
    return route

def channel_signalroute(root):
    ''' Channel/signalroute definition (connections) '''
    # no AST entry for edges - a simple dict is sufficient
    # (name, [route])
    edge = {'routes': []}
    for child in root.getChildren():
        if child.type == lexer.ID:
            edge['name'] = child.text
        elif child.type == lexer.ROUTE:
            edge['routes'].append(single_route(child))
    return edge

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
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.SIGNALROUTE:
            sigroute = channel_signalroute(child)
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
    for child in root.getChildren():
        if child.type == lexer.ID:
            system.name = child.text
            LOG.debug('System name: ' + system.name)
        elif child.type == lexer.SIGNAL:
            sig, err, warn = signal(child)
            errors.extend(err)
            warnings.extend(warn)
            system.signals.append(sig)
            LOG.debug('Found signal: ' + str(sig))
        elif child.type == lexer.PROCEDURE:
            LOG.debug('procedure declaration')
            proc, err, warn = procedure(
                    child, parent=None, context=system)
            errors.extend(err)
            warnings.extend(warn)
            system.procedures.append(proc)
            LOG.debug('Added procedure: ' + proc.inputString)
        elif child.type == lexer.CHANNEL:
            LOG.debug('channel declaration')
            channel = channel_signalroute(child)
            system.channels.append(channel)
        elif child.type == lexer.BLOCK:
            LOG.debug('block declaration')
            block, err, warn = block_definition(child, parent=system)
            errors.extend(err)
            warnings.extend(warn)
        else:
            warnings.append('Unsupported construct in system: ' +
                    str(child.type))
    return system, errors, warnings

def process_definition(root, parent=None, context=None):
    ''' Process definition analysis '''
    errors = []
    warnings = []
    process = ogAST.Process()
    process.filename = node_filename(root)
    process.parent = parent
    parent.processes.append(process)
    coord = False
    # Prepare the transition/state mapping
    process.mapping = {name: [] for name in get_state_list(root)}
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            process.pos_x, process.pos_y, process.width, process.height =\
                    cif(child)
            coord = True
        elif child.type == lexer.ID:
            # Get process (taste function) name
            process.processName = child.text
            try:
                # Retrieve process interface (PI/RI)
                async_signals, procedures = get_interfaces(
                        parent, child.text)
                process.input_signals.extend([sig for sig in async_signals
                    if sig['direction'] == 'in'])
                process.output_signals.extend([sig for sig in async_signals
                    if sig['direction'] == 'out'])
                process.procedures.extend(procedures)
            except AttributeError as err:
                LOG.error('Discarding process ' + child.text + ' ' + str(err))
            except TypeError as error:
                LOG.debug(str(error))
                errors.append(str(error))
            if coord:
                errors = [[e, [process.pos_x, process.pos_y]] for e in errors]
                warnings = [[w, [process.pos_x, process.pos_y]]
                             for w in warnings]
        elif child.type == lexer.TEXTAREA:
            # Text zone where variables and operators are declared
            textarea, err, warn = text_area(child, context=process)
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
        elif child.type == lexer.PROCEDURE:
            proc, err, warn = procedure(
                    child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.inner_procedures.append(proc)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(
                    child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.floating_labels.append(lab)
        elif child.type == lexer.COMPOSITE_STATE:
            comp, err, warn = composite_state(child,
                                              parent=None,
                                              context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.composite_states.append(comp)
        elif child.type == lexer.REFERENCED:
            process.referenced = True
        else:
            warnings.append('Unsupported process definition child: ' +
                             sdl92Parser.tokenNames[child.type] +
                            ' - line ' + str(child.getLine()))
    return process, errors, warnings

def input_part(root, parent, context):
    ''' Parse an INPUT - set of TASTE provided interfaces '''
    i = ogAST.Input()
    warnings, errors = [], []
    coord = False
    # Keep track of the number of terminator statements follow the input
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            i.pos_x, i.pos_y, i.width, i.height = cif(child)
            coord = True
        elif child.type == lexer.INPUTLIST:
            i.inputString = get_input_string(child)
            i.line = child.getLine()
            i.charPositionInLine = child.getCharPositionInLine()
            # get input name and parameters (support for one parameter only)
            sig_param_type, user_param_type = None, None
            inputnames = [c for c in child.getChildren()
                                                  if c.type != lexer.PARAMS]
            for inputname in inputnames:
                for inp_sig in context.input_signals:
                    if inp_sig['name'].lower() == inputname.text.lower():
                        i.inputlist.append(inp_sig['name'])
                        sig_param_type = inp_sig.get('type')
                        break
                else:
                    for timer in context.timers:
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
                    user_param_type = find_variable(user_param.text, context)
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
            if coord:
                errors = [[e, [i.pos_x, i.pos_y]] for e in errors]
                warnings = [[w, [i.pos_x, i.pos_y]] for w in warnings]
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
            trans, err, warn = transition(
                                    child, parent=i, context=context)
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
        else:
            warnings.append('Unsupported INPUT child type: ' +
                    str(child.type))
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
    errors = []
    warnings = []
    state_def = ogAST.State()
    asterisk_state = False
    asterisk_input = None
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            (state_def.pos_x, state_def.pos_y,
            state_def.width, state_def.height) = cif(child)
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
                if st not in (exceptions, 'START'):
                    state_def.statelist.append(st)
        elif child.type == lexer.INPUT:
            # A transition triggered by an INPUT
            inp, err, warn = \
                           input_part(child, parent=state_def, context=context)
            errors.extend(err)
            warnings.extend(warn)
            try:
                for statename in state_def.statelist:
                    context.mapping[statename.lower()].append(inp)
            except KeyError:
                warnings.append('State definition missing')
            state_def.inputs.append(inp)
            if inp.inputString.strip() == '*':
                if asterisk_input:
                    errors.append('Multiple asterisk inputs under state ' +
                            str(state_def.inputString))
                else:
                    asterisk_input = inp
        elif child.type == lexer.CONNECT:
            if asterisk_state or len(state_def.statelist) != 1 \
                 or (state_def.statelist[0].lower()
                 not in (comp.statename for comp in context.composite_states)):
                errors.append('State {} is not a composite state and cannot '
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
        else:
            warnings.append('Unsupported STATE definition child type: ' +
                str(child.type))
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

    return state_def, errors, warnings


def connect_part(root, parent, context):
    ''' Connection of a nested state exit point with a transition
        Very similar to INPUT '''
    errors, warnings = [], []
    coord = False
    conn = ogAST.Connect()
    try:
        statename = parent.statelist[0].lower()
    except AttributeError:
        # Ignore missing parent/statelist to allow local syntax check
        statename = ''
    id_token = []
    # Keep track of the number of terminator statements follow the input
    # useful if we want to render graphs from the SDL model
    terms = len(context.terminators)
    # Retrieve composite state
    try:
        nested, = (comp for comp in context.composite_states
                   if comp.statename == statename)
    except ValueError:
        # Ignore unexisting state - to allow local syntax check
        nested = ogAST.CompositeState()

    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            conn.pos_x, conn.pos_y, conn.width, conn.height = cif(child)
            coord = True
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
            errors.append('Exit point {ep} not defined in state {st}'
                          .format(ep=exitp, st=statename))
        terminators = [term for term in nested.terminators
                       if term.kind == 'return'
                       and term.inputString.lower() == exitp]
        if not terminators:
            errors.append('No {rs} return statement in nested state {st}'
                          .format(rs=exitp, st=statename))
        for each in terminators:
            # Set transition ID, referencing process.transitions
            each.next_id = trans_id
    # Set list of terminators
    conn.terminators = list(context.terminators[terms:])
    # Report errors with symbol coordinates
    if coord:
        errors = [[e, [conn.pos_x, conn.pos_y]] for e in errors]
        warnings = [[w, [conn.pos_x, conn.pos_y]] for w in warnings]
    return conn, errors, warnings


def cif(root):
    ''' Return the CIF coordinates '''
    result = []
    for child in root.getChildren():
        if child.type == lexer.DASH:
            val = -int(child.getChild(0).toString())
        else:
            val = int(child.toString())
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
        elif child.type == lexer.StringLiteral:
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
    body = {}
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
        else:
            warnings.append('Unsupported output body type:' +
                    str(child.type))
    # Check/set the type of each param
    try:
        check_and_fix_op_params(body.get('outputName', ''),
                                body.get('params', []),
                                context)
    except (AttributeError, TypeError) as op_err:
        errors.append(str(op_err) + ' - ' + get_input_string(root))
        LOG.debug('[outputbody] call check_and_fix_op_params : '
                    + get_input_string(root) + str(op_err))
        LOG.debug(str(traceback.format_exc()))
    if body.get('params'):
        body['tmpVars'] = []
        global TMPVAR
        for _ in range(len(body['params'])):
            body['tmpVars'].append(TMPVAR)
            TMPVAR += 1
    return body, errors, warnings


def output(root, parent, out_ast=None, context=None):
    ''' Parse an OUTPUT :  set of asynchronous required interface(s) '''
    errors = []
    warnings = []
    coord = False
    out_ast = out_ast or ogAST.Output() # syntax checker passes no ast
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            out_ast.pos_x, out_ast.pos_y, out_ast.width, out_ast.height = \
                    cif(child)
            coord = True
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
        else:
            warnings.append('Unsupported output child type: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    if coord:
        errors = [[e, [out_ast.pos_x, out_ast.pos_y]] for e in errors]
        warnings = [[w, [out_ast.pos_x, out_ast.pos_y]] for w in warnings]
    return out_ast, errors, warnings


def alternative_part(root, parent, context):
    ''' Parse a decision answer '''
    errors = []
    warnings = []
    ans = ogAST.Answer()
    coord = False
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            ans.pos_x, ans.pos_y, ans.width, ans.height = cif(child)
            coord = True
        elif child.type == lexer.CLOSED_RANGE:
            ans.kind = 'closed_range'
            ans.closedRange = [float(child.getChild(0).toString()),
                              float(child.getChild(1).toString())]
        elif child.type == lexer.CONSTANT:
            ans.kind = 'constant'
            ans.constant, err, warn = expression(
                                        child.getChild(0), context)
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
                    ans.openRangeOp = OPKIND[c.type]
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
            if coord:
                errors = [[e, [ans.pos_x, ans.pos_y]] for e in errors]
                warnings = [[w, [ans.pos_x, ans.pos_y]] for w in warnings]
    return ans, errors, warnings


def decision(root, parent, context):
    ''' Parse a DECISION '''
    errors = []
    warnings = []
    dec = ogAST.Decision()
    global TMPVAR
    dec.tmpVar = TMPVAR
    TMPVAR += 1
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            dec.pos_x, dec.pos_y, dec.width, dec.height = cif(child)
        elif child.type == lexer.QUESTION:
            dec.kind = 'question'
            decisionExpr, err, warn = expression(
                                        child.getChild(0), context)
            for e in err:
                errors.append([e, [dec.pos_x, dec.pos_y]])
            for w in warn:
                warnings.append([w, [dec.pos_x, dec.pos_y]])
            dec.question = decisionExpr
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
            dec.kind = 'any'
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
            dec.kind = child.toString()
            a = ogAST.Answer()
            a.inputString = 'ELSE'
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
        else:
            warnings.append(['Unsupported DECISION child type: ' +
                str(child.type), [dec.pos_x, dec.pos_y]])
        # Make type checks to be sure that question and answers are compatible
        for ans in dec.answers:
            if ans.kind in ('constant', 'open_range'):
                expr = ans.openRangeOp()
                expr.left = dec.question
                expr.right = ans.constant
                try:
                    fix_expression_types(expr, context)
                    if dec.question.exprType == UNKNOWN_TYPE:
                        dec.question = expr.left
                    ans.constant = expr.right
                except (AttributeError, TypeError) as err:
                    errors.append('Types are incompatible in DECISION: '
                        'question (' + expr.left.inputString + ', type= ' +
                        type_name(expr.left.exprType) + '), answer (' +
                        expr.right.inputString + ', type= ' +
                        type_name(expr.right.exprType) + ') ' + str(err))
    return dec, errors, warnings


def nextstate(root, context):
    ''' Parse a NEXTSTATE [VIA State_Entry_Point] '''
    next_state_id, via, entrypoint = '', None, None
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
                    raise TypeError('State {} is not a composite state'
                                    .format(next_state_id))
                else:
                    if entrypoint.lower() not in composite.state_entrypoints:
                        raise TypeError('State {s} has no "{p}" entrypoint'
                                        .format(s=next_state_id, p=entrypoint))
                    for each in composite.content.named_start:
                        if each.inputString == entrypoint.lower() + '_START':
                            break
                    else:
                        raise TypeError('Entrypoint {p} in state {s} is '
                                        'declared but not defined'.format
                                        (s=next_state_id, p=entrypoint))
            else:
                raise TypeError('"History" NEXTSTATE'
                                 ' cannot have a "via" clause')
        else:
            raise TypeError('NEXTSTATE undefined construct')
    return next_state_id, via, entrypoint


def terminator_statement(root, parent, context):
    ''' Parse a terminator (NEXTSTATE, JOIN, STOP) '''
    errors = []
    warnings = []
    t = ogAST.Terminator()
    coord = False
    for term in root.getChildren():
        if term.type == lexer.CIF:
            t.pos_x, t.pos_y, t.width, t.height = cif(term)
            coord = True
        elif term.type == lexer.LABEL:
            lab, err, warn = label(term, parent=parent)
            errors.extend(err)
            warnings.extend(warn)
            t.label = lab
            context.labels.append(lab)
            lab.terminators = [t]
        elif term.type == lexer.NEXTSTATE:
            t.kind = 'next_state'
            try:
                t.inputString, t.via, t.entrypoint = nextstate(term, context)
            except TypeError as err:
                errors.append(str(err))
            t.line = term.getChild(0).getLine()
            t.charPositionInLine = term.getChild(0).getCharPositionInLine()
            # Add next state infos at process level
            # Used in rendering backends to merge a NEXTSTATE with a STATE
            context.terminators.append(t)
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
    if coord:
        errors = [[e, [t.pos_x, t.pos_y]] for e in errors]
        warnings = [[w, [t.pos_x, t.pos_y]] for w in warnings]
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
    ''' Parse an assignation (a := b) in a task symbol '''
    errors = []
    warnings = []
    expr = ogAST.ExprAssign(
            get_input_string(root), root.getLine(),
            root.getCharPositionInLine())
    expr.kind = 'assign'
    for child in root.getChildren():
        if child.type == lexer.VARIABLE:
            # Left part of the assignation
            prim, err, warn = primary_value(child, context)
            prim.inputString = get_input_string(child)
            prim.line = child.getLine()
            prim.charPositionInLine = child.getCharPositionInLine()
            warnings.extend(warn)
            errors.extend(err)
            expr.left = prim
        else:
            # Right part of the assignation
            expr.right, err, warn = expression(child, context)
            errors.extend(err)
            warnings.extend(warn)
    try:
        fix_expression_types(expr, context)
    except(AttributeError, TypeError) as err:
        errors.append('Types are incompatible in assignment: left (' +
            expr.left.inputString + ', type= ' +
            type_name(expr.left.exprType) + '), right (' +
            expr.right.inputString + ', type= ' +
            type_name(expr.right.exprType) + ') ' + str(err))
    else:
        expr.right.exprType = expr.left.exprType

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
            #context.variables[child.text] = (INT32, 0)
        elif child.type == lexer.VARIABLE:
            list_var, err, warn = primary_value(child, context)
            forloop['list'] = ogAST.PrimVariable(primary=list_var)
            warnings.extend(warn)
            errors.extend(err)
        elif child.type == lexer.RANGE:
            forloop['range'], err, warn = for_range(child, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.TRANSITION:
            # First we need to define the type of the iterator (and check it)
            if forloop['list']:
                if forloop['list'].exprType == UNKNOWN_TYPE:
                    try:
                        forloop['list'].exprType = find_variable\
                                    (forloop['list'].inputString, context)
                    except AttributeError:
                        errors.append('In FOR loop: variable {} is undefined'
                                  .format(forloop['list'].inputString))
                        break
                basic_type = find_basic_type(forloop['list'].exprType)
                if basic_type.kind != 'SequenceOfType':
                    errors.append('Variable {} is not iterable'
                                  .format(forloop['list'].inputString))
                else:
                    forloop['type'] = basic_type.type
                    # Set the type of the iterator
                    context.variables[forloop['var']] = (forloop['type'], 0)
            else:
                # Using a range - set type of iterator to standard integer
                context.variables[forloop['var']] = (INT32, 0)

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
        else:
            warnings.append('Unsupported child type in task body: ' +
                    str(child.type))
    return body, errors, warnings


def task(root, parent=None, context=None):
    ''' Parse a TASK symbol (assignation or informal text) '''
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
        errors = [[e, [pos_x, pos_y]] for e in errors]
        warnings = [[w, [pos_x, pos_y]] for w in warnings]
    if body:
        body.comment = comment
    else:
        warnings.append('TASK missing content')
        body = ogAST.TaskAssign()
    return body, errors, warnings


def label(root, parent, context=None):
    ''' Parse a LABEL symbol '''
    errors = []
    warnings = []
    lab = ogAST.Label()
    coord = False
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            lab.pos_x, lab.pos_y, lab.width, lab.height = cif(child)
            coord = True
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
    if coord:
        errors = [[e, [lab.pos_x, lab.pos_y]] for e in errors]
        warnings = [[w, [lab.pos_x, lab.pos_y]] for w in warnings]
    return lab, errors, warnings


def pr_file(root):
    ''' Complete PR model - can be made up from several files/strings '''
    errors = []
    warnings = []
    ast = ogAST.AST()
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
        LOG.debug('USE clause')
        # USE clauses can contain a CIF comment with the ASN.1 filename
        use_clause_subs = child.getChildren()
        for clause in use_clause_subs:
            if clause.type == lexer.ASN1:
                asn1_filename = clause.getChild(0).text[1:-1]
                ast.asn1_filenames.append(asn1_filename)
            else:
                ast.use_clauses.append(clause.text)
        try:
            global DV
            if not DV:
                # Here XXX call asn1.exe to create DataView.py
                # (Currently done in buildsupport)
                DV = importlib.import_module('DataView')
            else:
                reload(DV)
            ast.dataview = types()
            ast.asn1Modules = DV.asn1Modules
            # Add constants defined in the ASN.1 modules (for visibility)
            for mod in ast.asn1Modules:
                ast.asn1_constants.extend(DV.exportedVariables[mod])
        except (ImportError, NameError):
            LOG.info('USE Clause did not contain ASN.1 filename')
    for child in systems:
        LOG.debug('found SYSTEM')
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
        LOG.debug('found PROCESS')
        process, err, warn = process_definition(child, parent=ast)
        process.dataview = ast.dataview
        process.asn1Modules = ast.asn1Modules
        errors.extend(err)
        warnings.extend(warn)
    LOG.debug('all files: ' + str(ast.pr_files))
    return ast, errors, warnings


def add_to_ast(ast, filename=None, string=None):
    ''' Parse a file or string and add it to an AST '''
    errors, warnings = [], []
    try:
        parser = parser_init(filename=filename, string=string)
    except IOError:
        LOG.error('parser_init failed')
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

    # At the end when common tree is complete, perform the parsing
    og_ast, err, warn = pr_file(common_tree)
    for error in err:
        errors.append([error] if type(error) is not list else error)
    for warning in warn:
        warnings.append([warning] if type(warning) is not list else warning)
    # Post-parsing: additional semantic checks
    # check that all NEXTSTATEs have a correspondingly defined STATE
    # (except the '-' state, which means "stay in the same state')
    for process in og_ast.processes:
        for ns in [t.inputString.lower() for t in process.terminators
                if t.kind == 'next_state']:
            if not ns in [s.lower() for s in
                    process.mapping.viewkeys()] + ['-']:
                errors.append(['State definition missing: ' + ns.upper()])
        # TODO: do the same with JOIN/LABEL
    return og_ast, warnings, errors


def parseSingleElement(elem='', string=''):
    '''
        Parse any symbol and return syntax error and AST entry
        Used for on-the-fly checks when user edits text
        and for copy/cut to create a new object
    '''
    assert(elem in ('input_part', 'output', 'decision', 'alternative_part',
            'terminator_statement', 'label', 'task', 'procedure_call', 'end',
            'text_area', 'state', 'start', 'procedure', 'floating_label',
            'connect_part', 'process_definition'))
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
        # Create a dummy process, needed to place context data
        context = ogAST.Process()
        try:
            t, semantic_errors, warnings = backend_ptr(
                                root=root, parent=None, context=context)
        except AttributeError as err:
            # Syntax checker has no visibility on variables and types
            # so we have to discard exceptions sent by e.g. find_variable
            pass
    return(t, syntax_errors, semantic_errors, warnings,
            context.terminators)


def parser_init(filename=None, string=None):
    ''' Initialize the parser (to be called first) '''
    try:
        char_stream = antlr3.ANTLRFileStream(filename)
    except (IOError, TypeError):
        try:
            char_stream = antlr3.ANTLRStringStream(string)
        except TypeError:
            raise IOError('Could not parse input')
    lex = lexer.sdl92Lexer(char_stream)
    tokens = antlr3.CommonTokenStream(lex)
    parser = sdl92Parser(tokens)
    return parser


if __name__ == '__main__':
    print 'This module is not callable'
