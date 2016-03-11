#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE - StringTemplate backend

    This module uses the StringTemplate library to ease writing new backends
    To use this module:
        import StgBackend as stg
        stg.prepare_model(ogAST.process) # give your process AST as input
        for each stg_file:
            stg.initialize_stg(simu=True/False, each)
            stg.generate(ogAST.process)


    Copyright (c) 2012-2015 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
from singledispatch import singledispatch

import ogAST
import Helper

try:
    import stringtemplate3
    stg = True
except ImportError:
    stg = False

LOG = logging.getLogger(__name__)

__all__ = ['generate']

# reference to the ASN.1 Data view and to the visible variables (in scope)
TYPES = None
VARIABLES = {}
LOCAL_VAR = {}
# List of output signals and procedures
OUT_SIGNALS = []
PROCEDURES = []

# Specify that the target is a shared library
SHARED_LIB = False

UNICODE_SEP = u'\u00dc'

# STG group file, avoid passing a parameter as it is a module-level shared var
STG = None

# Shortcut function to instantiate a STG template
new = lambda inst: STG.getInstanceOf(inst)

def initialize_stg(simu=False, stgfile='ada_body.st'):
    ''' Load the STG backend and set gobal STG pointer '''
    global STG
    global SHARED_LIB

    if not stg:
        LOG.error('Library missing. Use pip install stringtemplate3')
        return

    # Load the file containing a group of templates
    STG = stringtemplate3.StringTemplateGroup(file=open(stgfile))
    if not STG:
        LOG.error('Could not load StringTemplate group')
        return

    if simu:
        SHARED_LIB = True

def prepare_model(process):
    ''' Do some AST transformations: flatten model, etc. '''
    global TYPES
    TYPES = process.dataview
    del OUT_SIGNALS[:]
    del PROCEDURES[:]
    OUT_SIGNALS.extend(process.output_signals)
    PROCEDURES.extend(process.procedures)

    # In case model has nested states, flatten everything (in-place)
    Helper.flatten(process, sep=UNICODE_SEP)

    # Add an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    process.map_inp_states = Helper.map_input_state(process)

    VARIABLES.update(process.variables)

@singledispatch
def generate(*args, **kwargs):
    ''' Generate the code for an item of the AST '''
    raise TypeError('[StringTemplate backend] Unsupported AST construct')
    return [], []


# Processing of the AST
@generate.register(ogAST.Process)
def _process(process, **kwargs):
    ''' Generate the code for a complete process (AST Top level) '''
    assert stg and STG
    process_name = process.processName
    LOG.info('Generating code for process {}'.format(process.processName))

    # Get the template corresponding to a SDL PROCESS
    tpl = new("process")

    # Initialize array of strings containing all local declarations
    tpl['arrsDcl'], process_decl, process_vars = dcl(process, simu)

    # Set the list of SDL states
    tpl['states'] = (name for name in process.mapping.viewkeys()
                                  if not name.endswith(u'START'))

    # Set constants corresponding to substate start transitions
    constants = []
    for name, val in process.mapping.viewitems():
        if name.endswith(u'START') and name != u'START':
            const_template = new("constant")
            const_template['var'] = name
            const_template['val'] = str(val)
            constants.append(str(const_template))

    tpl['constants'] = constants

    try:
        tpl['asn1_mod'] = (dv.replace('-', '_') for dv in process.asn1Modules)
    except TypeError:
        pass # No ASN.1 module

    # Generate the the code of the procedures
    inner_procedures_decl = []
    inner_procedures_code = []
    for proc in process.content.inner_procedures:
        proc_code, proc_local = generate(proc)
        inner_procedure_decl.extend(proc_local)
        inner_procedures_code.extend(proc_code)

    # Generate the code for the process-level variable declarations
    tpl['pdecl'] = inner_procedure_decl
    tpl['pcode'] = inner_procedures_code


    # Generate the code for each input signal (provided interface) and timers
    pi_code = []
    for signal in process.input_signals + [
                        {'name': timer.lower()} for timer in process.timers]:
        sig_template = new('pi_signature')
        if signal.get('name', u'START') == u'START':
            continue
        sig_template['name'] = signal['name']
        # Add (optional) PI parameter (only one is possible in TASTE PI)
        if 'type' in signal:
            sig_template['param_name'] = signal.get('param_name')
            sig_template['param_sort'] = type_name(signal['type'])

        pi_template = new('input_signal')
        pi_template['header'] = str(sig_template)
        pi_template['name'] = signal['name']
        pi_template['process'] = process_name

        # For each input signal, define the possible transition based on the
        # current state.
        cases = []
        for state in process.mapping.viewkeys():
            if state.endswith(u'START'):
                continue
            case_template = new('case_state')
            case_template['name'] = state
            input_def = process.map_inp_state[signal['name']].get(state)
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
            ordered_exitlist = []
            for each in reversed(exitlist):
                if trans and all(each.startswith(trans_st)
                                 for trans_st in trans.possible_states):
                    ordered_exitlist.append(each)
            case_template['arrs_exitproc'] = ordered_exitlist

            if input_def:
                params_lst = []
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    assig_template = new('assign_param')
                    assig_template['local_var'] = inp
                    assig_template['param_name'] = param_name
                    params_lst.append(str(assig_template))
                case_template['arrs_param_assig'] = params_lst
                # Execute the correponding transition
                if input_def.transition:
                    case_template['transition'] = input_def.transition_id
            cases.append(str(case_template))
        pi_template['cases'] = cases

        # Generate the template amd add it to a list
        pi_code.append(str(pi_template))

    tpl['arrs_inp'] = pi_code

    # for the .ads file, generate the declaration of the required interfaces
    # output signals are the asynchronous RI - only one parameter
    required_interfaces = []
    for signal in process.output_signals:
        # TODO, pass the type and name of the parameter (for the Ads)
        ri_template = new("required_interface")
        ri_template['name'] = signal['name']
        ri_template['simu'] = simu
        required_interfaces.append(str(ri_template))

    tpl['arrs_async_ri'] = required_interfaces


    external_proc = []
    # Generate the declaration of the external procedures
    for proc in (proc for proc in process.procedures if proc.external):
        signature_template = new("ext_procedure_signature")
        signature_template['name'] = proc.inputString

        fpar = []
        for each in proc.fpar:
            fpar.append({'name': fpar.get('name'),
                         'sort': type_name(fpar.get('type'))})
        signature_template['fpar'] = fpar

        declaration_template = new("ext_procedure_declaration")
        declaration_template['header'] = str(signature_template)
        declaration_template['name'] = proc.inputString
        declaration_template['ctxt'] = process_name

        external_proc.append(str(declaration_template))

    tpl['ext_proc'] = external_proc

    # for the .ads file, generate the declaration of timers set/reset functions
    timer_decls, timer_defs = [], []
    for timer in process.timers:
        timer_decl_template = new("timer_declaration")
        timer_def_template = new("timer_definition")
        timer_decl_template['name'] = timer
        timer_def_template['name'] = timer
        timer_decl_template['ctxt'] = process_name
        timer_def_template['ctxt'] = process_name
        timer_decl_template['simu'] = simu
        timer_def_template['simu'] = simu
        timer_decls.append(str(timer_decl_template))
        timer_defs.append(str(timer_de_template))

    tpl['timer_decls'] = timer_decls
    tpl['timer_defs'] = timer_defs


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

    tpl['tr_locals'] = set(local_decl_transitions)
    tpl['flab_code'] = code_labels

    # Generate a loop that ends when a next state is reached
    # (there can be chained transition when entering a nested state)
    taste_template.append('while (trId /= -1) loop')

    # Generate the switch-case on the transition id
    taste_template.append('case trId is')

    tr_code = []
    for idx, val in enumerate(code_transitions):
        tr_template = new("transition_code")
        tr_template['idx'] = idx
        val = [u'{line}'.format(line=l) for l in val]
        tr_template['code'] = val
        tr_code.append(str(tr_template))

    tpl['tr_code'] = tr_code

    result = str(tpl).encode('latin1')

#   with open(process_name + '.adb', 'w') as ada_file:
#       ada_file.write(taste_template.encode('latin1'))
#
#   with open(process_name + '.ads', 'w') as ada_file:
#       ada_file.write(ads_template.encode('latin1'))

#   if simu:
#       with open(u'{}_interface.aadl'.format(process_name), 'w') as aadl:
#           aadl.write(u'\n'.join(minicv).encode('latin1'))


def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    code = []
    string = ''
    local = []
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
        if isinstance(param, ogAST.PrimStringLiteral):
            # Raw string
            code.append(u'Put("{}");'
                        .format(param.value[1:-1].replace('"', "'")))
        else:
            code, string, local = expression(param)
            if type_kind == 'OctetStringType':
                # Octet string -> convert to Ada string
                sep = UNICODE_SEP
                last_it = u""
                if isinstance(param, ogAST.PrimSubstring):
                    range_str = u"{}'Range".format(string)
                    iterator = u"i - {}'First + 1".format(string)
                elif basic_type.Min == basic_type.Max:
                    range_str = u"{}.Data'Range".format(string)
                    string += u".Data"
                    iterator = u"i"
                else:
                    range_str = u"1 .. {}.Length".format(string)
                    string += u".Data"
                    iterator = u"i"
                    last_it = u"({})".format(range_str)
                code.extend([u"for i in {} loop".format(range_str),
                             u"Put(Character'Val({st}(i)));"
                             .format(st=string, sep=sep, it=iterator),
                             u"end loop;"])
            else:
                code.append("Put({});".format(string))
    elif type_kind in ('IntegerType', 'RealType',
                       'BooleanType', 'Integer32Type'):
        code, string, local = expression(param)
        if type_kind in ('IntegerType', 'Integer32Type'):
            cast = "Asn1Int"
        elif type_kind == 'RealType':
            cast = 'Long_Float'
        elif type_kind == 'BooleanType':
            cast = 'Boolean'
        code.append(u"Put({cast}'Image({s}));".format(cast=cast, s=string))
    else:
        error = (u'Unsupported parameter in write call ' +
                param.inputString)
        LOG.error(error)
        raise TypeError(error)
    if newline:
        code.append(u"New_Line;")
    return code, string, local


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output, **kwargs):
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
            if not SHARED_LIB:
                code.append('RESET_{};'.format(p_id))
            else:
                code.append('RESET_{t}(New_String("{t}"));'.format(t=p_id))
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
            if not SHARED_LIB:
                # Use a temporary variable to store the timer value
                tmp_id = 'tmp' + str(out['tmpVars'][0])
                local_decl.append('{} : aliased asn1SccT_UInt32;'
                                  .format(tmp_id))
                code.append('{tmp} := {val};'.format(tmp=tmp_id, val=t_val))
                code.append("SET_{timer}({value}'access);"
                            .format(timer=p_id, value=tmp_id))
            else:
                code.append('SET_{t}(New_String("{t}"), {val});'
                            .format(t=p_id, val=t_val))
            continue
        proc, out_sig = None, None
        is_out_sig = False
        try:
            out_sig, = [sig for sig in OUT_SIGNALS
                        if sig['name'].lower() == signal_name.lower()]
            is_out_sig = True if SHARED_LIB else False
        except ValueError:
            # Not an output, try if it is an external or inner procedure
            try:
                proc, = [sig for sig in PROCEDURES
                            if sig.inputString.lower() == signal_name.lower()]
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
                p_code, p_id, p_local = expression(param)
                code.extend(p_code)
                local_decl.extend(p_local)
                # Create a temporary variable for input parameters only
                # (If needed, i.e. if argument is not a local variable)
                if param_direction == 'in' \
                        and (not (isinstance(param, ogAST.PrimVariable)
                        and p_id.startswith('l_'))
                        or isinstance(param, ogAST.PrimFPAR)):
                    tmp_id = 'tmp{}'.format(out['tmpVars'][idx])
                    local_decl.append('{tmp} : aliased {sort};'
                                      .format(tmp=tmp_id,
                                              sort=typename))
                    if isinstance(param,
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                        p_id = array_content(param, p_id,
                                             find_basic_type(param_type))
                    code.append('{} := {};'.format(tmp_id, p_id))
                    list_of_params.append("{}'access{}"
                                          .format(tmp_id,
                                                  ", {}'Size".format(tmp_id)
                                                     if is_out_sig else ""))
                else:
                    # Output parameters/local variables
                    list_of_params.append(u"{var}'access{shared}"
                                         .format(var=p_id,
                                                shared=", {}'Size".format(p_id)
                                                  if is_out_sig else ""))
            if list_of_params:
                code.append(u'{RI}({params});'
                            .format(RI=out['outputName'],
                                    params=', '.join(list_of_params)))
            else:
                if not SHARED_LIB:
                    code.append(u'{RI};'.format(RI=out['outputName']))
                else:
                    code.append(u'{RI}(New_String("{RI}"));'
                                .format(RI=out['outputName']))
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
                code.append(u'p{sep}{proc}({params});'.format(
                    sep=UNICODE_SEP,
                    proc=proc.inputString,
                    params=', '.join(list_of_params)))
            else:
                code.append(u'p{}{};'.format(UNICODE_SEP, proc.inputString))
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


@generate.register(ogAST.TaskInformalText)
def _task_informal_text(task, **kwargs):
    ''' Generate Ada comments for informal text '''
    code = []
    if task.comment:
        code.extend(traceability(task.comment))
    code.extend(['-- ' + text.replace('\n', '\n-- ') for text in task.elems])
    return code, []


@generate.register(ogAST.TaskForLoop)
def _task_forloop(task, **kwargs):
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
                start_stmt, start_str, start_local = expression(
                                                    loop['range']['start'])
                local_decl.extend(start_local)
                stmt.extend(start_stmt)
            if loop['range']['step'] == 1:
                start_str += '..'
            stop_stmt, stop_str, stop_local = expression(loop['range']['stop'])
            local_decl.extend(stop_local)
            stmt.extend(stop_stmt)
            if loop['range']['step'] == 1:
                if unicode.isnumeric(stop_str):
                    stop_str = unicode(int(stop_str) - 1)
                else:
                    stop_str = u'{} - 1'.format(stop_str)
                stmt.append(
                        u'for {it} in {start}{stop} loop'
                        .format(it=loop['var'], start=start_str, stop=stop_str))
            else:
                # Step is not directly supported in Ada, we need to use 'while'
                stmt.extend(['declare',
                             u'{it} : Integer := {start};'
                             .format(it=loop['var'],
                             start=start_str),
                             '',
                             'begin',
                             u'while {it} < {stop} loop'.format(it=loop['var'],
                                                               stop=stop_str)])
        else:
            # case of form: FOR x in SEQUENCE OF
            list_stmt, list_str, list_local = expression(loop['list'])
            basic_type = find_basic_type(loop['list'].exprType)
            list_payload = list_str + string_payload(loop['list'], list_str)
            if isinstance(loop['list'], ogAST.PrimSubstring) or \
                    basic_type.Min == basic_type.Max:
                range_str = u"{}'Range".format(list_payload)
            else:
                range_str = u"1 .. {}.Length".format(list_str)
            stmt.extend(list_stmt)
            local_decl.extend(list_local)
            stmt.extend(['declare',
                         '{} : {};'.format(loop['var'],
                                           type_name(loop['type'])),
                         '',
                         'begin',
                         'for {it}_idx in {rc} loop'.format(it=loop['var'],
                                                            rc=range_str),
                         '{it} := {var}({it}_idx);'.format(it=loop['var'],
                                                          var=list_payload)])
        try:
            code_trans, local_trans = generate(loop['transition'])
            if local_trans:
                stmt.append('declare')
                stmt.extend(set(local_trans))
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
    raise TypeError('Unsupported expression: ' + str(expr))
    return [], '', []


@expression.register(ogAST.PrimVariable)
def _primary_variable(prim):
    ''' Single variable reference '''
    sep = u'l_' if find_var(prim.value[0]) else u''

    ada_string = u'{sep}{name}'.format(sep=sep, name=prim.value[0])

    if prim.exprType.__name__ == 'for_range':
        # Ada iterator in FOR loops is an Integer - we must cast to 64 bits
        ada_string = u'Asn1Int({})'.format(ada_string)
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimCall)
def _prim_call(prim):
    stmts, ada_string, local_decl = [], '', []

    ident = prim.value[0].lower()
    params = prim.value[1]['procParams']

    if ident in ('abs', 'fix', 'float'):
        # Return absolute value of a number
        param_stmts, param_str, local_var = expression(params[0])
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += '{op}({param})'.format(
                param=param_str,
                op='abs' if ident == 'abs' else
                'Asn1Int' if ident == 'fix' else 'Asn1Real'
                if ident == 'float' else 'ERROR')
    elif ident == 'power':
        operands = [None, None]
        for idx, param in enumerate(params):
            stmt, operands[idx], local = expression(param)
            stmts.extend(stmt)
            local_decl.extend(local)
        ada_string += '{op[0]} ** Natural({op[1]})'.format(op=operands)
    elif ident == 'length':
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
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        if min_length == max_length \
                and not isinstance(exp, ogAST.PrimSubstring):
            ada_string += min_length
        else:
            if isinstance(exp, ogAST.PrimSubstring):
                range_str = u"{}'Length".format(param_str)
            else:
                range_str = u"{}.Length".format(param_str)
            ada_string += ('Asn1Int({})'.format(range_str))
    elif ident == 'present':
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
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += ('{sort}_Kind({e})'
                       .format(sort=exp_typename,
                               e=param_str))
    elif ident == 'num':
        # User wants to get an enumerated corresponding integer value
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp)
        local_decl.append('function num_{sort} is new Ada.Unchecked_Conversion'
                          '({sort}, Asn1Int);'.format(sort=exp_typename))
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += ('num_{sort}({p})'
                       .format(sort=exp_typename,
                               p=param_str))
    elif ident == 'floor':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Floor({p})".format(sort=exp_typename,
                                                 p=param_str)
    elif ident == 'ceil':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Ceiling({p})".format(sort=exp_typename,
                                                   p=param_str)
    elif ident == 'cos':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += "Math.Cos({})".format(param_str)
    elif ident == 'round':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Rounding({p})".format(sort=exp_typename,
                                                    p=param_str)
    elif ident == 'sin':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += "Math.Sin({})".format(param_str)
    elif ident == 'sqrt':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += "Math.Sqrt({})".format(param_str)
    elif ident == 'trunc':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Truncation({p})".format(sort=exp_typename,
                                                      p=param_str)
    else:
        ada_string += '('
        # Take all params and join them with commas
        list_of_params = []
        for param in params:
            param_stmt, param_str, local_var = (expression(param))
            list_of_params.append(param_str)
            stmts.extend(param_stmt)
            local_decl.extend(local_var)
        ada_string += ', '.join(list_of_params)
        ada_string += ')'

    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimIndex)
def _prim_index(prim):
    stmts, ada_string, local_decl = [], '', []

    receiver = prim.value[0]

    receiver_stms, reciver_string, receiver_decl = expression(receiver)
    ada_string = reciver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    idx_stmts, idx_string, idx_var = expression(prim.value[1]['index'][0])
    if unicode.isnumeric(idx_string):
        idx_string = int(idx_string) + 1
    else:
        idx_string = '1+Integer({idx})'.format(idx=idx_string)
    if not isinstance(receiver, ogAST.PrimSubstring):
        ada_string += '.Data'
    ada_string += '({idx})'.format(idx=idx_string)
    stmts.extend(idx_stmts)
    local_decl.extend(idx_var)

    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimSubstring)
def _prim_substring(prim):
    ''' Generate expression for SEQOF/OCT.STRING substrings, e.g. foo(1,2) '''
    stmts, ada_string, local_decl = [], '', []

    receiver = prim.value[0]

    receiver_stms, receiver_string, receiver_decl = expression(receiver)
    ada_string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    r1_stmts, r1_string, r1_local = expression(prim.value[1]['substring'][0])
    r2_stmts, r2_string, r2_local = expression(prim.value[1]['substring'][1])

    # Adding 1 because SDL starts indexes at 0, ASN1 Ada types at 1
    if unicode.isnumeric(r1_string):
        r1_string = unicode(int(r1_string) + 1)
    else:
        r1_string += ' + 1'
    if unicode.isnumeric(r2_string):
        r2_string = unicode(int(r2_string) + 1)
    else:
        r2_string += ' + 1'

    if not isinstance(receiver, ogAST.PrimSubstring):
        ada_string += '.Data'
    ada_string += '({r1}..{r2})'.format(r1=r1_string, r2=r2_string)
    stmts.extend(r1_stmts)
    stmts.extend(r2_stmts)
    local_decl.extend(r1_local)
    local_decl.extend(r2_local)

    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimSelector)
def _prim_selector(prim):
    ''' Selector (field access with '!' separation) '''
    stmts, ada_string, local_decl = [], '', []

    receiver = prim.value[0]
    field_name = prim.value[1]

    receiver_stms, receiver_string, receiver_decl = expression(receiver)
    ada_string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    receiver_bty = find_basic_type(receiver.exprType)

    if receiver_bty.kind == 'ChoiceType':
        ada_string = ('{sort}_{field_name}_get({ada_string})'
                    .format(sort=type_name(receiver.exprType),
                            field_name=field_name,
                            ada_string=ada_string))
    else:
        ada_string += '.' + field_name

    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.ExprPlus)
@expression.register(ogAST.ExprMul)
@expression.register(ogAST.ExprMinus)
@expression.register(ogAST.ExprGt)
@expression.register(ogAST.ExprGe)
@expression.register(ogAST.ExprLt)
@expression.register(ogAST.ExprLe)
@expression.register(ogAST.ExprDiv)
@expression.register(ogAST.ExprMod)
@expression.register(ogAST.ExprRem)
def _basic_operators(expr):
    ''' Expressions with two sides '''
    code, local_decl = [], []
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    ada_string = u'({left} {op} {right})'.format(
            left=left_str, op=expr.operand, right=right_str)
    code.extend(left_stmts)
    code.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, unicode(ada_string), local_decl


@expression.register(ogAST.ExprEq)
@expression.register(ogAST.ExprNeq)
def _equality(expr):
    code, left_str, local_decl = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    code.extend(right_stmts)
    local_decl.extend(right_local)
    asn1_type = getattr(expr.left.exprType, 'ReferencedTypeName', None)
    actual_type = type_name(expr.left.exprType)
    lbty = find_basic_type(expr.left.exprType)
    basic = lbty.kind in ('IntegerType', 'Integer32Type', 'BooleanType',
                          'RealType', 'EnumeratedType', 'ChoiceEnumeratedType')
    if basic:
        ada_string = u'({left} {op} {right})'.format(
                left=left_str, op=expr.operand, right=right_str)
    else:
        if asn1_type in TYPES:
            if isinstance(expr.right,
                          (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                right_str = array_content(expr.right, right_str, lbty)
            ada_string = u'{sort}_Equal({left}, {right})'.format(
                           sort=actual_type, left=left_str, right=right_str)
        else:
            # Raw types on both left and right.... use simple operator
            ada_string = u"({left}) {op} ({right})".format(left=left_str,
                    op=expr.operand, right=right_str)
        if isinstance(expr, ogAST.ExprNeq):
            ada_string = u'not {}'.format(ada_string)
    return code, unicode(ada_string), local_decl


@expression.register(ogAST.ExprAssign)
def _assign_expression(expr):
    ''' Assignment: almost the same a basic operators, except for strings '''
    code, local_decl = [], []
    strings = []
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    # If left side is a string/seqOf and right side is a substring, we must
    # assign the .Data and .Length parts properly
    basic_left = find_basic_type(expr.left.exprType)
    if basic_left.kind in ('SequenceOfType', 'OctetStringType'):
        rlen = "{}'Length".format(right_str)
        if isinstance(expr.right, ogAST.PrimSubstring):
            strings.append(u"{lvar}.Data(1..{rvar}'Length) := {rvar};"
                       .format(lvar=left_str, rvar=right_str))
        elif isinstance(expr.right, ogAST.ExprAppend):
            basic_right = find_basic_type(expr.right.exprType)
            rlen = append_size(expr.right)
            strings.append(u"{lvar}.Data(1..{lstr}) := {rvar};"
                           .format(lvar=left_str,
                                   rvar=right_str,
                                   lstr=rlen))
        elif isinstance(expr.right, (ogAST.PrimSequenceOf,
                                    ogAST.PrimStringLiteral)):
            strings.append(u"{lvar} := {value};"
                           .format(lvar=left_str,
                                   value=array_content(expr.right,
                                                       right_str,
                                                       basic_left)))
            rlen = None
        else:
            # Right part is a variable
            strings.append(u"{} := {};".format(left_str, right_str))
            rlen = None
        if rlen and basic_left.Min != basic_left.Max:
            strings.append(u"{lvar}.Length := {rlen};"
                           .format(lvar=left_str, rlen=rlen))
    else:
        strings.append(u"{} := {};".format(left_str, right_str))
    code.extend(left_stmts)
    code.extend(right_stmts)
    code.extend(strings)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, '', local_decl


@expression.register(ogAST.ExprOr)
@expression.register(ogAST.ExprAnd)
@expression.register(ogAST.ExprXor)
@expression.register(ogAST.ExprImplies)
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
            tmp_string = u'tmp{}'.format(expr.right.tmpVar)
            local_decl.append(u'{tmp} : aliased {sort};'.format(
                        tmp=tmp_string,
                        sort=type_name(expr.right.exprType)))
            code.append(u'{tmp} := {right};'.format(tmp=tmp_string,
                                                  right=right_str))
            right_str = tmp_string
            right_payload = right_str + '.Data'
        else:
            right_payload = right_str + string_payload(expr.right, right_str)
        left_payload = left_str + string_payload(expr.left, left_str)

        if isinstance(expr, ogAST.ExprImplies):
            ada_string = u'(Data => (({left} and {right}) or not {left}))'\
                .format(left=left_payload, right=right_payload)
        else:
            ada_string = u'(Data => ({left} {op} {right}))'.format(
                left=left_payload, op=expr.operand, right=right_payload)

    elif isinstance(expr, ogAST.ExprImplies):
        ada_string = u'(({left} and {right}) or not {left})'.format(
                                left=left_str,
                                right=right_str)

    else:
        ada_string = u'({left} {op}{short} {right})'.format(
                                left=left_str,
                                op=expr.operand,
                                short=expr.shortcircuit,
                                right=right_str)
    code.extend(left_stmts)
    code.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, unicode(ada_string), local_decl


@expression.register(ogAST.ExprNot)
def _not_expression(expr):
    ''' Generate the code for a not expression '''
    code, local_decl = [], []
    if isinstance(expr.expr, ogAST.PrimSequenceOf):
        # Raw sequence of boolean (e.g. not "{true, false}") -> flip values
        for each in expr.expr.value:
            each.value[0] = 'true' if each.value[0] == 'false' else 'false'
    expr_stmts, expr_str, expr_local = expression(expr.expr)

    bty_inner = find_basic_type(expr.expr.exprType)
    bty_outer = find_basic_type(expr.exprType)
    if bty_outer.kind != 'BooleanType':
        if bty_outer.Min == bty_outer.Max:
            size_expr = ''
        elif bty_inner.Min == bty_inner.Max:
            size_expr = ', Length => {}'.format(bty_inner.Min)
        else:
            size_expr = ', Length => {}.Length'.format(expr_str)
        if isinstance(expr.expr, ogAST.PrimSequenceOf):
            ada_string = array_content(expr.expr, expr_str, bty_outer)
        else:
            ada_string = u'(Data => (not {}.Data){})'.format(expr_str,
                                                             size_expr)
    else:
        ada_string = u'(not {expr})'.format(expr=expr_str)

    code.extend(expr_stmts)
    local_decl.extend(expr_local)
    return code, unicode(ada_string), local_decl


@expression.register(ogAST.ExprNeg)
def _neg_expression(expr):
    ''' Generate the code for a negative expression '''
    code, local_decl = [], []
    expr_stmts, expr_str, expr_local = expression(expr.expr)
    ada_string = u'(-{expr})'.format(op=expr.operand, expr=expr_str)
    code.extend(expr_stmts)
    local_decl.extend(expr_local)
    return code, unicode(ada_string), local_decl


@expression.register(ogAST.ExprAppend)
def _append(expr):
    ''' Generate code for the APPEND construct: a // b '''
    stmts, ada_string, local_decl = [], '', []
    left_stmts, left_str, left_local = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right)
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)

    left = '{}{}'.format(left_str, string_payload(expr.left, left_str) if
                    isinstance(expr.left, (ogAST.PrimVariable,
                                           ogAST.PrimConstant)) else '')
    right = '{}{}'.format(right_str, string_payload(expr.right, right_str) if
                    isinstance(expr.right, (ogAST.PrimVariable,
                                            ogAST.PrimConditional,
                                            ogAST.PrimConstant)) else '')

    ada_string = '(({}) & ({}))'.format(left, right)

    return stmts, unicode(ada_string), local_decl


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
    if isinstance(expr.left, ogAST.PrimSubstring):
        len_str = u"{}'Length".format(left_str)
    else:
        len_str = u"{}.Length".format(left_str)
        left_str += u".Data"
    if left_type.Min != left_type.Max:
        stmts.append("for elem in 1..{} loop".format(len_str))
    else:
        stmts.append("for elem in {}'Range loop".format(left_str))
    stmts.append("if {container}(elem) = {pattern} then".format
            (container=left_str, pattern=right_str))
    stmts.append("{} := True;".format(ada_string))
    stmts.append("end if;")
    stmts.append("exit in_loop_{tmp} when {tmp} = True;"
                  .format(tmp=ada_string))
    stmts.append("end loop in_loop_{};".format(ada_string))
    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary):
    ''' Generate code for an enumerated value '''
    enumerant = primary.value[0].replace('_', '-').lower()
    basic = find_basic_type(primary.exprType)
    for each in basic.EnumValues:
        if each.lower() == enumerant:
            break
    ada_string = (u'asn1Scc' + basic.EnumValues[each].EnumID)
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary):
    ''' Generate code for a choice determinant (enumerated) '''
    enumerant = primary.value[0].replace('_', '-').lower()
    for each in primary.exprType.EnumValues:
        if each.lower() == enumerant:
            break
    ada_string = primary.exprType.EnumValues[each].EnumID
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimInteger)
@expression.register(ogAST.PrimReal)
def _integer(primary):
    ''' Generate code for a raw numerical value  '''
    if float(primary.value[0]) < 0:
        # Parentesize negative integers for maintaining
        # the precedence in the generated code
        ada_string = u'({})'.format(primary.value[0])
    else:
        ada_string = primary.value[0]
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimBoolean)
def _boolean(primary):
    ''' Generate code for a raw boolean value  '''
    ada_string = primary.value[0]
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    ada_string = u'{}_Init'.format(type_name(primary.exprType))
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary):
    ''' Generate code for a string (Octet String) '''
    basic_type = find_basic_type(primary.exprType)
    # If user put a literal string to fill an Octet string,
    # then convert the string to an array of unsigned_8 integers
    # as expected by the Ada type corresponding to Octet String
    unsigned_8 = [str(ord(val)) for val in primary.value[1:-1]]

    ada_string = u', '.join(unsigned_8)
    return [], unicode(ada_string), []


@expression.register(ogAST.PrimConstant)
def _constant(primary):
    ''' Generate code for a reference to an ASN.1 constant '''
    return [], unicode(primary.value[0]), []


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    # TODO
    return [], u'', []


@expression.register(ogAST.PrimConditional)
def _conditional(cond):
    ''' Return string and statements for conditional expressions '''
    stmts = []

    tmp_type = type_name(cond.exprType)

    if tmp_type == 'String':
        then_str = cond.value['then'].value.replace("'", '"')
        else_str = cond.value['else'].value.replace("'", '"')
        lens = [len(then_str), len(else_str)]
        tmp_type = 'String(1 .. {})'.format(max(lens) - 2)
        # Ada require fixed-length strings, adjust with spaces
        if lens[0] < lens[1]:
            then_str = then_str[0:-1] + ' ' * (lens[1] - lens[0]) + '"'
        elif lens[1] < lens[0]:
            else_str = else_str[0:-1] + ' ' * (lens[0] - lens[1]) + '"'

    local_decl = ['tmp{idx} : {tmpType};'.format(idx=cond.value['tmpVar'],
                                                 tmpType=tmp_type)]
    if_stmts, if_str, if_local = expression(cond.value['if'])
    stmts.extend(if_stmts)
    local_decl.extend(if_local)
    if not tmp_type.startswith('String'):
        then_stmts, then_str, then_local = expression(cond.value['then'])
        else_stmts, else_str, else_local = expression(cond.value['else'])
        stmts.extend(then_stmts)
        stmts.extend(else_stmts)
        local_decl.extend(then_local)
        local_decl.extend(else_local)
    stmts.append(u'if {if_str} then'.format(if_str=if_str))
    stmts.append(u'tmp{idx} := {then_str};'.format(
                                                idx=cond.value['tmpVar'],
                                                then_str=then_str))
    stmts.append('else')
    stmts.append(u'tmp{idx} := {else_str};'.format(
                                                idx=cond.value['tmpVar'],
                                                else_str=else_str))
    stmts.append('end if;')
    ada_string = u'tmp{idx}'.format(idx=cond.value['tmpVar'])
    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimSequence)
def _sequence(seq):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    stmts, local_decl = [], []
    ada_string = u"{}'(".format(type_name(seq.exprType))
    sep = ''
    type_children = find_basic_type(seq.exprType).Children
    optional_fields = {field.lower().replace('-', '_'): {'present': False,
                                                         'ref': (field, val)}
                       for field, val in type_children.viewitems()
                       if val.Optional == 'True'}
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
            value_str = array_content(value, value_str,
                                      find_basic_type(elem_specty))
        ada_string += u"{} {} => {}".format(sep, elem, value_str)
        if elem.lower() in optional_fields:
            # Set optional field presence
            optional_fields[elem.lower()]['present'] = True
        sep = u', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    # Process optional fields
    if optional_fields:
        absent_fields = ((fd_name, fd_data['ref'])
                          for fd_name, fd_data in optional_fields.viewitems()
                          if not fd_data['present'])
        for fd_name, fd_data in absent_fields:
            fd_type = fd_data[1].type
            if fd_type.kind == 'ReferenceType':
                value = u'{}_Init'.format(type_name(fd_type))
            elif fd_type.kind == 'BooleanType':
                value = u'False'
            elif fd_type in ('IntegerType', 'RealType'):
                value = fd_type.Min
            ada_string += u'{}{} => {}'.format(sep, fd_name, value)
            sep = u', '
        ada_string += u', Exist => ('
        sep = ''
        for fd_name, fd_data in optional_fields.viewitems():
            ada_string += u'{}{} => {}'.format(sep, fd_name,
                                            '1' if fd_data['present'] else '0')
            sep = u', '
        ada_string += u')'

    ada_string += ')'
    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    stmts, local_decl = [], []
    seqof_ty = seqof.exprType
    try:
        asn_type = find_basic_type(TYPES[seqof_ty.ReferencedTypeName].type)
        min_size = asn_type.Min
        max_size = asn_type.Max
    except AttributeError:
        asn_type = None
        min_size, max_size = seqof_ty.Min, seqof_ty.Max
        if hasattr(seqof, 'expected_type'):
            asn_type = find_basic_type(
                    TYPES[seqof.expected_type.ReferencedTypeName].type.type)
            try:
                min_size, max_size = asn_type.Min, asn_type.Max
            except AttributeError:
                pass

    tab = []
    for i in xrange(len(seqof.value)):
        item_stmts, item_str, local_var = expression(seqof.value[i])
        if isinstance(seqof.value[i],
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            item_str = array_content(seqof.value[i], item_str, asn_type or
                    find_basic_type(seqof.value[i].exprType))
        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        tab.append(u'{i} => {value}'.format(i=i + 1, value=item_str))
    ada_string = u', '.join(tab)
    return stmts, unicode(ada_string), local_decl


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice):
    ''' Return the Ada code for a CHOICE expression '''
    stmts, choice_str, local_decl = expression(choice.value['value'])
    ada_string = u'{cType}_{opt}_set({expr})'.format(
                        cType=type_name(choice.exprType),
                        opt=choice.value['choice'],
                        expr=choice_str)
    return stmts, unicode(ada_string), local_decl


@generate.register(ogAST.Decision)
def _decision(dec, **kwargs):
    ''' generate the code for a decision '''
    code, local_decl = [], []
    if dec.kind == 'any':
        LOG.warning('Ada backend does not support the "ANY" statement')
        code.append('-- "DECISION ANY" statement was ignored')
        return code, local_decl
    elif dec.kind == 'informal_text':
        LOG.warning('Informal decision ignored')
        code.append('-- Informal decision was ignored: {}'
                    .format(dec.inputString))
        return code, local_decl
    question_type = dec.question.exprType
    actual_type = type_name(question_type)
    basic = find_basic_type(question_type).kind in ('IntegerType',
                          'Integer32Type', 'BooleanType',
                          'RealType', 'EnumeratedType', 'ChoiceEnumeratedType')
    # for ASN.1 types, declare a local variable
    # to hold the evaluation of the question
    if not basic:
        local_decl.append('tmp{idx} : aliased {actType};'.format(
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
                    if isinstance(a.constant, (ogAST.PrimSequenceOf,
                                               ogAST.PrimStringLiteral)):
                        ans_str = array_content(a.constant, ans_str,
                                                find_basic_type(question_type))
                    exp = u'{actType}_Equal(tmp{idx}, {ans})'.format(
                            actType=actual_type, idx=dec.tmpVar, ans=ans_str)
                    if a.openRangeOp == ogAST.ExprNeq:
                        exp = u'not {}'.format(exp)
                else:
                    exp = u'tmp{idx} {op} {ans}'.format(idx=dec.tmpVar,
                            op=a.openRangeOp.operand, ans=ans_str)
            else:
                exp = u'({q}) {op} {ans}'.format(q=q_str,
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
        elif a.kind == 'closed_range':
            cl0_stmts, cl0_str, cl0_decl = expression(a.closedRange[0])
            cl1_stmts, cl1_str, cl1_decl = expression(a.closedRange[1])
            code.extend(cl0_stmts)
            local_decl.extend(cl0_decl)
            code.extend(cl1_stmts)
            local_decl.extend(cl1_decl)
            code.append('{sep} {dec} >= {cl0} and {dec} <= {cl1} then'
                        .format(sep=sep, dec=q_str, cl0=cl0_str, cl1=cl1_str))
            if a.transition:
                stmt, tr_decl = generate(a.transition)
            else:
                stmt, tr_decl = ['null;'], []
            code.extend(stmt)
            local_decl.extend(tr_decl)
            sep = 'elsif '
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
def _label(lab, **kwargs):
    ''' Transition following labels are generated in a separate section
        for visibility reasons (see Ada scope)
    '''
    template = new("label")
    template['name'] = lab.inputString
    return str(template), []


@generate.register(ogAST.Transition)
def _transition(tr, **kwargs):
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
                    code.append(u'trId := ' +
                                unicode(tr.terminator.next_id) + u';')
                    if tr.terminator.next_id == -1:
                        code.append(u'state := {nextState};'.format(
                                nextState=tr.terminator.inputString))
                else:
                    if any(next_id
                           for next_id in tr.terminator.candidate_id.viewkeys()
                           if next_id != -1):
                        code.append('case state is')
                        for nid, sta in tr.terminator.candidate_id.viewitems():
                            if nid != -1:
                                for each in sta:
                                    code.extend([u'when {} =>'.format(each),
                                                 u'trId := {};'.format(nid)])

                        code.extend(['when others =>',
                                        'trId := -1;',
                                     'end case;'])
                    else:
                        code.append('trId := -1;')
                code.append('goto next_transition;')
            elif tr.terminator.kind == 'join':
                code.append(u'goto {label};'.format(
                    label=tr.terminator.inputString))
            elif tr.terminator.kind == 'stop':
                pass
                # TODO
            elif tr.terminator.kind == 'return':
                string = ''
                if tr.terminator.next_id == -1:
                    if tr.terminator.return_expr:
                        stmts, string, local = expression(
                                                    tr.terminator.return_expr)
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
def _floating_label(label, **kwargs):
    ''' Generate the code for a floating label (Ada label + transition) '''
    local_decl = []
    template = new("floating_label")
    template['traceability']= traceability(label)
    template['name'] = label.inputString
    if label.transition:
        template['transition'], local_decl = generate(label.transition)
    return str(template), local_decl


@generate.register(ogAST.Procedure)
def _inner_procedure(proc, **kwargs):
    ''' Generate the code for a procedure - does not support states '''
    code = []

    # Save variable scope (as local variables may shadow process variables)
    outer_scope = dict(VARIABLES)
    VARIABLES.update(proc.variables)
    # Also add procedure parameters in scope
    for var in proc.fpar:
        VARIABLES.update({var['name']: (var['type'], None)})

    signature_template = new("inner_procedure_signature")
    fpar = []
    for each in proc.fpar:
        fpar.append({'name': fpar.get('name'),
                     'direction': str(new("direction_out"))
                                  if fpar.get('direction') == 'out'
                                  else str(new("direction_in")),
                     'sort': type_name(fpar.get('type'))})

    signature_template['name'] = proc.inputString
    signature_template['external'] = proc.external
    signature_template['fpar'] = fpar

    declaration_template = new("inner_procedure_declaration")
    declaration_template['header'] = str(signature_template)
    declaration_template['name'] = proc.inputString
    declaration_template['external'] = proc.external

    local_decl = [str(declaration_template)]

    if not proc.external:
        # Generate the code for the procedure itself
        definition_template = new("inner_procedure_definition")
        definition_template['header'] = str(signature_template)
        definition_template['name'] = proc.inputString
        definition_template['dcl'], _ = dcl(proc, simu=False)

        # Look for labels in the diagram and transform them in floating labels
        Helper.inner_labels_to_floating(proc)
        if proc.content.start:
            start_code, other_decl = generate(proc.content.start.transition)
        definition_template['start'] = start_code
        # Generate code for the floating labels
        code_labels = []
        for label in proc.content.floating_labels:
            code_label, label_decl = generate(label)
            code_labels.extend(code_label)
            other_decl.extend(label_decl)
        definition_template['other_decl'] = set(other_decl)
        definition_template['labels'] = code_labels

    # Reset the scope to how it was prior to the procedure definition
    VARIABLES.clear()
    VARIABLES.update(outer_scope)

    return str(definition_template), local_decl


def dcl(entity, simu):
    ''' Generate the code to declare variables '''
    decl, arr_vars = [], []
    for var_name, (var_type, def_value) in entity.variables.viewitems():
        dcl_template = new("dcl")
        dcl_template['simu'] = simu
        if def_value:
            # Expression must be a ground expression, i.e. must not
            # require temporary variable to store computed result
            dst, dstr, dlocal = expression(def_value)
            varbty = find_basic_type(var_type)
            if varbty.kind in ('SequenceOfType', 'OctetStringType'):
                dstr = array_content(def_value, dstr, varbty)
            assert not dst and not dlocal, 'DCL: Expecting a ground expression'
        var = {'name': var_name, 'sort': type_name(var_type)}
        dcl_template['var'] = var
        arr_vars.append(var)
        dcl_template['def_expr'] = dstr if def_value else ''
        result.append(str(dcl_template))
    return decl, arr_vars


def string_payload(prim, ada_string):
    ''' Return the .Data part of a string, including range computed according
        to the length, if the string has a variable size '''
    if isinstance(prim, ogAST.PrimSubstring):
        return ''
    prim_basic = find_basic_type(prim.exprType)
    payload = ''
    if prim_basic.kind in ('SequenceOfType', 'OctetStringType'):
        if int(prim_basic.Min) != int(prim_basic.Max):
            payload = u'.Data(1..{}.Length)'.format(ada_string)
        else:
            payload = u'.Data'
    return payload


def array_content(prim, values, asnty):
    ''' String literal and SEQOF are given as a sequence of elements ;
    this function builds the Ada string needed to fit it in an ASN.1 array
    i.e. convert "1,2,3" to "Data => (1,2,3, others=>0), [Length => 3]"
    inputs: prim is of type PrimStringLiteral or PrimSequenceOf
    values is a string with the sequence of numbers as processed by expression
    asnty is the reference type of the string literal '''
    rtype = find_basic_type(prim.exprType)
    if asnty.Min != asnty.Max:
        # Reference type can vary -> there is a Length field
        rlen = u", Length => {}".format(rtype.Min)
    else:
        rlen = u""
    if isinstance(prim, ogAST.PrimStringLiteral):
        df = '0'
    else:
        # Find a default value for the "others" field in case of SEQOF
        _, df, _ = expression(prim.value[0])
        if isinstance(prim.value[0], (ogAST.PrimSequenceOf,
                                      ogAST.PrimStringLiteral)):
            df = array_content(prim.value[0], df, asnty)
    return u"(Data => ({}{}others => {}){})".format(values,
                                                    ', ' if values else '',
                                                    df, rlen)


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
                result += '{}.Length'.format(inner)
    return result


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


def type_name(a_type, use_prefix=True):
    ''' Check the type kind and return an Ada usable type name '''
    if a_type.kind == 'ReferenceType':
        return u'{}{}'.format('asn1Scc' if use_prefix else '',
                               a_type.ReferencedTypeName.replace('-', '_'))
    elif a_type.kind == 'BooleanType':
        return u'Boolean'
    elif a_type.kind.startswith('Integer'):
        return u'Asn1Int'
    elif a_type.kind == 'RealType':
        return u'Asn1Real'
    elif a_type.kind.endswith('StringType'):
        return u'String'
    elif a_type.kind == 'ChoiceEnumeratedType':
        return u'Asn1Int'
    else:
        raise NotImplementedError('Type name for {}'.format(a_type.kind))


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
                #print list(Helper.sorted_fields(current))
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
    template = new("comment")
    template['lines'] = symbol.trace().split('\n')
    result = [str(template)]
    if hasattr(symbol, 'comment') and symbol.comment:
        result.extend(traceability(symbol.comment))
    return result
