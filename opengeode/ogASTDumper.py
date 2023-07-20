#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module dumps objects to the file.

    Copyright (c) 2023 N7Space

    Designed and implemented by Igor Jarek

    Contact: ijarek@n7space.com
"""

import logging
from types import FunctionType, MethodType, BuiltinFunctionType
from functools import singledispatch
from types import GeneratorType
from collections import defaultdict

import antlr3
from antlr3 import tree

from .ogAST import *

# Global Variables
LOG = logging.getLogger(__name__)

DEFAULT_INDENT = '    '
DUMPED_OBJECTS = set()

# End Of Global Variables

# Public Function
# You can dump to the file every object built from classes from the ogAST.py file
# (e.g. AST, Process, Block, etc.) by using `dump(filename, object)` function 
def dump(filename, object):
    LOG.info(f'Dumping object to "{filename}" file')

    DUMPED_OBJECTS.clear()

    with open(filename, 'w') as file:
        dump_user_defined_obj(object, file, 0)


# Private Functions
def dump_obj(obj_name, obj_value, is_ignored, file, indent_level):
    obj_value_type = type(obj_value)
    indent = generate_indent(indent_level)

    if len(obj_name) > 0:
        file.write('%s%s ' % (indent, obj_name))
    else:
        file.write(indent)

    file.write('[%s' % str(obj_value_type))

    if is_ignored:
        file.write(', address %s, ignored]\n' % get_obj_address_str(obj_value))
        return

    if obj_value is None:
        file.write('] is NONE\n')
        return

    if obj_value_type in (bool, int, float, str):
        dump_built_in_obj(obj_value, file, indent_level)

    elif obj_value_type in (list, set, tuple):
        dump_list_like_obj(obj_value, file, indent_level)

    elif obj_value_type in (dict, defaultdict):
        dump_dict_like_obj(obj_value, file, indent_level)

    elif obj_value_type in (bytes, bytearray):
        dump_bytes_like_obj(obj_value, file, indent_level)

    elif obj_value_type == type:
        dump_type_obj(obj_value, file, indent_level)

    elif obj_value_type == type(logging):
        dump_module_obj(obj_value, file, indent_level)

    elif obj_value_type == GeneratorType:
        dump_generator_obj(obj_value, file, indent_level)

    elif obj_value_type == TypeError:
        dump_built_in_obj(obj_value, file, indent_level)

    elif obj_value_type == antlr3.tree.CommonTree:
        file.write(', ignored]\n')

    else:
        dump_complex_obj(obj_value, file, indent_level)


def dump_built_in_obj(obj, file, indent_level):
    file.write('] ')

    obj_type = type(obj)

    if obj_type == str:
        file.write('"')
        for c in obj:
            if c == '\n':
                file.write('\\n')
            elif c == '\t':
                file.write('\\t')
            elif c == '"':
                file.write('\\"')
            else:
                file.write(c)
        file.write('"')
    else:
        file.write(str(obj))

    file.write('\n')


def dump_list_like_obj(obj, file, indent_level):
    file.write('] ')

    indent = generate_indent(indent_level)

    file.write(':\n')
    file.write('%s{\n' % indent)

    for list_elem in obj:
        dump_obj('', list_elem, False, file, indent_level + 1)

    file.write('%s}\n' % indent)


def dump_dict_like_obj(obj, file, indent_level):
    file.write('] ')

    indent = generate_indent(indent_level)
    indent_next = generate_indent(indent_level + 1)

    file.write(':\n')
    file.write('%s{\n' % indent)

    for dict_key, dict_value in obj.items():
        file.write('%s\'%s\' -> %s\n' % (indent_next, dict_key, str(type(dict_value))))
        dump_obj('', dict_value, False, file, indent_level + 2)

    file.write('%s}\n' % indent)


def dump_bytes_like_obj(obj, file, indent_level):
    file.write('] ')
    file.write(str(obj))
    file.write('\n')


def dump_type_obj(obj, file, indent_level):
    if try_mark_obj_as_dumped(obj, file):
        file.write(']\n')

        for class_obj_property_name, class_obj_property_value in class_properties_generator(obj, file, indent_level + 1):
            dump_obj(class_obj_property_name, class_obj_property_value, False, file, indent_level + 2)


def dump_module_obj(obj, file, indent_level):
    if try_mark_obj_as_dumped(obj, file):
        file.write(']\n')

        for module_property_name, module_property_value in module_properties_generator(obj, file, indent_level + 1):
            dump_obj(module_property_name, module_property_value, False, file, indent_level + 2)


def dump_generator_obj(obj, file, indent_level):
        file.write(', ignored]\n')


def dump_complex_obj(obj, file, indent_level):
    if try_mark_obj_as_dumped(obj, file):
        file.write(']\n')

        dump_user_defined_obj(obj, file, indent_level + 1)


@singledispatch
def dump_user_defined_obj(*args):
    ''' Dump user-defined objects to file '''
    raise TypeError('Incorrect, unsupported or missing data type in AST : ', type(args[0]))


@dump_user_defined_obj.register(Expression)
@dump_user_defined_obj.register(Answer)
@dump_user_defined_obj.register(Task)
@dump_user_defined_obj.register(Create)
@dump_user_defined_obj.register(Input)
@dump_user_defined_obj.register(Output)
@dump_user_defined_obj.register(Label)
@dump_user_defined_obj.register(Decision)
@dump_user_defined_obj.register(Transition)
@dump_user_defined_obj.register(Start)
@dump_user_defined_obj.register(Comment)
@dump_user_defined_obj.register(State)
@dump_user_defined_obj.register(TextArea)
def _dump_general_objs(obj, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(obj, file, indent_level):
        dump_obj(class_obj_property_name, class_obj_property_value, False, file, indent_level + 1)


@dump_user_defined_obj.register(AST)
def _dump_ast(ast, file, indent_level):
    try_mark_obj_as_dumped(ast, file)
    for class_obj_property_name, class_obj_property_value in class_properties_generator(ast, file, indent_level):
        dump_obj(class_obj_property_name, class_obj_property_value, False, file, indent_level + 1)


@dump_user_defined_obj.register(System)
def _dump_system(system, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(system, file, indent_level):
        is_ignored = False

        if class_obj_property_name == 'ast':
            is_ignored = True

        dump_obj(class_obj_property_name, class_obj_property_value, is_ignored, file, indent_level + 1)


@dump_user_defined_obj.register(Procedure)
def _dump_procedure(procedure, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(procedure, file, indent_level):
        is_ignored = False

        if class_obj_property_name == 'procedures':
            is_ignored = True

        dump_obj(class_obj_property_name, class_obj_property_value, is_ignored, file, indent_level + 1)


@dump_user_defined_obj.register(Block)
def _dump_block(block, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(block, file, indent_level):
        is_ignored = False

        if class_obj_property_name == 'parent':
            is_ignored = True

        dump_obj(class_obj_property_name, class_obj_property_value, is_ignored, file, indent_level + 1)


@dump_user_defined_obj.register(Process)
def _dump_process(process, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(process, file, indent_level):
        is_ignored = False

        if class_obj_property_name == 'parent':
            is_ignored = True
        
        dump_obj(class_obj_property_name, class_obj_property_value, is_ignored, file, indent_level + 1)


@dump_user_defined_obj.register(Terminator)
def _dump_terminator(terminator, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(terminator, file, indent_level):
        is_ignored = False

        if class_obj_property_name == 'context':
            is_ignored = True

        dump_obj(class_obj_property_name, class_obj_property_value, is_ignored, file, indent_level + 1)


@dump_user_defined_obj.register(Automaton)
def _dump_automaton(automaton, file, indent_level):
    for class_obj_property_name, class_obj_property_value in class_properties_generator(automaton, file, indent_level):
        is_ignored = False

        if class_obj_property_name == 'parent':
            is_ignored = True

        dump_obj(class_obj_property_name, class_obj_property_value, is_ignored, file, indent_level + 1)


def class_properties_generator(class_obj, file, indent_level):
    indent = generate_indent(indent_level)

    file.write('%s[%s, address %s]\n' % (indent, str(type(class_obj)), get_obj_address_str(class_obj)))
    file.write('%s{\n' % indent)

    for class_obj_property_name in dir(class_obj):
        if class_obj_property_name.startswith('__'):
            continue

        class_obj_property_value = getattr(class_obj, class_obj_property_name)

        if isinstance(class_obj_property_value, (FunctionType, MethodType, BuiltinFunctionType)):
            continue

        yield (class_obj_property_name, class_obj_property_value)

    file.write('%s}\n' % indent)


def module_properties_generator(module_obj, file, indent_level):
    indent = generate_indent(indent_level)

    file.write('%s[%s, address %s]\n' % (indent, str(type(module_obj)), get_obj_address_str(module_obj)))
    file.write('%s{\n' % indent)

    for module_property_name in dir(module_obj):
        if module_property_name.startswith('__'):
            continue

        module_property_value = getattr(module_obj, module_property_name)
        yield (module_property_name, module_property_value)

    file.write('%s}\n' % indent)


def try_mark_obj_as_dumped(obj, file):
    if id(obj) in DUMPED_OBJECTS:
        file.write(', address %s, probably dumped above]\n' % get_obj_address_str(obj))
        return False
    
    DUMPED_OBJECTS.add(id(obj))
    return True


def get_obj_address_str(obj):
    return str(hex(id(obj)))


def generate_indent(indent_level):
    return DEFAULT_INDENT * indent_level
