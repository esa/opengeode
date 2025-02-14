#!/usr/bin/env python3

from opengeode.ogParser import (parser_init, antlr3, sdl92Parser, lexer,
        parse_pr, parseSingleElement)
from opengeode import AdaGenerator
from opengeode import CGenerator
Ada_Task_Assign = AdaGenerator._task_assign
C_Task_Assign = CGenerator._task_assign

# return a string corresponding to a token number:
token = lambda num: lexer.tokenNamesMap[num]

COMMON = '''
   system parse;
        /* CIF TEXT (123, 141), (210, 140) */
        use dataview comment 'data/dv.asn';
        /* CIF ENDTEXT */
        block parse;
        process parse;
            start;
                nextstate wait;
            state wait;
            endstate;
        endprocess parse;
        endblock;
   endsystem;
'''

def test_codegen():
    # Initialize the AST (parse ASN.1 file and set context)
    og_ast, errs, warns = parse_pr(string=COMMON)
    process_ast = og_ast.processes[0]

    # Parse with ANTLR
    dcl_int = 'dcl a MyInteger;'
    # Add a variable declaration to the context
    parseSingleElement(elem='content', string=dcl_int, context=process_ast)
    assign, _, _, _, _  = parseSingleElement('task', 'task a := 42;', process_ast)
    # Generate the code in Ada
    ada_code, ada_local_decl = Ada_Task_Assign(assign)
    cmt = ada_code[0]
    stmt = ada_code[1]
    # check that the generated code in Ada is the expected one:
    assert stmt == 'a := 42;'
    # Generate the code in C
    CGenerator.TYPES = process_ast.dataview
    c_code, c_local_decl = C_Task_Assign(assign)
    cmt = c_code[0]
    stmt = c_code[1]
    # check that the generated code in Ada is the expected one:
    assert stmt == 'a = (asn1SccMyInteger) 42;'


if __name__ == '__main__':
    for name, value in dict(globals()).items():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
