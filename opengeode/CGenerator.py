#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates C code from SDL process models.

    Copyright (c) 2015 Politecnico di Milano

    Designed and implemented by Marco Lattuada

    Contact: marco.lattuada@polimi.it
"""

import logging
import os
from singledispatch import singledispatch

import Helper
import ogAST

LOG = logging.getLogger(__name__)

__all__ = ['generate']

VARIABLES = {}
LOCAL_OUT_PARS = {}
LOCAL_VAR = {}
LOCAL_VARIABLE_TYPES = {}
OUT_SIGNALS = []
PROCEDURES = []

UNICODE_SEP = u'___'
LPREFIX = u'context'

LEFT_TYPE = ''
VAR_COUNTER = 0

# Specify that the target is a shared library
SHARED_LIB = False

@singledispatch
def generate(*args, **kwargs):
    ''' Generate the code for an item of the AST '''
    for arg in args:
        LOG.info(arg)
    raise TypeError('[CGenerator] Unsupported AST construct')
    return [], []

# Processing of the AST
@generate.register(ogAST.Decision)
def _decision(dec, **kwargs):
    ''' generate the code for a decision '''
    global VAR_COUNTER
    stmts, decls = [], []
    if dec.kind == 'any':
        LOG.warning('C backend does not support the "ANY" statement')
        stmts.append('// "DECISION ANY" statement was ignored')
        return stmts, decls
    elif dec.kind == 'informal_text':
        LOG.warning('Informal decision ignored')
        stmts.append('// Informal decision was ignored: {}'
                    .format(dec.inputString))
        return stmts, decls
    question_type = dec.question.exprType
    actual_type = type_name(question_type)
    basic = find_basic_type(question_type).kind in ('IntegerType', 'Integer32Type', 'BooleanType', 'RealType', 'EnumeratedType', 'ChoiceEnumeratedType')
    # for ASN.1 types, declare a local variable
    # to hold the evaluation of the question
    if not basic:
        decls.append('{actType} tmp{idx};'.format(idx=dec.tmpVar, actType=actual_type))
    question_stmts, question_string, question_decls = expression(dec.question)
    # Add code-to-model traceability
    stmts.extend(traceability(dec))
    decls.extend(question_decls)
    stmts.extend(question_stmts)
    if not basic:
        stmts.append('tmp{idx} = {q};'.format(idx=dec.tmpVar, q=question_string))
    sep = 'if('
    for a in dec.answers:
        stmts.extend(traceability(a))
        if a.kind in ('open_range', 'constant'):
            # Note: removed and a.transition here because empty transitions
            # have a different meaning, and a "null;" statement has to be
            # generated, to go into the branch
            ans_stmts, ans_str, ans_decl = expression(a.constant)
            stmts.extend(ans_stmts)
            decls.extend(ans_decl)
            if not basic:
                if a.openRangeOp in (ogAST.ExprEq, ogAST.ExprNeq):
                    if isinstance(a.constant, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                        ans_str = array_content(a.constant, ans_str, find_basic_type(question_type))
                        VAR_COUNTER = VAR_COUNTER + 1
                        decls.append(u'{ty} temp_equal_{var_counter} = {init};'.format(ty=actual_type, var_counter=VAR_COUNTER, init=ans_str))
                        ans_str = u'temp_equal_{var_counter}'.format(var_counter=VAR_COUNTER)
                    elif isinstance(a.constant, ogAST.PrimChoiceItem):
                        VAR_COUNTER = VAR_COUNTER + 1
                        decls.append(u'{ty} temp_equal_{var_counter};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                        stmts.append(u'temp_equal_{var_counter} = {init};'.format(var_counter=VAR_COUNTER, init=ans_str))
                        ans_str = u'temp_equal_{var_counter}'.format(var_counter=VAR_COUNTER)
                    exp = u'{actType}_Equal(&tmp{idx}, &{ans})'.format(actType=actual_type, idx=dec.tmpVar, ans=ans_str)
                    if a.openRangeOp == ogAST.ExprNeq:
                        exp = u'! {}'.format(exp)
                else:
                    exp = u'tmp{idx} {op} {ans}'.format(idx=dec.tmpVar, op='==' if a.openRangeOp.operand == '=' else a.openRangeOp.operand, ans=ans_str)
            else:
                exp = u'({q}) {op} {ans}'.format(q=question_string, op='==' if a.openRangeOp.operand == '=' else a.openRangeOp.operand, ans=ans_str)
            stmts.append(sep + exp + ')')
            stmts.append('{')
            if a.transition:
                transition_stmts, transition_decls = generate(a.transition)
            else:
                transition_stmts, transition_decls = [';'], []
            stmts.extend(transition_stmts)
            decls.extend(transition_decls)
            stmts.append('}')
            sep = 'else if('
        elif a.kind == 'closed_range':
            cl0_stmts, cl0_str, cl0_decl = expression(a.closedRange[0])
            cl1_stmts, cl1_str, cl1_decl = expression(a.closedRange[1])
            stmts.extend(cl0_stmts)
            decls.extend(cl0_decl)
            stmts.extend(cl1_stmts)
            decls.extend(cl1_decl)
            stmts.append('{sep} {dec} >= {cl0} && {dec} <= {cl1})'.format(sep=sep, dec=question_string, cl0=cl0_str, cl1=cl1_str))
            stmts.append('{')
            if a.transition:
                transition_stmts, transition_decls = generate(a.transition)
            else:
                transition_stmts, transition_decls = [';'], []
            stmts.extend(transition_stmts)
            decls.extend(transition_decls)
            stmts.append('}')
            sep = 'else if('
        elif a.kind == 'informal_text':
            continue
        elif a.kind == 'else':
            # Keep the ELSE statement for the end
            if a.transition:
                else_stmts, else_decl = generate(a.transition)
                else_stmts.insert(0, '{')
                else_stmts.append('}')
            else:
                else_stmts, else_decl = ['{',';','}'], []
            decls.extend(else_decl)
    try:
        if sep != 'if(':
            # If there is at least one 'if' branch
            else_stmts.insert(0, 'else')
            stmts.extend(else_stmts)
        else:
            stmts.extend(else_stmts)
    except:
        pass
    return stmts, decls


@generate.register(ogAST.Floating_label)
def _floating_label(label, **kwargs):
    ''' Generate the code for a floating label (C label + transition) '''
    code = []
    local_decl = []
    # Add the traceability information
    code.extend(traceability(label))
    code.append(u'{label}:'.format(label=label.inputString))
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
    return ['goto {label};'.format(label=lab.inputString)], []


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output, **kwargs):
    ''' Generate the code of a set of output or procedure call statement '''
    stmts = []
    decls = []

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
            if not SHARED_LIB:
                stmts.append('RESET_{};'.format(p_id))
            else:
                stmts.append('RESET_{t}("{t}");'.format(t=p_id))
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
            if not SHARED_LIB:
                # Use a temporary variable to store the timer value
                tmp_id = 'tmp' + str(out['tmpVars'][0])
                decls.append('asn1SccUint32 {};'.format(tmp_id))
                stmts.append('{tmp} = {val};'.format(tmp=tmp_id, val=t_val))
                stmts.append("SET_{timer}(&{value});".format(timer=p_id, value=tmp_id))
            else:
                stmts.append('SET_{t}("{t}", {val});'.format(t=p_id, val=t_val))
            continue
        proc, out_sig = None, None
        is_out_sig = False
        try:
            out_sig, = [sig for sig in OUT_SIGNALS if sig['name'].lower() == signal_name.lower()]
            is_out_sig = True if SHARED_LIB else False
        except ValueError:
            # Not an output, try if it is an external or inner procedure
            try:
                proc, = [sig for sig in PROCEDURES if sig.inputString.lower() == signal_name.lower()]
                if proc.external:
                    out_sig = proc
            except ValueError:
                # Not there? Impossible, the parser would have barked
                raise ValueError(u'Probably a bug - please report')
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
                        decls.append('{sort} {tmp} = {init};'.format(tmp=tmp_id, sort=typename, init= array_content(param, p_id, find_basic_type(param_type))))
                    else:
                        decls.append('{sort} {tmp};'.format(tmp=tmp_id, sort=typename))
                        if isinstance(param, ogAST.PrimSequenceOf):
                            p_id = array_content(param, p_id, find_basic_type(param_type))
                        stmts.append('{} = {};'.format(tmp_id, p_id))
                    list_of_params.append("&{}{}".format(tmp_id,", sizeof({})".format(tmp_id) if is_out_sig else ""))
                else:
                    # Output parameters/local variables
                    list_of_params.append(u"&{var}{shared}".format(var=p_id, shared=", sizeof({})".format(p_id) if is_out_sig else ""))
            if list_of_params:
                stmts.append(u'{RI}({params});'.format(RI=out['outputName'], params=', '.join(list_of_params)))
            else:
                if not SHARED_LIB:
                    stmts.append(u'{RI};'.format(RI=out['outputName']))
                else:
                    stmts.append(u'{RI}(("{RI}"));'.format(RI=out['outputName']))
        else:
            # inner procedure call
            list_of_params = []
            param_counter = 0
            for param in out.get('params', []):
                param_stmts, p_id, p_local = expression(param)
                stmts.extend(param_stmts)
                decls.extend(p_local)
                # no need to use temporary variables, we are in pure Ada
                if proc.fpar[param_counter].get('direction') == 'out':
                    p_id = u'&' + p_id
                list_of_params.append( p_id)
                param_counter = param_counter + 1
            if list_of_params:
                stmts.append(u'{sep}{proc}({params});'.format(sep=UNICODE_SEP, proc=proc.inputString, params=', '.join(list_of_params)))
            else:
                stmts.append(u'{}{}();'.format(UNICODE_SEP, proc.inputString))
    return stmts, decls


@generate.register(ogAST.Procedure)
def _inner_procedure(proc, **kwargs):
    ''' Generate the code for a procedure - does not support states '''
    LOG.debug('Expanding procedure ' + proc.inputString)
    code = []
    local_decl = []
    # TODO: Update the global list of procedures
    # with procedure defined inside the current procedure
    # Not critical: the editor forbids procedures inside procedures

    # Save variable scopes (as local variables may shadow process variables)
    outer_scope = dict(VARIABLES)
    local_scope = dict(LOCAL_VAR)
    outer_params = dict(LOCAL_OUT_PARS)
    VARIABLES.update(proc.variables)
    # Store local variables in global context
    LOCAL_VAR.update(proc.variables)
    LOCAL_OUT_PARS.clear()
    # Also add procedure parameters in scope
    for var in proc.fpar:
        elem = {var['name']: (var['type'], None)}
        VARIABLES.update(elem)
        LOCAL_VAR.update(elem)
        if var.get('direction') == 'out':
            LOCAL_OUT_PARS.update(elem)

    # Build the procedure signature (function if it can return a value)
    ret_type = type_name(proc.return_type) if proc.return_type else None
    pi_header = u'{ext}{ret_type} {sep}{proc_name}'.format(ext='extern ' if proc.external else '', ret_type='void' if not ret_type else ret_type, proc_name=proc.inputString, sep=UNICODE_SEP if not proc.external else '')

    pi_header += '('

    if proc.fpar:
        params = []
        first = True
        for fpar in proc.fpar:
            typename = type_name(fpar['type'])

            params.append(u'{ptype} {pt} {name}'.format(ptype=typename, pt='*' if fpar.get('direction') == 'out' or proc.external else '', name=fpar.get('name')))
            first = False
        pi_header += ','.join(params)

    pi_header += ')'

    local_decl.append(pi_header + ';')
    # Remote procedures need to be exported with a C calling convention

    if not proc.external:
        # Generate the code for the procedure itself
        # local variables and code of the START transition
        # Recursively generate the code for inner-defined procedures
        for inner_proc in proc.content.inner_procedures:
            inner_code, inner_local = generate(inner_proc)
            local_decl.extend(inner_local)
            code.extend(inner_code)
        code.append(pi_header)
        code.append(u'{')
        for var_name, (var_type, def_value) in proc.variables.viewitems():
            typename = type_name(var_type)
            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result
                dst, dstr, dlocal = expression(def_value)
                varbty = find_basic_type(var_type)
                if varbty.kind in ('SequenceOfType', 'OctetStringType'):
                    dstr = array_content(def_value, dstr, varbty)
                assert not dst and not dlocal, 'Ground expression error'
            code.append(u'{ty} {name} {default};'.format(ty=typename, name=var_name, default=' = ' + dstr if def_value else ''))

        # Look for labels in the diagram and transform them in floating labels
        Helper.inner_labels_to_floating(proc)
        if proc.content.start:
            tr_code, tr_decl = generate(proc.content.start.transition)
        else:
            tr_code, tr_decl = [';  //  Empty procedure'], []
        # Generate code for the floating labels
        code_labels = []
        for label in proc.content.floating_labels:
            code_label, label_decl = generate(label)
            code_labels.extend(code_label)
            tr_decl.extend(label_decl)
        code.extend(set(tr_decl))
        code.extend(tr_code)
        code.extend(code_labels)
        code.append(u'}')
    code.append('\n')

    # Reset the scope to how it was prior to the procedure definition
    VARIABLES.clear()
    VARIABLES.update(outer_scope)
    LOCAL_VAR.clear()
    LOCAL_VAR.update(local_scope)
    LOCAL_OUT_PARS.clear()
    LOCAL_OUT_PARS.update(outer_params)

    return code, local_decl

@generate.register(ogAST.Process)
def _process(process, simu=False, **kwargs):
    ''' Generate the code for a complete process (AST Top level) '''

    #Types
    global TYPES
    TYPES = process.dataview

    del OUT_SIGNALS[:]
    OUT_SIGNALS.extend(process.output_signals)

    del PROCEDURES[:]
    PROCEDURES.extend(process.procedures)

    #The name of the process
    process_name = process.processName

    #The generated source code
    c_source_code = []
    h_source_code = []

    #The global declarations
    global_decls = []

    #The number of temporary variable
    global tmp_var_id
    tmp_var_id = 0

    #True if math.h has to be included
    global math_include
    math_include = False

    #True if stdio.h has to be included
    global STDIO_INCLUDE
    STDIO_INCLUDE = False

    #True if string.h has to be included
    global string_include
    string_include = False

    global LPREFIX
    global SHARED_LIB
    if simu:
        SHARED_LIB = True
        LPREFIX = process_name + u'_ctxt'

    # When building a shared library (with simu=True), generate a "mini-cv"
    # for aadl2glueC to create the code interfacing with asn1scc
    minicv = ['// Automatically generated by OpenGEODE - do NOT modify!']
    def aadl_template(sp_name, io_param, pi_or_ri):
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
        res.append('SUBPROGRAM IMPLEMENTATION {}.GUI_{}'
                      .format(sp_name, pi_or_ri))
        res.append('PROPERTIES')
        res.append('    FV_Name => "{}";'.format(process_name))
        res.append('    Source_Language => GUI_{};'.format(pi_or_ri))
        res.append('END {}.GUI_{};\n'.format(sp_name, pi_or_ri))
        return '\n'.join(res)

    # bash script to simulate the system (TEMPORARY)
    simu_script = '''#!/bin/bash -e
opengeode {pr}.pr --shared --toC
asn1.exe -c dataview-uniq.asn -typePrefix asn1Scc -equal
gcc -c *.c -fPIC
gcc -shared -fPIC -o lib{pr}.so {pr}.o dataview-uniq.o adaasn1rtl.o -lgnat
rm -rf simu
mkdir -p simu
asn2aadlPlus dataview-uniq.asn simu/DataView.aadl
cp lib{pr}.so dataview-uniq.asn *.pr simu
mv *.aadl simu
cd simu
aadl2glueC DataView.aadl {pr}_interface.aadl
asn2dataModel -toPython dataview-uniq.asn
make -f Makefile.python
echo "errCodes=$(taste-asn1-errCodes ./dataview-uniq.h)" >>datamodel.py
LD_LIBRARY_PATH=. taste-gui -l
'''.format(pr=process_name)


    LOG.info('Generating C code for process ' + str(process_name))

    # In case model has nested states, flatten everything
    Helper.flatten(process, sep=UNICODE_SEP)

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    VARIABLES.update(process.variables)

    #Computing state lists
    state_list = ', '.join(name for name in process.mapping.iterkeys() if not name.endswith(u'START')) or 'No_State'

    #Declaring global type modeling the state
    if state_list:
        state_decl = u'typedef enum {{{}}} states_t;'.format(state_list)
        global_decls.append(state_decl)

    #Declaring global type modeling the context
    context_type = []
    context_init_code = []
    context_type.append(u'typedef struct')
    context_type.append(u'{')
    context_init_code.append(u'void CInit()')
    context_init_code.append(u'{')

    if state_list:
        context_type.append(u'states_t state;')

    for var_name, (var_type, init) in process.variables.viewitems():
        init_stmt = []
        init_string = ''
        init_decl = []
        if init:
            init_stmt, temp_init_string, init_decls  = expression(init)
            if find_basic_type(var_type).kind in ('SequenceOfType', 'OctetStringType'):
                init_string = array_content(init, temp_init_string, find_basic_type(var_type ))
                if find_basic_type(var_type).Min == find_basic_type(var_type).Max:
                    init_string = u'{{{init}}}'.format(init=init_string)
            else:
                init_stmt, init_string, init_decl = expression(init)
            if find_basic_type(var_type).kind in ('SequenceOfType', 'OctetStringType', 'SequenceType'):
                init_string = u'(' + type_name(var_type) + u') ' + init_string
            LOG.debug(var_name)
            context_init_code.append(u'{ct}.{field} = {init};'.format(ct=LPREFIX, field=var_name, init=init_string))
            assert not init_stmt, 'Initialization of ' + init_name + ' requires to add statement'
            assert not init_decl, 'Initialization of ' + init_name + ' requires to add declartions'
        context_type.append(u'{tn} {vn};'.format(tn = type_name(var_type), vn = var_name))


    context_type.extend(['} context_t;'])
    context_init_code.append(u'}')
    global_decls.extend(context_type)

    # Adding the declaration of the state variable
    global_decls.append(u'context_t {ct};'.format(ct=LPREFIX))
    global_decls.extend(context_init_code)

    for name, val in process.mapping.viewitems():
        if name.endswith(u'START') and name != u'START':
            global_decls.append(u'#define {name} {val}'.format(name=name, val=str(val)))

    # Add the declaration of the runTransition procedure, if needed
    if process.transitions:
        global_decls.append('void runTransition(int Id);')

    # Generate the code of the start transition (if process not empty)
    start_transition = ['runTransition(0);'] if process.transitions else []

    dll_code = []
    if simu:
        h_source_code.append('//  DLL Interface')
        dll_code.append('// DLL Interface to remotely change internal data')
        # Add function allowing to trace current state as a string
        global_decls.append(u'char * {pn}_state()'.format(pn=process_name))
        global_decls.append(u'{')
        for state_name in process.mapping.iterkeys():
            if not state_name.endswith(u'START') and  state_name != 'No_State':
                global_decls.append(u'if({ctxt}.state == {sn}) return \"{sn}\\0\";'.format(ctxt=LPREFIX, sn=state_name))
        global_decls.append(u'return \"\\0\";')
        global_decls.append(u'}')

        set_state_decl = u'void _set_state(char * new_state)'
        h_source_code.append(u'{};'.format(set_state_decl))

        dll_code.append(u'{}'.format(set_state_decl))
        dll_code.append(u'{')
        for state_name in process.mapping.iterkeys():
            if not state_name.endswith(u'START') and  state_name != 'No_State':
                dll_code.append(u'if(strcmp(new_state, \"{st}\") == 0) {ctxt}.state = {st};'.format(st=state_name, ctxt=LPREFIX))
        dll_code.append(u'}')
        dll_code.append(u'')

        # Functions to get gobal variables (length and value)
        for var_name, (var_type, _) in process.variables.viewitems():
            # Getters for local variables
            global_decls.append(u'int {name}_size()'.format(name=var_name))
            global_decls.append(u'{')
            global_decls.append(u'return sizeof({ctnx}.{name});'.format(ctnx=LPREFIX, name=var_name))
            global_decls.append(u'}')
            global_decls.append(u'{ty} * {name}_value()'.format(ty=type_name(var_type), name=var_name))
            global_decls.append(u'{')
            global_decls.append(u'return &({ctnx}.{name});'.format(ctnx=LPREFIX, name=var_name))
            global_decls.append(u'}')

            # Setters for local variables
            setter_decl = u'void dll_set_l_{name}({ty} * value)'.format(name=var_name, ty=type_name(var_type))
            h_source_code.append('{};'.format(setter_decl))
            dll_code.append(u'{}'.format(setter_decl))
            dll_code.append(u'{')
            dll_code.append(u'{}.{} = *value;'.format(LPREFIX, var_name))
            dll_code.append(u'}')
            dll_code.append(u'')

    # Generate the code of the procedures
    inner_procedures_code = []
    for proc in process.content.inner_procedures:
        proc_code, proc_declaration = generate(proc)
        global_decls.extend(proc_declaration)
        inner_procedures_code.extend(proc_code)

    input_signals_code = []

    for signal in process.input_signals + [{'name': timer.lower()} for timer in process.timers]:
        if signal.get('name', u'START') == u'START':
            continue
        pi_header = u'void {sig_name}'.format(sig_name=signal['name'])
        param_name = signal.get('param_name') or u'{}_param'.format(signal['name'])
        # Add (optional) PI parameter (only one is possible in TASTE PI)
        if 'type' in signal:
            typename = type_name(signal['type'])
            pi_header += u'({tn} * {pn})'.format(tn=typename, pn=param_name)
        else:
            pi_header += u'()'

        # Add declaration of the provided interface in the .h file
        h_source_code.append(u'//  Provided interface "' + signal['name'] + '"')
        h_source_code.append(pi_header + ';')
        if simu:
            # Generate code for the mini-cv template
            params = [(param_name, type_name(signal['type'], use_prefix=False),'IN')] if 'type' in signal else []
            minicv.append(aadl_template(signal['name'], params, 'RI'))
        input_signals_code.append(pi_header)
        input_signals_code.append(u'{')
        input_signals_code.append(u'switch({ct}.state)'.format(ct=LPREFIX))
        input_signals_code.append(u'{')
        for state in process.mapping.viewkeys():
            if state.endswith(u'START'):
                continue
            input_signals_code.append(u'case {st}:'.format(st=state))
            input_signals_code.append('{')
            input_def = mapping[signal['name']].get(state)
            # Check for nested states to call optional exit procedure
            sep = UNICODE_SEP
            state_tree = state.split(sep)
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
                        current = current + sep
                        break
            for each in reversed(exitlist):
                if trans and all(each.startswith(trans_st) for trans_st in trans.possible_states):
                    input_signals_code.append(u'{sep}{ref}{sep}exit();'.format(ref=each, sep=sep))
            if input_def:
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    input_signals_code.append(u'{ctxt}.{inp} = *{tInp};'.format(ctxt=LPREFIX,inp=inp,tInp=param_name));
                # Execute the correponding transition
                if input_def.transition:
                    input_signals_code.append('runTransition({idx});'.format(idx=input_def.transition_id))
            input_signals_code.append('break;')
            input_signals_code.append('}')
        input_signals_code.append('default:')
        input_signals_code.append('{')
        input_signals_code.append('break;')
        input_signals_code.append('}')
        input_signals_code.append('}')
        input_signals_code.append('}\n')

    output_signals_code = []

    simu_code = []

    for signal in process.output_signals:
        param_name = signal.get('param_name') or u'{}_param'.format(signal['name'])
        # Add (optional) RI parameter
        param_spec = '' if not simu else "(tm: chars_ptr)"
        if 'type' in signal:
            typename = type_name(signal['type'])
            param_spec = u'({sort} * {pName})'.format(pName=param_name, sort=typename)
        else:
            param_spec = u'()'
        output_signals_code.append(u'//  Required interface "' + signal['name'] + '"')
        if simu:
            # When generating a shared library, we need a callback mechanism
            h_source_code.append(u'typedef void (* {}_T)();'.format(signal['name'], param_spec))
            h_source_code.append(u'{sig}_T {sig};'.format(sig=signal['name']))
            h_source_code.append(u'void Register_{sig}({sig}_T Callback);'.format(sig=signal['name']))

            # Generate code for the mini-cv template
            params = [(param_name, type_name(signal['type'], use_prefix=False), 'IN')] if 'type' in signal else []
            minicv.append(aadl_template(signal['name'], params, 'PI'))

            simu_code.append(u'void Register_{sig}({sig}_T Callback)'.format(sig=signal['name']))
            simu_code.append(u'{')
            simu_code.append(u'{} = Callback;'.format(signal['name']))
            simu_code.append(u'}')
            simu_code.append(u'')
        else:
            output_signals_code.append(u'void {}{};'.format(signal['name'], param_spec))

    # for the .h file, generate the declaration of the external procedures
    for proc in (proc for proc in process.procedures if proc.external):
        h_source_code.append(u'#define {fn} {pn}_RI_{fn}'.format(fn=proc.inputString, pn=process_name))
        ri_header = u'void {sig_name}'.format(sig_name=proc.inputString)
        params = []
        for param in proc.fpar:
            typename = type_name(param['type'])
            params.append(u'{ty} * {par}'.format(par=param['name'], ty=typename))
        if params:
            ri_header += u'(' + u','.join(params) + ')'
        else:
            ri_header += u'()'
        h_source_code.append(u'//  Sync required interface "' + proc.inputString)
        h_source_code.append(ri_header + u';')

    timers_code = []

    # for the .h file, generate the declaration of timers set/reset functions
    for timer in process.timers:
        h_source_code.append(u'//  Timer {} SET and RESET functions'.format(timer))
        if simu:
            # Declare callback registration for the SET and RESET functions
            h_source_code.append(u'typedef void (* SET_{}_T) (char * name, int duration);'.format(timer))
            h_source_code.append(u'typedef void (* RESET_{}_T) (char * name);'.format(timer))
            for each in ('', 'RE'):
                h_source_code.append(u'{re}SET_{t}_T {re}SET_{t};'.format(re=each, t=timer))
                h_source_code.append(u'void Register_{re}SET_{t}({re}SET_{t}_T Callback);'.format(re=each, t=timer))
            # Code for the SET/RESET timer callback registration
            for each in ('', 'RE'):
                timers_code.append(u'void Register_{re}SET_{t}({re}SET_{t}_T Callback)'.format(re=each, t=timer))
                timers_code.append(u'{')
                timers_code.append(u'{re}SET_{t} = Callback;'.format(re=each, t=timer))
                timers_code.append(u'}')
                timers_code.append(u'')

        else:
            h_source_code.append(u'void SET_{}(asn1SccUint32 * val);'.format(timer))
            h_source_code.append(u'void RESET_{}();'.format(timer))
    # Transform inner labels to floating labels
    Helper.inner_labels_to_floating(process)

    # Generate the code for all transitions
    code_transitions = []
    decl_transitions = []
    for transition in process.transitions:
        transition_stmts, transition_decls = generate(transition)
        code_transitions.append(transition_stmts)
        decl_transitions.extend(transition_decls)

    # Generate code for the floating labels
    code_labels = []
    for label in process.content.floating_labels:
        code_label, label_decl = generate(label)
        decl_transitions.extend(label_decl)
        code_labels.extend(code_label)

    transition_source_code = []

    # Generate the code of the runTransition procedure, if needed
    if process.transitions:
        transition_source_code.append('void runTransition(int Id)')
        transition_source_code.append('{')
        transition_source_code.append('int trId = Id;')

        # Declare the local variables needed by the transitions in the template
        transition_source_code.extend(set(decl_transitions))

        # Generate a loop that ends when a next state is reached
        # (there can be chained transition when entering a nested state)
        transition_source_code.append('while (trId != -1)')
        transition_source_code.append('{')

        # Generate the switch-case on the transition id
        transition_source_code.append('switch(trId)')
        transition_source_code.append('{')

        for idx, val in enumerate(code_transitions):
            transition_source_code.append(u'case {idx}:'.format(idx=idx))
            transition_source_code.append('{')
            val = [u'{line}'.format(line=l) for l in val]
            if val:
                transition_source_code.extend(val)
            transition_source_code.append('break;')
            transition_source_code.append('}')

        transition_source_code.append('default:')
        transition_source_code.append('{')
        transition_source_code.append('break;')
        transition_source_code.append('}')
        transition_source_code.append('}')
        if code_labels:
            # Due to nested states (chained transitions) jump over label code
            # (NEXTSTATEs do not return from runTransition)
            transition_source_code.append('goto next_transition;')

        # Add the code for the floating labels
        transition_source_code.extend(code_labels)

        transition_source_code.append('next_transition:')
        transition_source_code.append(';')
        transition_source_code.append('}')
        transition_source_code.append('}')
        transition_source_code.append('\n')

    if math_include == True:
        c_source_code.append(u'#include <math.h>')

    if STDIO_INCLUDE == True:
        c_source_code.extend(['#include <stdio.h>'])

    if string_include == True:
        c_source_code.extend(['#include <string.h>'])

    for each in process.DV.asn1Files:
        hname = os.extsep.join(each.split(os.extsep)[:-1]) + os.extsep + 'h'
        c_source_code.extend(['#include "{}"'.format(hname)])
    c_source_code.append('#include \"{pn}.h\"'.format(pn=process_name))

    c_source_code.extend(global_decls)
    c_source_code.extend(input_signals_code)
    c_source_code.extend(output_signals_code)
    c_source_code.extend(timers_code)
    c_source_code.extend(simu_code)
    c_source_code.extend(inner_procedures_code)
    c_source_code.extend(dll_code)
    c_source_code.extend(transition_source_code)

    with open(process_name + '.c', 'w') as c_file:
        c_file.write(u'\n'.join(indent_c_code(c_source_code)).encode('latin1'))
    with open(process_name + '.h', 'w') as h_file:
        h_file.write(u'\n'.join(indent_c_code(h_source_code)).encode('latin1'))


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
    '''
        Return the code corresponding to a for loop. Two forms are possible:
    '''
    stmts, decls = [], []
    local_scope = dict(LOCAL_VAR)
    if task.comment:
        stmts.extend(traceability(task.comment))
    stmts.extend(traceability(task))
    for loop in task.elems:
        stmts.append('{')
        if loop['range']:
            stmts.append('unsigned int ' + loop['var'] + ';')
            start_str, inc_str, stop_str = '0', '', ''
            if loop['range']['start']:
                start_stmts, start_str, start_local = expression(loop['range']['start'])
                decls.extend(start_local)
                stmts.extend(start_stmts)
            start_str = loop['var'] + '  = ' + start_str
            if loop['range']['step'] == 1:
                inc_str += loop['var'] + '++'
            else:
                inc_str += loop['var'] + ' +=' + str(loop['range']['step'])
            stop_stmts, stop_str, stop_local = expression(loop['range']['stop'])
            decls.extend(stop_local)
            stmts.extend(stop_stmts)
            stop_str = loop['var'] + ' < ' + stop_str
            stmts.append('for(' + start_str + '; ' + stop_str + '; ' + inc_str + ')')
            stmts.append('{')
        else:
            # case of form: FOR x in SEQUENCE OF
            # Add iterator to the list of local variables
            LOCAL_VAR.update({loop['var']: (loop['type'], None)})

            list_stmt, list_str, list_local = expression(loop['list'])
            basic_type = find_basic_type(loop['list'].exprType)
            if isinstance(loop['list'], ogAST.PrimSubstring):
                stmts.extend(list_stmt)
                decls.extend(list_local)
                stmts.append('unsigned int ' + loop['var'] + '_idx;')
                stmts.append('{} {};'.format(type_name(loop['type']), loop['var']))
                stmts.append('for({it}_idx = min_range_{var_counter}; {it}_idx <= max_range_{var_counter}; {it}_idx++)'.format(it=loop['var'], var_counter=VAR_COUNTER))
                stmts.append('{')
                stmts.append('{it} = {var}.arr[{it}_idx];'.format(it=loop['var'], var=list_str))
            elif basic_type.Min == basic_type.Max:
                stmts.extend(list_stmt)
                decls.extend(list_local)
                stmts.append('unsigned int ' + loop['var'] + '_idx;')
                stmts.append('{} {};'.format(type_name(loop['type']), loop['var']))
                stmts.append('for({it}_idx = 0; {it}_idx < {length}; {it}_idx++)'.format(it=loop['var'], length=basic_type.Min))
                stmts.append('{')
                stmts.append('{it} = {var}.arr[{it}_idx];'.format(it=loop['var'], var=list_str))
            else:
                stmts.extend(list_stmt)
                decls.extend(list_local)
                stmts.append('unsigned int ' + loop['var'] + '_idx;')
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
    LOCAL_VAR.clear()
    LOCAL_VAR.update(local_scope)
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
    empty_transition = all(isinstance(act, ogAST.TaskInformalText) for act in tr.actions)
    for action in tr.actions:
        action_stmts, action_decls = generate(action)
        stmts.extend(action_stmts)
        decls.extend(action_decls)
        if isinstance(action, ogAST.Label):
            break
    else:
        if tr.terminator:
            empty_transition = False
            stmts.extend(traceability(tr.terminator))
            if tr.terminator.label:
                stmts.append('{label}:'.format(
                    label=tr.terminator.label.inputString))
            if tr.terminator.kind == 'next_state':
                if tr.terminator.inputString.strip() != '-':
                    stmts.append(u'trId = ' + unicode(tr.terminator.next_id) + u';')
                    if tr.terminator.next_id == -1:
                        stmts.append(u'{ctxt}.state = {nextState};'.format(ctxt=LPREFIX, nextState=tr.terminator.inputString.lower()))
                else:
                    if any(next_id for next_id in tr.terminator.candidate_id.viewkeys()if next_id != -1):
                        stmts.append('switch ({}.state)'.format(LPREFIX))
                        stmts.append('{')
                        for nid, sta in tr.terminator.candidate_id.viewitems():
                            if nid != -1:
                                for each in sta:
                                    stmts.append(u'case {} :'.format(each))
                                    stmts.append(u'{{' u'trId = {};'.format(nid))
                                    stmts.append(u'break;')
                                    stmts.append(u'}')
                        stmts.extend(['default:','{','trId = -1;','break;','}','}'])
                    else:
                        stmts.append('trId = -1;')
                stmts.append('goto next_transition;')
            elif tr.terminator.kind == 'join':
                stmts.append(u'goto {label};'.format(
                    label=tr.terminator.inputString))
            elif tr.terminator.kind == 'stop':
                pass
                # TODO
            elif tr.terminator.kind == 'return':
                return_string = ''
                if tr.terminator.next_id == -1:
                    if tr.terminator.return_expr:
                        return_stmt, return_string, return_decls = expression(tr.terminator.return_expr)
                        stmts.extend(return_stmts)
                        decls.extend(return_decls)
                    stmts.append('return{};'.format(' ' + return_string if return_string else ''))
                else:
                    stmts.append('trId = ' + str(tr.terminator.next_id) + ';')
                    stmts.append('goto next_transition;')
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
    var = find_var(prim.value[0])
    if prim.value[0] in LOCAL_OUT_PARS:
        string = u'(*{name})'.format(name=prim.value[0])
    elif not var or is_local(var):
        string = u'{name}'.format(name=prim.value[0])
    else:
        string = u'{lp}.{name}'.format(lp=LPREFIX, name=prim.value[0])

    return [], unicode(string.lower()), []


@expression.register(ogAST.PrimCall)
def _prim_call(prim):
    global math_include
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
            ret_string = 'abs({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'ceil':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'ceil({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'cos':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'cos({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'fix':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = '(int)({})'.format(param_string)
        ret_decls.extend(param_decls)
    elif function_name == 'float':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = '(float)({})'.format(param_string)
        ret_decls.extend(param_decls)
    elif function_name == 'floor':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'floor({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'length':
        # Length of sequence of: take only the first parameter
        exp = params[0]
        exp_type = find_basic_type(exp.exprType)
        min_length = getattr(exp_type, 'Min', None)
        max_length = getattr(exp_type, 'Max', None)
        if min_length is None or max_length is None:
            error = '{} is not a SEQUENCE OF'.format(
                    exp.inputString)
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
        math_include = True
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
        ret_string += ('{sort}_Kind({e})'
                       .format(sort=exp_typename,
                               e=param_str))
    elif function_name == 'round':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'roundf({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'sin':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'sinf({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'sqrt':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'sqrt({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    elif function_name == 'trunc':
        param_stmts, param_string, param_decls = expression(params[0])
        ret_stmts.extend(param_stmts)
        ret_string = 'trunc({})'.format(param_string)
        ret_decls.extend(param_decls)
        math_include = True
    else:
        ret_string = function_name + '('
        list_of_params = []
        for param in params:
            list_of_params.append(expression(param))
        ret_string += ', '.join(list_of_params)
        ret_string += ')'
    return ret_stmts, ret_string, ret_decls

@expression.register(ogAST.PrimIndex)
def _prim_index(prim):
    stmts, string, local_decl = [], '', []

    receiver = prim.value[0]

    receiver_stms, reciver_string, receiver_decl = expression(receiver)
    string = reciver_string
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

    return stmts, unicode(string), local_decl



def _prim_substring(prim):
    ret_stmts = []
    ret_string = []
    ret_decls = []

    base = prim.value[0]

    expression_type = find_basic_type(base)
    if expression_type == "OctetStringType":
        base_stmts, base_string, base_decls = expression(base)
        ret_stmts.extend(base_stmts)
        ret_decls.extend(base_decls)
        r1_stmts, r1_string, r1_local = expression(prim.value[1]['substring'][0])
        r2_stmts, r2_string, r2_local = expression(prim.value[1]['substring'][1])
        if unicode.isnumeric(r1_string) and unicode.isnumeric(r2_string):
            ret_decls.extend(['char var' + tmp_var_id + '[' + (int(r2_string) - int(r1_string) + 1) + '];'])
        else:
            ret_decls.extend(['char * var' + tmp_var_id + ';'])
            ret_stmts.extend(['var' + tmp_var_id + '= malloc(' + r2_string + ' - ' + r1_string + ' + 1];'])
        ret_stmts.extend(['{'])
        ret_stmts.extend(['unsigned int memcpy_counter;'])
        ret_stmts.extend(['for(memcpy_counter = 0; memcpy_counter < ' + r2_string + ' - ' + r1_string + ' + 1) memcpy_counter++)'])
        ret_stmts.extend(['{'])
        ret_stmts.extend(['var' + tmp_var_id + '[memcpy_counter] = ' + base_string + '[' + r1_string + ' + memcpy_counter];'])
        ret_stmts.extend(['}'])
        ret_stmts.extend(['}'])
    else:
        error = expression_type
        LOG.error(expression_type)
        raise TypeError(expression_type)

    return ret_stmts, ret_string, ret_decls


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
        string = ('{sort}_{field_name}_get({string})'.format(sort=type_name(receiver.exprType), field_name=field_name, string=string))
    else:
        # Sequence: we must get the right casing of the field
        for field_case in receiver_bty.Children:
            if field_case.lower() == field_name.lower():
                break
        else:
            field_case = field_name
        string += '.' + field_case

    return stmts, unicode(string), local_decl


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
    return code, unicode(string), local_decl


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
    return code, unicode(string), local_decl


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
    basic = lbty.kind in ('IntegerType', 'Integer32Type', 'BooleanType', 'EnumeratedType', 'ChoiceEnumeratedType')
    if basic:
        string = u'({left} {op} {right})'.format(left=left_string, op=operand, right=right_string)
    else:
        if asn1_type in TYPES:
            if isinstance(expr.left, ogAST.PrimSelector):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(u'{ty} selector_{var_counter};'.format(ty=actual_type, var_counter=VAR_COUNTER))
                stmts.append(u'selector_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
                left_string = u'selector_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif not (isinstance(expr.left, ogAST.PrimVariable) or isinstance(expr.left, ogAST.ExprAnd) or isinstance(expr.left, ogAST.ExprOr) or isinstance(expr.left, ogAST.ExprXor) or isinstance(expr.left, ogAST.ExprImplies) or isinstance(expr.left, ogAST.ExprNot)):
                raise NotImplementedError(str(type(expr.left)) + ' in left part of comparison')
            if isinstance(expr.right, ogAST.PrimReal):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(u'{ty} constant_{var_counter} = {cst};'.format(ty=actual_type, var_counter=VAR_COUNTER, cst=right_string))
                right_string = u'constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif isinstance(expr.right, ogAST.PrimStringLiteral):
                VAR_COUNTER = VAR_COUNTER + 1
                decls.append(u'{ty} constant_{var_counter} = ({ty}){{{size}, {cst}}};'.format(ty=actual_type, var_counter=VAR_COUNTER, size=rbty.Max, cst=array_content(expr.right, right_string, rbty)))
                right_string = u'constant_{var_counter}'.format(var_counter=VAR_COUNTER)
            elif not (isinstance(expr.right, ogAST.PrimVariable)):
                raise NotImplementedError(str(type(expr.right)) + ' in right part of comparison')
            string = u'{sort}_Equal(&{left}, &{right})'.format(sort=actual_type, left=left_string, right=right_string)
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
                decls.append(u'{ty} constant_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=left_type, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
                right_string = u'constant_{var_counter}'.format(var_counter=VAR_COUNTER)
                string = u'{left_type}_Equal(&{ls}, &{rs})'.format(left_type=left_type, ls=left_string, rs=right_string)
            else:
                string = u"({left}) {op} ({right})".format(left=left_string, op=operand, right=right_string)
        if isinstance(expr, ogAST.ExprNeq):
            string = u'! {}'.format(string)
    return stmts, unicode(string), decls


@expression.register(ogAST.ExprAssign)
def _assign_expression(expr):
    LOG.debug(u'Expanding assignment')
    stmts, decls = [], []
    strings = []
    left_stmts, left_string, left_decls = expression(expr.left)
    variable_name = left_string[len(LPREFIX)+1:] if left_string.startswith(LPREFIX) else left_string
    basic_left = find_basic_type(expr.left.exprType)
    global LEFT_TYPE
    global VAR_COUNTER
    if variable_name in VARIABLES:
        LEFT_TYPE = type_name(VARIABLES[variable_name][0])
    else:
        LEFT_TYPE = u'asn1Scc' + basic_left.__name__[:-5].replace('-','_')
    right_stmts, right_string, right_decls = expression(expr.right)
    # If left side is a string/seqOf and right side is a substring, we must
    # assign the .arr and .Length parts properly
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    decls.extend(left_decls)
    decls.extend(right_decls)
    if basic_left.kind in ('SequenceOfType', 'OctetStringType'):
        rlen = "{}.nCount".format(right_string)
        if isinstance(expr.right, ogAST.PrimSubstring):
            rlen = u'max_range_{var_counter} - min_range_{var_counter} + 1'.format(var_counter=VAR_COUNTER)
            decls.append(u'unsigned int var_counter_{var_counter};'.format(var_counter=VAR_COUNTER))
            stmts.append(u'{')
            stmts.append(u'for(var_counter_{var_counter} = 0; var_counter_{var_counter} <= max_range_{var_counter} - min_range_{var_counter}; var_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, rvar=right_string))
            stmts.append(u'{')
            stmts.append(u'{lvar}.arr[var_counter_{var_counter}] =  {rvar}.arr[var_counter_{var_counter} + min_range_{var_counter}];'.format(lvar=left_string, rvar=right_string, var_counter=VAR_COUNTER))
            stmts.append('}')
            stmts.append('}')
        elif isinstance(expr.right, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            VAR_COUNTER = VAR_COUNTER + 1
            decls.append(u'{ty} assign_var_{var_counter} = {init};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, init=array_content(expr.right, right_string, basic_left)))
            strings.append(u"{lvar} = assign_var_{var_counter};".format(lvar=left_string, var_counter=VAR_COUNTER))
            rlen = None
        elif isinstance(expr.right, ogAST.ExprNot) and isinstance(expr.right.expr, ogAST.PrimSequenceOf):
            strings.append(u"{ls} = ({ty}) {rs};".format(ls=left_string, ty=LEFT_TYPE, rs=right_string))
            rlen = None
        else:
            # Right part is a variable
            strings.append(u"{} = {};".format(left_string, right_string))
            rlen = None
        if rlen and basic_left.Min != basic_left.Max:
            strings.append(u"{lvar}.nCount= {rlen};".format(lvar=left_string, rlen=rlen))
    else:
        if isinstance(expr.right, ogAST.PrimSequence):
            VAR_COUNTER = VAR_COUNTER + 1
            decls.append(u'{ty} constant_{var_counter} = {init};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, init=right_string))
            stmts.append(u'{ls} = constant_{var_counter};'.format(ls=left_string, var_counter=VAR_COUNTER))
        else:
            strings.append(u"{} = {};".format(left_string, right_string))
    stmts.extend(strings)
    LOG.debug(u'Expanded assignment')
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
        if expr.right.is_raw:
            raise NotImplementedError('Logical operator applied on bit string')
        else:
            if not isinstance(expr.left, ogAST.PrimVariable):
                raise NotImplementedError(str(type(expr.left)))
            global VAR_COUNTER
            VAR_COUNTER = VAR_COUNTER + 1
            variable_name = left_string[len(LPREFIX)+1:] if left_string.startswith(LPREFIX) else left_string
            decls.append(u'{ty} expr_{var_counter};'.format(ty=type_name(VARIABLES[variable_name][0]), var_counter=VAR_COUNTER))
            decls.append(u'unsigned int expr_counter_{var_counter};'.format(var_counter=VAR_COUNTER))
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
    return stmts, unicode(string), decls


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
    if bty_outer.kind != 'BooleanType':
        if bty_outer.Min == bty_outer.Max:
            size_expr = bty_outer.Max;
        elif bty_inner.Min == bty_inner.Max:
            size_expr = '{}'.format(bty_inner.Min)
        else:
            size_expr = '{}.nCount'.format(expr_str)
        if isinstance(expr.expr, ogAST.PrimSequenceOf):
            string = array_content(expr.expr, expr_str, bty_outer)
        elif isinstance(expr.expr, ogAST.PrimVariable):
            global VAR_COUNTER
            VAR_COUNTER = VAR_COUNTER + 1
            decls.append(u'asn1Scc{ty} not_{var_counter};'.format(ty=bty_outer.__name__[:-5].replace('-','_'), var_counter=VAR_COUNTER))
            decls.append(u'unsigned int not_counter_{var_counter};'.format(var_counter=VAR_COUNTER))
            stmts.append(u'{')
            stmts.append(u'for(not_counter_{var_counter} = 0; not_counter_{var_counter} < {size_expr}; not_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size_expr=size_expr))
            stmts.append(u'{')
            stmts.append(u'not_{var_counter}.arr[not_counter_{var_counter}] = !{right_var}.arr[not_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, right_var=expr_str))
            stmts.append(u'}')
            if bty_outer.Min != bty_outer.Max:
                stmts.append(u'not_{var_counter}.nCount = {right_var}.nCount;'.format(var_counter=VAR_COUNTER, right_var=expr_str))
            stmts.append(u'}')
            string = (u'not_{var_counter}'.format(var_counter=VAR_COUNTER))
        else:
            raise NotImplementedError(u'Not of a ' + str(type(expr.expr)))
            string = u'{{{{! {expr_str} }}, {size_expr} }})'.format(expr_str=expr_str.replace(',',',!'), size_expr=size_expr);
    else:
        string = u'!{expr}'.format(expr=expr_str.replace(',',',!'))

    return stmts, unicode(string), decls


@expression.register(ogAST.ExprNeg)
def _neg_expression(expr):
    ''' Generate the code for a negative expression '''
    code, local_decl = [], []
    expr_stmts, expr_str, expr_local = expression(expr.expr)
    string = u'(-{expr})'.format( expr=expr_str)
    code.extend(expr_stmts)
    local_decl.extend(expr_local)
    return code, unicode(string), local_decl


@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    stmts, string, decls = [], '', []
    global LEFT_TYPE
    global VAR_COUNTER
    global LOCAL_VARIABLE_TYPES
    rbty = find_basic_type(expr.right.exprType)
    lbty = find_basic_type(expr.left.exprType)
#    stmts.append(str(type(expr.left)) + ' ' + str(type(expr.right)))
    stmts.append('{')
    if (isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimSequenceOf)):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        decls.append(u'{ty} right_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
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
    elif isinstance(expr.left, ogAST.PrimSequenceOf) and isinstance(expr.right, ogAST.PrimSequenceOf):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE
        stmts.append(u'memcpy_temp_{var_counter}.arr[0] = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'memcpy_temp_{var_counter}.arr[1] = {rs};'.format(var_counter=VAR_COUNTER, rs=right_string))
        stmts.append(u'memcpy_temp_{var_counter}.nCount = 2;'.format(var_counter=VAR_COUNTER))
        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimVariable) and isinstance(expr.right, ogAST.PrimSequenceOf):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        decls.append(u'{ty} right_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
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
    elif isinstance(expr.left, ogAST.PrimVariable) and isinstance(expr.right, ogAST.PrimVariable):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
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
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE
        decls.append(u'{ty} constant_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
        #First copy left part in the result
        stmts.append(u'memcpy_temp_{var_counter} = {ls};'.format(var_counter=VAR_COUNTER, ls=left_string))
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=rbty.Max))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = constant_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {rsize};'.format(var_counter=VAR_COUNTER, rsize=rbty.Max))
        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimVariable):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
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
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
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
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        decls.append(u'{ty} constant_{var_counter} = {{{size}, {{{init}}}}};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER, size=rbty.Max, init=right_string))
        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < (max_range_{var_counter1} - min_range_{var_counter1}) + 1; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = {ls}.arr[min_range_{var_counter1} + memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1, ls=left_string))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount = (max_range_{var_counter1} - min_range_{var_counter1} + 1);'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} < {right_size}; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = constant_{var_counter}.arr[memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += {right_size};'.format(var_counter=VAR_COUNTER, right_size=rbty.Max))
        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif isinstance(expr.left, ogAST.PrimSubstring) and isinstance(expr.right, ogAST.PrimSubstring):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
        decls.append(u'{ty} memcpy_temp_{var_counter};'.format(ty=LEFT_TYPE, var_counter=VAR_COUNTER))
        LOCAL_VARIABLE_TYPES[u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)] = LEFT_TYPE

        #First copy left part in the result
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} <= (max_range_{var_counter} - min_range_{var_counter}) + 1; memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_counter_{var_counter}] = {ls}.arr[min_range_{var_counter} + memcpy_counter_{var_counter}];'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1, ls=left_string))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount = (max_range_{var_counter} - min_range_{var_counter} + 1);'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))

        #Then append the right part
        stmts.append(u'for(memcpy_counter_{var_counter} = 0; memcpy_counter_{var_counter} <= (max_range_{var_counter1} - min_range_{var_counter1} + 1); memcpy_counter_{var_counter}++)'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))
        stmts.append(u'{')
        stmts.append(u'memcpy_temp_{var_counter}.arr[memcpy_temp_{var_counter}.nCount + memcpy_counter_{var_counter}] = {rs}.arr[memcpy_counter_{var_counter} + min_range_{var_counter1}];'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1, rs=right_string))
        stmts.append(u'}')
        stmts.append(u'memcpy_temp_{var_counter}.nCount += (max_range_{var_counter1} - min_range_{var_counter1} + 1);'.format(var_counter=VAR_COUNTER, var_counter1=VAR_COUNTER-1))
        string = u'memcpy_temp_{var_counter}'.format(var_counter=VAR_COUNTER)
    elif (isinstance(expr.left, ogAST.ExprAppend) and isinstance(expr.right, ogAST.PrimConstant)):
        LOG.debug(str(type(expr.left)) + str(type(expr.right)))
        right_stmts, right_string, right_decls = expression(expr.right)
        stmts.extend(right_stmts)
        decls.extend(right_decls)
        left_stmts, left_string, left_decls = expression(expr.left)
        stmts.extend(left_stmts)
        decls.extend(left_decls)
        VAR_COUNTER = VAR_COUNTER + 1;
        decls.append(u'unsigned int memcpy_counter_{var_counter} = 0;'.format(var_counter=VAR_COUNTER))
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
    else:
        raise NotImplementedError(str(type(expr.left)) + str(type(expr.right)))
    stmts.append(u'}')
    return stmts, unicode(string), decls


@expression.register(ogAST.ExprIn)
def _expr_in(expr):
    ''' IN expressions: check if item is in a SEQUENCE OF '''
    # Check if item is in a SEQUENCE OF
    # Temporary variable needed to hold the test result
    global VAR_COUNTER
    VAR_COUNTER = VAR_COUNTER + 1
    string = 'tmp{}'.format(expr.tmpVar)
    stmts = []
    decls = ['_Bool {var} = false;'.format(var=string)]
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    decls.extend(left_local)
    decls.extend(right_local)
    left_type = find_basic_type(expr.left.exprType)
    if isinstance(expr.left, ogAST.PrimSubstring):
        NotImplementedError('Looking for substring in string')
    else:
        len_str = u'{}.nCount'.format(left_str)
        left_str += u'.arr'
    decls.append(u'unsigned int for_{var_counter};'.format(var_counter=VAR_COUNTER))
    if left_type.Min != left_type.Max:
        stmts.append(u'for(for_{var_counter} = 0; for_{var_counter} < {ls}; for_{var_counter}++)'.format(var_counter=VAR_COUNTER, ls=len_str))
    else:
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
    return stmts, unicode(string), decls


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    enumerant = primary.value[0].replace('_', '-').lower()
    basic = find_basic_type(primary.exprType)
    for each in basic.EnumValues:
        if each.lower() == enumerant:
            break
    prefix = type_name(basic)
    string = (prefix + basic.EnumValues[each].EnumID)
    return [], unicode(string), []


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    enumerant = primary.value[0].replace('_', '-').lower()
    for each in primary.exprType.EnumValues:
        if each.lower() == enumerant:
            break
    string = primary.exprType.EnumValues[each].EnumID
    return [], unicode(string), []


@expression.register(ogAST.PrimInteger)
@expression.register(ogAST.PrimReal)
def _integer(primary):
    ''' Generate code for a raw numerical value  '''
    string = primary.value[0]
    return [], unicode(string), []


@expression.register(ogAST.PrimBoolean)
def _boolean(primary):
    ''' Generate code for a raw boolean value  '''
    string = primary.value[0]
    return [], unicode(string.lower()), []


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    string = u'{}_Init()'.format(type_name(primary.exprType))
    return [], unicode(string), []


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    basic_type = find_basic_type(primary.exprType)
    # If user put a literal string to fill an Octet string,
    # then convert the string to an array of unsigned_8 integers
    # as expected by the Ada type corresponding to Octet String
    unsigned_8 = [str(ord(val)) for val in primary.value[1:-1]]

    string = u', '.join(unsigned_8)
    return [], unicode(string), []


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    return [], unicode(primary.value[0]), []


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
    if isinstance(cond.value['then'], ogAST.PrimStringLiteral):
        then_str = u'({tmpTyp}) {{{size}, {{{then_str}}}}}'.format(tmpTyp=tmp_type, then_str=then_str, size=len((cond.value['then'].value))-2)
        else_str = u'({tmpTyp}) {{{size}, {{{else_str}}}}}'.format(tmpTyp=tmp_type, else_str=else_str, size=len((cond.value['else'].value))-2)
    stmts.append(u'if ({if_str})'.format(if_str=if_str))
    stmts.append(u'{')
    stmts.append(u'tmp{idx} = {then_str};'.format(idx=cond.value['tmpVar'], then_str=then_str))
    stmts.append(u'}')
    stmts.append('else')
    stmts.append(u'{')
    stmts.append(u'tmp{idx} = {else_str};'.format(idx=cond.value['tmpVar'], else_str=else_str))
    stmts.append(u'}')
    string = u'tmp{idx}'.format(idx=cond.value['tmpVar'])
    return stmts, unicode(string), local_decl


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Return C string for an ASN.1 SEQUENCE '''
    stmts, local_decl = [], []
    string = u"({}) {{".format(type_name(seq.exprType))
    sep = ''
    type_children = find_basic_type(seq.exprType).Children
    optional_fields = {field.lower().replace('-', '_'): {'present': False,'ref': (field, val)} for field, val in type_children.viewitems() if val.Optional == 'True'}
    present_fields = []
    absent_fields = []
    for elem, value in seq.value.viewitems():
        # Set the type of the field - easy thanks to ASN.1 flattened AST
        delem = elem.replace('_', '-')
        for each in type_children:
            if each.lower() == delem.lower():
                elem_spec = type_children[each]
                break
        elem_specty = elem_spec.type
        value_stmts, value_str, local_var = expression(value)
        if isinstance(value, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            value_str = array_content(value, value_str, find_basic_type(elem_specty))
        elif isinstance(value, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            value_str = array_content(value, value_str, find_basic_type(elem_specty))
        string += u"{}.{} = {}".format(sep, elem.lower(), value_str)
        if elem.lower() in optional_fields:
            # Set optional field presence
            optional_fields[elem.lower()]['present'] = True
        sep = u', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    # Process optional fields
    if optional_fields:
        absent_fields = ((fd_name, fd_data['ref']) for fd_name, fd_data in optional_fields.viewitems() if not fd_data['present'])
        for fd_name, fd_data in absent_fields:
            fd_type = fd_data[1].type
            if fd_type.kind == 'ReferenceType':
                value = u'{}_Init()'.format(type_name(fd_type))
            elif fd_type.kind == 'BooleanType':
                value = u'false'
            elif fd_type in ('IntegerType', 'RealType'):
                value = fd_type.Min
            string += u'{}.{} = {}'.format(sep, fd_name.lower(), value)
            sep = u', '
        string += u', .exist = {'
        sep = ''
        for fd_name, fd_data in optional_fields.viewitems():
            string += u'{} {}'.format(sep, '1' if fd_data['present'] else '0')
            sep = u', '
        string += u'}'

    string += '}'
    return stmts, unicode(string), local_decl


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Return C string for an ASN.1 SEQUENCE OF '''
    stmts, local_decl = [], []
    string = ''
    seqof_ty = seqof.exprType
    try:
        asn_type = find_basic_type(TYPES[seqof_ty.ReferencedTypeName].type)
        min_size, max_size = asn_type.Min, asn_type.Max
    except AttributeError:
        asn_type = None
        min_size, max_size = seqof_ty.Min, seqof_ty.Max
        if hasattr(seqof, 'expected_type'):
            asn_type = find_basic_type(TYPES[seqof.expected_type.ReferencedTypeName].type.type)
            try:
                min_size, max_size = asn_type.Min, asn_type.Max
            except AttributeError:
                pass
    tab = []
    for i in xrange(len(seqof.value)):
        temp = ''
        item_stmts, item_str, local_var = expression(seqof.value[i])
        if isinstance(seqof.value[i], (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            item_str = array_content(seqof.value[i], item_str, asn_type or find_basic_type(seqof.value[i].exprType))
        temp += item_str
        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        tab.append(temp)
    string += u', '.join(tab)
    return stmts, unicode(string), local_decl


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Return the c code for a CHOICE expression '''
    stmts, choice_str, local_decl = expression(choice.value['value'])
    if isinstance(choice.value['value'], (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
        choice_str = array_content(choice.value['value'], choice_str, find_basic_type(choice.value['value'].exprType))
        choice_str = u'({ty}) {cs}'.format(ty=u'asn1Scc' + find_basic_type(choice.value['value'].exprType).__name__[:-5], cs=choice_str)
    string = u'{cType}_{opt}_set({expr})'.format(cType=type_name(choice.exprType), opt=choice.value['choice'], expr=choice_str)
    return stmts, unicode(string), local_decl

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
    stmts.append(u'min_range_{var_counter} = {r1};'.format(var_counter=VAR_COUNTER, r1=r1_string))
    stmts.extend(r2_stmts)
    stmts.append(u'max_range_{var_counter} = {r2};'.format(var_counter=VAR_COUNTER, r2=r2_string))
    local_decl.extend(r1_local)
    local_decl.append(u'unsigned int min_range_{var_counter};'.format(var_counter=VAR_COUNTER))
    local_decl.extend(r2_local)
    local_decl.append(u'unsigned int max_range_{var_counter};'.format(var_counter=VAR_COUNTER))

    return stmts, unicode(string), local_decl



def array_content(prim, values, asnty):
    ''' String literal and SEQOF are given as a sequence of elements '''
    if asnty.Min != asnty.Max:
        length = len(prim.value)
        if isinstance(prim, ogAST.PrimStringLiteral):
            # Quotes are kept in string literals
            length -= 2
        # Reference type can vary -> there is a Length field
        rlen = u'{}'.format(length)
    else:
        rlen = u''
    if isinstance(prim, ogAST.PrimStringLiteral):
        df = '0'
    else:
        # Find a default value for the "others" field in case of SEQOF
        _, df, _ = expression(prim.value[0])
        if isinstance(prim.value[0], (ogAST.PrimSequenceOf,
                                      ogAST.PrimStringLiteral)):
            df = array_content(prim.value[0], df, asnty.type)
    if asnty.Min != asnty.Max:
        return u'{{{rlen},{{{values}}}}}'.format(rlen=rlen, values=values)
    else:
        return u'{{{values}}}'.format(values=values)


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


def is_local(var):
    ''' Check if a variable is in the global context or in a local scope
        Typically needed to select the right prefix to use '''
    return var in LOCAL_VAR.viewkeys()


def string_payload(prim, string):
    ''' Return the .arr part of a string, including range computed according
        to the length, if the string has a variable size '''
    if isinstance(prim, ogAST.PrimSubstring):
        return ''
    prim_basic = find_basic_type(prim.exprType)
    payload = ''
    if prim_basic.kind in ('SequenceOfType', 'OctetStringType'):
        if int(prim_basic.Min) != int(prim_basic.Max):
            payload = u'.arr(1..{}.Length)'.format(string)
        else:
            payload = u'.arr'
    return payload


def traceability(symbol):
    ''' Return a string with code-to-model traceability '''
    trace = [u'// {line}'.format(line=l) for l in
        symbol.trace().split('\n')]
    if hasattr(symbol, 'comment') and symbol.comment:
        trace.extend(traceability(symbol.comment))
    return trace


def type_name(a_type, use_prefix=True):
    ''' Check the type kind and return an C usable type name '''
    if a_type.kind == 'ReferenceType':
        return u'{}{}'.format('asn1Scc' if use_prefix else '', a_type.ReferencedTypeName.replace('-', '_'))
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
        return u'asn1Scc'
    else:
        raise NotImplementedError('Type name for {}'.format(a_type.kind))



def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    code = []
    string = ''
    local = []
    basic_type = find_basic_type(param.exprType) or {}
    type_kind = basic_type.kind
    global STDIO_INCLUDE
    global VAR_COUNTER
    STDIO_INCLUDE = True
    if isinstance(param, ogAST.ExprAppend):
        # Append: call Put_Line separately for each side of the expression
        st1, _, lcl1= write_statement(param.left, newline = False)
        st2, _, lcl2 = write_statement(param.right, newline = False)
        code.extend(st1)
        code.extend(st2)
        local.extend(lcl1)
        local.extend(lcl2)
    elif type_kind.endswith('StringType'):
        if isinstance(param, ogAST.PrimStringLiteral):
            # Raw string
            code.append(u'printf(\"{}\");'.format(param.value[1:-1].replace('"', "'")))
        else:
            code, string, local = expression(param)
            if type_kind == 'OctetStringType':
                # Octet string -> convert to Ada string
                sep = UNICODE_SEP
                last_it = u""
                if isinstance(param, ogAST.PrimSubstring):
                    code.append('{')
                    local.append(u'unsigned int write_{var_counter};'.format(var_counter=VAR_COUNTER))
                    if basic_type.Min == basic_type.Max:
                        code.append('for(write_{var_counter} = min_range_{var_counter}; write_{var_counter} <= max_range_{var_counter}; write_{var_counter}++)'.format(var_counter=VAR_COUNTER))
                    else:
                        code.append('for(write_{var_counter} = 0; write_{var_counter} < {le}.nCount; write_{var_counter}++)'.format(var_counter=VAR_COUNTER,le=string))
                    code.append('{')
                    code.append('printf(\"%c\", {st}.arr[write_{var_counter}]);'.format(st=string, var_counter=VAR_COUNTER))
                    code.append('}')
                    code.append('}')
                elif basic_type.Min == basic_type.Max:
                    VAR_COUNTER = VAR_COUNTER + 1
                    local.append(u'unsigned int write_{var_counter};'.format(var_counter=VAR_COUNTER))
                    code.append('for(write_{var_counter} = 0; write_{var_counter} < {size}; write_{var_counter}++)'.format(var_counter=VAR_COUNTER, size=basic_type.Max))
                    code.append('{')
                    code.append('printf(\"%c\", {st}.arr[write_{var_counter}]);'.format(st=string, var_counter=VAR_COUNTER))
                    code.append('}')
                else:
                    VAR_COUNTER = VAR_COUNTER + 1
                    local.append(u'unsigned int write_{var_counter};'.format(var_counter=VAR_COUNTER))
                    code.append('for(write_{var_counter} = 0; write_{var_counter} < {le}.nCount; write_{var_counter}++)'.format(var_counter=VAR_COUNTER,le=string))
                    code.append('{')
                    code.append('printf(\"%c\", {st}.arr[write_{var_counter}]);'.format(st=string, var_counter=VAR_COUNTER))
                    code.append('}')
            else:
                code.append(u'{')
                code.append(u'unsigned int tmp_counter = 0;')
                code.append(u'for(tmp_counter = 0; tmp_counter < {st}.nCount; tmp_counter++)'.format(st=string))
                code.append(u'{')
                code.append(u'printf(\"%c\", {}.arr[tmp_counter]);'.format(string))
                code.append(u'}')
                code.append(u'}')
    elif type_kind in ('IntegerType', 'RealType', 'BooleanType', 'Integer32Type'):
        code, string, local = expression(param)
        if type_kind in ('IntegerType', 'Integer32Type'):
            code.append(u'if((int)({st}) >= 0) printf(\" \");'.format(st=string))
            code.append('printf(\"%d\", {st});'.format(st=string))
        elif type_kind == 'BooleanType':
            code.append('printf({value} ? \"TRUE\" : \"FALSE\");'.format(value=string))
        elif type_kind == 'RealType':
            code.append('printf(\" %lf\", {st});'.format(st=string))
    else:
        error = (u'Unsupported parameter in write call ' + param.inputString)
        LOG.error(error)
        raise TypeError(error)
    if newline:
        code.append(u'printf(\"\\n\");')
    return code, string, local
