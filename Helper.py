#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module provides helper functions typically used by backends:

        flatten(ast) : transform a model with nested states to a flat model
        rename_everything(ast, from_name, to_name) : rename symbols
        inner_labels_to_floating(process) : remove labels from transitions

    Copyright (c) 2012-2014 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import logging
from itertools import chain

from singledispatch import singledispatch

import ogAST

LOG = logging.getLogger(__name__)

__all__ = ['flatten', 'rename_everything', 'inner_labels_to_floating']


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
    for new_floating in find_labels(process.content.start.transition):
        process.content.floating_labels.append(new_floating)
    for each in process.content.named_start:
        for new_floating in find_labels(each.transition):
            process.content.floating_labels.append(new_floating)


def flatten(process):
    ''' Flatten the nested states:
        Rename inner states, procedures, etc. and move them to process level
    '''
    def update_terminator(context, term):
        '''Set next_id, identifying the next transition to run '''
        if term.inputString.lower() in (st.statename.lower()
                                for st in context.composite_states):
            if not term.via:
                term.next_id = context.mapping \
                                          [term.inputString.lower() + '_START']
            else:
                term.next_id = context.mapping[term.inputString.lower()
                                               + '_'
                                               + term.entrypoint.lower()
                                               + '_START']

    def update_composite_state(state, process):
        ''' Rename inner states, recursively, and add inner transitions
            to process, updating indexes, and update terminators
        '''
        trans_idx = len(process.transitions)
        prefix = state.statename + '_'
        state.mapping = {prefix + key:state.mapping.pop(key)
                         for key in state.mapping.keys()}
        process.transitions.extend(state.transitions)

        # Add prefix to local variable names and push them at process level
        for dcl in state.variables.viewkeys():
            rename_everything(state.content, dcl, prefix + dcl)
        state.variables = {prefix + key: state.variables.pop(key)
                           for key in state.variables.keys()}
        process.variables.update(state.variables)

        for key, value in state.mapping.viewitems():
            # Update transition indices
            if isinstance(value, int):
                state.mapping[key] = value + trans_idx
            else:
                for inp in value:
                    inp.transition_id += trans_idx
        process.mapping.update(state.mapping)

        # If composite state has entry procedures, add the call
        if state.entry_procedure:
            for each in (trans for trans in state.mapping.viewvalues()
                         if isinstance(trans, int)):
                call_entry = ogAST.ProcedureCall()
                call_entry.inputString = 'entry'
                call_entry.output = [{'outputName': prefix + 'entry',
                                     'params': [], 'tmpVars': []}]
                process.transitions[each].actions.insert(0, call_entry)

        # If composite state has exit procedure, add the call
        if state.exit_procedure:
            for each in chain(state.transitions, (lab.transition for lab in
                                              state.content.floating_labels)):
                if each.terminator.kind == 'return':
                    call_exit = ogAST.ProcedureCall()
                    call_exit.inputString = 'exit'
                    call_exit.output = [{'outputName': prefix + 'exit',
                                     'params': [], 'tmpVars': []}]
                    each.actions.append(call_exit)

        for inner in state.composite_states:
            # Go recursively in inner composite states
            inner.statename = prefix + inner.statename
            update_composite_state(inner, process)
        for each in state.terminators:
            # Give prefix to terminators
            if each.label:
                each.label.inputString = prefix + each.label.inputString
            if each.kind == 'next_state':
                each.inputString = prefix + each.inputString
                # Set next transition id
                update_terminator(state, each)
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

    def propagate_inputs(nested_state, inputlist):
        ''' Nested states: Inputs at level N must be handled at level N-1
            that is, all inputs of a composite states (the ones that allow
            to exit the composite state from the outer scope) must be
            processed by each of the substates.
        '''
        for _, val in nested_state.mapping.viewitems():
            try:
                val.extend(inputlist)
            except AttributeError:
                pass
        for each in nested_state.composite_states:
            # do the same recursively
            propagate_inputs(each, nested_state.mapping[each.statename])
            del nested_state.mapping[each.statename]

    for each in process.composite_states:
        update_composite_state(each, process)
        propagate_inputs(each, process.mapping[each.statename])
        del process.mapping[each.statename]

    # Update terminators at process level
    for each in process.terminators:
        if each.kind == 'next_state':
            update_terminator(process, each)


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
        for inp in each.inputs:
            rename_everything(inp.transition, from_name, to_name)
            for idx, param in enumerate(inp.parameters):
                if param.lower() == from_name.lower():
                    inp.parameter[idx] = to_name
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
        pass # TODO when supported
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

@rename_everything.register(ogAST.PrimPath)
@rename_everything.register(ogAST.PrimVariable)
def _rename_path(ast, from_name, to_name):
    ''' Ultimate seek point for the renaming: primary path/variables '''
    if ast.value[0].lower() == from_name.lower():
        ast.value[0] = to_name


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
            new_trans.actions = trans.actions[slice(idx+1, len(trans.actions))]
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
                        new_fl.transition.actions.extend(
                               trans.actions[slice(idx+1, len(trans.actions))])
                        new_fl.transition.terminator = trans.terminator
                    yield new_fl

