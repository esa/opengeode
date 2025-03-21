#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates C code from SDL process models.

    Copyright (c) 2015-2020 Politecnico di Milano & ESA
    Copyright (c) 2020-2023 N7Space & ESA
    Copyright (c) 2024 ESA

    Original design by Marco Lattuada
    Now maintained by ESA
"""

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Imports
import logging
import os
from functools import singledispatch
from itertools import chain, product

from . import Helper, ogAST
from .ogASTDumper import dump

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Global Variables
__all__ = ['generate']

LOG = logging.getLogger(__name__)

PROCESS_NAME = ''
VARIABLES = {}
ALIASES = {}
MONITORS = {}
LOCAL_OUT_VARIABLES = {}
TIMER_VARIABLES = []
LOCAL_VARIABLES = {}
LOCAL_VARIABLE_TYPES = {}
OUT_SIGNALS = []
PROCEDURES = []
STATES = []

SEPARATOR = '_0_'
LPREFIX = 'ctxt'

LEFT_TYPE = ''
VAR_COUNTER = 0
ASN1SCC = 'asn1Scc'

# True if stdio.h has to be included
STDIO_INCLUDE = False

# True if math.h has to be included
MATH_INCLUDE = False

# True if string.h has to be included
STRING_INCLUDE = False

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Functions
@singledispatch
def generate(*args, **kwargs):
    ''' Generate the code for an item of the AST '''
    for arg in args:
        LOG.info(arg)
    raise TypeError('[CGenerator] Unsupported AST construct')
    return [], []


@generate.register(ogAST.Process)
def _process(process, **kwargs):
    ''' Generate the code for a complete process (AST Top level) '''

    app_parameters = kwargs["options"]
    process_name = process.processName

    LOG.info(f'Generating C code for process {process_name}')

    global TYPES
    global STDIO_INCLUDE
    global MATH_INCLUDE
    global STRING_INCLUDE
    global LPREFIX
    global TIMER_VARIABLES
    global PROCESS_NAME

    PROCESS_NAME = process_name

    TYPES = process.dataview

    del OUT_SIGNALS[:]
    OUT_SIGNALS.extend(process.output_signals)

    del PROCEDURES[:]
    PROCEDURES.extend(process.procedures)

    del TIMER_VARIABLES[:]
    TIMER_VARIABLES.extend(process.timers)

    STDIO_INCLUDE = False
    MATH_INCLUDE = False
    STRING_INCLUDE = False

    # Prepare the AST for code generation (flatten states, etc.)
    no_renames = Helper.code_generation_preprocessing(process)

    # Make the aliases visible
    ALIASES.update(process.aliases)

    if app_parameters.dumpAST:
        dump('preprocessed_ast.dump', process.parent.parent.ast)

    Helper.generate_asn1_datamodel(process)
    
    VARIABLES.update(process.variables)
    MONITORS.update(process.monitors)

    del STATES[:]
    STATES.extend(process.mapping.keys())

    beginning_of_include_guard_header_file_code, ending_of_include_guard_header_file_code = generate_header_file_include_guard(process)
    sdl_constants_code = generate_sdl_constants(process)
    aliases_code = processing_process_aliases(process, no_renames)
    context_code = generating_context(process)
    startup_header_file_code, startup_function_code = generating_startup_function(process, no_renames)
    aggreg_start_proc_code = generating_aggregate_start_funtions(process)
    run_transition_declaration_code = generating_run_transition_declaration(process)
    nested_states_code = generating_nested_states(process)
    inner_procedures_header_file_code, inner_procedures_declarations_code, inner_procedures_code = processing_inner_procedures(process)
    input_signals_header_file_code, input_signals_code = processing_input_signals(process)
    output_signals_header_file_code, output_signals_code = processing_output_signals(process)
    external_procedures_header_file_code = processing_external_procedures(process, output_signals_code)
    timers_header_file_code = processing_timers(process, output_signals_code)

    Helper.inner_labels_to_floating(process)

    continuous_signals_header_file_code, transition_code = processing_transitions_and_floating_labels(process)
    includes_code = generating_includes(process)
    generate_current_state_to_str_code = generating_current_state_to_str(process)

    generated_c_source_code = []
    generated_c_source_code.extend(includes_code)
    generated_c_source_code.extend(nested_states_code)
    generated_c_source_code.extend(sdl_constants_code)
    generated_c_source_code.extend(aliases_code)
    generated_c_source_code.extend(context_code)
    generated_c_source_code.extend(run_transition_declaration_code)
    generated_c_source_code.extend(aggreg_start_proc_code)
    generated_c_source_code.extend(inner_procedures_declarations_code)
    generated_c_source_code.extend(startup_function_code)
    generated_c_source_code.extend(input_signals_code)
    generated_c_source_code.extend(output_signals_code)
    generated_c_source_code.extend(inner_procedures_code)
    generated_c_source_code.extend(transition_code)
    generated_c_source_code.extend(generate_current_state_to_str_code)

    with open(process_name.lower() + '.c', 'wb') as c_file:
        c_file.write(u'\n'.join(indent_c_code(generated_c_source_code)).encode('latin1'))

    generated_h_source_code = []
    generated_h_source_code.extend(beginning_of_include_guard_header_file_code)
    generated_h_source_code.extend(startup_header_file_code)
    generated_h_source_code.extend(inner_procedures_header_file_code)
    generated_h_source_code.extend(input_signals_header_file_code)
    generated_h_source_code.extend(output_signals_header_file_code)
    generated_h_source_code.extend(continuous_signals_header_file_code)
    generated_h_source_code.extend(external_procedures_header_file_code)
    generated_h_source_code.extend(timers_header_file_code)
    generated_h_source_code.extend(ending_of_include_guard_header_file_code)

    with open(process_name.lower() + '.h', 'wb') as h_file:
        h_file.write(u'\n'.join(indent_c_code(generated_h_source_code)).encode('latin1'))


# Processing of the AST
@generate.register(ogAST.Decision)
def _decision(dec, **kwargs):
    ''' generate the code for a decision '''

    branch_to = kwargs['branch_to'] if 'branch_to' in kwargs else None
    exitcalls = kwargs['exitcalls'] if 'exitcalls' in kwargs else []
    sep       = kwargs['sep']       if 'sep'       in kwargs else 'if('
    last      = kwargs['last']      if 'last'      in kwargs else '} //last'

    global VAR_COUNTER
    stmts, decls = [], []

    if dec.kind == 'any':
        error = 'C backend does not support the "Decision ANY" statement'
        LOG.error(error)
        raise TypeError(error)
    elif dec.kind == 'informal_text':
        LOG.warning('Informal decision ignored')
        stmts.append('// Informal decision was ignored: {}'.format(dec.inputString))
        return stmts, decls
    elif dec.kind == 'alternative':
        # Only generate the code of one asnwer branch (like an #ifdef in C)
        # The parser has already selected the transition to generate
        if dec.alternative is not None:
            return generate(dec.alternative)
        else:
            return stmts, decls

    question_type = dec.question.exprType
    question_basic_type = find_basic_type(question_type)
    actual_type = type_name(question_type)
    basic = question_basic_type.kind in (
            'IntegerType',
            'Integer32Type',
            'IntegerU8Type',
            'BooleanType',
            'RealType',
            'EnumeratedType',
            'ChoiceEnumeratedType')

    # for ASN.1 types, declare a local variable
    # to hold the evaluation of the question
    if not basic:
        decls.append('{actType} tmp{idx};'.format(idx=dec.tmpVar, actType=actual_type))

    question_stmts, question_string, question_decls = expression(dec.question)

    # Add code-to-model traceability
    stmts.extend(traceability(dec))
    decls.extend(question_decls)
    stmts.extend(question_stmts)

    question_pointer = ''

    if not basic:
        if question_basic_type.kind == 'IA5StringType':
            VAR_COUNTER = VAR_COUNTER + 1
            decls.append(u'asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
            stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=question_basic_type.Max))
            stmts.append(u'{')
            stmts.append(u'tmp{idx}[memcpy_counter_{var_counter}] = {question_string}[memcpy_counter_{var_counter}];'.format(idx=dec.tmpVar, var_counter=VAR_COUNTER, question_string=question_string))
            stmts.append(u'}')
        else:
            question_pointer = '&'
            stmts.append('tmp{idx} = {q};'.format(idx=dec.tmpVar, q=question_string))

    stmts_last_index = len(stmts) # last stmts index before first if in C code

    for idx, answer in enumerate(dec.answers):
        stmts.extend(traceability(answer))

        for element in answer.answers:
            ans_kind    = element['kind']
            ans_content = element['content']

            if ans_kind in ('open_range', 'constant'):
                op, constant = ans_content # get the constant
                constant_basic_type_kind = find_basic_type(constant.exprType).kind
                ans_stmts, ans_str, ans_decl = expression(constant)

                for stmt in ans_stmts:
                    stmts.insert(stmts_last_index, stmt)
                    stmts_last_index = stmts_last_index + 1

                decls.extend(ans_decl)

                if not basic:
                    if op in (ogAST.ExprEq, ogAST.ExprNeq):
                        if isinstance(constant, ogAST.PrimSequenceOf):
                            ans_str = array_content(constant, ans_str, question_basic_type)
                            VAR_COUNTER = VAR_COUNTER + 1
                            decls.append('static {ty} temp_equal_{var_counter};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                            stmts.insert(stmts_last_index, 'temp_equal_{var_counter} = ({ty}) {init};'.format(ty=actual_type, var_counter=VAR_COUNTER, init=ans_str))
                            stmts_last_index = stmts_last_index + 1
                            ans_str = '&temp_equal_{var_counter}'.format(var_counter=VAR_COUNTER)
                        elif isinstance(constant, ogAST.PrimStringLiteral):
                            ans_str = array_content(constant, ans_str, question_basic_type)
                            VAR_COUNTER = VAR_COUNTER + 1
                            decls.append('static {ty} temp_equal_{var_counter} = {init};'.format(ty=actual_type, var_counter=VAR_COUNTER, init=ans_str))
                            ans_str = 'temp_equal_{var_counter}'.format(var_counter=VAR_COUNTER)

                            if question_basic_type.kind != 'IA5StringType':
                                ans_str = '&' + ans_str
                        elif isinstance(constant, ogAST.PrimChoiceItem):
                            VAR_COUNTER = VAR_COUNTER + 1
                            decls.append('static {ty} temp_equal_{var_counter};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                            stmts.insert(stmts_last_index, 'temp_equal_{var_counter} = ({ty}) {init};'.format(ty=actual_type, var_counter=VAR_COUNTER, init=ans_str))
                            stmts_last_index = stmts_last_index + 1
                            ans_str = '&temp_equal_{var_counter}'.format(var_counter=VAR_COUNTER)
                        elif isinstance(constant, ogAST.ExprNot) and constant_basic_type_kind == 'SequenceOfType':
                            VAR_COUNTER = VAR_COUNTER + 1
                            decls.append('static {ty} temp_equal_{var_counter};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                            stmts.insert(stmts_last_index, 'temp_equal_{var_counter} = ({ty}) {init};'.format(ty=actual_type, var_counter=VAR_COUNTER, init=ans_str))
                            stmts_last_index = stmts_last_index + 1
                            ans_str = '&temp_equal_{var_counter}'.format(var_counter=VAR_COUNTER)
                        else:
                            ans_str = '&' + ans_str

                        exp = '{actType}_Equal({question_pointer}tmp{idx}, {ans})'.format(actType=actual_type, question_pointer=question_pointer, idx=dec.tmpVar, ans=ans_str)

                        if op == ogAST.ExprNeq:
                            exp = u'! {}'.format(exp)
                    else:
                        exp = '(tmp{idx} {op} {ans})'.format(idx=dec.tmpVar, op='==' if op.operand == '=' else op.operand, ans=ans_str)
                else:
                    if isinstance(constant, (ogAST.PrimBitStringLiteral, ogAST.PrimOctetStringLiteral)):
                        ans_str = str(constant.numeric_value)

                    exp = u'(({q}) {op} {ans})'.format(q=question_string, op='==' if op.operand == '=' else op.operand, ans=ans_str)

                stmts.append(sep + exp + ')')
                stmts.append('{')

                if not branch_to:
                    if answer.transition:
                        transition_stmts, transition_decls = generate(answer.transition)
                    else:
                        transition_stmts, transition_decls = [';'], []

                    stmts.extend(transition_stmts)
                    decls.extend(transition_decls)
                else:
                    for exit in exitcalls:
                        stmts.append(exit)

                    stmts.append(f'trId = {branch_to};')

                #stmts.append('}')  not here
                sep = '} else if('
            elif ans_kind == 'closed_range':
                cl0_stmts, cl0_str, cl0_decl = expression(ans_content[0])
                cl1_stmts, cl1_str, cl1_decl = expression(ans_content[1])

                stmts.extend(cl0_stmts)
                decls.extend(cl0_decl)
                stmts.extend(cl1_stmts)
                decls.extend(cl1_decl)
                stmts.append('{sep} {dec} >= {cl0} && {dec} <= {cl1})'.format(sep=sep, dec=question_string, cl0=cl0_str, cl1=cl1_str))
                stmts.append('{')

                if answer.transition:
                    transition_stmts, transition_decls = generate(answer.transition)
                else:
                    transition_stmts, transition_decls = [';'], []

                stmts.extend(transition_stmts)
                decls.extend(transition_decls)
                # stmts.append('}')
                sep = '} else if('
            elif ans_kind == 'informal_text':
                continue
            elif ans_kind == 'else':
                # Keep the ELSE statement for the end
                if answer.transition:
                    else_stmts, else_decl = generate(answer.transition)
                    else_stmts.insert(0, '{')
                    #else_stmts.append('} // 3')
                else:
                    else_stmts, else_decl = ['{','// nothing done'], []

                decls.extend(else_decl)
    try:
        if sep != 'if(':
            # If there is at least one 'if' branch
            else_stmts.insert(0, '} // 1')  # close the if part
            else_stmts.insert(1, 'else')
            stmts.extend(else_stmts)
        else:
            else_stmts.insert(0, '} // 2')  # close the if part
            stmts.extend(else_stmts)
    except:
        # no else statement
        pass

    if sep != 'if(' and last:
        # "last" is usually nothing but it can be changed by parameter
        # e.g. if the decision is chained with other tests with "elsif"
        stmts.append(last)
    return stmts, decls


@generate.register(ogAST.Floating_label)
def _floating_label(label, **kwargs):
    ''' Generate the code for a floating label (C label + transition) '''

    code = []
    local_decl = []

    # Add the traceability information
    code.extend(traceability(label))
    code.append(u'{label}:'.format(label=label.inputString.lower()))

    if label.transition:
        code_trans, local_trans = generate(label.transition)
        code.extend(code_trans)
        local_decl.extend(local_trans)
    else:
        code.append('return;')

    return code, local_decl


@generate.register(ogAST.Label)
def _label(lab, **kwargs):
    ''' Transition following labels are generated in a separate section
        for visibility reasons
    '''
    return ['goto {label};'.format(label=lab.inputString.lower())], []


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output, **kwargs):
    ''' Generate the code of a set of output or procedure call statement '''

    stmts = []
    decls = []
    # need_prefix: indicate that we need a <functionName>_RI_ prefix to function calls
    # which is the case for all calls (of RIs/external procedures) but not
    # the case for the automatic call of the _transition() function
    # and the inner call of exported procedures
    need_prefix = True

    # Add the traceability information
    stmts.extend(traceability(output))

    for out in output.output:
        signal_name = out['outputName']

        if signal_name.lower() in ('write', 'writeln'):
            # special built-in SDL procedure for printing strings
            # supports printing of native types (int, real, bool)
            # but not yet complex ASN.1 structures (sequence/seqof/choice)
            for param in out['params'][:-1]:
                write_stmts, _, local = write_statement(param, newline=False)
                stmts.extend(write_stmts)
                decls.extend(local)

            for param in out['params'][-1:]:
                # Last parameter - add newline if necessary
                write_stmts, _, local = write_statement(param, newline=True if signal_name.lower() == 'writeln' else False)
                stmts.extend(write_stmts)
                decls.extend(local)

            continue
        elif signal_name.lower() == 'reset_timer':
            # built-in operator for resetting timers. param = timer name
            param, = out['params']
            param_stmts, p_id, p_local = expression(param)
            stmts.extend(param_stmts)
            decls.extend(p_local)

            stmts.append('RESET_{}();'.format(p_id))

            continue
        elif signal_name.lower() == 'set_timer':
            # built-in operator for setting a timer: SET(1000, timer_name)
            timer_value, timer_id = out['params']

            timer_stmts, t_val, t_local = expression(timer_value)
            param_stmts, p_id, p_local = expression(timer_id)

            stmts.extend(timer_stmts)
            stmts.extend(param_stmts)
            decls.extend(t_local)
            decls.extend(p_local)

            # Use a temporary variable to store the timer value
            tmp_id = 'tmp' + str(out['tmpVars'][0])
            decls.append(f'{ASN1SCC}T_UInt32 {tmp_id};')
            stmts.append('{tmp} = {val};'.format(tmp=tmp_id, val=t_val))
            stmts.append("SET_{timer}(&{value});".format(timer=p_id, value=tmp_id))

            continue

        proc, out_sig = None, None
        is_out_sig = False

        try:
            out_sig, = [sig for sig in OUT_SIGNALS
                    if sig['name'].lower() == signal_name.lower()]
            is_out_sig = False
        except ValueError:
            # Not an output, try if it is an external or inner procedure
            try:
                candidates = [sig for sig in PROCEDURES
                            if sig.inputString.lower() == signal_name.lower()]
                if not candidates:
                    raise ValueError
                if len(candidates) > 1:
                    # there are 2 results when the procedure is exported
                    # (happens in the case of a call of an inner procedure
                    # that is exported)
                    # there can be 3 if a procedure exists as PI and RI
                    if not out.get('toDest'):
                        need_prefix = False
                        # find a candidate that is not marked as external
                        for c in candidates:
                            if not c.external:
                                proc = c
                    else:
                        # if toDest is set, it has to be a RI call
                        # find the candidate that is declared as external
                        for c in candidates:
                            if c.external:
                                proc = c
                else:
                    proc = candidates[0]
                if proc.external:
                    out_sig = proc

            except ValueError:
                # Last chance to find it: if it is an exported procedure,
                # in that case an additional signal with _Transition suffix
                # exists but is not visible in the model at this point
                for sig in PROCEDURES:
                    if signal_name.lower() == f'{PROCESS_NAME.lower()}_{sig.inputString.lower()}_transition':
                        out_sig = sig
                        need_prefix = False
                        break
                else:
                    # Not there? Impossible, the parser would have barked
                    # Can happen with stop conditions because they are defined
                    # as exported but the _Transition signal was not added
                    LOG.warning(f'Could not find signal/procedure: {signal_name} - ignoring call')
                    return stmts, decls

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

                typename = type_name(param_type)
                param_stmts, p_id, p_local = expression(param)
                stmts.extend(param_stmts)
                decls.extend(p_local)

                # Create a temporary variable for input parameters only
                # (If needed, i.e. if argument is not a local variable)
                if param_direction == 'in' and (not (isinstance(param, ogAST.PrimVariable) and p_id.startswith(LPREFIX))  or isinstance(param, ogAST.PrimFPAR)):
                    tmp_id = 'tmp{}'.format(out['tmpVars'][idx])

                    if isinstance(param, ogAST.PrimStringLiteral):
                        decls.append('{sort} {tmp} = {init};'.format(tmp=tmp_id, sort=typename, init=array_content(param, p_id, find_basic_type(param_type))))
                    else:
                        decls.append('{sort} {tmp};'.format(tmp=tmp_id, sort=typename))

                        if isinstance(param, ogAST.PrimSequenceOf):
                            p_id = array_content(param, p_id, find_basic_type(param_type))

                        stmts.append(f'{tmp_id} = ({typename}) {p_id};')

                    list_of_params.append("&{}{}".format(tmp_id,", sizeof({})".format(tmp_id) if is_out_sig else ""))
                else:
                    # Output parameters/local variables
                    list_of_params.append("&{var}{shared}".format(var=p_id, shared=", sizeof({})".format(p_id) if is_out_sig else ""))

            # Call the <processName>_RI_<requiredInterfaceName> function
            if need_prefix:
                RIName = f"{PROCESS_NAME.lower()}_RI_{out['outputName']}"
            else:
                RIName = out['outputName']
            if list_of_params:
                params = ', '.join(list_of_params)
                stmts.append(f'{RIName}({params});')
            else:
                stmts.append(f'{RIName}();')
        else:
            # inner procedure call
            # TODO here some things are not aligned with Ada, several cases
            # are missing...
            list_of_params = []
            param_counter = 0

            for param in out.get('params', []):
                param_stmts, p_id, p_local = expression(param)

                stmts.extend(param_stmts)
                decls.extend(p_local)
                # no need to use temporary variables
                if proc.fpar[param_counter].get('direction') == 'out' or proc.exported:
                    p_id = '&' + p_id

                list_of_params.append( p_id)
                param_counter = param_counter + 1

            if need_prefix:
                full_name = f'{SEPARATOR}{PROCESS_NAME.lower()}_{proc.inputString}'
            else:
                full_name = f'{PROCESS_NAME.lower()}_PI_{proc.inputString}'
            if list_of_params:
                params=', '.join(list_of_params)
                stmts.append(f'{full_name}({params});')
            else:
                stmts.append(f'{full_name}();')

    return stmts, decls


@generate.register(ogAST.Procedure)
def _inner_procedure(proc, **kwargs):
    ''' Generate the code for a procedure - does not support states '''

    LOG.debug('Expanding procedure ' + proc.inputString)

    is_rpc = kwargs['is_rpc'] if 'is_rpc' in kwargs else True

    code = []
    local_decl = []

    # TODO: Update the global list of procedures
    # with procedure defined inside the current procedure
    # Not critical: the editor forbids procedures inside procedures

    # Save variable scopes (as local variables may shadow process variables)
    outer_scope = dict(VARIABLES)
    local_scope = dict(LOCAL_VARIABLES)
    outer_params = dict(LOCAL_OUT_VARIABLES)
    VARIABLES.update(proc.variables)
    # Store local variables in global context
    LOCAL_VARIABLES.update(proc.variables)
    LOCAL_OUT_VARIABLES.clear()

    # Also add procedure parameters in scope
    for var in proc.fpar:
        elem = {var['name']: (var['type'], None)}
        VARIABLES.update(elem)
        LOCAL_VARIABLES.update(elem)
        if var.get('direction') == 'out':
            LOCAL_OUT_VARIABLES.update(elem)

    if proc.external:
        # Inner procedures declared external (e.g. direct use of an external lib)
        # Build the procedure signature (function if it can return a value)
        procedure_declaration = procedure_header(proc, noPrefix=True)
        local_decl.append(f'#undef {proc.inputString}')
        local_decl.append(f'{procedure_declaration};')
        name = f'{SEPARATOR}{PROCESS_NAME.lower()}_{proc.inputString}'
        local_decl.append(f'#define {name} {proc.inputString}')

    else:
        # Build the procedure signature (function if it can return a value)
        procedure_declaration = procedure_header(proc)

        local_decl.append(f'{procedure_declaration};')
        # Generate the code for the procedure itself
        # local variables and code of the START transition
        # Recursively generate the code for inner-defined procedures
        for inner_proc in proc.content.inner_procedures:
            inner_code, inner_local = generate(inner_proc)
            local_decl.extend(inner_local)
            code.extend(inner_code)

        code.append(procedure_declaration)
        code.append('{')

        if proc.exported:
            # The input parameters of exported procedures are pointers,
            # so they must be copied in local variables (the procedure
            # statements do not expect pointers at this level
            for fpar in proc.fpar:
                typename = type_name(fpar['type'])
                name = fpar.get('name').lower()
                direction = fpar.get('direction')

                if direction != 'in':
                    continue

                code.append(f'{typename} {name} = *in__{name};')

        for var_name, (var_type, def_value) in proc.variables.items():
            typename = type_name(var_type)

            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result

                dst, dstr, dlocal = expression(def_value)
                varbty = find_basic_type(var_type)

                if varbty.kind.startswith('Integer') and isinstance(def_value, (ogAST.PrimOctetStringLiteral, ogAST.PrimBitStringLiteral)):
                    dstr = str(def_value.numeric_value)
                elif varbty.kind in ('SequenceOfType', 'OctetStringType', 'BitStringType'):
                    dstr = array_content(def_value, dstr, varbty)

                assert not dst and not dlocal, 'Ground expression error'

            code.append('{ty} {name}{default};'.format(ty=typename, name=var_name, default=' = ' + dstr if def_value else ''))

        # Look for labels in the diagram and transform them in floating labels
        Helper.inner_labels_to_floating(proc)

        if proc.exported and proc.content.start is not None and is_rpc:
            # Exported procedure end calling the corresponding transition
            # procedure that allows user to change state after RPC call
            # We need to update all the transitions of the procedure
            # (including floating labels) that contain a return statement
            # andadd the call to the __transition procedure before
            trans_with_return = []

            for each in chain ([proc.content.start.transition],
                    (lab.transition for lab in proc.content.floating_labels)):

                def rec_transition(trans : ogAST.Transition):
                    if trans.terminator:
                        if trans.terminator.kind == 'return':
                            trans_with_return.append (trans)
                    elif isinstance(trans.actions[-1], ogAST.Decision):
                        # There is no terminator, so the transition may finish
                        # with a DECISION, we must check it recursively
                        for answer in trans.actions[-1].answers:
                            rec_transition (answer.transition)

                rec_transition (each)

            for trans in trans_with_return:
                call_trans = ogAST.ProcedureCall()
                call_trans.inputString = f'{PROCESS_NAME.lower()}_{proc.inputString}_transition'
                trans_proc = f'{PROCESS_NAME.lower()}_{proc.inputString.lower()}_transition'
                call_trans.output = [{'outputName': trans_proc, 'params': [], 'tmpVars': []}]
                trans.actions.append(call_trans)

        if proc.content.start and proc.content.start.transition:
            tr_code, tr_decl = generate(proc.content.start.transition)
        else:
            tr_code, tr_decl = ['// Empty Procedure'], []

        # Generate code for the floating labels
        code_labels = []

        for label in proc.content.floating_labels:
            code_label, label_decl = generate(label)
            code_labels.extend(code_label)
            tr_decl.extend(label_decl)

        code.extend(set(tr_decl))
        code.extend(tr_code)
        code.extend(code_labels)
        code.append('}')

    code.append('\n')

    # Reset the scope to how it was prior to the procedure definition
    VARIABLES.clear()
    VARIABLES.update(outer_scope)
    LOCAL_VARIABLES.clear()
    LOCAL_VARIABLES.update(local_scope)
    LOCAL_OUT_VARIABLES.clear()
    LOCAL_OUT_VARIABLES.update(outer_params)
    LOG.debug('Expanding procedure ' + proc.inputString + ': DONE')

    return code, local_decl


@generate.register(ogAST.TaskAssign)
def _task_assign(task, **kwargs):
    ''' A list of assignments in a task symbol '''

    code, local_decl = [], []

    if task.comment:
        code.extend(traceability(task.comment))

    for expr in task.elems:
        code.extend(traceability(expr))

        # ExprAssign only returns code statements, no string
        code_assign, _, decl_assign = expression(expr)
        
        code.extend(code_assign)
        local_decl.extend(decl_assign)
        
    return code, local_decl


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task, **kwargs):
    ''' Return the code corresponding to a for loop. Two forms are possible: '''

    stmts, decls = [], []
    local_scope = dict(LOCAL_VARIABLES)

    if task.comment:
        stmts.extend(traceability(task.comment))

    stmts.extend(traceability(task))

    for loop in task.elems:
        stmts.append('{')

        # Add iterator to the list of local variables
        LOCAL_VARIABLES.update({loop['var']: (loop['type'], None)})

        if loop['range']:
            start_str, inc_str = '0', ''

            stop_stmts, stop_str, stop_local = expression(loop['range']['stop'])

            if stop_str.endswith('nCount'):
                stmts.append('int ' + loop['var'] + ';')
            else:
                stmts.append('asn1SccUint ' + loop['var'] + ';')

            if loop['range']['start']:
                start_stmts, start_str, start_local = expression(loop['range']['start'])
                decls.extend(start_local)
                stmts.extend(start_stmts)

            start_str = loop['var'] + ' = ' + start_str

            if loop['range']['step'] == 1:
                inc_str += loop['var'] + '++'
            else:
                inc_str += loop['var'] + ' +=' + str(loop['range']['step'])

            decls.extend(stop_local)
            stmts.extend(stop_stmts)

            stop_str = loop['var'] + ' < ' + stop_str

            stmts.append('for(' + start_str + '; ' + stop_str + '; ' + inc_str + ')')
            stmts.append('{')
        else:
            list_stmt, list_str, list_local = expression(loop['list'])
            basic_type = find_basic_type(loop['list'].exprType)

            if isinstance(loop['list'], ogAST.PrimSubstring):
                stmts.extend(list_stmt)
                decls.extend(list_local)
                stmts.append('asn1SccUint ' + loop['var'] + '_idx;')
                stmts.append('{} {};'.format(type_name(loop['type']), loop['var']))
                stmts.append('for({it}_idx = min_range_{var_counter}; {it}_idx <= max_range_{var_counter}; {it}_idx++)'.format(it=loop['var'], var_counter=VAR_COUNTER))
                stmts.append('{')
                stmts.append('{it} = {var}.arr[{it}_idx];'.format(it=loop['var'], var=list_str))
            elif basic_type.Min == basic_type.Max:
                stmts.extend(list_stmt)
                decls.extend(list_local)
                stmts.append('asn1SccUint ' + loop['var'] + '_idx;')
                stmts.append('{} {};'.format(type_name(loop['type']), loop['var']))
                stmts.append('for({it}_idx = 0; {it}_idx < {length}; {it}_idx++)'.format(it=loop['var'], length=basic_type.Min))
                stmts.append('{')
                stmts.append('{it} = {var}.arr[{it}_idx];'.format(it=loop['var'], var=list_str))
            else:
                stmts.extend(list_stmt)
                decls.extend(list_local)
                stmts.append('int ' + loop['var'] + '_idx;')
                stmts.append('{} {};'.format(type_name(loop['type']), loop['var']))
                stmts.append('for({it}_idx = 0; {it}_idx < {ls}.nCount; {it}_idx++)'.format(it=loop['var'],ls=list_str))
                stmts.append('{')
                stmts.append('{it} = {var}.arr[{it}_idx];'.format(it=loop['var'], var=list_str))

        code_trans, local_trans = generate(loop['transition'])

        if local_trans:
            stmts.extend(set(local_trans))

        stmts.extend(code_trans)
        stmts.append('}')
        stmts.append('}')

    # Restore list of local variables
    LOCAL_VARIABLES.clear()
    LOCAL_VARIABLES.update(local_scope)

    return stmts, decls


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task, **kwargs):
    ''' Generate C comments for informal text '''

    code = []

    if task.comment:
        code.extend(traceability(task.comment))

    code.extend(['// ' + text.replace('\n', '\n// ') for text in task.elems])
    return code, []


@generate.register(ogAST.Transition)
def _transition(tr, **kwargs):
    ''' generate the code for a transition '''

    stmts, decls = [], []

    empty_transition = all(isinstance(act, ogAST.TaskInformalText)
            for act in tr.actions)

    for action in tr.actions:
        action_stmts, action_decls = generate(action)
        stmts.extend(action_stmts)
        decls.extend(action_decls)
        if isinstance(action, ogAST.Label):
            break
    else:
        if tr.terminator:
            ns = tr.terminator.inputString.strip()
            empty_transition = False
            stmts.extend(traceability(tr.terminator))
            if tr.terminator.label:
                stmts.append(f'{ns}:')

            next_state_id = find_state_in_states(tr.terminator.next_id)
            next_state_id_str = ''

            if next_state_id:
                next_state_id_str = next_state_id
            else:
                next_state_id_str = str(tr.terminator.next_id)

            if tr.terminator.kind == 'next_state':
                history = ns in ('-', '-*')
                if tr.terminator.next_is_aggregation and not history:
                    stmts.append(f'//  Entering state aggregation {tr.terminator.inputString}')
                    # First change the state (to avoid looping in continuous signals since
                    # they will be evaluated after the start transition ; if the state is
                    # still the old state, there is a risk of infinite recursion)
                    if not tr.terminator.substate:
                        stmts.append(
                          f'{LPREFIX}.state = {generate_state_name(tr.terminator.inputString)};')
                    else:
                        # We may be already in a substate
                        stmts.append(f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}state ='
                                        f' {generate_state_name(tr.terminator.inputString)};')
                    # Call the START function of the state aggregation
                    stmts.append(f'{tr.terminator.next_id}();')
                    stmts.append('trId = -1;')

                elif not history:
                    stmts.append('trId = {next_state};'.format(next_state=next_state_id_str))

                    if tr.terminator.next_id == -1:
                        if not tr.terminator.substate:
                            stmts.append(f'{LPREFIX}.state = {generate_state_name(tr.terminator.inputString)};')
                        else:
                            stmts.append(f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}state ='
                                        f' {generate_state_name(tr.terminator.inputString)};')
                else:
                    if ns != "-*" and any(next_id
                            for next_id in tr.terminator.candidate_id.keys()
                            if next_id != -1):
                        stmts.append(f'switch({LPREFIX}.state)')
                        stmts.append('{')

                        for nid, sta in tr.terminator.candidate_id.items():
                            if nid != -1:
                                for each in sta:
                                    stmts.append(f'case {generate_state_name(each)}:')
                                    stmts.append('{')
                                    stmts.append(f'trId = {nid};')
                                    stmts.append('break;')
                                    stmts.append('}')

                        stmts.extend(['default:','{','trId = -1;','break;','}','}'])
                    else:
                        stmts.append('trId = -1;')

                stmts.append('goto continuous_signals;')
            elif tr.terminator.kind == 'join':
                stmts.append('goto {label};'.format(label=tr.terminator.inputString.lower()))
            elif tr.terminator.kind == 'stop':
                pass
                # TODO
            elif tr.terminator.kind == 'return':
                return_string = ''
                
                aggregate = False
                if tr.terminator.substate:
                    aggregate = True
                    # within a state aggregation, a return means that one
                    # of the parallel states becomes disabled, but it does
                    # not mean that the whole state aggregation can be
                    # exited. We must set this substate to a "finished"
                    # state until all the substates are returned. Then only
                    # call the overall state aggregation exit procedures.
                    stmts.append(
                        f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}state '
                        f'= {generate_state_name("state")}{SEPARATOR}end;')
                    cond = '{ctxt}.{sib}{sep}state == {state}{sep}end'
                    conds = [cond.format(sib=sib,
                                         ctxt=LPREFIX,
                                         sep=SEPARATOR,
                                         state=generate_state_name("state"))
                            for sib in tr.terminator.siblings
                            if sib.lower() != tr.terminator.substate.lower()]
                    stmts.append(f'if({" && ".join(conds)})')
                    stmts.append('{')

                if tr.terminator.next_id == -1:
                    if tr.terminator.return_expr:
                        return_stmt, return_string, return_decls = expression(tr.terminator.return_expr)
                        stmts.extend(return_stmt)
                        decls.extend(return_decls)

                    stmts.append('return{};'.format(' ' + return_string if return_string else ''))
                else:
                    stmts.append('trId = {next_state};'.format(next_state=next_state_id_str))
                    stmts.append('goto continuous_signals;')
                if aggregate:
                    stmts.append('} else')
                    stmts.append('{')
                    stmts.append('trId = -1;')
                    stmts.append('goto continuous_signals;')
                    stmts.append('}')

    if empty_transition:
        stmts.append(';')

    return stmts, decls


@singledispatch
def expression(expr):
    ''' Generate the code for Expression-classes, returning 3 things:
        - list of statements
        - useable string corresponding to the evaluation of the expression,
        - list of local declarations
    '''
    raise TypeError('Unsupported expression: ' + str(expr))
    return [], '', []


@expression.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Single variable reference '''

    prim_variable_raw_value = prim.value[0]
    out_string = ''

    if '.' in prim_variable_raw_value:
        _, qualified = ALIASES[prim.renamed_from]
        _, string, _ = expression(qualified)
        out_string = string.lower()
    else:
        local_out_variable = find_var_in_local_out_variables(prim_variable_raw_value)
        local_variable = find_var_in_local_variables(prim_variable_raw_value)
        timer_variable = find_var_in_timers(prim_variable_raw_value)
        variable = find_var_in_variables(prim_variable_raw_value)

        if local_out_variable:
            out_string = f'(*{local_out_variable})'
        elif local_variable:
            out_string = local_variable
        elif timer_variable:
            out_string = timer_variable
        elif variable:
            out_string = f'{LPREFIX}.{variable}'
        else:
            out_string = prim.value[0]
            error = 'PrimVariable value ({}) is not supported, code will probably not compile'.format(prim_variable_raw_value)
            LOG.error(error)
            #raise TypeError(error)

    return [], out_string, []


@expression.register(ogAST.PrimCall)
def _prim_call(prim):
    global MATH_INCLUDE

    function_name = prim.value[0].lower()
    LOG.debug('Expanding call to ' + function_name)

    params = prim.value[1]['procParams']
    ret_stmts = []
    ret_string = ''
    ret_decls = []

    if function_name == 'abs':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)

        if find_basic_type(params[0].exprType).kind == 'RealType':
            ret_string = 'fabs({})'.format(param_string)
        else:
            ret_string = f'({param_string}) < 0 ? -({param_string}):({param_string})'

        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'chr':
        param_stmts, param_str, param_decls = expression(params[0])

        ret_stmts.extend(param_stmts)
        ret_string = '(byte)({param})'.format(param=param_str)
        ret_decls.extend(param_decls)

    elif function_name == 'ceil':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'ceil({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'cos':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'cos({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'fix':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = '(asn1SccUint)({})'.format(param_string)
        ret_decls.extend(param_decls)

    elif function_name == 'float':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = '(asn1Real64)({})'.format(param_string)
        ret_decls.extend(param_decls)

    elif function_name == 'floor':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'floor({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'length':
        # Length of sequence of: take only the first parameter
        exp = params[0]
        exp_type = find_basic_type(exp.exprType)
        min_length = getattr(exp_type, 'Min', None)
        max_length = getattr(exp_type, 'Max', None)

        if min_length is None or max_length is None:
            error = '{} is not a SEQUENCE OF'.format(exp.inputString)
            LOG.error(error)
            raise TypeError(error)

        param_stmts, param_str, local_var = expression(exp)

        ret_stmts.extend(param_stmts)
        ret_decls.extend(local_var)

        if min_length == max_length and not isinstance(exp, ogAST.PrimSubstring):
            ret_string += min_length
        else:
            if isinstance(exp, ogAST.PrimSubstring):
                range_str = u"max_range_{var_counter} - min_range_{var_counter} + 1".format(var_counter=VAR_COUNTER)
            else:
                range_str = u"{}.nCount".format(param_str)

            ret_string += ('{}'.format(range_str))

    elif function_name == 'num':
        exp = params[0]
        param_stmts, param_string, param_decls = expression(exp)
        ret_stmts.extend(param_stmts)
        ret_string = param_string
        ret_decls.extend(param_decls)

    elif function_name == 'power':
        param_stmts0, param_string0, param_decls0 = expression(params[0])
        param_stmts1, param_string1, param_decls1 = expression(params[1])
        ret_stmts.extend(param_stmts0)
        ret_stmts.extend(param_stmts1)
        ret_string = 'pow({arg0}, {arg1})'.format(arg0 = param_string0, arg1 = param_string1)
        ret_decls.extend(param_decls0)
        ret_decls.extend(param_decls1)
        MATH_INCLUDE = True

    elif function_name == 'present':
        # User wants to know what CHOICE element is present
        exp = params[0]
        # Get the basic type to make sure it is a choice
        exp_type = find_basic_type(exp.exprType)
        # Also get the ASN.1 type name as it is
        # needed to build the Ada expression
        exp_typename = type_name(exp.exprType)

        if exp_type.kind != 'ChoiceType':
            error = '{} is not a CHOICE'.format(exp.inputString)
            LOG.error(error)
            raise TypeError(error)
        
        param_stmts, param_str, local_var = expression(exp)
        ret_stmts.extend(param_stmts)
        ret_decls.extend(local_var)
        ret_string += ('{e}.kind'.format(e=param_str))

    elif function_name == 'choice_to_int':
        p1, p2 = params
        sort = find_basic_type (p1.exprType)
        assert (sort.kind == 'ChoiceType')  # normally checked by the parser
        param_stmts, varstr, local_var = expression(p1)
        ret_stmts.extend(param_stmts)
        ret_decls.extend(local_var)
        param_stmts, defaultstr, local_var = expression(p2)
        ret_stmts.extend(param_stmts)
        ret_decls.extend(local_var)
        choices = []
        need_default = False
        # all choice elements must be either signed or unsigned
        # a mix would result in inconsistencies
        # therefore we have to cast to signed as if there is at least one
        # signed element (with the risk of cutting very big values)
        has_unsigned = False
        has_signed   = False
        for each in sort.Children.values():
            child_sort = find_basic_type(each.type)
            if child_sort.kind.startswith('Integer'):
                if float(child_sort.Min) < 0.0:
                    has_signed = True
                else:
                    has_unsigned = True
        need_cast = has_signed and has_unsigned
        for child_name, descr in sort.Children.items():
            child_name_c = child_name.replace('-', '_')
            child_id   = descr.EnumID
            child_sort = find_basic_type(descr.type)
            if not child_sort.kind.startswith('Integer'):
                need_default = True
                continue
            set_value = f'{varstr}.u.{child_name_c}'
            if need_cast and float(child_sort.Min) >= 0.0:
                set_value = f'(asn1SccSint){set_value}'
            choices.append(f'{varstr}.kind=={child_id}?{set_value}')
        if need_default:
            choices.append(defaultstr)
        ret_string = ':'.join(choices)

    elif function_name == 'round':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'roundf({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'sin':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'sinf({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'sqrt':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'sqrt({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name == 'trunc':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'trunc({})'.format(param_string)
        ret_decls.extend(param_decls)
        MATH_INCLUDE = True

    elif function_name in ('shift_left', 'shift_right'):
        p1, p2 = params

        param_stmts, s1, param_decls = expression(p1)
        ret_stmts.extend(param_stmts)
        ret_decls.extend(param_decls)

        param_stmts, s2, param_decls = expression(p2)
        ret_stmts.extend(param_stmts)
        ret_decls.extend(param_decls)

        shift_operator = '<<' if function_name == "shift_left" else '>>'
        ret_string = u'({} {} {})'.format(s1, shift_operator, s2)
    elif function_name == 'exist':
        # User wants to know if an optional field is present or not
        selector = params[0]  # type PrimSelector
        receiver = selector.value[0]
        field    = selector.value[1]
        # In C, case matters, so we must retrieve the field name in the type
        fields   = find_basic_type(receiver.exprType).Children.keys()
        for each in fields:
            with_case = each.replace('-', '_')
            if with_case.lower() == field.lower():
                field = with_case
                break
        rec_stmt, rec_str, rec_decl = expression (receiver)
        ret_stmts.extend(rec_stmt)
        ret_decls.extend(rec_decl)
        ret_string += f'({rec_str}.exist.{field} == 1)'
    elif function_name in ('to_selector', 'to_enum'):
        variable, target_type = params
        var_typename = type_name (variable.exprType, False)
        var_stmts, var_str, var_decl = expression (variable)
        ret_stmts.extend(var_stmts)
        ret_decls.extend(var_decl)
        destSort = target_type.value[0]
        sortC = destSort.replace('-', '_')
        sort_name = f'{ASN1SCC}{PROCESS_NAME.capitalize()}_{sortC.capitalize()}_Selection'
        if function_name == 'to_selector':
            # add 1 because we are converting to a CHOICE selector, which has an
            # additional field choice_NONE with value 0. so all values are shifted
            ret_string += f"(({sort_name}){var_str} + 1)"
        elif function_name == 'to_enum':
            # symetrically to to_selector, we must remove 1 to get the right value
            sort_name_val = f'{ASN1SCC}{sortC}'
            sort_name = f'{ASN1SCC}{var_typename}'
            ret_string += f"(({sort_name_val}){var_str} - 1)"
    elif function_name == 'val':
        variable, target_type = params
        var_typename = type_name (variable.exprType)
        var_stmts, var_str, var_decl = expression (variable)
        ret_stmts.extend(var_stmts)
        ret_decls.extend(var_decl)
        ret_string += f"((int){var_str})"
    else:
        procedure = find_procedure_by_name(function_name)
        if not procedure:
            print("ERROR:", function_name, ' NOT SUPPORTED')

        ret_string = f"{SEPARATOR}{PROCESS_NAME.lower()}_{procedure.inputString} ("
        list_of_params = []

        for param_counter, param in enumerate(params):
            param_stmt, param_str, local_var = expression(param)
            param_direction = procedure.fpar[param_counter]['direction']
            param_type = procedure.fpar[param_counter]['type']
            param_basic_type = find_basic_type (param_type)

            if isinstance(param, ogAST.PrimStringLiteral) and param_basic_type.kind.startswith('Integer'):
                param_str = str(param.numeric_value)
            elif param_direction == 'out':
                param_str = '&' + param_str

            list_of_params.append(param_str)
            ret_stmts.extend(param_stmt)
            ret_decls.extend(local_var)

        ret_string += ', '.join(list_of_params)
        ret_string += ')'
    LOG.debug('Expanding call to ' + function_name + ': DONE')

    return ret_stmts, ret_string, ret_decls


@expression.register(ogAST.PrimIndex)
def _prim_index(prim):
    stmts, string, local_decl = [], '', []

    receiver = prim.value[0]

    receiver_stms, receiver_string, receiver_decl = expression(receiver)
    string = receiver_string

    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    idx_stmts, idx_string, idx_var = expression(prim.value[1]['index'][0])
    string += u'.arr'

    if not isinstance(receiver, ogAST.PrimSubstring):
        string += u'[{idx}]'.format(idx=idx_string)
    else:
        string += u'[{idx} + min_range_{var_counter}]'.format(idx=idx_string, var_counter=VAR_COUNTER)

    stmts.extend(idx_stmts)
    local_decl.extend(idx_var)

    return stmts, str(string), local_decl


@expression.register(ogAST.PrimSelector)
def _prim_selector(prim):
    ''' Selector (field access with '!' separation) '''

    stmts, string, local_decl = [], '', []

    receiver = prim.value[0]
    field_name = prim.value[1]

    receiver_stms, receiver_string, receiver_decl = expression(receiver)
    string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    receiver_bty = find_basic_type(receiver.exprType)

    if receiver_bty.kind == 'ChoiceType':
        # try to use original children selector since field_name is always lowercase
        for field_case in receiver_bty.Children:
            if field_case.replace('-','_').lower() == field_name.lower():
                break
        else:
            field_case = field_name

        string = ('{string}.u.{field_name}'.format(field_name=field_case.replace('-','_'),
                                                   string=string))
    else:
        # Sequence: we must get the right casing of the field
        for field_case in receiver_bty.Children:
            if field_case.replace('-','_').lower() == field_name.lower():
                break
        else:
            field_case = field_name
        
        string += '.' + field_case.replace('-','_')

    return stmts, str(string), local_decl


@expression.register(ogAST.PrimStateReference)
def _primary_state_reference(prim):
    ''' Reference to the current state '''

    error = 'To Be Implemented'
    LOG.error(error)
    raise TypeError(error)
    return [], '', []


@expression.register(ogAST.ExprPlus)
@expression.register(ogAST.ExprMul)
@expression.register(ogAST.ExprMinus)
@expression.register(ogAST.ExprGt)
@expression.register(ogAST.ExprGe)
@expression.register(ogAST.ExprLt)
@expression.register(ogAST.ExprLe)
@expression.register(ogAST.ExprDiv)
@expression.register(ogAST.ExprRem)
def _basic_operators(expr):
    ''' Expressions with two sides '''

    code, local_decl = [], []

    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)

    operand = '%' if isinstance(expr, ogAST.ExprRem) else expr.operand
    string = u'({left} {op} {right})'.format(left=left_str, op=operand, right=right_str)

    code.extend(left_stmts)
    code.extend(right_stmts)

    local_decl.extend(left_local)
    local_decl.extend(right_local)

    return code, str(string), local_decl


@expression.register(ogAST.ExprMod)
def _basic_operators(expr):
    ''' Expressions with two sides '''
    code, local_decl = [], []

    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)

    string = u'({left} % {right})'.format(left=left_str, op=expr.operand, right=right_str)

    code.extend(left_stmts)
    code.extend(right_stmts)

    local_decl.extend(left_local)
    local_decl.extend(right_local)

    return code, str(string), local_decl


@expression.register(ogAST.ExprEq)
@expression.register(ogAST.ExprNeq)
def _equality(expr):
    global VAR_COUNTER
    global VARIABLES

    stmts, left_string, decls = expression(expr.left)
    right_stmts, right_string, right_local = expression(expr.right)

    stmts.extend(right_stmts)
    decls.extend(right_local)

    asn1_type = getattr(expr.left.exprType, 'ReferencedTypeName', None)
    actual_type = type_name(expr.left.exprType)

    lbty = find_basic_type(expr.left.exprType)
    rbty = find_basic_type(expr.right.exprType)

    operand = '==' if isinstance(expr, ogAST.ExprEq) else '!='

    basic = lbty.kind in ('IntegerType',
                          'Integer32Type',
                          'IntegerU8Type',
                          'BooleanType',
                          'EnumeratedType',
                          'ChoiceEnumeratedType')

    if basic:
        if isinstance(expr.right, (ogAST.PrimBitStringLiteral,
                                   ogAST.PrimOctetStringLiteral)):
            right_string = str(expr.right.numeric_value)

        string = f'({left_string} {operand} {right_string})'
    else:
        if asn1_type in TYPES:
            if isinstance(expr.left, ogAST.PrimSelector):
                VAR_COUNTER = VAR_COUNTER + 1
                if isinstance(expr.right, ogAST.PrimStringLiteral):
                    decls.append(u'{ty} selector_{var_counter} = {{0}};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                    decls.append(u'asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
                    stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {right_size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))
                    stmts.append(u'{')
                    stmts.append(u'selector_{var_counter}[memcpy_counter_{var_counter}] = {left}[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, left=left_string))
                    stmts.append(u'}')
                    left_string = u'selector_{var_counter}'.format(var_counter=VAR_COUNTER)
                else:
                    decls.append(u'{ty} selector_{var_counter};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                    stmts.append(u'selector_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
                    left_string = u'&selector_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif not (isinstance(expr.left, ogAST.PrimVariable) or 
                      isinstance(expr.left, ogAST.ExprAnd) or 
                      isinstance(expr.left, ogAST.ExprOr) or 
                      isinstance(expr.left, ogAST.ExprXor) or 
                      isinstance(expr.left, ogAST.ExprImplies) or 
                      isinstance(expr.left, ogAST.ExprNot)):
                raise NotImplementedError(str(type(expr.left)) + ' in left part of comparison')
            else:
                left_string = '&' + left_string

            if isinstance(expr.right, ogAST.PrimReal):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(f'static {actual_type} constant_{VAR_COUNTER} = {right_string};')
                right_string = '&constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif isinstance(expr.right, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                VAR_COUNTER = VAR_COUNTER + 1

                if lbty.kind == 'IA5StringType':
                    decls.append('static {ty} constant_{var_counter} = {{{values}}};'.format(ty=actual_type, var_counter=VAR_COUNTER, size=rbty.Max, values=right_string))
                    right_string = 'constant_{var_counter}'.format(var_counter=VAR_COUNTER)
                else:
                    decls.append('static {ty} constant_{var_counter} = ({ty}) {{{size}, {{{values}}}}};'.format(ty=actual_type, var_counter=VAR_COUNTER, size=rbty.Max, values=right_string))
                    right_string = '&constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif isinstance(expr.right, ogAST.PrimEmptyString):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(f'static {actual_type} constant_{VAR_COUNTER} = {{}};')
                right_string = '&constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif isinstance(expr.right, (ogAST.PrimChoiceItem, ogAST.PrimSequence)):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(f'static {actual_type} constant_{VAR_COUNTER};')
                stmts.append(f'constant_{VAR_COUNTER} = ({actual_type}) {right_string};')
                right_string = '&constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif isinstance(expr.right, ogAST.PrimCall):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(f'static {actual_type} constant_{VAR_COUNTER};')
                stmts.append(f'constant_{VAR_COUNTER} = ({actual_type}) {right_string};')
                right_string = '&constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif not (isinstance(expr.right, ogAST.PrimVariable)):
                raise NotImplementedError(str(type(expr.right)) + f' in right part of comparison ({expr.inputString})')
            else:
                right_string = '&' + right_string

            string = '{sort}_Equal({left}, {right})'.format(sort=actual_type, left=left_string, right=right_string)
        else:
            # Raw types on both left and right.... use simple operator
            if isinstance(expr.right, ogAST.PrimStringLiteral):
                VAR_COUNTER = VAR_COUNTER + 1
                variable_name = left_string[len(LPREFIX)+1:] if left_string.startswith(LPREFIX) else left_string

                if variable_name in LOCAL_VARIABLE_TYPES:
                    left_type = LOCAL_VARIABLE_TYPES[variable_name]
                elif variable_name in VARIABLES:
                    left_type = type_name(VARIABLES[variable_name][0])
                else:
                    raise NotImplementedError('Type of {var} is unknown'.format(var=variable_name))

                decls.append('static {ty} constant_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=left_type, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
                right_string = u'constant_{var_counter}'.format(var_counter=VAR_COUNTER)
                string = '{left_type}_Equal(&{ls}, &{rs})'.format(left_type=left_type, ls=left_string, rs=right_string)
            else:
                string = "(({left}) {op} ({right}))".format(left=left_string, op=operand, right=right_string)

        if isinstance(expr, ogAST.ExprNeq):
            string = u'! {}'.format(string)

    return stmts, str(string), decls


@expression.register(ogAST.ExprAssign)
def _assign_expression(expr):
    LOG.debug('Expanding assignment: ' + expr.inputString)

    global LEFT_TYPE
    global VAR_COUNTER

    stmts, decls = [], []
    strings = []

    left_stmts, left_string, left_decls = expression(expr.left)
    variable_name = left_string[len(LPREFIX)+1:] if left_string.startswith(LPREFIX) else left_string
    basic_left = find_basic_type(expr.left.exprType)
    basic_right = find_basic_type(expr.right.exprType)

    LEFT_TYPE=type_name(expr.left.exprType)
#   if variable_name in VARIABLES:
#       LEFT_TYPE = type_name(VARIABLES[variable_name][0])
#   else:
#       if basic_left.__name__ == 'Subtype':  # numerical type
#           breakpoint()
#           LEFT_TYPE = ''
#       else:
#           LEFT_TYPE = 'asn1Scc' + basic_left.__name__[:-5].replace('-','_')

    right_stmts, right_string, right_decls = expression(expr.right)
    # If left side is a string/seqOf and right side is a substring, we must
    # assign the .arr and .Length parts properly
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    decls.extend(left_decls)
    decls.extend(right_decls)

    if (basic_left.kind == 'IA5StringType' and isinstance(expr.right, ogAST.PrimStringLiteral)):
        VAR_COUNTER = VAR_COUNTER + 1
        decls.append('{ty} assign_var_{var_counter} = {{{init}}};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, init=right_string))
        decls.append('asn1SccUint var_counter_{var_counter};'.format(var_counter=VAR_COUNTER))

        stmts.append('for(var_counter_{var_counter} = 0; var_counter_{var_counter} < {size}; var_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=basic_right.Max))
        stmts.append('{')
        stmts.append('{lvar}[var_counter_{var_counter}] = assign_var_{var_counter}[var_counter_{var_counter}];'.format(lvar=left_string, var_counter=VAR_COUNTER))
        stmts.append('}')
    elif basic_left.kind in ('SequenceOfType', 'OctetStringType'):
        rlen = "{}.nCount".format(right_string)

        if isinstance(expr.right, ogAST.PrimSubstring):
            rlen = u'max_range_{var_counter} - min_range_{var_counter} + 1'.format(var_counter=VAR_COUNTER)

            decls.append('asn1SccUint var_counter_{var_counter};'.format(var_counter=VAR_COUNTER))
            stmts.append('{')
            stmts.append('for(var_counter_{var_counter} = 0; var_counter_{var_counter} <= max_range_{var_counter} - min_range_{var_counter}; var_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, rvar=right_string))
            stmts.append('{')
            stmts.append('{lvar}.arr[var_counter_{var_counter}] =  {rvar}.arr[var_counter_{var_counter} + min_range_{var_counter}];'.format(lvar=left_string, rvar=right_string, var_counter=VAR_COUNTER))
            stmts.append('}')
            stmts.append('}')
        elif isinstance(expr.right, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            VAR_COUNTER = VAR_COUNTER + 1
            decls.append('{ty} assign_var_{var_counter} = {init};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, init=array_content(expr.right, right_string, basic_left)))
            strings.append("{lvar} = assign_var_{var_counter};".format(lvar=left_string, var_counter=VAR_COUNTER))
            rlen = None
        elif isinstance(expr.right, ogAST.ExprNot) and isinstance(expr.right.expr, ogAST.PrimSequenceOf):
            strings.append("{ls} = ({ty}) {rs};".format(ls=left_string, ty=LEFT_TYPE, rs=right_string))
            rlen = None
        else:
            # Right part is a variable
            strings.append(f"{left_string} = ({LEFT_TYPE}) {right_string};")
            rlen = None

        if rlen and basic_left.Min != basic_left.Max:
            strings.append(u"{lvar}.nCount= {rlen};".format(lvar=left_string, rlen=rlen))
    else:
        if isinstance(expr.right, ogAST.PrimSequence):
            # not sure why we need an intermediate variable here...removed it
            #VAR_COUNTER = VAR_COUNTER + 1
            #decls.append(f'static {LEFT_TYPE} constant_{VAR_COUNTER};')
            #stmts.append(f'constant_{VAR_COUNTER} = ({LEFT_TYPE}) {right_string};')
            #stmts.append('{ls} = constant_{var_counter};'.format(ls=left_string, var_counter=VAR_COUNTER))
            stmts.append(f'{left_string} = ({LEFT_TYPE}) {right_string};')
        else:
            strings.append(f"{left_string} = ({LEFT_TYPE}) {right_string};")

    stmts.extend(strings)
    LOG.debug('Expanding assignment: ' + expr.inputString + ': DONE')

    return stmts, '', decls


@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
@expression.register(ogAST.ExprImplies)
def _bitwise_operators(expr):
    ''' Logical operators '''

    stmts, decls = [], []
    left_stmts, left_string, left_local = expression(expr.left)
    right_stmts, right_string, right_local = expression(expr.right)
    basic_type = find_basic_type(expr.exprType)

    if basic_type.kind != 'BooleanType':
        left_bty  = find_basic_type (expr.left.exprType)
        right_bty  = find_basic_type (expr.right.exprType)

        if expr.right.is_raw and left_bty.kind.startswith('Integer'):
            # right is raw (e.g. hex string literal) and left is a number
            if isinstance (expr.right, (ogAST.PrimBitStringLiteral, ogAST.PrimOctetStringLiteral)):
                right_payload = str(expr.right.numeric_value)
            else:
                right_payload = right_string

            left_payload = left_string

            string = f'({left_payload} {get_bitwise_operator(expr.operand)} {right_payload})'
        elif left_bty.kind.startswith('Integer') and right_bty.kind.startswith('Integer'):
            # left and right are numbers
            string = f'({left_string} {get_bitwise_operator(expr.operand)} {right_string})'
        else:
            if not isinstance(expr.left, ogAST.PrimVariable):
                raise NotImplementedError(str(type(expr.left)))

            global VAR_COUNTER
            VAR_COUNTER = VAR_COUNTER + 1

            variable_name = left_string[len(LPREFIX)+1:] if left_string.startswith(LPREFIX) else left_string
            decls.append(u'{ty} expr_{var_counter};'.format(ty=type_name(VARIABLES[variable_name][0]), var_counter=VAR_COUNTER))
            decls.append(u'asn1SccUint expr_counter_{var_counter};'.format(var_counter=VAR_COUNTER))

            if basic_type.Min != basic_type.Max:
                stmts.append(u'for(expr_counter_{var_counter} = 0; expr_counter_{var_counter} < {ls}.nCount; expr_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, ls=left_string))
            else:
                stmts.append(u'for(expr_counter_{var_counter} = 0; expr_counter_{var_counter} < {size}; expr_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=basic_type.Max))

            stmts.append(u'{')

            if isinstance(expr, ogAST.ExprImplies):
                stmts.append(u'expr_{var_counter}.arr[expr_counter_{var_counter}] = ({ls}.arr[expr_counter_{var_counter}] && {rs}.arr[expr_counter_{var_counter}]) || !{ls}.arr[expr_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, ls=left_string, rs=right_string))
            else:
                op = '||' if isinstance(expr, ogAST.ExprOr) else '&&' if isinstance(expr, ogAST.ExprAnd) else '!='
                stmts.append(u'expr_{var_counter}.arr[expr_counter_{var_counter}] = {ls}.arr[expr_counter_{var_counter}] {op} {rs}.arr[expr_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, ls=left_string, op=op, rs=right_string))

            stmts.append(u'}')
            string = u'expr_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr, ogAST.ExprImplies):
        string = u'(({left} && {right}) || !{left})'.format(left=left_string, right=right_string)
    else:
        op = '||' if isinstance(expr, ogAST.ExprOr) else '&&' if isinstance(expr, ogAST.ExprAnd) else '!='
        string = u'({left} {op} {right})'.format(left=left_string, op=op, right=right_string)

    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    decls.extend(left_local)
    decls.extend(right_local)

    return stmts, str(string), decls


@expression.register(ogAST.ExprNot)
def _not_expression(expr):
    ''' Generate the code for a not expression '''

    stmts, decls = [], []

    if isinstance(expr.expr, ogAST.PrimSequenceOf):
        # Raw sequence of boolean (e.g. not "{true, false}") -> flip values
        for each in expr.expr.value:
            each.value[0] = 'true' if each.value[0] == 'false' else 'false'

    expr_stmts, expr_str, expr_local = expression(expr.expr)
    stmts.extend(expr_stmts)
    decls.extend(expr_local)

    bty_inner = find_basic_type(expr.expr.exprType)
    bty_outer = find_basic_type(expr.exprType)

    if bty_outer.kind != 'BooleanType' and not 'Integer' in bty_outer.kind:
        if bty_outer.Min == bty_outer.Max:
            size_expr = bty_outer.Max
        elif bty_inner.Min == bty_inner.Max:
            size_expr = '{}'.format(bty_inner.Min)
        else:
            size_expr = '{}.nCount'.format(expr_str)

        if isinstance(expr.expr, ogAST.PrimSequenceOf):
            string = array_content(expr.expr, expr_str, bty_outer)
        elif isinstance(expr.expr, ogAST.PrimVariable):
            global VAR_COUNTER
            VAR_COUNTER = VAR_COUNTER + 1

            decls.append(u'{ASN1SCC}{ty} not_{var_counter};'.format(ASN1SCC=ASN1SCC, ty=bty_outer.__name__[:-5].replace('-','_'), var_counter=VAR_COUNTER))
            decls.append(u'asn1SccUint not_counter_{var_counter};'.format(var_counter=VAR_COUNTER))
            stmts.append(u'{')
            stmts.append(u'for(not_counter_{var_counter} = 0; not_counter_{var_counter} < {size_expr}; not_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size_expr=size_expr))
            stmts.append(u'{')
            stmts.append(u'not_{var_counter}.arr[not_counter_{var_counter}] = !{right_var}.arr[not_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, right_var=expr_str))
            stmts.append(u'}')

            if bty_outer.Min != bty_outer.Max:
                stmts.append(u'not_{var_counter}.nCount = {right_var}.nCount;'.format(var_counter=VAR_COUNTER, right_var=expr_str))

            stmts.append(u'}')
            string = (u'not_{var_counter}'.format(var_counter=VAR_COUNTER))
        elif isinstance(expr.expr, ogAST.PrimCall):
            string = f'!{expr_str}'
        else:
            raise NotImplementedError(u'Not of a ' + str(type(expr.expr)))
            string = u'{{{{! {expr_str} }}, {size_expr} }})'.format(expr_str=expr_str.replace(',',',!'), size_expr=size_expr)
    else:
        string = u'!{expr}'.format(expr=expr_str.replace(',',',!'))

    return stmts, str(string), decls


@expression.register(ogAST.ExprNeg)
def _neg_expression(expr):
    ''' Generate the code for a negative expression '''

    code, local_decl = [], []
    expr_stmts, expr_str, expr_local = expression(expr.expr)
    string = u'(-{expr})'.format( expr=expr_str)
    code.extend(expr_stmts)
    local_decl.extend(expr_local)

    return code, str(string), local_decl


@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''

    LOG.debug(str(type(expr.left)) + str(type(expr.right)))

    global LEFT_TYPE
    global VAR_COUNTER
    global LOCAL_VARIABLE_TYPES

    stmts, string, decls = [], '', []

    lbty = find_basic_type(expr.left.exprType)
    rbty = find_basic_type(expr.right.exprType)

    stmts.append('{')

    left_stmts, left_string, left_decls = expression(expr.left)
    stmts.extend(left_stmts)
    decls.extend(left_decls)

    right_stmts, right_string, right_decls = expression(expr.right)
    stmts.extend(right_stmts)
    decls.extend(right_decls)

    VAR_COUNTER = VAR_COUNTER + 1

    if (isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimSequenceOf)):
        decls.append('asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append('{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        decls.append('{ty} right_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
        stmts.append('right_temp_{var_counter} =({ty}) {{{size}, {{{init}}}}};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))

        LOCAL_VARIABLE_TYPES['memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {right_size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = right_temp_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {right_size};'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimSequenceOf) and isinstance(expr.right, ogAST.PrimSequenceOf):
        # ?? I find this suspiciousm why would result be of size 2?
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        stmts.append(u'memcpy_temp_{var_counter}.arr[0] = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'memcpy_temp_{var_counter}.arr[1] = {rs};'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'memcpy_temp_{var_counter}.nCount = 2;'.format(var_counter=VAR_COUNTER))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, (ogAST.PrimVariable, ogAST.PrimSelector)) and isinstance(expr.right, ogAST.PrimSequenceOf):
        decls.append(u'asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        decls.append(u'{ty} right_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        stmts.append(u'right_temp_{var_counter} =({ty}) {{{size}, {{{init}}}}};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {right_size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = right_temp_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {right_size};'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimSequenceOf) and isinstance(expr.right, ogAST.PrimVariable):
        # e.g. in foo := { bar } // baz
        # LEFT_TYPE is the type of the result of the append (here: type of foo)
        decls.append(f'asn1SccUint memcpy_counter_{VAR_COUNTER} = 0;')
        decls.append(f'{LEFT_TYPE} memcpy_temp_{VAR_COUNTER};')
        #decls.append(f'{LEFT_TYPE} left_temp_{VAR_COUNTER};')

        LOCAL_VARIABLE_TYPES[f'memcpy_temp_{VAR_COUNTER}'] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(f'memcpy_temp_{VAR_COUNTER} = ({LEFT_TYPE}) {{{lbty.Max}, {{{left_string}}}}};')
        #stmts.append(f'memcpy_temp_{VAR_COUNTER} = {left_string};')

        #Then append the right part
        stmts.append(f'for(memcpy_counter_{VAR_COUNTER} = 0; memcpy_counter_{VAR_COUNTER} < {right_string}.nCount; memcpy_counter_{VAR_COUNTER}++)')
        stmts.append('{')
        stmts.append(f'memcpy_temp_{VAR_COUNTER}.arr[memcpy_temp_{VAR_COUNTER}.nCount + memcpy_counter_{VAR_COUNTER}] = {right_string}.arr[memcpy_counter_{VAR_COUNTER}];')
        stmts.append('}')
        stmts.append(f'memcpy_temp_{VAR_COUNTER}.nCount += {right_string}.nCount;')

        string = f'memcpy_temp_{VAR_COUNTER}'

    elif isinstance(expr.left, (ogAST.PrimVariable, ogAST.PrimSelector)) and isinstance(expr.right, ogAST.PrimVariable):
        decls.append(u'int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {rs}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {rs}.nCount;'.format(var_counter=VAR_COUNTER, rs=right_string))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimVariable) and isinstance(expr.right, ogAST.PrimStringLiteral):
        decls.append(u'asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        decls.append('static {ty} constant_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=rbty.Max))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = constant_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {rsize};'.format(var_counter=VAR_COUNTER, rsize=rbty.Max))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimVariable):
        decls.append(u'int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {rs}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {rs}.nCount;'.format(var_counter=VAR_COUNTER, rs=right_string))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimVariable) and isinstance(expr.right, ogAST.PrimConditional):
        decls.append(u'int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {rs}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {rs}.nCount;'.format(var_counter=VAR_COUNTER, rs=right_string))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimSubstring) and isinstance(expr.right, ogAST.PrimSequenceOf):
        decls.append(f'asn1SccUint memcpy_counter_{VAR_COUNTER} = 0;')
        decls.append(f'{LEFT_TYPE} memcpy_temp_{VAR_COUNTER};')
        decls.append(f'static {LEFT_TYPE} constant_{VAR_COUNTER};')
        stmts.append(f'constant_{VAR_COUNTER} = ({LEFT_TYPE}) {{{rbty.Max}, {{{right_string}}}}};')

        LOCAL_VARIABLE_TYPES[f'memcpy_temp_{VAR_COUNTER}'] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(f'for(memcpy_counter_{VAR_COUNTER} = 0; memcpy_counter_{VAR_COUNTER} < (max_range_{VAR_COUNTER-1} - min_range_{VAR_COUNTER-1}) + 1; memcpy_counter_{VAR_COUNTER}++)')
        stmts.append('{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = {ls}.arr[min_range_{var_counter1} + memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1, ls=left_string))
        stmts.append('}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount = (max_range_{var_counter1} - min_range_{var_counter1} + 1);'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {right_size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = constant_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {right_size};'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimSequenceOf) and isinstance(expr.right, ogAST.PrimSubstring):
        decls.append(f'asn1SccUint memcpy_counter_{VAR_COUNTER} = 0;')

        # Result container
        decls.append(f'{LEFT_TYPE} memcpy_temp_{VAR_COUNTER};')

        # Resulting string
        string = f'memcpy_temp_{VAR_COUNTER}'

        LOCAL_VARIABLE_TYPES[f'memcpy_temp_{VAR_COUNTER}'] = LEFT_TYPE

        #First copy left part (PrimSequenceOf) in the result
        stmts.append(f'memcpy_temp_{VAR_COUNTER} = ({LEFT_TYPE}) {{{lbty.Max}, {{{left_string}}}}};')

        #Then append the right part (PrimSubString)
        stmts.append(f'for(memcpy_counter_{VAR_COUNTER} = 0; memcpy_counter_{VAR_COUNTER} < (max_range_{VAR_COUNTER-1} - min_range_{VAR_COUNTER-1}) + 1; memcpy_counter_{VAR_COUNTER}++)')
        stmts.append('{')
        stmts.append(f'memcpy_temp_{VAR_COUNTER}.arr[memcpy_temp_{VAR_COUNTER}.nCount + memcpy_counter_{VAR_COUNTER}] = {right_string}.arr[min_range_{VAR_COUNTER-1} + memcpy_counter_{VAR_COUNTER}];')
        stmts.append(f'memcpy_temp_{VAR_COUNTER}.nCount++;')
        stmts.append('}')

    elif isinstance(expr.left, ogAST.PrimSubstring) and isinstance(expr.right, ogAST.PrimSubstring):
        decls.append(u'asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER-1))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER-1))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER-1)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < (max_range_{var_counter1} - min_range_{var_counter1}) + 1; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER-1, var_counter1=VAR_COUNTER-2))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = {ls}.arr[min_range_{var_counter1} + memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER-1, var_counter1=VAR_COUNTER-2, ls=left_string))
        stmts.append(u'}\n')
        stmts.append(u'memcpy_temp_{var_counter}.nCount = (max_range_{var_counter1} - min_range_{var_counter1} + 1);\n'.format(var_counter=VAR_COUNTER-1, var_counter1=VAR_COUNTER-2))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < (max_range_{var_counter} - min_range_{var_counter} + 1); memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER-1))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[min_range_{var_counter} + memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER-1, rs=right_string))
        stmts.append(u'}\n')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += (max_range_{var_counter} - min_range_{var_counter} + 1);'.format(var_counter=VAR_COUNTER-1))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER-1)
    elif (isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimConstant)):
        decls.append(u'int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))

        #Append right part single value
        if find_basic_type(expr.right.exprType).kind == 'SequenceOfType':
            stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {rs}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, rs=right_string))
            stmts.append(u'{')
            stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, rs=right_string))
            stmts.append(u'}')
            stmts.append(u'memcpy_temp_{var_counter}.nCount = {rs}.nCount;'.format(var_counter=VAR_COUNTER, rs=right_string))
        else:
            stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount] = {rs};'.format(var_counter=VAR_COUNTER, rs=right_string))
            stmts.append(u'memcpy_temp_{var_counter}.nCount += 1;'.format(var_counter=VAR_COUNTER))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, (ogAST.PrimVariable, ogAST.ExprAppend)) and isinstance(expr.right, ogAST.PrimSubstring):
        decls.append(u'asn1SccUint memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} <= (max_range_{var_counter1} - min_range_{var_counter1}); memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[min_range_{var_counter1} + memcpy_counter_{var_counter}];'
                .format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1, rs=right_string))
        stmts.append(u'}\n')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += max_range_{var_counter1} - min_range_{var_counter1} + 1;'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimStringLiteral) and isinstance(expr.right, ogAST.PrimStringLiteral):
        typename = type_name(expr.expected_type)

        decls.append(u'int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=typename, var_counter=VAR_COUNTER))
        decls.append('static {ty} constant_left_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=typename, var_counter=VAR_COUNTER, size=lbty.Max, init=left_string))
        decls.append('static {ty} constant_right_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=typename, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = typename

        # Append the left part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < constant_left_{var_counter}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = constant_left_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}\n')

        # Append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < constant_right_{var_counter}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter} + constant_left_{var_counter}.nCount] = constant_right_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}\n')

        stmts.append(u'memcpy_temp_{var_counter}.nCount = constant_left_{var_counter}.nCount + constant_right_{var_counter}.nCount;'.format(var_counter=VAR_COUNTER))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif (isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimStringLiteral)):
        typename = type_name(expr.expected_type)

        decls.append(u'int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append('static {ty} memcpy_temp_{var_counter};'.format(ty=typename, var_counter=VAR_COUNTER))
        decls.append('static {ty} constant_right_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=typename, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = typename

        # Append the left part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {left}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, left=left_string))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = {left}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, left=left_string))
        stmts.append(u'}\n')

        # Append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < constant_right_{var_counter}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter} + {left}.nCount] = constant_right_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, left=left_string))
        stmts.append(u'}\n')

        stmts.append(u'memcpy_temp_{var_counter}.nCount = {left}.nCount + constant_right_{var_counter}.nCount;'.format(var_counter=VAR_COUNTER, left=left_string))

        string = 'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimStringLiteral) and isinstance(expr.right, ogAST.PrimVariable):
        typename = type_name(expr.expected_type)

        decls.append('int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append('static {ty} memcpy_temp_{var_counter};'.format(ty=typename, var_counter=VAR_COUNTER))
        decls.append('static {ty} constant_left_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=typename, var_counter=VAR_COUNTER, size=lbty.Max, init=left_string))

        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = typename

        # Append the left part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < constant_left_{var_counter}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = constant_left_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}\n')

        # Append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {right}.nCount; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, right=right_string))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter} + constant_left_{var_counter}.nCount] = {right}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, right=right_string))
        stmts.append(u'}\n')

        stmts.append(u'memcpy_temp_{var_counter}.nCount = constant_left_{var_counter}.nCount + {right}.nCount;'.format(var_counter=VAR_COUNTER, right=right_string))

        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    else:
        LOG.error("Append expression not supported in C backend: " + expr.inputString)
        raise NotImplementedError(str(type(expr.left)) + ' and ' + str(type(expr.right)))

    stmts.append(u'}')

    return stmts, string, decls


@expression.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' IN expressions: check if item is in a SEQUENCE OF '''

    # Check if item is in a SEQUENCE OF
    global VAR_COUNTER
    VAR_COUNTER = VAR_COUNTER + 1

    string = ''
    stmts, decls = [], []
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)

    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    decls.extend(left_local)
    decls.extend(right_local)

    left_type = find_basic_type(expr.left.exprType)

    # it is possible to test against a raw sequence of: x in { 1,2,3 }
    # in that case we create an array on the type of x, and we test
    # presence using a loop
    if isinstance(expr.left, ogAST.PrimSequenceOf):
        sort = type_name(expr.right.exprType)
        size = expr.left.exprType.Max
        string = f'tmp{VAR_COUNTER}'   # Result of the test
        decls.append(f'_Bool {string} = false;')

        decls.append(f'{sort} tmp{expr.tmpVar}[{size}] = {{{left_str}}};')
        stmts.extend([
            f'for (int i=0; i<{size}; i++)',
             '{',
            #f'//if ({right_str} == tmp{expr.tmpVar}[i])', Can't work with structs
            f'if ({sort}_Equal (&{right_str}, &tmp{expr.tmpVar}[i]))',
             '{',
            f'{string} = true;',
             'break;',
             '}',
             '}'
        ])
    else:
        string = f'tmp{expr.tmpVar}'
        decls.append(f'_Bool {string} = false;')
        if isinstance(expr.left, ogAST.PrimSubstring):
            len_str = f"{left_str}'Length"  # XXX UNTESTED TERRITORY
            #raise NotImplementedError('Looking for substring in string')
        else:
            len_str = f'{left_str}.nCount'
            left_str += '.arr'

        if left_type.Min != left_type.Max:
            decls.append(u'int for_{var_counter};'.format(var_counter=VAR_COUNTER))
            stmts.append(u'for(for_{var_counter} = 0; for_{var_counter} < {ls}; for_{var_counter}++)'.format(var_counter=VAR_COUNTER, ls=len_str))
        else:
            decls.append(u'asn1SccUint for_{var_counter};'.format(var_counter=VAR_COUNTER))
            stmts.append(u'for(for_{var_counter} = 0; for_{var_counter} < {ls}; for_{var_counter}++)'.format(var_counter=VAR_COUNTER, ls=left_type.Max))

        stmts.append(u'{')

        if isinstance(expr.left, ogAST.PrimSubstring):
            stmts.append(u'if ({container}.arr[for_{var_counter}] == {pattern})'.format(container=left_str, pattern=right_str, var_counter=VAR_COUNTER))
        else:
            stmts.append(u'if ({container}[for_{var_counter}] == {pattern})'.format(container=left_str, pattern=right_str, var_counter=VAR_COUNTER))

        stmts.append(u'{')
        stmts.append(u'{} = true;'.format(string))
        stmts.append(u'break;')
        stmts.append(u'}')
        stmts.append(u'}')

    return stmts, str(string), decls


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''

    basic_type = find_basic_type(primary.exprType)
    enumerant_raw = primary.value[0].replace('_', '-').lower()

    for enumerant in basic_type.EnumValues.keys():
        if enumerant.lower() == enumerant_raw:
            enumID = basic_type.EnumValues[enumerant].EnumID

    if enumID.endswith("_PRESENT"): # choice
        return [], enumID, []
    else:
        prefix = type_name(basic_type, use_prefix=True)
        enumName = basic_type.CName

        value = ''
        if enumID.startswith(enumName):
            value = prefix + enumID
        else:
            value = prefix + enumName + '_' + enumID

        return [], value, []


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''

    enumerant = primary.value[0].replace('_', '-').lower()

    for each in primary.exprType.EnumValues:
        if each.lower() == enumerant:
            break

    string = primary.exprType.EnumValues[each].EnumID

    return [], str(string), []


@expression.register(ogAST.PrimInteger)
@expression.register(ogAST.PrimReal)
def _integer(primary):
    ''' Generate code for a raw numerical value  '''

    string = primary.value[0]
    return [], str(string), []


@expression.register(ogAST.PrimBoolean)
def _boolean(primary):
    ''' Generate code for a raw boolean value  '''

    string = primary.value[0]
    return [], str(string.lower()), []


@expression.register(ogAST.PrimNull)
def _null(primary, **kwargs):
    ''' Generate code for a raw null value  '''

    string = '0'
    return [], string, []


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''

    typename = type_name(primary.exprType)

    string = f'{typename}_constant'
    return [], string, []


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    
    # If user put a literal string to fill an Octet string,
    # then convert the string to an array of unsigned_8 integers
    # as expected by the Ada type corresponding to Octet String
    if isinstance(primary, ogAST.PrimOctetStringLiteral):
        # Hex string used as input
        unsigned_8 = [str(x) for x in primary.hexstring]
    else:
        unsigned_8 = [str(ord(val)) for val in primary.value[1:-1]]

    string = ', '.join(unsigned_8)
    return [], string, []


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''

    return [], str(primary.constant_c_name), []


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''

    error = 'To Be Implemented'
    LOG.error(error)
    raise TypeError(error)
    return [], '', []


@expression.register(ogAST.PrimConditional)
def _conditional(cond):
    ''' Return string and statements for conditional expressions '''
    # FIXME: this function is not fully aligned with Ada, many cases are missing

    stmts = []
    tmp_type = type_name(cond.exprType)
    local_decl = ['{tmpType} tmp{idx};'.format(idx=cond.value['tmpVar'], tmpType=tmp_type)]
    if_stmts, if_str, if_local = expression(cond.value['if'])

    stmts.extend(if_stmts)
    local_decl.extend(if_local)

    then_stmts, then_str, then_local = expression(cond.value['then'])
    else_stmts, else_str, else_local = expression(cond.value['else'])

    stmts.extend(then_stmts)
    stmts.extend(else_stmts)

    local_decl.extend(then_local)
    local_decl.extend(else_local)

    if isinstance(cond.value['then'], (ogAST.PrimStringLiteral, ogAST.PrimSequenceOf)):
        then_str = u'({tmpTyp}) {{{size}, {{{then_str}}}}}'.format(tmpTyp=tmp_type, then_str=then_str, size=len((cond.value['then'].value))-2)
    
    if isinstance(cond.value['else'], (ogAST.PrimStringLiteral, ogAST.PrimSequenceOf)):
        else_str = u'({tmpTyp}) {{{size}, {{{else_str}}}}}'.format(tmpTyp=tmp_type, else_str=else_str, size=len((cond.value['else'].value))-2)

    stmts.append('if ({if_str})'.format(if_str=if_str))
    stmts.append('{')
    # the following has to check if the expression is an Append or a Substring and generate the proper code.
    # see the Ada backend to complete.
    if isinstance(cond.value['then'], ogAST.PrimSubstring):
       # assign the substring elements to the temporary storage
       stmts.extend([
           f'for(int var_counter_{VAR_COUNTER} = 0; var_counter_{VAR_COUNTER} <= max_range_{VAR_COUNTER} - min_range_{VAR_COUNTER}; var_counter_{VAR_COUNTER}++)',
           '{',
           f"tmp{cond.value['tmpVar']}.arr[var_counter_{VAR_COUNTER}] = {then_str}.arr[var_counter_{VAR_COUNTER} + min_range_{VAR_COUNTER}];", 
           '}'
           ])
       rlen = f'max_range_{VAR_COUNTER} - min_range_{VAR_COUNTER} + 1'
       basic = find_basic_type(cond.exprType)
       if basic.Min != basic.Max:
           stmts.append(f"tmp{cond.value['tmpVar']}.nCount = {rlen};")
    else:
       stmts.append('tmp{idx} = ({ty}) {then_str};'.format(ty=tmp_type, idx=cond.value['tmpVar'], then_str=then_str))
    stmts.append('}')
    stmts.append('else')
    stmts.append('{')
    if isinstance(cond.value['else'], ogAST.PrimSubstring):
       # assign the substring elements to the temporary storage
       stmts.extend([
           f'for(int var_counter_{VAR_COUNTER} = 0; var_counter_{VAR_COUNTER} <= max_range_{VAR_COUNTER} - min_range_{VAR_COUNTER}; var_counter_{VAR_COUNTER}++)',
           '{',
           f"tmp{cond.value['tmpVar']}.arr[var_counter_{VAR_COUNTER}] = {else_str}.arr[var_counter_{VAR_COUNTER} + min_range_{VAR_COUNTER}];",
           '}'
           ])
       rlen = f'max_range_{VAR_COUNTER} - min_range_{VAR_COUNTER} + 1'
       basic = find_basic_type(cond.exprType)
       if basic.Min != basic.Max:
           stmts.append(f"tmp{cond.value['tmpVar']}.nCount = {rlen};")
    else:
        stmts.append('tmp{idx} = ({ty}) {else_str};'.format(ty=tmp_type, idx=cond.value['tmpVar'], else_str=else_str))
    stmts.append('}')

    string = u'tmp{idx}'.format(idx=cond.value['tmpVar'])

    return stmts, str(string), local_decl


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Return C string for an ASN.1 SEQUENCE '''

    stmts, local_decl = [], []
    #string = u"({}) {{".format(type_name(seq.exprType))
    string = "{"
    sep = ''
    type_children = find_basic_type(seq.exprType).Children
    optional_fields = {field.lower().replace('-', '_'): {'present': False,'ref': (field, val)} for field, val in type_children.items() if val.Optional == 'True'}
    absent_fields = []

    for elem, value in seq.value.items():
        # Set the type of the field - easy thanks to ASN.1 flattened AST
        delem = elem.replace('_', '-')
        found = False

        for each in type_children:
            if each.lower() == delem.lower():
                elem_spec = type_children[each]
                found = True
                break

        # try to use original children selector since elem is always lowercase
        elem_name = each.replace('-', '_') if found else elem

        elem_specty = elem_spec.type
        elem_bty = find_basic_type(elem_specty)

        value_stmts, value_str, local_var = expression(value)

        if isinstance(value, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            if elem_bty.kind.startswith('Integer'):
                value_str = str(value.numeric_value)
            else:
                value_str = array_content(value, value_str, elem_bty)

        string += u"{}.{} = {}".format(sep, elem_name, value_str)

        if elem.lower() in optional_fields:
            # Set optional field presence
            optional_fields[elem.lower()]['present'] = True

        sep = u', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    
    # Process optional fields
    if optional_fields:
        absent_fields = ((fd_name, fd_data['ref']) for fd_name, fd_data in optional_fields.items() if not fd_data['present'])

        for fd_name, fd_data in absent_fields:
            fd_type = fd_data[1].type

            if fd_type.kind == 'ReferenceType':
                typename = type_name(fd_type)

                value = f'{typename}_constant'
            elif fd_type.kind == 'BooleanType':
                value = u'false'
            elif fd_type in ('IntegerType', 'RealType'):
                value = fd_type.Min

            string += u'{}.{} = {}'.format(sep, fd_name.lower(), value)
            sep = u', '

        string += u', .exist = {'
        sep = ''

        for fd_name, fd_data in optional_fields.items():
            string += u'{} {}'.format(sep, '1' if fd_data['present'] else '0')
            sep = u', '
        
        string += u'}'

    string += '}'

    return stmts, str(string), local_decl


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Return C string for an ASN.1 SEQUENCE OF '''

    stmts, local_decl, tab = [], [], []
    seqof_ty = seqof.exprType

    try:
        asn_type = find_basic_type(TYPES[seqof_ty.ReferencedTypeName].type)
    except AttributeError:
        asn_type = None

        if hasattr(seqof, 'expected_type'):
            sortref = TYPES[seqof.expected_type.ReferencedTypeName]

            while(hasattr(sortref, "type")):
                sortref = sortref.type
                
            asn_type = find_basic_type(sortref)

    for i in range(len(seqof.value)):
        temp = ''
        item_stmts, item_str, local_var = expression(seqof.value[i])

        if isinstance(seqof.value[i], (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            item_str = array_content(seqof.value[i], item_str, asn_type or find_basic_type(seqof.value[i].exprType))

        temp += item_str

        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        tab.append(temp)

    string = u', '.join(tab)
    return stmts, str(string), local_decl


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Return the c code for a CHOICE expression '''

    stmts, choice_str, local_decl = expression(choice.value['value'])
    bty = find_basic_type(choice.value['value'].exprType)

    if isinstance(choice.value['value'], (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
        if bty.kind.startswith('Integer'):
            choice_str = choice.value['value'].numeric_value
        else:
            choice_str = array_content(choice.value['value'], choice_str, bty)

    # look for the right spelling of the choice discriminant
    # (normally field_PRESENT, but can be prefixed by the type name if there
    # is a namespace conflict)
    basic = find_basic_type(choice.exprType)
    prefix = 'CHOICE_NOT_FOUND'
    search = choice.value['choice'].lower().replace('-', '_')
    opt = ''

    for each in basic.Children:
        curr_choice = each.lower().replace('-', '_')
        if curr_choice == search:
            opt = each.replace('-', '_')
            prefix = basic.Children[each].EnumID
            break

    #string = f'({type_name(choice.exprType)}) {{ .kind = {prefix}, .u.{opt} = {choice_str} }}'
    string = f'{{ .kind = {prefix}, .u.{opt} = {choice_str} }}'
    return stmts, string, local_decl


@expression.register(ogAST.PrimSubstring)
def _prim_substring(prim):
    ''' Generate expression for SEQOF/OCT.STRING substrings, e.g. foo(1,2) '''

    stmts, string, local_decl = [], '', []
    receiver = prim.value[0]

    receiver_stms, receiver_string, receiver_decl = expression(receiver)
    string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    r1_stmts, r1_string, r1_local = expression(prim.value[1]['substring'][0])
    r2_stmts, r2_string, r2_local = expression(prim.value[1]['substring'][1])

    global VAR_COUNTER
    VAR_COUNTER = VAR_COUNTER + 1

    stmts.extend(r1_stmts)
    stmts.append(f'min_range_{VAR_COUNTER} = {r1_string};')
    stmts.extend(r2_stmts)
    stmts.append(f'max_range_{VAR_COUNTER} = {r2_string};')

    local_decl.extend(r1_local)
    local_decl.append(f'asn1SccUint min_range_{VAR_COUNTER};')
    local_decl.extend(r2_local)
    local_decl.append(f'asn1SccUint max_range_{VAR_COUNTER};')

    return stmts, str(string), local_decl

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Utility Functions

def generate_header_file_include_guard(process):
    process_name = process.processName.upper()

    beginning_of_include_guard_header_file_code = []
    beginning_of_include_guard_header_file_code.append(f'#ifndef {process_name}_PROCESS_INCLUDE_GUARD_H')
    beginning_of_include_guard_header_file_code.append(f'#define {process_name}_PROCESS_INCLUDE_GUARD_H')
    beginning_of_include_guard_header_file_code.append(u'\n')

    ending_of_include_guard_header_file_code = []
    ending_of_include_guard_header_file_code.append(u'\n')
    ending_of_include_guard_header_file_code.append(f'#endif /* {process_name}_PROCESS_INCLUDE_GUARD_H */')

    return beginning_of_include_guard_header_file_code, ending_of_include_guard_header_file_code


def generate_sdl_constants(process):
    sdl_constants_code = ['//// SDL Constants']

    # First add SDL constants (synonyms) - they can be used in the context
    for sdl_constant in process.DV.SDL_Constants.values():
        sdl_constant_basic_type = find_basic_type(sdl_constant.type)

        if sdl_constant_basic_type.kind in ('IntegerType', 'RealType', 'NullType', 'BooleanType', 'Integer32Type', 'IntegerU8Type'):
            val = sdl_constant.value
            if isinstance(val, ogAST.PrimSelector):
                # synonym may reference a field of an ASN.1 constant
                _, val, _ = expression(sdl_constant.value)
        else:
            # complex value - must be a ground expression
            _, val, _ = expression(sdl_constant.value)
            if sdl_constant_basic_type.kind in('SequenceOfType', 'OctetStringType', 'BitStringType'):
                val = array_content(sdl_constant.value, val, sdl_constant_basic_type)
            elif sdl_constant_basic_type.kind == 'NullType':
                val = '0'
            elif sdl_constant_basic_type.kind not in ("EnumeratedType", "SequenceType"):
                # should have been detected by ogParser
                raise TypeError(f'Constant "{sdl_constant.varName}" value is not a ground expression')

        data_type = sdl_constant.type.ReferencedTypeName.replace('-', '_')
        # Don't generate the "self" constant if the process is a process type
        # as it is provided as a generic parameter during instantiation
        if process.process_type and sdl_constant.varName == 'self' and 'PID' in TYPES:
            pass
        else:
            sdl_constants_code.append(f"static const {ASN1SCC}{data_type} {sdl_constant.varName} = {val};")

    sdl_constants_code.append('\n')

    return sdl_constants_code


def processing_process_aliases(process, no_renames):
    aliases_code = ['//// Aliases']

    # Add aliases
    for alias_name, (alias_sort, alias_expr) in process.aliases.items():
        if alias_name in no_renames:
            continue

        _, qualified, _ = expression(alias_expr)

        #aliases_code.append(f'{type_name(alias_sort)} {alias_name};')
        aliases_code.append(f'#define {alias_name} {qualified}')

    aliases_code.append('\n')

    return aliases_code


def generating_context(process):
    context_code = ['//// Context']
    #context_code.append(f'__attribute__ ((persistent)) {ASN1SCC}{process.processName.capitalize()}_Context {LPREFIX} = {{0}};\n')
    context_code.append(f'static {ASN1SCC}{process.processName.capitalize()}_Context {LPREFIX} = {{0}};\n')

    return context_code

def generating_aggregate_start_funtions(process):
   aggreg_start_proc = ['//// State Aggregations Start functions']
   # Declare start procedure for aggregate states
   # should create one START per "via" clause, TODO later
   for name, substates in process.aggregates.items():
       proc_name = f'void {name}{SEPARATOR}START(void)'
       aggreg_start_proc.extend([f'{proc_name}',
                                 '{'])
       aggreg_start_proc.extend(f'runTransition{process.processName} ({subname.statename}{SEPARATOR}START);'
                                for subname in substates)
       aggreg_start_proc.extend(['}',
                                '\n'])

   return aggreg_start_proc


def generating_startup_function(process, no_renames):
    startup_header_file_code = [u'//// Startup']

    generic = process.instance_of_name

    if not generic:
        startup_header_file_code.append(u'void {}_startup();'.format(process.processName.lower()))

    startup_header_file_code.append(u'\n')

    # Generate the code of the start transition (if process not empty)
    startup_function_code = ['//// Startup']
    startup_function_code.append(f'void CInit{process.processName.lower()}()')
    startup_function_code.append('{')

    processing_process_variables(process, no_renames, startup_function_code)

    if process.transitions:
        startup_function_code.append('\n')
        startup_function_code.append(f'runTransition{process.processName}(0);')

    startup_function_code.append(f'{LPREFIX}.init_done = true;')
    startup_function_code.append('}\n')

    startup_function_code.append('// Required To Work With TASTE\'s Wrappers')
    startup_function_code.append(f'void {process.processName.lower()}_startup()')
    startup_function_code.append('{')
    startup_function_code.append(f'CInit{process.processName.lower()}();')
    startup_function_code.append('}\n')

    return startup_header_file_code, startup_function_code


def generating_run_transition_declaration(process):
    run_transition_declaration_code = [f'#define CS_Only {len(process.transitions)}']

    if process.transitions:
        run_transition_declaration_code.append(u'void runTransition{}(int Id);\n'.format(process.processName))

    return run_transition_declaration_code


def generating_nested_states(process):
    nested_states_code = [u'//// Nested States']

    for name, val in process.mapping.items():
        if name.endswith('START') and name != 'START' and val:
            nested_states_code.append(f'#define {name} {str(val)}')

    nested_states_code.append(u'\n')

    return nested_states_code


def processing_process_variables(process, no_renames, startup_function_code):
    for var_name, (var_type, init) in process.variables.items():
        LOG.debug(var_name)

        if var_name not in no_renames:
            content = (var_type, init)

            if var_name in process.aliases.keys():
                LOCAL_VARIABLES[var_name] = content
            else:
                VARIABLES[var_name] = content

        if var_name in process.aliases.keys():
            # aliases are not part of the context
            continue

        if init:
            init_stmt, init_string, init_decl = expression(init)
            basic_type_of_var_type = find_basic_type(var_type)

            if basic_type_of_var_type.kind == 'IntegerType' and isinstance(init, (ogAST.PrimOctetStringLiteral, ogAST.PrimBitStringLiteral)):
                startup_function_code.append(u'{ct}.{field} = {init_val};'.format(ct=LPREFIX, field=var_name, init_val=init.numeric_value))
            elif basic_type_of_var_type.kind in ('SequenceOfType', 'OctetStringType', 'BitStringType') and init.is_raw:
                init_val = array_content(init, init_string, basic_type_of_var_type)
                startup_function_code.append(u'{ct}.{field} = ({type}) {init_val};'.format(ct=LPREFIX, field=var_name, type=type_name(var_type), init_val=init_val))
            elif basic_type_of_var_type.kind == 'IA5StringType' and isinstance(init, ogAST.PrimStringLiteral):
                init_val = array_content(init, init_string, basic_type_of_var_type)

                startup_function_code.append(u'{')
                startup_function_code.append(u'{type} {field}_val = {init_val};'.format(type=type_name(var_type), field=var_name, init_val=init_val))
                startup_function_code.append(u'asn1SccUint {field}_memcpy;\n'.format(field=var_name))
                startup_function_code.append(u'{type}_Initialize({ct}.{field});'.format(ct=LPREFIX, type=type_name(var_type), field=var_name))
                startup_function_code.append(u'for({field}_memcpy = 0; {field}_memcpy < {len}; {field}_memcpy++)'.format(field=var_name, len=(len(init.value) - 2)))
                startup_function_code.append(u'{')
                startup_function_code.append(u'{ct}.{field}[{field}_memcpy] = {field}_val[{field}_memcpy];'.format(ct=LPREFIX, field=var_name))
                startup_function_code.append(u'}')
                startup_function_code.append(u'}')
            else:
                if basic_type_of_var_type.kind in ('SequenceType', 'ChoiceType'):
                    init_string = '({type}) {init}'.format(type=type_name(var_type), init=init_string)

                startup_function_code.append('{ct}.{field} = {init};'.format(ct=LPREFIX, field=var_name, init=init_string))

            assert not init_stmt, 'Initialization of ' + var_name + ' requires to add statement'
            assert not init_decl, 'Initialization of ' + var_name + ' requires to add declarations'
    

def processing_inner_procedures(process):
    inner_procedures_header_file_code = [u'//// Declaration Of Exported Inner Procedures']
    inner_procedures_declarations_code = [u'//// Declaration Of Inner Procedures']
    inner_procedures_code = [u'//// Definition Of Inner Procedures']

    generic = process.instance_of_name

    for procedure in process.content.inner_procedures:
        not_local = False
        spelling = procedure.inputString
        for procedure_definition in process.procedures:
            if procedure_definition.inputString.lower() == procedure.inputString.lower() and procedure_definition.referenced:
                spelling = procedure_definition.inputString
                not_local = True

        proc_code, proc_declaration = generate(procedure, is_rpc=not_local)
        inner_procedures_declarations_code.extend(proc_declaration)
        inner_procedures_code.extend(proc_code)

        if procedure.exported:
            if not procedure.external and not generic:
                if not_local:
                    return_type = type_name(procedure.return_type) if procedure.return_type else None
                    return_type = 'void' if not return_type else return_type

                    declaration_args, invoke_args = procedure_args(procedure)
                    procedure_declaration = f'{return_type} {PROCESS_NAME.lower()}_PI_{spelling}({declaration_args})'
                    inner_procedures_header_file_code.append(f'{procedure_declaration};')

                    if spelling != procedure.inputString.lower():
                        invoked_procedure_name = f'{PROCESS_NAME.lower()}_PI_{procedure.inputString.lower()}'

                        inner_procedures_code.append(u'// Required To Work With TASTE\'s Wrappers')
                        inner_procedures_code.append(procedure_declaration)
                        inner_procedures_code.append(u'{')
                        inner_procedures_code.append(f'{invoked_procedure_name}({invoke_args});')
                        inner_procedures_code.append(u'}\n')

    inner_procedures_header_file_code.append(u'\n')
    inner_procedures_declarations_code.append(u'\n')
    inner_procedures_code.append(u'\n')

    return inner_procedures_header_file_code, inner_procedures_declarations_code, inner_procedures_code


def processing_input_signals(process):
    input_signals_header_file_code = ['//// Input Signals\n']
    input_signals_code = ['//// Input Signals']
    
    reduced_statelist = {s for s in process.full_statelist
            if s not in process.parallel_states}

    for signal in process.input_signals + [{'name': timer} for timer in process.timers]:
        signame = signal.get('name', 'START')

        if signame == 'START':
            continue

        fake_name = False

        # Check if there is an exported procedure with the name of the signal
        ignore_export = False
        for proc in process.procedures:
            if proc.inputString.lower() == signame.lower():
                ignore_export = True

        if ignore_export:
            # this signal corresponds to the transitions triggered after
            # exported procedures have been executed (synchronous PIs, or RPS)
            # therefore it is renamed as it is not a regular PI
            fake_name = f'{PROCESS_NAME.lower()}_{signame.lower()}_transition'

        pn = process.processName
        pn = pn.lower()
        sig_name = signal['name']
        name = fake_name or f'{pn}_PI_{sig_name}'
        pi_header = f'void {name}'

        param_name = signal.get('param_name') or '{}_param'.format(signal['name'])
        # Add (optional) PI parameter (only one is possible in TASTE PI)
        if 'type' in signal:
            typename = type_name(signal['type'])
            pi_header += '({tn} * {pn})'.format(tn=typename, pn=param_name)
        else:
            pi_header += '()'

        # Add declaration of the provided interface in the .h file
        input_signals_header_file_code.append('// Provided interface "' + signal['name'] + '"')
        input_signals_header_file_code.append(pi_header + ';\n')

        input_signals_code.append(pi_header)
        input_signals_code.append('{')
        input_signals_code.append(f'switch({LPREFIX}.state)')
        input_signals_code.append('{')

        def execute_transition(state, dest=[]):
            ''' Aligned with Ada
                Generate the code that triggers the transition for the current
                state/input combination '''
            input_def = process.input_mapping[signame].get(state)
            # Check for nested states to call optional exit procedures
            # (we may exit from more than one state, the exit procedures must
            #  be called in the right order)
            state_tree = state.split(SEPARATOR)
            context = process
            exitlist = []
            current = ''
            trans = input_def and process.transitions[input_def.transition_id]
            while state_tree:
                current = current + state_tree.pop(0)
                for comp in context.composite_states:
                    if current.lower() == comp.statename.lower():
                        if comp.exit_procedure:
                            exitlist.append(current)
                        context = comp
                        current = current + SEPARATOR
                        break
            for each in reversed(exitlist):
                # Here we add a call to the exit procedure of nested states
                # when we exit the state due to a transition in the superstate
                # not due to a return statement from within the substate
                # this other case is handled in Helper.py when flattening
                # the model.
                # The exit here is added only for transitions triggered by an
                # INPUT. The continuous signals are not processed here
                if trans and all(each.startswith(trans_st)
                                 for trans_st in trans.possible_states):
                    dest.append(f'{SEPARATOR}{process.processName}_{each}{SEPARATOR}exit();')

            if input_def:
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    dest.append(f'{LPREFIX}.{inp} = *{param_name};')
                # Execute the corresponding transition
                if input_def.transition:
                    dest.append(f'runTransition{process.processName}({input_def.transition_id});')
                    dest.append('break;')
                    dest.append('}')
                else:
                    dest.append('break;')
                    dest.append('}')
                    return False
            else:
                dest.append('break;')
                dest.append('}')
                return False
            return True

        def case_state(state):
            ''' Aligned with Ada
                Recursive function (in case of state aggregation) to generate
                the code that calls the proper transition according
                to the current state
                The input name is in signame
            '''
            if state.endswith('START'):
                return
            statecase = [f'case {generate_state_name(state)}:', '{']
            input_def = process.input_mapping[signal['name']].get(state)
            if state in process.aggregates.keys():
                input_signals_code.extend(statecase)
                # State aggregation:
                # - find which substate manages this input
                # - add a switch case on the corresponding substate
                input_signals_code.append('//  This is a state aggregation')
                for sub in process.aggregates[state]:
                    if [a for a in sub.mapping.keys()
                            if a in process.input_mapping[signame].keys()]:
                        input_signals_code.append(f'switch ({LPREFIX}.{sub.statename}{SEPARATOR}state)')
                        input_signals_code.append('{')
                        for par in sub.mapping.keys():
                            case_state(par)
                        input_signals_code.append('default:')
                        input_signals_code.append(f'runTransition{process.processName}(CS_Only);')
                        input_signals_code.append('}')
                        break
                else:
                    # Input is not managed in the state aggregation
                    if input_def:
                        # check if it is managed one level above
                        execute_transition(state, input_signals_code)
                    else:
                        input_signals_code.append(f'runTransition{process.processName}(CS_Only);')
            else:
                if execute_transition(state, statecase):
                    input_signals_code.extend(statecase)

        for each_state in reduced_statelist:
            case_state(each_state)

        input_signals_code.append('default:')
        input_signals_code.append('{')
        input_signals_code.append(f'runTransition{process.processName}(CS_Only);')
        input_signals_code.append('break;')
        input_signals_code.append('}')
        input_signals_code.append('}')
        input_signals_code.append('}')

    input_signals_code.append('\n\n')

    return input_signals_header_file_code, input_signals_code


def processing_output_signals(process):
    output_signals_header_file_code = [u'//// Output Signals\n']
    output_signals_code = [u'//// Output Signals\n']

    process_name = process.processName

    for signal in process.output_signals:
        param_name = signal.get('param_name') or u'{}_param'.format(signal['name'])
        # Add (optional) RI parameter
        param_spec = ''

        if 'type' in signal:
            typename = type_name(signal['type'])
            param_spec = u'({sort} * {pName})'.format(pName=param_name, sort=typename)
        else:
            param_spec = u'()'

        output_signals_code.append(u'// Required interface "' + signal['name'] + '"')

        # Edit (MP) remove the #define for RIs, it makes no sense and cause compilation errors
        #output_signals_code.append('#define {} {}_RI_{}'.format(signal['name'], process_name.lower(), signal['name']))
        output_signals_header_file_code.append('// Output signal "' + signal['name'])
        output_signals_header_file_code.append('void {}_RI_{}{};\n'.format(process_name.lower(), signal['name'], param_spec))

    return output_signals_header_file_code, output_signals_code


def processing_external_procedures(process, output_signals_code):
    process_name = process.processName
    external_procedures_header_file_code = ['//// External Procedures\n']

    # for the .h file, generate the declaration of the external procedures
    for proc in (proc for proc in process.procedures if proc.external):
        ri_header = 'void {pn}_RI_{sig_name}'.format(sig_name=proc.inputString, pn=process_name.lower())
        params = []

        for param in proc.fpar:
            typename = type_name(param['type'])
            params.append(u'{ty} * {par}'.format(par=param['name'], ty=typename))

        if params:
            ri_header += u'(' + u','.join(params) + ')'
        else:
            ri_header += u'()'

        external_procedures_header_file_code.append('// Sync Required Interface "' + proc.inputString)
        external_procedures_header_file_code.append(ri_header + u';\n')

        # Edit (MP) remove the #defines for RI to avoid compilation issues
        #external_procedures_header_file_code.append('#define {sig_name} {pn}_RI_{sig_name}'
        #                           .format(sig_name=proc.inputString, pn=process_name.lower()))

    return external_procedures_header_file_code


def processing_timers(process, output_signals_code):
    process_name = process.processName

    timers_header_file_code = ['//// Timers\n']

    # for the .h file, generate the declaration of timers set/reset functions
    for timer in process.timers:
        timers_header_file_code.append(u'// Timer {} SET and RESET functions'.format(timer))

        timers_header_file_code.append(f'void {process_name.lower()}_RI_SET_{timer}(const {ASN1SCC}T_UInt32 * val);')
        timers_header_file_code.append(f'void {process_name.lower()}_RI_RESET_{timer}();')

        output_signals_code.append('#define SET_{timer} {pn}_RI_SET_{timer}'.format(timer=timer, pn=process_name.lower()))
        output_signals_code.append('#define RESET_{timer} {pn}_RI_RESET_{timer}'.format(timer=timer, pn=process_name.lower()))

    return timers_header_file_code


def generating_current_state_to_str(process):
    # Generate code returning the current state as a string (used by tracer)

    process_name = process.processName
    return ['//// Current State To String',
            f'char* {process_name.lower()}_state(void)',
             '{',
             '  return "Not_supported_in_C__Use_the_Ada_backend";',
             '}']


def generating_includes(process):
    includes_code = [u'//// Includes']

    if MATH_INCLUDE == True:
        includes_code.append(u'#include <math.h>')

    if STDIO_INCLUDE == True:
        includes_code.append(u'#include <stdio.h>')

    if STRING_INCLUDE == True:
        includes_code.append(u'#include <string.h>')

    for each in process.DV.asn1Files:
        hname = os.extsep.join(each.split(os.extsep)[:-1]) + os.extsep + 'h'
        includes_code.append(f'#include "{hname.split(os.sep)[-1]}"')

    includes_code.append(f'#include \"{process.name.lower()}_datamodel.h\"')
    includes_code.append(f'#include \"{process.processName.lower()}.h\"\n')

    return includes_code


def processing_transitions_and_floating_labels(process):
    continuous_signals_header_file_code = [u'//// Continuous Signals']
    transition_code = [u'//// Definition Of Run Transition']

    has_continuous_signals = any(process.cs_mapping.values())

    code_transitions = []
    decl_transitions = []
    code_labels = []

    for transition in process.transitions:
        transition_stmts, transition_decls = generate(transition)
        code_transitions.append(transition_stmts)
        decl_transitions.extend(transition_decls)

    # Generate code for the floating labels
    for label in process.content.floating_labels:
        code_label, label_decl = generate(label)
        decl_transitions.extend(label_decl)
        code_labels.extend(code_label)

    # Generate the code of the runTransition procedure, if needed
    if process.transitions:
        transition_code.append('void runTransition{}(int Id)'.format(process.processName))
        transition_code.append('{')
        transition_code.append('int trId = Id;')

        if has_continuous_signals:
            transition_code.append('flag message_pending = true;')

        # Declare the local variables needed by the transitions in the template
        transition_code.extend(set(decl_transitions))

        # Generate a loop that ends when a next state is reached
        # (there can be chained transition when entering a nested state)
        transition_code.append('while (trId != -1)')
        transition_code.append('{')

        # Generate the switch-case on the transition id
        transition_code.append('switch(trId)')
        transition_code.append('{')

        for idx, val in enumerate(code_transitions):
            transition_code.append('case {idx}:'.format(idx=idx))
            transition_code.append('{')
            val = ['{line}'.format(line=l) for l in val]

            if val:
                transition_code.extend(val)

            transition_code.append('break;')
            transition_code.append('}')

        transition_code.append('case CS_Only:')
        transition_code.append('{')
        transition_code.append('trId = -1;')
        transition_code.append('goto continuous_signals;')
        transition_code.append('}')
        transition_code.append('default:')
        transition_code.append('{')
        transition_code.append('break;')
        transition_code.append('}')
        transition_code.append('}')

        if code_labels:
            # Due to nested states (chained transitions) jump over label code
            # (NEXTSTATEs do not return from runTransition)
            transition_code.append('goto continuous_signals;')

        # Add the code for the floating labels
        transition_code.extend(code_labels)

        transition_code.append('continuous_signals:\n')

        # After completing active transition(s), check continuous signals:
        #     - Check current state(s)
        #     - For each continuous signal generate code (test+transition)
        if has_continuous_signals:
            if not MONITORS:
                continuous_signals_header_file_code.append(f'void {process.processName.lower()}_check_queue(bool* has_pending_msg);')

                transition_code.append('// Process Continuous Signals')
                transition_code.append(f'if({LPREFIX}.init_done)')
                transition_code.append(u'{')
                transition_code.append(f'{process.processName.lower()}_check_queue(&message_pending);')
                transition_code.append(u'}\n')
            else:
                transition_code.append('// Process Observer Transitions')
                transition_code.append("message_pending = false;\n")
                
        if has_continuous_signals:
            transition_code.append(u'if(message_pending || trId != -1)')
            transition_code.append(u'{')
            transition_code.append(u'goto next_transition;')
            transition_code.append(u'}\n')

        # Process the continuous signals in state aggregations first
        # (reminder: state aggregations = parallel states)
        done = []
        sep = 'if('
        last = ''

        # flag indicating there are CS in nested states but not at root
        need_final_endif = False
        first_of_aggreg = True
        for cs, agg in product(process.cs_mapping.items(), process.aggregates.items()):
            (statename, cs_item)  = cs
            (agg_name, substates) = agg

            if not cs_item:
                continue

            for each in substates:
                if statename in each.cs_mapping and each.cs_mapping[statename]:
                    if first_of_aggreg:
                        transition_code.append(f'if({LPREFIX}.state == {generate_state_name(agg_name)})')
                        transition_code.append('{')
                        first_of_aggreg = False

                    need_final_endif = True
                    first = "} else" if done else ""
                    transition_code.append(f'if({LPREFIX}.{each.statename}{SEPARATOR}state == {generate_state_name(statename)})')
                    transition_code.append('{')

                    # Change priority 0 (no priority set) to lowest priority
                    lowest_priority = max(item.priority for item in cs_item)
                    for each in cs_item:
                        if each.priority == 0:
                            each.priority = lowest_priority + 1

                    for provided_clause in sorted(cs_item, key=lambda itm: itm.priority):
                        transition_code.append(f'// Priority {provided_clause.priority}')
                        trId = process.transitions.index(provided_clause.transition)
                        code, loc = generate(provided_clause.trigger,
                                            branch_to=trId,
                                            sep=sep, last=last)
                        code.append('goto next_transition;')
                        sep='} else if('
                        transition_code.extend(code)

                    done.append(statename)
                    transition_code.append('}')  # inner if
                    transition_code.append('}')  # substate if
                    sep = 'if('
                    break

        count = 0
        for statename in process.cs_mapping.keys() - done:
            cs_item = process.cs_mapping[statename]

            if cs_item:
                count += 1 
                need_final_endif = False
                first = "} else " if done else ""
                transition_code.append(f'{first}if({LPREFIX}.state == {generate_state_name(statename)})')
                transition_code.append(u'{')

            # Change priority 0 (no priority set) to lowest priority
            if cs_item:
                lowest_priority = max(item.priority for item in cs_item)

            for each in cs_item:
                if each.priority == 0:
                    each.priority = lowest_priority + 1

            for provided_clause in sorted(cs_item, key=lambda itm: itm.priority):
                transition_code.append(f'// Priority: {provided_clause.priority}')
                trId = process.transitions.index(provided_clause.transition)

                # check if we are leaving a nested state with a CS
                state_tree = statename.split(SEPARATOR)
                context = process
                exitlist, exitcalls = [], []
                current = ''

                while state_tree:
                    current = current + state_tree.pop(0)

                    for comp in context.composite_states:
                        if current.lower() == comp.statename.lower():
                            if comp.exit_procedure:
                                exitlist.append(current)

                            context = comp
                            current = current + SEPARATOR
                            break

                trans = process.transitions[trId]
                for each in reversed (exitlist):
                    if trans and all(each.startswith(trans_st)
                            for trans_st in trans.possible_states):
                        exitcalls.append(f"p{SEPARATOR}{each}{SEPARATOR}exit();") # should be tested and fixed

                code, loc = generate(provided_clause.trigger,
                                     branch_to=trId, sep=sep, last=last,
                                     exitcalls=exitcalls)
                sep='} else if('
                transition_code.extend(code)

            if cs_item:
                transition_code.append('} // inner if') # inner if
                transition_code.append('} // current state') # current state

            sep = 'if('

        if need_final_endif:
            transition_code.append('}')

        transition_code.append('next_transition:')
        transition_code.append(';')
        transition_code.append('}')
        transition_code.append('}')
        transition_code.append('\n')

    continuous_signals_header_file_code.append(u'\n')

    return continuous_signals_header_file_code, transition_code


def aadl_template(process_name, sp_name, io_param, pi_or_ri):
    ''' AADL mini-cv code in case of shared library
        sp_name  : name of the PI or RI
        io_param : list of (param_name, type_name, direction)
        pi_or_ri : string "PI" or "RI" depending on the direction
        return a string
    '''

    res = []

    if not io_param:
        LOG.info('Parameterless interface "{}" will not appear in the'
                    ' AADL file but will be handled directly by the GUI'
                    .format(sp_name))
        return ''
    
    # In case of shared library, generate the AADL "mini-cv" code
    res.append('SUBPROGRAM {}'.format(sp_name))

    if io_param:
        res.append('FEATURES')

        for param_name, sort, direction in io_param:
            res.append('    {pname}: {io} PARAMETER DataView::{sort} '
                        '{{encoding=>Native;}};'.format(pname=param_name,
                                                        sort=sort,
                                                        io=direction))
            
    res.append('END {};\n'.format(sp_name))
    res.append('SUBPROGRAM IMPLEMENTATION {}.GUI_{}'.format(sp_name, pi_or_ri))
    res.append('PROPERTIES')
    res.append('    FV_Name => "{}";'.format(process_name))
    res.append('    Source_Language => GUI_{};'.format(pi_or_ri))
    res.append('END {}.GUI_{};\n'.format(sp_name, pi_or_ri))

    return '\n'.join(res)


def procedure_args(proc):
    declaration_args = ''
    invoke_args = ''

    if proc.fpar:
        declaration_args_list = []
        invoke_args_list = []

        for fpar in proc.fpar:
            name = fpar['name'].lower()
            direction = fpar['direction']
            typename = type_name(fpar['type'])
            pointer = '*' if direction == 'out' or proc.exported else ''

            if proc.exported and direction == 'in':
                name = f'in__{name}'

            declaration_args_list.append(f'{typename} {pointer}{name}')
            invoke_args_list.append(name)

        declaration_args = ', '.join(declaration_args_list)
        invoke_args = ', '.join(invoke_args_list)

    return declaration_args, invoke_args


def procedure_header(procedure, noPrefix=False):
    ''' Build the prototype of a procedure '''
    # use noPrefix=True to return the signature with the raw name, that is
    # needed for inner external procedure (e.g. to link with math symbols)

    return_type = type_name(procedure.return_type) if procedure.return_type else None
    return_type = 'void' if not return_type else return_type

    external = 'extern ' if procedure.external else ''
    separator = f'{SEPARATOR}{PROCESS_NAME.lower()}_' if not procedure.exported else ''

    procedure_name = procedure.inputString if not procedure.exported and not procedure.external else procedure.inputString.lower()

    if procedure.exported and noPrefix==False:
        procedure_name = f'{PROCESS_NAME.lower()}_PI_{procedure_name}'

    declaration_args, _ = procedure_args(procedure)

    if noPrefix:
        procedure_declaration = f'{external}{return_type} {procedure_name}({declaration_args})'
    else:
        procedure_declaration = f'{external}{return_type} {separator}{procedure_name}({declaration_args})'

    return procedure_declaration


def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    return Helper.find_basic_type(TYPES, a_type)


def array_content(prim, values, asnty):
    ''' String literal and SEQOF are given as a sequence of elements '''

    if isinstance(prim, ogAST.PrimEmptyString):
        return values

    elif asnty.kind == 'IA5StringType':
        return u'{{{values}}}'.format(values=values)

    elif asnty.Min != asnty.Max:
        length = len(prim.value)

        if isinstance(prim, ogAST.PrimOctetStringLiteral):
            length = len(prim.hexstring)
        elif isinstance(prim, ogAST.PrimStringLiteral):
            # Quotes are kept in string literals
            length -= 2

        return u'{{{length}, {{{values}}}}}'.format(length=length, values=values)

    return u'{{{{{values}}}}}'.format(values=values)


def type_name(a_type, use_prefix=True):
    ''' Check the type kind and return an C usable type name '''

    if a_type.kind == 'ReferenceType':
        return u'{}{}'.format(ASN1SCC if use_prefix else '', a_type.ReferencedTypeName.replace('-', '_'))
    elif a_type.kind == 'BooleanType':
        return u'_Bool'
    elif a_type.kind.startswith('Integer'):
        return u'asn1SccSint'
    elif a_type.kind == 'RealType':
        return u'asn1SccReal'
    elif a_type.kind.endswith('StringType'):
        return u'asn1SccString'
    elif a_type.kind == 'ChoiceEnumeratedType':
        return u'asn1SccSint'
    elif a_type.kind == 'StateEnumeratedType':
        return u''
    elif a_type.kind == 'EnumeratedType':
        return ASN1SCC if use_prefix else ''
    else:
        raise NotImplementedError('Type name for {}'.format(a_type.kind))


def find_procedure_by_name(procedure_name):
    procedure = None
    procedure_name_lower = procedure_name.lower()

    for proc in PROCEDURES:
        if proc.inputString.lower() == procedure_name_lower:
            procedure = proc
            break

    return procedure


def find_var_in_variables(var):
    ''' Return a variable from VARIABLES, with proper case '''

    var_lower = var.lower()

    for variable in VARIABLES.keys():
        variable_lower = variable.lower()

        if variable_lower == var_lower:
            return variable_lower

    return None


def find_var_in_local_out_variables(var):
    ''' Return a variable from LOCAL_OUT_VARIABLES, with proper case '''

    var_lower = var.lower()

    for local_out_variable in LOCAL_OUT_VARIABLES.keys():
        local_out_variable_lower = local_out_variable.lower()

        if local_out_variable_lower == var_lower:
            return local_out_variable_lower
        
    return None


def find_var_in_local_variables(var):
    ''' Return a variable from LOCAL_VARIABLES, with proper case '''
    
    var_lower = var.lower()

    for local_variable in LOCAL_VARIABLES.keys():
        local_variable_lower = local_variable.lower()

        if local_variable_lower == var_lower:
            return local_variable_lower
        
    return None


def find_var_in_timers(var):
    ''' Return a timer variable from TIMER_VARIABLES, with proper case '''

    var_lower = var.lower()

    for timer_variable in TIMER_VARIABLES:
        if timer_variable.lower() == var_lower:
            return timer_variable
        
    return None


def generate_state_name(state):
    return f'{ASN1SCC}{PROCESS_NAME.capitalize()}_States_{state.lower()}'


def find_state_in_states(state):
    ''' Return a state name from STATES, with proper case '''

    state_lower = str(state).lower()

    for state_variable in STATES:
        if state_variable.lower() == state_lower:
            return state_variable
        
    return None


def append_size(append):
    ''' Return a string corresponding to the length of an APPEND construct
        This function is recursive, to handle cases such as a//b//c
        that is handled as (a//b) // c -> get the length of a//b then add c
    '''

    result = ''
    basic = find_basic_type(append.exprType)

    if basic.Min == basic.Max:
        # Simple case when appending two fixed-length sizes
        return basic.Min
    
    for each in (append.left, append.right):
        if result:
            result += ' + '

        if isinstance(each, ogAST.ExprAppend):
            # Inner append -> go recursively
            result += append_size(each)
        else:
            bty = find_basic_type(each.exprType)

            if bty.Min == bty.Max:
                result += bty.Min
            else:
                # Must be a variable of type SEQOF
                _, inner, _ = expression(each)
                result += '{}.Count'.format(inner)

    return result


def indent_c_code(lines):
    indent = 0
    indent_pattern = '   '

    for line in lines:
        elems = line.strip().split()

        if elems and elems[0].startswith(('}')):
            indent -=1

        if line:
            yield indent_pattern * indent + line

        if elems and elems[0].startswith(('{')):
            indent +=1


def traceability(symbol):
    ''' Return a string with code-to-model traceability '''

    trace = [u'// {line}'.format(line=l) for l in symbol.trace().split('\n')]

    if hasattr(symbol, 'comment') and symbol.comment:
        trace.extend(traceability(symbol.comment))

    return trace


def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''

    global STDIO_INCLUDE
    global VAR_COUNTER

    STDIO_INCLUDE = True

    code = []
    local = []
    string = ''

    basic_type = find_basic_type(param.exprType) or {}
    type_kind = basic_type.kind

    if isinstance(param, ogAST.ExprAppend):
        # Append: call Put_Line separately for each side of the expression
        st1, _, lcl1= write_statement(param.left, newline = False)
        st2, _, lcl2 = write_statement(param.right, newline = False)

        code.extend(st1)
        code.extend(st2)

        local.extend(lcl1)
        local.extend(lcl2)
    elif type_kind.endswith('StringType'):
        if isinstance(param, ogAST.PrimOctetStringLiteral):
            code.append('printf(\"{}\");'.format(param.printable_string))
        elif isinstance(param, ogAST.PrimStringLiteral):
            # adding/or not escaping for quote (") character
            raw_string = param.value[1:-1]
            new_string = ''

            start_pos = 0
            while True:
                quote_pos = raw_string.find('"', start_pos)

                if quote_pos == -1:
                    new_string += raw_string[start_pos:]
                    break

                if raw_string[quote_pos - 1] == '\\':
                    new_string += raw_string[start_pos:quote_pos+1]
                else:
                    new_string += raw_string[start_pos:quote_pos]
                    new_string += '\\"'

                start_pos = quote_pos + 1

            # looking for '\n' characters
            start_pos = 0
            while True:
                new_line_pos = new_string.find('\n', start_pos)

                if new_line_pos == -1:
                    code.append(f'printf(\"{new_string[start_pos:]}\");')
                    break

                code.append(f'printf(\"{new_string[start_pos:new_line_pos]}\");')
                code.append(u'printf(\"\\n\");')

                start_pos = new_line_pos + 1
        else:
            code, string, local = expression(param)

            if type_kind == 'OctetStringType':
                # Octet string -> convert to Ada string
                if isinstance(param, ogAST.PrimSubstring):
                    local.append(u'asn1SccUint write_{var_counter};'.format(var_counter=VAR_COUNTER))

                    code.append('{')
                    code.append('for(write_{var_counter} = min_range_{var_counter}; write_{var_counter} <= max_range_{var_counter}; write_{var_counter}++)'.format(var_counter=VAR_COUNTER))
                    code.append('{')
                    code.append('printf(\"%c\", {st}.arr[write_{var_counter}]);'.format(st=string, var_counter=VAR_COUNTER))
                    code.append('}')
                    code.append('}')
                elif basic_type.Min == basic_type.Max:
                    VAR_COUNTER = VAR_COUNTER + 1

                    local.append(u'asn1SccUint write_{var_counter};'.format(var_counter=VAR_COUNTER))
                    code.append('for(write_{var_counter} = 0; write_{var_counter} < {size}; write_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=basic_type.Max))
                    code.append('{')
                    code.append('printf(\"%c\", {st}.arr[write_{var_counter}]);'.format(st=string, var_counter=VAR_COUNTER))
                    code.append('}')
                else:
                    VAR_COUNTER = VAR_COUNTER + 1

                    local.append(u'int write_{var_counter};'.format(var_counter=VAR_COUNTER))
                    code.append('for(write_{var_counter} = 0; write_{var_counter} < {le}.nCount; write_{var_counter}++)'.format(var_counter=VAR_COUNTER, le=string))
                    code.append('{')
                    code.append('printf(\"%c\", {st}.arr[write_{var_counter}]);'.format(st=string, var_counter=VAR_COUNTER))
                    code.append('}')
            elif type_kind == 'IA5StringType' and isinstance(param, ogAST.PrimVariable): # should be fixed later
                code.append(u'{')
                code.append(u'asn1SccUint tmp_counter = 0;')
                code.append(u'for(tmp_counter = 0; tmp_counter < {size} && {var}[tmp_counter] != \'\\0\'; tmp_counter++)'.format(size=basic_type.Max, var=string))
                code.append(u'{')
                code.append(u'printf(\"%c\", {var}[tmp_counter]);'.format(var=string))
                code.append(u'}')
                code.append(u'}')
            else:
                code.append(u'{')
                code.append(u'int tmp_counter = 0;')
                code.append(u'for(tmp_counter = 0; tmp_counter < {st}.nCount; tmp_counter++)'.format(st=string))
                code.append(u'{')
                code.append(u'printf(\"%c\", {}.arr[tmp_counter]);'.format(string))
                code.append(u'}')
                code.append(u'}')
    elif type_kind in ('IntegerType', 'RealType', 'BooleanType', 'Integer32Type',
            'IntegerU8Type'):
        code, string, local = expression(param)

        if type_kind in ('IntegerType', 'Integer32Type'):
            code.append(generate_printf_call(basic_type, string, param))
        elif type_kind == 'BooleanType':
            code.append('printf({value} ? \"TRUE\" : \"FALSE\");'.format(value=string))
        elif type_kind == 'RealType':
            code.append(f'printf(\" %lf\", {string});')
    elif type_kind == 'EnumeratedType':
        code, string, local = expression(param)
        code.append(f'switch({string}) {{')
        for name, enumid in basic_type.EnumValues.items():
            code.append(f'case {enumid.EnumID}: printf("{name.upper()}"); break;')
        code.append('}')
    else:
        error = (u'Unsupported parameter in write call ' + param.inputString)
        LOG.error(error)
        raise TypeError(error)

    if newline:
        code.append('printf(\"\\n\");')

    return code, string, local

def generate_printf_call(int_basic_type, string, param):
    int_min_value = int(float(int_basic_type.Min))

    # Enum type values are unsigned int. -num must be printed with %d
    neg_num = int_basic_type.__name__ == 'Neg' and param.expr.exprType.__name__ == 'Num'

    printf_call = 'printf('
    if neg_num:
        printf_call += '\"%d\"'
    elif int_min_value < 0:
        printf_call += '\" %ld\"'
    else:
        printf_call += '\" %lu\"'

    printf_call += ', {str});'.format(str=string)

    return printf_call

def get_bitwise_operator(operand):
    if operand == 'and':
        return '&'
    elif operand == 'or':
        return '|'
    elif operand == 'xor':
        return '^'
    else:
        raise NotImplementedError(f'Unknown bitwise operator - "{operand}"')
