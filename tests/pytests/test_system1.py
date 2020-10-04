#!/usr/bin/env python

from opengeode.ogParser import parser_init, antlr3, sdl92Parser, lexer, check_syntax

# return a string corresponding to a token number:
token = lambda num: lexer.tokenNamesMap[num]


def test_system_with_no_error():
    ''' Detect the syntax error (missing SEMI after "procedure entry") '''
    string='''system ss;
block ss;
process ss;
START;
    NEXTSTATE aa;
state aa, hh;
endstate;
endprocess ss;
endblock;
endsystem;
'''
    test = parser_init(string=string)
    # Parse and then check that the reported error is the expected one

    res = test.system_definition()
    node = res.tree
    check_syntax(node, node, True, input_string=string)

def test_system_with_error():
    ''' Detect the syntax error (missing SEMI after "procedure entry") '''
    string='''system ss;
block ss;
process ss;
START;
    NEXTSTATE -aa;
state aa, hh;
endstate;
endprocess ss;
endblock;
endsystem;
'''
    test = parser_init(string=string)
    # Parse and then check that the reported error is the expected one

    res = test.system_definition()
    node = res.tree
    try:
        check_syntax(node, recursive=True, input_string=string)
    except SyntaxError:
        pass
    else:
        assert False

def test_system_with_error_2():
    ''' no error '''
    string='''system huuh;
block huuh;
process huuh;
/* CIF START (171, 77), (70, 35) */
START;
/* CIF NEXTSTATE (171, 132), (70, 35) */
NEXTSTATE -;
/* CIF state (386, 90), (70, 35) */
state a;
endstate;
endprocess huuh;
endblock;
endsystem;
'''
    test = parser_init(string=string)
    # Parse and then check that the reported error is the expected one

    #res = test.system_definition()
    res = test.pr_file()
    node = res.tree
    try:
        check_syntax(node, recursive=True, input_string=string)
    except SyntaxError:
        err = "\n".join(test.error_list)
        raise SyntaxError(err)
    else:
        pass

if __name__ == '__main__':
    for name, value in dict(globals()).viewitems():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
