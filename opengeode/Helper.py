#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module provides helper functions typically used by backends:

        flatten(ast) : transform a model with nested states to a flat model
        rename_everything(ast, from_name, to_name) : rename symbols
        inner_labels_to_floating(process) : remove labels from transitions
        map_input_state(process) -> mapping: create a mapping
                                    input-state-transition
        sorted_fields(SEQ/CHOICE) : returns the ordered list of fields
                                    of an ASN.1 SEQUENCE or CHOICE type
        state_aggregations: enrich AST with state aggregation flags,
                            and return the list of substates of aggregations
        parallel_states: return a list of strings naming all parallel states
        statenames: return a list of properly-formatted state names
        rec_findstates: recursively find parallel/composite statenames
        update_full_statelist(process): set field full_statelist in process AST
        code_generation_preprocessing: to be called before generating code
        generate_asn1_datamodel: generate the _datamodel.asn file for a process

    Copyright (c) 2012-2022 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import operator
import logging
from itertools import chain
from collections import defaultdict

from functools import singledispatch

from . import ogAST

LOG = logging.getLogger(__name__)
DEFAULT_SEPARATOR='_0_'
ASN1SCC = 'asn1Scc'

__all__ = ['flatten', 'rename_everything', 'inner_labels_to_floating',
           'map_input_state', 'sorted_fields', 'state_aggregations',
           'parallel_states', 'statenames', 'rec_findstates',
           'generate_asn1_datamodel',
           'get_full_statelist', 'code_generation_preprocessing']


def statenames(context, sep=DEFAULT_SEPARATOR):
    ''' Return the list of states (just the names) of a given context
    Format the output by replacing unicode separator symbol with a dot '''
    # note: if model has been flattened, all contexts are already merged
    return (s.replace(sep, '.') for s in context.mapping.keys()
            if not s.endswith('START'))


def rec_findstates(context, prefix=''):
    ''' In case of state compositions/aggregations, find substates '''
    for each in context.composite_states:
        if not isinstance(each, ogAST.StateAggregation):
            # Aggregations are just containers, not states
            for name in statenames(each):
                yield f'{prefix}{each.statename}.{name}'
        for substate in rec_findstates(each,
                                       prefix=f'{prefix}{each.statename}.'):
            yield substate


def state_aggregations(process):
    ''' Explore recursively the AST to find all state aggregations, and
        return the composite states inside them
        input: ogAST.Process element
        output: {state_aggregation: {list of ogAST.CompositeState}
    '''
    # { aggregate_name : [list of parallel states] }
    aggregates = defaultdict(list)
    def do_composite(comp, aggregate=''):
        ''' Recursively find all state aggregations in order to allow code
        generator backends to store the state of each parallel state '''
        pre = comp.statename if isinstance(comp, ogAST.StateAggregation) \
                    else ''
        for each in comp.composite_states:
            do_composite(each, pre)
            if isinstance(each, ogAST.StateAggregation):
                # substate of the current state is a state aggregation
                # -> set a flag in each terminator of the current state
                for term in comp.terminators:
                    if term.inputString.lower() == each.statename.lower():
                        term.next_is_aggregation = True
        if aggregate and not isinstance(comp, ogAST.StateAggregation):
            # Composite state inside a state aggregation
            aggregates[aggregate].append(comp)
            # Here, all the terminators inside the composite states must
            # be flagged with the name of the substate so that the NEXTSTATE
            # will not be using the main "context.state" variable but will
            # use the parallel substate name when generating code.
            for each in comp.terminators:
                each.substate = comp.statename
    for each in process.composite_states:
        do_composite(each)
    for each in process.terminators:
        if each.inputString.lower() in aggregates:
            each.next_is_aggregation = True
    for name, comp in aggregates.items():
        # for each state aggregation. update the terminators
        # of each parallel state with the name of all sibling states
        # useful for backends to handle parallel state termination (return)
        # since they have to synchronize with the sibling states
        siblings = [sib.statename for sib in comp]
        for term in [terms for sib in comp for terms in sib.terminators]:
            term.siblings = siblings
    return aggregates


def parallel_states(aggregates):
    ''' Given a mapping obtained with state_aggregation(process), extract
        all parallel states and return a list of state names '''
    parallel_states = []
    for name, comp in aggregates.items():
        for each in comp:
            parallel_states.extend(name for name in each.mapping.keys()
                    if not name.endswith(u'START'))
    return parallel_states


def map_input_state(process):
    ''' Create a mapping dict {input1: {state1: transition, ...}, ...} '''
    mapping = defaultdict(dict)
    input_signals = [sig['name'] for sig in process.input_signals]
    # Add timers to the mapping
    input_signals.extend(process.timers)
    for input_signal in input_signals:
        for state_name, input_symbols in process.mapping.items():
            if isinstance(input_symbols, list):
                # Start symbols have no list of inputs
                for i in input_symbols:
                    if input_signal.lower() in (inp.lower() for
                                               inp in i.inputlist):
                        mapping[input_signal][state_name] = i
    return mapping


def update_full_statelist(process, SEPARATOR=DEFAULT_SEPARATOR) -> None:
    ''' Compute the value of the AST field "process.full_statelist"
        Inputs:
          * process is of type ogAST.Process
    '''

    process.full_statelist = set(chain(process.aggregates.keys(),
                               (name for name in process.mapping.keys()
                                    if not name.endswith('START'))))
    if process.aggregates:
        # Parallel states in a state aggregation may terminate
        process.full_statelist.add(f'state{SEPARATOR}end')

def inner_labels_to_floating(process):
    '''
        Transform inner labels of both floating labels and transitions
        into new floating labels, so that they can be generated in a separate
        section of code, where they are in the scope of everybody
        Works with processes, procedures and nested states
    '''
    for idx in range(len(process.content.floating_labels)):
        for new_floating in find_labels(
                      process.content.floating_labels[idx].transition):
            process.content.floating_labels.append(new_floating)
    for proc_tr in process.transitions:
        for new_floating in find_labels(proc_tr):
            process.content.floating_labels.append(new_floating)
    if process.content.start:
        for new_floating in find_labels(process.content.start.transition):
            process.content.floating_labels.append(new_floating)
    for each in process.content.named_start:
        for new_floating in find_labels(each.transition):
            process.content.floating_labels.append(new_floating)


def flatten(process, sep=u'_'):
    ''' In-place update of the AST: flatten a model with nested states
        Rename inner states, procedures, etc. and move them to process level
    '''
    def update_terminator(context, term, process):
        '''Set next_id, identifying the next transition to run '''
        if term.inputString.lower() in (st.statename.lower()
                                for st in context.composite_states):
            if not term.via:
                term.next_id = term.inputString.lower() + sep + 'START'
            else:
                term.next_id = f'{term.inputString}{sep}{term.entrypoint}_START'
        elif term.inputString.strip() in ('-', '-*'):
            for each in term.possible_states:
                term.candidate_id[-1].append(each)
                for comp in context.composite_states:
                    if each.lower() == comp.statename.lower():
                        if isinstance(comp, ogAST.StateAggregation):
                            term.next_is_aggregation = True
                            term.candidate_id[each + sep + 'START'] = [each]
                        else:
                            term.candidate_id[each + sep + 'START'] = \
                                       [st for st in process.mapping.keys()
                                        if st.startswith(each)
                                        and not st.endswith('START')]
                        continue

    def update_composite_state(state, process):
        ''' Rename inner states, recursively, and add inner transitions
            to process, updating indexes, and update terminators
        '''
        trans_idx = len(process.transitions)
        prefix = state.statename + sep
        set_terminator_states(state, prefix)
        set_transition_states(state, prefix)

        state.mapping = {prefix + key: state.mapping.pop(key)
                         for key in list(state.mapping.keys())}
        # Continuous signal mappings
        state.cs_mapping = {prefix + key: state.cs_mapping.pop(key)
                            for key in list(state.cs_mapping.keys())}

        process.transitions.extend(state.transitions)

        # Add prefix to local variable names and push them at process level
        for dcl in state.variables.keys():
            rename_everything(state.content, dcl, prefix + dcl)
        state.variables = {prefix + key: state.variables.pop(key)
                           for key in list(state.variables.keys())}
        process.variables.update(state.variables)

        # Update return transition indices
        for each in state.terminators:
            if each.kind == 'return':
                for idx, trans in enumerate(process.transitions):
                    if trans == each.next_trans:
                        each.next_id = idx
                        break

        values = []
        for key, value in state.mapping.items():
            # Update transition indices
            if isinstance(value, int):
                # START transitions
                state.mapping[key] = value + trans_idx
            else:
                values.extend(value)

        for each in state.cs_mapping.values():
            # Update transition indices of continuous signals
            # XXX shouldn't we do it also for CONNECT parts?
            values.extend(each)

        for inp in set(values):
            # values may contain duplicate entries if an input corresponds
            # to multiple states. In that case we must update the index of the
            # input only once, thus the set().
            inp.transition_id += trans_idx

        process.mapping.update(state.mapping)
        process.cs_mapping.update(state.cs_mapping)

        # If composite state has entry procedures, add the call
        if state.entry_procedure:
            for each in (trans for trans in state.mapping.values()
                         if isinstance(trans, int)):
                call_entry = ogAST.ProcedureCall()
                call_entry.inputString = 'entry'
                entryproc = f'{prefix}entry'
                call_entry.output = [{'outputName': entryproc,
                                     'params': [], 'tmpVars': []}]
                process.transitions[each].actions.insert(0, call_entry)

        # If composite state has exit procedure, add an call to this
        # procedure if the transition ends up exiting the state with
        # a return statement. There are other calls to the exit procedure
        # that the code generation backend must add when the state is exited
        # from a transition trigger in the super state. See AdaGenerator.py
        if state.exit_procedure:
            # Build up a list of transitions that contain a return statement
            trans_with_return = []
            for each in chain(state.transitions, (lab.transition for lab in
                                              state.content.floating_labels)):
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
                call_exit = ogAST.ProcedureCall()
                call_exit.inputString = 'exit'
                exitproc = f'{prefix}exit'
                call_exit.output = [{'outputName': exitproc,
                                     'params': [], 'tmpVars': []}]
                trans.actions.append(call_exit)

        for inner in state.composite_states:
            # Go recursively in inner composite states
            inner.statename = prefix + inner.statename
            update_composite_state(inner, process)
            # Remove: recursion is already handled within propagate_inputs
            #propagate_inputs(inner, process)
            #del process.mapping[inner.statename]
        for each in state.terminators:
            # Give prefix to terminators
            if each.label:
                each.label.inputString = prefix + each.label.inputString
            if each.kind == 'next_state':
                if each.inputString.strip() not in ('-', '-*'):
                    each.inputString = prefix + each.inputString
                # Set next transition id
                update_terminator(context=state, term=each, process=process)
            elif each.kind == 'join':
                rename_everything(state.content,
                                  each.inputString,
                                  prefix + each.inputString)
        for each in state.labels:
            # Give prefix to labels in transitions
            rename_everything(state.content,
                              each.inputString,
                              prefix + each.inputString)
        # Add prefixed floating labels of the composite state to the process
        process.content.floating_labels.extend(state.content.floating_labels)
        # Rename inner procedures
        for each in state.content.inner_procedures:
            rename_everything(state.content, each.inputString,
                              prefix + each.inputString)
            each.inputString = prefix + each.inputString
        process.content.inner_procedures.extend(state.content.inner_procedures)

    def propagate_inputs(nested_state, context):
        ''' Nested states: Inputs at level N must be handled at level N-1
            that is, all inputs of a composite states (the ones that allow
            to exit the composite state from the outer scope) must be
            processed by each of the substates.
        '''
        if not isinstance(nested_state, ogAST.StateAggregation):
            for val in nested_state.mapping.values():
                try:
                    inputlist = context.mapping[nested_state.statename]
                    val.extend(inputlist)
                except (AttributeError, KeyError):
                    # KeyError in case of StateAggregation
                    pass
            for val in nested_state.cs_mapping.values():
                try:
                    inputlist = context.cs_mapping[nested_state.statename]
                    val.extend(inputlist)
                except (AttributeError, KeyError):
                    # KeyError in case of StateAggregation
                    pass
        for each in nested_state.composite_states:
            # do the same recursively
            propagate_inputs(each, nested_state)
            #del nested_state.mapping[each.statename]
        if not isinstance(nested_state, ogAST.StateAggregation):
            del context.mapping[nested_state.statename]
            del context.cs_mapping[nested_state.statename]

    def set_terminator_states(context, prefix=''):
        ''' Associate state to terminators, needed to process properly
            a history nextstates (dash nextstate) in code generators '''
        for each in context.content.states:
            for inp in chain(each.inputs,
                             each.continuous_signals,
                             each.connects):
                for term in inp.terminators:
                    term.possible_states.extend(prefix + name.lower()
                                                for name in each.statelist)

    def set_transition_states(context, prefix=''):
        ''' Associate state to transitions, needed to process properly
            the call to the exit procedure of a nested state '''
        for each in context.content.states:
            for inp in chain(each.inputs,
                             each.continuous_signals,
                             each.connects):
                if inp.transition is not None:
                    inp.transition.possible_states.extend(prefix + name.lower()
                                                for name in each.statelist)

    set_terminator_states(process)
    set_transition_states(process)

    for each in process.composite_states:
        update_composite_state(each, process)
        propagate_inputs(each, process)
        #del process.mapping[each.statename]

    # Update terminators at process level
    for each in process.terminators:
        if each.kind == 'next_state':
            update_terminator(process, each, process)


@singledispatch
def rename_everything(ast, from_name, to_name):
    '''
        Rename in all symbols all occurrences of name_ref into new_name.
        This is used to avoid name clashes in nested diagrams when they get
        flattened. For example rename all accesses to a variable declared
        in the scope of a composite state, so that they do not overwrite
        a variable with the same name declared at a higher scope.
    '''
    LOG.debug ('rename_everything - ' + str(ast) + " - ")
    try:
        LOG.debug(ast.inputString)
    except:
        pass

    _, _, _ = ast, from_name, to_name


@rename_everything.register(ogAST.Automaton)
def _rename_automaton(ast, from_name, to_name):
    ''' Renaming at Automaton top level (content of diagrams) '''
    if ast.start:
        rename_everything(ast.start.transition, from_name, to_name)
    for each in ast.named_start:
        rename_everything(each.transition, from_name, to_name)
    for each in ast.floating_labels:
        rename_everything(each, from_name, to_name)
    for each in ast.states:
        for inp in chain(each.inputs, each.continuous_signals, each.connects):
            rename_everything(inp.transition, from_name, to_name)
            for idx, param in enumerate(inp.parameters):
                if param.lower() == from_name.lower():
                    inp.parameters[idx] = to_name
            try:
                rename_everything(inp.trigger, from_name, to_name)
            except AttributeError:
                # only for continuous signals
                pass
        if each.composite:
            rename_everything(each.composite.content, from_name, to_name)
    for each in ast.inner_procedures:
        # Check that from_name is not a redefined variable in the procedure
        for varname in each.variables.keys():
            if varname.lower() == from_name:
                break
        else:
            # do the same for procedure input/output variables (FPAR section)
            for fpar in each.fpar:
                if fpar['name'].lower() == from_name:
                    break
            else:
                rename_everything(each.content, from_name, to_name)


@rename_everything.register(ogAST.Output)
@rename_everything.register(ogAST.ProcedureCall)
def _rename_output(ast, from_name, to_name):
    ''' Rename actual parameter names in output/procedure calls
        and possibly the procedure name '''
    for each in ast.output:
        if each['outputName'].lower() == from_name.lower():
            each['outputName'] = to_name
        for param in each['params']:
            rename_everything(param, from_name, to_name)


@rename_everything.register(ogAST.Label)
def _rename_label(ast, from_name, to_name):
    ''' Rename elements in the transition following a label '''
    if ast.inputString.lower() == from_name.lower():
        ast.inputString = to_name
    rename_everything(ast.transition, from_name, to_name)


@rename_everything.register(ogAST.Decision)
def _rename_decision(ast, from_name, to_name):
    ''' Rename elements in decision '''
    if ast.kind == 'question':
        rename_everything(ast.question, from_name, to_name)
    for each in ast.answers:
        rename_everything(each, from_name, to_name)


@rename_everything.register(ogAST.Answer)
def _rename_answer(ast, from_name, to_name):
    ''' Rename elements in an answer branch '''
    for each in ast.answers:
        if each['kind'] in ('constant', 'open_range'):
            _, constant = each['content'] # get the constant
            rename_everything(constant, from_name, to_name)
        elif each['kind'] == 'closed_range':
            pass  # TODO when supported
    rename_everything(ast.transition, from_name, to_name)


@rename_everything.register(ogAST.Transition)
def _rename_transition(ast, from_name, to_name):
    ''' Rename in all symbols of a transition '''
    for each in chain(ast.actions, ast.terminators):
        # Label, output, task, decision, terminators
        rename_everything(each, from_name, to_name)


@rename_everything.register(ogAST.Terminator)
def _rename_terminator(ast, from_name, to_name):
    ''' Rename terminators: join/labels, next_state '''
    if ast.inputString.lower() == from_name.lower():
        ast.inputString = to_name
    rename_everything(ast.label, from_name, to_name)
    rename_everything(ast.return_expr, from_name, to_name)


@rename_everything.register(ogAST.TaskAssign)
def _rename_task_assign(ast, from_name, to_name):
    ''' List of assignments '''
    for each in ast.elems:
        rename_everything(each, from_name, to_name)


@rename_everything.register(ogAST.TaskForLoop)
def _rename_forloop(ast, from_name, to_name):
    ''' List of FOR loops '''
    for each in ast.elems:
        rename_everything(each['list'], from_name, to_name)
        if each['range'] is not None:
            rename_everything(each['range']['start'], from_name, to_name)
            rename_everything(each['range']['stop'], from_name, to_name)
        if each['transition'] is not None:
            rename_everything(each['transition'], from_name, to_name)


@rename_everything.register(ogAST.ExprPlus)
@rename_everything.register(ogAST.ExprMul)
@rename_everything.register(ogAST.ExprMinus)
@rename_everything.register(ogAST.ExprEq)
@rename_everything.register(ogAST.ExprNeq)
@rename_everything.register(ogAST.ExprGt)
@rename_everything.register(ogAST.ExprGe)
@rename_everything.register(ogAST.ExprLt)
@rename_everything.register(ogAST.ExprLe)
@rename_everything.register(ogAST.ExprDiv)
@rename_everything.register(ogAST.ExprMod)
@rename_everything.register(ogAST.ExprRem)
@rename_everything.register(ogAST.ExprAssign)
@rename_everything.register(ogAST.ExprOr)
@rename_everything.register(ogAST.ExprIn)
@rename_everything.register(ogAST.ExprAnd)
@rename_everything.register(ogAST.ExprXor)
@rename_everything.register(ogAST.ExprAppend)
@rename_everything.register(ogAST.ExprAssign)
def _rename_expr(ast, from_name, to_name):
    ''' Two-sided expressions '''
    rename_everything(ast.left, from_name, to_name)
    rename_everything(ast.right, from_name, to_name)


@rename_everything.register(ogAST.PrimSequenceOf)
def _rename_prim_seq_of(ast, from_name, to_name):
    ''' List of primary '''
    for each in ast.value:
        rename_everything(each, from_name, to_name)

@rename_everything.register(ogAST.PrimSequence)
def _rename_prim_seq(ast, from_name, to_name):
    ''' Values in the fields of a SEQUENCE '''
    for each in ast.value.values():
        rename_everything(each, from_name, to_name)

@rename_everything.register(ogAST.PrimChoiceItem)
def _rename_prim_choice_item(ast, from_name, to_name):
    ''' Value of a CHOICE item '''
    rename_everything(ast.value['value'], from_name, to_name)


@rename_everything.register(ogAST.PrimIndex)
def _rename_index(ast, from_name, to_name):
    ''' Index of an array '''
    rename_everything(ast.value[0], from_name, to_name)
    for each in ast.value[1]['index']:
        rename_everything(each, from_name, to_name)


@rename_everything.register(ogAST.PrimSubstring)
def _rename_substring(ast, from_name, to_name):
    ''' Substrings '''
    rename_everything(ast.value[0], from_name, to_name)
    for each in ast.value[1]['substring']:
        rename_everything(each, from_name, to_name)


@rename_everything.register(ogAST.PrimSelector)
def _rename_primselector(ast, from_name, to_name):
    ''' Rename variable name in field access (a.b.c) '''
    rename_everything(ast.value[0], from_name, to_name)


@rename_everything.register(ogAST.PrimVariable)
def _rename_path(ast, from_name, to_name):
    ''' Ultimate seek point for the renaming: primary path/variables '''
    if ast.value[0].lower() == from_name.lower():
        ast.value[0] = to_name


@rename_everything.register(ogAST.PrimCall)
def _rename_primcall(ast, from_name, to_name):
    ''' PrimCall is used e.g. by function "length" (special operators) '''
    for each in ast.value[1]['procParams']:
        rename_everything(each, from_name, to_name)


@rename_everything.register(ogAST.PrimConditional)
def _rename_ifthenelse(ast, from_name, to_name):
    ''' Rename expressions in Conditional expression construct '''
    for expr in ('if', 'then', 'else'):
        rename_everything(ast.value[expr], from_name, to_name)


def find_labels(trans):
    '''
        Yield a list of transition actions whenever a label is found
        Used to transform labels into floating labels so that the gotos
        in a backend can be contained within a single scope.
    '''
    if not trans:
        return
    # Terminators can have a label - add it to the transition actions
    # (to trigger a goto at code generation)
    if trans.terminator and trans.terminator.label:
        trans.actions.append(trans.terminator.label)
        trans.terminator.label = None
    # Then for each action, check if there are labels and yield
    # a new transition with the remaining actions (following the label)
    for idx, action in enumerate(trans.actions):
        if isinstance(action, ogAST.Label):
            new_trans = ogAST.Transition()
            # Create a floating label
            flab = ogAST.Floating_label(label=action)
            new_trans.actions = \
                    trans.actions[slice(idx + 1, len(trans.actions))]
            new_trans.terminator = trans.terminator
            new_trans.terminators = trans.terminators
            flab.transition = new_trans
            # Transform the label into a JOIN in the original transition
            trans.actions[idx:] = []
            trans.terminator = ogAST.Terminator()
            trans.terminator.inputString = action.inputString
            trans.terminator.kind = 'join'
            # Recursively find labels in the new transition
            for flabel in find_labels(flab.transition):
                yield flabel
            # Then yield the new transition
            yield flab
        elif isinstance(action, ogAST.Decision):
            for answer in action.answers:
                for new_fl in find_labels(answer.transition):
                    # Append the remaining actions of the transition
                    if not new_fl.transition.terminator:
                        new_fl.transition.actions.extend(trans.actions
                                          [slice(idx + 1, len(trans.actions))])
                        new_fl.transition.terminator = trans.terminator
                    yield new_fl


def sorted_fields(atype):
    ''' Return the sorted list of a SEQUENCE or CHOICE type fields '''
    if atype.kind not in ('SequenceType', 'ChoiceType'):
        raise TypeError('Not a SEQUENCE nor a CHOICE')
    tmp = ([k, val.Line, val.CharPositionInLine]
             for k, val in atype.Children.items())
    return (x[0] for x in sorted(tmp, key=operator.itemgetter(1,2)))


def find_basic_type(TYPES, a_type):
    ''' Return the ASN.1 basic type of a_type.
    TYPES is process.dataview
    '''
    basic_type = a_type
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in TYPES.keys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = TYPES[typename].type
                break
    return basic_type


def generate_asn1_datamodel(process: ogAST.Process, SEPARATOR: str=DEFAULT_SEPARATOR) -> None:
    ''' Generate an ASN.1 model containing:
          - the state definition
          - a type describing the SDL context
          - all user-defined SDL type (NEWTYPEs...)
        This function is independent from specific backends.
    '''

    if not process.name:
        process.name = process.processName

    process_asn1 = process.name.capitalize().replace('_', '-')
    asn1_template = [
            f'{process_asn1}-Datamodel DEFINITIONS ::=',
            'BEGIN',
            '--  This file was generated automatically by OpenGEODE']

    # The ASN.1 module must import the types from other asn1 modules
    types_with_proper_case, imports = [], []
    imports = []
    for moduleName, sorts in process.DV.exportedTypes.items():
        actual_sorts = []
        for each in sorts:
            process.mapping_sort_module[each] = moduleName
            if process.DV.types[each].AddedType == "False":
                actual_sorts.append(each)
                types_with_proper_case.append(each)
        sortsAsList = ", ".join(actual_sorts)
        if sortsAsList:
            imports.append(f'{sortsAsList} FROM {moduleName}')
    if types_with_proper_case:
        asn1_template.append(
                "IMPORTS\n   " + "\n   ".join(imports) + ";")

    # Format the state list with ASN.1-compatible syntax
    statelist_asn1 = (state.lower().replace('_', '-')
                      for state in process.full_statelist)
    states_asn1 = ", ".join(statelist_asn1) \
            or f'{process_asn1.lower()}-has-no-state'
    # Create an ASN.1 definition of the list of states, instead of
    # a native Ada type - this allows external tools to access
    # information about the model without having to parse SDL
    asn1_states_def = f"\n{process_asn1}-States ::= ENUMERATED" \
                      f" {{{states_asn1}}}"

    asn1_template.append(asn1_states_def)

    # Template to generate the full SDL context as a single ASN.1 type
    # This is very useful then to manipulate it from C, Ada or Python as
    # it is then directly accessible and uPER-encodable
    context_elems = []
    if process.full_statelist:
        # Some systems may have no states - only a start transition
        context_elems.append(f'   state {process_asn1}-States')

    context_elems.append ('init-done BOOLEAN')
    # State aggregation: add list of substates
    for substates in process.aggregates.values():
        for each in substates:
            context_elems.append(
              f'{each.statename.lower()}{SEPARATOR}state {process_asn1}-States')

    for var_name, (var_type, def_value) in process.variables.items():
        if var_name in process.aliases.keys():
            continue
        try:
            sortname = var_type.ReferencedTypeName
        except AttributeError:
            # if the DCL variable references a non-existing type, it shall
            # not prevent the model saving.
            continue
        # If the type is a ends with _selection, i.e. it is an OG-created
        # CHOICE selector, then prefix the type with the process name
        if sortname.endswith('-selection'):
            sortname = f'{process.name}-{sortname}'.title()
        context_elems.append(f'{var_name.lower()} {sortname}')

    asn1_context = (f'\n{process_asn1}-Context ::='' SEQUENCE {\n'
                    + ",\n   ".join(line.replace("_", "-").replace("'", '"') for line in context_elems)
                    + "\n}\n")

    asn1_template.append(asn1_context)

    # Add user-defined NEWTYPEs and CHOICE selector types
    choice_selections = []
    for sortname, sortdef in process.user_defined_types.items():
        if sortdef.type.kind == "SequenceOfType":
            rangeMin = sortdef.type.Min
            rangeMax = sortdef.type.Max
            refType  = sortdef.type.type.ReferencedTypeName
            for refTypeCase in types_with_proper_case:
                if refTypeCase.lower().replace('-', '_') == \
                        refType.lower().replace('-', '_'):
                    break
            asn1_template.append(
                    f'{sortname.replace("_", "-").capitalize()} ::= SEQUENCE '
                    f'(SIZE ({rangeMin} .. {rangeMax})) OF '
                    f'{refTypeCase.replace("_", "-")}')
        elif sortdef.type.kind == "EnumeratedType":
            # At the moment, the only user-defined ENUMERATED types that are
            # supported are the ones generated for the CHOICE selectors
            # We can therefore safely rename them systematically here,
            # by using the process name as prefix, to avoid any risk of
            # duplicate type definition in case it exists in another SDL
            # process of the system.
            prefixed_name = f'{process.name}_{sortdef.ChoiceTypeName}_selection '
            keys = []
            for idx, key in enumerate(sortdef.type.EnumValues.keys()):
                # give an index to the enumerations to align with -selection
                # types used in choice index
                keys.append(f'{key}-present({idx+1})')
            asn1_template.append(
                    f'{prefixed_name.replace("_", "-").title()} ::= ENUMERATED {{' + ", ".join(keys) + '}')
    asn1_template.append('END\n')

    # Write the ASN.1 file
    with open(process.name.lower() + '_datamodel.asn', 'w') as asn1_file:
        asn1_file.write('\n'.join(asn1_template))



def code_generation_preprocessing(process, separator=DEFAULT_SEPARATOR):
    ''' Do all sorts of preprocessing before invoking a code generator
        and update the AST of the process
    '''
    # In case model has nested states, flatten everything
    flatten(process, sep=separator)

    # Pre-processing of aliases: we must rename all references to the aliases
    # when they point to a structure that contain a CHOICE field (we cannot
    # use a rename clause in that case, since the field depends on a
    # discriminant.
    no_renames = []
    for (alias, (sort, alias_expr)) in process.aliases.items():
        def rec_detect_choice(expr: ogAST.Expression) -> bool:
            if not isinstance(expr, ogAST.PrimSelector):
                return False
            receiver = expr.value[0]
            bty = find_basic_type(TYPES=process.dataview,
                                  a_type=receiver.exprType)
            if bty.kind == 'ChoiceType':
                return True
            return rec_detect_choice(receiver)
        is_choice = rec_detect_choice(alias_expr)
        if is_choice:
            LOG.debug(f"alias: {alias_expr.inputString} will replace {alias}")
            rename_everything(process.content,
                              alias,
                              alias_expr.inputString)
            no_renames.append(alias)

    # Process State aggregations (Parallel states)

    # Find recursively in the AST all state aggregations
    # Format: {'aggregation_name' : [list of ogAST.CompositeState]
    process.aggregates = state_aggregations(process)

    # Make an mapping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    process.input_mapping = map_input_state(process)

    # Extract the list of parallel states names inside the composite states
    # of state aggregations
    process.parallel_states = parallel_states(process.aggregates)

    # Establish the list of states (excluding START states)
    update_full_statelist(process, separator)

    return no_renames
