#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

    OpenGEODE - A tiny SDL Editor for TASTE

    AST that can be used to write SDL backends (code generators, etc.)
    In all classes the 'inputString' field corresponds to the exact
    text from the PR file; line and charPositionInLine refer to the
    location of the string in the input PR stream.
    The 'coordinates' field corresponds to the CIF information.
    To use the AST, you must import ogAST and ogParser
    Example of code:

    import ogParser
    import ogAST

    ast = ogParser.parse_pr(files=['file1.pr', ...], string='...')

    -> ast is of type AST (see below)

    Design note:
        classes are used here only for the purpose of convenient
        reading of the AST. There is no object-orientation needed or
        used here.

    See AdaGenerator.py for an example of use.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import logging
LOG = logging.getLogger(__name__)


class Expression(object):
    ''' AST Entry for expressions - Always use subtype '''
    is_raw = False
    def __init__(self, inputString='', line=-1, charPositionInLine=-1):
        ''' Initialize Expression attributes '''
        self.inputString = inputString
        self.line = line
        self.charPositionInLine = charPositionInLine
        # left and right are of type Expression (absent for primaries)
        self.left = None
        self.right = None
        # exprType is an ASN.1 type (as exported by asn1scc)
        self.exprType = None
        # Hint for code generators: intermediate storage identifier
        self.tmpVar = -1

    def __repr__(self):
        ''' Debug output for an expression '''
        return '{exp} ({l},{c})'.format(exp=self.inputString,
                                        l=self.line,
                                        c=self.charPositionInLine)


class ExprPlus(Expression):
    operand = '+'


class ExprMul(Expression):
    operand = '*'


class ExprMinus(Expression):
    operand = '-'


class ExprOr(Expression):
    operand = 'or'


class ExprAnd(Expression):
    operand = 'and'


class ExprXor(Expression):
    operand = 'xor'


class ExprEq(Expression):
    operand = '='


class ExprNeq(Expression):
    operand = '/='


class ExprGt(Expression):
    operand = '>'


class ExprGe(Expression):
    operand = '>='


class ExprLt(Expression):
    operand = '<'


class ExprLe(Expression):
    operand = '<='


class ExprDiv(Expression):
    operand = '/'


class ExprMod(Expression):
    operand = 'mod'


class ExprRem(Expression):
    operand = 'mod'


class ExprAssign(Expression):
    operand = ':='


class ExprAppend(Expression): pass
class ExprIn(Expression): pass
class ExprImplies(Expression): pass

class Primary(Expression):
    '''
        AST entry for a primary construction (that is a terminal expression)
        Abstract class, never used directly, see subtypes below
    '''
    is_raw = True
    def __init__(self, inputString='', line=-1, charPositionInLine=-1,
                 primary=None):
        ''' Initialize common primary attributes '''
        if primary:
            self.inputString = primary.inputString
            self.line = primary.line
            self.charPositionInLine = primary.charPositionInLine
            self.op_not = primary.op_not
            self.op_minus = primary.op_minus
            self.value = primary.value
            self.exprType = primary.exprType
        else:
            self.inputString = inputString
            self.line = line
            self.charPositionInLine = charPositionInLine
            self.op_not = False
            self.op_minus = False
            self.value = None
            self.exprType = None

    def __repr__(self):
        ''' Debug output for a primary '''
        return 'PRIMARY : {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)

# Subclasses of Primary - never use Primary directly
class PrimPath(Primary):
    ''' PrimPath is a list of elements needed to identify a value
        For example, "i!j!k(5)" is stored as:
        [ 'i', 'j', 'k', {'index':[Expression list]}]
           (in that case, 5 is an index)
        other example: "hello(world)" ->
             ['hello', {'procParams':[Expression list]'}]
        (in that case, hello is an operator and world is its parameter)
    '''
    is_raw = False

class PrimVariable(PrimPath): pass # XXX should not be raw for codegen
class PrimFPAR(PrimVariable): pass
class PrimEnumeratedValue(Primary): pass
class PrimInteger(Primary): pass
class PrimReal(Primary): pass
class PrimBoolean(Primary): pass
class PrimConstant(Primary): is_raw = False #pass
class PrimBitStringLiteral(Primary): pass   # Not supported yet
class PrimOctetStringLiteral(Primary): pass # Not supported yet


class PrimIfThenElse(Primary):
    ''' value is a dictionnary:
        { 'if': Expression, 'then': Expression,
        'else': Expression, 'tmpVar': integer}
        tmpVar can be used if the backend needs a temporary variable
        to process the ifThenElse
    '''
    pass


class PrimStringLiteral(Primary):
    ''' Value is a string with quotes '''
    @property
    def exprType(self):
        return self._exprType

    @exprType.setter
    def exprType(self, val):
#       name = getattr(self, 'value', self.inputString)
#       import traceback
#       traceback.print_stack()
#       print 'SET type of', name, 'to', val
        self._exprType = val


class PrimMantissaBaseExp(Primary):
    ''' Value is a dict: {'mantissa': int, 'base': int, 'exponent': int} '''
    pass


class PrimEmptyString(Primary): pass


class PrimChoiceItem(Primary):
    ''' Value is a dict : {'choice': string, 'value': Expression} '''
    pass


class PrimChoiceDeterminant(Primary): pass


class PrimSequenceOf(Primary):
    ''' Value is a list of Primary '''


class PrimSequence(Primary):
    ''' Value is a dict : { field1: Expression, field2: Expression } '''
    pass


class Decision(object):
    ''' AST Entry for a decision '''
    def __init__(self):
        ''' A DECISION statement '''
        self.inputString = ''
        self.line = None
        self.charPositionInLine = None
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 50
        # kind can be 'any', 'informal_text', or 'question'
        self.kind = None
        # question is an Expression
        self.question = None
        # informalText is a string (when kind == 'informal_text')
        self.informalText = None
        # list of type Answer
        self.answers = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # hint for backends needing a temporary variable to hold the question
        self.tmpVar = -1

    def __repr__(self):
        ''' Debug output for a decision '''
        return 'DECISION {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Answer(object):
    ''' AST Entry for a decision answer '''
    def __init__(self):
        ''' One ANSWER of a DECISION '''
        self.inputString = ''
        self.line = None
        self.charPositionInLine = None
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 10.5
        # one of 'closed_range' 'constant' 'open_range' 'else' 'informal_text'
        self.kind = None
        # informalText is a string, when kind == 'informal_text'
        self.informalText = None
        # closedRange is a set of two numbers
        self.closedRange = []
        # constant is an Expression
        #    (contains 'open_range' and 'constant' kinds corresponding value)
        self.constant = None
        # one of ExprEq, ExprNeq, ExprGt, ExprGe, ExprLt, ExprLe (types)
        self.openRangeOp = None
        # transition is of type Transition
        self.transition = None
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for an answer '''
        return 'ANSWER {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Task(object):
    ''' AST Entry for TASKS '''
    def __init__(self):
        ''' Initialize TASK attributes (set of ASSIGN statements) '''
        self.inputString = ''
        self.line = None
        self.charPositionInLine = None
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        self.elems = []

    def __repr__(self):
        ''' Debug output for a task '''
        return 'TASK {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class TaskAssign(Task):
    ''' 'elems' contains a list of ExprAssign expressions '''
    pass


class TaskInformalText(Task):
    ''' 'elems' contains a list of strings '''
    pass


class TaskForLoop(Task):
    '''
        'elems' is a list of for-loops:{'var': string, 'type': Asn1SccType,
        'list': Primary, 'range': {'start': expression, 'stop': expression,
        'step' : int}, 'transition': Transition }
    '''
    pass

class Output(object):
    ''' AST Entry for OUTPUT statements '''
    def __init__(self, defName=''):
        ''' Set of OUTPUT statements '''
        self.inputString = defName
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        self.line = None
        self.charPositionInLine = None
        # list of {'outputName':ID, 'params':list of Expression, 'tmpVars':[]}
        self.output = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for an Output symbol '''
        return '{exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class ProcedureCall(Output):
    ''' Procedure calls content is identical to Outputs '''
    pass


class Terminator(object):
    ''' Terminator elements (join, nextstate, stop) '''
    def __init__(self, defName=''):
        ''' Initialize terminator attributes '''
        self.inputString = defName
        self.pos_x = None
        self.pos_y = None
        self.width = 70
        self.height = 35
        self.line = None
        self.charPositionInLine = None
        # one of 'next_state' 'join' 'stop', 'return'
        self.kind = None
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # optional Label instance (to be placed just before the terminator)
        self.label = None
        # Return expression
        self.return_expr = None
        # via clause, used for entering nested state with an entry point
        # 'via' is the string for the renderer (e.g. "via foo")
        self.via = None
        # 'entrypoint' is the string of the entry point (e.g. "foo")
        self.entrypoint = None
        # some transitions can be chained, when entering/leaving nested states
        self.next_id = -1

    def __repr__(self):
        ''' Debug output for terminators '''
        return '{kind} {exp} ({l},{c}) at {x}, {y}'.format(
                exp=self.inputString,
                kind=self.kind.upper(), l=self.line, c=self.charPositionInLine,
                x=self.pos_x, y=self.pos_y)


class Label(object):
    ''' AST Entry for a Label '''
    def __init__(self):
        ''' Initialize the label attributes '''
        # inputString holds the label name
        self.inputString = ''
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        self.line = None
        self.charPositionInLine = None
        # optional hyperlink
        self.hyperlink = None
        # No comment for labels - keep to None
        self.comment = None
        # List of terminators following this label
        self.terminators = []
        # Transition is used for floating labels (see AST entry)
        self.transition = None

    def __repr__(self):
        ''' Debug output for a label '''
        return 'LABEL {label} ({l},{c})'.format(label=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Floating_label(Label, object):
    ''' AST Entry for a floating label '''
    def __init__(self, label=None):
        ''' Initialize the floating label attributes '''
        super(Floating_label, self).__init__()
        if label:
            self.inputString = label.inputString
            self.pos_x = label.pos_x
            self.pos_y = label.pos_y
            self.width = label.width
            self.height = label.height
            self.line = label.line
            self.charPositionInLine = label.charPositionInLine
            self.terminators = label.terminators
            self.transition = label.transition

    def __repr__(self):
        ''' Debug output for a label (used by code generator) '''
        return 'CONNECTION {label} ({l},{c})'.format(label=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Transition(object):
    ''' AST Entry for a complete transition '''
    def __init__(self):
        ''' Initialize the transition attributes '''
        # list of either Label, Output, Task, Decision
        self.actions = []
        # terminator is of type Terminator (it is optional)
        self.terminator = None
        # All Terminators of this transition
        self.terminators = []


    def __repr__(self):
        ''' Debug output: display all actions '''
        data = [repr(action) for action in self.actions]
        if self.terminator:
            data.append(repr(self.terminator))
        return '\n'.join(data)


class Input(object):
    ''' AST Entry for the INPUT symbol '''
    def __init__(self):
        ''' Initialize the Input attributes '''
        # inputString is the user text, it can contain several inputs
        self.inputString = ''
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        self.line = None
        self.charPositionInLine = None
        # provided clause (not supported yet)
        self.provided = None
        # transition is of type Transition
        self.transition = None
        # List of input parameters (strings: each param is a variable)
        # (If there are several inputs in the symbol, there are no parameters)
        self.parameters = []
        # list of input signal names
        self.inputlist = []
        # transition_id is an index of the process.transitions list
        self.transition_id = -1
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # list of terminators following the input symbol
        self.terminators = []

    def __repr__(self):
        ''' Debug output for an INPUT symbol '''
        return 'INPUT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Connect(Input):
    ''' AST Entry for the CONNECT part (transition below a nested state) '''
    def __init__(self):
        ''' Only one difference with INPUT: the connect_list attribute '''
        super(Connect, self).__init__()
        # List of strings
        self.connect_list = []
        self.width = 1

    def __repr__(self):
        ''' Debug output for a CONNECT symbol '''
        return 'CONNECT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Start(object):
    ''' AST Entry for the START symbol '''
    def __init__(self):
        ''' Initialize the Start symbol attributes '''
        self.inputString = ''
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        # start transition is of type Transition
        self.transition = None
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # list of terminators following the start symbol
        self.terminators = []

    def __repr__(self):
        ''' Debug output for a START symbol '''
        return 'START {}'.format(self.inputString)


class Procedure_start(Start):
    ''' Procedure start symbol - inherits from Start '''
    pass


class CompositeState_start(Start):
    ''' Composite state start symbol - inherits from Start, can have a name '''
    pass


class Comment(object):
    ''' AST Entry for COMMENT symbols '''
    def __init__(self):
        ''' Comment symbol '''
        # inputString is the comment value itself
        self.inputString = ''
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        self.line = None
        self.charPositionInLine = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a COMMENT symbol '''
        return 'COMMENT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class State(object):
    ''' AST Entry for STATE symbols '''
    def __init__(self, defName=''):
        ''' Used only for rendering backends - not for code generation '''
        # inputString contains possibly several states (and asterisk)
        self.inputString = defName
        # List of state names contained in the symbol
        self.statelist = []
        self.line = None
        self.charPositionInLine = None
        self.pos_x = 0
        self.pos_y = 0
        self.width = 70
        self.height = 35
        # list of type Input
        self.inputs = []
        # list of type Connect (connection below a nested state)
        self.connects = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # optional composite state content (type CompositeState)
        self.composite = None

    def __repr__(self):
        ''' Debug output for a STATE symbol '''
        return 'STATE {exp} ({l},{c}) at {x},{y}'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine,
                x=self.pos_x, y=self.pos_y)


class TextArea(object):
    ''' AST Entry for text areas (containing declarations/comments) '''
    def __init__(self):
        ''' Text area (raw content for rendering only) '''
        self.inputString = '-- Declare your variables\n\n' \
                           '-- Syntax: DCL <variable name> <type name>;\n\n'
        # DCL variables in the text area {name: (sort, default_value), ...}
        self.variables = {}
        self.line = None
        self.charPositionInLine = None
        # Set default coordinates and width/height
        self.pos_x = 0
        self.pos_y = 0
        self.width = 170
        self.height = 140
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a text area '''
        return 'TEXTAREA {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Automaton(object):
    ''' Elements contained in a process or a procedure '''
    def __init__(self, parent=None):
        ''' AST grouping the elements that can be rendered graphically '''
        self.parent = parent
        self.textAreas = []
        self.inner_procedures = []
        self.start = None
        self.floating_labels = []
        self.states = []
        self.named_start = []


class Procedure(object):
    ''' Internal procedure definition '''
    def __init__(self):
        ''' Procedure AST default value '''
        self.inputString = ''
        self.line = None
        self.charPositionInLine = None
        # Set default coordinates and width/height
        self.pos_x = self.pos_y = 0
        self.width = 70
        self.height = 35
        # Optional hyperlink
        self.hyperlink = None
        # Local variables dictionnary (see Process)
        self.variables = {}
        # Inherited variables from all levels above
        self.global_variables = {}
        # Formal parameters - list of dict:
        # [{'name': str, 'direction': 'in'/'out', 'type': str}]
        self.fpar = []
        # return type (ASN.1)
        self.return_type = None
        # start, terminators, text areas, floating_labels (see Process)
        #self.start = None
        #self.states = []
        self.terminators = []
        #self.textAreas = []
        # Keep a list of labels and floating labels - useful for backends
        self.labels = []
        #self.floating_labels = []
        # Inherited procedures and operators
        self.procedures = []
        self.operators = []
        # inner procedures and operators (see Process for format)
        #self.inner_procedures = []
        self.inner_operators = []
        # mapping, transitions: see Process
        self.mapping = {}
        self.transitions = []
        # Determine if a procedure is externally defined
        self.external = False
        # Optional comment
        self.comment = None
        # Set of symbols contained in the procedure (type Automaton)
        self.content = Automaton(parent=self)


class Process(object):
    ''' SDL Process entry point '''
    def __init__(self):
        ''' Process AST default values '''
        self.processName = None
        # Optional filename containing this process (PR file)
        self.filename = None
        # Process parent context (Block or AST if defined at root level)
        self.parent = None
        # A process can be referenced (externally defined)
        self.referenced = False
        # variables: dictionnary: {variable1Name: (asn1SccType, default value)}
        self.variables = {}
        # global variables can be used to inherit variables
        self.global_variables = {}
        
        # Set default coordinates and width/height
        self.pos_x = self.pos_y = 150
        self.width = 150
        self.height = 75
        # Optional hyperlink
        self.hyperlink = None
        # Optional comment
        self.comment = None

        # dataview: complete AST of the ASN.1 types
        self.asn1Modules = None
        self.dataview = None

        # input and output signal lists:
        # [{'name': str, 'type': str, 'direction':'in'/'out'}]
        self.input_signals = []
        self.output_signals = []

        # terminators are useful for rendering backends
        self.terminators = []

        # Keep a list of labels and floating labels - useful for backends
        # List of Label
        self.labels = []

        # list of operators (not supported) and procedures
        self.operators = {}
        # list of Procedure (external procedures)
        self.procedures = []

        # The Mapping structure should be used for code generation backends
        # dictionnary: {'stateName': [class Input1, Input2,...], ...}
        # then Input contains the inputs list and corresponding transition
        self.mapping = {}

        # list of type Transition - use 'mapping' to map index to inputs/states
        self.transitions = []

        # list of type CompositeState
        self.composite_states = []

        # Set of symbols contained in the process (type Automaton)
        # (Includes inner procedures)
        self.content = Automaton(parent=self)

        # List of timers (strings) declared in the process
        self.timers = []


class CompositeState(Process):
    '''
        Composite states: the difference with Process is that they can have:
        - several START elements, that correspond to state entry points,
        - state exit points (with RETURN terminators)
        - entry and exit procedures
    '''
    def __init__(self):
        super(CompositeState, self).__init__()
        self.statename = ''
        self.state_entrypoints = []
        self.state_exitpoints = []
        # Special entry and exit procedures (named "entry" and "exit")
        self.entry_procedure = None
        self.exit_procedure = None
        # Body can contain text areas, procedures, composite states,
        # one nameless START, named START (one per entrypoint), states,
        # amd floating labels

    def __repr__(self):
        ''' Debug output for composite state '''
        return 'COMPOSITE STATE {exp} ({l},{c})'.format(exp=self.statename,
                l=self.line, c=self.charPositionInLine)


class Block(object):
    ''' AST for a BLOCK entity '''
    def __init__(self):
        '''
            Blocks can contain signal declarations, signalroutes,
            connections, inner block definitions, and process
            definitions.
        '''
        # Block name
        self.name = ''
        # Parent block or system
        self.parent = None
        # list of signal declarations - see class System for the structure
        self.signals = []
        # signalroutes: see self.channels in class System for the structure
        self.signalroutes = []
        # connections are between a channel and signalroute
        # [{'channel': str, 'signalroute': str}]
        self.connections = []
        # list of class Block
        self.blocks = []
        # list of class Process
        self.processes = []


class System(object):
    ''' AST for a SYSTEM entity '''
    def __init__(self):
        '''
            Create system default values
            contains blocks, procedures, channels and signal declarations
        '''
        # System name
        self.name = ''
        # Optional filename containing this system (PR file)
        self.filename = None
        # Reference to top-level AST
        self.ast = None
        # list of SIGNAL declarations: [{'name': str, 'type': str}]
        # (Supporting only one parameter)
        self.signals = []
        # list of ogAST.Procedure
        self.procedures = []
        # channels: [{'name':str, 'routes':[{'source': str, 'dest': str, 
        # 'signals': ['sig1', .. ]}]
        self.channels = []
        self.blocks = []


class AST(object):
    ''' Top-level AST entry point '''
    def __init__(self):
        '''
            AST entries are systems, processes, and USE clauses
            (cf. ANTLR grammar, production "pr_file")
        '''
        # Set of input files the AST was created from
        self.pr_files = set()
        # USE clauses: list of strings (eg. "DataView")
        self.use_clauses = []
        # Optional list of ASN.1 filenames (defined in CIF of USE clauses)
        self.asn1_filenames = []
        # Refs to the ASN.1 dataview AST (set with USE clauses)
        self.dataview = None
        self.asn1Modules = None
        # Constants stored in the ASN.1 modules (type is unknown/unchecked)
        self.asn1_constants = []

        # List of System
        self.systems = []
        # List of Process
        self.processes = []
