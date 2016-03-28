#!/usr/bin/env python
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

    Copyright (c) 2012-2015 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import operator
import logging
from itertools import chain, ifilterfalse
from collections import defaultdict

from singledispatch import singledispatch

import ogAST

LOG = logging.getLogger(__name__)

__all__ = ['flatten', 'rename_everything', 'inner_labels_to_floating',
           'map_input_state', 'sorted_fields', 'state_aggregations',
           'parallel_states', 'statenames', 'rec_findstates']


def statenames(context, sep=u'\u00dc'):
    ''' Return the list of states (just the names) of a given context
    Format the output by replacing unicode separator symbol with a dot '''
    return (s.replace(sep, u'.') for s in context.mapping.viewkeys()
            if not s.endswith(u'START'))


#def non_composite_statenames(context, sep=u'\u00dc'):
#   ''' Return a list of statenames excluding parents of state compositions '''
#   composites = []
#   for each in context.composite_states:
#       if not isinstance(each, ofAST.StateAggregation):
#
#   return ifilterfalse(lambda x: , statenames(context, sep))


def rec_findstates(context, prefix=''):
    ''' In case of state compositions/aggregations, find substates '''
    for each in context.composite_states:
        if not isinstance(each, ogAST.StateAggregation):
            # Aggregations are just containers, not states
            for name in statenames(each):
                yield u'{}{}.{}'.format(prefix, each.statename, name)
        for substate in rec_findstates(each,
                                       prefix=u'{}{}.'.format(prefix,
                                                              each.statename)):
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
    for name, comp in aggregates.viewitems():
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
    for name, comp in aggregates.viewitems():
        for each in comp:
            parallel_states.extend(name for name in each.mapping.viewkeys()
                    if not name.endswith(u'START'))
    return parallel_states


def map_input_state(process):
    ''' Create a mapping dict {input1: {state1: transition, ...}, ...} '''
    mapping = defaultdict(dict)
    input_signals = [sig['name'] for sig in process.input_signals]
    # Add timers to the mapping
    input_signals.extend(process.timers)
    for input_signal in input_signals:
        for state_name, input_symbols in process.mapping.viewitems():
            if isinstance(input_symbols, list):
                # Start symbols have no list of inputs
                for i in input_symbols:
                    if input_signal.lower() in (inp.lower() for
                                               inp in i.inputlist):
                        mapping[input_signal][state_name] = i
    return mapping


def inner_labels_to_floating(process):
    '''
        Transform inner labels of both floating labels and transitions
        into new floating labels, so that they can be generated in a separate
        section of code, where they are in the scope of everybody
        Works with processes, procedures and nested states
    '''
    for idx in xrange(len(process.content.floating_labels)):
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
                term.next_id = term.inputString.lower() + sep + u'START'
            else:
                term.next_id = u'{term}{sep}{entry}_START'.format(
                        term=term.inputString, entry=term.entrypoint, sep=sep)
        elif term.inputString.strip() == '-':
            for each in term.possible_states:
                term.candidate_id[-1].append(each)
                for comp in context.composite_states:
                    if each.lower() == comp.statename.lower():
                        if isinstance(comp, ogAST.StateAggregation):
                            term.next_is_aggregation = True
                            term.candidate_id[each + sep + u'START'] = [each]
                        else:
                            term.candidate_id[each + sep + u'START'] = \
                                       [st for st in process.mapping.viewkeys()
                                        if st.startswith(each)
                                        and not st.endswith(u'START')]
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
                         for key in state.mapping.keys()}
        # Continuous signal mappings
        state.cs_mapping = {prefix + key: state.cs_mapping.pop(key)
                            for key in state.cs_mapping.keys()}
        process.transitions.extend(state.transitions)

        # Add prefix to local variable names and push them at process level
        for dcl in state.variables.viewkeys():
            rename_everything(state.content, dcl, prefix + dcl)
        state.variables = {prefix + key: state.variables.pop(key)
                           for key in state.variables.keys()}
        process.variables.update(state.variables)

        # Update return transition indices
        for each in state.terminators:
            if each.kind == 'return':
                for idx, trans in enumerate(process.transitions):
                    if trans == each.next_trans:
                        each.next_id = idx
                        break

        values = []
        for key, value in state.mapping.viewitems():
            # Update transition indices
            if isinstance(value, int):
                # START transitions
                state.mapping[key] = value + trans_idx
            else:
                values.extend(value)

        for each in state.cs_mapping.viewvalues():
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
            for each in (trans for trans in state.mapping.viewvalues()
                         if isinstance(trans, int)):
                call_entry = ogAST.ProcedureCall()
                call_entry.inputString = 'entry'
                entryproc = u'{pre}entry'.format(pre=prefix)
                call_entry.output = [{'outputName': entryproc,
                                     'params': [], 'tmpVars': []}]
                process.transitions[each].actions.insert(0, call_entry)

        # If composite state has exit procedure, add the call
        if state.exit_procedure:
            for each in chain(state.transitions, (lab.transition for lab in
                                              state.content.floating_labels)):
                if each.terminator.kind == 'return':
                    call_exit = ogAST.ProcedureCall()
                    call_exit.inputString = 'exit'
                    exitproc = u'{pre}exit'.format(pre=prefix)
                    call_exit.output = [{'outputName': exitproc,
                                         'params': [], 'tmpVars': []}]
                    each.actions.append(call_exit)

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
                if each.inputString.strip() != '-':
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
            for _, val in nested_state.mapping.viewitems():
                try:
                    inputlist = context.mapping[nested_state.statename]
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

    def set_terminator_states(context, prefix=''):
        ''' Associate state to terminators, needed to process properly
            a history nextstates (dash nextstate) in code generators '''
        for each in context.content.states:
            for inp in each.inputs:
                for term in inp.terminators:
                    term.possible_states.extend(prefix + name.lower()
                                                for name in each.statelist)

    def set_transition_states(context, prefix=''):
        ''' Associate state to transitions, needed to process properly
            the call to the exit procedure of a nested state '''
        for each in context.content.states:
            for inp in each.inputs:
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
        Rename in all symbols all occurences of name_ref into new_name.
        This is used to avoid name clashes in nested diagrams when they get
        flattened. For example rename all accesses to a variable declared
        in the scope of a composite state, so that they do not overwrite
        a variable with the same name declared at a higher scope.
    '''
    _, _, _ = ast, from_name, to_name


@rename_everything.register(ogAST.Automaton)
def _rename_automaton(ast, from_name, to_name):
    ''' Renaming at Automaton top level (content of digragrams) '''
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
        for varname in each.variables.viewkeys():
            if varname.lower() == from_name:
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
    if ast.kind in ('constant', 'open_range'):
        rename_everything(ast.constant, from_name, to_name)
    elif ast.kind == 'closed_range':
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
        rename_everything(each['range']['start'], from_name, to_name)
        rename_everything(each['range']['stop'], from_name, to_name)
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


@rename_everything.register(ogAST.PrimVariable)
def _rename_path(ast, from_name, to_name):
    ''' Ultimate seek point for the renaming: primary path/variables '''
    if ast.value[0].lower() == from_name.lower():
        ast.value[0] = to_name


@rename_everything.register(ogAST.PrimConditional)
def _rename_ifhthenelse(ast, from_name, to_name):
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
             for k, val in atype.Children.viewitems())
    return (x[0] for x in sorted(tmp, key=operator.itemgetter(1,2)))
