# OpenGEODE Design documentation

## Introduction

This document describes some parts of the design of the tool, as well as
practical guidelines to implement new features.

The first chapter explains the steps to be followed in order to implement SDL
language features that are not yet supported by the tool and is based on a
concrete use case: adding support for *Continuous signals*.

The source of this document is in the *Markdown* format and other formats are
generated using the *pandoc* tool. Please take it in consideration when
updating the text.

## Guideline for extending OpenGEODE with Continuous Signals

Continuous signals are part of the SDL language and their semantics
and syntax is formally specified in the Z100 standard.

This chapter explains how concretely to add support for this construct to the
tool. It covers:

* Extending the ANTLR grammar
* Updating the parser and the AST (metamodel), including syntax/semantic checks
* Creating a new graphical symbol and updating the renderer and the menus
* Updating the backend to parse the graphical model and save PR files
* Updating other backends such as the Statechart renderer and code generators
* Updating the clipboard functionality

This is explained step by step in an order which allows to understand the logic
easily.

### Add the new grammar to sdl92.g

The file `sdl92.g` contains the ANTLR3 grammar of the SDL language.
Please refer to the ANTLR documentation if needed.

We add the following production:

    continuous_signal
            :       cif?
                    hyperlink?
                    PROVIDED expression e=end
                    (PRIORITY p=INT end)?
                    transition?
            ->      ^(PROVIDED expression cif? hyperlink? $p? $e? transition?)
            ;


When a new token is needed (here: *PROVIDED*) it must be added at several
places in the ANTLR grammar:

* in the "symbolname" production (for the CIF part)
* as a new keyword (`PROVIDED : P R O V I D E D`)
* in the list of tokens (tokens { ... })


__Notes:__

* *cif* and *hyperlink* are optional
* the *transition* is also optional, to allow partial model saving
* the expression is always the first child, since it does not have a
dedicated token, and is the only mandatory field
* *end* corresponds to the *COMMENT* part in SDL


Then the new production is added as a child option to the (existing) *state*:

    state_part
            :       input_part
                    | save_part
                    | spontaneous_transition
                    | continuous_signal       // <==== HERE
                    | connect_part
            ;

### Prepare the parser in ogParser.py

Find the parent rule (*state* here) and add a branch to parse the new child.
Usually the rule is a function named after the production name. So look for
`def state (...)`


    def state(root, parent, context):
        '''
            Parse a STATE.
            "parent" is used to compute absolute coordinates
            "context" is the AST used to store global data (process/procedure)
        '''


Each rule parses all its children based on the token name from ANTLR. It is
therefore straightforward to add the parsing of a new child:


    for child in root.getChildren():
        if child.type == lexer.CIF:
        ....
        # you must add a new branch based on your token name:
        elif child.type == lexer.PROVIDED:
            # Add a placeholder for your code here
            sterr.append('I am adding support for Continuous Signals now!')


If the new rule has children, you will likely want to add a new function to
parse it following the same scheme as the parent rule (add a function called
`continuous_signal` which returns the full content of the grammar).

We keep this as a placeholder for the time being because we must first define
if/what new entries are needed in the AST (`ogAST.py`).

__Note:__

In SDL there are family of features and very often, new features are similar
to existing ones so you will find a model to know how to easily code your new
function. In the case of the continuous signals, they are very similar to
`INPUT` and `CONNECT` - they are triggers for a transition below a state.


### Add new entries to the AST in ogAST.py

Find the relevant places and add new entries if needed. Here we look for the
State entry and we add a list of *continuous signals*.

Depending on the complexity of the new feature, we can create a new class for
the entry, or use a simple type/dictionary.

The general rule is that if we are adding a new symbol (with coordinates,
comments, hyperlink, ...) it is better to create a new class to handle it.
It is the case here.

So first in the State class:

    class State(object):
        ''' AST Entry for STATE symbols '''
        def __init__(self, defName=''):
            # (...) Add the following lines:
            # list of ContinuousSignal (provided clauses below a state)
            self.continuous_signals = []


Then create the new class, using the same structure as another class of a
feature of the same family - here, we inherit from Input. The class is very
simple:


    class ContinuousSignal(Input):
        ''' AST Entry for the Continuous Signal '''
        def __init__(self):
            ''' Difference with Input: trigger is an expression '''
            super(ContinuousSignal, self).__init__()
            # Expression triggering the transition
            self.trigger = None
            # Priority (integer)
            self.priority = 0

        def trace(self):
            ''' Debug output for a Continuous signal '''
            return u'PROVIDED {exp} ({l},{c})'.format(exp=self.inputString,
                    l=self.line, c=self.charPositionInLine)


We are done with the AST, we can close `ogAST.py`.


### Back to `ogParser.py`


Now we can parse the construct and create the AST entries we just defined.
In the state() function, we replace the placeholder we added at step 2:

    (...)
    elif child.type == lexer.PROVIDED:
        # Continuous signal
        provided_part, err, warn = continuous_signal(child, state_def, context)
        state_def.continuous_signals.append(provided_part)
        (...)


Then we can implement the continuous_signal function.

    def continuous_signal(root, parent, context):
        ''' Parse a PROVIDED clause in a continuous signal '''
        i = ogAST.ContinuousSignal()
        (...)
        return i, errors, warnings


At this point we are done with the parser, which is now capable of filling
an AST containing the new construct.

There are still a number of updates to perform to complete the support of the
new feature:

* Update the on-the-fly parser for syntax checks in the graphical editor (`ogParser.py`)
* Create a graphical symbol for the new feature (in `sdlSymbols.py`)
* Update the renderer to draw the symbol (`Renderer.py`)
* Update the backend that saves the model to phrase representation (`Pr.py`)
* Create an icon and add the new symbol to the palette
* Update the statechart renderer (`Statechart.py`)
* Update other backends that can be impacted, such as code generators (`AdaGenerator.py`, etc.)
* Update clipboard


### Syntax checker in `ogParser.py`

When a graphical symbol is edited, a call to `ogParser.parseSingleElement`
is made to check that there are no syntax errors.

There is an assertion at the beginning of this function to prevent trying to
parse unsupported construct and raise a exception which would be more
difficult to debug.

We need to add our new "continuous_signal" symbol here:


    assert(elem in ('input_part', 'output', 'decision', 'alternative_part',
            'terminator_statement', 'label', 'task', 'procedure_call', 'end',
            'text_area', 'state', 'start', 'procedure', 'floating_label',
            'connect_part', 'process_definition', 'proc_start', 'state_start',
            'signalroute', 'stop_if', 'continuous_signal'))


### Create a new symbol in `sdlSymbols.py`


sdlSymbols.py module contains the SDL-specific symbol ; they all inherit from
a higher level symbol class, which provides the standard behaviour of the
symbol, e.g. when it is moved, etc.

The symbol-specific class must contain the following information:

* the name of the symbol as understood by the syntax checker
* the shape of the symbol
* the behaviour of the autocompletion feature
* the list of symbols that can be connected to this symbol
* and possibly tuning of some paramters

At the top-part of the module, the new class needs to be added to the \_\_all\_\_
global:

    __all__ = ['Input', 'Output', 'State', 'Task', 'ProcedureCall', 'Label',
               'Decision', 'DecisionAnswer', 'Join', 'Start', 'TextSymbol',
               'Procedure', 'ProcedureStart', 'ProcedureStop', 'ASN1Viewer',
               'StateStart', 'Process', 'ContinuousSignal']


Then the class is defined... extract:


    # pylint: disable=R0904
    class ContinuousSignal(HorizontalSymbol):
        ''' " Provided" part below a state - not a enabling condition '''
        common_name = 'continuous_signal' # <==== Same name as in ogParser.py

        def set_shape(self, width, height):
            ''' Define the shape '''
            path = QPainterPath()
            path.moveTo(15, 0)
            path.lineTo(0, height / 2.0)
            path.lineTo(15, height)
            path.moveTo(width - 15, 0)
            path.lineTo(width, height / 2.0)
            path.lineTo(width - 15, height)
            self.setPath(path)
            super(ContinuousSignal, self).set_shape(width, height)


And you may need to add your new symbol to the properties of other symbols.
For example _insertable_followers gives the list of signals that the tool will
allow you to place after (or next to) the currently selected symbol.

The "state" symbol has this property:

    _insertable_followers = ['Input', 'Connect', 'ContinuousSignal']


### Update the renderer to see some first result: `Renderer.py`


Since the parser is ready and the symbol is defined, it is now possible to
update the graphical renderer and see if the symbol is properly displayed.

The renderer is a backend that uses a visitor design pattern (using the python
*singledispatch* mechanism). It makes it easy to extend.

Rendering means taking an ogAST class and creating an sdlSymbols class.
There is a single `render` function that is dispatched depending on the class
name. You have to provide a function (name does not matter) and register it
using a singledispatch decorator:


    @render.register(ogAST.ContinuousSignal)
    def _continuous_signal(ast, scene, parent, states):
        ''' Add continuous signal to the scene '''
        cont = sdlSymbols.ContinuousSignal(parent, ast=ast)
        if cont not in scene.items():
            add_to_scene(cont, scene)
        if not parent:
            cont.pos_x, cont.pos_y = ast.pos_x, ast.pos_y
        if ast.transition:
            render(ast.transition,
                   scene=scene,
                   parent=cont,
                   states=states)
        return cont


And then you must call the render function from the State and Terminator
renderers, since the continuous signals are generated below states,
just like Inputs:

    @render.register(ogAST.State)
    def _state(ast, scene, states, terminators, parent=None):
        (...)
        for exit in chain(ast.inputs, ast.connects, ast.continuous_signals):
            render(exit, scene=scene, parent=new_state, states=states)
        (...)


### Update the graphical parser backend (Pr.py)


In order to save the model or make syntax checks, we need to make sure that
the graphical model parser recognises the new symbol.
The principle is the same as for the renderer - a singledispatch visitor
pattern, but on the graphical symbols instead of the AST.
It is therefore straightforward to parse - just add a new function that
mimicks an existing one and register it to singledispatch.


    @generate.register(sdlSymbols.ContinuousSignal)
    def _continuous_signal(symbol, recursive=True, **kwargs):
        ''' "Provided" symbol or branch if recursive is set '''
        result = common('PROVIDED', symbol)
        if recursive:
            result.extend(recursive_aligned(symbol))
        return result


As before, also make sure that the parent symbol (here: state) can recursively
parse the new child.


### Create an icon for the palette

To be able to use the new symbol in the graphical editor you need to create
an icon that will be displayed in the palette of the GUI.
The icons are specified in SVG format (in the `icons/` directory) using
the *inkscape* tool and must be exporte to PNG.

The filename must be the same as the class name of your symbol, but with
lowercases.

Our class is named `ContinuousSignal` so we will create `continuoussignal.png`.

The following properties apply when exporting to PNG:

* width 46
* height 35
* 90 DPI

Add the resulting filename inside the Qt resource file: `opengeode.qrc`. This
file lists all files that are "embedded" in the application. This was done to
avoid external files, making the distribution of the tools easier to handle.

    <!DOCTYPE RCC><RCC version="1.0">
     <qresource>
         <file>icons/comment.png</file>
         <file>icons/decision.png</file>
         <file>icons/decisionanswer.png</file>
         <file>icons/input.png</file>
         ... add the new file here (`continuoussignal.png`)


To compile this resource file to get a Python file, run:

    make compile-all

You then need to specify in which palette(s) this new icon is available.
This is done in `opengeode.py`.

First add the new symbol (*ContinuousSignal*) to the list of imports:

    from sdlSymbols import(Input, Output, Decision, DecisionAnswer, Task,
            ProcedureCall, TextSymbol, State, Start, Join, Label, Procedure,
            ProcedureStart, ProcedureStop, StateStart, Connect, Process,
            ContinuousSignal)

Then edit the `ACTION` look-up table to specify which scenes can use the
symbol. In our case, the process, state and clipboard scenes. You can decide
at which place it will appear graphically - it respects the ordering of the
list.

### Update the Statechart backend

Very few symbol changes imply a modification of the statechart renderer. It is
the case of the `continuous signals` because, like `inputs`, they can trigger
transitions.

The `Statechart.py` file is containing the code that creates a graphviz
translation of the SDL model to render a statechart.

The function that needs to be updated is `create_dot_graph`. It takes a SDL
model (instance of AST) and generates a number of graphviz models, one for each
level of hierarchy if the SDL model contains state composition or aggregations.

What needs to be extended is the list of edges between the states.

It is easy here, we have to extend the creation of edges from:

    for state, inputs in root_ast.mapping.viewitems():
        # ... create edges triggered by inputs below states

to:

    for state, inputs in chain(root_ast.mapping.viewitems(),
                               root_ast.cs_mapping.viewitems()):
        # chain the input iterator with continuous signals

### Update the code generator backends

All backends use a Visitor design pattern (with Python's *singledispatch*
mechanism).

Updating backends with custom code generation features is therefore
straightforward. You need to find the parent function of your construct,
and create a new visitor function to generate the code corresponding you need
(or directly embed, depending on the complexity of the pattern).

The Ada code generator contains documentation and details on how to proceed
with updates. See `AdaGenerator.py` file.
