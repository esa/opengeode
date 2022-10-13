#!/usr/bin/env python3
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

    Copyright (c) 2012-2022 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
import traceback
import os
import stat
from itertools import chain, product
from functools import singledispatch
from typing import List, Tuple

from . import ogAST, Helper

LOG = logging.getLogger(__name__)

__all__ = ['generate']


PROCESS_NAME = ""

# reference to the ASN.1 Data view and to the visible variables (in scope)
TYPES = None

VARIABLES = {}
MONITORS = {}
LOCAL_VAR = {}
# List of output signals and procedures
OUT_SIGNALS = []
PROCEDURES = []

# Avoid Unicode characters, they cause occasional annoying issues
SEPARATOR = "_0_"
LPREFIX = 'ctxt'
ASN1SCC = 'asn1Scc'


def is_numeric(string) -> bool:
    ''' Return true if value is a number '''
    try:
        float(string)
    except ValueError:
        return False
    return True


def external_ri_list(process) -> List:
    ''' Helper function: create a list of RI with proper signature
    Used for the formal parameters of generic packages when using process type
    '''
    result = []
    #print process.fpar
    for signal in process.output_signals:
        param_name = signal.get('param_name') or f'{signal["name"]}_param'
        param_spec = ''
        if 'type' in signal:
            typename = type_name(signal['type'])
            if 'PID' in TYPES:
                param_spec = f'({param_name}: in out {typename}; Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)'
            else:
                param_spec = f'({param_name}: in out {typename})'
        result.append(f"procedure RI{SEPARATOR}{signal['name']}{param_spec}")
    for proc in (proc for proc in process.procedures if proc.external):
        ri_header = f'procedure RI{SEPARATOR}{proc.inputString}'
        params = []
        params_spec = ''
        for param in proc.fpar:
            typename = type_name(param['type'])
            if param['direction'] == 'in':
                direct = 'in out'
            else:
                direct = 'out'
            params.append(f'{param["name"]} : {direct} {typename}')
        if params:
            if 'PID' in TYPES:
                params_spec = f"({'; '.join(params)}; Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)"
            else:
                params_spec = "({})".format("; ".join(params))
            ri_header += params_spec
        result.append(ri_header)

    for timer in process.timers:
        if 'PID' in TYPES:
            result.append(
                f"procedure Set_{timer} (Val : in out {ASN1SCC}T_Uint32; Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)")
            result.append(f"procedure Reset_{timer} (Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)")
        else:
            result.append(
                f"procedure Set_{timer} (Val : in out {ASN1SCC}T_Uint32)")
            result.append(f"procedure Reset_{timer}")
    return result


@singledispatch
def generate(*args, **kwargs) -> Tuple:
    ''' Generate the code for an item of the AST '''
    raise TypeError('Incorrect, unsupported or missing data in model AST')
    return [], []


# Processing of the AST
@generate.register(ogAST.Process)
def _process(process, simu=False, instance=False, taste=False, **kwargs) -> str:
    ''' Generate the code for a complete process (AST Top level)
        use instance=True to generate the code for a process type instance
        rather than the process type itself.
    '''
    # support generation of code of a process type
    if not instance:
        process.name = process.instance_of_name or process.processName
        generic = process.instance_of_name  #  shortcut
        process_instance = process
        process = process.instance_of_ref or process
    else:
        process.name = process.processName
        generic = False
        process_instance = process

    global PROCESS_NAME
    PROCESS_NAME = process.name

    global TYPES
    TYPES = process.dataview
    del OUT_SIGNALS[:]
    del PROCEDURES[:]
    OUT_SIGNALS.extend(process.output_signals)
    PROCEDURES.extend(process.procedures)
    global LPREFIX

    for each in PROCEDURES:
        process.random_generator.update(each.random_generator)

    # taste-properties module-specific flag for the Ada backend:
    # import the state data from an external module
    stop_condition = kwargs["ppty_check"] if "ppty_check" in kwargs else ""

    asn1_mods = (f'''"{mod.lower().replace('-', '_')}"''' for mod in process.asn1Modules)

    # determine if there are context parameters (defined at taste level)
    # they are passed as generic parameters in function type/instances
    has_context_params = any(mod.startswith("Context-")
            for mod in process.asn1Modules)

    #  Create a .gpr to build the library for the simulator
    lib_gpr = f'''project {process.name.lower()}_Lib is
   for Languages use ("Ada");
   for Library_Name use "{process.name.lower()}";
   for Library_Interface use ("{process.name.lower()}", "adaasn1rtl", {", ".join(asn1_mods)});
   for Object_Dir use "obj";
   for Library_Dir use "lib";
   for Library_Standalone use "encapsulated";
   for Library_Kind use "dynamic";
   for Source_Dirs use (".");
end {process.name.lower()}_Lib;'''

    #  Create a .gpr to build the Ada generated code
    ada_gpr = f'''project {process.name.lower()}_Ada is
   for Languages use ("Ada");
      for Source_Dirs use (".") & External_As_List ("CODE_PATH", ":");
      for Object_Dir use "../obj";
   end {process.name.lower()}_Ada;'''

    pr = process.name.lower()

    LOG.info(f'Generating Ada code for process {process.name}')

    #  Prepare the AST for code generation (flatten states, etc.)
    no_renames = Helper.code_generation_preprocessing(process)

    if not stop_condition:
        Helper.generate_asn1_datamodel(process)

    for (var_name, content) in process.variables.items():
        # filter out the aliases and put them in the local variable pool
        # to avoid unwanted prefixes when using them
        if var_name in no_renames:
            continue
        if var_name in process.aliases.keys():
            LOCAL_VAR[var_name] = content
        else:
            VARIABLES[var_name] = content

    MONITORS.update(process.monitors)

    process_level_decl = []

    reduced_statelist = {s for s in process.full_statelist
            if s not in process.parallel_states}

    #  When a signal is sent from the model a call to a function is emitted
    #  This function has to be provided - either by TASTE (kazoo), or by
    #  the user. Opengeode will generate a stub package for this.
    ri_stub_ads = []
    ri_stub_adb = []

    # CHOICE selector types: we created an ASN.1 type to access them
    # (in Helper.generate_asn1_datamodel), but we need conversion functions
    choice_selections = []
    for sortname, sortdef in process.user_defined_types.items():
        if sortdef.type.kind == "EnumeratedType":
            choiceTypeModule = process.mapping_sort_module[sortdef.ChoiceTypeName].replace('-', '_')
            sortAda = sortname.replace('-', '_')
            fromMod = f'{choiceTypeModule}.{ASN1SCC}{sortAda}'
            toMod = f'{process.name}_Datamodel.{ASN1SCC}{process.name}_{sortAda}'
            choice_selections.append(
                    f"function To_{sortAda} (Src : {fromMod}) return {toMod} is ({toMod}'Enum_Val (Src'Enum_Rep));")

    # Generate the code to declare process-level context
    context_decl = []
    if not stop_condition:
        # but not in stop condition code, since we reuse the context type
        # of the state machine being observed

        ctxt = (f'{LPREFIX} : aliased {ASN1SCC}{process.name.capitalize()}_Context :=\n'
            '      (Init_Done => False,\n       ')
        initial_values = []
        # some parts of the context may have initial values
        for var_name, (var_type, def_value) in process.variables.items():
            if var_name in process.aliases.keys():
                # aliases are not part of the context
                continue
            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result
                dst, dstr, dlocal = expression(def_value)
                varbty = find_basic_type(var_type)

                if varbty.kind.startswith('Integer') and \
                        isinstance(def_value, (ogAST.PrimOctetStringLiteral,
                                               ogAST.PrimBitStringLiteral)):
                    dstr = str(def_value.numeric_value)

                elif varbty.kind in ('SequenceOfType',
                                     'OctetStringType',
                                     'BitStringType'):
                    dstr = array_content(def_value, dstr, varbty)

                elif varbty.kind == 'IA5StringType':
                    dstr = ia5string_raw(def_value)
                assert not dst and not dlocal,\
                        'DCL: Expecting a ground expression'
                initial_values.append(f'{var_name} => {dstr}')

        if initial_values:
            ctxt += ",\n      ".join(initial_values) + ",\n      "
        ctxt += "others => <>);"
        context_decl.append(ctxt)

        # Add monitors, that are variables that must be set by an external
        # module. They are not part of the global state of the process, and
        # are used by observer functions to read/write the system state
        # We don't use pointers because that is incompatible with aliases
        for mon_name, (mon_type, _) in process.monitors.items():
            context_decl.append(f"{mon_name} : {type_name(mon_type)};")

        # Add aliases
        for alias_name, (alias_sort, alias_expr) in process.aliases.items():
            if alias_name in no_renames:
                continue
            _, qualified, _ = expression(alias_expr)
            context_decl.append(f"{alias_name} : {type_name(alias_sort)} "
                                f"renames {qualified};")

        # Add SDL constants (synonyms)
        for const in process.DV.SDL_Constants.values():
            bkind = find_basic_type (const.type).kind
            if bkind in ('IntegerType', 'RealType', 'EnumeratedType',
                         'BooleanType', 'Integer32Type', 'IntegerU8Type'):
                val = const.value
            else:
                # complex value - must be a ground expression
                _, val, _ = expression(const.value, readonly=1)
                if bkind in('SequenceOfType', 'OctetStringType', 'BitStringType'):
                    val = array_content(const.value, val, bkind)
                elif bkind == 'IA5StringType':
                    val = ia5string_raw(const.value)
                else:
                    raise f'ERROR: constant {const.varName} value is not a ground expression'

            const_sort = const.type.ReferencedTypeName.replace('-', '_')
            context_decl.append(f"{const.varName} : constant {ASN1SCC}{const_sort} := {val};")

        # The choice selections will allow to use the present operator
        # together with a variable of the -selection type
        context_decl.extend(choice_selections)
    if stop_condition:
        #  code of stop conditions must use the same type as the main process
        context_decl.append(
                f'{LPREFIX} : {ASN1SCC}{stop_condition}_Context \
                    renames {stop_condition}.{stop_condition}_ctxt;')

    aggreg_start_proc = []
    start_transition = []
    # Continuous State transition id
    if not instance:
        # CS only is declared in the .ads, so that it can be seen by the simulator
        #process_level_decl.append(f'CS_Only : constant := {len(process.transitions)};')

        for name, val in process.mapping.items():
            # Test val, in principle there is a value but if the code targets
            # generation of properties, the model may have been cleaned up and
            # in that case no value would be set..
            if name.endswith('START') and name != 'START' and val:
                process_level_decl.append(f'{name} : constant := {str(val)};')

        # Declare start procedure for aggregate states XXX add in C generator
        # should create one START per "via" clause, TODO later
        for name, substates in process.aggregates.items():
            proc_name = f'procedure {name}{SEPARATOR}START'
            process_level_decl.append(f'{proc_name};')
            aggreg_start_proc.extend([f'{proc_name} is',
                                      'begin'])
            aggreg_start_proc.extend(f'Execute_Transition ({subname.statename}{SEPARATOR}START);'
                                     for subname in substates)
            aggreg_start_proc.extend([f'end {name}{SEPARATOR}START;',
                                     '\n'])

        # Generate the code of the start transition (if process not empty)
        Init_Done = f'{LPREFIX}.Init_Done := True;'
        rand_reset_decl = []
        for rand_g in process.random_generator:
            rand_reset_decl.append(f'Rand_{rand_g}_Pkg.Reset (Gen_{rand_g});');

        start_transition = [
                'procedure Startup is',
                'begin',
                *rand_reset_decl,
                'Execute_Transition (0);'
                if process.transitions else 'null;',
                Init_Done,
                'end Startup;',
                '',
                'begin',
                'Startup;']

    # Generate the TASTE template
    try:
        asn1_modules = '\n'.join([f"with {dv.replace('-', '_')};\nuse {dv.replace('-', '_')};"
                                  for dv in process.asn1Modules])
        if process.asn1Modules:
            asn1_modules += '\nwith adaasn1rtl;\nuse adaasn1rtl;'
    except TypeError:
        asn1_modules = '--  No ASN.1 data types are used in this model'

    taste_template = [f'''\
-- This file was generated automatically by OpenGEODE: DO NOT MODIFY IT !

with System.IO;
use System.IO;

with Ada.Unchecked_Conversion;
with Ada.Numerics.Generic_Elementary_Functions;

package body {process.name} is'''
    if not instance else f'''--  Package body for instance - Generated by OpenGEODE (DO NOT EDIT)
package body {process.name} is''']

    has_cs = any(process.cs_mapping.values())

    generic_spec, instance_decl = "", ""
    if generic:
        generic_spec = "generic\n"
        ri_list = external_ri_list(process)
        if has_context_params:
            # Add context parameter to the process type generics, to make sure
            # the value of the instance is used, not the ASN1 constant of the
            # type.
            generic_spec += f"   {process.name}_ctxt : {ASN1SCC}Context_{process.name};\n"
        if has_cs:
            # For continuous signals the runtime must provide Check_Queue
            generic_spec += "   with procedure Check_Queue (Res : out Asn1Boolean);\n"
        if ri_list:
            generic_spec += "   with " + ";\n   with ".join(ri_list) + ';'
    if instance:
        instance_decl = f"with {process.instance_of_name};"

    # print process.fpar
    # FPAR could be set for Context Parameters. They are available here

    # Generate the source file (.ads) header

    # Stop conditions must import the SDL model they observe
    imp_str = f"with {stop_condition}; use {stop_condition};" \
            if stop_condition else ''

    imp_datamodel = (f"with {process.name}_Datamodel; "
                     f"use {process.name}_Datamodel;") \
                             if not stop_condition and not instance else (
                                     f"with {stop_condition}_Datamodel; "
                                     f"use {stop_condition}_Datamodel;"
                                     if stop_condition else "")

    imp_ri = f"with {process.name}_RI;" if not generic else ""

    rand = ('with Ada.Numerics.Discrete_Random;'
            if process.random_generator else "")
    rand_decl = []
    for each in process.random_generator:
        rand_decl.extend([
            f'type Rand_{each}_ty is new Integer range 1 .. {each};',
            f'package Rand_{each}_Pkg is new  Ada.Numerics.Discrete_Random'\
                    f' (Rand_{each}_ty);',
            f'Gen_{each} : Rand_{each}_Pkg.Generator;',
            f'Num_{each} : Rand_{each}_ty;'])

    ads_template = [f'''\
-- This file was generated automatically by OpenGEODE: DO NOT MODIFY IT !

with Interfaces,
     Interfaces.C.Strings,
     Ada.Characters.Handling;

use Interfaces,
    Interfaces.C.Strings,
    Ada.Characters.Handling;

{asn1_modules}
{imp_datamodel}
{imp_str}
{imp_ri}
{instance_decl}
{rand}
{generic_spec}'''.strip() + f'''
package {process.name} with Elaborate_Body is''']

    ri_stub_ads = [f'''\
--  This file is a stub for the implementation of the required interfaces
--  It is normally overwritten by TASTE with the actual connection to the
--  middleware. If you use Opengeode independently from TASTE you must
--  edit the .adb (body) with your own implementation of these functions.
--  The body stub will be generated only once.

{asn1_modules}

with Interfaces.C.Strings; use Interfaces.C.Strings;

package {process.name}_RI is

   --  In TASTE, used to return the state as char * (but uses malloc so
   --  just return null here - feel free to implement it differently)
   function To_C_Pointer (State_As_String : String) return Chars_Ptr is
      (Null_Ptr);

''']
    ri_stub_adb = [f'''--  Stub generated by OpenGEODE.
--  You can edit this file, it will not be overwritten

package body {process.name}_RI is''']

    dll_api = []
    ads_template.extend(rand_decl)
    if not instance:
        ads_template.extend(context_decl)

    if not generic and not instance and not stop_condition:
        # Add function allowing to trace current state as a string
        # This uses malloc and should be generated only for Linux
        # when Debug is ON
        ads_template.append(
                f"function Get_State return Chars_Ptr "
                f"is ({process.name.title()}_RI.To_C_Pointer "
                f"({ASN1SCC}{process.name}_States'Image ({LPREFIX}.State)))"
                f" with Export, Convention => C, "
                f'Link_Name => "{process.name.lower()}_state";')

    # Declare procedure Startup in .ads
    if not generic:
        ads_template.append(f'procedure Startup'
                            f' with Export, Convention => C,'
                            f' Link_Name => "{process.name}_startup";')
    else:  # function type
        ads_template.append(f'procedure Startup;')


    # Generate the code of the procedures
    inner_procedures_code = []
    for proc in process.content.inner_procedures:
        proc_code, proc_local = generate(proc)
        process_level_decl.extend(proc_local)
        inner_procedures_code.extend(proc_code)
        if proc.exported:
            spelling = proc.inputString
            # Exported procedures are declared in the process
            # We must take the proper spelling (case) from there, since
            # the definition may have a different one.
            for p_decl in process.procedures:
                if p_decl.inputString.lower() == proc.inputString.lower() \
                        and p_decl.referenced:
                    spelling = p_decl.inputString
            # Exported procedures must be declared in the .ads
            pi_header = procedure_header(proc)
            ads_template.append(f'{pi_header};')
            if not proc.external and not generic:
                # Export for TASTE as a synchronous PI
                prefix = f'p{SEPARATOR}' if not proc.exported else ''
                ads_template.append(
                   f'pragma Export (C, {prefix}{proc.inputString},'
                   f' "{process.name.lower()}_PI_{spelling}");')

    # Generate the code for the process-level variable declarations
    taste_template.extend(process_level_decl)

    # Generate the code of internal operators, if needed
    if process.errorstates or process.ignorestates or process.successstates:
        obs_status = [f'function Observer_State_Status return {ASN1SCC}Observer_State_Kind is',
                f'(case {LPREFIX}.State is']
        if process.errorstates:
            opts = ' | '.join(f'{ASN1SCC}{st}' for st in process.errorstates)
            obs_status.append(f'  when {opts} => {ASN1SCC}Error_State,')
        if process.ignorestates:
            opts = ' | '.join(f'{ASN1SCC}{st}' for st in process.ignorestates)
            obs_status.append(f'  when {opts} => {ASN1SCC}Ignore_State,')
        if process.successstates:
            opts = ' | '.join(f'{ASN1SCC}{st}' for st in process.successstates)
            obs_status.append(f'  when {opts} => {ASN1SCC}Success_State,')
        obs_status.append(f'  when others => {ASN1SCC}Regular_State);')
        obs_status.append('\n')
        taste_template.extend(obs_status)

    # Add the code of the procedures definitions
    taste_template.extend(inner_procedures_code)

    # Generate the code of the START procedures of state aggregations
    # XXX to be added to C generator
    taste_template.extend(aggreg_start_proc)

    # Add the code of the DLL interface
    taste_template.extend(dll_api)

    # Generate the code for each input signal (provided interface) and timers
    for signal in process.input_signals + [
                        {'name': timer} for timer in process.timers]:
        if stop_condition:
            # dont generate anything in stop_condition functions
            break

        if 'renames' in signal and signal['renames'] is not None:
            # don't generate anything if this is an observer signal
            # (a renames clause for a continuous signal)
            continue

        signame = signal.get('name', 'START')
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
            fake_name = f'{signame}_Transition'

        if signame == 'START':
            continue
        pi_header = f'procedure {fake_name or signame}'
        param_name = signal.get('param_name') or f'{signame}_param'
        # Add (optional) PI parameter (only one is possible in TASTE PI)
        if 'type' in signal:
            typename = type_name(signal['type'])
            pi_header += f'({param_name}: in out {typename})'

        # Add declaration of the provided interface in the .ads file
        ads_template.append(f'--  Provided interface "{signame}"')
        ads_template.append(pi_header + ';')

        if not generic and not ignore_export:
            ads_template.append(
                    f'pragma Export(C, {signame},'
                    f' "{process.name.lower()}_PI_{signame}");')

        pi_header += ' is'
        taste_template.append(pi_header)
        taste_template.append('begin')

        def execute_transition(state, dest=[]):
            ''' Generate the code that triggers the transition for the current
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
                    dest.append(f'p{SEPARATOR}{each}{SEPARATOR}exit;')

            if input_def:
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    dest.append(f'{LPREFIX}.{inp} := {param_name};')
                # Execute the corresponding transition
                if input_def.transition:
                    dest.append(f'Execute_Transition ({input_def.transition_id});')
                else:
                    #taste_template.append('Execute_Transition (CS_Only);')
                    # removed: CS_Only in "when others" branch
                    return False
            else:
                return False
                # removed: CS_Only in "when others" branch
                #taste_template.append('Execute_Transition (CS_Only);')
            return True

        if not instance:
            taste_template.append(f'case {LPREFIX}.state is')

        def case_state(state):
            ''' Recursive function (in case of state aggregation) to generate
                the code that calls the proper transition according
                to the current state
                The input name is in signame
            '''
            if state.endswith('START'):
                return
            #taste_template.append(f'when {ASN1SCC}{state} =>')
            statecase = [f'when {ASN1SCC}{state} =>']
            input_def = process.input_mapping[signame].get(state)
            if state in process.aggregates.keys():
                taste_template.extend(statecase)
                # State aggregation:
                # - find which substate manages this input
                # - add a switch case on the corresponding substate
                taste_template.append('--  This is a state aggregation')
                for sub in process.aggregates[state]:
                    if [a for a in sub.mapping.keys()
                            if a in process.input_mapping[signame].keys()]:
                        taste_template.append('case '
                               f'{LPREFIX}.{sub.statename}{SEPARATOR}state is')
                        for par in sub.mapping.keys():
                            case_state(par)
                        taste_template.append('when others =>')
                        taste_template.append('Execute_Transition (CS_Only);')
                        taste_template.append('end case;')
                        break
                else:
                    # Input is not managed in the state aggregation
                    if input_def:
                        # check if it is managed one level above
                        execute_transition(state, taste_template)
                    else:
                        taste_template.append('Execute_Transition (CS_Only);')
            else:
                if execute_transition(state, statecase):
                    taste_template.extend(statecase)

        if not instance:
            for each_state in reduced_statelist:
                case_state(each_state)
            taste_template.append('when others =>')
            taste_template.append('Execute_Transition (CS_Only);')
            taste_template.append('end case;')
        else:
            inst_call = f"{process.name}_Instance.{signame}"
            if 'type' in signal:
                inst_call += f" ({param_name})"
            taste_template.append(f"{inst_call};")

        taste_template.append(f'end {fake_name or signame};')
        taste_template.append('\n')

    #  add call to startup function for instances
    if instance:
        taste_template.extend(['procedure Startup is',
                               'begin',
                               f'{process.name}_Instance.Startup;',
                               'end Startup;',
                               ''])

    # for the .ads file, generate the declaration of the required interfaces
    # output signals are the asynchronous RI - only one parameter
    for signal in process.output_signals:
        sig = signal['name']
        param_name = signal.get('param_name') or f'{sig}_param'
        # Add (optional) RI parameter
        param_spec = ''
        if 'type' in signal:
            typename = type_name(signal['type'])
            if 'PID' in TYPES:
                # the PID type is provided by TASTE, does not exist otherwise
                param_spec = f'({param_name} : in out {typename}; Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)'
            else:
                param_spec = f'({param_name} : in out {typename})'
        else:
            if 'PID' in TYPES:
                # the PID type is provided by TASTE, does not exist otherwise
                param_spec = f'(Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)'
            else:
                param_spec = ''
        if not generic:
            ads_template.append('--  {}equired interface "{}"'
                                .format("Paramless r" if not 'type' in signal
                                    else "R", sig))

            if not instance:
                ads_template.append(f'procedure RI{SEPARATOR}{sig}{param_spec} '
                    f'renames {process.name}_RI.{sig};')
            ri_stub_ads.append(f'procedure {sig}{param_spec};')
            ri_stub_adb.append(f'procedure {sig}{param_spec} is null;')
            #  TASTE generates the pragma import in <function>_ri.ads
            #  therefore do not generate it in the .ads
            # ads_template.append(f'pragma Import (C, RI{SEPARATOR}{sig}, "{process.name.lower()}_RI_{sig}");')

    # for the .ads file, generate the declaration of the external procedures
    for proc in (proc for proc in process.procedures if proc.external):
        sig = proc.inputString
        ri_header = f'procedure RI{SEPARATOR}{sig}'
        params = []
        params_spec = ""
        for param in proc.fpar:
            typename = type_name(param['type'])
            name     = param['name']
            if param['direction'] == 'in':
                direct = 'in out'
            else:
                direct = 'out'

            params.append(f'{name} : {direct} {typename}')
        if params:
            if 'PID' in TYPES:
                # the PID type is provided by TASTE, does not exist otherwise
                params_spec = f' ({"; ".join(params)}; Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)'
            else:
                params_spec = f' ({"; ".join(params)})'
            ri_header += params_spec
        else:
            if 'PID' in TYPES:
                # the PID type is provided by TASTE, does not exist otherwise
                params_spec = f' (Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env)'
            else:
                params_spec = ''
            ri_header += params_spec

        if not generic:
            if not instance:
                # Type and instance do not need this declarations, only standalone
                # processes.
                ads_template.append(f'--  Synchronous Required Interface "{sig}"')
                ads_template.append(f'{ri_header} renames {process.name}_RI.{sig};')
            ri_stub_ads.append(f'procedure {sig}{params_spec};')
            ri_stub_adb.append(f'procedure {sig}{params_spec} is null;')

    # for the .ads file, generate the declaration of timers set/reset functions
    for timer in process.timers:
        if stop_condition:
            # don't generate timer code for stop conditions
            break
        ads_template.append(f'--  Timer {timer} SET and RESET functions')

        if not generic:
            procname = process.name.lower()
            if 'PID' in TYPES:
                ads_template.append(
                   f'procedure SET_{timer} (Val : in out {ASN1SCC}T_UInt32; Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env) '
                   f'renames {process.name}_RI.Set_{timer};')
                ads_template.append(
                   f'procedure RESET_{timer} (Dest_PID : {ASN1SCC}PID := {ASN1SCC}Env) '
                   f'renames {process.name}_RI.Reset_{timer};')
            else:
                ads_template.append(
                   f'procedure SET_{timer} (Val : in out {ASN1SCC}T_UInt32) '
                   f'renames {process.name}_RI.Set_{timer};')
                ads_template.append(
                   f'procedure RESET_{timer} renames {process.name}_RI.Reset_{timer};')
            ri_stub_ads.append(f'procedure SET_{timer} (Val : in out {ASN1SCC}T_UInt32);')
            ri_stub_adb.append(f'procedure SET_{timer} (Val : in out {ASN1SCC}T_UInt32) is null;')
            ri_stub_ads.append(f'procedure RESET_{timer};')
            ri_stub_adb.append(f'procedure RESET_{timer} is null;')
        else:
            # Generic functions get the SET and RESET from template
            pass


    if instance:
        # Instance of a process type, all the RIs (including timers) must
        # be gathered to instantiate the package
        pkg_decl = (f"package {process.name}_Instance is new {process.instance_of_name}")
        ri_list = [(f"RI{SEPARATOR}{sig['name']}", sig['name'])
                   for sig in process.output_signals]
        if has_cs:
            ri_list.append(("Check_Queue", "Check_Queue"))
        ri_list.extend ([(f"RI{SEPARATOR}{proc.inputString}", proc.inputString)
                        for proc in process.procedures if proc.external])
        ri_list.extend([(f"set_{timer}", f"set_{timer}")   for timer in process.timers])
        ri_list.extend([(f"reset_{timer}", f"reset_{timer}") for timer in process.timers])
        ri_inst = [f"{ri[0]} => {process.name.title()}_RI.{ri[1]}" for ri in ri_list]
        if ri_inst or has_context_params:
            pkg_decl += " ("
        if ri_inst:
            pkg_decl += f'{", ".join(ri_inst)}'
        if has_context_params:
            if ri_inst:
                pkg_decl += ", "
            # Add instance-value of the context parameters
            pkg_decl += f"{process.instance_of_name}_ctxt => {process.name}_ctxt"
        if ri_inst or has_context_params:
            pkg_decl += ")"
        ads_template.append(f"{pkg_decl};")
        ads_template.append(
               f"function Get_State return chars_ptr "
               f"is ({process.name}_RI.To_C_Pointer ({process.name}_Instance.{LPREFIX}.State'Img))"
               f" with Export, Convention => C, "
               f'Link_Name => "{process.name.lower()}_state";')

        # Expose Execute_Transition, needed by the simulator to execute continuous signals
        ads_template.append(f'procedure Execute_Transition (Id : Integer) renames {process.name}_Instance.Execute_Transition;')
        ads_template.append(f'CS_Only : constant := {process.name}_Instance.CS_Only;')

    else:
        ads_template.append(f'procedure Execute_Transition (Id : Integer);')
        ads_template.append(f'CS_Only : constant := {len(process.transitions)};')



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

    # Generate the code of the Execute_Transition  procedure, if needed
    if process.transitions and not instance:
        taste_template.append('procedure Execute_Transition (Id : Integer) is')
        taste_template.append('trId : Integer := Id;')
        if has_cs:
            taste_template.append('Message_Pending : Asn1Boolean := True;')

        # Declare the local variables needed by the transitions in the template
        taste_template.extend(set(local_decl_transitions))
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

        taste_template.append('when CS_Only =>')
        taste_template.append('trId := -1;')
        taste_template.append('goto Continuous_Signals;')

        taste_template.append('when others =>')
        taste_template.append('null;')

        taste_template.append('end case;')
        if code_labels:
            # Due to nested states (chained transitions) jump over label code
            # (NEXTSTATEs do not return from Execute_Transition)
            taste_template.append('goto Continuous_Signals;')

        # Add the code for the floating labels
        taste_template.extend(code_labels)

        taste_template.append('<<Continuous_Signals>>')

        # After completing active transition(s), check continuous signals:
        #     - Check current state(s)
        #     - For each continuous signal generate code (test+transition)
        # XXX add to C backend
        if has_cs:
            if not MONITORS:
                taste_template.append('--  Process continuous signals')
                taste_template.append(f'if {LPREFIX}.Init_Done then')
                taste_template.append("Check_Queue (Message_Pending);")
                taste_template.append('end if;')
                if not generic:  # not a function type
                    ads_template.append('procedure Check_Queue (Res : out Asn1Boolean)')
                    ads_template.append(f'with Import, Convention => C, '
                                        f'Link_Name => "{process.name.lower()}_check_queue";')
            else:
                taste_template.append('--  Process observer transitions')
                taste_template.append("Message_Pending := False;")
        if has_cs:
            taste_template.extend(['if Message_Pending or trId /= -1 then',
                                      'goto Next_Transition;',
                                   'end if;'])
        #else:
        #    taste_template.append('null;')

        # Process the continuous signals in state aggregations first
        # (reminder: state aggregations = parallel states)
        done = []
        sep = 'if '
        last = ''
        # flag indicating there are CS in nested states but not at root
        need_final_endif = False
        first_of_aggreg = True
        for cs, agg in product(process.cs_mapping.items(),
                               process.aggregates.items()):
            (statename, cs_item)  = cs
            (agg_name, substates) = agg

            if not cs_item:
                continue
            for each in substates:
                if statename in each.cs_mapping and each.cs_mapping[statename]:
                    if first_of_aggreg:
                        taste_template.append(
                                f'if {LPREFIX}.State = {ASN1SCC}{agg_name} then')
                        first_of_aggreg = False
                    need_final_endif = True
                    first = "els" if done else ""
                    taste_template.append(
                            f'if {LPREFIX}.{each.statename}{SEPARATOR}State = '
                            f'{ASN1SCC}{statename} then')
                    # Change priority 0 (no priority set) to lowest priority
                    lowest_priority = max(item.priority for item in cs_item)
                    for each in cs_item:
                        if each.priority == 0:
                            each.priority = lowest_priority + 1
                    for provided_clause in sorted(cs_item,
                                                 key=lambda itm: itm.priority):
                        taste_template.append(f'--  Priority {provided_clause.priority}')
                        trId = process.transitions.index\
                                            (provided_clause.transition)
                        code, loc = generate(provided_clause.trigger,
                                             branch_to=trId,
                                             sep=sep, last=last)
                        code.append('goto Next_Transition;')
                        sep='elsif '
                        taste_template.extend(code)
                    done.append(statename)
                    taste_template.append('end if;')  # inner if
                    taste_template.append('end if;')  # substate if
                    sep = 'if '
                    break

        for statename in process.cs_mapping.keys() - done:
            cs_item = process.cs_mapping[statename]
            if cs_item:
                need_final_endif = False
                first = "els" if done else ""
                taste_template.append(
                        f'{first}if {LPREFIX}.State = {ASN1SCC}{statename}'
                        ' then')
            # Change priority 0 (no priority set) to lowest priority
            if cs_item:
                lowest_priority = max(item.priority for item in cs_item)
            for each in cs_item:
                if each.priority == 0:
                    each.priority = lowest_priority + 1
            for provided_clause in sorted(cs_item,
                                          key=lambda itm: itm.priority):
                taste_template.append(f'--  Priority: {provided_clause.priority}')
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
                        exitcalls.append(f"p{SEPARATOR}{each}{SEPARATOR}exit;")

                code, loc = generate(provided_clause.trigger,
                                     branch_to=trId, sep=sep, last=last,
                                     exitcalls=exitcalls)
                sep='elsif '
                taste_template.extend(code)
            if cs_item:
                taste_template.append('end if;') # inner if
                taste_template.append('end if;') # current state
            sep = 'if '

        if need_final_endif:
            taste_template.append('end if;')

        taste_template.append('<<Next_Transition>>')
        taste_template.append('end loop;')
        taste_template.append('end Execute_Transition;')
        taste_template.append('\n')
    elif not instance:
        # No transitions defined, but keep the interface for CS_Only calls
        taste_template.append('procedure Execute_Transition (Id : Integer) is null;')
        taste_template.append('\n')

    # Add code of the package elaboration
    taste_template.extend(start_transition)
    taste_template.append(f'end {process.name};')

    ads_template.append(f'end {process.name};')

    ri_stub_ads.append(f'end {process.name}_RI;')
    ri_stub_adb.append(f'end {process.name}_RI;')

    with open(process.name.lower() + os.extsep + 'adb', 'wb') as ada_file:
        code = '\n'.join(format_ada_code(taste_template)).encode('latin1')
        ada_file.write(code)

    with open(process.name.lower() + os.extsep + 'ads', 'wb') as ada_file:
        ada_file.write(
                '\n'.join(format_ada_code(ads_template)).encode('latin1'))

    if not taste:
        with open(f"{process.name.lower()}_ri.ads", "wb") as ri_stub:
            ri_stub.write ("\n".join(format_ada_code(ri_stub_ads)).encode('latin1'))
        stub_adb = f'{process.name.lower()}_ri.adb'
        # don't overwrite adb as it may contain user code
        # also don't generate if there are no RI in the system
        if not os.path.exists(stub_adb) and len(ri_stub_adb) > 2:
            with open(stub_adb, "wb") as ri_stub:
                ri_stub.write ("\n".join(format_ada_code(ri_stub_adb)).encode('latin1'))

    with open(f"{process.name.lower()}_ada.gpr", "wb") as gprada:
        gprada.write(ada_gpr.encode('utf-8'))

    if process_instance is not process:
        # Generate an instance of the process type, too.
        # First copy the list of timers to the instance (otherwise the
        # instance would miss some PIs and RIs to set the actual timers)
        process_instance.timers = process.timers
        # And for the same reason copy the continuous states, needed to
        # determine if Check_Queue is needed
        process_instance.cs_mapping = process.cs_mapping
        generate(process_instance, simu, instance=True, taste=taste)

def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    code = []
    string = ''
    local = []
    basic_type = find_basic_type(param.exprType) or {}
    type_kind = basic_type.kind
    if isinstance(param, ogAST.ExprAppend):
        # Append: call Put_Line separately for each side of the expression
        st1, _, lcl1 = write_statement(param.left,  newline = False)
        st2, _, lcl2 = write_statement(param.right, newline = False)
        code.extend(st1)
        code.extend(st2)
        local.extend(lcl1)
        local.extend(lcl2)
    elif type_kind == 'IA5StringType':
        # IA5String are null-terminated to match the C representation
        # ASN1SCC API offers the getStringSize function to read the actual size
        code, string, local = expression(param, readonly=1)
        code.append(f'Put ({string} (1 .. adaasn1rtl.GetStringSize ({string})));')
    elif type_kind.endswith('StringType'):
        if isinstance(param, ogAST.PrimOctetStringLiteral):
            # Octet string or bit string
            code.append(f'Put ("{param.printable_string}");')
        elif isinstance(param, ogAST.PrimStringLiteral):
            # Raw string
            # First remove the newline statements and handle escaping
            text = param.value[1:-1]
            text = text.replace("\\'", "'").replace('\\"', '"')
            text = text.replace('"', '""').split('\n')
            for idx, val in enumerate(text):
                code.append(f'Put ("{val}");')
                if len(text) > 1 and idx < len(text) - 1:
                    code.append('New_Line;')
        else:
            code, string, local = expression(param, readonly=1)
            if type_kind == 'OctetStringType':
                # Octet string -> convert to Ada string
                last_it = ""
                if isinstance(param, ogAST.PrimSubstring):
                    range_str = f"{string}'Range"
                    iterator = f"i - {string}'First + 1"
                elif basic_type.Min == basic_type.Max:
                    range_str = f"{string}.Data'Range"
                    string += ".Data"
                    iterator = "i"
                else:
                    range_str = f"1 .. {string}.Length"
                    string += ".Data"
                    iterator = "i"
                    last_it = f"({range_str})"
                code.extend([f"for i in {range_str} loop",
                             f"Put (Character'Val({string}(i)));",
                             "end loop;"])
            else:
                code.append(f"Put ({string});")
    elif type_kind in ('IntegerType', 'RealType',
                       'BooleanType', 'Integer32Type', 'IntegerU8Type'):
        code, string, local = expression(param, readonly=1)
        if hasattr(param, "expected_type"):
            cast = type_name(param.expected_type)
        else:
            cast = type_name(param.exprType)
        code.append(f"Put ({cast}'Image ({string}));")
    elif type_kind == 'EnumeratedType':
        code, string, local = expression(param, readonly=1)
        #code.append(f"Put ({type_name(param.exprType)}'Image ({string}));")
        # enumerated must be variable, so we can use 'Img
        code.append(f"Put ({string}'Img);")
    else:
        error = ('Unsupported parameter in write call ' +
                param.inputString + '(type kind: ' + type_kind + ')')
        LOG.error(error)
        raise TypeError(error)
    if newline:
        code.append("New_Line;")
    return code, string, local


@generate.register(ogAST.Output)
@generate.register(ogAST.ProcedureCall)
def _call_external_function(output, **kwargs):
    ''' Generate the code of a set of output or procedure call statement '''
    code = []
    local_decl = []

    # Add the traceability information
    code.extend(traceability(output))
    #code.extend(debug_trace())

    # Calling a procedure or RI usually needs a prefix (RI_.. or p_...)
    # Exception is the _Transition procedures called after exported PIs (RPC)
    need_prefix = True

    for out in output.output:
        signal_name = out['outputName']
        list_of_params = []

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
            p_code, p_id, p_local = expression(param, readonly=1)
            code.extend(p_code)
            local_decl.extend(p_local)
            code.append(f'RESET_{p_id};')
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
            local_decl.append(f'{tmp_id} : {ASN1SCC}T_UInt32;')
            code.append(f'{tmp_id} := {t_val};')
            code.append(f"SET_{p_id} ({tmp_id});")
            continue
        proc, out_sig = None, None
        try:
            out_sig, = [sig for sig in OUT_SIGNALS
                        if sig['name'].lower() == signal_name.lower()]
        except ValueError:
            # Not an output, try if it is an external or inner procedure
            try:
                proc, = [sig for sig in PROCEDURES
                            if sig.inputString.lower() == signal_name.lower()]
                if proc.external:
                    out_sig = proc
            except ValueError:
                # Last chance to find it: if it is an exported procedure,
                # in that case an additional signal with _Transition suffix
                # exists but is not visible in the model at this point
                for sig in PROCEDURES:
                    if signal_name.lower() == f'{sig.inputString.lower()}_transition':
                        out_sig = sig
                        need_prefix = False
                        break
                else:
                    # Not there? Impossible, the parser would have barked
                    # Can happen with stop conditions because they are defined
                    # as exported but the _Transition signal was not added
                    LOG.warning(f'Could not find signal/procedure: {signal_name} - ignoring call')
                    return code, local_decl
        if out_sig:
            dest_pid = out.get('toDest') or 'env'
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
                p_code, p_id, p_local = expression(param, readonly=1)
                code.extend(p_code)
                local_decl.extend(p_local)
                # Create a temporary variable for input parameters only
                # (If needed, i.e. if argument is not a local variable)
                if param_direction == 'in' \
                        and (not (isinstance(param, ogAST.PrimVariable)
                        and p_id.startswith(LPREFIX)) # NO FIXME WITH CTXT
                        or isinstance(param, ogAST.PrimFPAR)):
                    tmp_id = f'tmp{out["tmpVars"][idx]}'
                    #local_decl.extend(debug_trace())
                    local_decl.append(f'{tmp_id} : {typename};')
                    basic_param = find_basic_type (param_type)
                    if basic_param.kind.startswith('Integer'):
                        p_id = f"{typename} ({p_id})"
                    if isinstance(param,
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                        if basic_param.kind == 'IA5StringType':
                            p_id = ia5string_raw(param)
                        elif basic_param.kind.startswith('Integer'):
                            p_id = str(param.numeric_value)
                        else:
                            p_id = array_content(param, p_id, basic_param)

                    if isinstance(param, ogAST.ExprAppend):
                        # Process Append constructs properly when they are
                        # used as raw params (e.g. callme(a//b//c))
                        # TODO: ogAST.PrimSubstring seem to be missing
                        # Check the template in def _conditional
                        app_len = append_size(param)
                        #code.extend(debug_trace())
                        code.append(f'{tmp_id}.Data (1 .. {app_len}) := {p_id};')
                        if basic_param.Min != basic_param.Max:
                            # Append should only apply to this case, i.e.
                            # types of varying length...
                            code.append(f'{tmp_id}.Length := {app_len};')
                    else:
                        code.append(f'{tmp_id} := {p_id};')
                    list_of_params.append(tmp_id)
                else:
                    # Output parameters/local variables
                    list_of_params.append(p_id)
            name = out["outputName"]
            if list_of_params:
                params=', '.join(list_of_params)
                if dest_pid != 'env' and 'PID' in TYPES:
                    code.append(f'RI{SEPARATOR}{name}({params}, Dest_PID => {ASN1SCC}{dest_pid});')
                else:
                    code.append(f'RI{SEPARATOR}{name}({params});')

            else:
                prefix = f'RI{SEPARATOR}' if need_prefix else ''
                if dest_pid != 'env' and 'PID' in TYPES:
                    code.append(f'{prefix}{name}(Dest_PID => {ASN1SCC}{dest_pid});')
                else:
                    code.append(f'{prefix}{name};')
        else:
            # inner procedure call without a RETURN statement
            # retrieve the procedure signature
            ident = proc.inputString
            p, = [p for p in PROCEDURES if p.inputString.lower() == ident.lower()]

            list_of_params = []
            for idx, param in enumerate(out.get('params', [])):
                # Expected basic type of the parameter
                param_type = p.fpar[idx]['type']
                basic_param = find_basic_type (param_type)

                p_code, p_id, p_local = expression(param, readonly=1)

                # We need to format strings properly, this depends on the expected
                # type of the procedure parameter
                if isinstance(param,
                        (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                    if basic_param.kind == 'IA5StringType':
                        p_id = ia5string_raw(param)
                    elif basic_param.kind.startswith('Integer'):
                        p_id = str(param.numeric_value)
                    else:
                        p_id = array_content(param, p_id, basic_param)

                code.extend(p_code)
                local_decl.extend(p_local)
                # no need to use temporary variables, we are in pure Ada
                list_of_params.append(p_id)
            if list_of_params:
                code.append(f'p{SEPARATOR}{proc.inputString}({", ".join(list_of_params)});')
            else:
                code.append(f'p{SEPARATOR}{proc.inputString};')
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
        try:
            code_assign, _, decl_assign = expression(expr)
        except TypeError as err:
            raise TypeError(f"{str(err)} - TaskAssign: '{task.inputString}' (please report this bug)")
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
    local_scope = dict(LOCAL_VAR)
    if task.comment:
        stmt.extend(traceability(task.comment))
    stmt.extend(traceability(task))
    for loop in task.elems:
        if loop['range']:
            start_str, stop_str = '0', ''

            if loop['range']['start']:
                basic = find_basic_type(loop['range']['start'].exprType)
                start_stmt, start_str, start_local = \
                        expression(loop['range']['start'])

                if not is_numeric(start_str):
                    start_str = f"Integer ({start_str})"

                local_decl.extend(start_local)
                stmt.extend(start_stmt)

            if loop['range']['step'] == 1:
                start_str += ' .. '

            basic = find_basic_type(loop['range']['stop'].exprType)
            stop_stmt, stop_str, stop_local = expression(loop['range']['stop'])

            if not is_numeric(stop_str):
                stop_str = f"Integer ({stop_str})"

            local_decl.extend(stop_local)
            stmt.extend(stop_stmt)
            if loop['range']['step'] == 1:
                if str.isnumeric(stop_str):
                    stop_str = str(int(stop_str) - 1)
                else:
                    stop_str = '{} - 1'.format(stop_str)
                stmt.append('for {it} in {start}{stop} loop'
                            .format(it=loop['var'],
                                    start=start_str,
                                    stop=stop_str))
            else:
                # Step is not directly supported in Ada, we need to use 'while'
                stmt.extend(['declare',
                             f'{loop["var"]} : Integer := {start_str};',
                             '',
                             'begin',
                             f'while {loop["var"]} < {stop_str} loop'])
            # Add iterator to the list of local variables
            LOCAL_VAR.update({loop['var']: (loop['type'], None)})
        else:
            # case of form: FOR x in SEQUENCE OF
            # Add iterator to the list of local variables
            LOCAL_VAR.update({loop['var']: (loop['type'], None)})

            list_stmt, list_str, list_local = expression(loop['list'])
            basic_type = find_basic_type(loop['list'].exprType)
            list_payload = list_str + string_payload(loop['list'], list_str)
            if isinstance(loop['list'], ogAST.PrimSubstring) or \
                    basic_type.Min == basic_type.Max:
                range_str = f"{list_payload}'Range"
            else:
                range_str = f"1 .. {list_str}.Length"
            stmt.extend(list_stmt)
            local_decl.extend(list_local)
            stmt.extend(['declare',
                         f'{loop["var"]} : {type_name(loop["type"])};',
                         '',
                         'begin',
                         f'for {loop["var"]}_idx in {range_str} loop',
                         f'{loop["var"]} := {list_payload}({loop["var"]}_idx);'])
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
    # Restore list of local variables
    LOCAL_VAR.clear()
    LOCAL_VAR.update(local_scope)
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
def _primary_variable(prim, **kwargs):
    ''' Single variable reference '''
    var = find_var(prim.value[0])
    if (not var) or is_local(var):
        sep = ''
    else:
        sep = LPREFIX + '.'

    ada_string = f'{sep}{prim.value[0]}'

    return [], str(ada_string), []


@expression.register(ogAST.PrimCall)
def _prim_call(prim, **kwargs):
    ''' Cover all built-in functions and inner procedures with RETURN stmt '''
    stmts, ada_string, local_decl = [], '', []

    ident = prim.value[0].lower()
    params = prim.value[1]['procParams']

    if ident in ('abs', 'fix', 'float', 'chr'):

        # Fix operator: make a cast depending on the lower range
        unsigned = False
        if ident == 'fix':
            unsigned = float(find_basic_type(params[0].exprType).Min) >= 0


        param_stmts, param_str, local_var = expression(params[0], readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += '{op}({param})'.format(
                param=param_str,
                op='abs'           if ident == 'abs'
                else 'Asn1Int'     if (ident == 'fix'  and not unsigned)
                else 'Asn1UInt'    if (ident == 'fix'  and unsigned)
                else 'Asn1Byte'    if ident == 'chr'
                else 'Asn1Real'    if ident  == 'float' else 'ERROR')

    elif ident == 'power':
        operands = [None, None]
        for idx, param in enumerate(params):
            stmt, operands[idx], local = expression(param, readonly=1)
            stmts.extend(stmt)
            local_decl.extend(local)
        ada_string += f'{operands[0]} ** Natural({operands[1]})'

    elif ident == 'length':
        # Length of sequence of: take only the first parameter
        # return an Integer32 type
        exp = params[0]
        exp_type = find_basic_type(exp.exprType)
        min_length = getattr(exp_type, 'Min', None)
        max_length = getattr(exp_type, 'Max', None)
        if min_length is None or max_length is None:
            error = f'{exp.inputString} is not a SEQUENCE OF'
            LOG.error(error)
            raise TypeError(error)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        if min_length == max_length \
                and not isinstance(exp, ogAST.PrimSubstring):
            ada_string += min_length
        else:
            if isinstance(exp, ogAST.PrimSubstring):
                range_str = f"{param_str}'Length"
            else:
                range_str = f"{param_str}.Length"
            ada_string += range_str

    elif ident == 'present':
        # User wants to know what CHOICE element is present
        exp = params[0]
        # Get the basic type to make sure it is a choice
        exp_type = find_basic_type(exp.exprType)
        # Also get the ASN.1 type name as it is
        # needed to build the Ada expression
        exp_typename = type_name(exp.exprType, use_prefix=False)
        if exp_type.kind != 'ChoiceType':
            error = f'{exp.inputString} is not a CHOICE'
            LOG.error(error)
            raise TypeError(error)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += f'To_{exp_typename}_Selection ({param_str}.Kind)'

    elif ident == 'choice_to_int':
        p1, p2 = params
        sort = find_basic_type (p1.exprType)
        assert (sort.kind == 'ChoiceType')  # normally checked by the parser
        param_stmts, varstr, local_var = expression(p1, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        param_stmts, defaultstr, local_var = expression(p2, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += (f'(case {varstr}.Kind is ')
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
            child_name_ada = child_name.replace('-', '_')
            child_id   = descr.EnumID
            child_sort = find_basic_type(descr.type)
            if not child_sort.kind.startswith('Integer'):
                need_default = True
                continue
            set_value = f'{varstr}.{child_name_ada}'
            if need_cast and float(child_sort.Min) >= 0.0:
                set_value = f'Asn1Int({set_value})'
            choices.append(f'when {child_id} => {set_value}')
        if need_default:
            choices.append(f'when others => {defaultstr}')
        ada_string += ', '.join(choices) + ')'

    elif ident in ('shift_left', 'shift_right'):
        p1, p2 = params
        param_stmts, s1, local_var = expression(p1, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        param_stmts, s2, local_var = expression(p2, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        fcn = 'Shift_Left' if ident == "shift_left" else 'Shift_Right'
        ada_string += f'{fcn} ({s1}, {s2})'

    elif ident == 'exist':
        # User wants to know if an optional field is present or not
        selector = params[0]  # type PrimSelector
        receiver = selector.value[0]
        field    = selector.value[1]
        rec_stmt, rec_str, rec_decl = expression (receiver, readonly=1)
        stmts.extend(rec_stmt)
        local_decl.extend(rec_decl)
        ada_string += f'({rec_str}.exist.{field} = 1)'

    elif ident in ('to_selector', 'to_enum'):
        variable, target_type = params
        var_typename = type_name (variable.exprType, False)
        var_stmts, var_str, var_decl = expression (variable, readonly=1)
        stmts.extend(var_stmts)
        local_decl.extend(var_decl)
        destSort = target_type.value[0]
        sortAda = destSort.replace('-', '_')
        sort_name = f'{PROCESS_NAME}_Datamodel.{ASN1SCC}{PROCESS_NAME}_{sortAda}_selection'
        if ident == 'to_selector':
            ada_string += f"{sort_name}'Val ({ASN1SCC}{var_typename}'Pos ({var_str}))"
        elif ident == 'to_enum':
            sort_name_val = f'{ASN1SCC}{sortAda}'
            sort_name = f'{PROCESS_NAME}_Datamodel.{ASN1SCC}{PROCESS_NAME}_{var_typename}'
            ada_string += f"{sort_name_val}'Val ({sort_name}'Pos ({var_str}))"

    elif ident == 'val':
        variable, target_type = params
        var_typename = type_name (variable.exprType)
        var_stmts, var_str, var_decl = expression (variable, readonly=1)
        stmts.extend(var_stmts)
        local_decl.extend(var_decl)
        sort_name = ASN1SCC + target_type.value[0].replace('-', '_')
        ada_string += f"{sort_name}'Enum_Val ({var_str})"

    elif ident == 'num':
        # User wants to get an enumerated corresponding integer value
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        # 'Enum_Rep gives directly the universal integer of an enumerated
        # (was in GNAT, now in Ada 2020)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += f"{param_str}'Enum_Rep"

    elif ident == 'floor':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += f"{exp_typename}'Floor({param_str})"

    elif ident == 'ceil':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += f"{exp_typename}'Ceiling({param_str})"

    elif ident == 'cos':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += f"Math.Cos({param_str})"

    elif ident == 'round':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += f"{exp_typename}'Rounding({param_str})"

    elif ident == 'sin':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += f"Math.Sin({param_str})"

    elif ident == 'sqrt':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += f"Math.Sqrt({param_str})"

    elif ident == 'trunc':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += f"{exp_typename}'Truncation({param_str})"

    elif ident == 'observer_status':
        #  For observers (model checking) only: return the state status
        #  The procedure is generated at process level when it is needed
        ada_string += f"Observer_State_Status"

    else:
        # inner procedure call (with a RETURN statement)
        # retrieve the procedure signature
        p, = [p for p in PROCEDURES if p.inputString.lower() == ident.lower()]

        # for inner procedures we do not use a temporary variable because
        # we remain in Ada and therefore in parameters do not need to
        # be pointers (in out).
        ada_string += f'p{SEPARATOR}{ident}' + (' (' if params else '')
        # Take all params and join them with commas
        list_of_params = []
        for idx, param in enumerate(params):
            # Expected basic type of the parameter
            param_type = p.fpar[idx]['type']
            basic_param = find_basic_type (param_type)

            param_stmt, param_str, local_var = expression(param, readonly=1)

            # We need to format strings properly, this depends on the expected
            # type of the procedure parameter
            if isinstance(param,
                    (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                if basic_param.kind == 'IA5StringType':
                    param_str = ia5string_raw(param)
                elif basic_param.kind.startswith('Integer'):
                    param_str = str(param.numeric_value)
                else:
                    param_str = array_content(param, param_str, basic_param)

            list_of_params.append(param_str)
            stmts.extend(param_stmt)
            local_decl.extend(local_var)
        ada_string += ', '.join(list_of_params)
        ada_string += ')' if params else ''

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimIndex)
def _prim_index(prim, **kwargs):
    stmts, ada_string, local_decl = [], '', []
    ro = kwargs.get("readonly", 0)

    receiver = prim.value[0]

    receiver_stms, ada_string, receiver_decl = expression(receiver,
                                                          readonly=ro)
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    index = prim.value[1]['index'][0]
    idx_stmts, idx_string, idx_var = expression(index, readonly=ro)
    if str.isnumeric(idx_string):
        idx_string = int(idx_string) + 1
    else:
        idx_string = f'1 + Integer ({idx_string})'
    if not isinstance(receiver, ogAST.PrimSubstring):
        ada_string += '.Data'
    ada_string += f'({idx_string})'
    stmts.extend(idx_stmts)
    local_decl.extend(idx_var)

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimSubstring)
def _prim_substring(prim, **kwargs):
    ''' Generate expression for SEQOF/OCT.STRING substrings, e.g. foo(1,2) '''
    stmts, ada_string, local_decl = [], '', []
    ro = kwargs.get("readonly", 0)

    receiver = prim.value[0]
    receiver_stms, receiver_string, receiver_decl = expression(receiver,
                                                               readonly=ro)
    ada_string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    r1_stmts, r1_string, r1_local = expression(prim.value[1]['substring'][0],
                                               readonly=ro)
    r2_stmts, r2_string, r2_local = expression(prim.value[1]['substring'][1],
                                               readonly=ro)

    # Adding 1 because SDL starts indexes at 0, ASN1 Ada types at 1
    if str.isnumeric(r1_string):
        r1_string = str(int(r1_string) + 1)
    else:
        r1_string = f"Integer ({r1_string}) + 1"
    if str.isnumeric(r2_string):
        r2_string = str(int(r2_string) + 1)
    else:
        r2_string = f"Integer ({r2_string}) + 1"

    if not isinstance(receiver, ogAST.PrimSubstring):
        ada_string += '.Data'
    ada_string += f' ({r1_string} .. {r2_string})'
    stmts.extend(r1_stmts)
    stmts.extend(r2_stmts)
    local_decl.extend(r1_local)
    local_decl.extend(r2_local)

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimSelector)
def _prim_selector(prim, **kwargs):
    ''' Selector (field access with '!' or '.' separation) '''
    stmts, ada_string, local_decl = [], '', []
    ro = kwargs.get("readonly", 0)

    receiver = prim.value[0]  # can be a PrimSelector
    field_name = prim.value[1]

    receiver_stms, receiver_string, receiver_decl = expression(receiver,
                                                               readonly=ro)

    ada_string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    receiver_bty = find_basic_type(receiver.exprType)

    if receiver_bty.kind == 'ChoiceType':
        ada_string = f'{ada_string}.{field_name}'
    else:
        # SEQUENCE, check for field optionality first
        child = child_spelling(field_name, receiver_bty)
        if receiver_bty.Children[child].Optional == 'True' \
                and not kwargs.get("readonly", 0):
            # Must set Exist only when assigning value, not each time it is
            # accessed: this is what "readonly" ensures.
            stmts.append(f'{ada_string}.Exist.{field_name} := 1;')
        ada_string += '.' + field_name

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimStateReference)
def _primary_state_reference(prim, **kwargs):
    ''' Reference to the current state '''
    return [], f'{LPREFIX}.state', []

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
def _basic_operators(expr, **kwargs):
    ''' Expressions with two sides '''
    code, local_decl = [], []

    left_stmts,  left_str,  left_local  = expression(expr.left, readonly=1)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)

    # Check if either side is a literal number
    right_is_numeric = is_numeric(right_str)
    left_is_numeric  = is_numeric(left_str)

    lbty = find_basic_type(expr.left.exprType)
    rbty = find_basic_type(expr.right.exprType)

    if lbty.kind.startswith('Integer') and \
            isinstance(expr.right, (ogAST.PrimOctetStringLiteral,
                                   ogAST.PrimBitStringLiteral)):
        right_str = str(expr.right.numeric_value)

    if rbty.kind.startswith('Integer') and \
            isinstance(expr.left, (ogAST.PrimOctetStringLiteral,
                                   ogAST.PrimBitStringLiteral)):
        left_str = str(expr.left.numeric_value)

    if left_is_numeric != right_is_numeric or rbty.kind == lbty.kind:
        # No cast is needed if:
        # - one of the two sides only is a literal
        # - or if the basic types are identical
        ada_string = '({left} {op} {right})'.format(left=left_str,
                                                     op=expr.operand,
                                                     right=right_str)

    elif left_is_numeric == right_is_numeric == True:
        # Both sides are literals : compute the result on the fly
        ada_string = "{}".format(eval("{left} {op} {right}"
                                       .format(left=left_str,
                                               op=expr.operand,
                                               right=right_str)))

    elif rbty.kind != lbty.kind:
        # Basic types are different (one is an Integer32, eg. loop iterator)
        # => We must cast it to the type of the other side
        if lbty.kind == 'Integer32Type':
            left_str = f'{type_name(expr.right.exprType)} ({left_str})'
        else:
            right_str = f'{type_name(expr.left.exprType)}({right_str})'
        ada_string = f'({left_str} {expr.operand} {right_str})'

    code.extend(left_stmts)
    code.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, str(ada_string), local_decl


@expression.register(ogAST.ExprEq)
@expression.register(ogAST.ExprNeq)
def _equality(expr, **kwargs):
    code,        left_str,  local_decl  = expression(expr.left, readonly=1)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)

    code.extend(right_stmts)
    local_decl.extend(right_local)

    asn1_type = getattr(expr.left.exprType, 'ReferencedTypeName', None)
    actual_type = type_name(expr.left.exprType)

    lbty = find_basic_type(expr.left.exprType)
    rbty = find_basic_type(expr.right.exprType)

    basic = lbty.kind in ('IntegerType',
                          'Integer32Type',
                          'IntegerU8Type',
                          'BooleanType',
                          'EnumeratedType',
                          'ChoiceEnumeratedType')
    if basic:
        if isinstance(expr.right, (ogAST.PrimBitStringLiteral,
                                   ogAST.PrimOctetStringLiteral)):
            right_str = str(expr.right.numeric_value)
        # Cast in case a side is using a 32bits ints (eg when using Length(..))
        if lbty.kind == 'IntegerType' and rbty.kind != lbty.kind:
            right_str = f'{type_name(lbty)} ({right_str})'
        elif rbty.kind == 'IntegerType' and lbty.kind != rbty.kind:
            left_str = f'{type_name(rbty)}({left_str})'
        ada_string = f'({left_str} {expr.operand} {right_str})'
    else:
        if asn1_type in TYPES:
            if isinstance(expr.right, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                if lbty.kind.startswith('Integer'):
                    right_str = str(expr.right.numeric_value)
                elif lbty.kind == 'IA5StringType':
                    right_str = ia5string_raw(expr.right)
                else:
                    right_str = array_content(expr.right, right_str, lbty)
            ada_string = f'{actual_type}_Equal ({left_str}, {right_str})'
        else:
            # Raw types on both left and right.... use simple operator
            ada_string = f"({left_str}) {expr.operand} ({right_str})"
        if isinstance(expr, ogAST.ExprNeq):
            ada_string = f'not {ada_string}'
    return code, str(ada_string), local_decl


@expression.register(ogAST.ExprAssign)
def _assign_expression(expr, **kwargs):
    ''' Assignment: almost the same a basic operators, except for strings '''
    code, local_decl = [], []
    strings = []
    left_stmts,  left_str,  left_local  = expression(expr.left)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)

    # If left side is a string/seqOf and right side is a substring, we must
    # assign the .Data and .Length parts properly
    basic_left = find_basic_type(expr.left.exprType)
    if (basic_left.kind == 'IA5StringType'
            and isinstance(expr.right, ogAST.PrimStringLiteral)):
        # Assignment of a raw IA5String: do not use the result of expression
        # as it represents the string as a sequence of numbers to fit
        # OCTET STRINGs.
        def_value = ia5string_raw(expr.right)
        strings.append(f'{left_str} := {def_value};')
    elif basic_left.kind in ('SequenceOfType', 'OctetStringType', 'BitStringType'):
        rlen = f"{right_str}'Length"

        if isinstance(expr.right, ogAST.PrimSubstring):
            if not isinstance(expr.left, ogAST.PrimSubstring):
                # only if left is not a substring, otherwise syntax
                # would be wrong due to result of _prim_substring
                strings.append(f"{left_str}.Data(1..{right_str}'Length) := {right_str};")
            else:
               # left is substring: no length, direct assignment
               rlen = ""
               strings.append(f"{left_str} := {right_str};")

        elif isinstance(expr.right, ogAST.ExprAppend):
            basic_right = find_basic_type(expr.right.exprType)
            rlen = append_size(expr.right)
            strings.append("{lvar}.Data(1..{lstr}) := {rvar};"
                           .format(lvar=left_str,
                                   rvar=right_str,
                                   lstr=rlen))

        elif isinstance(expr.right, (ogAST.PrimSequenceOf,
                                    ogAST.PrimStringLiteral)):
            if not isinstance(expr.left, ogAST.PrimSubstring):
                strings.append(
                    f"{left_str} := {array_content(expr.right, right_str, basic_left)};")
            else:
               # left is substring: no length, direct assignment
               strings.append(f"{left_str} := ({right_str});")

            rlen = None
        else:
            # Right part is a variable
            strings.append(f"{left_str} := {right_str};")
            rlen = None
        if rlen and basic_left.Min != basic_left.Max:
            strings.append(f"{left_str}.Length := {rlen};")
    elif basic_left.kind.startswith('Integer') and \
            isinstance(expr.right, (ogAST.PrimOctetStringLiteral,
                                    ogAST.PrimBitStringLiteral)):
        # If right is an octet string or bit string literal, use the numerical
        # value directly.
        right_str = str(expr.right.numeric_value)
        strings.append(f"{left_str} := {right_str};")
    elif basic_left.kind.startswith('Integer'):
#       print '\nASSIGN:', expr.inputString,
#       print "Left type = ",type_name(find_basic_type (expr.left.exprType)),
#       print "- Right type = ",type_name(find_basic_type (expr.right.exprType))

        # Make sure that integers are cast to 64 bits
        # It is possible that left and right are of different types
        # (signed vs unsigned and/or 32 bits vs 64 bits).
        # The parser should have ensured that the ranges are compatible.
        # We can therefore safely cast to the left type
        basic_right = find_basic_type (expr.right.exprType)
        cast_left, cast_right = type_name(basic_left), type_name(basic_right)
        #print (cast_left, cast_right, right_str)
        if cast_left != cast_right:
            res = f'{cast_left} ({right_str})'
        else:
            if hasattr (expr.right, "expected_type") \
                    and expr.right.expected_type is not None:

                cast_expected = type_name (expr.right.expected_type)
                if cast_expected != cast_left:
                    res = f'{cast_left} ({right_str})'
                else:
                    res = right_str
            else:
                res = right_str

        strings.append(f"{left_str} := {res};")
    else:
        strings.append(f"{left_str} := {right_str};")
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
def _bitwise_operators(expr, **kwargs):
    ''' Logical operators '''
    code, local_decl = [], []
    ada_string = ""

    left_stmts, left_str, left_local = expression(expr.left, readonly=1)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)

    basic_type = find_basic_type(expr.exprType)

    if basic_type.kind != 'BooleanType':
        left_bty  = find_basic_type (expr.left.exprType)
        right_bty = find_basic_type (expr.left.exprType)

        # Left is Sequence of boolean or bit string: 
        if expr.right.is_raw and not left_bty.kind.startswith('Integer'):
            # right is a raw value (hex/bit string)
            # right cannot be an integer here (it would need to be converted
            # to an hex string for bitwise operations to work against
            # a sequence of / bit string

            # Declare a temporary variable to store the raw value
            tmp_string = f'tmp{expr.right.tmpVar}'

            if isinstance(expr.right,
                          (ogAST.PrimSequenceOf,
                           ogAST.PrimStringLiteral)):
                right_str = array_content(expr.right, right_str, basic_type)

            local_decl.append(f'{tmp_string} : constant {type_name(expr.right.exprType)} := {right_str};')
            #code.append(f'{tmp_string} := {right_str};')

            right_str = tmp_string
            right_payload = right_str + '.Data'

        elif expr.right.is_raw and left_bty.kind.startswith('Integer'):
            # right is raw (e.g. hex string literal) and left is a number
            if isinstance (expr.right, (ogAST.PrimBitStringLiteral, ogAST.PrimOctetStringLiteral)):
                right_payload = str(expr.right.numeric_value)
            else:
                right_payload = right_str

            left_payload = left_str # + string_payload(expr.left, left_str)
            ada_string = f'({left_payload} {expr.operand} {right_payload})'
        elif left_bty.kind.startswith('Integer') and right_bty.kind.startswith('Integer'):
            # left and right are numbers
            ada_string = f'({left_str} {expr.operand} {right_str})'
        else:
            # ?
            right_payload = right_str + string_payload(expr.right, right_str)

        left_payload = left_str + string_payload(expr.left, left_str)

        if isinstance(expr, ogAST.ExprImplies):
            ada_string = f'(Data => (({left_payload} and {right_payload}) or not {left_payload}))'
        elif not ada_string:
            ada_string = f'(Data => ({left_payload} {expr.operand} {right_payload}))'

    elif isinstance(expr, ogAST.ExprImplies):
        ada_string = f'(({left_str} and {right_str}) or not {left_str})'
    else:
        ada_string = f'({left_str} {expr.operand}{expr.shortcircuit} {right_str})'

    code.extend(left_stmts)
    code.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)
    return code, str(ada_string), local_decl


@expression.register(ogAST.ExprNot)
def _not_expression(expr, **kwargs):
    ''' Generate the code for a not expression '''
    code, local_decl = [], []
    if isinstance(expr.expr, ogAST.PrimSequenceOf):
        # Raw sequence of boolean (e.g. not "{true, false}") -> flip values
        for each in expr.expr.value:
            each.value[0] = 'true' if each.value[0] == 'false' else 'false'
    expr_stmts, expr_str, expr_local = expression(expr.expr, readonly=1)

    bty_inner = find_basic_type(expr.expr.exprType)
    bty_outer = find_basic_type(expr.exprType)
    if bty_outer.kind != 'BooleanType' and not "Integer" in bty_outer.kind:
        if bty_outer.Min == bty_outer.Max:
            size_expr = ''
        elif bty_inner.Min == bty_inner.Max:
            size_expr = f', Length => {bty_inner.Min}'
        else:
            size_expr = f', Length => {expr_str}.Length'
        if isinstance(expr.expr, ogAST.PrimSequenceOf):
            ada_string = array_content(expr.expr, expr_str, bty_outer)
        else:
            ada_string = f'(Data => (not {expr_str}.Data){size_expr})'
    else:
        ada_string = f'(not {expr_str})'.format(expr=expr_str)

    code.extend(expr_stmts)
    local_decl.extend(expr_local)
    return code, str(ada_string), local_decl


@expression.register(ogAST.ExprNeg)
def _neg_expression(expr, **kwargs):
    ''' Generate the code for a negative expression '''
    code, local_decl = [], []
    expr_stmts, expr_str, expr_local = expression(expr.expr, readonly=1)
    cast = type_name (find_basic_type (expr.exprType))
    if not is_numeric(expr_str):
        ada_string = '(-{cast}({expr}))'.format(cast=cast, expr=expr_str)
    else:
         ada_string = '(-{expr})'.format(expr=expr_str)
    code.extend(expr_stmts)
    local_decl.extend(expr_local)
    return code, str(ada_string), local_decl


@expression.register(ogAST.ExprAppend)
def _append(expr, **kwargs):
    ''' Generate code for the APPEND construct: a // b '''
    stmts, ada_string, local_decl = [], '', []
    left_stmts,  left_str,  left_local  = expression(expr.left, readonly=1)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)
    stmts.extend(left_stmts)
    stmts.extend(right_stmts)
    local_decl.extend(left_local)
    local_decl.extend(right_local)

    right_self_standing = False
    left_self_standing = isinstance(expr.left,
            (ogAST.PrimVariable, ogAST.PrimConstant, ogAST.PrimSubstring))

    left = '{}{}'.format(left_str,
                         string_payload(expr.left, left_str)
                         if left_self_standing else '')

    if isinstance(expr.right, (ogAST.PrimVariable,
                               ogAST.PrimConditional,
                               ogAST.PrimConstant)):
        payload = string_payload(expr.right, right_str)
        right_self_standing = True
    else:
        payload = ''
    if isinstance (expr.right, ogAST.PrimSubstring):
        right_self_standing = True
    right = '{}{}'.format(right_str, payload)
    try:
        name_of_type = type_name (expr.expected_type)
    except (NotImplementedError, AttributeError):
        name_of_type = type_name (expr.left.exprType)

    if not right_self_standing:
        right = f"{name_of_type}_Array'({right}, others => <>)(1 .. {expr.right.exprType.Max})"

    if not left_self_standing and not isinstance(expr.left, ogAST.ExprAppend):
        # e.g. is the left part of the append is mkstring(var(someIndex))
        left = f"{name_of_type}_Array'({left}, others => <>)(1 .. {expr.left.exprType.Max})"

    ada_string = f"(({left}) & {right})"

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.ExprIn)
def _expr_in(expr, **kwargs):
    ''' IN expressions: check if item is in a SEQUENCE OF '''
    stmts, local_decl = [], []
    ada_string = ""

    left_stmts,  left_str,  left_local  = expression(expr.left, readonly=1)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)

    local_decl.extend(left_local)
    local_decl.extend(right_local)

    stmts.extend(left_stmts)
    stmts.extend(right_stmts)

    # it is possible to test against a raw sequence of: x in { 1,2,3 }
    # in that case we create an array on the type of x, and we test
    # presence using the form "for some Value of tmpXXX => x = Value"
    if isinstance(expr.left, ogAST.PrimSequenceOf):
        sort = type_name(expr.right.exprType)
        size = expr.left.exprType.Max

        local_decl.append(f'tmp{expr.tmpVar} : constant array (1 .. {size}) of {sort} := ({left_str});')
        ada_string = f'(for some var of tmp{expr.tmpVar} => var = {right_str})'
    else:
        local_decl.append(f'tmp{expr.tmpVar} : Boolean := False;')
        ada_string = f'tmp{expr.tmpVar}'

        stmts.append(f"in_loop_{ada_string}:")
        left_type = find_basic_type(expr.left.exprType)

        if isinstance(expr.left, ogAST.PrimSubstring):
            len_str = f"{left_str}'Length"
        else:
            len_str = f"{left_str}.Length"
            left_str += ".Data"

        if left_type.Min != left_type.Max:
            stmts.append(f"for elem in 1 .. {len_str} loop")
        else:
            stmts.append(f"for elem in {left_str}'Range loop")

        stmts.append(f"if {left_str} (elem) = {right_str} then")

        stmts.append(f"{ada_string} := True;")
        stmts.append("end if;")

        stmts.append(f"exit in_loop_{ada_string} when {ada_string} = True;")
        stmts.append(f"end loop in_loop_{ada_string};")

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimEnumeratedValue)
def _enumerated_value(primary, **kwargs):
    ''' Generate code for an enumerated value '''
    enumerant = primary.value[0].replace('_', '-').lower()
    basic = find_basic_type(primary.exprType)
    for each in basic.EnumValues:
        if each.lower() == enumerant:
            break
    # no "asn1Scc" prefix if the enumerated is a choice selector
    use_prefix = getattr(basic.EnumValues[each], "IsStandardEnum", True)
    prefix = type_name(basic, use_prefix=use_prefix)
    ada_string = (prefix + basic.EnumValues[each].EnumID)
    return [], str(ada_string), []


@expression.register(ogAST.PrimChoiceDeterminant)
def _choice_determinant(primary, **kwargs):
    ''' Generate code for a choice determinant (enumerated) '''
    enumerant = primary.value[0].replace('_', '-').lower()
    for each in primary.exprType.EnumValues:
        if each.lower() == enumerant:
            break
    ada_string = primary.exprType.EnumValues[each].EnumID
    return [], str(ada_string), []


@expression.register(ogAST.PrimInteger)
@expression.register(ogAST.PrimReal)
def _integer(primary, **kwargs):
    ''' Generate code for a raw numerical value  '''
    if float(primary.value[0]) < 0:
        # Put brackets around negative integers for maintaining
        # the precedence in the generated code
        ada_string = f'({primary.value[0]})'
    else:
        ada_string = primary.value[0]
    return [], str(ada_string), []


@expression.register(ogAST.PrimBoolean)
def _boolean(primary, **kwargs):
    ''' Generate code for a raw boolean value  '''
    ada_string = primary.value[0]
    return [], str(ada_string), []


@expression.register(ogAST.PrimNull)
def _null(primary, **kwargs):
    ''' Generate code for a raw null value  '''
    ada_string = '0'
    return [], str(ada_string), []


@expression.register(ogAST.PrimEmptyString)
def _empty_string(primary, **kwargs):
    ''' Generate code for an empty SEQUENCE OF: {} '''
    ada_string = '{}_Init'.format(type_name(primary.exprType))
    return [], str(ada_string), []


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary, **kwargs):
    ''' Generate code for a string (Octet String) '''
    basic_type = find_basic_type(primary.exprType)
    # If user put a literal string to fill an Octet string,
    # then convert the string to an array of unsigned_8 integers
    # as expected by the Ada type corresponding to Octet String
    if isinstance(primary, ogAST.PrimOctetStringLiteral):
        # Hex string used as input
        unsigned_8 = [str(x) for x in primary.hexstring]
    else:
        unsigned_8 = [str(ord(val)) for val in primary.value[1:-1]]

    ada_string = ', '.join(unsigned_8)
    return [], str(ada_string), []

def ia5string_raw(prim: ogAST.PrimStringLiteral):
    ''' IA5 Strings are of type String in Ada but this is not directly
    compatible with variable-length strings as defined in ASN.1
    Since the Ada type maps to a null-terminated C type, we have to make
    a corresponding assignment, filling then non-used part of the container
    with NULL character. To know the size, we can use adaasn1rtl.getStringSize
    '''
    return "('" + "', '".join(prim.value[1:-1]) + "', others => Standard.ASCII.NUL)"

@expression.register(ogAST.PrimConstant)
def _constant(primary, **kwargs):
    ''' Generate code for a reference to an ASN.1 constant '''
    return [], str(primary.constant_c_name), []


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary, **kwargs):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    # TODO
    return [], '', []


@expression.register(ogAST.PrimConditional)
def _conditional(cond, **kwargs):
    ''' Return string and statements for conditional expressions '''
    stmts = []

    tmp_type = type_name(cond.exprType)

    if tmp_type == 'String':
        then_str = cond.value['then'].value.replace("'", '"')
        else_str = cond.value['else'].value.replace("'", '"')
        lens = [len(then_str), len(else_str)]
        tmp_type = f'String (1 .. {max(lens) - 2})'
        # Ada require fixed-length strings, adjust with spaces
        if lens[0] < lens[1]:
            then_str = then_str[0:-1] + ' ' * (lens[1] - lens[0]) + '"'
        elif lens[1] < lens[0]:
            else_str = else_str[0:-1] + ' ' * (lens[0] - lens[1]) + '"'

    local_decl = [f'tmp{cond.value["tmpVar"]} : {tmp_type};']
    if_stmts, if_str, if_local = expression(cond.value['if'], readonly=1)
    stmts.extend(if_stmts)
    local_decl.extend(if_local)
    if not tmp_type.startswith('String'):
        then_stmts, then_str, then_local = expression(cond.value['then'],
                                                      readonly=1)
        else_stmts, else_str, else_local = expression(cond.value['else'],
                                                      readonly=1)
#       print "\nCONDITIONAL :", cond.inputString, tmp_type,
#       print "THEN TYPE:", type_name(find_basic_type(cond.value['then'].exprType)),
#       print "ELSE TYPE:", type_name(find_basic_type(cond.value['else'].exprType))
        stmts.extend(then_stmts)
        stmts.extend(else_stmts)
        local_decl.extend(then_local)
        local_decl.extend(else_local)
    stmts.append('if {if_str} then'.format(if_str=if_str))

    basic_then = find_basic_type(cond.value['then'].exprType)
    basic_else = find_basic_type(cond.value['else'].exprType)

    then_len = None
    if not tmp_type.startswith('String') and isinstance(cond.value['then'],
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
        then_str = array_content(cond.value['then'], then_str, basic_then)
    if isinstance(cond.value['then'], ogAST.ExprAppend):
        then_len = append_size(cond.value['then'])
        stmts.append("tmp{idx}.Data(1..{then_len}) := {then_str};"
                     .format(idx=cond.value['tmpVar'],
                             then_len=then_len, then_str=then_str))
    elif isinstance(cond.value['then'], ogAST.PrimSubstring):
        stmts.append("tmp{idx}.Data(1..{then_str}'Length) := {then_str};"
                     .format(idx=cond.value['tmpVar'], then_str=then_str))
        if basic_then.Min != basic_then.Max:
            then_len = f"{then_str}'Length"
    else:
        stmts.append('tmp{idx} := {then_str};'
                     .format(idx=cond.value['tmpVar'], then_str=then_str))
    if then_len:
        stmts.append("tmp{idx}.Length := {then_len};"
                     .format(idx=cond.value['tmpVar'], then_len=then_len))

    stmts.append('else')
    else_len = None
    if not tmp_type.startswith('String') and isinstance(cond.value['else'],
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
        else_str = array_content(cond.value['else'], else_str, basic_else)

    if isinstance(cond.value['else'], ogAST.ExprAppend):
        else_len = append_size(cond.value['else'])
        stmts.append("tmp{idx}.Data(1..{else_len}) := {else_str};"
                     .format(idx=cond.value['tmpVar'],
                             else_len=else_len, else_str=else_str))
    elif isinstance(cond.value['else'], ogAST.PrimSubstring):
        stmts.append("tmp{idx}.Data(1..{else_str}'Length) := {else_str};"
                     .format(idx=cond.value['tmpVar'], else_str=else_str))
        if basic_else.Min != basic_else.Max:
            else_len = "{}'Length".format(else_str)
    else:
        stmts.append('tmp{idx} := {else_str};'.format(
                                                    idx=cond.value['tmpVar'],
                                                    else_str=else_str))
    if else_len:
        stmts.append("tmp{idx}.Length := {else_len};"
                     .format(idx=cond.value['tmpVar'], else_len=else_len))
    stmts.append('end if;')
    ada_string = 'tmp{idx}'.format(idx=cond.value['tmpVar'])
    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimSequence)
def _sequence(seq, **kwargs):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    stmts, local_decl = [], []
    try:
        ada_string = f"{type_name(seq.exprType)}'("
    except NotImplementedError as err:
        err = f"!!YOU FOUND A BUG!! - The type of this record is undefined: {seq.inputString}"
        raise TypeError(str(err).replace('\n', ''))

    sep = ''
    type_children = find_basic_type(seq.exprType).Children
    optional_fields = {field.lower().replace('-', '_'): {'present': False,
                                                         'ref': (field, val)}
                       for field, val in type_children.items()
                       if val.Optional == 'True'}
    present_fields = []
    absent_fields = []
    for elem, value in seq.value.items():
        # Set the type of the field - easy thanks to ASN.1 flattened AST
        delem = elem.replace('_', '-')
        for each in type_children:
            if each.lower() == delem.lower():
                elem_spec = type_children[each]
                break

        elem_specty = elem_spec.type

        # Find the basic type of the elem: if it is a number and the value
        # is an octet/bit string literal, then use the raw number
        elem_bty = find_basic_type(elem_specty)

        value_stmts, value_str, local_var = expression(value, readonly=1)

        if isinstance(value, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            if elem_bty.kind.startswith('Integer'):
                value_str = str(value.numeric_value)
            elif elem_bty.kind == 'IA5StringType':
                value_str = ia5string_raw(value)
            else:
                value_str = array_content(value, value_str, elem_bty)

        ada_string += f"{sep} {elem} => {value_str}"
        if elem.lower() in optional_fields:
            # Set optional field presence
            optional_fields[elem.lower()]['present'] = True
        sep = ', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    # Process optional fields
    if optional_fields:
        absent_fields = ((fd_name, fd_data['ref'])
                          for fd_name, fd_data in optional_fields.items()
                          if not fd_data['present'])
        for fd_name, fd_data in absent_fields:
            fd_type = fd_data[1].type
            if fd_type.kind == 'ReferenceType':
                value = f'{type_name(fd_type)}_Init'
            elif fd_type.kind == 'BooleanType':
                value = 'False'
            elif fd_type in ('IntegerType', 'RealType'):
                value = fd_type.Min
            ada_string += f'{sep}{fd_name} => {value}'
            sep = ', '
        ada_string += ', Exist => ('
        sep = ''
        for fd_name, fd_data in optional_fields.items():
            ada_string += f'{sep}{fd_name} => {"1" if fd_data["present"] else "0"}'
            sep = ', '
        ada_string += ')'

    ada_string += ')'
    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimSequenceOf)
def _sequence_of(seqof, **kwargs):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    stmts, local_decl = [], []
    seqof_ty = seqof.exprType
    try:
        asn_type = find_basic_type(TYPES[seqof_ty.ReferencedTypeName].type)
    except AttributeError:
        asn_type = None
        min_size, max_size = seqof_ty.Min, seqof_ty.Max
        if hasattr(seqof, 'expected_type'):
            sortref = TYPES[seqof.expected_type.ReferencedTypeName]
            while(hasattr(sortref, "type")):
                sortref = sortref.type
            asn_type = find_basic_type(sortref)
    tab = []
    for i in range(len(seqof.value)):
        item_stmts, item_str, local_var = expression(seqof.value[i],
                                                     readonly=1)
        if isinstance(seqof.value[i],
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            item_str = array_content(seqof.value[i], item_str, asn_type or
                    find_basic_type(seqof.value[i].exprType))
        elif isinstance(seqof.value[i], ogAST.PrimSubstring):
            # Put substring elements in a local variable, otherwise they may
            # not work well with some operators (e.g. Append)
            tmpVarName = f'tmp{seqof.value[i].tmpVar}'
            tmpVarSort = seqof.value[i].exprType
            local_decl.append(f'{tmpVarName} : {type_name(tmpVarSort)};')
            # To get a proper assignment we need to create an ExprAssign
            expr = ogAST.ExprAssign()
            expr.left = ogAST.PrimVariable()
            expr.left.value = [tmpVarName]
            expr.left.exprType = tmpVarSort
            expr.right = seqof.value[i]
            expr.right.exprType = tmpVarSort
            expr.exprType = tmpVarSort
            assign_stmt, _, assign_loc = expression(expr, readonly=1)
            item_stmts.extend(assign_stmt)
            local_decl.extend(assign_loc)
            item_str = tmpVarName

        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        tab.append(f'{i+1} => {item_str}')
    ada_string = ', '.join(tab)
    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice, **kwargs):
    ''' Return the Ada code for a CHOICE expression '''
    stmts, choice_str, local_decl = expression(choice.value['value'],
                                               readonly=1)

    bty = find_basic_type(choice.value['value'].exprType)

    if isinstance(choice.value['value'], (ogAST.PrimSequenceOf,
                                          ogAST.PrimStringLiteral)):
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
    for each in basic.Children:
        curr_choice = each.lower().replace('-', '_')
        if curr_choice == search:
            prefix = basic.Children[each].EnumID
            break
    ada_string = f'(Kind => {prefix}, {choice.value["choice"]} => {choice_str})'
    return stmts, str(ada_string), local_decl


@generate.register(ogAST.Decision)
def _decision(dec, branch_to=None, sep='if ', last='end if;', exitcalls=[],
        **kwargs):
    ''' Generate the code for a decision
        A decision is made of a question and some answers ; each answer may
        be followed by a transition (ogAST.Transition). The code of the
        transition is by default generated, but it is possible to generate only
        the code of the question and reference a transition Id (trId) if
        the reference number is passed to the branch_to parameter. In addition
        it is possible to pass a list of exit calls: this is for nested
        functions when they are exited with a continuous signal at a level
        above, a chain a calls to exit procedures has to be added.
        This option is used for example when generating the code of
        continuous signal: the code is generated in the <<Continuous_Signals>>
        part, while the code of the transition already exists in the
        part above. The need is only to set the id of the next transition.
        XXX has to be done also in the C backend
    '''
    code, local_decl = [], []
    basic = True

    if dec.kind == 'any':
        #LOG.warning('Ada backend does not support the "ANY" statement')
        code.extend(traceability(dec))
        #code.append('null;')
        #return code, local_decl
        nb = len(dec.answers)
        code.append(f'case Rand_{nb}_Pkg.Random (Gen_{nb}) is')
    elif dec.kind == 'informal_text':
        LOG.warning('Informal decision ignored')
        code.append(f'-- Informal decision was ignored: {dec.inputString}')
        code.append('null;')
        return code, local_decl
    else:
        question_type = dec.question.exprType
        actual_type = type_name(question_type)
        question_basic = find_basic_type(question_type).kind
        basic = question_basic in (
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
            local_decl.append(f'tmp{dec.tmpVar} : {actual_type};')

        q_stmts, q_str, q_decl = expression(dec.question, readonly=1)

        # Add code-to-model traceability
        code.extend(traceability(dec))
        local_decl.extend(q_decl)
        code.extend(q_stmts)

        if not basic:
            code.append(f'tmp{dec.tmpVar} := {q_str};')

    previous_ans = ''
    for idx, a in enumerate(dec.answers):
        code.extend(traceability(a))
        if dec.kind == 'any':
            code.append(f'when {idx+1} =>');
            if not branch_to:
                if a.transition:
                    stmt, tr_decl = generate(a.transition)
                else:
                    stmt, tr_decl = ['null;'], []
                code.extend(stmt)
                local_decl.extend(tr_decl)
            else:
                # Before branching we should optionally execute the exit
                # procedures of the nested states we may be leaving
                for exit in exitcalls:
                    code.append(exit);
                code.append(f'trId := {branch_to};')
            continue
        if dec.kind == 'informal_text':
            break

        sub_sep = ''
        exp = ''
        for element in a.answers:
            # each branch can trigger based on multiple coma-separated answers
            ans_kind    = element['kind']
            ans_content = element['content']
            qbty = find_basic_type(question_type)

            if ans_kind in ('open_range', 'constant'):
                op, constant = ans_content # get the constant
                ans_stmts, ans_str, ans_decl = expression(constant, readonly=1)
                code.extend(ans_stmts)
                local_decl.extend(ans_decl)
                if not basic:
                    if op in (ogAST.ExprEq, ogAST.ExprNeq):
                        if isinstance(constant, (ogAST.PrimSequenceOf,
                                                 ogAST.PrimStringLiteral)):
                            if qbty.kind == 'IA5StringType':
                               ans_str = ia5string_raw (constant)
                            else:
                               ans_str = array_content(constant, ans_str, qbty)
                        expPart = f'{actual_type}_Equal(tmp{dec.tmpVar}, {ans_str})'
                        if op == ogAST.ExprNeq:
                            exp += f'{sub_sep}not {expPart}'
                        else:
                            exp += f'{sub_sep}{expPart}'
                    else:
                        exp += f'{sub_sep}tmp{dec.tmpVar} {op.operand} {ans_str}'
                else:
                    # Basic (number/enumerated/boolean)
                    # but the answer may be an hex or bit string literal
                    if isinstance(constant, (ogAST.PrimBitStringLiteral,
                                             ogAST.PrimOctetStringLiteral)):
                        ans_str = str(constant.numeric_value)

                    if actual_type != 'Boolean':
                        if question_basic.startswith('Integer'):
                            # cast integers, useful e.g. for octet string elements
                            exp += f'{sub_sep}({q_str}) {op.operand} {actual_type}({ans_str})'
                        else:
                            exp += f'{sub_sep}({q_str}) {op.operand} {ans_str}'
                    elif ans_str == 'true' and previous_ans != 'false':
                        exp += f'{sub_sep}({q_str})'
                    elif ans_str == 'false' and previous_ans != 'true':
                        exp += f'{sub_sep}not ({q_str})'
                    else:
                        exp = 'ELSEONLY'
                # In case of true/false, avoid repeating the expression
                previous_ans = ans_str


            elif ans_kind == 'closed_range':
                cl0_stmts, cl0_str, cl0_decl = expression(ans_content[0],
                                                          readonly=1)
                cl1_stmts, cl1_str, cl1_decl = expression(ans_content[1],
                                                          readonly=1)
                code.extend(cl0_stmts)
                local_decl.extend(cl0_decl)
                code.extend(cl1_stmts)
                local_decl.extend(cl1_decl)

                exp += f'{sub_sep}({q_str} >= {cl0_str} and {q_str} <= {cl1_str})'

            elif ans_kind == 'informal_text':
                continue
            elif ans_kind == 'else':
                # Keep the ELSE statement for the end
                if a.transition:
                    else_code, else_decl = generate(a.transition)
                else:
                    else_code, else_decl = ['null;'], []
                local_decl.extend(else_decl)

            sub_sep = " or "
        if exp:
            if exp == 'ELSEONLY':
                # Optimization for true/false answers
                code.append('else')
            else:
                code.append(sep + exp + ' then')
            if not branch_to:
                if a.transition:
                    stmt, tr_decl = generate(a.transition)
                else:
                    stmt, tr_decl = ['null;'], []
                code.extend(stmt)
                local_decl.extend(tr_decl)
            else:
                # Before branching we should optionally execute the exit
                # procedures of the nested states we may be leaving
                for exit in exitcalls:
                    code.append(exit);
                code.append(f'trId := {branch_to};')
            sep = 'elsif '
    try:
        if sep != 'if ':
            # If there is at least one 'if' branch
            else_code.insert(0, 'else')
            code.extend(else_code)
        else:
            code.extend(else_code)
    except:
        pass
    if sep != 'if ' and last:
        # If there is at least one 'if' branch
        # "last" is usually "end if;" but it can be changed by parameter
        # e.g. if the decision is chained with other tests with "elsif"
        code.append(last)

    if dec.kind == 'any':
        code.append ('end case;')
    return code, local_decl


@generate.register(ogAST.Label)
def _label(lab, **kwargs):
    ''' Transition following labels are generated in a separate section
        for visibility reasons (see Ada scope)
    '''
    return [f'goto {lab.inputString};'], []


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
            ns = tr.terminator.inputString.strip()
            empty_transition = False
            code.extend(traceability(tr.terminator))
            if tr.terminator.label:
                code.append(f'<<{ns}>>')
            if tr.terminator.kind == 'next_state':
                history = ns in ('-', '-*')
                if tr.terminator.next_is_aggregation and not history: # XXX add to C generator
                    code.append(f'-- Entering state aggregation {tr.terminator.inputString}')
                    # First change the state (to avoid looping in continuous signals since
                    # they will be evaluated after the start transition ; if the state is
                    # still the old state, there is a risk of infinite recursion)
                    if not tr.terminator.substate:
                        code.append(
                          f'{LPREFIX}.State := {ASN1SCC}{tr.terminator.inputString};')
                    else:
                        # We may be already in a substate
                        code.append(f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}State :='
                                        f' {ASN1SCC}{tr.terminator.inputString};')
                    # Call the START function of the state aggregation
                    code.append(f'{tr.terminator.next_id};')
                    code.append('trId := -1;')
                elif not history:
                    code.append(f'trId := {str(tr.terminator.next_id)};')
                    if tr.terminator.next_id == -1:
                        if not tr.terminator.substate: # XXX add to C generator
                            code.append(f'{LPREFIX}.State := {ASN1SCC}{tr.terminator.inputString};')
                        else:
                            code.append(f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}State :='
                                        f' {ASN1SCC}{tr.terminator.inputString};')
                else:
                    # "nextstate -": switch case to re-run the entry transition
                    # in case of a composite state or state aggregation
                    # and "nextstate -*" to return to the previous state
                    # (parallel states only, not composite states at the moment
                    # as the previous state is not stored)
                    if ns != "-*" and any(next_id
                           for next_id in tr.terminator.candidate_id.keys()
                           if next_id != -1):
                        code.append(f'case {LPREFIX}.State is')
                        for nid, sta in tr.terminator.candidate_id.items():
                            if nid != -1:
                                if tr.terminator.next_is_aggregation:
                                    statement = ns != '-*' and f'{nid};' or 'trId := -1;'
                                else:
                                    statement = f'trId := {nid};'
                                states_prefix = (f"{ASN1SCC}{s}" for s in sta)
                                joined_states = " | ".join(states_prefix)
                                code.extend(
                                        [f'when {joined_states} =>',
                                         statement])

                        code.extend(['when others =>',
                                        'trId := -1;',
                                     'end case;'])
                    else:
                        code.append('trId := -1;')
                code.append('goto Continuous_Signals;')
            elif tr.terminator.kind == 'join':
                code.append(f'goto {tr.terminator.inputString};')
            elif tr.terminator.kind == 'stop':
                pass
                # TODO
            elif tr.terminator.kind == 'return':
                string = ''
                aggregate = False
                if tr.terminator.substate: # XXX add to C generator
                    aggregate = True
                    # within a state aggregation, a return means that one
                    # of the parallel states becomes disabled, but it does
                    # not mean that the whole state aggregation can be
                    # exited. We must set this substate to a "finished"
                    # state until all the substates are returned. Then only
                    # call the overall state aggregation exit procedures.
                    code.append(
                        f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}State '
                        f':= {ASN1SCC}state{SEPARATOR}end;')
                    cond = '{ctxt}.{sib}{sep}State = {asn1scc}state{sep}end'
                    conds = [cond.format(sib=sib,
                                         ctxt=LPREFIX,
                                         sep=SEPARATOR,
                                         asn1scc=ASN1SCC)
                            for sib in tr.terminator.siblings
                            if sib.lower() != tr.terminator.substate.lower()]
                    code.append(f'if {" and ".join(conds)} then')
                if tr.terminator.next_id == -1:
                    retexp = tr.terminator.return_expr
                    if retexp:
                        stmts, string, local = expression(retexp, readonly=1)

                        # Check the return type in case of a procedure, in
                        # case it is a string - to format it properly
                        if isinstance(tr.terminator.context, ogAST.Procedure):
                            basic = find_basic_type(tr.terminator.context.return_type)
                            if isinstance(retexp,
                                    (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                                if basic.kind == 'IA5StringType':
                                    string = ia5string_raw(retexp)
                                elif basic.kind.startswith('Integer'):
                                    string = str(retexp.numeric_value)
                                else:
                                    string = array_content(retexp, string, basic)

                        code.extend(stmts)
                        local_decl.extend(local)
                    code.append(f'return{" " + string if string else ""};')
                else:
                    code.append(f'trId :=  {str(tr.terminator.next_id)};')
                    code.append('goto Continuous_Signals;')
                if aggregate:
                    code.append('else')
                    code.append('trId := -1;')
                    code.append('goto Continuous_Signals;')
                    code.append('end if;')
    if empty_transition:
        # If transition does not have any statement, generate an Ada 'null;'
        code.append('null;')
    return code, local_decl


@generate.register(ogAST.Floating_label)
def _floating_label(label, **kwargs):
    ''' Generate the code for a floating label (Ada label + transition) '''
    code = []
    local_decl = []
    # Add the traceability information
    code.extend(traceability(label))
    code.append(f'<<{label.inputString}>>')
    if label.transition:
        code_trans, local_trans = generate(label.transition)
        code.extend(code_trans)
        local_decl.extend(local_trans)
    else:
        code.append('return;')
    return code, local_decl


def procedure_header(proc):
    ''' Build the prototype of a procedure '''
    ret_type = type_name(proc.return_type) if proc.return_type else None
    kind = 'procedure' if not proc.return_type else 'function'
    sep = f'p{SEPARATOR}' if not proc.exported else ''
    proc_name = proc.inputString
    pi_header = f'{kind} {sep}{proc_name}'
    if proc.fpar:
        pi_header += '('
        params = []
        for fpar in proc.fpar:
            typename = type_name(fpar['type'])
            params.append('{name}: in{out} {ptype}'.format(
                    name=fpar.get('name'),
                    # out: exported procedures always use in out for taste (C code) compatibility
                    out=' out' if (fpar.get('direction') == 'out' or proc.exported) else '',
                    ptype=typename))
        pi_header += ';'.join(params)
        pi_header += ')'
    if ret_type:
        pi_header += f' return {ret_type}'
    return pi_header


@generate.register(ogAST.Procedure)
def _inner_procedure(proc, **kwargs):
    ''' Generate the code for a procedure - does not support states '''
    code = []
    local_decl = []
    # TODO: Update the global list of procedures
    # with procedure defined inside the current procedure
    # Not critical: the editor forbids procedures inside procedures

    # Save variable scopes (as local variables may shadow process variables)
    outer_scope = dict(VARIABLES)
    local_scope = dict(LOCAL_VAR)
    VARIABLES.update(proc.variables)
    # Note: here we ignore locally-declared monitorings.. they should be
    # defined at process level (but this is not checked in the parser)
    # Store local variables in global context
    LOCAL_VAR.update(proc.variables)
    # Also add procedure parameters in scope
    for var in proc.fpar:
        elem = {var['name']: (var['type'], None)}
        VARIABLES.update(elem)
        LOCAL_VAR.update(elem)

    # Build the procedure signature (function if it can return a value)
    pi_header = procedure_header(proc)
    if not proc.exported:
        local_decl.append(pi_header + ';')

    if proc.external:
        # Inner procedures declared external by the user: pragma import
        # the C symbol with the same name. Overrules the pragma import from
        # taste for required interfaces.
        local_decl.append(f'pragma Import (C, p{SEPARATOR}{proc.inputString}, '
                          f'"{proc.inputString}");')
    else:
        # Generate the code for the procedure itself
        # local variables and code of the START transition
        # Recursively generate the code for inner-defined procedures
        for inner_proc in proc.content.inner_procedures:
            inner_code, inner_local = generate(inner_proc)
            local_decl.extend(inner_local)
            code.extend(inner_code)
        code.append(f'{pi_header} is')
        for var_name, (var_type, def_value) in proc.variables.items():
            typename = type_name(var_type)
            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result
                dst, dstr, dlocal = expression(def_value, readonly=1)
                varbty = find_basic_type(var_type)

                if varbty.kind.startswith('Integer') and \
                        isinstance(def_value, (ogAST.PrimOctetStringLiteral,
                                               ogAST.PrimBitStringLiteral)):
                    dstr = str(def_value.numeric_value)

                elif varbty.kind in ('SequenceOfType',
                                     'OctetStringType',
                                     'BitStringType'):
                    dstr = array_content(def_value, dstr, varbty)

                elif varbty.kind == 'IA5StringType':
                    dstr = ia5string_raw(def_value)
                assert not dst and not dlocal, 'Ground expression error'
            default = f' := {dstr}' if def_value else ''
            code.append(f'{var_name} : {typename}{default};')

        # Look for labels in the diagram and transform them in floating labels
        Helper.inner_labels_to_floating(proc)

        if proc.exported and proc.content.start is not None:
            # Exported procedure end calling the corresponding transition
            # procedure that allows user to change state after RPC call
            # We need to update all the transitions of the procedure
            # (including floating labels) that contain a return statement
            # andadd the call to the _Transition procedure before
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
                call_trans.inputString = f'{proc.inputString}_Transition'
                trans_proc = f'{proc.inputString}_Transition'
                call_trans.output = [{'outputName': trans_proc,
                                     'params': [], 'tmpVars': []}]
                trans.actions.append(call_trans)

        if proc.content.start and proc.content.start.transition:
            tr_code, tr_decl = generate(proc.content.start.transition)
        else:
            tr_code, tr_decl = ['null;  --  Empty procedure'], []
        # Generate code for the floating labels
        code_labels = []
        for label in proc.content.floating_labels:
            code_label, label_decl = generate(label)
            code_labels.extend(code_label)
            tr_decl.extend(label_decl)
        code.extend(set(tr_decl))
        code.append('begin')
        code.extend(tr_code)
        code.extend(code_labels)
        if proc.exported:
            code.append(f'end {proc.inputString};')
        else:
            code.append(f'end p{SEPARATOR}{proc.inputString};')
    code.append('\n')

    # Reset the scope to how it was prior to the procedure definition
    VARIABLES.clear()
    VARIABLES.update(outer_scope)
    LOCAL_VAR.clear()
    LOCAL_VAR.update(local_scope)

    return code, local_decl


def string_payload(prim, ada_string):
    ''' Return the .Data part of a string, including range computed according
        to the length, if the string has a variable size '''
    if isinstance(prim, ogAST.PrimSubstring):
        return ''
    prim_basic = find_basic_type(prim.exprType)
    payload = ''
    if prim_basic.kind in ('SequenceOfType', 'OctetStringType', 'BitStringType'):
        if int(prim_basic.Min) != int(prim_basic.Max):
            payload = f'.Data(1..{ada_string}.Length)'
        else:
            payload = '.Data'
    return payload


def array_content(prim, values, asnty):
    ''' String literal and SEQOF are given as a sequence of elements ;
    this function builds the Ada string needed to fit it in an ASN.1 array
    i.e. convert "1,2,3" to "Data => (1,2,3, others=>0), [Length => 3]"
    inputs: prim is of type PrimStringLiteral or PrimSequenceOf
    values is a string with the sequence of numbers as processed by expression
    asnty is the reference type of the string literal '''
    if isinstance(prim, ogAST.PrimEmptyString):
        return values
    if asnty.Min != asnty.Max:
        length = len(prim.value)
        if isinstance(prim, ogAST.PrimStringLiteral):
            # Quotes are kept in string literals
            length -= 2
        if isinstance(prim, ogAST.PrimOctetStringLiteral):
            length=len(prim.hexstring)
        # Reference type can vary -> there is a Length field
        rlen = f", Length => {length}"
    else:
        rlen = ""
    if isinstance(prim, ogAST.PrimStringLiteral):
        df = '0'
    else:
        # Find a default value for the "others" field in case of SEQOF
        _, df, _ = expression(prim.value[0], readonly=1)
        if isinstance(prim.value[0], (ogAST.PrimSequenceOf,
                                      ogAST.PrimStringLiteral)):
            df = array_content(prim.value[0], df, asnty.type)
    return "(Data => ({}{}others => {}){})".format(values,
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
                _, inner, _ = expression(each, readonly=1)
                if isinstance (each, ogAST.PrimSubstring):
                    result += "{}'Length".format(inner)
                else:
                    result += "{}.Length".format(inner)
    return result


def find_basic_type(a_type):
    return Helper.find_basic_type(TYPES, a_type)


def asn1_type_name(a_type):
    ''' Return the type name with the proper casing as defined in ASN.1 '''
    assert a_type.kind == 'ReferenceType'
    for typename in TYPES.keys():
        if typename.lower() == a_type.ReferencedTypeName.lower():
            return typename
    return f"ERROR: Type Not Found: {a_type.ReferencedTypeName}"

def type_name(a_type, use_prefix=True):
    ''' Check the type kind and return an Ada usable type name '''
    if a_type.kind == 'ReferenceType':
        if use_prefix:
            return ASN1SCC + a_type.ReferencedTypeName.replace('-', '_')
        else:
            return a_type.ReferencedTypeName.replace("-", "_")
    elif a_type.kind == 'BooleanType':
        return 'Boolean'
    elif a_type.kind.startswith('Integer32'):
        return 'Integer'
    elif a_type.kind.startswith('IntegerU8'):
        return 'Interfaces.Unsigned_8'
    elif a_type.kind.startswith('Integer'):
        if float(a_type.Min) >= 0:
            return 'Asn1UInt'
        else:
            return 'Asn1Int'
    elif a_type.kind == 'RealType':
        return 'Asn1Real'
    elif a_type.kind.endswith('StringType'):
        return 'String'
    elif a_type.kind == 'ChoiceEnumeratedType':
        return 'Asn1InT'
    elif a_type.kind == 'StateEnumeratedType':
        return ASN1SCC
    elif a_type.kind == 'EnumeratedType':
        return ASN1SCC if use_prefix else ''
    else:
        raise NotImplementedError(f'Type name for {a_type.kind}')


def child_spelling(name, bty):
    ''' Return the index in Children with the proper spelling (case, dash) '''
    for each in bty.Children:
        if name.lower().replace('_', '-') == each.lower():
            return each
    raise TypeError(f'Child not found: {name}')


def find_var(var):
    ''' Return a variable from the scope, with proper case '''
    for visible_var in VARIABLES.keys():
        if var.lower() == visible_var.lower():
            return visible_var
    return None

def find_monitoring(mon):
    ''' Return a monitoring from the scope, with proper case '''
    for visible_mon in MONITORS.keys():
        if mon.lower() == visible_mon.lower():
            return visible_mon
    return None


def is_local(var):
    ''' Check if a variable is in the global context or in a local scope
        Typically needed to select the right prefix to use '''
    return var.lower() in (loc.lower() for loc in LOCAL_VAR.keys())


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
    declarations = dict(VARIABLES)
    declarations.update(MONITORS)
    vartype, _ = declarations[find_var(path[0])]
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
    trace = ['--  {line}'.format(line=l) for l in
        symbol.trace().split('\n')]
    if hasattr(symbol, 'comment') and symbol.comment:
        trace.extend(traceability(symbol.comment))
    return trace

def debug_trace(limit=2):
    ''' Return a list of comments containing traceability to the code
    generator, needed to know the origin of a statement in the code '''
    result = []
    for each in traceback.format_stack (limit=limit)[:-1]:
        formatted = each.replace('\n', ' ').split(',')
        function = formatted[2].strip().split(' ')[1]
        line_nb  = formatted[1].strip()
        added = ['--  !! stack: {} {}'.format(function, line_nb)]
        result.extend(added)
    return result

def format_ada_code(stmts):
    ''' Indent properly the Ada code '''
    indent = 0
    indent_pattern = '   '
    for line in stmts[:-1]:
        elems = line.strip().split()
        if elems and elems[0].startswith(('when', 'end', 'elsif', 'else')):
            indent = max(indent - 1, 0)
        if elems and elems[-1] == 'case;':  # Corresponds to end case;
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
