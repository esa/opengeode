#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates Ada code from SDL process models.
    The Ada code is compliant with the TASTE interfaces, and is
    using the ASN.1 "Space-Certified" compiler for data type definition.
    (See TASTE documentation for more information)

    The design is flexible and can be used as basis for other backends.

    Entry point:
    The AST of the model that is parsed is described in ogAST.py

    A Visitor Pattern using Python's "singledispatch" mechanism is used
    to go through the AST and generate code for each SDL construct.

    There is a single function called "generate", decorated with the
    singledispatch mechanism, that needs to be called to generate the code
    of any AST element.

    The generate function returns two values: "code" and "local_decl",
    containing a set of statements and a set of local variables
    (that can be later placed anywhere in the code).

    Expressions (all classes derived from ogAST.Expression) are generated
    using the "expression" visitor (singledispatch set of function).

    Expressions return three values: "code", "ada_string" and "local_decl".
    The "ada_string" value is the usable string that corresponds
    to the result of the expression evaluation.

    For example, take the SDL statement "OUTPUT hello(a+5)"

    This results (in TASTE terminology) in calling the required interface
    called "hello" and passing a parameter of an ASN.1 type (say MyInteger).
    The parameter is always passed by reference.

    It is therefore necessary to build a temporary variable to hold the result
    of the "a+5" expression.

    In this example, the "generate" function will return:
    local_decl = ["tmp01 : MyInteger;"]
    (The template backend can then place it wherever appropriate)

    and code = ["tmp01 := a + 5;", "hello(tmp01);"]
    (The template will then do a '\n'.join(code) - and add indents, etc.)

    To know about "tmp01" and generate the code "hello(tmp01);",
    the function will recursively call "generate" and
    pass a+5 as parameter. The call will return the tuple:

    local_decl = ["tmp01 : MyInteger;"]
    code = ["tmp01 := a + 5;"]
    ada_string = "tmp01"

    This design allows to have any level of complexity in the embedded
    expression in a way that is easy to handle (adding constructs with
    this pattern is straightforward, once the generate function for each AST
    entry is properly implemented).

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from singledispatch import singledispatch

import ogAST
import Helper

LOG = logging.getLogger(__name__)

__all__ = ['generate']

# reference to the ASN.1 Data view and to the visible variables (in scope)
TYPES = None
VARIABLES = {}
LOCAL_VAR = {}
# List of output signals and procedures
OUT_SIGNALS = []
PROCEDURES = []
INNER_PROCEDURES = []


@singledispatch
def generate(ast):
    ''' Generate the code for an item of the AST '''
    _ = ast
    raise TypeError('[AdaGenerator] Unsupported AST construct')
    return [], []

# Processing of the AST

@generate.register(ogAST.Process)
def _process(process):
    ''' Generate the code for a complete process (AST Top level) '''
    process_name = process.processName
    global TYPES
    TYPES = process.dataview
    del OUT_SIGNALS[:]
    del PROCEDURES[:]
    del INNER_PROCEDURES[:]
    OUT_SIGNALS.extend(process.output_signals)
    PROCEDURES.extend(process.procedures)

    LOG.info('Generating Ada code for process ' + str(process_name))

    # In case model has nested states, flatten everything
    Helper.flatten(process, sep='_')

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    VARIABLES.update(process.variables)
    INNER_PROCEDURES.extend(process.content.inner_procedures)

    # Generate the code to declare process-level variables
    process_level_decl = []
    for var_name, (var_type, def_value) in process.variables.viewitems():
        if def_value:
            # Expression must be a ground expression, i.e. must not
            # require temporary variable to store computed result
            dst, dstr, dlocal = expression(def_value)
            assert not dst and not dlocal, 'DCL: Expecting a ground expression'
        process_level_decl.append(
                'l_{n} : aliased asn1Scc{t}{default};'.format(
                        n=var_name,
                        t=var_type.ReferencedTypeName.replace('-', '_'),
                        default=' := ' + dstr if def_value else ''))


    # Add the process states list to the process-level variables
    states_decl = 'type states is ('
    states_decl += ', '.join(name for name in process.mapping.iterkeys()
                             if not name.endswith('START')) + ');'
    process_level_decl.append(states_decl)
    process_level_decl.append('state : states;')

    for name, val in process.mapping.viewitems():
        if name.endswith('START') and name != 'START':
            process_level_decl.append('{name} : constant := {val};'
                                      .format(name=name, val=str(val)))

    # Add function allowing to trace current state as a string
    #process_level_decl.append('function get_state return String;')
    #process_level_decl.append('pragma export(C, get_state, "{}_state");'
    #                                                     .format(process_name))

    # Add the declaration of the runTransition procedure
    process_level_decl.append('procedure runTransition(Id: Integer);')
    process_level_decl.append('procedure state_start;')
    #process_level_decl.append('pragma export(C, start, "{}_start");'
    #                          .format(process_name))

    # Generate the code of the start transition:
    start_transition = ['begin',
                        'runTransition(0);']


    # Generate the TASTE template
    try:
        asn1_modules = '\n'.join(['with {dv};\nuse {dv};'.format(
            dv=dv.replace('-', '_'))
            for dv in process.asn1Modules])
    except TypeError:
        asn1_modules = '--  No ASN.1 data types are used in this model'
    taste_template = ['''\
-- This file was generated automatically: DO NOT MODIFY IT !

with System.IO;
use System.IO;

{dataview}

with adaasn1rtl;
use adaasn1rtl;

with Interfaces;
use Interfaces;

package body {process_name} is'''.format(process_name=process_name,
    dataview=asn1_modules)]

    # Generate the source file (.ads) header
    ads_template = ['''\
-- This file was generated automatically: DO NOT MODIFY IT !

{dataview}

package {process_name} is'''.format(process_name=process_name,
    dataview=asn1_modules)]

    # Generate the the code of the procedures
    inner_procedures_code = []
    for proc in process.content.inner_procedures:
        proc_code, proc_local = generate(proc)
        process_level_decl.extend(proc_local)
        inner_procedures_code.extend(proc_code)

    # Generate the code for the process-level variable declarations
    taste_template.extend(process_level_decl)

    # Generate the code for the start procedure
    taste_template.extend([
        'procedure state_start is',
        'begin',
            'null;',
        'end state_start;', ''])

    # Add the code of the procedures definitions
    taste_template.extend(inner_procedures_code)

    # Generate the code for each input signal (provided interface) and timers
    for signal in process.input_signals + [
                        {'name': timer.lower()} for timer in process.timers]:
        if signal.get('name', 'START') == 'START':
            continue
        pi_header = 'procedure {sig_name}'.format(sig_name=signal['name'])
        param_name = signal.get('param_name') or 'MISSING_PARAM_NAME'
        # Add (optional) PI parameter (only one is possible in TASTE PI)
        if 'type' in signal:
            typename = signal['type'].ReferencedTypeName.replace('-', '_')
            pi_header += '({pName}: access asn1Scc{pType})'.format(
                                           pName=param_name, pType=typename)

        # Add declaration of the provided interface in the .ads file
        ads_template.append('--  Provided interface "' + signal['name'] + '"')
        ads_template.append(pi_header + ';')
        ads_template.append('pragma export(C, {name}, "{proc}_{name}");'
                            .format(name=signal['name'], proc=process_name))

        pi_header += ' is'
        taste_template.append(pi_header)
        taste_template.append('begin')
        taste_template.append('case state is')
        for state in process.mapping.viewkeys():
            if state.endswith('START'):
                continue
            taste_template.append('when {state} =>'.format(state=state))
            input_def = mapping[signal['name']].get(state)
            # Check for nested states to call optional exit procedure
            sep = '_'
            state_tree = state.split(sep)
            context=process
            exitlist = []
            current = ''
            trans = input_def and process.transitions[input_def.transition_id]
            while state_tree:
                current = current + state_tree.pop(0)
                for comp in context.composite_states:
                    if current == comp.statename.lower():
                        if comp.exit_procedure:
                            exitlist.append(current)
                        context = comp
                        current = current + sep
                        break
            for each in reversed(exitlist):
                if trans and all(each.startswith(trans_st)
                                 for trans_st in trans.possible_states):
                    taste_template.append(each + '_' + 'exit;')

            if input_def:
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    taste_template.append('l_{inp} := {tInp}.all;'.format(
                        inp=inp, tInp=param_name))
                # Execute the correponding transition
                if input_def.transition:
                    taste_template.append('runTransition({idx});'.format(
                        idx=input_def.transition_id))
                else:
                    taste_template.append('null;')
            else:
                taste_template.append('null;')
        taste_template.append('when others =>')
        taste_template.append('null;')
        taste_template.append('end case;')
        taste_template.append('end {sig_name};'.format(
                                                      sig_name=signal['name']))
        taste_template.append('\n')

    # for the .ads file, generate the declaration of the required interfaces
    # output signals are the asynchronous RI - only one parameter
    for signal in process.output_signals:
        ri_header = 'procedure {sig_name}'.format(sig_name=signal['name'])
        param_name = signal.get('param_name') or 'MISSING_PARAM_NAME'
        # Add (optional) RI parameter
        if 'type' in signal:
            typename = signal['type'].ReferencedTypeName.replace('-', '_')
            ri_header += '({pName}: access asn1Scc{pType})'.format(
                pName=param_name, pType=typename)
        ads_template.append('--  Required interface "' + signal['name'] + '"')
        ads_template.append(ri_header + ';')
        ads_template.append('pragma import(C, {sig}, "{proc}_RI_{sig}");'
                .format(sig=signal['name'], proc=process_name))

    # for the .ads file, generate the declaration of the external procedures
    for proc in process.procedures:
        ri_header = 'procedure {sig_name}'.format(sig_name=proc.inputString)
        params = []
        for param in proc.fpar:
            typename = param['type'].ReferencedTypeName.replace('-', '_')
            params.append('{par[name]}: access asn1Scc{partype}'.format(
                par=param, partype=typename))
        if params:
            ri_header += '(' + ';'.join(params) + ')'
        ads_template.append('--  Sync required interface "' + proc.inputString)
        ads_template.append(ri_header + ';')
        ads_template.append('pragma import(C, {sig}, "{proc}_RI_{sig}");'
                .format(sig=proc.inputString, proc=process_name))

    # for the .ads file, generate the declaration of timers set/reset functions
    for timer in process.timers:
        ads_template.append(
                '--  Timer {} SET and RESET functions'.format(timer))
        ads_template.append('procedure SET_{}(val: access asn1SccT_UInt32);'
                .format(timer))
        ads_template.append(
                'pragma import(C, SET_{timer}, "{proc}_RI_set_{timer}");'
                .format(timer=timer, proc=process_name))
        ads_template.append('procedure RESET_{};'.format(timer))
        ads_template.append(
                'pragma import(C, RESET_{timer}, "{proc}_RI_reset_{timer}");'
                .format(timer=timer, proc=process_name))

    taste_template.append('procedure runTransition(Id: Integer) is')
    taste_template.append('trId : Integer := Id;')

    # Transform inner labels to floating labels
    Helper.inner_labels_to_floating(process)

    # Generate the code for all transitions
    code_transitions = []
    local_decl_transitions = []
    for proc_tr in process.transitions:
        code_tr, tr_local_decl = generate(proc_tr)
        code_transitions.append(code_tr)
        local_decl_transitions.extend(tr_local_decl)


    # Generate code for the floating labels
    code_labels = []
    for label in process.content.floating_labels:
        code_label, label_decl = generate(label)
        local_decl_transitions.extend(label_decl)
        code_labels.extend(code_label)

    # Declare the local variables needed by the transitions in the template
    decl = ['{line}'.format(line=l)
            for l in local_decl_transitions]
    taste_template.extend(decl)
    taste_template.append('begin')

    # Generate a loop that ends when a next state is reached
    # (there can be chained transition when entering a nested state)
    taste_template.append('while (trId /= -1) loop')

    # Generate the switch-case on the transition id
    taste_template.append('case trId is')

    for idx, val in enumerate(code_transitions):
        taste_template.append('when {idx} =>'.format(idx=idx))
        val = ['{line}'.format(line=l) for l in val]
        if val:
            taste_template.extend(val)
        else:
            taste_template.append('null;')

    taste_template.append('when others =>')
    taste_template.append('null;')

    taste_template.append('end case;')
    if code_labels:
        # Due to nested states (chained transitions) jump over label code
        # (NEXTSTATEs do not return from runTransition)
        taste_template.append('goto next_transition;')

    # Add the code for the floating labels
    taste_template.extend(code_labels)

    #if code_labels:
    taste_template.append('<<next_transition>>')
    taste_template.append('null;')
    taste_template.append('end loop;')
    taste_template.append('end runTransition;')
    taste_template.append('\n')

    # Code of the function allowing to trace current state
    #taste_template.append('function get_state return String is')
    #taste_template.append('begin')
    #taste_template.append("return states'Image(state);")
    #taste_template.append('end get_state;')
    #taste_template.append('\n')


    taste_template.extend(start_transition)
    taste_template.append('end {process_name};'
            .format(process_name=process_name))

    ads_template.append('end {process_name};'
            .format(process_name=process_name))

    with open(process_name + '.adb', 'w') as ada_file:
        ada_file.write('\n'.join(format_ada_code(taste_template)))

    with open(process_name + '.ads', 'w') as ada_file:
        ada_file.write('\n'.join(format_ada_code(ads_template)))


def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    code = []
    string = ''
    local = []
    basic_type = find_basic_type(param.exprType) or {}
    type_kind = basic_type.kind
    if type_kind.endswith('StringType'):
        if isinstance(param, ogAST.PrimStringLiteral):
            # Raw string
            string = '"' + param.value[1:-1].replace('"', "'") + '"'
        else:
            # XXX Cannot print an octet string like that...
            code, string, local = expression(param)
    elif type_kind in ('IntegerType', 'RealType',
                       'BooleanType', 'Integer32Type'):
        code, string, local = expression(param)
        if type_kind == 'IntegerType':
            cast = "Interfaces.Integer_64"
        elif type_kind == 'RealType':
            cast = 'Long_Float'
        elif type_kind == 'BooleanType':
            cast = 'Boolean'
        elif type_kind == 'Integer32Type':
            cast = 'Integer'
        string = "{cast}'Image({s})".format(cast=cast, s=string)
    else:
        error = ('Unsupported parameter in write call ' +
                param.inputString)
        LOG.error(error)
        raise TypeError(error)
    code.append('Put{line}({string});'.format(
        line='_Line' if newline else '',
        string=string))
    return code, string, local


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output):
    ''' Generate the code of a set of output or procedure call statement '''
    code = []
    local_decl = []

    # Add the traceability information
    code.extend(traceability(output))

    for out in output.output:
        signal_name = out['outputName']

        if signal_name.lower() in ('write', 'writeln'):
            # special built-in SDL procedure for printing strings
            # supports printing of native types (int, real, bool)
            # but not yet complex ASN.1 structures (sequence/seqof/choice)
            for param in out['params'][:-1]:
                stmts, _, local = write_statement(param, newline=False)
                code.extend(stmts)
                local_decl.extend(local)
            for param in out['params'][-1:]:
                # Last parameter - add newline if necessary
                stmts, _, local = write_statement(param, newline=True if
                        signal_name.lower() == 'writeln' else False)
                code.extend(stmts)
                local_decl.extend(local)
            continue
        elif signal_name.lower() == 'reset_timer':
            # built-in operator for resetting timers. param = timer name
            param, = out['params']
            p_code, p_id, p_local = expression(param)
            code.extend(p_code)
            local_decl.extend(p_local)
            code.append('RESET_{};'.format(p_id))
            continue
        elif signal_name.lower() == 'set_timer':
            # built-in operator for setting a timer: SET(1000, timer_name)
            timer_value, timer_id = out['params']
            t_code, t_val, t_local = expression(timer_value)
            p_code, p_id, p_local = expression(timer_id)
            code.extend(t_code)
            code.extend(p_code)
            local_decl.extend(t_local)
            local_decl.extend(p_local)
            # Use a temporary variable to store the timer value
            tmp_id = 'tmp' + str(out['tmpVars'][0])
            local_decl.append('{} : aliased asn1SccT_Uint32;'.format(tmp_id))
            code.append('{tmp} := {val};'.format(tmp=tmp_id, val=t_val))
            code.append("SET_{timer}({value}'access);"
                                             .format(timer=p_id, value=tmp_id))
            continue
        proc, out_sig = None, None
        try:
            out_sig, = [sig for sig in OUT_SIGNALS
                        if sig['name'].lower() == signal_name.lower()]
        except ValueError:
            # Not an output, try if it is an external procedure
            try:
                out_sig, = [sig for sig in PROCEDURES
                            if sig.inputString.lower() == signal_name.lower()]
            except ValueError:
                # Not external? Must be an inner procedure then.
                # otherwise the parser would have barked
                proc, = [sig for sig in INNER_PROCEDURES
                     if sig.inputString.lower() == signal_name.lower()]
        if out_sig:
            list_of_params = []
            for idx, param in enumerate(out.get('params') or []):
                param_direction = 'in'
                try:
                    # If it is an output, there is a single parameter
                    param_type = out_sig['type']
                except TypeError:
                    # Else if it is a procedure, get the type
                    param_type = out_sig.fpar[idx]['type']
                    param_direction = out_sig.fpar[idx]['direction']

                typename = param_type.ReferencedTypeName.replace('-', '_')
                p_code, p_id, p_local = expression(param)
                code.extend(p_code)
                local_decl.extend(p_local)
                # Create a temporary variable for input parameters only
                # (If needed, i.e. if argument is not a local variable)
                if param_direction == 'in' \
                and (not (isinstance(param, ogAST.PrimVariable) and
                p_id.startswith('l_')) or isinstance(param, ogAST.PrimFPAR)):
                    tmp_id = out['tmpVars'][idx]
                    local_decl.append('tmp{idx} : aliased asn1Scc{oType};'
                                      .format(idx=tmp_id, oType=typename))
                    code.append('tmp{idx} := {p_id};'
                                .format(idx=tmp_id, p_id=p_id))
                    list_of_params.append("tmp{idx}'access"
                                          .format(idx=out['tmpVars'][idx]))
                else:
                    # Output parameters - no need for a temp variable
                    list_of_params.append("{var}'access".format(var=p_id))
            if list_of_params:
                code.append('{RI}({params});'.format(
                    RI=out['outputName'], params=', '.join(list_of_params)))
            else:
                code.append('{RI};'.format(RI=out['outputName']))
        else:
            # inner procedure call
            list_of_params = []
            for param in out.get('params', []):
                p_code, p_id, p_local = expression(param)
                code.extend(p_code)
                local_decl.extend(p_local)
                # no need to use temporary variables, we are in pure Ada
                list_of_params.append(p_id)
            if list_of_params:
                code.append('{proc}({params});'.format(
                    proc=proc.inputString,
                    params=', '.join(list_of_params)))
            else:
                code.append('{};'.format(proc.inputString))
    return code, local_decl


@generate.register(ogAST.TaskAssign)
def _task_assign(task):
    ''' A list of assignments in a task symbol '''
    code, local_decl = [], []
    ada_string = ''
    if task.comment:
        code.extend(traceability(task.comment))
    for expr in task.elems:
        code.extend(traceability(expr))
        code_assign, ada_string, decl_assign = expression(expr)
        code.extend(code_assign)
        code.append(ada_string[1:-1] + ';')
        local_decl.extend(decl_assign)
    return code, local_decl


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task):
    ''' Generate Ada comments for informal text '''
    code = []
    if task.comment:
        code.extend(traceability(task.comment))
    code.extend(['-- ' + text.replace('\n', '\n-- ') for text in task.elems])
    return code, []


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task):
    '''
        Return the code corresponding to a for loop. Two forms are possible:
        for x in range ([start], stop [, step])
        for x in iterable (a SEQUENCE OF)
    '''
    stmt, local_decl = [], []
    if task.comment:
        stmt.extend(traceability(task.comment))
    stmt.extend(traceability(task))
    for loop in task.elems:
        if loop['range']:
            start_str, stop_str = '0', ''
            if loop['range']['start']:
                start_stmt, start_str, start_local = expression\
                                                       (loop['range']['start'])
                local_decl.extend(start_local)
                stmt.extend(start_stmt)
                # ASN.1 Integers are 64 bits - we need to convert to 32 bits
                if isinstance(loop['range']['start'], ogAST.PrimInteger):
                    start_str = 'Integer({})'.format(start_str)
            if loop['range']['step'] == 1:
                start_str += '..'
            stop_stmt, stop_str, stop_local = expression(loop['range']['stop'])
            local_decl.extend(stop_local)
            stmt.extend(stop_stmt)
            if isinstance(loop['range']['stop'], ogAST.PrimInteger):
                stop_str = 'Integer({})'.format(stop_str)
            if loop['range']['step'] == 1:
                stmt.append(
                       'for {it} in {start}{stop} loop'
                       .format(it=loop['var'], start=start_str, stop=stop_str))
            else:
                # Step is not directly supported in Ada, we need to use 'while'
                stmt.extend(['declare',
                             '{it} : Integer := {start};'
                             .format(it=loop['var'],
                             start=start_str),
                             '',
                             'begin',
                             'while {it} < {stop} loop'.format(it=loop['var'],
                                                               stop=stop_str)])
        else:
            # case of form: FOR x in SEQUENCE OF
            elem_type = loop['type'].ReferencedTypeName.replace('-', '_')
            list_stmt, list_str, list_local = expression(loop['list'])
            basic_type = find_basic_type(loop['list'].exprType)
            range_cond = "{}.Data'Range".format(list_str)\
                    if basic_type.Min == basic_type.Max\
                    else "1..{}.Length".format(list_str)
            stmt.extend(list_stmt)
            local_decl.extend(list_local)
            stmt.extend(['declare',
                         '{it} : asn1Scc{it_ty};'.format(it=loop['var'],
                                                         it_ty=elem_type),
                         '',
                         'begin',
                         'for {it}_idx in {rc} loop'.format(it=loop['var'],
                                                            rc=range_cond),
                         '{it} := {var}.Data({it}_idx);'.format(it=loop['var'],
                                                                var=list_str)])
        try:
            code_trans, local_trans = generate(loop['transition'])
            if local_trans:
                stmt.append('declare')
                stmt.extend(local_trans)
                stmt.append('')
                stmt.append('begin')
            stmt.extend(code_trans)
            if local_trans:
                stmt.append('end;')
        except AttributeError:
            stmt.append('null;')
        if loop['range'] and loop['range']['step'] != 1:
            stmt.append('{it} := {it} + {step};'.format(it=loop['var'],
                                                   step=loop['range']['step']))
        stmt.append('end loop;')
        if (loop['range'] and loop['range']['step'] != 1) or loop['list']:
            stmt.append('end;')
    return stmt, local_decl


@singledispatch
def expression(expr):
    ''' Generate the code for Expression-classes, returning 3 things:
        - list of statements
        - useable string corresponding to the evaluation of the expression,
        - list of local declarations
    '''
    _ = expr
    raise TypeError('Unsupported expression: ' + str(expr))
    return [], '', []

@expression.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Single variable reference '''
    sep = 'l_' if find_var(prim.value[0]) else ''
    return [], '{sep}{name}'.format(sep=sep, name=prim.value[0]), []


@expression.register(ogAST.PrimPath)
def _prim_path(primary_id):
    '''
        Return the Ada string of an element list (path)
        cases: a => 'l_a' (reference to a variable)
        a_timer => 'a_timer'  (reference to a timer)
        a!b => a.b (field of a structure)
        a!b if a is a CHOICE => TypeOfa_b_get(a)
        a(Expression) => a(ExpressionSolver) (array index)
        Expression can be complex (if-then-else-fi..)
    '''
    ada_string = ''
    stmts, local_decl = [], []

    # If first element is not a variable (can be a timer) do not add prefix
    sep = 'l_' if find_var(primary_id.value[0]) else ''

    sub_id = []
    for pr_id in primary_id.value:
        if type(pr_id) is not dict:
            if pr_id.lower() == 'length':
                special_op = 'Length'
                continue
            elif pr_id.lower() == 'present':
                special_op = 'ChoiceKind'
                continue
            elif pr_id.lower() == 'abs':
                special_op = 'Abs'
                continue
            special_op = ''
            parent_kind, parent_typename = path_type(sub_id)
            sub_id.append(pr_id)
            if parent_kind == 'ChoiceType':
                ada_string = ('asn1Scc{typename}_{p_id}_get({ada_string})'
                        .format(typename=parent_typename,
                                p_id=pr_id, ada_string=ada_string))
            else:
                ada_string += sep + pr_id
        else:
            if 'substring' in pr_id:
                # substring: two parameters (range)
                r1_stmts, r1_string, r1_local = \
                        expression(pr_id['substring'][0])
                r2_stmts, r2_string, r2_local = \
                        expression(pr_id['substring'][1])
                # should we add 1 in case of numerical values? (see index)
                ada_string += '.Data({r1}..{r2})'.format(
                                                r1=r1_string, r2=r2_string)
                stmts.extend(r1_stmts)
                stmts.extend(r2_stmts)
                local_decl.extend(r1_local)
                local_decl.extend(r2_local)
                _, parent_typename = path_type(sub_id)
                local_decl.append('tmp{idx} : aliased asn1Scc{parent_type};'
                          .format(idx=pr_id['tmpVar'],
                              parent_type=parent_typename))
                # XXX types with fixed length: substrings will not work
                if unicode.isnumeric(r1_string) and unicode.isnumeric(
                                                                r2_string):
                    length = int(r2_string) - int(r1_string) + 1
                else:
                    length = ('{r2} - {r1} + 1'
                        .format(r2=r2_string, r1=r1_string))
                stmts.append('tmp{idx}.Length := {length};'
                        .format(idx=pr_id['tmpVar'], length=length))

                stmts.append('tmp{idx}.Data(1..{length}) := {data};'
                        .format(idx=pr_id['tmpVar'],
                            length=length, data=ada_string))
                ada_string = 'tmp{idx}'.format(idx=pr_id['tmpVar'])
            elif 'index' in pr_id:
                # index is a list but it can have only one element
                idx_stmts, idx_string, local_var = expression(
                        pr_id['index'][0])
                if unicode.isnumeric(idx_string):
                    idx_string = int(idx_string) + 1
                else:
                    idx_string = '1+Integer({idx})'.format(idx=idx_string)
                ada_string += '.Data({idx})'.format(idx=idx_string)
                stmts.extend(idx_stmts)
                local_decl.extend(local_var)
            elif 'procParams' in pr_id:
                if special_op == 'Abs':
                    # Return absolute value of a number
                    exp, = pr_id['procParams']
                    exp_type = find_basic_type(exp.exprType)
                    if exp_type.kind not in ('IntegerType', 'RealType'):
                        error = ('{} must be a number to return absolute value'
                                .format(exp.inputString))
                        LOG.error(error)
                        raise TypeError(error)
                    param_stmts, param_str, local_var = expression(exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    ada_string += 'abs(' + param_str + ')'

                elif special_op == 'Length':
                    # Length of sequence of: take only the first parameter
                    exp, = pr_id['procParams']
                    exp_type = find_basic_type(exp.exprType)
                    min_length = getattr(exp_type, 'Min', None)
                    max_length = getattr(exp_type, 'Max', None)
                    if min_length is None or max_length is None:
                        error = '{} is not a SEQUENCE OF'.format(
                                exp.inputString)
                        LOG.error(error)
                        raise TypeError(error)
                    param_stmts, param_str, local_var = expression(
                            exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    if min_length == max_length:
                        ada_string += min_length
                    else:
                        ada_string += ('Interfaces.Integer_64({e}.Length)'
                                .format(e=param_str))
                elif special_op == 'ChoiceKind':
                    # User wants to know what CHOICE element is present
                    exp, = pr_id['procParams']
                    # Get the basic type to make sure it is a choice
                    exp_type = find_basic_type(exp.exprType)
                    # Also get the ASN.1 type name as it is
                    # needed to build the Ada expression
                    exp_typename = \
                            (getattr(exp.exprType, 'ReferencedTypeName',
                                 None) or exp.exprType.kind).replace('-', '_')
                    if exp_type.kind != 'ChoiceType':
                        error = '{} is not a CHOICE'.format(exp.inputString)
                        LOG.error(error)
                        raise TypeError(error)
                    param_stmts, param_str, local_var = expression(
                            exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    ada_string += ('asn1Scc{t}_Kind({e})'.format(
                        t=exp_typename, e=param_str))
                else:
                    ada_string += '('
                    # Take all params and join them with commas
                    list_of_params = []
                    for param in pr_id['procParams']:
                        param_stmt, param_str, local_var = (
                                expression(param))
                        list_of_params.append(param_str)
                        stmts.extend(param_stmt)
                        local_decl.extend(local_var)
                    ada_string += ', '.join(list_of_params)
                    ada_string += ')'
        sep = '.'
    return stmts, ada_string, local_decl


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
@expression.register(ogAST.ExprAssign)
def _basic_operators(expr):
    ''' Expressions with two sides '''
    code, local_decl = [], []
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    ada_string = '({left} {op} {right})'.format(
            left=left_str, op=expr.operand, right=right_str)
    code.extend(left_stmts)
    code.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, ada_string, local_decl

@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
def _bitwise_operators(expr):
    ''' Logical operators '''
    code, local_decl = [], []
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    basic_type = find_basic_type(expr.exprType)
    if basic_type.kind != 'BooleanType':
        # Sequence of boolean or bit string
        if expr.right.is_raw:
            # Declare a temporary variable to store the raw value
            tmp_string = 'tmp{}'.format(expr.right.tmpVar)
            local_decl.append('{tmp} : aliased asn1Scc{eType};'.format(
                        tmp=tmp_string,
                        eType=expr.right.exprType.ReferencedTypeName
                        .replace('-', '_')))
            code.append('{tmp} := {right};'.format(tmp=tmp_string,
                                                  right=right_str))
            right_str = tmp_string
        ada_string = '(Data => ({left}.Data {op} {right}.Data)'.format(
                left=left_str, op=expr.operand, right=right_str)
        if basic_type.Min != basic_type.Max:
            ada_string += ", Length => {left}.Length".format(left=left_str)
        ada_string += ')'
    else:
        ada_string = '({left} {op} {right})'.format(
                               left=left_str, op=expr.operand, right=right_str)
    code.extend(left_stmts)
    code.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, ada_string, local_decl


@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    stmts, ada_string, local_decl = [], '', []
#    basic_type_expr = find_basic_type(expr.exprType)
    # We can do a length check if both strings are literals
    # XXX should be already done by the parser
#   if(expr.right.kind == 'primary'
#      and expr.right.var.kind == 'stringLiteral'
#      and expr.left.kind == 'primary'
#      and expr.left.var.kind == 'stringLiteral'
#      and len(expr.right.var.stringLiteral[1:-1]) +
#      len(expr.left.var.stringLiteral[1:-1]) > basic_type_expr.Max):
#       raise ValueError('String concatenation exceeds container length: '
#               'length(' + expr.left.var.stringLiteral[1:-1] +
#               expr.right.var.stringLiteral[1:-1] + ') > ' +
#               str(basic_type_expr.Max))

    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    # Declare a temporary variable to hold the result of the append
    ada_string = 'tmp{}'.format(expr.tmpVar)
    local_decl.append('{tmp} : aliased asn1Scc{eType};'.format(
                    tmp=ada_string,
                    eType=expr.exprType.ReferencedTypeName
                    .replace('-', '_')))

    # If right or left is raw, declare a temporary variable for it, too
    for sexp, sid in zip((expr.right, expr.left), (right_str, left_str)):
        if sexp.is_raw:
            local_decl.append('tmp{idx} : aliased asn1Scc{eType};'.format(
                    idx=sexp.tmpVar,
                    eType=sexp.exprType.ReferencedTypeName
                    .replace('-', '_')))
            stmts.append('tmp{idx} := {s_id};'.format(
                idx=sexp.tmpVar, s_id=sid))
            sexp.sid = 'tmp' + str(sexp.tmpVar)
            # Length of raw string - update for sequence of
            if isinstance(sexp, ogAST.PrimStringLiteral):
                sexp.slen = len(sexp.value[1:-1])
            elif isinstance(sexp, ogAST.PrimEmptyString):
                sexp.slen = 0
            elif isinstance(sexp, ogAST.PrimSequenceOf):
                sexp.slen = len(sexp.value)
            else:
                raise TypeError('Not a string/Sequence in APPEND')
        else:
            sexp.sid = sid
            basic = find_basic_type(sexp.exprType)
            if basic.Min == basic.Max:
                # Fixed-size string
                sexp.slen = basic.Max
            else:
                # Variable-size types have a Length field
                sexp.slen = '{}.Length'.format(sexp.sid)
    stmts.append('{res}.Data(1..{l1}) := {lid}.Data(1..{l1});'.format(
                res=ada_string, l1=expr.left.slen, lid=expr.left.sid))
    stmts.append('{res}.Data({l1}+1..{l1}+{l2}) := {rid}.Data(1..{l2});'
                .format(res=ada_string, l1=expr.left.slen,
                rid=expr.right.sid, l2=expr.right.slen))
    stmts.append('{res}.Length := {l1} + {l2};'.format(
                res=ada_string, l1=expr.left.slen, l2=expr.right.slen))
    return stmts, ada_string, local_decl


@expression.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' IN expressions: check if item is in a SEQUENCE OF '''
    # Check if item is in a SEQUENCE OF
    # Temporary variable needed to hold the test result
    ada_string = 'tmp{}'.format(expr.tmpVar)
    stmts = []
    local_decl = ['{} : BOOLEAN := False;'.format(ada_string)]
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    stmts.append("in_loop_{}:".format(ada_string))
    left_type = find_basic_type(expr.left.exprType)
    if left_type.Min != left_type.Max:
        stmts.append("for elem in 1..Integer({}.Length) loop"
                     .format(left_str))
    else:
        stmts.append("for elem in {}.Data'Range loop".format(left_str))
    stmts.append("if {container}.Data(elem) = {pattern} then".format
            (container=left_str, pattern=right_str))
    stmts.append("{} := True;".format(ada_string))
    stmts.append("end if;")
    stmts.append("exit in_loop_{tmp} when {tmp} = True;"
                  .format(tmp=ada_string))
    stmts.append("end loop in_loop_{};".format(ada_string))
    return stmts, ada_string, local_decl


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    enumerant = primary.value[0].replace('_', '-')
    basic = find_basic_type(primary.exprType)
    ada_string = ('asn1Scc' + basic.EnumValues[enumerant].EnumID)
    return [], ada_string, []


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    enumerant = primary.value[0].replace('_', '-')
    ada_string = primary.exprType.EnumValues[enumerant].EnumID
    return [], ada_string, []


@expression.register(ogAST.PrimInteger)
@expression.register(ogAST.PrimReal)
@expression.register(ogAST.PrimBoolean)
def _integer(primary):
    ''' Generate code for a raw integer/real/boolean value  '''
    return [], primary.value[0], []


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    ada_string = 'asn1Scc{typeRef}_Init'.format(
             typeRef=primary.exprType.ReferencedTypeName.replace('-', '_'))
    return [], ada_string, []


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    basic_type = find_basic_type(primary.exprType)
    # If user put a literal string to fill an Octet string,
    # then convert the string to an array of unsigned_8 integers
    # as expected by the Ada type corresponding to Octet String
    unsigned_8 = [str(ord(val)) for val in primary.value[1:-1]]
    ada_string = '(Data => (' + ', '.join(
                                         unsigned_8) + ', others => 0)'
    if basic_type.Min != basic_type.Max:
        # Non-fixed string size -> add Length field
        ada_string += ', Length => {}'.format(
                                str(len(primary.value[1:-1])))
    ada_string += ')'
    return [], ada_string, []


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    return [], primary.value[0], []


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    # TODO
    _ = primary
    return [], '', []

@expression.register(ogAST.PrimIfThenElse)
def _if_then_else(ifThenElse):
    ''' Return string and statements for ternary operator '''
    resType = ifThenElse.exprType
    stmts = []
    local_decl = ['tmp{idx} : asn1Scc{resType};'.format(
        idx=ifThenElse.value['tmpVar'],
        resType=resType.ReferencedTypeName.replace('-', '_'))]
    if_stmts, if_str, if_local = expression(ifThenElse.value['if'])
    then_stmts, then_str, then_local = expression(ifThenElse.value['then'])
    else_stmts, else_str, else_local = expression(ifThenElse.value['else'])
    stmts.extend(if_stmts)
    stmts.extend(then_stmts)
    stmts.extend(else_stmts)
    local_decl.extend(if_local)
    local_decl.extend(then_local)
    local_decl.extend(else_local)
    stmts.append('if {if_str} then'.format(
        if_str=if_str))
    stmts.append('tmp{idx} := {then_str};'.format(
        idx=ifThenElse.value['tmpVar'], then_str=then_str))
    stmts.append('else')
    stmts.append('tmp{idx} := {else_str};'.format(
        idx=ifThenElse.value['tmpVar'], else_str=else_str))
    stmts.append('end if;')
    ada_string = 'tmp{idx}'.format(idx=ifThenElse.value['tmpVar'])
    return stmts, ada_string, local_decl


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    stmts, local_decl = [], []
    seqType = seq.exprType
    LOG.debug('PrimSequence: ' + str(seq) + str(seqType))

    ada_string = "asn1Scc{seqType}'(".format(
            seqType=seqType.ReferencedTypeName.replace('-', '_'))
    sep = ''
    for elem, value in seq.value.viewitems():
        # Set the type of the field - easy thanks to ASN.1 flattened AST
        delem = elem.replace('_', '-')
        value.exprType = (TYPES
                    [seqType.ReferencedTypeName].type.Children[delem].type)
        value_stmts, value_str, local_var = expression(value)
        ada_string += sep + elem + ' => ' + value_str
        sep = ', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    ada_string += ')'
    return stmts, ada_string, local_decl


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    stmts, local_decl = [], []
    seqofType = seqof.exprType
    typename = seqofType.ReferencedTypeName
    LOG.debug('SequenceOf Typename:' + str(typename))
    asn_type = TYPES[typename].type
    min_size = asn_type.Min
    max_size = asn_type.Max
    ada_string = 'asn1Scc{seqofType}\'('.format(
                                seqofType=typename.replace('-', '_'))
    if min_size == max_size:
        # Fixed-length array - no need to set the Length field
        ada_string += 'Data => asn1Scc{seqofType}_array\'('.format(
                seqofType=typename.replace('-', '_'))
    else:
        # Variable-length array
        ada_string += (
                'Length => {length}, Data => asn1Scc{seqofType}_array\'('
                .format(seqofType=typename.replace('-', '_'),
                        length=len(seqof.value)))
    for i in xrange(len(seqof.value)):
        # Set the type of the element (should not be useful anymore)
        #seqof.value[i].exprType = TYPES[typename].type.type
        item_stmts, item_str, local_var = expression(seqof.value[i])
        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        ada_string += '{i} => {value}, '.format(i=i + 1, value=item_str)
    ada_string += 'others => {anyVal}))'.format(anyVal=item_str)
    return stmts, ada_string, local_decl


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Return the Ada code for a CHOICE expression '''
    stmts, choice_str, local_decl = expression(choice.value['value'])
    choiceType = choice.exprType
    actual_type = getattr(
                     choiceType, 'ReferencedTypeName', None) or choiceType.kind
    actual_type = actual_type.replace('-', '_')
    ada_string = 'asn1Scc{cType}_{opt}_set({expr})'.format(
            cType=actual_type,
            opt=choice.value['choice'],
            expr=choice_str)
    return stmts, ada_string, local_decl


@generate.register(ogAST.Decision)
def _decision(dec):
    ''' generate the code for a decision '''
    code, local_decl = [], []
    question_type = dec.question.exprType
    # XXX check if we should get the type like this
    actual_type = getattr(
            question_type, 'ReferencedTypeName', None) or question_type.kind
    actual_type = actual_type.replace('-', '_')
    basic = find_basic_type(question_type).kind in ('IntegerType',
                          'Integer32Type', 'BooleanType',
                          'RealType', 'EnumeratedType', 'ChoiceEnumeratedType')
    # for ASN.1 types, declare a local variable
    # to hold the evaluation of the question
    if not basic:
        local_decl.append('tmp{idx} : aliased asn1Scc{actType};'.format(
                          idx=dec.tmpVar, actType=actual_type))
    q_stmts, q_str, q_decl = expression(dec.question)
    # Add code-to-model traceability
    code.extend(traceability(dec))
    local_decl.extend(q_decl)
    code.extend(q_stmts)
    if not basic:
        code.append('tmp{idx} := {q};'.format(idx=dec.tmpVar, q=q_str))
    sep = 'if '
    for a in dec.answers:
        code.extend(traceability(a))
        if a.kind in ('open_range', 'constant'):
            # Note: removed and a.transition here because empty transitions
            # have a different meaning, and a "null;" statement has to be
            # generated, to go into the branch
            ans_stmts, ans_str, ans_decl = expression(a.constant)
            code.extend(ans_stmts)
            local_decl.extend(ans_decl)
            if not basic:
                if a.openRangeOp in (ogAST.ExprEq, ogAST.ExprNeq):
                    exp = 'asn1Scc{actType}_Equal(tmp{idx}, {ans})'.format(
                            actType=actual_type, idx=dec.tmpVar, ans=ans_str)
                    if a.openRangeOp == ogAST.ExprNeq:
                        exp = 'not ' + exp
                else:
                    exp = 'tmp{idx} {op} {ans}'.format(idx=dec.tmpVar,
                            op=a.openRangeOp.operand, ans=ans_str)
            else:
                exp = '{q} {op} {ans}'.format(q=q_str,
                                              op=a.openRangeOp.operand,
                                              ans=ans_str)
            code.append(sep + exp + ' then')
            if a.transition:
                stmt, tr_decl = generate(a.transition)
            else:
                stmt, tr_decl = ['null;'], []
            code.extend(stmt)
            local_decl.extend(tr_decl)
            sep = 'elsif '
        elif a.kind == 'close_range':
            sep = 'elsif '
            # TODO support close_range
        elif a.kind == 'informal_text':
            continue
        elif a.kind == 'else':
            # Keep the ELSE statement for the end
            if a.transition:
                else_code, else_decl = generate(a.transition)
            else:
                else_code, else_decl = ['null;'], []
            local_decl.extend(else_decl)
    try:
        if sep != 'if ':
            # If there is at least one 'if' branch
            else_code.insert(0, 'else')
            code.extend(else_code)
        else:
            code.extend(else_code)
    except:
        pass
    if sep != 'if ':
        # If there is at least one 'if' branch
        code.append('end if;')
    return code, local_decl

@generate.register(ogAST.Label)
def _label(lab):
    ''' Transition following labels are generated in a separate section
        for visibility reasons (see Ada scope)
    '''
    return ['goto {label};'.format(label=lab.inputString)], []


@generate.register(ogAST.Transition)
def _transition(tr):
    ''' generate the code for a transition '''
    code, local_decl = [], []
    empty_transition = all(isinstance(act, ogAST.TaskInformalText)
                           for act in tr.actions)
    for action in tr.actions:
        stmt, local_var = generate(action)
        code.extend(stmt)
        local_decl.extend(local_var)
        if isinstance(action, ogAST.Label):
            break
    else:
        if tr.terminator:
            empty_transition = False
            code.extend(traceability(tr.terminator))
            if tr.terminator.label:
                code.append('<<{label}>>'.format(
                    label=tr.terminator.label.inputString))
            if tr.terminator.kind == 'next_state':
                if tr.terminator.inputString.strip() != '-':
                    code.append('trId := ' + str(tr.terminator.next_id) + ';')
                    if tr.terminator.next_id == -1:
                        code.append('state := {nextState};'.format(
                                 nextState=tr.terminator.inputString))
                else:
                    if any(next_id
                           for next_id in tr.terminator.candidate_id.viewkeys()
                           if next_id != -1):
                        code.append('case state is')
                        for nid, sta in tr.terminator.candidate_id.viewitems():
                            if nid != -1:
                                for each in sta:
                                    code.extend(['when {} =>'.format(each),
                                                 'trId := {};'.format(nid)])

                        code.extend(['when others =>',
                                        'trId := -1;',
                                     'end case;'])
                    else:
                        code.append('trId := -1;')
                code.append('goto next_transition;')
            elif tr.terminator.kind == 'join':
                code.append('goto {label};'.format(
                    label=tr.terminator.inputString))
            elif tr.terminator.kind == 'stop':
                pass
                # TODO
            elif tr.terminator.kind == 'return':
                string = ''
                if tr.terminator.next_id == -1:
                    if tr.terminator.return_expr:
                        stmts, string, local = expression\
                                                    (tr.terminator.return_expr)
                        code.extend(stmts)
                        local_decl.extend(local)
                    code.append('return{};'
                                .format(' ' + string if string else ''))
                else:
                    code.append('trId := ' + str(tr.terminator.next_id) + ';')
                    code.append('goto next_transition;')
    if empty_transition:
        # If transition does not have any statement, generate an Ada 'null;'
        code.append('null;')
    return code, local_decl


@generate.register(ogAST.Floating_label)
def _floating_label(label):
    ''' Generate the code for a floating label (Ada label + transition) '''
    code = []
    local_decl = []
    # Add the traceability information
    code.extend(traceability(label))
    code.append('<<{label}>>'.format(label=label.inputString))
    if label.transition:
        code_trans, local_trans = generate(label.transition)
        code.extend(code_trans)
        local_decl.extend(local_trans)
    else:
        code.append('return;')
    return code, local_decl


@generate.register(ogAST.Procedure)
def _inner_procedure(proc):
    ''' Generate the code for a procedure - does not support states '''
    code = []
    local_decl = []
    # TODO: Update the global list of procedures
    # with procedure defined inside the current procedure
    # Not critical: the editor forbids procedures inside procedures

    # Save variable scope (as local variables may shadow process variables)
    outer_scope = dict(VARIABLES)
    VARIABLES.update(proc.variables)
    # Also add procedure parameters in scope
    for var in proc.fpar:
        VARIABLES.update({var['name']: (var['type'], None)})

    # Build the procedure signature
    pi_header = 'procedure {proc_name}'.format(proc_name=proc.inputString)
    if proc.fpar:
        pi_header += '('
        params = []
        for fpar in proc.fpar:
            typename = fpar['type'].ReferencedTypeName.replace('-', '_')
            params.append('l_{name}: in{out} asn1Scc{ptype}'.format(
                    name=fpar.get('name'),
                    out=' out' if fpar.get('direction') == 'out' else '',
                    ptype=typename))
        pi_header += ';'.join(params)
        pi_header += ')'

    local_decl.append(pi_header + ';')

    if proc.external:
        local_decl.append('pragma import(C, {});'.format(proc.inputString))
    else:
        # Generate the code for the procedure itself
        # local variables and code of the START transition
        # Recursively generate the code for inner-defined procedures
        for inner_proc in proc.content.inner_procedures:
            inner_code, inner_local = generate(inner_proc)
            local_decl.extend(inner_local)
            code.extend(inner_code)
        code.append(pi_header + ' is')
        for var_name, (var_type, def_value) in proc.variables.viewitems():
            typename = var_type.ReferencedTypeName.replace('-', '_')
            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result
                dst, dstr, dlocal = expression(def_value)
                assert not dst and not dlocal, 'Ground expression error'
            code.append('l_{name} : asn1Scc{sort}{default};'.format(
                name=var_name,
                sort=typename,
                default=' := ' + dstr if def_value else ''))

        # Look for labels in the diagram and transform them in floating labels
        Helper.inner_labels_to_floating(proc)

        tr_code, tr_decl = generate(proc.content.start.transition)
        # Generate code for the floating labels
        code_labels = []
        for label in proc.content.floating_labels:
            code_label, label_decl = generate(label)
            code_labels.extend(code_label)
            tr_decl.extend(label_decl)
        code.extend(tr_decl)
        code.append('begin')
        code.extend(tr_code)
        code.extend(code_labels)
        code.append('end {procName};'.format(procName=proc.inputString))
    code.append('\n')

    # Reset the scope to how it was prior to the procedure definition
    VARIABLES.clear()
    VARIABLES.update(outer_scope)

    return code, local_decl


# A few helper functions needed by the Ada backend

def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in TYPES.viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = TYPES[typename].type
                break
    return basic_type


def find_var(var):
    ''' Return a variable from the scope, with proper case '''
    for visible_var in VARIABLES.viewkeys():
        if var.lower() == visible_var.lower():
            return visible_var
    return None


def path_type(path):
    '''
        Return the type of a path construct
        Input: path a!b!c in the form [a, b, c]
        Output: parent_kind, parent_typename (strings)
        Used for Ada to know about CHOICE types
    '''
    # NOTE: all this code is duplicated from the find_type function
    # in ogParser - XXX Refactoring to be done
    if not path or not find_var(path[0]):
        return None, None
    kind = ''
    vartype, _ = VARIABLES[find_var(path[0])]
    asn1_name = vartype.ReferencedTypeName
    # Get ASN.1 type of the first element
    current = TYPES[asn1_name].type
    if len(path) > 1:
        for elem in path[1:]:
            current = find_basic_type(current)
            if 'procParams' in elem:
                # Discard operator parameters: they do not change the type
                continue
            # Sequence, Choice (case insensitive)
            if current.kind in ('SequenceType', 'ChoiceType'):
                elem_asn1 = elem.replace('_', '-').lower()
                type_idx, = (c for c in current.Children
                                    if c.lower() == elem_asn1)
                current = current.Children[type_idx].type
            # Sequence of
            elif current.kind == 'SequenceOfType':
                current = current['type']
            elif current.kind.endswith('EnumeratedType'):
                pass
            else:
                raise TypeError('Expression ' + '.'.join(path) +
                                ' does not resolve')
        asn1_name = current.ReferencedTypeName
    kind = find_basic_type(current).kind.replace('-', '_')
    LOG.debug('[Ada Generator] Type of path ' + '!'.join(path) +
             ' is ' + asn1_name + ' (' + kind + ')')
    return kind, asn1_name.replace('-', '_')


def traceability(symbol):
    ''' Return a string with code-to-model traceability '''
    trace = ['-- {line}'.format(line=l) for l in
        repr(symbol).split('\n')]
    if hasattr(symbol, 'comment') and symbol.comment:
        trace.extend(traceability(symbol.comment))
    return trace

def format_ada_code(stmts):
    ''' Indent properly the Ada code '''
    indent = 0
    indent_pattern = '    '
    for line in stmts[:-1]:
        elems = line.strip().split()
        if elems and elems[0].startswith(('when', 'end', 'elsif', 'else')):
            indent = max(indent - 1, 0)
        if elems and elems[-1] == 'case;': # Corresponds to end case;
            indent = max(indent - 1, 0)
        if line:
            yield indent_pattern * indent + line
        if elems and elems[-1] in ('is', 'then', 'loop', 'declare'):
            indent += 1
        if elems and elems[0] in ('begin', 'case', 'else', 'when'):
            indent += 1
        if not elems:  # newline -> decrease indent
            indent -= 1
    yield stmts[-1]
