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

    Copyright (c) 2012-2020 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import logging
import traceback
import os
import stat
from itertools import chain, product
from functools import singledispatch

from . import ogAST, Helper

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

#SEPARATOR = u'\u00dc'
# Avoid Unicode characters, they cause occasional annoying issues
SEPARATOR = "_0_"
LPREFIX = 'ctxt'
ASN1SCC = 'asn1Scc'


def is_numeric(string):
    ''' Return true if value is a number '''
    try:
        float(string)
    except ValueError:
        return False
    return True


def external_ri_list(process):
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
            params_spec = u"({})".format("; ".join(params))
            ri_header += params_spec
        result.append(ri_header)

    for timer in process.timers:
        result.append(
                f"procedure Set_{timer} (Val : in out {ASN1SCC}T_Uint32)")
        result.append(f"procedure Reset_{timer}")
    return result


@singledispatch
def generate(*args, **kwargs):
    ''' Generate the code for an item of the AST '''
    raise TypeError('Incorrect, unsupported or missing data in model AST')
    return [], []


# Processing of the AST
@generate.register(ogAST.Process)
def _process(process, simu=False, instance=False, taste=False, **kwargs):
    ''' Generate the code for a complete process (AST Top level)
        use instance=True to generate the code for a process type instance
        rather than the process type itself.
    '''
    # support generation of code of a process type
    if not instance:
        process_name = process.instance_of_name or process.processName
        generic = process.instance_of_name  #  shortcut
        process_instance = process
        process = process.instance_of_ref or process
    else:
        process_name = process.processName
        generic = False
        process_instance = process

    if process_instance is not process:
        # Generate an instance of the process type, too.
        # First copy the list of timers to the instance (otherwise the
        # instance would miss some PIs and RIs to set the actual timers)
        process_instance.timers = process.timers
        generate(process_instance, simu, instance=True, taste=taste)

    global TYPES
    TYPES = process.dataview
    del OUT_SIGNALS[:]
    del PROCEDURES[:]
    OUT_SIGNALS.extend(process.output_signals)
    PROCEDURES.extend(process.procedures)
    global SHARED_LIB
    global LPREFIX
    if simu:
        SHARED_LIB = True
        LPREFIX = process_name + u'_ctxt'

    for each in PROCEDURES:
        process.random_generator.update(each.random_generator)

    # taste-properties module-specific flag for the Ada backend:
    # import the state data from an external module
    import_context = kwargs["ppty_check"] if "ppty_check" in kwargs else ""

    # When building a shared library (with simu=True), generate a "mini-cv"
    # for aadl2glueC to create the code interfacing with asn1scc
    minicv = ['-- Automatically generated by OpenGEODE - do NOT modify!']
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

    # go up to the root of the AST to get the list of ASN.1 files
    parent = process.parent
    while hasattr(parent, 'parent') and parent.parent:
        parent = parent.parent
    if isinstance(parent, ogAST.System):
        parent = parent.ast
    asn1_filenames = (f"{' '.join(parent.asn1_filenames)} "
                      f"{process_name.lower()}_datamodel.asn")
    asn1_uniq = ' '.join(each for each in parent.asn1_filenames
                         if not each.endswith('dataview-uniq.asn'))
    asn1_uniq += f" {process_name.lower()}_datamodel.asn"
    pr_path = ' '.join(parent.pr_files) if None not in parent.pr_files else ''
    pr_names = ' '.join(
                      os.path.basename(pr_file) for pr_file in parent.pr_files)
    asn1_modules_o = (name.lower().replace('-', '_') + '.o'
                    for name in process.asn1Modules)

    asn1_mods = ("\"{}\"".format(mod.lower().replace('-', '_'))
                for mod in process.asn1Modules)

    #  Create a .gpr to build the library for the simulator
    lib_gpr = '''project {pr}_Lib is
   for Languages use ("Ada");
   for Library_Name use "{pr}";
   for Library_Interface use ("{pr}", "adaasn1rtl", {other_asn1_modules});
   for Object_Dir use "obj";
   for Library_Dir use "lib";
   for Library_Standalone use "encapsulated";
   for Library_Kind use "dynamic";
   for Source_Dirs use (".");
end {pr}_Lib;'''.format(pr=process_name.lower(),
                        other_asn1_modules=", ".join(asn1_mods))

    #  Create a .gpr to build the Ada generated code
    ada_gpr = '''project {pr}_Ada is
   for Languages use ("Ada");
      for Source_Dirs use (".") & External_As_List ("CODE_PATH", ":");
      for Object_Dir use "../obj";
   end {pr}_Ada;'''.format(pr=process_name.lower())

    pr = process_name.lower()
    simu_script = f'''#!/bin/bash -e
mkdir -p {pr}_simu
cp {pr_path} {asn1_filenames} {pr}_simu
cd {pr}_simu
opengeode {pr_names} --shared
cat {asn1_uniq} >> dataview-uniq.asn

mono $(which asn1.exe) -Ada -typePrefix {ASN1SCC} -equal dataview-uniq.asn
mono $(which asn1.exe) -c -typePrefix {ASN1SCC} -equal dataview-uniq.asn

gprbuild -p -P {process_name.lower()}_lib.gpr
rm -f dataview-uniq.c dataview-uniq.h
asn2aadlPlus dataview-uniq.asn DataView.aadl
aadl2glueC DataView.aadl {process_name.lower()}_interface.aadl
asn2dataModel -toPython dataview-uniq.asn
make -f Makefile.python
echo "errCodes=$(taste-asn1-errCodes ./dataview-uniq.h)" >>datamodel.py
LD_LIBRARY_PATH=./lib:. opengeode-simulator
'''

    LOG.info('Generating Ada code for process ' + str(process_name))

    # In case model has nested states, flatten everything
    Helper.flatten(process, sep=SEPARATOR)

    # Process State aggregations (Parallel states) XXX Add to C backend

    # Find recursively in the AST all state aggregations
    # Format: {'aggregation_name' : [list of ogAST.CompositeState]
    aggregates = Helper.state_aggregations(process)

    # Extract the list of parallel states names inside the composite states
    # of state aggregations XXX add to C generator
    parallel_states = Helper.parallel_states(aggregates)

    # Make an maping {input: {state: transition...}} in order to easily
    # generate the lookup tables for the state machine runtime
    mapping = Helper.map_input_state(process)

    VARIABLES.update(process.variables)

    process_level_decl = []

    # Establish the list of states (excluding START states) XXX update C backend
    full_statelist = set(chain(aggregates.keys(),
                               (name for name in process.mapping.keys()
                                    if not name.endswith(u'START'))))
    reduced_statelist = {s for s in full_statelist if s not in parallel_states}

    if aggregates:
        # Parallel states in a state aggregation may terminate
        full_statelist.add(f'state{SEPARATOR}end')

    # Format the state list with ASN.1-compatible syntax
    process_asn1 = process_name.upper().replace('_', '-')
    statelist_asn1 = (state.lower().replace('_', '-')
                      for state in full_statelist)
    states_asn1 = ", ".join(statelist_asn1) \
            or f'{process_asn1.lower()}-has-no-state'
    # Create an ASN.1 definition of the list of states, instead of
    # a native Ada type - this allows external tools to access
    # information about the model without having to parse SDL
    asn1_states_def = f"{process_asn1}-States ::= ENUMERATED" \
                      f" {{{states_asn1}}}"

    context_decl = []

    # Generate an ASN.1 model containing the state definition, as well as
    # all the user-defined SDL type (NEWTYPEs...)
    asn1_template = [f'{process_asn1}-Datamodel DEFINITIONS ::=',
                      'BEGIN']

    #  When a signal is sent from the model a call to a function is emitted
    #  This function has to be provided - either by TASTE (kazoo), or by
    #  the user. Opengeode will generate a stub package for this.
    ri_stub_ads = []
    ri_stub_adb = []

    # Add user-defined NEWTYPEs
    if process.user_defined_types:
        types_with_proper_case = []

        # The ASN.1 module must import the types from other asn1 modules
        for _, sortdef in process.user_defined_types.items():
            sort = sortdef.type.type.ReferencedTypeName
            for moduleName, sorts in process.DV.exportedTypes.items():
                for each in sorts:
                    if sort.lower().replace('-', '_') == \
                            each.lower().replace('-', '_'):
                        asn1_template.append(u'IMPORTS {t} FROM {m};'
                                .format (t=each, m=moduleName))
                        types_with_proper_case.append (each)

        for sortname, sortdef in process.user_defined_types.items():
            rangeMin = sortdef.type.Min
            rangeMax = sortdef.type.Max
            refType  = sortdef.type.type.ReferencedTypeName
            for refTypeCase in types_with_proper_case:
                if refTypeCase.lower().replace('-', '_') == \
                        refType.lower().replace('-', '_'):
                    break
            asn1_template.append(
                    '{sort} ::= SEQUENCE (SIZE ({rangeMin} .. {rangeMax})) '
                    'OF {refType}'
                    .format(sort=sortname.upper().replace('_', '-'),
                            rangeMin=rangeMin,
                            rangeMax=rangeMax,
                            refType=refTypeCase.replace('_', '-')))
    if not import_context:
        #  don't generate state type in Stop Condition/Observer
        #  automaton as it is defined in the observed process
        asn1_template.append(asn1_states_def)
    asn1_template.append('END')

    # Write the ASN.1 file
    with open(process_name.lower() + '_datamodel.asn', 'w') as asn1_file:
        asn1_file.write('\n'.join(asn1_template))

    # Generate the code to declare process-level context
    if not import_context:
        # but not in stop condition code, since we reuse the context type
        # of the state machine being observed
        context_decl.extend([f'type {LPREFIX}_Ty is', 'record'])

        if full_statelist:
            context_decl.append(f'State : {ASN1SCC}{process_name}_States;')

        context_decl.append('Init_Done : Boolean := False;')

        # State aggregation: add list of substates
        for substates in aggregates.values():
            for each in substates:
                context_decl.append(
                   f'{each.statename}{SEPARATOR}state:'
                   f' {ASN1SCC}{process_name}_States;')

        for var_name, (var_type, def_value) in process.variables.items():
            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result
                dst, dstr, dlocal = expression(def_value)
                varbty = find_basic_type(var_type)
                if varbty.kind in ('SequenceOfType', 'OctetStringType'):
                    dstr = array_content(def_value, dstr, varbty)
                assert not dst and not dlocal,\
                        'DCL: Expecting a ground expression'
            context_decl.append(
                            '{n} : {aliased}{sort}{default};'
                            .format(n=var_name,
                                   aliased="aliased " if simu else "",
                                   sort=type_name(var_type),
                                   default=' := ' + dstr if def_value else ''))

        context_decl.append('end record;')
    # context is aliased so that the model checker can work with access type
    if import_context:
        #  code of stop conditions must use the same type as the main process
        context_decl.append(
                f'{LPREFIX}: {import_context}.{import_context}_Ctxt_Ty '
                f'renames {import_context}.{import_context}_ctxt;')
    else:
        context_decl.append('{ctxt} : {ctxt}_Ty;'.format(ctxt=LPREFIX))
    if simu:
        # Export the context, so that it can be manipulated from outside
        # (in practice used by the "properties" module.
        context_decl.append(u'pragma export (C, {ctxt}, "{ctxt}");'
                                  .format(ctxt=LPREFIX))
        # Exhaustive simulation needs a backup of the context to quickly undo
        context_decl.append(u'{ctxt}_bk: {ctxt}_Ty;'
                                  .format(ctxt=LPREFIX))

    # Don't declare the context in the adb - declare it in the ads
    #if not simu and not instance:
    #    process_level_decl.extend(context_decl)

    aggreg_start_proc = []
    start_transition = []
    # Continuous State transition id
    if not instance:
        process_level_decl.append('CS_Only : constant := {};'
                                  .format(len(process.transitions)))

        for name, val in process.mapping.items():
            # Test val, in principle there is a value but if the code targets
            # generation of properties, the model may have been cleant up and
            # in that case no value would be set..
            if name.endswith(u'START') and name != u'START' and val:
                process_level_decl.append(u'{name} : constant := {val};'
                                          .format(name=name, val=str(val)))

        # Declare start procedure for aggregate states XXX add in C generator
        # should create one START per "via" clause, TODO later
        for name, substates in aggregates.items():
            proc_name = f'procedure {name}{SEPARATOR}START'
            process_level_decl.append(f'{proc_name};')
            aggreg_start_proc.extend([f'{proc_name} is',
                                      'begin'])
            aggreg_start_proc.extend(u'Execute_Transition ({sub}{sep}START);'
                                     .format(sub=subname.statename,
                                             sep=SEPARATOR)
                                     for subname in substates)
            aggreg_start_proc.extend([f'end {name}{SEPARATOR}START;',
                                     '\n'])

        # Add the declaration of the Execute_Transition  procedure
        process_level_decl.append(
                'procedure Execute_Transition (Id : Integer);')

        # Generate the code of the start transition (if process not empty)
        Init_Done = f'{LPREFIX}.Init_Done := True;'
#       if not simu:
#           start_transition = ['begin']
#           if process.transitions:
#               start_transition.append('Execute_Transition (0);')
#           start_transition.append(Init_Done)
#       else:
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
        asn1_modules = '\n'.join(['with {dv};\nuse {dv};'.format(
            dv=dv.replace('-', '_'))
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

package body {process_name} is'''
    if not instance else u"package body {} is".format(process_name)]

    generic_spec, instance_decl = "", ""
    if generic:
        generic_spec = u"generic\n"
        ri_list = external_ri_list(process)
        if ri_list:
            generic_spec += u"    with " + u";\n    with ".join(ri_list) + ';'
    if instance:
        instance_decl = u"with {};".format(process.instance_of_name)

    # print process.fpar
    # FPAR could be set for Context Parameters. They are available here

    # Generate the source file (.ads) header

    # Stop conditions must import the SDL model they observe
    imp_str = f"with {import_context}; use {import_context};" \
            if import_context else ''

    imp_datamodel = (f"with {process_name}_Datamodel; "
                     f"use {process_name}_Datamodel;") \
                             if not import_context and not instance else ""

    imp_ri = f"with {process_name}_RI;" if not simu and not generic else ""

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
package {process_name} with Elaborate_Body is''']

    ri_stub_ads = [f'''\
--  This file is a stub for the implementation of the required interfaces
--  It is normally overwritten by TASTE with the actual connection to the
--  middleware. If you use Opengeode independently from TASTE you must
--  edit the .adb (body) with your own implementation of these functions.
--  The body stub will be generated only once.

{asn1_modules}

package {process_name}_RI is''']
    ri_stub_adb = [f'''--  Stub generated by OpenGEODE.
--  You can edit this file, it will not be overwritten

package body {process_name}_RI is''']

    dll_api = []
    ads_template.extend(rand_decl)
    if not instance:
        ads_template.extend(context_decl)
    if not generic and not instance:
        # Add function allowing to trace current state as a string
        ads_template.append(
                f"function Get_State return chars_ptr "
                f"is (New_String "
                f"({ASN1SCC}{process_name}_States'Image ({LPREFIX}.State)))"
                f" with Export, Convention => C, "
                f'Link_Name => "{process_name.lower()}_state";')

    if simu:
        ads_template.append('--  API for simulation via DLL')
        dll_api.append('-- API to remotely change internal data')
        set_state_decl = "procedure Set_State (New_State : chars_ptr)"
        ads_template.append(f'{set_state_decl} with Export, Convention => C, '
                            f' Link_Name => "_set_state";')
        dll_api.append(f"{set_state_decl} is")
        dll_api.append("begin")
        dll_api.append(f"for S in {ASN1SCC}{process_name}_States loop")
        dll_api.append(f"if To_Upper (Value (New_State))"
                       f" = {ASN1SCC}{process_name}_States'Image (S) then")
        dll_api.append(f"{LPREFIX}.State := S;")
        dll_api.append("end if;")
        dll_api.append("end loop;")
        dll_api.append("end Set_State;")
        dll_api.append("")

        # Save/restore state allow one step undo, as needed for model checking
        save_state_decl = "procedure Save_Context"
        restore_state_decl = "procedure Restore_Context"
        ads_template.append("{};".format(save_state_decl))
        ads_template.append('pragma Export (C, Save_Context,'
                            ' "_save_context");')
        ads_template.append("{};".format(restore_state_decl))
        ads_template.append('pragma Export (C, Restore_Context,'
                            ' "_restore_context");')
        dll_api.append("{} is".format(save_state_decl))
        dll_api.append("begin")
        dll_api.append("{ctxt}_bk := {ctxt};".format(ctxt=LPREFIX))
        dll_api.append("end Save_Context;")
        dll_api.append("")
        dll_api.append("{} is".format(restore_state_decl))
        dll_api.append("begin")
        dll_api.append("{ctxt} := {ctxt}_bk;".format(ctxt=LPREFIX))
        dll_api.append("end Restore_Context;")
        dll_api.append("")

        # Declare procedure Startup in .ads
        ads_template.append(u'procedure Startup;')
        ads_template.append(u'pragma Export (C, Startup, "{}_startup");'
                            .format(process_name))

        # interface to get/set state aggregations XXX add to C generator
        for substates in aggregates.values():
            for each in substates:
                process_level_decl.append(
                      f"function Get_{each.statename}_State return chars_ptr "
                      f"is (New_String ({ASN1SCC}{process_name}_States'Image"
                      f" ({LPREFIX}.{each.statename}{SEPARATOR}state)"
                      f")) with Export, Convention => C, "
                      f'Link_Name => "{process_name}_{each.statename}_state";')

        # Functions to get gobal variables (length and value)
        for var_name, (var_type, _) in process.variables.items():
            # Getters for external applications to view local variables via dll
            process_level_decl.append(
                    f"function l_{var_name}_value"
                    f" return access {type_name(var_type)} "
                    f"is ({LPREFIX}.{var_name}'access) with Export,"
                    f" Convention => C,"
                    f' Link_Name => "{var_name}_value";')
            # Setters for local variables
            setter_decl = u"procedure DLL_Set_l_{name} (Value: in out {sort})"\
                          .format(name=var_name, sort=type_name(var_type))
            ads_template.append(
                    f'{setter_decl} with Export, Convention => C, '
                    f'Link_Name => "_set_{var_name}";')
            dll_api.append(f'{setter_decl} is')
            dll_api.append('begin')
            dll_api.append(f'{LPREFIX}.{var_name} := Value;')
            dll_api.append(f'end DLL_Set_l_{var_name};')
            dll_api.append('')

    # Generate the the code of the procedures
    inner_procedures_code = []
    for proc in process.content.inner_procedures:
        proc_code, proc_local = generate(proc)
        process_level_decl.extend(proc_local)
        inner_procedures_code.extend(proc_code)
        if proc.exported:
            # Exported procedures must be declared in the .ads
            pi_header = procedure_header(proc)
            ads_template.append(u'{};'.format(pi_header))
            if not proc.external and not generic:
                ads_template.append(u'pragma Export'
                                    u'(C, p{sep}{proc_name}, "_{proc_name}");'
                                    .format(sep=SEPARATOR,
                                            proc_name=proc.inputString))

    # Generate the code for the process-level variable declarations
    taste_template.extend(process_level_decl)

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
        if import_context:
            # dont generate anything in stop_condition functions
            break

        signame = signal.get('name', u'START')
        if signame == u'START':
            continue
        pi_header = u'procedure {sig_name}'.format(sig_name=signame)
        param_name = signal.get('param_name') \
                                or u'{}_param'.format(signame)
        # Add (optional) PI parameter (only one is possible in TASTE PI)
        if 'type' in signal:
            typename = type_name(signal['type'])
            pi_header += u'({pName}: in out {sort})'.format(
                                        pName=param_name, sort=typename)

        # Add declaration of the provided interface in the .ads file
        ads_template.append(u'--  Provided interface "{}"'.format(signame))
        ads_template.append(pi_header + ';')
        if not generic:
            ads_template.append(
                    u'pragma Export(C, {name}, "{proc}_PI_{name}");'
                     .format(name=signame, proc=process_name.lower()))
                     # don't lower case the signal name, not for kazoo at least
                     #.format(name=signame.lower(), proc=process_name.lower()))

        if simu:
            # Generate code for the mini-cv template
            params = [(param_name, type_name(signal['type'], use_prefix=False),
                      'IN')] if 'type' in signal else []
            minicv.append(aadl_template(signame, params, 'RI'))

        pi_header += ' is'
        taste_template.append(pi_header)
        taste_template.append('begin')

        def execute_transition(state):
            ''' Generate the code that triggers the transition for the current
                state/input combination '''
            input_def = mapping[signame].get(state)
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
                    taste_template.append(f'p{SEPARATOR}{each}{SEPARATOR}exit;')

            if input_def:
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    taste_template.append(f'{LPREFIX}.{inp} := {param_name};')
                # Execute the correponding transition
                if input_def.transition:
                    taste_template.append(u'Execute_Transition ({idx});'
                            .format(idx=input_def.transition_id))
                else:
                    taste_template.append('Execute_Transition (CS_Only);')
            else:
                taste_template.append('Execute_Transition (CS_Only);')

        if not instance:
            taste_template.append('case {}.state is'.format(LPREFIX))

        def case_state(state):
            ''' Recursive function (in case of state aggregation) to generate
                the code that calls the proper transition according
                to the current state
                The input name is in signame
            '''
            if state.endswith(u'START'):
                return
            taste_template.append(f'when {ASN1SCC}{state} =>')
            input_def = mapping[signame].get(state)
            if state in aggregates.keys():
                # State aggregation:
                # - find which substate manages this input
                # - add a swich case on the corresponding substate
                taste_template.append(u'-- this is a state aggregation')
                for sub in aggregates[state]:
                    if [a for a in sub.mapping.keys()
                            if a in mapping[signame].keys()]:
                        taste_template.append(u'case '
                                              u'{ctxt}.{sub}{sep}state is'
                                              .format(ctxt=LPREFIX,
                                                     sub=sub.statename,
                                                     sep=SEPARATOR))
                        for par in sub.mapping.keys():
                            case_state(par)
                        taste_template.append('when others =>')
                        taste_template.append('null;')
                        taste_template.append('end case;')
                        break
                else:
                    # Input is not managed in the state aggregation
                    if input_def:
                        # check if it is managed one level above
                        execute_transition(state)
                    taste_template.append('null;')
            else:
                execute_transition(state)

        if not instance:
            for each_state in reduced_statelist:
                case_state(each_state)
            taste_template.append('when others =>')
            taste_template.append('Execute_Transition (CS_Only);')
            taste_template.append('end case;')
        else:
            inst_call = f"{process_name}_Instance.{signame}"
            if 'type' in signal:
                inst_call += f" ({param_name})"
            taste_template.append(f"{inst_call};")

        taste_template.append(f'end {signame};')
        taste_template.append('\n')

    # for the .ads file, generate the declaration of the required interfaces
    # output signals are the asynchronous RI - only one parameter
    for signal in process.output_signals:
        sig = signal['name']
        param_name = signal.get('param_name') or f'{sig}_param'
        # Add (optional) RI parameter
        # Paramless TMs: when targetting simulation, the name of the TM is
        # passed as single parameter. This allows the simualor to handle them
        # dynamically, with a single callback function for all TMs
        param_spec = '' if not simu else " (TM : chars_ptr)"
        if 'type' in signal:
            typename = type_name(signal['type'])
            param_spec = f' ({param_name} : in out {typename}{"; Size : Integer" if SHARED_LIB else ""})'
        if not generic:
            ads_template.append(u'--  {}equired interface "{}"'
                                .format("Paramless r" if not 'type' in signal
                                    else "R", sig))
        if simu:
            # When generating a shared library, we need a callback mechanism
            code = [f'type {sig}_T is access procedure{param_spec};',
                    f'pragma Convention (Convention => C, Entity => {sig}_T);',
                    f'RI{SEPARATOR}{sig} : {sig}_T;',
                    f'procedure Register_{sig} (Callback : {sig}_T);',
                    f'pragma Export(C, Register_{sig}, "register_{sig}");']
            ads_template.extend(code)

            # Generate code for the mini-cv template
            params = [(param_name,
                       type_name(signal['type'], use_prefix=False),
                      'IN')] if 'type' in signal else []

            minicv.append(aadl_template(sig, params, 'PI'))

            code = [f'procedure Register_{sig} (Callback : {sig}_T) is',
                     'begin',
                    f'RI{SEPARATOR}{sig} := Callback;',
                    f'end Register_{sig};',
                    '']
            taste_template.extend(code)
        elif not generic:
            ads_template.append(f'procedure RI{SEPARATOR}{sig}{param_spec} '
                    f'renames {process_name}_RI.{sig};')
            ri_stub_ads.append(f'procedure {sig}{param_spec};')
            ri_stub_adb.append(f'procedure {sig}{param_spec} is null;')
            #  TASTE generates the pragma import in <function>_ri.ads
            #  therefore do not generate it in the .ads
            # ads_template.append(f'pragma Import (C, RI{SEPARATOR}{sig}, "{process_name.lower()}_RI_{sig}");')

    # for the .ads file, generate the declaration of the external procedures
    for proc in (proc for proc in process.procedures if proc.external):
        sig = proc.inputString
        ri_header = f'procedure RI{SEPARATOR}{sig}'
        params = []
        params_spec = ""
        if simu:
            # For simulators: add the TM name as first parameter
            params.append("TM : chars_ptr")
        for param in proc.fpar:
            typename = type_name(param['type'])
            name     = param['name']
            if param['direction'] == 'in':
                direct = 'in out'
            else:
                direct = 'out'
            shared=f"; {name}_Size : Integer" if SHARED_LIB else ""

            params.append(f'{name} : {direct} {typename}{shared}')
        if params:
            params_spec = " ({})".format("; ".join(params))
            ri_header += params_spec
        ads_template.append(f'--  Sync required interface "{sig}"')
        if simu:
            # As for async TM, generate a callback mechanism
            code = [f"type {sig}_T is access procedure{params_spec};",
                    f'pragma Convention(Convention => C, Entity => {sig}_T);',
                    f'RI{SEPARATOR}{sig} : {sig}_T;',
                    f'procedure Register_{sig}(Callback: {sig}_T);',
                    f'pragma Export(C, Register_{sig}, "register_{sig}");']

            ads_template.extend(code)

            code = [f'procedure Register_{sig} (Callback : {sig}_T) is',
                     'begin',
                    f'RI{SEPARATOR}{sig} := Callback;',
                    f'end Register_{sig};',
                     '']
            taste_template.extend(code)

        elif not generic:
            ads_template.append(f'{ri_header} renames {process_name}_RI.{sig};')
            ri_stub_ads.append(f'procedure {sig}{params_spec};')
            ri_stub_adb.append(f'procedure {sig}{params_spec} is null;')

    # for the .ads file, generate the declaration of timers set/reset functions
    for timer in process.timers:
        ads_template.append(u'--  Timer {} SET and RESET functions'
                            .format(timer))
        if simu:
            # Declare callback registration for the SET and RESET functions
            ads_template.append(u'type SET_{}_T is access procedure'
                                 '(name: chars_ptr; duration: Asn1Int);'
                                .format(timer))
            ads_template.append(u'type RESET_{}_T is access procedure'
                                '(name: chars_ptr);'.format(timer))
            for each in ('', 'RE'):
                ads_template.append(u'pragma Convention (Convention => C,'
                                    u' Entity => {re}SET_{t}_T);'
                                    .format(re=each, t=timer))
                ads_template.append(u'{re}SET_{t} : {re}SET_{t}_T;'
                                    .format(re=each, t=timer))
                ads_template.append(u'procedure Register_{re}SET_{t}'
                                    u'(Callback: {re}SET_{t}_T);'
                                    .format(re=each, t=timer))
                ads_template.append(u'pragma Export(C, Register_{re}SET_{t},'
                                    u' "register_{re}SET_{t}");'
                                    .format(re=each, t=timer))
            # Code for the SET/RESET timer callback registration
            for each in ('', 'RE'):
                taste_template.append(u'procedure Register_{re}SET_{t}'
                                      u'(Callback:{re}SET_{t}_T) is'
                                      .format(re=each, t=timer))
                taste_template.append(u'begin')
                taste_template.append(u'{re}SET_{t} := Callback;'
                                      .format(re=each, t=timer))
                taste_template.append(u'end Register_{re}SET_{t};'
                                      .format(re=each, t=timer))
                taste_template.append('')

        elif not generic:
            procname = process_name.lower()
            ads_template.append(
               f'procedure SET_{timer} (Val : in out asn1SccT_UInt32) '
               f'renames {process_name}_RI.Set_{timer};')
            ri_stub_ads.append(f'procedure SET_{timer} (Val : in out asn1SccT_UInt32);')
            ri_stub_adb.append(f'procedure SET_{timer} (Val : in out asn1SccT_UInt32) is null;')
            #ads_template.append(
            #        f'pragma Import (C, SET_{timer}, "{procname}_RI_SET_{timer}");')
            ads_template.append(f'procedure RESET_{timer} '
                    f'renames {process_name}_RI.Reset_{timer};')
            ri_stub_ads.append(f'procedure RESET_{timer};')
            ri_stub_adb.append(f'procedure RESET_{timer} is null;')
            #ads_template.append(
            #     f'pragma Import (C, RESET_{timer}, "{procname}_RI_RESET_{timer}");')
        else:
            # Generic functions get the SET and RESET from template
            pass


    if instance:
        # Instance of a process type, all the RIs (including timers) must
        # be gathered to instantiate the package
        pkg_decl = (u"package {}_Instance is new {}"
                    .format(process_name, process.instance_of_name))
        ri_list = [f"RI{SEPARATOR}{sig['name']}"
                   for sig in process.output_signals]
        ri_list.extend ([u"RI{sep}{name}".format(sep=SEPARATOR,
                                                 name=proc.inputString)
                        for proc in process.procedures if proc.external])
        ri_list.extend([u"set_{}".format(timer) for timer in process.timers])
        ri_list.extend([u"reset_{}".format(timer) for timer in process.timers])
        ri_inst = [u"{ri} => {ri}".format(ri=ri) for ri in ri_list]
        if ri_inst:
            pkg_decl += u" ({})".format(u", ".join(ri_inst))
        ads_template.append(pkg_decl + u";")
        ads_template.append(
                f"function Get_State return chars_ptr "
                f"is (New_String ({process_name}_Instance.{LPREFIX}.State'Img))"
                f" with Export, Convention => C, "
                f'Link_Name => "{process_name.lower()}_state";')

    has_cs = any(process.cs_mapping.values())

    if simu and has_cs:
        # Callback registration for Check_Queue
        taste_template.append(u'procedure Register_Check_Queue'
                              u'(Callback: Check_Queue_T) is')
        taste_template.append(u'begin')
        taste_template.append(u'Check_Queue := Callback;')
        taste_template.append(u'end Register_Check_Queue;')
        taste_template.append(u'')

    # If the process has no input, output, procedures, or timers, then Ada
    # will not compile the body - generate a pragma to fix this
    if not process.timers and not process.procedures \
            and not process.input_signals and not process.output_signals:
        ads_template.append('pragma elaborate_body;')

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
            taste_template.append(
                              'msgPending : Asn1Boolean := True;')

        # Declare the local variables needed by the transitions in the template
        taste_template.extend(set(local_decl_transitions))
        taste_template.append('begin')

        # Generate a loop that ends when a next state is reached
        # (there can be chained transition when entering a nested state)
        taste_template.append('while (trId /= -1) loop')

        # Generate the switch-case on the transition id
        taste_template.append('case trId is')

        for idx, val in enumerate(code_transitions):
            taste_template.append(u'when {idx} =>'.format(idx=idx))
            val = [u'{line}'.format(line=l) for l in val]
            if val:
                taste_template.extend(val)
            else:
                taste_template.append('null;')

        taste_template.append('when CS_Only =>')
        taste_template.append('trId := -1;')
        taste_template.append('goto Next_Transition;')

        taste_template.append('when others =>')
        taste_template.append('null;')

        taste_template.append('end case;')
        if code_labels:
            # Due to nested states (chained transitions) jump over label code
            # (NEXTSTATEs do not return from Execute_Transition)
            taste_template.append('goto Next_Transition;')

        # Add the code for the floating labels
        taste_template.extend(code_labels)

        taste_template.append('<<Next_Transition>>')

        # After completing active transition(s), check continuous signals:
        #     - Check current state(s)
        #     - For each continuous signal generate code (test+transition)
        # XXX add to C backend
        if has_cs and not simu:
            taste_template.append('--  Process continuous signals')
            taste_template.append('if {}.Init_Done then'.format(LPREFIX))
            taste_template.append("Check_Queue (msgPending);")
            taste_template.append('end if;')
            ads_template.append('procedure Check_Queue (Res : out Asn1Boolean);')
            if not generic:
                ads_template.append(f'pragma Import(C, Check_Queue, "{process_name}_check_queue");')
        elif has_cs and simu:
            taste_template.append('if {}.Init_Done then'.format(LPREFIX))
            taste_template.append("Check_Queue (msgPending);")
            taste_template.append('end if;')
            # simulation: create a callback registration function
            ads_template.append('type Check_Queue_T is access procedure'
                                '(Res : out Asn1Boolean);')
            ads_template.append('pragma Convention(Convention => C,'
                                ' Entity => Check_Queue_T);')
            ads_template.append('Check_Queue : Check_Queue_T;')
            ads_template.append('procedure Register_Check_Queue'
                                '(Callback : Check_Queue_T);')
            ads_template.append('pragma Export (C, Register_Check_Queue,'
                                ' "register_check_queue");')
        else:
            taste_template.append('null;')

        # Process the continuous signals in state aggregations first
        # (reminder: state aggregations = parallel states)
        done = []
        sep = 'if '
        last = ''
        # flag indicating there are CS in nested states but not at root
        need_final_endif = False
        for cs, agg in product(process.cs_mapping.items(),
                               aggregates.items()):
            (statename, cs_item)  = cs
            (agg_name, substates) = agg

            if not cs_item:
                continue
            for each in substates:
                if statename in each.cs_mapping and each.cs_mapping[statename]:
                    #print("statename --->", statename)
                    #print("cs_item   --->", cs_item)
                    #print("agg_name  --->", agg_name)
                    #print("substates --->", substates)
                    need_final_endif = True
                    first = "els" if done else ""
                    taste_template.append(
                            f'{first}if not msgPending and '
                            f'trId = -1 and '
                            f'{LPREFIX}.State = {ASN1SCC}{agg_name} and '
                            f'{LPREFIX}.{each.statename}{SEPARATOR}State = '
                            f'{ASN1SCC}{statename} then')
                    # Change priority 0 (no priority set) to lowest priority
                    lowest_priority = max(item.priority for item in cs_item)
                    for each in cs_item:
                        if each.priority == 0:
                            each.priority = lowest_priority + 1
                    for provided_clause in sorted(cs_item,
                                                 key=lambda itm: itm.priority):
                        taste_template.append(u'--  CS Priority {}'
                                             .format(provided_clause.priority))
                        trId = process.transitions.index\
                                            (provided_clause.transition)
                        code, loc = generate(provided_clause.trigger,
                                             branch_to=trId,
                                             sep=sep, last=last)
                        sep='elsif '
                        taste_template.extend(code)
                    done.append(statename)
                    taste_template.append(u'end if;')  # inner if
                    sep = 'if '
                    break

        for statename in process.cs_mapping.keys() - done:
            cs_item = process.cs_mapping[statename]
            if cs_item:
                need_final_endif = False
                first = "els" if done else ""
                taste_template.append(
                        f'{first}if not msgPending and '
                        f'trId = -1 and {LPREFIX}.State = {ASN1SCC}{statename}'
                        ' then')
            # Change priority 0 (no priority set) to lowest priority
            if cs_item:
                lowest_priority = max(item.priority for item in cs_item)
            for each in cs_item:
                if each.priority == 0:
                    each.priority = lowest_priority + 1
            for provided_clause in sorted(cs_item,
                                          key=lambda itm: itm.priority):
                taste_template.append(u'--  Priority {}'
                                      .format(provided_clause.priority))
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
                taste_template.append(u'end if;') # inner if
                taste_template.append(u'end if;') # current state
            sep = 'if '

        if need_final_endif:
            taste_template.append(u'end if;')

        taste_template.append('end loop;')
        taste_template.append('end Execute_Transition;')
        taste_template.append('\n')
    elif not instance:
        # No transitions defined, but keep the interface for CS_Only calls
        taste_template.append('procedure Execute_Transition (Id : Integer) is')
        taste_template.append('begin')
        taste_template.append('null;')
        taste_template.append('end Execute_Transition;')
        taste_template.append('\n')

    # Add code of the package elaboration
    taste_template.extend(start_transition)
    taste_template.append(f'end {process_name};')

    ads_template.append(f'end {process_name};')

    ri_stub_ads.append(f'end {process_name}_RI;')
    ri_stub_adb.append(f'end {process_name}_RI;')

    with open(process_name.lower() + os.extsep + 'adb', 'wb') as ada_file:
        code = '\n'.join(format_ada_code(taste_template)).encode('latin1')
        ada_file.write(code)

    with open(process_name.lower() + os.extsep + 'ads', 'wb') as ada_file:
        ada_file.write(
                '\n'.join(format_ada_code(ads_template)).encode('latin1'))

    if not taste:
        with open(f"{process_name.lower()}_ri.ads", "wb") as ri_stub:
            ri_stub.write ("\n".join(format_ada_code(ri_stub_ads)).encode('latin1'))
        stub_adb = f'{process_name.lower()}_ri.adb'
        # don't overwrite adb as it may contain user code
        # also don't generate if there are no RI in the system
        if not os.path.exists(stub_adb) and len(ri_stub_adb) > 2:
            with open(stub_adb, "wb") as ri_stub:
                ri_stub.write ("\n".join(format_ada_code(ri_stub_adb)).encode('latin1'))

    with open("{}_ada.gpr".format(process_name.lower()), "wb") as gprada:
        gprada.write(ada_gpr.encode('utf-8'))

    if simu:
        with open(u'{}_interface.aadl'
                  .format(process_name.lower()), 'wb') as aadl:
            aadl.write(u'\n'.join(minicv).encode('latin1'))
        script = '{}_simu.sh'.format(process_name.lower())
        with open(script, 'w') as bash_script:
            bash_script.write(simu_script)
        with open("{}_lib.gpr".format(process_name.lower()), 'w') as gprlib:
            gprlib.write(lib_gpr)
        os.chmod(script, os.stat(script).st_mode | stat.S_IXUSR)


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
    elif type_kind.endswith('StringType'):
        if isinstance(param, ogAST.PrimStringLiteral):
            # Raw string
            # First remove the newline statements
            text = param.value[1:-1].replace('"', "'").split('\n')
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
                       'BooleanType', 'Integer32Type'):
        code, string, local = expression(param, readonly=1)
        if hasattr(param, "expected_type"):
            cast = type_name(param.expected_type)
        else:
            cast = type_name(param.exprType)
        code.append(f"Put ({cast}'Image ({string}));")
    elif type_kind == 'EnumeratedType':
        code, string, local = expression(param, readonly=1)
        code.append(f"Put ({type_name(param.exprType)}'Image ({string}));")
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
            if not SHARED_LIB:
                code.append(f'RESET_{p_id};')
            else:
                code.append(f'RESET_{p_id} (New_String ("{p_id}"));')
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
                local_decl.append(f'{tmp_id} : asn1SccT_UInt32;')
                code.append(f'{tmp_id} := {t_val};')
                code.append(f"SET_{p_id} ({tmp_id});")
            else:
                code.append(f'SET_{p_id} (New_String ("{p_id}"), {t_val});')
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
                    if SHARED_LIB:
                        is_out_sig = True
                        list_of_params = [
                                f'New_String ("{out["outputName"]}")']
            except ValueError:
                # Not there? Impossible, the parser would have barked
                raise ValueError('Probably a bug - please report'
                        ' (related to ' + signal_name.lower() + ')')
        if out_sig:
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
                    local_decl.extend(debug_trace())
                    local_decl.append(f'{tmp_id} : {typename};')
                    basic_param = find_basic_type (param_type)
                    if basic_param.kind.startswith('Integer'):
                        p_id = f"{typename} ({p_id})"
                    if isinstance(param,
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
                        p_id = array_content(param, p_id,
                                             find_basic_type(param_type))

                    if isinstance(param, ogAST.ExprAppend):
                        # Process Append constructs properly when they are
                        # used as raw params (e.g. callme(a//b//c))
                        # TODO: ogAST.PrimSubstring seem to be missing
                        # Check the template in def _conditional
                        app_len = append_size(param)
                        code.extend(debug_trace())
                        code.append(u'{tmp}.Data (1 .. {app_len}) := {val};'
                               .format(tmp=tmp_id, app_len=app_len, val=p_id))
                        if basic_param.Min != basic_param.Max:
                            # Append should only apply to this case, i.e.
                            # types of varying length...
                            code.append(u'{tmp}.Length := {app_len};'
                                    .format(tmp=tmp_id, app_len=app_len))
                    else:
                        code.append(u'{} := {};'.format(tmp_id, p_id))
                    list_of_params.append(u"{}{}"
                                          .format(tmp_id,
                                                  u", {}'Size".format(tmp_id)
                                                     if is_out_sig else ""))
                else:
                    # Output parameters/local variables
                    list_of_params.append(u"{var}{shared}"
                                         .format(var=p_id,
                                                shared=", {}'Size".format(p_id)
                                                  if is_out_sig else ""))
            name = out["outputName"]
            if list_of_params:
                params=', '.join(list_of_params)
                code.append(f'RI{SEPARATOR}{name}({params});')

            else:
                if not SHARED_LIB:
                    code.append(f'RI{SEPARATOR}{name};')
                else:
                    code.append(f'RI{SEPARATOR}{name} (New_String ("{name}"));')
        else:
            # inner procedure call
            list_of_params = []
            for param in out.get('params', []):
                p_code, p_id, p_local = expression(param, readonly=1)
                code.extend(p_code)
                local_decl.extend(p_local)
                # no need to use temporary variables, we are in pure Ada
                list_of_params.append(p_id)
            if list_of_params:
                code.append(u'p{sep}{proc}({params});'.format(
                    sep=SEPARATOR,
                    proc=proc.inputString,
                    params=', '.join(list_of_params)))
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
            raise TypeError("{} - TaskAssign: '{}' (please report this bug)"
                            .format(str(err), task.inputString))
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
                    stop_str = u'{} - 1'.format(stop_str)
                stmt.append(u'for {it} in {start}{stop} loop'
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
                range_str = f"1 .. {list_str}.Length".format(list_str)
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
            stmt.append(u'{it} := {it} + {step};'.format(it=loop['var'],
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

    ada_string = u'{sep}{name}'.format(sep=sep, name=prim.value[0])

    return [], str(ada_string), []


@expression.register(ogAST.PrimCall)
def _prim_call(prim, **kwargs):
    ''' Cover all built-in functions and inner procedures with RETURN stmt '''
    stmts, ada_string, local_decl = [], '', []

    ident = prim.value[0].lower()
    params = prim.value[1]['procParams']

    if ident in ('abs', 'fix', 'float'):

        # Fix operator: make a cast depending on the lower range
        unsigned = False
        if ident == "fix":
            unsigned = float(find_basic_type(params[0].exprType).Min) >= 0

        # Debug output:
#       elif ident == "abs":
#           print "\nABS EXPRESSION: ", prim.inputString,
#           print "- parameter type / expression type: ", \
#                   type_name (find_basic_type (params[0].exprType)), \
#                   type_name (find_basic_type (prim.exprType))

        param_stmts, param_str, local_var = expression(params[0], readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += '{op}({param})'.format(
                param=param_str,
                op='abs'           if ident == 'abs'
                else 'Asn1Int'     if (ident == 'fix'  and not unsigned)
                else 'Asn1UInt'    if (ident == 'fix'  and unsigned)
                else 'Asn1Real'    if ident  == 'float' else 'ERROR')
#        if ident == 'abs':
#            ada_string += ')'
    elif ident == 'power':
        operands = [None, None]
        for idx, param in enumerate(params):
            stmt, operands[idx], local = expression(param, readonly=1)
            stmts.extend(stmt)
            local_decl.extend(local)
        ada_string += '{op[0]} ** Natural({op[1]})'.format(op=operands)
    elif ident == 'length':
        # Length of sequence of: take only the first parameter
        # return an Integer32 type
        exp = params[0]
        exp_type = find_basic_type(exp.exprType)
        min_length = getattr(exp_type, 'Min', None)
        max_length = getattr(exp_type, 'Max', None)
        if min_length is None or max_length is None:
            error = '{} is not a SEQUENCE OF'.format(
                    exp.inputString)
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
                range_str = u"{}'Length".format(param_str)
            else:
                range_str = u"{}.Length".format(param_str)
            ada_string += range_str
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
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += ('{}.Kind'.format(param_str))
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
        ada_string += (u'(case {var}.Kind is '.format(var=varstr))
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
            set_value = '{var}.{name}'.format(var=varstr, name=child_name_ada)
            if need_cast and float(child_sort.Min) >= 0.0:
                set_value = 'Asn1Int({})'.format(set_value)
            choices.append(f'when {child_id} => {set_value}')
        if need_default:
            choices.append(f'when others => {defaultstr}')
        ada_string += ', '.join(choices) + ')'
    elif ident == 'exist':
        # User wants to know if an optional field is present or not
        selector = params[0]  # type PrimSelector
        receiver = selector.value[0]
        field    = selector.value[1]
        rec_stmt, rec_str, rec_decl = expression (receiver, readonly=1)
        stmts.extend(rec_stmt)
        local_decl.extend(rec_decl)
        ada_string += '({rec}.exist.{field} = 1)'.format(rec   = rec_str,
                                                         field = field)
    elif ident in ('to_selector', 'to_enum'):
        variable, target_type = params
        var_typename = type_name (variable.exprType)
        var_stmts, var_str, var_decl = expression (variable, readonly=1)
        stmts.extend(var_stmts)
        local_decl.extend(var_decl)
        sort_name = 'asn1Scc' + target_type.value[0].replace('-', '_')
        if ident == 'to_selector':
            sort_name += '_selection'
        ada_string += "{sort}'Val ({var_type}'Pos ({var_str}))"\
                .format(sort=sort_name,
                        var_type=var_typename,
                        var_str=var_str)
    elif ident == 'val':
        variable, target_type = params
        var_typename = type_name (variable.exprType)
        var_stmts, var_str, var_decl = expression (variable, readonly=1)
        stmts.extend(var_stmts)
        local_decl.extend(var_decl)
        sort_name = 'asn1Scc' + target_type.value[0].replace('-', '_')
        ada_string += "{sort}'Val ({var_str})"\
                .format(sort=sort_name,
                        var_str=var_str)
    elif ident == 'num':
        # User wants to get an enumerated corresponding integer value
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        if float(find_basic_type(prim.exprType).Min) >= 0:
            asn1_sort = "Asn1UInt"
        else:
            asn1_sort = "Asn1Int"
        local_decl.append('function num_{sort} is new Ada.Unchecked_Conversion'
                          '({sort}, {asn1Sort});'.format(sort=exp_typename,
                                                         asn1Sort=asn1_sort))
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += ('num_{sort}({p})'
                       .format(sort=exp_typename,
                               p=param_str))
    elif ident == 'floor':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Floor({p})".format(sort=exp_typename,
                                                 p=param_str)
    elif ident == 'ceil':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Ceiling({p})".format(sort=exp_typename,
                                                   p=param_str)
    elif ident == 'cos':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += "Math.Cos({})".format(param_str)
    elif ident == 'round':
        exp = params[0]
        exp_typename = type_name(exp.exprType)
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        ada_string += "{sort}'Rounding({p})".format(sort=exp_typename,
                                                    p=param_str)
    elif ident == 'sin':
        exp = params[0]
        param_stmts, param_str, local_var = expression(exp, readonly=1)
        stmts.extend(param_stmts)
        local_decl.extend(local_var)
        local_decl.append('package Math is new '
                          'Ada.Numerics.Generic_Elementary_Functions'
                          '(Asn1Real);')
        ada_string += "Math.Sin({})".format(param_str)
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
    else:
        # inner procedure call (with a RETURN statement)
        ada_string += f'p{SEPARATOR}{ident}' + (' (' if params else '')
        # Take all params and join them with commas
        list_of_params = []
        for param in params:
            param_stmt, param_str, local_var = expression(param, readonly=1)
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
        r2_string = f"Integer ({r2_string}) + 1".format(r2_string)

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

    receiver = prim.value[0]
    field_name = prim.value[1]

    receiver_stms, receiver_string, receiver_decl = expression(receiver,
                                                               readonly=ro)

    ada_string = receiver_string
    stmts.extend(receiver_stms)
    local_decl.extend(receiver_decl)

    receiver_bty = find_basic_type(receiver.exprType)

    # for asn1scc v3, sort = type_name(receiver.exprType)
    if receiver_bty.kind == 'ChoiceType':
        ada_string = (u'{ada_string}.{field_name}'
                    .format(field_name=field_name,
                            ada_string=ada_string))
    else:
        # SEQUENCE, check for field optionality first
        child = child_spelling(field_name, receiver_bty)
        if receiver_bty.Children[child].Optional == 'True' \
                and not kwargs.get("readonly", 0):
            # Must set Exist only when assigning value, not each time it is
            # accessed: this is what "readonly" ensures.
            stmts.append(u'{}.Exist.{} := 1;'.format(ada_string, field_name))
        ada_string += '.' + field_name

    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimStateReference)
def _primary_state_reference(prim, **kwargs):
    ''' Reference to the current state '''
    return [], u'{}.state'.format(LPREFIX), []

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

#   print '\nBINARY EXPRESSION:', expr.inputString, type_name(find_basic_type(expr.exprType)),
#   print "Left type = ", type_name(find_basic_type (expr.left.exprType)),
#   print "- Right type = ", type_name(find_basic_type (expr.right.exprType))

    # Check if either side is a literal number
    right_is_numeric = is_numeric(right_str)
    left_is_numeric  = is_numeric(left_str)

    lbty = find_basic_type(expr.left.exprType)
    rbty = find_basic_type(expr.right.exprType)

    if left_is_numeric != right_is_numeric or rbty.kind == lbty.kind:
        # No cast is needed if:
        # - one of the two sides only is a literal : no cast is needed
        # - or if the the basic types are identical
        ada_string = u'({left} {op} {right})'.format(left=left_str,
                                                     op=expr.operand,
                                                     right=right_str)

    elif left_is_numeric == right_is_numeric == True:
        # Both sides are literals : compute the result on the fly
        ada_string = u"{}".format(eval(u"{left} {op} {right}"
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
                          'BooleanType',
                          'EnumeratedType',
                          'ChoiceEnumeratedType')
    if basic:
        # Cast in case a side is using a 32bits ints (eg when using Length(..))
        if lbty.kind == 'IntegerType' and rbty.kind != lbty.kind:
            right_str = f'{type_name(lbty)} ({right_str})'
        elif rbty.kind == 'IntegerType' and lbty.kind != rbty.kind:
            left_str = f'{type_name(rbty)}({left_str})'
        ada_string = f'({left_str} {expr.operand} {right_str})'
    else:
        if asn1_type in TYPES:
            if isinstance(expr.right,
                          (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
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
    if basic_left.kind in ('SequenceOfType', 'OctetStringType'):
        rlen = u"{}'Length".format(right_str)

        if isinstance(expr.right, ogAST.PrimSubstring):
            if not isinstance(expr.left, ogAST.PrimSubstring):
                # only if left is not a substring, otherwise syntax
                # would be wrong due to result of _prim_substring
                strings.append(u"{lvar}.Data(1..{rvar}'Length) := {rvar};"
                               .format(lvar=left_str,
                                       rvar=right_str))
            else:
               # left is substring: no length, direct assignment
               rlen = ""
               strings.append(u"{lvar} := {rvar};"
                               .format(lvar=left_str,
                                       rvar=right_str))

        elif isinstance(expr.right, ogAST.ExprAppend):
            basic_right = find_basic_type(expr.right.exprType)
            rlen = append_size(expr.right)
            strings.append(u"{lvar}.Data(1..{lstr}) := {rvar};"
                           .format(lvar=left_str,
                                   rvar=right_str,
                                   lstr=rlen))

        elif isinstance(expr.right, (ogAST.PrimSequenceOf,
                                    ogAST.PrimStringLiteral)):
            if not isinstance(expr.left, ogAST.PrimSubstring):
                strings.append(u"{lvar} := {value};"
                           .format(lvar=left_str,
                                   value=array_content(expr.right,
                                                       right_str,
                                                       basic_left)))
            else:
               # left is substring: no length, direct assignment
               strings.append(u"{lvar} := ({rvar});"
                               .format(lvar=left_str,
                                       rvar=right_str))

            rlen = None
        else:
            # Right part is a variable
            strings.append(u"{} := {};".format(left_str, right_str))
            rlen = None
        if rlen and basic_left.Min != basic_left.Max:
            strings.append(u"{lvar}.Length := {rlen};"
                           .format(lvar=left_str, rlen=rlen))
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
        #print cast_left, cast_right, right_str
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

        strings.append(f"{left_str} := {res};".format(left_str, res))
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
def _bitwise_operators(expr, **kwargs):
    ''' Logical operators '''
    code, local_decl = [], []
    left_stmts, left_str, left_local = expression(expr.left, readonly=1)
    right_stmts, right_str, right_local = expression(expr.right, readonly=1)
    basic_type = find_basic_type(expr.exprType)
    if basic_type.kind != 'BooleanType':
        # Sequence of boolean or bit string
        if expr.right.is_raw:
            # Declare a temporary variable to store the raw value
            tmp_string = u'tmp{}'.format(expr.right.tmpVar)
            local_decl.append(u'{tmp} : {sort};'.format(
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
    return code, str(ada_string), local_decl


@expression.register(ogAST.ExprNeg)
def _neg_expression(expr, **kwargs):
    ''' Generate the code for a negative expression '''
    code, local_decl = [], []
    expr_stmts, expr_str, expr_local = expression(expr.expr, readonly=1)
    # Debug output:
#   print "\nNEG Expression: ", expr.inputString,
#   print " - Inner type: ", type_name (find_basic_type (expr.exprType))
    cast = type_name (find_basic_type (expr.exprType))
    if not is_numeric(expr_str):
        ada_string = u'(-{cast}({expr}))'.format(cast=cast, expr=expr_str)
    else:
         ada_string = u'(-{expr})'.format(expr=expr_str)
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

    self_standing = False
    left = u'{}{}'.format(left_str, string_payload(expr.left, left_str) if
                    isinstance(expr.left, (ogAST.PrimVariable,
                                           ogAST.PrimConstant)) else '')
    if isinstance(expr.right, (ogAST.PrimVariable,
                               ogAST.PrimConditional,
                               ogAST.PrimConstant)):
        payload = string_payload(expr.right, right_str)
        self_standing = True
    else:
        payload = ''
    if isinstance (expr.right, ogAST.PrimSubstring):
        self_standing = True
    right = u'{}{}'.format(right_str, payload)
#   print "Append:", expr.inputString
#   print "        LEFT      = ", left
#   print "        RIGHT     = ", right, isinstance(expr.right, ogAST.PrimSubstring)
#   print "        Payload   = ", payload
    try:
        name_of_type = type_name (expr.expected_type)
    except (NotImplementedError, AttributeError):
        name_of_type = type_name (expr.left.exprType)
#   print "        Left type = ", name_of_type
#   print "        Right range = ", expr.right.exprType.Max

    if not self_standing:
        right = u"{sort}_Array'({right}, others => <>)(1 .. {rMax})".format(
                right=right,
                sort=name_of_type,
                rMax=expr.right.exprType.Max)

    ada_string = \
      u"(({left}) & {right})".format(left=left, right=right)
#     u"(({left}) & {sort}_Array'({right}, others => <>)(1 .. {rMax}))".format(
#        left=left,
#        right=right,
#        sort=name_of_type,
#        rMax=expr.right.exprType.Max)


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

        local_decl.extend([u'tmp{} : constant array (1 .. {}) of {} := ({});'
                .format(expr.tmpVar, size, sort, left_str)])
        ada_string = u'(for some var of tmp{} => var = {})'.format(expr.tmpVar,
                                                                 right_str)
    else:
        local_decl.extend([u'tmp{} : Boolean := False;'.format(expr.tmpVar)])
        ada_string = u'tmp{}'.format(expr.tmpVar)

        stmts.append(u"in_loop_{}:".format(ada_string))
        left_type = find_basic_type(expr.left.exprType)

        if isinstance(expr.left, ogAST.PrimSubstring):
            len_str = u"{}'Length".format(left_str)
        else:
            len_str = u"{}.Length".format(left_str)
            left_str += u".Data"

        if left_type.Min != left_type.Max:
            stmts.append(u"for elem in 1..{} loop".format(len_str))
        else:
            stmts.append(u"for elem in {}'Range loop".format(left_str))

        stmts.append(u"if {container}(elem) = {pattern} then".format
                (container=left_str, pattern=right_str))

        stmts.append(u"{} := True;".format(ada_string))
        stmts.append(u"end if;")

        stmts.append(u"exit in_loop_{tmp} when {tmp} = True;"
                      .format(tmp=ada_string))
        stmts.append(u"end loop in_loop_{};".format(ada_string))

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
        ada_string = u'({})'.format(primary.value[0])
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
    ada_string = u'{}_Init'.format(type_name(primary.exprType))
    return [], str(ada_string), []


@expression.register(ogAST.PrimStringLiteral)
def _string_literal(primary, **kwargs):
    ''' Generate code for a string (Octet String) '''
    basic_type = find_basic_type(primary.exprType)
    # If user put a literal string to fill an Octet string,
    # then convert the string to an array of unsigned_8 integers
    # as expected by the Ada type corresponding to Octet String
    unsigned_8 = [str(ord(val)) for val in primary.value[1:-1]]

    ada_string = u', '.join(unsigned_8)
    return [], str(ada_string), []


@expression.register(ogAST.PrimConstant)
def _constant(primary, **kwargs):
    ''' Generate code for a reference to an ASN.1 constant '''
    return [], str(primary.constant_c_name), []


@expression.register(ogAST.PrimMantissaBaseExp)
def _mantissa_base_exp(primary, **kwargs):
    ''' Generate code for a Real with Mantissa-base-Exponent representation '''
    # TODO
    return [], u'', []


@expression.register(ogAST.PrimConditional)
def _conditional(cond, **kwargs):
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
    stmts.append(u'if {if_str} then'.format(if_str=if_str))

    basic_then = find_basic_type(cond.value['then'].exprType)
    basic_else = find_basic_type(cond.value['else'].exprType)

    then_len = None
    if not tmp_type.startswith('String') and isinstance(cond.value['then'],
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
        then_str = array_content(cond.value['then'], then_str, basic_then)
    if isinstance(cond.value['then'], ogAST.ExprAppend):
        then_len = append_size(cond.value['then'])
        stmts.append(u"tmp{idx}.Data(1..{then_len}) := {then_str};"
                     .format(idx=cond.value['tmpVar'],
                             then_len=then_len, then_str=then_str))
    elif isinstance(cond.value['then'], ogAST.PrimSubstring):
        stmts.append(u"tmp{idx}.Data(1..{then_str}'Length) := {then_str};"
                     .format(idx=cond.value['tmpVar'], then_str=then_str))
        if basic_then.Min != basic_then.Max:
            then_len = u"{}'Length".format(then_str)
    else:
        stmts.append(u'tmp{idx} := {then_str};'
                     .format(idx=cond.value['tmpVar'], then_str=then_str))
    if then_len:
        stmts.append(u"tmp{idx}.Length := {then_len};"
                     .format(idx=cond.value['tmpVar'], then_len=then_len))

    stmts.append('else')
    else_len = None
    if not tmp_type.startswith('String') and isinstance(cond.value['else'],
                              (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
        else_str = array_content(cond.value['else'], else_str, basic_else)

    if isinstance(cond.value['else'], ogAST.ExprAppend):
        else_len = append_size(cond.value['else'])
        stmts.append(u"tmp{idx}.Data(1..{else_len}) := {else_str};"
                     .format(idx=cond.value['tmpVar'],
                             else_len=else_len, else_str=else_str))
    elif isinstance(cond.value['else'], ogAST.PrimSubstring):
        stmts.append(u"tmp{idx}.Data(1..{else_str}'Length) := {else_str};"
                     .format(idx=cond.value['tmpVar'], else_str=else_str))
        if basic_else.Min != basic_else.Max:
            else_len = u"{}'Length".format(else_str)
    else:
        stmts.append(u'tmp{idx} := {else_str};'.format(
                                                    idx=cond.value['tmpVar'],
                                                    else_str=else_str))
    if else_len:
        stmts.append(u"tmp{idx}.Length := {else_len};"
                     .format(idx=cond.value['tmpVar'], else_len=else_len))
    stmts.append('end if;')
    ada_string = u'tmp{idx}'.format(idx=cond.value['tmpVar'])
    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimSequence)
def _sequence(seq, **kwargs):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    stmts, local_decl = [], []
    try:
        ada_string = u"{}'(".format(type_name(seq.exprType))
    except NotImplementedError as err:
        raise TypeError("Bug - unknown type in Sequence: {}"
                        .format(str(seq.value)))

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
        value_stmts, value_str, local_var = expression(value, readonly=1)
        if isinstance(value, (ogAST.PrimSequenceOf, ogAST.PrimStringLiteral)):
            value_str = array_content(value, value_str,
                                      find_basic_type(elem_specty))
        ada_string += f"{sep} {elem} => {value_str}"
        if elem.lower() in optional_fields:
            # Set optional field presence
            optional_fields[elem.lower()]['present'] = True
        sep = u', '
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
        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        tab.append(u'{i} => {value}'.format(i=i + 1, value=item_str))
    ada_string = u', '.join(tab)
    return stmts, str(ada_string), local_decl


@expression.register(ogAST.PrimChoiceItem)
def _choiceitem(choice, **kwargs):
    ''' Return the Ada code for a CHOICE expression '''
    stmts, choice_str, local_decl = expression(choice.value['value'],
                                               readonly=1)
    if isinstance(choice.value['value'], (ogAST.PrimSequenceOf,
                                          ogAST.PrimStringLiteral)):
        choice_str = array_content(choice.value['value'], choice_str,
                               find_basic_type(choice.value['value'].exprType))
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
    ada_string = u'(Kind => {kind}, {opt} => {expr})'.format(
                        kind=prefix,
                        opt=choice.value['choice'],
                        expr=choice_str)
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
        it is possible to passs a list of exit calls: this is for nested
        functions when they are exited with a continuous signal at a level
        above, a chain a calls to exit procedures has to be added.
        This option is used for example when generating the code of
        continuous signal: the code is generated in the <<Next_Transition>>
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
        code.append('-- Informal decision was ignored: {}'
                    .format(dec.inputString))
        code.append('null;')
        return code, local_decl
    else:
        question_type = dec.question.exprType
        actual_type = type_name(question_type)
        basic = find_basic_type(question_type).kind in ('IntegerType',
                                                        'Integer32Type',
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

        elif a.kind in ('open_range', 'constant'):
            ans_stmts, ans_str, ans_decl = expression(a.constant, readonly=1)
            code.extend(ans_stmts)
            local_decl.extend(ans_decl)
            if not basic:
                if a.openRangeOp in (ogAST.ExprEq, ogAST.ExprNeq):
                    if isinstance(a.constant, (ogAST.PrimSequenceOf,
                                               ogAST.PrimStringLiteral)):
                        ans_str = array_content(a.constant, ans_str,
                                                find_basic_type(question_type))
                    exp = f'{actual_type}_Equal(tmp{dec.tmpVar}, {ans_str})'
                    if a.openRangeOp == ogAST.ExprNeq:
                        exp = f'not {exp}'
                else:
                    exp = f'tmp{dec.tmpVar} {a.openRangeOp.operand} {ans_str}'
            else:
                exp = f'({q_str}) {a.openRangeOp.operand} {ans_str}'

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

        elif a.kind == 'closed_range':
            cl0_stmts, cl0_str, cl0_decl = expression(a.closedRange[0],
                                                      readonly=1)
            cl1_stmts, cl1_str, cl1_decl = expression(a.closedRange[1],
                                                      readonly=1)
            code.extend(cl0_stmts)
            local_decl.extend(cl0_decl)
            code.extend(cl1_stmts)
            local_decl.extend(cl1_decl)
            code.append('{sep} {dec} >= {cl0} and {dec} <= {cl1} then'
                        .format(sep=sep, dec=q_str, cl0=cl0_str, cl1=cl1_str))
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
                code.append('trId := {};'.format(branch_to))
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
    return ['goto {label};'.format(label=lab.inputString)], []


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
                history = tr.terminator.inputString.strip() == '-'
                if tr.terminator.next_is_aggregation and not history: # XXX add to C generator
                    code.append(u'-- Entering state aggregation {}'
                                .format(tr.terminator.inputString))
                    # Call the START function of the state aggregation
                    code.append(f'{tr.terminator.next_id};')
                    code.append(
                      f'{LPREFIX}.State := {ASN1SCC}{tr.terminator.inputString};')
                    code.append('trId := -1;')
                elif not history: # tr.terminator.inputString.strip() != '-':
                    code.append(u'trId := ' +
                                str(tr.terminator.next_id) + u';')
                    if tr.terminator.next_id == -1:
                        if not tr.terminator.substate: # XXX add to C generator
                            code.append(f'{LPREFIX}.State := {ASN1SCC}{tr.terminator.inputString};')
                        else:
                            code.append(f'{LPREFIX}.{tr.terminator.substate}{SEPARATOR}State :='
                                        f' {ASN1SCC}{tr.terminator.inputString};')
                else:
                    # "nextstate -": switch case to re-run the entry transition
                    # in case of a composite state or state aggregation
                    if any(next_id
                           for next_id in tr.terminator.candidate_id.keys()
                           if next_id != -1):
                        code.append('case {}.State is'.format(LPREFIX))
                        for nid, sta in tr.terminator.candidate_id.items():
                            if nid != -1:
                                if tr.terminator.next_is_aggregation:
                                    statement = u'{};'.format(nid)
                                else:
                                    statement = u'trId := {};'.format(nid)
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
                code.append('goto Next_Transition;')
            elif tr.terminator.kind == 'join':
                code.append(u'goto {label};'.format(
                    label=tr.terminator.inputString))
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
                    cond = u'{ctxt}.{sib}{sep}State = {asn1scc}state{sep}end'
                    conds = [cond.format(sib=sib,
                                         ctxt=LPREFIX,
                                         sep=SEPARATOR,
                                         asn1scc=ASN1SCC)
                            for sib in tr.terminator.siblings
                            if sib.lower() != tr.terminator.substate.lower()]
                    code.append(u'if {} then'.format(' and '.join(conds)))
                if tr.terminator.next_id == -1:
                    if tr.terminator.return_expr:
                        stmts, string, local = \
                                expression(tr.terminator.return_expr,
                                           readonly=1)
                        code.extend(stmts)
                        local_decl.extend(local)
                    code.append(u'return{};'
                                .format(' ' + string if string else ''))
                else:
                    code.append(u'trId := ' + str(tr.terminator.next_id) + ';')
                    code.append(u'goto Next_Transition;')
                if aggregate:
                    code.append(u'else')
                    code.append(u'trId := -1;')
                    code.append(u'goto Next_Transition;')
                    code.append(u'end if;')
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
    code.append(u'<<{label}>>'.format(label=label.inputString))
    if label.transition:
        code_trans, local_trans = generate(label.transition)
        code.extend(code_trans)
        local_decl.extend(local_trans)
    else:
        code.append('return;')
    return code, local_decl


def procedure_header(proc):
    ''' Build the protoype of a procedure '''
    ret_type = type_name(proc.return_type) if proc.return_type else None
    pi_header = u'{kind} {sep}{proc_name}'.format(kind='procedure'
                                                  if not proc.return_type
                                                  else 'function',
                                                  sep=(u'p' + SEPARATOR),
                                                  proc_name=proc.inputString)
    if proc.fpar:
        pi_header += '('
        params = []
        for fpar in proc.fpar:
            typename = type_name(fpar['type'])
            params.append(u'{name}: in{out} {ptype}'.format(
                    name=fpar.get('name'),
                    out=' out' if fpar.get('direction') == 'out' else '',
                    ptype=typename))
        pi_header += ';'.join(params)
        pi_header += ')'
    if ret_type:
        pi_header += ' return {}'.format(ret_type)
    return pi_header


@generate.register(ogAST.Procedure)
def _inner_procedure(proc, **kwargs):
    ''' Generate the code for a procedure - does not support states '''
    code = []
    local_decl = []
    # TODO: Update the global list of procedures
    # with procedure defined inside the current procedure
    # Not critical: the editor forbids procedures inside procedures

    if proc.external and SHARED_LIB:
        return code, local_decl

    # Save variable scopes (as local variables may shadow process variables)
    outer_scope = dict(VARIABLES)
    local_scope = dict(LOCAL_VAR)
    VARIABLES.update(proc.variables)
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
        local_decl.append(u'pragma import(C, p{sep}{proc_name}, '
                          u'"{proc_name}");'
                          .format(sep=SEPARATOR,
                                  proc_name=proc.inputString))
    else:
        # Generate the code for the procedure itself
        # local variables and code of the START transition
        # Recursively generate the code for inner-defined procedures
        for inner_proc in proc.content.inner_procedures:
            inner_code, inner_local = generate(inner_proc)
            local_decl.extend(inner_local)
            code.extend(inner_code)
        code.append(pi_header + u' is')
        for var_name, (var_type, def_value) in proc.variables.items():
            typename = type_name(var_type)
            if def_value:
                # Expression must be a ground expression, i.e. must not
                # require temporary variable to store computed result
                dst, dstr, dlocal = expression(def_value, readonly=1)
                varbty = find_basic_type(var_type)
                if varbty.kind in ('SequenceOfType', 'OctetStringType'):
                    dstr = array_content(def_value, dstr, varbty)
                assert not dst and not dlocal, 'Ground expression error'
            code.append(u'{name} : {sort}{default};'
                        .format(name=var_name,
                                sort=typename,
                                default=' := ' + dstr if def_value else ''))

        # Look for labels in the diagram and transform them in floating labels
        Helper.inner_labels_to_floating(proc)
        if proc.content.start:
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
        code.append(u'end p{sep}{procName};'.format(sep=SEPARATOR,
                                                    procName=proc.inputString))
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
    if isinstance(prim, ogAST.PrimEmptyString):
        return values
    if asnty.Min != asnty.Max:
        length = len(prim.value)
        if isinstance(prim, ogAST.PrimStringLiteral):
            # Quotes are kept in string literals
            length -= 2
        # Reference type can vary -> there is a Length field
        rlen = u", Length => {}".format(length)
    else:
        rlen = u""
    if isinstance(prim, ogAST.PrimStringLiteral):
        df = '0'
    else:
        # Find a default value for the "others" field in case of SEQOF
        _, df, _ = expression(prim.value[0], readonly=1)
        if isinstance(prim.value[0], (ogAST.PrimSequenceOf,
                                      ogAST.PrimStringLiteral)):
            df = array_content(prim.value[0], df, asnty.type)
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
                _, inner, _ = expression(each, readonly=1)
                if isinstance (each, ogAST.PrimSubstring):
                    result += u"{}'Length".format(inner)
                else:
                    result += u"{}.Length".format(inner)
    return result


def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in TYPES.keys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = TYPES[typename].type
                break
    return basic_type


def type_name(a_type, use_prefix=True):
    ''' Check the type kind and return an Ada usable type name '''
    if a_type.kind == 'ReferenceType':
        return '{}{}'.format('asn1Scc' if use_prefix else '',
                               a_type.ReferencedTypeName.replace('-', '_'))
    elif a_type.kind == 'BooleanType':
        return 'Boolean'
    elif a_type.kind.startswith('Integer32'):
        return 'Integer'
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
        return ''
    elif a_type.kind == 'EnumeratedType':
        return 'asn1Scc' if use_prefix else ''
    else:
        raise NotImplementedError('Type name for {}'.format(a_type.kind))


def child_spelling(name, bty):
    ''' Return the index in Children with the proper spelling (case, dash) '''
    for each in bty.Children:
        if name.lower().replace('_', '-') == each.lower():
            return each
    raise TypeError('Child not found: {}'.format(name))


def find_var(var):
    ''' Return a variable from the scope, with proper case '''
    for visible_var in VARIABLES.keys():
        if var.lower() == visible_var.lower():
            return visible_var
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
    trace = [u'--  {line}'.format(line=l) for l in
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
        added = [u'--  !! stack: {} {}'.format(function, line_nb)]
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
