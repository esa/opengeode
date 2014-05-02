/* 
    OpenGEODE
    ANTLR 3.1.3 grammar for the SDL92 langage
    Includes the following features from SDL2000+:
    - FOR loops in TASKs
    - Composite states

    author: Maxime Perrotin
*/

grammar sdl92;

options {
    language=Python;
    output=AST;
    ASTLabelType=CommonTree;
    backtrack=true;
}

tokens {
        FOR;
        RANGE;
        TIMER;
        LABEL;
        IFTHENELSE;
        COMMENT;
        VALUE;
        CHOICE;
        SEQUENCE;
        SEQOF;
        EMPTYSTR;
        FLOAT;
        FLOAT2;
        BITSTR;
        OCTSTR;
        STRING;
        EXPRESSION;
        DIGITS;
        ENDTEXT;
        PROCESS;
        NUMBER_OF_INSTANCES;
        TRANSITION;
        STATE;
        INPUT_NONE;
        SAVE;
        PROVIDED;
        SIGNAL_LIST;
        INPUT;
        STIMULUS;
        ACTION;
        PROCEDURE_CALL;
        PROCEDURE;
        SET;
        RESET;
        EXPORT;
        DECISION;
        ALTERNATIVE;
        ANSWER;
        CLOSED_RANGE;
        OPEN_RANGE;
        CONSTANT;
        ELSE;
        ALL;
        TO;
        VIA;
        VIAPATH;
        OUTPUT;
        OUTPUT_BODY;
        ASSIGN;
        TEXT;
        NEXTSTATE;
        JOIN;
        TERMINATOR;
        RETURN;
        PROCEDURE_NAME;
        PARAMS;
        FIELD_NAME;
        PRIMARY;
        PRIMARY_ID;
        IF;
        THEN;
        FI;
        CIF;
        HYPERLINK;
        STATELIST;
        INPUTLIST;
        INFORMAL_TEXT;
        VARIABLE;
        VARIABLES;
        SORT;
        DCL;
        MINUS;
        GROUND;
        TEXTAREA;
        TEXTAREA_CONTENT;
        TASK;
        TASK_BODY;
        QUESTION;
        FPAR;
        PARAM;
        INOUT;
        EXTERNAL;
        IN;
        STOP;
        SYSTEM;
        USE;
        SIGNAL;
        CHANNEL;
        CONNECTION;
        ROUTE;
        BLOCK;
        PARAMNAMES;
        ASN1;
        FLOATING_LABEL;
        COMPOSITE_STATE;
        CONNECT;
}


/*
    Top level: any .pr file
*/

pr_file
        :       (use_clause
                | system_definition
                | process_definition)+;


system_definition
        :       SYSTEM system_name end
                entity_in_system*
                ENDSYSTEM system_name? end
        ->      ^(SYSTEM system_name entity_in_system*);


use_clause
        :       use_asn1?
                USE package_name end
        ->      ^(USE use_asn1? package_name);


/* Entity in system:
   Declare signals, external procedures, connections and blocks
*/
entity_in_system
        :       signal_declaration
                | procedure
                | channel
                | block_definition;

/* signal_declaration:
   e.g. SIGNAL open_door(typeA, typeB);
*/
signal_declaration
        :       paramnames?
                SIGNAL signal_id input_params? end
        ->      ^(SIGNAL paramnames? signal_id input_params?);


channel
        :       CHANNEL channel_id
                route+
                ENDCHANNEL end
        ->      ^(CHANNEL channel_id route+);


route
        :       FROM source_id TO dest_id WITH signal_id (',' signal_id)* end
        ->      ^(ROUTE source_id dest_id signal_id+);


block_definition
        :       BLOCK block_id end
                entity_in_block* 
                ENDBLOCK end
        ->      ^(BLOCK block_id entity_in_block*);


/* Inside a SDL block:
   there can be nested blocks, processes, signalroutes and connections
   to above channels
*/
entity_in_block
        :       signal_declaration
                | signalroute
                | connection
                | block_definition
                | process_definition;


signalroute
        :       SIGNALROUTE route_id
                route+
        ->      ^(SIGNALROUTE route_id route+);


connection
        :       CONNECT channel_id AND route_id end
        ->      ^(CONNECTION channel_id route_id);


process_definition
        :       PROCESS process_id number_of_instances? REFERENCED end
        ->      ^(PROCESS process_id number_of_instances? REFERENCED)
                | cif? PROCESS process_id number_of_instances? end
                (text_area | procedure | composite_state)*
                processBody? ENDPROCESS process_id?
                end
        ->      ^(PROCESS cif? process_id number_of_instances?
                text_area* procedure* composite_state* processBody?);


// procedure: missing the RETURNS statement
// (TODO - but check new SDL2000 syntax that has no RETURNS token)
procedure
        :       cif?
                PROCEDURE procedure_id end
                fpar?
                (text_area | procedure)*
                ((processBody? ENDPROCEDURE procedure_id?) | EXTERNAL)
                end
        ->      ^(PROCEDURE cif? procedure_id end? fpar?
                text_area* procedure* processBody? EXTERNAL?);


// Procedure formal parameters
fpar
        :       FPAR formal_variable_param
                (',' formal_variable_param)*
                end
        ->      ^(FPAR formal_variable_param+);


formal_variable_param
        :       (INOUT | IN)?
                variable_id (',' variable_id)* sort
        ->      ^(PARAM INOUT? IN? variable_id+ sort);


// text_area: TODO add operator description in content
text_area
        :       cif
                content?
                cif_end_text
        ->      ^(TEXTAREA cif content? cif_end_text);


// Text areas can contain textual procedures, FPAR declarations,
// and variable or timer declarations
content
        :        (procedure
                 | fpar
                 | timer_declaration
                 | variable_definition)*
        ->       ^(TEXTAREA_CONTENT
                     fpar* procedure* variable_definition* timer_declaration*);


timer_declaration
        :       TIMER timer_id
                (',' timer_id)*
                end
        ->      ^(TIMER timer_id+);

variable_definition
        :       DCL variables_of_sort
                (',' variables_of_sort)*
                end
        ->      ^(DCL variables_of_sort+);


variables_of_sort
        :       variable_id (',' variable_id)* sort (':=' ground_expression)?
        ->      ^(VARIABLES variable_id+ sort ground_expression?);


ground_expression
        :       expression
        ->      ^(GROUND expression);


number_of_instances
        :       '(' initial_number=INT ',' maximum_number=INT ')'
        ->      ^(NUMBER_OF_INSTANCES $initial_number $maximum_number);


processBody
        :       start? (state | floating_label)*;


start
        :       cif?
                hyperlink?
                START name=state_entry_point_name? end
                transition?
        ->      ^(START cif? hyperlink? $name? end? transition?);


floating_label
        :       cif?
                hyperlink?
                CONNECTION connector_name ':'
                transition?
                cif_end_label?
                ENDCONNECTION SEMI
        ->      ^(FLOATING_LABEL cif? hyperlink? connector_name transition?);


state
        :       cif?
                hyperlink?
                STATE statelist e=end
                (state_part)*
                ENDSTATE statename? f=end
        ->      ^(STATE cif? hyperlink? $e? statelist state_part*);


statelist
        :       ((statename)(',' statename)*)
        ->      ^(STATELIST statename+)
                | ASTERISK exception_state?
        ->      ^(ASTERISK exception_state?);


exception_state
        :       '(' statename (',' statename)* ')'
        ->      statename+;


composite_state
        :       STATE statename e=end
                SUBSTRUCTURE
                connection_points*
                body=composite_state_body
                ENDSUBSTRUCTURE statename? f=end
        ->      ^(COMPOSITE_STATE statename connection_points* $body $e?);


connection_points
        :       IN state_entry_exit_points end
        ->      ^(IN state_entry_exit_points end?)
                | OUT state_entry_exit_points end
        ->      ^(OUT state_entry_exit_points end?);


state_entry_exit_points
        :       '(' statename (',' statename)* ')'
        ->      statename+;


composite_state_body
        :       (text_area | procedure | composite_state)*
                start* (state | floating_label)*;


state_part
        :       input_part
                //| priority_input        // Not supported
                | save_part               // Not supported in openGEODE
                | spontaneous_transition
                | continuous_signal       // Not supoorted in openGEODE
                | connect_part;


// connect part is used to connect nested state exit points to a transition
connect_part
        :       cif?
                hyperlink?
                CONNECT connect_list? end
                transition?
        ->      ^(CONNECT cif? hyperlink? connect_list? end? transition?);


connect_list
        :       state_exit_point_name (',' state_exit_point_name)*
                -> state_exit_point_name+
                | ASTERISK;


spontaneous_transition
        :       cif?
                hyperlink?
                INPUT NONE end
                enabling_condition?
                transition
        ->      ^(INPUT_NONE cif? hyperlink? transition);


enabling_condition
        :       PROVIDED expression end
        ->      ^(PROVIDED expression);


continuous_signal
        :       PROVIDED expression end 
                (PRIORITY integer_literal_name=INT end)?
                transition
        ->      ^(PROVIDED expression $integer_literal_name? transition);


save_part
        :       SAVE save_list
                end
        ->      ^(SAVE save_list);


save_list
        :       signal_list
                | asterisk_save_list;


asterisk_save_list
        :       ASTERISK;


signal_list
        :       signal_item (',' signal_item)*
        ->      ^(SIGNAL_LIST signal_item+);



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
        :       'PRIORITY INPUT' priority_input_list end transition;


priority_input_list
        :       priority_stimulus (',' priority_stimulus)*;

priority_stimulus
        :       priority_signal_id ( '(' variable_id (',' variable_id)* ')');
*/


// this is only the "basic input part" from SDL92
input_part
        :       cif?
                hyperlink?
                INPUT inputlist end
                enabling_condition?
                transition?
        ->      ^(INPUT cif? hyperlink? end?
                inputlist enabling_condition? transition?);


// asterisk means: all signals not excplicitely specified
// (semantic is different from asterisk state)
inputlist
        :       ASTERISK
                | (stimulus (',' stimulus)*)
        ->      ^(INPUTLIST stimulus+);


stimulus
        :       stimulus_id input_params?;


input_params
        :       L_PAREN variable_id (',' variable_id)* R_PAREN
        ->      ^(PARAMS variable_id+);


transition
        :       action+ label? terminator_statement?
        ->      ^(TRANSITION action+ label? terminator_statement?)
                | terminator_statement
        ->      ^(TRANSITION terminator_statement);


action
        :       label?
                (task
                | task_body
                | output
                | create_request
                | decision
                | transition_option
                | set_timer
                | reset_timer
                | export     // Not supported in OpenGEODE
                | procedure_call);

export
        :       EXPORT
                L_PAREN variable_id (COMMA variable_id)* R_PAREN
                end
        ->      ^(EXPORT variable_id+);

/*
remote_procedure_call
        :       'CALL' remote_procedure_call_body;

remote_procedure_call_body
        :       remote_procedure_id actual_parameters? ('TO' destination)?;
*/


procedure_call
        :       cif?
                hyperlink?
                CALL procedure_call_body end
        ->      ^(PROCEDURE_CALL cif? hyperlink? end? procedure_call_body);


procedure_call_body
        :       procedure_id actual_parameters?   
        ->      ^(OUTPUT_BODY procedure_id actual_parameters?);


set_timer
        :       SET set_statement (COMMA set_statement)*
                end
        ->      set_statement+;


set_statement
        :       L_PAREN (expression COMMA)? timer_id R_PAREN
        ->      ^(SET expression? timer_id);
        // ('('expression_list')')? ')'; (removed because of non-LL(*) problem)


reset_timer
        :       RESET reset_statement (',' reset_statement)*
                end
        ->      reset_statement+;


reset_statement
        :       timer_id ('(' expression_list ')')?
        ->      ^(RESET timer_id expression_list?);


transition_option
        :       ALTERNATIVE alternative_question e=end
                answer_part
                alternative_part
                ENDALTERNATIVE f=end
        ->      ^(ALTERNATIVE answer_part alternative_part);


alternative_part
        :       (answer_part+ else_part?)
        ->      answer_part+ else_part?
                | else_part
        ->      else_part;


alternative_question
        :       expression
                | informal_text;


decision
        :       cif?
                hyperlink?
                DECISION question e=end
                answer_part?
                alternative_part?
                ENDDECISION f=end
        ->      ^(DECISION cif? hyperlink? $e? question
                answer_part? alternative_part?);


answer_part
        :       cif?
                hyperlink?
                L_PAREN answer R_PAREN ':' transition?
        ->      ^(ANSWER cif? hyperlink? answer transition?);


answer
        :       range_condition
                | informal_text;


else_part
        :       cif?
                hyperlink?
                ELSE ':' transition?
        ->      ^(ELSE cif? hyperlink? transition?);


question
        :       expression
        ->      ^(QUESTION expression)
                | informal_text
        ->      informal_text
                | ANY
        ->      ^(ANY);


range_condition
        :       (closed_range | open_range);
                //(',' (closed_range|open_range))*;


closed_range
        :       a=INT ':' b=INT
        ->      ^(CLOSED_RANGE $a $b);


open_range
        :       constant
        ->      constant
                | ( (EQ|NEQ|GT|LT|LE|GE) constant)
        ->      ^(OPEN_RANGE EQ? NEQ? GT? LT? LE? GE? constant);


constant
        :       expression
        ->      ^(CONSTANT expression);


create_request
        :       CREATE 
                createbody
                actual_parameters?
                end
        ->      ^(CREATE createbody actual_parameters?);


createbody
        :       process_id
                | THIS;


output
        :       cif?
                hyperlink?
                OUTPUT outputbody end
        ->      ^(OUTPUT cif? hyperlink? end? outputbody);


outputbody
        :       outputstmt (',' outputstmt)*
        ->      ^(OUTPUT_BODY outputstmt+);
//                to_part?
//                via_part?
//      -> (signal_id actual_parameters?)+ to_part? via_part?;


outputstmt
        :       signal_id 
                actual_parameters?;

//to_part
//        :       ('TO' destination)
//        -> ^(TO destination);

//via_part
//        :       'VIA' viabody
//        -> ^(VIA viabody);


// ambiguous in SDL92, added OR between ALL and via_path
viabody
        :       'ALL'
        ->      ^(ALL)
                | via_path
        ->      ^(VIAPATH via_path);


destination
        :       pid_expression
                | process_id
                | THIS;


via_path
        :       via_path_element (',' via_path_element)*
        ->      via_path_element+;


via_path_element
        :       ID; // signal_route_id | channel_id | gate_id;


actual_parameters
        :      '(' expression (',' expression)* ')'
        ->     ^(PARAMS expression+);


task
        :       cif?
                hyperlink?
                TASK task_body? end
        ->      ^(TASK cif? hyperlink? end? task_body?);


task_body
        :       (assignement_statement (',' assignement_statement)*)
        ->      ^(TASK_BODY assignement_statement+)
                | (informal_text (',' informal_text)*)
        ->      ^(TASK_BODY informal_text+)
                | (forloop (',' forloop)*)
        ->      ^(TASK_BODY forloop+)
        ;

// SDL extension - FOR loop in TASKs
forloop
        :       FOR variable_id IN (variable | range) ':'
                transition?
                ENDFOR
        ->      ^(FOR variable_id variable? range? transition?);

range
        :       RANGE
                L_PAREN a=ground_expression
                (COMMA b=ground_expression)? (COMMA step=INT)?
                R_PAREN
        ->      ^(RANGE $a $b? $step?);

assignement_statement
        :       variable ':=' expression
        ->      ^(ASSIGN variable expression);


// Variable: covers eg. toto(5)(4)!titi(3)!tutu!yoyo
variable
        :       variable_id primary_params*
        ->      ^(VARIABLE variable_id primary_params*);

field_selection
        :       (('!'|'.') field_name);

expression      :       operand0 ( IMPLIES^ operand0)* ;
operand0        :       operand1 (( OR^ | XOR^ ) operand1)*;
operand1        :       operand2 ( AND^ operand2)*;
operand2        :       operand3
                        (( EQ^ | NEQ^ | GT^ | GE^ | LT^ | LE^ | IN^ )
                        operand3)*;
operand3        :       operand4 (( PLUS^ | DASH^ | APPEND^ ) operand4)*;
operand4        :       operand5
                        (( ASTERISK^ | DIV^ | MOD^ | REM^ ) operand5)*;
operand5        :       primary_qualifier? primary
                ->      ^(PRIMARY primary_qualifier? primary);


// primary below covers all cases including ASN.1 Value Notation 
primary
        :       a=asn1Value primary_params*
        ->      ^(PRIMARY_ID asn1Value primary_params*)
                | L_PAREN expression R_PAREN
        ->      ^(EXPRESSION expression)
                | conditional_ground_expression;

// ASN.1 Value Notation used for assignations and comparisons
asn1Value
        :       BitStringLiteral            -> ^(BITSTR BitStringLiteral)
        |       OctetStringLiteral          -> ^(OCTSTR OctetStringLiteral)
        |       TRUE^
        |       FALSE^
        |       StringLiteral               -> ^(STRING StringLiteral)
        |       NULL^
        |       PLUS_INFINITY^
        |       MINUS_INFINITY^
        |       ID
        |       INT
        |       FloatingPointLiteral        -> ^(FLOAT FloatingPointLiteral)
        |       L_BRACKET R_BRACKET         -> ^(EMPTYSTR)
        |       L_BRACKET
                MANTISSA mant=INT COMMA
                BASE bas=INT COMMA
                EXPONENT exp=INT 
                R_BRACKET                   -> ^(FLOAT2 $mant $bas $exp)
        |       choiceValue
        |       L_BRACKET
                namedValue (COMMA namedValue)*
                R_BRACKET                   -> ^(SEQUENCE namedValue+)
        |       L_BRACKET
                asn1Value (COMMA asn1Value)*
                R_BRACKET                   -> ^(SEQOF asn1Value+)
        ;

BitStringLiteral
        :       '"' ('0'|'1'|' ' | '\t' | '\r' | '\n')* '"B';


OctetStringLiteral
        :       '"' ('0'..'9'|'a'..'f'|'A'..'F'|' ' | '\t' | '\r' | '\n')*
                '"H';


informal_text
        :        StringLiteral
        ->       ^(INFORMAL_TEXT StringLiteral);


// hello:5  (CHOICE field value)
choiceValue 
        :        choice=ID ':' expression
        ->       ^(CHOICE $choice expression);


// { a 5 } (SEQUENCE field value)
namedValue
        :       ID expression;


primary_qualifier
        :       DASH
        ->      ^(MINUS)
                | NOT;


primary_params
        :      '(' expression_list ')'
        ->     ^(PARAMS expression_list)
               | '!' literal_id
        ->     ^(FIELD_NAME literal_id);


/* All cases are covered by the ground primary 
   above (Except structure primary, but we favour ASN.1 notation)
extended_primary
        :       synonym         |
                indexed_primary |
                field_primary   |
                structure_primary;
*/


indexed_primary
        :       primary '(' expression_list ')';


field_primary
        :       primary field_selection;


structure_primary
        :       '(.' expression_list '.)';
// Removed "qualifier" from the standard
// (to be put later, but never used in practice)


active_expression
        :       active_primary;


active_primary
        :       variable_access
                | operator_application
                | conditional_expression
                | imperative_operator
                | '(' active_expression ')'
                | 'ERROR';
   // active_extended_primary removed because not defined in the standard


imperative_operator
        :       now_expression
                | import_expression
                | pid_expression
                | view_expression
                | timer_active_expression
                | anyvalue_expression;


timer_active_expression
        :       'ACTIVE' '(' timer_id ('(' expression_list ')')? ')';


anyvalue_expression
        :       'ANY' '(' sort ')';


sort    :       sort_id
        ->      ^(SORT sort_id);


syntype :       syntype_id;


import_expression
        :       'IMPORT' '(' remote_variable_id (',' destination)? ')';


view_expression
        :       'VIEW' '(' view_id (',' pid_expression)? ')';


variable_access
        :       variable_id;


operator_application
        :       operator_id '('active_expression_list ')';


active_expression_list 
        :       active_expression (',' expression_list)?;/* |
                ground_expression ',' active_expression_list;*/   // Will not work (recursion)
/*
conditional_expression
        :       IF boolean_active_expression THEN consequence_expression ELSE alternative_expression FI |
                IF boolean_expression THEN active_consequence_expression ELSE alternative_expression FI |
                IF boolean_expression THEN consequence_expression ELSE active_alternative_expression FI;
*/


// Simpler version, the rest will is checked by semantic analysis
conditional_expression
        :       IF expression THEN expression ELSE expression FI;


synonym :       ID; // synonym_id | external_synonym;


external_synonym
        :       external_synonym_id;


conditional_ground_expression
        :       IF ifexpr=expression
                THEN thenexpr=expression
                ELSE elseexpr=expression FI
        ->      ^(IFTHENELSE $ifexpr $thenexpr $elseexpr);


expression_list 
        :       expression (',' expression)*
        ->      expression+;


terminator_statement
        :       label?
                cif?
                hyperlink?
                terminator
                end
        ->      ^(TERMINATOR label? cif? hyperlink? end? terminator);

label
        :       cif? connector_name ':'
        ->      ^(LABEL cif? connector_name);


terminator
        :       nextstate | join | stop | return_stmt;


join
        :        JOIN connector_name
        ->       ^(JOIN connector_name);


stop    :       STOP;


return_stmt
        :       RETURN expression?
        ->      ^(RETURN expression?);


nextstate
        :       NEXTSTATE nextstatebody
        ->      ^(NEXTSTATE nextstatebody);


nextstatebody
        :       statename via?
                | dash_nextstate;


via     :       VIA state_entry_point_name
        ->      ^(VIA state_entry_point_name);


end
        :   (cif? hyperlink? COMMENT StringLiteral)? SEMI
        -> ^(COMMENT cif? hyperlink? StringLiteral)?;


cif
        :       cif_decl symbolname
                L_PAREN x=INT COMMA y=INT R_PAREN
                COMMA
                L_PAREN width=INT COMMA height=INT R_PAREN 
                cif_end
        ->      ^(CIF $x $y $width $height);


hyperlink
        :       cif_decl KEEP SPECIFIC GEODE HYPERLINK StringLiteral
                cif_end
        ->      ^(HYPERLINK StringLiteral);

/* OpenGEODE specific: SDL does not allow specifying the name
   of signal parameters, but it is needed to generate function signatures
   when generating code (in particular in Ada, where the name in the 
   body must comply with the one of the source
   Extension is using CIF comment so it is invisible to other SDL parsers
   (This is valid SDL code - see ITU-T Z106)
*/
paramnames
        :       cif_decl KEEP SPECIFIC GEODE PARAMNAMES field_name+ cif_end
        ->      ^(PARAMNAMES field_name+);


/* OpenGEODE specific: Allow specifying the name of an ASN.1 file
   as a CIF extension linked to a USE clause.
   CIF Extensions are valid SDL constructs (ITU-T Z106)
*/
use_asn1
        :       cif_decl KEEP SPECIFIC GEODE ASNFILENAME StringLiteral cif_end
        ->      ^(ASN1 StringLiteral);


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
                | CONNECT;


cif_decl
        :       '/* CIF';


cif_end
        :       '*/';


cif_end_text
        :       cif_decl ENDTEXT cif_end
        ->      ^(ENDTEXT);

cif_end_label
        :       cif_decl END LABEL cif_end;


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
field_name      :       ID;
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
END             :       E N D;
KEEP            :       K E E P;
PARAMNAMES      :       P A R A M N A M E S;
SPECIFIC        :       S P E C I F I C;
GEODE           :       G E O D E;
HYPERLINK       :       H Y P E R L I N K;
ENDTEXT         :       E N D T E X T;
RETURN          :       R E T U R N;
TIMER           :       T I M E R;
PROCESS         :       P R O C E S S;
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
SET             :       S E T;
RESET           :       R E S E T;
ENDALTERNATIVE  :       E N D A L T E R N A T I V E;
ALTERNATIVE     :       A L T E R N A T I V E;
DECISION        :       D E C I S I O N;
ENDDECISION     :       E N D D E C I S I O N;
EXPORT          :       E X P O R T;
EXTERNAL        :       E X T E R N A L;
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
SUBSTRUCTURE    :       S U B S T R U C T U R E;
ENDSUBSTRUCTURE :       E N D S U B S T R U C T U R E;
FPAR            :       F P A R;
PARAM           :       P A R A M;
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
NULL            :       N U L L;
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

StringLiteral   :       STR+ ;

fragment
STR
        :       '\'' ( options {greedy=false;} : .)* '\''
        ;

ID
        :       ALPHA (ALPHA | DIGITS | '_')*;

fragment
ALPHA   :       ('a'..'z')|('A'..'Z');

INT     :       DASH? ( '0' | ('1'..'9') ('0'..'9')*);


fragment
DIGITS
        :       ('0'..'9')+;

FloatingPointLiteral
        :       INT DOT (DIGITS)? (Exponent)?
        |       INT
        ;

WS  :   (' ' | '\t' | '\r' | '\n')+ {$channel=HIDDEN;}
    ;
/*
COMMENT
    :   '//' ( options {greedy=false;} : . )* '//' {$channel=HIDDEN;}
    ;
*/

fragment
Exponent : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;


COMMENT2
        :        '--' ( options {greedy=false;} : . )* ('--'|'\r'?'\n')
                 {$channel=HIDDEN;};


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
