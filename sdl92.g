/*
    OpenGEODE
    ANTLR 3.1.3 grammar for the SDL92 langage
    Includes the following features from SDL2000+:
    - FOR loops in TASKs
    - Composite states (nested and aggregation/parallel states)

    author: Maxime Perrotin
    with contributions from Diego Barbera, Laurent Meyer
*/

grammar sdl92;

options {
    language=Python3;
    output=AST;
    ASTLabelType=CommonTree;
    backtrack=true;
}

tokens {
        ACTION;
        ALL;
        ALTERNATIVE;
        ANSWER;
        ARRAY;
        ASN1;
        ASSIGN;
        BITSTR;
        BLOCK;
        CHANNEL;
        CHOICE;
        CIF;
        CLOSED_RANGE;
        COMMENT;
        COMPOSITE_STATE;
        CONDITIONAL;
        CONNECT;
        CONNECTION;
        CONSTANT;
        CONSTANTS;
        DCL;
        MONITOR;
        DECISION;
        DIGITS;
        ELSE;
        EMPTYSTR;
        ENDNEWTYPE;
        ENDSYNTYPE;
        ENDTEXT;
        ENTRY_POINT;
        EXPORT;
        EXPRESSION;
        EXTERNAL;
        FI;
        FIELD;
        FIELD_NAME;
        FIELDS;
        FLOAT2;
        FLOAT;
        FLOATING_LABEL;
        FOR;
        FPAR;
        GROUND;
        HISTORY_NEXTSTATE;
        HYPERLINK;
        IF;
        IFTHENELSE;
        IN;
        INFORMAL_TEXT;
        INOUT;
        INPUT;
        INPUT_NONE;
        INPUTLIST;
        JOIN;
        LABEL;
        LITERAL;
        NEG;
        NEWTYPE;
        NEXTSTATE;
        NUMBER_OF_INSTANCES;
        OCTSTR;
        OPEN_RANGE;
        OUTPUT;
        OUTPUT_BODY;
        PARAM;
        IOPARAM;
        PARAMNAMES;
        PARAMS;
        PAREN;
        PFPAR;
        POINT;
        PRIMARY;
        PROCEDURE;
        PROCEDURE_CALL;
        PROCEDURE_NAME;
        PROCESS;
        PROVIDED;
        QUESTION;
        RANGE;
        RENAMES;
        INTERCEPT;
        //RESET;
        RETURN;
        RETURNS;
        ROUTE;
        SAVE;
        SELECTOR;
        SEQOF;
        SEQUENCE;
        //SET;
        SIGNAL;
        SIGNAL_LIST;
        SORT;
        STATE;
        STATE_AGGREGATION;
        STATE_PARTITION_CONNECTION;
        STATELIST;
        STIMULUS;
        STOP;
        STOPIF;
        STRING;
        STRUCT;
        SYNONYM;
        SYNONYM_LIST;
        SYNTYPE;
        SYMBOLID;
        SYSTEM;
        TASK;
        TASK_BODY;
        TERMINATOR;
        TEXT;
        TEXTAREA;
        TEXTAREA_CONTENT;
        THEN;
        TIMER;
        TO;
        TRANSITION;
        TYPE_INSTANCE;
        UNHANDLED;
        USE;
        VALUE;
        VARIABLE;
        VARIABLES;
        VIA;
        VIAPATH;
        INPUT_EXPRESSION;
        OUTPUT_EXPRESSION;
        ALWAYS;
        NEVER;
        EVENTUALLY;
        FILTER_OUT;
        N7S_SCL;
}


/*
    Top level: any .pr file
*/
pr_file
        :       (use_clause
                | system_definition
                | process_definition)+
        ;


system_definition
        :       SYSTEM system_name end
                entity_in_system*
                ENDSYSTEM system_name? end
        ->      ^(SYSTEM system_name entity_in_system*)
        ;


use_clause
        :       use_asn1?
                USE package_name
                ('/' def_selection_list )?
                end
        ->      ^(USE use_asn1? end? package_name def_selection_list?)
        ;


/*
    In USE clause: USE package/X, Y, Z;
*/
def_selection_list
        :       ID (','! ID)*
        ;


/* Entity in system:
   Declare signals, external procedures, connections and blocks
*/
entity_in_system
        :       signal_declaration
                | text_area
                | procedure
                | channel
                | block_definition
        ;

/* signal_declaration:
   e.g. SIGNAL open_door(typeA, typeB);
*/
signal_declaration
        :       paramnames?
                SIGNAL signal_id input_params?
                (RENAMES (input_expression | output_expression))? // for observers
                end
        ->      ^(SIGNAL paramnames? signal_id input_params? ^(INTERCEPT input_expression? output_expression?))
        ;


channel
        :       CHANNEL channel_id
                route+
                ENDCHANNEL end
        ->      ^(CHANNEL channel_id route+)
        ;


route
        :       FROM source_id TO dest_id WITH signal_id (',' signal_id)* end
        ->      ^(ROUTE source_id dest_id signal_id+)
        ;


block_definition
        :       BLOCK block_id end
                entity_in_block*
                ENDBLOCK end
        ->      ^(BLOCK block_id entity_in_block*)
        ;


/* Inside a SDL block:
   there can be nested blocks, processes, signalroutes and connections
   to above channels
*/
entity_in_block
        :       signal_declaration
                | signalroute
                | connection
                | block_definition
                | process_definition
        ;

// There should be at least one route in the signal route
// However it is now optional (* and not +) to appease the
// syntax checker in the tool.
signalroute
        :       SIGNALROUTE route_id end?
                route*
        ->      ^(SIGNALROUTE route_id route*)
        ;


connection
        :       CONNECT channel_id AND route_id end
        ->      ^(CONNECTION channel_id route_id)
        ;


/* process_definition
   Covers various cases such as:
   PROCESS name REFERENCED;
   PROCESS name;
      <body>
   ENDPROCESS <name>;
   Etc. The grammar is tolerant, semantic checks are done in the code.
*/
process_definition
        :       cif?
                symbolid?
                PROCESS t=TYPE? process_id
                number_of_instances? (':' type_inst)? REFERENCED? a=end
                pfpar?
                (text_area | procedure | (composite_state_preamble) =>composite_state)*
                processBody? ENDPROCESS? TYPE? process_id?
                end?
        ->      ^(PROCESS cif? symbolid? process_id number_of_instances? type_inst?
                $t? REFERENCED? $a? pfpar? text_area* procedure*
                composite_state* processBody?)
        ;


// Process formal parameters
pfpar
        :       FPAR parameters_of_sort
                (',' parameters_of_sort)*
                end?
        ->      ^(PFPAR parameters_of_sort+)
        ;


parameters_of_sort
        :       variable_id (',' variable_id)* sort
        ->      ^(PARAM variable_id+ sort)
        ;


// procedure
// 2021-03 Added EXPORTED and REFEERENCED keywords
// needed to declare a synchronous provided interface at system level
procedure
        :       cif?
                symbolid?
                EXPORTED? PROCEDURE procedure_id (e1=end | SEMI)
                fpar?
                res=procedure_result?
                (text_area | procedure)*
                ((processBody? ENDPROCEDURE procedure_id?)
                 | EXTERNAL | REFERENCED)
                e2=end
        ->      ^(PROCEDURE cif? symbolid? procedure_id $e1? $e2? fpar? $res?
                text_area* procedure* processBody? EXTERNAL? EXPORTED? REFERENCED?)
        ;

// Procedure result / optional return type
procedure_result
        :       ('->' | RETURNS)
                variable_id?
                sort end?
        ->      ^(RETURNS variable_id? sort)
        ;

// Procedure formal parameters
fpar
        :       FPAR formal_variable_param
                (',' formal_variable_param)*
                end
        ->      ^(FPAR formal_variable_param+)
        ;


formal_variable_param
        :       (INOUT | IN | OUT)?
                variable_id (',' variable_id)* sort
        ->      ^(PARAM INOUT? IN? OUT? variable_id+ sort)
        ;


// text_area: TODO add operator description in content
text_area
        :       cif
                symbolid?
                content?
                cif_end_text
        ->      ^(TEXTAREA cif symbolid? content? cif_end_text)
        ;


// Text areas can contain textual procedures, FPAR declarations,
// and variable or timer declarations
content
        :        (procedure
                 | use_clause
                 | signal_declaration
                 | fpar
                 | res=procedure_result
                 | timer_declaration
                 | syntype_definition
                 | newtype_definition
                 | variable_definition
                 | monitor_definition
                 | observer_special_states_declaration
                 | synonym_definition)*
        ->       ^(TEXTAREA_CONTENT fpar* $res? procedure* variable_definition*
                   monitor_definition* syntype_definition* newtype_definition*
                   timer_declaration* signal_declaration* use_clause*
                   observer_special_states_declaration* synonym_definition*)
        ;

// Observers for model checking can have states that are flagged as
// error, ignore or success states. They are declared like this:
// errorstates stateA, stateB;
// ignorestates stateC;
// successstates stateD, stateE;
observer_special_states_declaration
        :       ERRORSTATES      statename (',' statename)* end
        ->      ^(ERRORSTATES statename+)
                | IGNORESTATES   statename (',' statename)* end
        ->      ^(IGNORESTATES statename+)
                | SUCCESSSTATES  statename (',' statename)* end
        ->      ^(SUCCESSSTATES statename+)
        ;


timer_declaration
        :       TIMER timer_id
                (',' timer_id)*
                end
        ->      ^(TIMER timer_id+)
        ;


syntype_definition
        :       SYNTYPE syntype_name '=' parent_sort
                (CONSTANTS (range_condition (',' range_condition)* ))?
                ENDSYNTYPE syntype_name? end
        ->      ^(SYNTYPE syntype_name parent_sort range_condition*)
        ;


syntype_name
        :       sort
        ;


parent_sort
        :       sort
        ;


newtype_definition
        :       NEWTYPE type_name (array_definition|structure_definition)?
                ENDNEWTYPE type_name? end
        ->      ^(NEWTYPE type_name array_definition* structure_definition*)
        ;


type_name
        :       sort
        ;


array_definition
        :       ARRAY '(' sort ',' sort ')'
        ->      ^(ARRAY sort sort)
        ;


structure_definition
        :       STRUCT field_list end
        ->      ^(STRUCT field_list)
        ;


field_list
        :       field_definition (end field_definition)*
        ->      ^(FIELDS field_definition+)
        ;


field_definition
        :       field_name (',' field_name)* sort
        ->      ^(FIELD field_name+ sort)
        ;


/* variable definition has one extension to SDL: it is possible to specify
   an alias to a data structure element:
   dcl variable type renames foo.bar.baz */
variable_definition
        :       DCL variables_of_sort
                (',' variables_of_sort)*
                end
        ->      ^(DCL variables_of_sort+)
        ;

/* Monitors are an extension used when creating observers for model checking */
monitor_definition
        :       MONITOR variables_of_sort
                (',' variables_of_sort)*
                end
        ->      ^(MONITOR variables_of_sort+)
        ;

/* synonyms in SDL allow to declare constants */
synonym_definition
        :       internal_synonym_definition
        ;


internal_synonym_definition
        :       SYNONYM synonym_definition_item (',' synonym_definition_item)*
                end
        ->      ^(SYNONYM_LIST synonym_definition_item+)
        ;


synonym_definition_item
        :       variable_id sort '=' (ground_expression | EXTERNAL)
        ->      ^(SYNONYM variable_id sort ground_expression? EXTERNAL?)
        ;


variables_of_sort
        :       variable_id (',' variable_id)* sort
                ((':=' ground_expression) | (RENAMES variable))?
        ->      ^(VARIABLES variable_id+ sort
                  ground_expression? ^(RENAMES variable)?)
        ;


ground_expression
        :       expression
        ->      ^(GROUND expression)
        ;


number_of_instances
        :       '(' initial_number=INT ',' maximum_number=INT ')'
        ->      ^(NUMBER_OF_INSTANCES $initial_number $maximum_number)
        ;


processBody
        :       start? (state | floating_label)*
        ;


start
        :       cif?
                symbolid?
                hyperlink?
                START name=state_entry_point_name? end
                transition?
        ->      ^(START cif? hyperlink? symbolid? $name? end? transition?)
        ;


floating_label
        :       cif?
                symbolid?
                hyperlink?
                CONNECTION connector_name ':'
                transition?
                cif_end_label?
                ENDCONNECTION SEMI
        ->      ^(FLOATING_LABEL cif? hyperlink? symbolid? connector_name transition?)
        ;

// state is either a full state definition, or a state instance
state
        : state_definition
          | state_instance
        ;

// the "via" part is needed to allow the graphical merge with a nextstate
state_definition
        :       cif?
                symbolid?
                hyperlink?
                STATE statelist via? (e=end | SEMI)
                (state_part)*
                ENDSTATE statename? f=end
        ->      ^(STATE cif? hyperlink? symbolid? $e? statelist via? state_part*)
        ;


state_instance
        :       cif?
                symbolid?
                hyperlink?
                STATE statename ':' type_inst via? (e=end | SEMI)
                (state_part)*
                ENDSTATE statename? f=end
        ->      ^(STATE cif? hyperlink? symbolid? $e? statename via? type_inst state_part*)
        ;


statelist
        :       ((statename)(',' statename)*)
        ->      ^(STATELIST statename+)
                | ASTERISK exception_state?
        ->      ^(ASTERISK exception_state?)
        ;


exception_state
        :       '(' statename (',' statename)* ')'
        ->      statename+
        ;


// 11.11 State Machine and Composite State (SDL2000)
composite_state
        :       composite_state_graph
                | state_aggregation
        ;

// used for syntactic predicate
composite_state_preamble
        :       STATE AGGREGATION? statename end
                SUBSTRUCTURE
        ;

composite_state_graph
        :       STATE statename e=end
                SUBSTRUCTURE
                connection_points*
                body=composite_state_body
                ENDSUBSTRUCTURE statename? f=end
        ->      ^(COMPOSITE_STATE statename connection_points* $body $e?)
        ;


// 11.11.2 State Aggregation (SDL2000)
state_aggregation
        :       STATE AGGREGATION statename e=end
                SUBSTRUCTURE
                connection_points*
                entities=entity_in_composite_state*
                body=state_aggregation_body
                ENDSUBSTRUCTURE statename? f=end
        ->      ^(STATE_AGGREGATION statename connection_points*
                                    $entities* $body $e?)
        ;


// 11.11.2 State Aggregation (SDL2000)
entity_in_composite_state
        :       (text_area | procedure)
        ;


// 11.11.2 State Aggregation (SDL2000)
state_aggregation_body
        :       (state_partitioning | state_partition_connection)*
                state*
        ;


// 11.11.2 State Aggregation (SDL2000)
state_partitioning
        :       composite_state
        ;


// 11.11.2 State Aggregation (SDL2000)
state_partition_connection
        :       CONNECT outer=entry_point AND inner=entry_point end
        ->      ^(STATE_PARTITION_CONNECTION $outer $inner end?)
        ;


// 11.11.2 State Aggregation (SDL2000)
entry_point
        :       state_part_id=ID VIA point
        ->      ^(ENTRY_POINT $state_part_id point)
        ;


// 11.11.2 State Aggregation (SDL2000)
point
        :       (state_point=ID | DEFAULT)
        ->      ^(POINT $state_point? DEFAULT?)
        ;


// 11.11.1 and 11.11.2 Composite State (SDL2000)
connection_points
        :       IN state_entry_exit_points end
        ->      ^(IN state_entry_exit_points end?)
                | OUT state_entry_exit_points end
        ->      ^(OUT state_entry_exit_points end?)
        ;


// 11.11.1 and 11.11.2 Composite State (SDL2000)
state_entry_exit_points
        :       '(' statename (',' statename)* ')'
        ->      statename+
        ;


// 11.11.1 Composite State graph content (SDL2000)
// Use a syntactic predicate to disambiguate the parsing of the composite
// state vs a normal state, in the case of a syntax error in the composite.
composite_state_body
        :  (text_area
            | procedure
            | (composite_state_preamble) =>composite_state)*
           start* (state | floating_label)*
           EOF?
        ;


state_part
        :       input_part
                //| priority_input        // Not supported
                | save_part               // Not supported in openGEODE
                | spontaneous_transition
                | continuous_signal
                | connect_part
        ;


// connect part is used to connect nested state exit points to a transition
connect_part
        :       cif?
                symbolid?
                hyperlink?
                CONNECT connect_list? end
                transition?
        ->      ^(CONNECT cif? hyperlink? symbolid? connect_list? end? transition?)
        ;


connect_list
        :       state_exit_point_name (',' state_exit_point_name)*
                -> state_exit_point_name+
                | ASTERISK
        ;


spontaneous_transition
        :       cif?
                symbolid?
                hyperlink?
                INPUT NONE end
                enabling_condition?
                transition
        ->      ^(INPUT_NONE cif? hyperlink? symbolid? transition)
        ;


enabling_condition
        :       PROVIDED expression end
        ->      ^(PROVIDED expression)
        ;


continuous_signal
        :       cif?
                symbolid?
                hyperlink?
                PROVIDED expression e=end
                (PRIORITY p=INT end)?
                transition?
        ->      ^(PROVIDED expression cif? hyperlink? symbolid? $p? $e? transition?)
        ;


save_part
        :       SAVE save_list
                end
        ->      ^(SAVE save_list)
        ;


save_list
        :       signal_list
                | asterisk_save_list
        ;


asterisk_save_list
        :       ASTERISK;


signal_list
        :       signal_item (',' signal_item)*
        ->      ^(SIGNAL_LIST signal_item+)
        ;



// Signal_item alternatives are all of the same ID type.
// Should be resolved at semantic analysis.
signal_item
        :       signal_id; /* |
                priority_signal_id |
                signal_list_id |
                timer_id;*/

/*   Not considered for the moment
     (irrelevant in the scope of the generation of code for a single process)
priority_input
        :       PRIORITY INPUT priority_input_list end transition;


priority_input_list
        :       priority_stimulus (',' priority_stimulus)*;

priority_stimulus
        :       priority_signal_id ( '(' variable_id (',' variable_id)* ')');
*/


// this is only the "basic input part" from SDL92
input_part
        :       cif?
                symbolid?
                hyperlink?
                INPUT inputlist end
                enabling_condition?
                transition?
        ->      ^(INPUT cif? hyperlink? symbolid? end?
                inputlist enabling_condition? transition?)
        ;


// asterisk means: all signals not excplicitely specified
// (semantic is different from asterisk state)
inputlist
        :       ASTERISK
                | (stimulus (',' stimulus)*)
        ->      ^(INPUTLIST stimulus+)
        ;


stimulus
        :       stimulus_id input_params?
        ;


input_params
        :       L_PAREN variable_id (',' variable_id)* R_PAREN
        ->      ^(PARAMS variable_id+)
        ;


transition
        :       action+ label? terminator_statement?
        ->      ^(TRANSITION action+ label? terminator_statement?)
                | terminator_statement
        ->      ^(TRANSITION terminator_statement)
        ;


action
        :       label?
                (task
                | task_body
                | output
                | create_request
                | decision
                | transition_option
                //| set_timer
                //| reset_timer
                | export     // Not supported in OpenGEODE
                | procedure_call)
        ;


export
        :       EXPORT
                L_PAREN variable_id (COMMA variable_id)* R_PAREN
                end
        ->      ^(EXPORT variable_id+)
        ;


/*
remote_procedure_call
        :       CALL remote_procedure_call_body;

remote_procedure_call_body
        :       remote_procedure_id actual_parameters? (TO destination)?;
*/
procedure_call
        :       cif?
                symbolid?
                hyperlink?
                CALL procedure_call_body end
        ->      ^(PROCEDURE_CALL cif? hyperlink? symbolid? end? procedure_call_body)
        ;


procedure_call_body
        :       procedure_id actual_parameters?
        ->      ^(OUTPUT_BODY procedure_id actual_parameters?)
        ;


/* Commented out because OG does not support the SET/RESET symbols
   but dedicated procedures (set_timer/reset_timer)
   This allows to "free" the reserved keywords "set" and "reset"
   for other purposes such as message or variable names
set_timer
        :       SET set_statement (COMMA set_statement)*
                end
        ->      set_statement+
        ;


set_statement
        :       L_PAREN (expression COMMA)? timer_id R_PAREN
        ->      ^(SET expression? timer_id)
        ;
        // ('('expression_list')')? ')'; (removed because of non-LL(*) problem)

reset_timer
        :       RESET reset_statement (',' reset_statement)*
                end
        ->      reset_statement+
        ;


reset_statement
        :       timer_id ('(' expression_list ')')?
        ->      ^(RESET timer_id expression_list?)
        ;
*/

transition_option
        :       ALTERNATIVE alternative_question e=end
                answer_part
                alternative_part
                ENDALTERNATIVE f=end
        ->      ^(ALTERNATIVE answer_part alternative_part)
        ;


alternative_part
        :       (answer_part+ else_part?)
        ->      answer_part+ else_part?
                | else_part
        ->      else_part
        ;


alternative_question
        :       expression
                | informal_text
        ;


decision
        :       cif?
                symbolid?
                hyperlink?
                DECISION question e=end
                answer_part?
                alternative_part?
                ENDDECISION f=end
        ->      ^(DECISION cif? hyperlink? symbolid? $e? question
                answer_part? alternative_part?)
        ;


answer_part
        :       cif?
                symbolid?
                hyperlink?
                L_PAREN answer R_PAREN ':' transition?
        ->      ^(ANSWER cif? hyperlink? symbolid? answer transition?)
        ;


answer
        :       range_condition
                | informal_text
        ;


else_part
        :       cif?
                symbolid?
                hyperlink?
                ELSE ':' transition?
        ->      ^(ELSE cif? hyperlink? symbolid? transition?)
        ;


question
        :       informal_text
                | expression
        ->      ^(QUESTION expression)
                | ANY
        ->      ^(ANY)
        ;


range_condition
        :       (closed_range | open_range)
                (','! (closed_range|open_range))*
        ;


closed_range
        :       a=expression ':' b=expression
        ->      ^(CLOSED_RANGE $a $b)
        ;


open_range
        :       constant
        ->      constant
                | ( (EQ|NEQ|GT|LT|LE|GE) constant)
        ->      ^(OPEN_RANGE EQ? NEQ? GT? LT? LE? GE? constant)
        ;


constant
        :       expression
        ->      ^(CONSTANT expression)
        ;


create_request
        :       CREATE
                createbody
                actual_parameters?
                end
        ->      ^(CREATE createbody actual_parameters?)
        ;


createbody
        :       process_id
                | THIS
        ;


output
        :       cif?
                symbolid?
                hyperlink?
                OUTPUT outputbody end
        ->      ^(OUTPUT cif? hyperlink? symbolid? end? outputbody)
        ;


outputbody
        :       outputstmt (',' outputstmt)* to_part?
        ->      ^(OUTPUT_BODY outputstmt+ to_part?)
        ;
 //               via_part?
 //     -> (signal_id actual_parameters?)+ to_part? via_part?;


outputstmt
        :       signal_id
                actual_parameters?
        ;

to_part
        :       (TO destination)
        ->      ^(TO destination)
        ;

via_part
        :       VIA viabody
        ->      ^(VIA viabody)
        ;


// ambiguous in SDL92, added OR between ALL and via_path
viabody
        :       ALL
        ->      ^(ALL)
                | via_path
        ->      ^(VIAPATH via_path)
        ;


destination
        :       pid_expression
                | process_id
                | THIS
        ;


via_path
        :       via_path_element (',' via_path_element)*
        ->      via_path_element+
        ;


via_path_element
        :       ID
        ; // signal_route_id | channel_id | gate_id;


actual_parameters
        :      '(' expression (',' expression)* ')'
        ->     ^(PARAMS expression+)
        ;


task
        :       cif?
                symbolid?
                hyperlink?
                TASK task_body? end
        ->      ^(TASK cif? hyperlink? symbolid? end? task_body?)
        ;


task_body
        :       (assignment_statement (',' assignment_statement)*)
        ->      ^(TASK_BODY assignment_statement+)
                | (informal_text (',' informal_text)*)
        ->      ^(TASK_BODY informal_text+)
                | (forloop (',' forloop)*)
        ->      ^(TASK_BODY forloop+)
        ;


// SDL extension - FOR loop in TASKs
forloop
        :       FOR variable_id IN (range | variable) ':'
                transition?
                ENDFOR
        ->      ^(FOR variable_id variable? range? transition?);

range
        :       RANGE
                L_PAREN a=ground_expression
                (COMMA b=ground_expression)? (COMMA step=INT)?
                R_PAREN
        ->      ^(RANGE $a $b? $step?);

assignment_statement
        :       variable ':=' expression
        ->      ^(ASSIGN variable expression);


// Variable: covers eg. toto(5)(4)!titi(3)!tutu!yoyo
variable
        :       postfix_expression
        |       ID                     ->  ^(VARIABLE ID);


field_selection
        :       (('!' | DOT) field_name);


expression
        :       binary_expression;


binary_expression
        :       binary_expression_0 ( IMPLIES^ binary_expression_0)*;
binary_expression_0
        :       binary_expression_1 (( (OR^ ELSE?) | XOR^ ) binary_expression_1)*;
binary_expression_1
        :       binary_expression_2 ( AND^ THEN? binary_expression_2)*;
binary_expression_2
        :       binary_expression_3 (( EQ^ | NEQ^ | GT^ | GE^ | LT^ | LE^ | IN^ ) binary_expression_3)*;
binary_expression_3
        :       binary_expression_4 (( PLUS^ | DASH^ | APPEND^ ) binary_expression_4)*;
binary_expression_4
        :       unary_expression (( ASTERISK^ | DIV^ | MOD^ | REM^ ) unary_expression)*;


unary_expression
        :       postfix_expression
        |       primary_expression
        |       NOT^ unary_expression
        |       DASH unary_expression    -> ^(NEG unary_expression)
        |       CALL procedure_call_body -> ^(PROCEDURE_CALL procedure_call_body)
        |       input_expression            // used in observers
        |       output_expression           // used in observers
        ;


postfix_expression
        :       (ID -> ^(PRIMARY ^(VARIABLE ID)))
                (   '(' params=expression_list? ')'
                -> ^(CALL $postfix_expression ^(PARAMS $params?))
                |   ('!' | DOT) field_name
                -> ^(SELECTOR $postfix_expression field_name)
                )+
        ;

//  input and output expression allow observers (for model checking) to
//  monitor the sending and receiving of messages with a nice syntax
//  (e.g. event = output msg (p) from foo)
//  the parameter is optional. It does not need to be declared as a variable,
//  as it it implicit.
input_expression
        :       UNHANDLED? INPUT
                -> ^(INPUT_EXPRESSION UNHANDLED?)
                | UNHANDLED? INPUT (msg=ID ('(' param=ID ')')? )? (FROM src=ID)? TO dest=ID
                -> ^(INPUT_EXPRESSION UNHANDLED? $msg? ^(IOPARAM $param)? ^(FROM $src)? ^(TO $dest))
        ;


output_expression
        :       OUTPUT
                -> ^(OUTPUT_EXPRESSION)
                | OUTPUT (msg=ID ('(' param=ID ')')? )? (FROM src=ID) (TO dest=ID)?
                -> ^(OUTPUT_EXPRESSION $msg? ^(IOPARAM $param)? ^(FROM $src) ^(TO $dest)?)
        ;

primary_expression
        :       primary                       -> ^(PRIMARY primary)
        |       '(' expression ')'            -> ^(PAREN expression)
        |       conditional_expression
        ;

//  primary covers most expressions with ASN.1 value notation
//  note that mkstring is the SDL operator transforming an element
//  into an array. The regular sytanx { hello(1) } is ambiguous because
//  it could be a record element with value 1 as well as an array with index 1
primary
        :       TRUE^
        |       FALSE^
        |       STRING
        |       PLUS_INFINITY^
        |       MINUS_INFINITY^
        |       INT^
        |       FLOAT^
        |       ID ':' expression           -> ^(CHOICE ID expression)
        |       ID                          -> ^(VARIABLE ID)
        |       '{' '}'                     -> ^(EMPTYSTR)
        |       '{'
                MANTISSA mant=INT COMMA
                BASE bas=INT COMMA
                EXPONENT exp=INT
                '}'                         -> ^(FLOAT2 $mant $bas $exp)
        |       '{'
                named_value (COMMA named_value)*
                '}'                         -> ^(SEQUENCE named_value+)
        |       '{'
                expression (COMMA expression)*
                '}'                         -> ^(SEQOF expression+)
        |       MKSTRING '(' expression (COMMA expression)* ')'
                                            -> ^(SEQOF expression+)
        |       STATE^
        ;


informal_text
        :        STRING
        ->       ^(INFORMAL_TEXT STRING)
        ;


// { a 5 } (SEQUENCE field value)
named_value
        :       ID expression
        ;

/*
primary_params
        :      '(' expression_list ')'
        ->     ^(PARAMS expression_list)
               | '!' literal_id
        ->     ^(FIELD_NAME literal_id)
        ;
*/

/* All cases are covered by the ground primary
   above (Except structure primary, but we favour ASN.1 notation)
extended_primary
        :       synonym         |
                indexed_primary |
                field_primary   |
                structure_primary
        ;
*/


indexed_primary
        :       primary '(' expression_list ')'
        ;


field_primary
        :       primary field_selection
        ;


structure_primary
        :       '(.' expression_list '.)'
        ;
// Removed "qualifier" from the standard
// (to be put later, but never used in practice)

/*
active_expression
        :       active_primary
        ;


active_primary
        :       variable_access
                | operator_application
                | conditional_expression
                | imperative_operator
                | '(' active_expression ')'
                | 'ERROR'
        ;
   // active_extended_primary removed because not defined in the standard


imperative_operator
        :       now_expression
                | import_expression
                | pid_expression
                | view_expression
                | timer_active_expression
                | anyvalue_expression
        ;


timer_active_expression
        :       ACTIVE '(' timer_id ('(' expression_list ')')? ')'
        ;


anyvalue_expression
        :       ANY '(' sort ')'
        ;
*/

sort    :       sort_id
        ->      ^(SORT sort_id)
        ;


type_inst
        :       type_id
        ->      ^(TYPE_INSTANCE type_id)
        ;


syntype :       syntype_id
        ;

/*
import_expression
        :       IMPORT '(' remote_variable_id (',' destination)? ')'
        ;


view_expression
        :       VIEW '(' view_id (',' pid_expression)? ')'
        ;
*/

variable_access
        :       variable_id
        ;

/*
operator_application
        :       operator_id '('active_expression_list ')'
        ;


active_expression_list
        :       active_expression (',' expression_list)?
        ;
// 	| ground_expression ',' active_expression_list;   // Will not work (recursion)

*/

//synonym :       ID; // synonym_id | external_synonym;

external_synonym
        :       external_synonym_id
        ;


conditional_expression
        :       IF ifexpr=expression
                THEN thenexpr=expression
                ELSE elseexpr=expression FI
        ->      ^(CONDITIONAL $ifexpr $thenexpr $elseexpr)
        ;


expression_list
        :       expression (',' expression)*
        ->      expression+
        ;


terminator_statement
        :       label?
                cif?
                symbolid?
                hyperlink?
                terminator
                end
        ->      ^(TERMINATOR label? cif? hyperlink? symbolid? end? terminator)
        ;

label
        :       cif? symbolid? connector_name ':'
        ->      ^(LABEL cif? symbolid? connector_name)
        ;


terminator
        :       nextstate | join | stop | return_stmt
        ;


join
        :        JOIN connector_name
        ->       ^(JOIN connector_name)
        ;


stop    :       STOP
        ;


return_stmt
        :       RETURN expression?
        ->      ^(RETURN expression?)
        ;


nextstate
        :       NEXTSTATE nextstatebody
        ->      ^(NEXTSTATE nextstatebody)
        ;


nextstatebody
        :       statename (':'! type_inst)? via?
                | dash_nextstate
                | history_nextstate
        ;


via     :       VIA state_entry_point_name
        ->      ^(VIA state_entry_point_name)
        ;


end
        :   (cif? symbolid? hyperlink? COMMENT STRING)? SEMI+
        -> ^(COMMENT cif? hyperlink? symbolid? STRING)?
        ;


cif
        :       (cif_decl symbolname
                L_PAREN x=signed COMMA y=signed R_PAREN
                COMMA
                L_PAREN width=INT COMMA height=INT R_PAREN
                cif_end
        ->      ^(CIF $x $y $width $height))
        ;


hyperlink
        :       cif_decl KEEP SPECIFIC GEODE HYPERLINK STRING
                cif_end
        ->      ^(HYPERLINK STRING)
        ;

symbolid
        :       cif_decl '_id' ptr=INT cif_end
        ->      ^(SYMBOLID $ptr)
        ;

/* OpenGEODE specific: SDL does not allow specifying the name
   of signal parameters, but it is needed to generate function signatures
   when generating code (in particular in Ada, where the name in the
   body must comply with the one of the source
   Extension is using CIF comment so it is invisible to other SDL parsers
   (This is valid SDL code - see ITU-T Z106)
*/
paramnames
        :       cif_decl KEEP SPECIFIC GEODE PARAMNAMES field_name+ cif_end
        ->      ^(PARAMNAMES field_name+)
        ;


/* OpenGEODE specific: Allow specifying the name of an ASN.1 file
   as a CIF extension linked to a USE clause.
   CIF Extensions are valid SDL constructs (ITU-T Z106)
*/
use_asn1
        :       cif_decl KEEP SPECIFIC GEODE ASNFILENAME STRING cif_end
        ->      ^(ASN1 STRING)
        ;


/* OpenGEODE specific: Boolean condition that can be used in simulators
*/
stop_if
        :       (STOP IF expression end)+
        ->      ^(STOPIF expression+)
        ;


symbolname
        :       START
                | INPUT
                | OUTPUT
                | STATE
                | PROCEDURE
                | PROCESS
                | PROCEDURE_CALL
                | STOP
                | RETURN
                | DECISION
                | TEXT
                | TASK
                | NEXTSTATE
                | ANSWER
                | PROVIDED
                | COMMENT
                | LABEL
                | JOIN
                | CONNECT
        ;


cif_decl
        :       '/* CIF'
        ;


cif_end
        :       '*/'
        ;


cif_end_text
        :       cif_decl ENDTEXT cif_end
        ->      ^(ENDTEXT)
        ;


cif_end_label
        :       cif_decl END LABEL cif_end
        ;

/* OpenGEODE specific: Stop Condition Language rules for TASTE Model Checker.
*/
n7s_scl
        :       (n7s_scl_statement)*
        ->      ^(N7S_SCL n7s_scl_statement*)
        ;

n7s_scl_statement
        :       (n7s_scl_never | n7s_scl_always | n7s_scl_eventually | n7s_scl_filter_out)
        ;

n7s_scl_never
        :       (NEVER expression end)
        ->      ^(NEVER expression)
        ;

n7s_scl_always
        :       (ALWAYS expression end)
        ->      ^(ALWAYS expression)
        ;

n7s_scl_eventually
        :       (EVENTUALLY expression end)
        ->      ^(EVENTUALLY expression)
        ;

n7s_scl_filter_out
        :       (FILTER_OUT expression end)
        ->      ^(FILTER_OUT expression)
        ;

// Token used by Stop Condition Language for TASTE Model Checker.
ALWAYS          :       A L W A Y S;
NEVER           :       N E V E R;
EVENTUALLY      :       E V E N T U A L L Y;
FILTER_OUT      :       F I L T E R '_' O U T;

// history nextstate allows to re-enter parallel substates without going
// through the startup transition.
history_nextstate
        :       '-*'  -> ^(HISTORY_NEXTSTATE)
        ;

dash_nextstate  :       DASH;
connector_name  :       ID;
signal_id       :       ID;
statename       :       ID;
state_exit_point_name
                :       ID;
state_entry_point_name
                :       ID;
variable_id     :       ID;
literal_id      :       ID | INT;
process_id      :       ID;
system_name     :       ID;
package_name    :       ID;
priority_signal_id
                :       ID;
signal_list_id  :       ID;
timer_id        :       ID;
field_name      :       ID | STATE;
signal_route_id :       ID;
channel_id      :       ID;
route_id        :       ID;
block_id        :       ID;
source_id       :       ID;
dest_id         :       ID;
gate_id         :       ID;
procedure_id    :       ID;
remote_procedure_id
                :       ID;
operator_id     :       ID;
synonym_id      :       ID;
external_synonym_id
                :       ID;
remote_variable_id
                :       ID;
view_id         :       ID;
sort_id         :       ID;
type_id         :       ID;
syntype_id      :       ID;
stimulus_id     :       ID;
ASSIG_OP        :       ':=';
L_BRACKET       :       '{';
R_BRACKET       :       '}';
L_PAREN         :       '(';
R_PAREN         :       ')';
COMMA           :       ',';
SEMI            :       ';';
DASH            :       '-';
ANY             :       A N Y;
ASTERISK        :       '*';
DCL             :       D C L;
RENAMES         :       R E N A M E S;
MONITOR         :       M O N I T O R;
END             :       E N D;
KEEP            :       K E E P;
PARAMNAMES      :       P A R A M N A M E S;
SPECIFIC        :       S P E C I F I C;
GEODE           :       G E O D E;
HYPERLINK       :       H Y P E R L I N K;
MKSTRING        :       M K S T R I N G;
ENDTEXT         :       E N D T E X T;
RETURN          :       R E T U R N;
RETURNS         :       R E T U R N S;
TIMER           :       T I M E R;
PROCESS         :       P R O C E S S;
TYPE            :       T Y P E;
ENDPROCESS      :       E N D P R O C E S S;
START           :       S T A R T;
STATE           :       S T A T E;
TEXT            :       T E X T;
PROCEDURE       :       P R O C E D U R E;
ENDPROCEDURE    :       E N D P R O C E D U R E;
PROCEDURE_CALL  :       P R O C E D U R E C A L L;
ENDSTATE        :       E N D S T A T E;
INPUT           :       I N P U T;
PROVIDED        :       P R O V I D E D;
PRIORITY        :       P R I O R I T Y;
SAVE            :       S A V E;
NONE            :       N O N E;
pid_expression
                :       S E L F
                |       P A R E N T
                |       O F F S P R I N G
                |       S E N D E R;
now_expression  :       N O W;
FOR             :       F O R;
ENDFOR          :       E N D F O R;
RANGE           :       R A N G E;
NEXTSTATE       :       N E X T S T A T E;
ANSWER          :       A N S W E R;
COMMENT         :       C O M M E N T;
LABEL           :       L A B E L;
STOP            :       S T O P;
IF              :       I F;
THEN            :       T H E N;
ELSE            :       E L S E;
FI              :       F I;
CREATE          :       C R E A T E;
OUTPUT          :       O U T P U T;
CALL            :       C A L L;
THIS            :       T H I S;
//SET             :       S E T;
//RESET           :       R E S E T;
ENDALTERNATIVE  :       E N D A L T E R N A T I V E;
ALTERNATIVE     :       A L T E R N A T I V E;
DEFAULT         :       D E F A U L T;
DECISION        :       D E C I S I O N;
ENDDECISION     :       E N D D E C I S I O N;
EXPORT          :       E X P O R T;
EXTERNAL        :       E X T E R N A L;
EXPORTED        :       E X P O R T E D;
REFERENCED      :       R E F E R E N C E D;
CONNECTION      :       C O N N E C T I O N;
ENDCONNECTION   :       E N D C O N N E C T I O N;
FROM            :       F R O M;
TO              :       T O;
WITH            :       W I T H;
VIA             :       V I A;
ALL             :       A L L;
TASK            :       T A S K;
JOIN            :       J O I N;
PLUS            :       '+';
DOT             :       '.';
APPEND          :       '//';
IN              :       I N;
OUT             :       O U T;
INOUT           :       I N '/' O U T;
AGGREGATION     :       A G G R E G A T I O N;
SUBSTRUCTURE    :       S U B S T R U C T U R E;
ENDSUBSTRUCTURE :       E N D S U B S T R U C T U R E;
FPAR            :       F P A R;
EQ              :       '=';
NEQ             :       '/=';
GT              :       '>';
GE              :       '>=';
LT              :        '<';
LE              :       '<=';
NOT             :       N O T;
OR              :       O R;
XOR             :       X O R;
AND             :       A N D;
IMPLIES         :       '=>';
DIV             :       '/';
MOD             :       M O D;
REM             :       R E M;
TRUE            :       T R U E;
FALSE           :       F A L S E;
ASNFILENAME     :       A S N F I L E N A M E;
PLUS_INFINITY   :       P L U S '-' I N F I N I T Y;
MINUS_INFINITY  :       M I N U S '-' I N F I N I T Y;
MANTISSA        :       M A N T I S S A;
EXPONENT        :       E X P O N E N T;
BASE            :       B A S E;
SYSTEM          :       S Y S T E M;
ENDSYSTEM       :       E N D S Y S T E M;
CHANNEL         :       C H A N N E L;
ENDCHANNEL      :       E N D C H A N N E L;
USE             :       U S E;
SIGNAL          :       S I G N A L;
BLOCK           :       B L O C K;
ENDBLOCK        :       E N D B L O C K;
SIGNALROUTE     :       S I G N A L R O U T E;
CONNECT         :       C O N N E C T;
SYNTYPE         :       S Y N T Y P E;
ENDSYNTYPE      :       E N D S Y N T Y P E;
NEWTYPE         :       N E W T Y P E;
ENDNEWTYPE      :       E N D N E W T Y P E;
ARRAY           :       A R R A Y;
CONSTANTS       :       C O N S T A N T S;
STRUCT          :       S T R U C T;
SYNONYM         :       S Y N O N Y M;
IMPORT          :       I M P O R T;
VIEW            :       V I E W;
ACTIVE          :       A C T I V E;
UNHANDLED       :       U N H A N D L E D;
//  Observer special states (error, ignore, success)
ERRORSTATES     :       E R R O R S T A T E S;
IGNORESTATES    :       I G N O R E S T A T E S;
SUCCESSSTATES   :       S U C C E S S S T A T E S;


STRING
        :       STR+ (B|H)?
        ;


// Strings can be either single or double quoted
fragment
STR
       // :       '\'' ( options {greedy=false;} : .)* '\''
        :       '\'' (ESC1 | ~('\\' | '\'' ))* '\''
        |       '"' (ESC2 | ~('\\' | '"' ))* '"'
        //|       '"' ( options {greedy=false;} : .)* '"'
        ;

// escaping for single-quote strings
fragment
ESC1    : '\\'
        (
        | '\''
        | '\\')
        ;

// escaping for double-quote strings
fragment
ESC2    : '\\'
        (
        | '"'
        | '\\')
        ;


ID
        :       ALPHA (ALPHA | DIGITS | '_')*
        ;


fragment
ALPHA
        :       ('a'..'z')
                |('A'..'Z')
        ;


INT
        :        '0' | ('1'..'9') ('0'..'9')*
        ;

signed
        :       DASH? INT
        ;

fragment
DIGITS
        :       ('0'..'9')+
        ;


FLOAT
        :       INT DOT (DIGITS)? (Exponent)?
        |       INT
        ;


WS
        :       (' ' | '\t' | '\r' | '\n')+ {$channel=HIDDEN;}
        ;


/*
COMMENT
    :   '//' ( options {greedy=false;} : . )* '//' {$channel=HIDDEN;}
    ;
*/

fragment
Exponent
        : ('e'|'E') ('+'|'-')? ('0'..'9')+
        ;


COMMENT2
        :        '--' ( options {greedy=false;} : . )* ('--'|'\r'?'\n')
                 {$channel=HIDDEN;}
        ;


// Following fragments allows to have case insensitive grammar
fragment A:('a'|'A');
fragment B:('b'|'B');
fragment C:('c'|'C');
fragment D:('d'|'D');
fragment E:('e'|'E');
fragment F:('f'|'F');
fragment G:('g'|'G');
fragment H:('h'|'H');
fragment I:('i'|'I');
fragment J:('j'|'J');
fragment K:('k'|'K');
fragment L:('l'|'L');
fragment M:('m'|'M');
fragment N:('n'|'N');
fragment O:('o'|'O');
fragment P:('p'|'P');
fragment Q:('q'|'Q');
fragment R:('r'|'R');
fragment S:('s'|'S');
fragment T:('t'|'T');
fragment U:('u'|'U');
fragment V:('v'|'V');
fragment W:('w'|'W');
fragment X:('x'|'X');
fragment Y:('y'|'Y');
fragment Z:('z'|'Z');
