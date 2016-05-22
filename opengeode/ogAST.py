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

    Copyright (c) 2012-2015 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

import logging
from collections import defaultdict
LOG = logging.getLogger(__name__)


class Expression(object):
    ''' AST Entry for expressions - Always use subtype '''
    is_raw = False

    def __init__(self, inputString='', line=-1, charPositionInLine=-1):
        ''' Initialize Expression attributes '''
        self.inputString = inputString
        self.line = line
        self.charPositionInLine = charPositionInLine
        # Binary expressions have two sides
        self.right = self.left = None
        # Unary expressions are stored in "expr"
        self.expr = None

        # exprType is an ASN.1 type (as exported by asn1scc)
        self.exprType = None
        # Hint for code generators: intermediate storage identifier
        self.tmpVar = -1

    def trace(self):
        ''' Debug output for an expression '''
        return u'{exp} ({l},{c})'.format(exp=self.inputString,
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
    # Indicate that short circuit form is used ("or else")
    shortcircuit = ''


class ExprAnd(Expression):
    operand = 'and'
    # Indicate that short circuit form is used ("and then")
    shortcircuit = ''


class ExprXor(Expression):
    operand = 'xor'
    shortcircuit = ''


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
    operand = 'rem'


class ExprNot(Expression):
    operand = 'not'


class ExprNeg(Expression):
    operand = '-'

    @property
    def is_raw(self):
        ''' Redefine is_raw - check the actual element '''
        return self.expr.is_raw


class ExprAssign(Expression):
    operand = ':='


class ExprAppend(Expression):
    pass


class ExprIn(Expression):
    pass


class ExprImplies(Expression):
    pass


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
            self.value = primary.value
            self.exprType = primary.exprType
        else:
            self.inputString = inputString
            self.line = line
            self.charPositionInLine = charPositionInLine
            self.value = None
            self.exprType = None

    def trace(self):
        ''' Debug output for a primary '''
        return u'PRIMARY : {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class PrimCall(Primary):
    is_raw = False


class PrimIndex(Primary):
    is_raw = False


class PrimSubstring(Primary):
    is_raw = False


class PrimSelector(Primary):
    is_raw = False


class PrimVariable(Primary):
    is_raw = False


class PrimFPAR(PrimVariable):
    pass


class PrimEnumeratedValue(Primary):
    pass


class PrimInteger(Primary):
    pass


class PrimReal(Primary):
    pass


class PrimBoolean(Primary):
    pass


class PrimNull(Primary):
    pass

class PrimConstant(Primary):
    is_raw = False


class PrimStateReference(Primary):
    ''' This primary ("state" keyword) is used only in stop conditions and
    possibly in the future in observers, to reference the state of the system
    '''
    is_raw = False


class PrimBitStringLiteral(Primary):
    ''' Not supported yet '''
    pass


class PrimOctetStringLiteral(Primary):
    ''' Not supported yet '''
    pass


class PrimConditional(Primary):
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


class PrimEmptyString(Primary):
    pass


class PrimChoiceItem(Primary):
    ''' Value is a dict : {'choice': string, 'value': Expression} '''
    pass


class PrimChoiceDeterminant(Primary):
    pass


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
        self.pos_x, self.pos_y = None, None
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

    def trace(self):
        ''' Debug output for a decision '''
        return u'DECISION {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Answer(object):
    ''' AST Entry for a decision answer '''
    def __init__(self):
        ''' One ANSWER of a DECISION '''
        self.inputString = ''
        self.line = None
        self.charPositionInLine = None
        self.pos_x, self.pos_y = None, None
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

    def trace(self):
        ''' Debug output for an answer '''
        return u'ANSWER {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Task(object):
    ''' AST Entry for TASKS '''
    def __init__(self):
        ''' Initialize TASK attributes (set of ASSIGN statements) '''
        self.inputString = ''
        self.line = None
        self.charPositionInLine = None
        self.pos_x, self.pos_y = None, None
        self.width = 70
        self.height = 35
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        self.elems = []

    def trace(self):
        ''' Debug output for a task '''
        return u'TASK {exp} ({l},{c})'.format(exp=self.inputString,
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
        self.pos_x, self.pos_y = None, None
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

    def trace(self):
        ''' Debug output for an Output symbol '''
        return u'{exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class ProcedureCall(Output):
    ''' Procedure calls content is identical to Outputs '''
    pass


class Terminator(object):
    ''' Terminator elements (join, nextstate, stop, return) '''
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
        # Pointer to the next transition, when using return/connect
        self.next_trans = None
        # List of State that can lead to this terminator
        # There can be several if terminator follows a floating label
        # Note, this field is updated by the Helper.flatten function
        self.possible_states = []
        # optional composite state content (type CompositeState)
        self.composite = None
        # Flag to indicate if the nextstate is a state aggregation
        self.next_is_aggregation = False
        # List of sibling states if terminator is within a state aggregation
        # (list of strings with all parallel states of the aggregation)
        # Used by backend to synchronise parallel state terminations
        self.siblings = []
        # If this terminator is within a state aggregation, store the name
        # of the parallel substate (set by Helper.state_aggregations)
        self.substate = ''
        # candidate_id: {transition_id: [states]}
        # field is set by Helper.py/flatten, in case of "nextstate -"
        # there is a list of states that set transition_id to -1 : the standard
        # states ; and there are the composite states, that set a different
        # id corresponding to the start transition of the state.
        self.candidate_id = defaultdict(list)

    def trace(self):
        ''' Debug output for terminators '''
        return u'{kind} {exp} ({l},{c}) at {x}, {y}'.format(
                exp=self.inputString,
                kind=self.kind.upper(), l=self.line, c=self.charPositionInLine,
                x=self.pos_x, y=self.pos_y)


class Label(object):
    ''' AST Entry for a Label '''
    def __init__(self):
        ''' Initialize the label attributes '''
        # inputString holds the label name
        self.inputString = ''
        self.pos_x, self.pos_y = None, None
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

    def trace(self):
        ''' Debug output for a label '''
        return u'LABEL {label} ({l},{c})'.format(label=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Floating_label(Label):
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

    def trace(self):
        ''' Debug output for a label (used by code generator) '''
        return u'CONNECTION {label} ({l},{c})'.format(label=self.inputString,
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
        # List of states (string) that can lead to this transition
        # There can be several if state has multiple names (e.g. STATE a, b)
        # Note, this field is updated by the Helper.flatten function
        # and is needed to properly know when to call a nested state exit
        # procedure when the model is flattened.
        self.possible_states = []

    def trace(self):
        ''' Debug output: display all actions '''
        data = [action.trace() for action in self.actions]
        if self.terminator:
            data.append(self.terminator.trace())
        return u'\n'.join(data)


class Input(object):
    ''' AST Entry for the INPUT symbol '''
    def __init__(self):
        ''' Initialize the Input attributes '''
        # inputString is the user text, it can contain several inputs
        self.inputString = ''
        self.pos_x, self.pos_y = None, None
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

    def trace(self):
        ''' Debug output for an INPUT symbol '''
        return u'INPUT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Connect(Input):
    ''' AST Entry for the CONNECT part (transition below a nested state) '''
    def __init__(self):
        ''' Only one difference with INPUT: the connect_list attribute '''
        super(Connect, self).__init__()
        # List of strings
        self.connect_list = []
        self.width = 1

    def trace(self):
        ''' Debug output for a CONNECT symbol '''
        return u'CONNECT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)

class ContinuousSignal(Input):
    ''' AST Entry for the Continuous Signal '''
    def __init__(self):
        ''' Difference with Input: trigger is an expression '''
        super(ContinuousSignal, self).__init__()
        # Decision triggering the transition
        self.trigger = None
        # Priority (integer)
        self.priority = 0

    def trace(self):
        ''' Debug output for a Continuous signal '''
        return u'PROVIDED {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Start(object):
    ''' AST Entry for the START symbol '''
    def __init__(self):
        ''' Initialize the Start symbol attributes '''
        self.inputString = ''
        self.pos_x, self.pos_y = None, None
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

    def trace(self):
        ''' Debug output for a START symbol '''
        return u'START {}'.format(self.inputString)


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
        self.pos_x = None
        self.pos_y = None
        self.width = 70
        self.height = 35
        self.line = None
        self.charPositionInLine = None
        # optional hyperlink
        self.hyperlink = None

    def trace(self):
        ''' Debug output for a COMMENT symbol '''
        return u'COMMENT {exp} ({l},{c})'.format(
                exp=self.inputString,
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
        self.pos_x, self.pos_y = None, None
        self.pos_y = 0
        self.width = 70
        self.height = 35
        # list of type Input
        self.inputs = []
        # list of type Connect (connection below a nested state)
        self.connects = []
        # list of ContinuousSignal (provided clauses below a state)
        self.continuous_signals = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # optional composite state content (type CompositeState)
        self.composite = None

    def trace(self):
        ''' Debug output for a STATE symbol '''
        return u'STATE {exp} ({l},{c}) at {x},{y}'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine,
                x=self.pos_x, y=self.pos_y)


class TextArea(object):
    ''' AST Entry for text areas (containing declarations/comments) '''
    def __init__(self):
        ''' Text area (raw content for rendering only) '''
        self.inputString = '-- Text area for declarations and comments\n\n'
        self.line = None
        self.charPositionInLine = None
        # Set default coordinates and width/height
        self.pos_x, self.pos_y = None, None
        self.width = 170
        self.height = 140
        # DCL variables in the text area {name: (sort, default_value), ...}
        self.variables = {}
        # fpar and timers are also listed, useful when using autocompletion
        self.fpar = []
        self.timers = []
        # signals can be declared in a text area (structure: see System class)
        self.signals = []
        # USE construct can be declared in a text area (list of strings)
        # asn1_files lists optional COMMENT strings of USE constructs
        self.use_clauses = []
        self.asn1_files = []
        # inner procedures - useful to get autocompletion params
        self.procedures = []
        # optional hyperlink
        self.hyperlink = None

    def trace(self):
        ''' Debug output for a text area '''
        return u'TEXTAREA {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Automaton(object):
    ''' Elements contained in a process, procedure or composite state'''
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
        self.pos_x = self.pos_y = None
        self.width = 70
        self.height = 35
        # Optional hyperlink
        self.hyperlink = None
        # Local variables dictionnary (see Process)
        self.variables = {}
        self.timers = []
        # Inherited variables and timers from all levels above
        self.global_variables = {}
        self.global_timers = []
        # Formal parameters - list of dict:
        # [{'name': str, 'direction': 'in'/'out', 'type': str}]
        self.fpar = []
        # return type (ASN.1)
        self.return_type = None
        # when procedure has a RETURN it can also contain a variable name
        self.return_var = None
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
        # Determine if a procedure is a remote procedure
        self.exported = False
        # Optional comment
        self.comment = None
        # Set of symbols contained in the procedure (type Automaton)
        self.content = Automaton(parent=self)
        # input/output signal lists - unused but for context information
        self.input_signals = []
        self.output_signals = []


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
        # global variables and timers can be used to inherit from a level above
        self.global_variables = {}
        self.global_timers = []
        # Set default coordinates and width/height
        self.pos_x = 250
        self.pos_y = 150
        self.width = 150
        self.height = 75
        # Optional hyperlink
        self.hyperlink = None
        # Optional comment
        self.comment = None

        # dataview: complete AST of the ASN.1 types
        self.asn1Modules = None
        self.dataview = None
        # Reference to the Python module containing the ASN.1 AST
        self.DV = None

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
        # list of Procedure (external and inner procedures)
        self.procedures = []

        # The Mapping structure should be used for code generation backends
        # dictionnary: {'stateName': [class Input1, Input2,...], ...}
        # then Input contains the inputs list and corresponding transition
        self.mapping = {}

        # Similar mapping for continuous signals
        self.cs_mapping = defaultdict(list)

        # list of type Transition - use 'mapping' to map index to inputs/states
        self.transitions = []

        # list of type CompositeState
        self.composite_states = []

        # Set of symbols contained in the process (type Automaton)
        # (Includes inner procedures)
        self.content = Automaton(parent=self)

        # Process formal parameters - list of dict:
        # [{'name': str, 'type': str}]
        self.fpar = []

        # List of timers (strings) declared in the process
        self.timers = []

        # list of processes used for context management of the GUI
        self.processes = []


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

    def trace(self):
        ''' Debug output for composite state '''
        return u'COMPOSITE STATE {exp} ({l},{c})'.format(exp=self.statename,
                l=self.line, c=self.charPositionInLine)


class StateAggregation(CompositeState):
    '''
        State Aggregation (Parallel states) are supported since SDL2000
        These states can only contain (in the self.content field):
            text areas
            procedure definitions
            composite states (including sub-state aggregations)
        But no state machine definition
    '''
    def __init__(self):
        super(StateAggregation, self).__init__()
        # List of partition connections:
        # [{'outer': {'state_part_id': str, 'point': str},
        #   'inner': {'state_part_id': str, 'point': str}}]
        self.state_partition_connections = []

    def trace(self):
        ''' Debug output for state aggregation '''
        return u'STATE AGGREGATION {exp} ({l},{c})'.format(exp=self.statename,
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
        # list of ogAST.Procedure
        self.procedures = []
        # Block formal parameters - list of dict (unused)
        # [{'name': str, 'type': str}]
        self.fpar = []


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
        # list of SIGNAL declarations: [{'name': str, 'type': asn1type}]
        # (Supporting only one parameter)
        self.signals = []
        # list of ogAST.Procedure
        self.procedures = []
        # channels: [{'name':str, 'routes':[{'source': str, 'dest': str,
        # 'signals': ['sig1', .. ]}]
        self.channels = []
        self.blocks = []
        self.text_areas = []


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
        # ASN.1-defined constants (constants in Ada but variables in C)
        # dictionnary: {ConstantName: type } - copied from dataview.py
        self.asn1_constants = {}

        # List of System
        self.systems = []
        # List of Process
        self.processes = []
