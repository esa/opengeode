# $ANTLR 3.1.3 Mar 17, 2009 19:23:44 sdl92.g 2014-07-13 22:58:34

import sys
from antlr3 import *
from antlr3.compat import set, frozenset

from antlr3.tree import *



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
NUMBER_OF_INSTANCES=59
COMMENT2=209
MANTISSA=166
ROUTE=79
MOD=158
GROUND=43
PARAM=64
NOT=160
SEQOF=81
TEXTAREA_CONTENT=102
EOF=-1
ACTION=4
CREATE=147
IMPORT=170
FPAR=42
NEXTSTATE=58
RETURN=78
THIS=148
CHANNEL=13
VIAPATH=112
ENDCONNECTION=125
EXPORT=31
EQ=141
INFORMAL_TEXT=48
GEODE=174
D=183
E=186
F=193
GE=146
G=194
A=180
IMPLIES=151
B=202
C=184
L=185
M=190
N=181
O=195
TERMINATOR=99
H=196
I=192
J=203
ELSE=26
K=187
U=199
T=197
W=201
V=200
STOP=90
Q=210
INT=123
P=188
S=191
R=189
VALUE=108
Y=182
X=198
FI=34
Z=211
MINUS_INFINITY=165
WS=208
OUT=131
NONE=132
INPUT_NONE=51
CONSTANT=21
GT=143
CALL=137
END=176
FLOATING_LABEL=40
IFTHENELSE=46
T__215=215
T__216=216
T__213=213
T__214=214
T__217=217
T__218=218
INPUT=50
ENDSUBSTRUCTURE=130
FLOAT=39
SUBSTRUCTURE=129
PAREN=67
ASTERISK=128
INOUT=49
STR=205
STIMULUS=89
THEN=103
ENDDECISION=139
OPEN_RANGE=61
SIGNAL=84
ENDSYSTEM=113
PLUS=154
CHOICE=14
T__212=212
TASK_BODY=98
PARAMS=66
CLOSED_RANGE=16
STATE=87
STATELIST=88
TO=105
ASSIG_OP=177
SIGNALROUTE=118
ENDSYNTYPE=29
SORT=86
SET=83
TEXT=100
SEMI=126
TEXTAREA=101
BLOCK=12
CIF=15
START=124
DECISION=24
DIV=157
PROCESS=73
STRING=91
INPUTLIST=52
EXTERNAL=33
LT=144
EXPONENT=168
TRANSITION=106
ENDBLOCK=117
RESET=77
ENDNEWTYPE=28
SIGNAL_LIST=85
ENDTEXT=30
CONNECTION=20
SYSTEM=96
CONNECT=19
PATH=68
L_PAREN=134
PROCEDURE_CALL=71
BASE=167
COMMENT=17
SYNONYM=93
ENDALTERNATIVE=138
ARRAY=8
ACTIVE=169
ENDFOR=150
FIELD_NAME=36
OCTSTR=60
VIEW=171
EMPTYSTR=27
ENDCHANNEL=114
NULL=163
ANSWER=7
PRIMARY=69
TASK=97
REFERENCED=120
ALPHA=206
SEQUENCE=82
VARIABLE=109
PRIORITY=133
SPECIFIC=173
OR=152
COMPOSITE_STATE=18
FIELD=35
USE=107
FROM=115
ENDPROCEDURE=122
FALSE=162
OUTPUT=62
SYNONYM_LIST=94
APPEND=156
L_BRACKET=178
DIGITS=25
HYPERLINK=44
NEWTYPE=57
Exponent=207
FOR=41
ENDSTATE=127
PROCEDURE_NAME=72
CONSTANTS=22
AND=119
ID=149
FLOAT2=38
IF=45
IN=47
PROVIDED=74
COMMA=136
ALL=5
ASNFILENAME=175
DOT=204
EXPRESSION=32
WITH=116
BITSTR=11
XOR=153
DASH=155
DCL=23
ENDPROCESS=121
RANGE=76
VIA=111
SAVE=80
LITERAL=55
STRUCT=92
FIELDS=37
REM=159
TRUE=161
PROCEDURE=70
JOIN=53
R_BRACKET=179
R_PAREN=135
OUTPUT_BODY=63
ANY=140
NEQ=142
QUESTION=75
LABEL=54
PARAMNAMES=65
PLUS_INFINITY=164
ASN1=9
KEEP=172
NEG=56
ASSIGN=10
VARIABLES=110
ALTERNATIVE=6
SYNTYPE=95
TIMER=104
LE=145

# token names
tokenNames = [
    "<invalid>", "<EOR>", "<DOWN>", "<UP>", 
    "ACTION", "ALL", "ALTERNATIVE", "ANSWER", "ARRAY", "ASN1", "ASSIGN", 
    "BITSTR", "BLOCK", "CHANNEL", "CHOICE", "CIF", "CLOSED_RANGE", "COMMENT", 
    "COMPOSITE_STATE", "CONNECT", "CONNECTION", "CONSTANT", "CONSTANTS", 
    "DCL", "DECISION", "DIGITS", "ELSE", "EMPTYSTR", "ENDNEWTYPE", "ENDSYNTYPE", 
    "ENDTEXT", "EXPORT", "EXPRESSION", "EXTERNAL", "FI", "FIELD", "FIELD_NAME", 
    "FIELDS", "FLOAT2", "FLOAT", "FLOATING_LABEL", "FOR", "FPAR", "GROUND", 
    "HYPERLINK", "IF", "IFTHENELSE", "IN", "INFORMAL_TEXT", "INOUT", "INPUT", 
    "INPUT_NONE", "INPUTLIST", "JOIN", "LABEL", "LITERAL", "NEG", "NEWTYPE", 
    "NEXTSTATE", "NUMBER_OF_INSTANCES", "OCTSTR", "OPEN_RANGE", "OUTPUT", 
    "OUTPUT_BODY", "PARAM", "PARAMNAMES", "PARAMS", "PAREN", "PATH", "PRIMARY", 
    "PROCEDURE", "PROCEDURE_CALL", "PROCEDURE_NAME", "PROCESS", "PROVIDED", 
    "QUESTION", "RANGE", "RESET", "RETURN", "ROUTE", "SAVE", "SEQOF", "SEQUENCE", 
    "SET", "SIGNAL", "SIGNAL_LIST", "SORT", "STATE", "STATELIST", "STIMULUS", 
    "STOP", "STRING", "STRUCT", "SYNONYM", "SYNONYM_LIST", "SYNTYPE", "SYSTEM", 
    "TASK", "TASK_BODY", "TERMINATOR", "TEXT", "TEXTAREA", "TEXTAREA_CONTENT", 
    "THEN", "TIMER", "TO", "TRANSITION", "USE", "VALUE", "VARIABLE", "VARIABLES", 
    "VIA", "VIAPATH", "ENDSYSTEM", "ENDCHANNEL", "FROM", "WITH", "ENDBLOCK", 
    "SIGNALROUTE", "AND", "REFERENCED", "ENDPROCESS", "ENDPROCEDURE", "INT", 
    "START", "ENDCONNECTION", "SEMI", "ENDSTATE", "ASTERISK", "SUBSTRUCTURE", 
    "ENDSUBSTRUCTURE", "OUT", "NONE", "PRIORITY", "L_PAREN", "R_PAREN", 
    "COMMA", "CALL", "ENDALTERNATIVE", "ENDDECISION", "ANY", "EQ", "NEQ", 
    "GT", "LT", "LE", "GE", "CREATE", "THIS", "ID", "ENDFOR", "IMPLIES", 
    "OR", "XOR", "PLUS", "DASH", "APPEND", "DIV", "MOD", "REM", "NOT", "TRUE", 
    "FALSE", "NULL", "PLUS_INFINITY", "MINUS_INFINITY", "MANTISSA", "BASE", 
    "EXPONENT", "ACTIVE", "IMPORT", "VIEW", "KEEP", "SPECIFIC", "GEODE", 
    "ASNFILENAME", "END", "ASSIG_OP", "L_BRACKET", "R_BRACKET", "A", "N", 
    "Y", "D", "C", "L", "E", "K", "P", "R", "M", "S", "I", "F", "G", "O", 
    "H", "T", "X", "U", "V", "W", "B", "J", "DOT", "STR", "ALPHA", "Exponent", 
    "WS", "COMMENT2", "Q", "Z", "':'", "'!'", "'(.'", "'.)'", "'ERROR'", 
    "'/* CIF'", "'*/'"
]




class sdl92Parser(Parser):
    grammarFileName = "sdl92.g"
    antlr_version = version_str_to_tuple("3.1.3 Mar 17, 2009 19:23:44")
    antlr_version_str = "3.1.3 Mar 17, 2009 19:23:44"
    tokenNames = tokenNames

    def __init__(self, input, state=None, *args, **kwargs):
        if state is None:
            state = RecognizerSharedState()

        super(sdl92Parser, self).__init__(input, state, *args, **kwargs)

        self.dfa19 = self.DFA19(
            self, 19,
            eot = self.DFA19_eot,
            eof = self.DFA19_eof,
            min = self.DFA19_min,
            max = self.DFA19_max,
            accept = self.DFA19_accept,
            special = self.DFA19_special,
            transition = self.DFA19_transition
            )

        self.dfa30 = self.DFA30(
            self, 30,
            eot = self.DFA30_eot,
            eof = self.DFA30_eof,
            min = self.DFA30_min,
            max = self.DFA30_max,
            accept = self.DFA30_accept,
            special = self.DFA30_special,
            transition = self.DFA30_transition
            )

        self.dfa37 = self.DFA37(
            self, 37,
            eot = self.DFA37_eot,
            eof = self.DFA37_eof,
            min = self.DFA37_min,
            max = self.DFA37_max,
            accept = self.DFA37_accept,
            special = self.DFA37_special,
            transition = self.DFA37_transition
            )

        self.dfa43 = self.DFA43(
            self, 43,
            eot = self.DFA43_eot,
            eof = self.DFA43_eof,
            min = self.DFA43_min,
            max = self.DFA43_max,
            accept = self.DFA43_accept,
            special = self.DFA43_special,
            transition = self.DFA43_transition
            )

        self.dfa44 = self.DFA44(
            self, 44,
            eot = self.DFA44_eot,
            eof = self.DFA44_eof,
            min = self.DFA44_min,
            max = self.DFA44_max,
            accept = self.DFA44_accept,
            special = self.DFA44_special,
            transition = self.DFA44_transition
            )

        self.dfa48 = self.DFA48(
            self, 48,
            eot = self.DFA48_eot,
            eof = self.DFA48_eof,
            min = self.DFA48_min,
            max = self.DFA48_max,
            accept = self.DFA48_accept,
            special = self.DFA48_special,
            transition = self.DFA48_transition
            )

        self.dfa66 = self.DFA66(
            self, 66,
            eot = self.DFA66_eot,
            eof = self.DFA66_eof,
            min = self.DFA66_min,
            max = self.DFA66_max,
            accept = self.DFA66_accept,
            special = self.DFA66_special,
            transition = self.DFA66_transition
            )

        self.dfa67 = self.DFA67(
            self, 67,
            eot = self.DFA67_eot,
            eof = self.DFA67_eof,
            min = self.DFA67_min,
            max = self.DFA67_max,
            accept = self.DFA67_accept,
            special = self.DFA67_special,
            transition = self.DFA67_transition
            )

        self.dfa68 = self.DFA68(
            self, 68,
            eot = self.DFA68_eot,
            eof = self.DFA68_eof,
            min = self.DFA68_min,
            max = self.DFA68_max,
            accept = self.DFA68_accept,
            special = self.DFA68_special,
            transition = self.DFA68_transition
            )

        self.dfa72 = self.DFA72(
            self, 72,
            eot = self.DFA72_eot,
            eof = self.DFA72_eof,
            min = self.DFA72_min,
            max = self.DFA72_max,
            accept = self.DFA72_accept,
            special = self.DFA72_special,
            transition = self.DFA72_transition
            )

        self.dfa83 = self.DFA83(
            self, 83,
            eot = self.DFA83_eot,
            eof = self.DFA83_eof,
            min = self.DFA83_min,
            max = self.DFA83_max,
            accept = self.DFA83_accept,
            special = self.DFA83_special,
            transition = self.DFA83_transition
            )

        self.dfa84 = self.DFA84(
            self, 84,
            eot = self.DFA84_eot,
            eof = self.DFA84_eof,
            min = self.DFA84_min,
            max = self.DFA84_max,
            accept = self.DFA84_accept,
            special = self.DFA84_special,
            transition = self.DFA84_transition
            )

        self.dfa92 = self.DFA92(
            self, 92,
            eot = self.DFA92_eot,
            eof = self.DFA92_eof,
            min = self.DFA92_min,
            max = self.DFA92_max,
            accept = self.DFA92_accept,
            special = self.DFA92_special,
            transition = self.DFA92_transition
            )

        self.dfa89 = self.DFA89(
            self, 89,
            eot = self.DFA89_eot,
            eof = self.DFA89_eof,
            min = self.DFA89_min,
            max = self.DFA89_max,
            accept = self.DFA89_accept,
            special = self.DFA89_special,
            transition = self.DFA89_transition
            )

        self.dfa90 = self.DFA90(
            self, 90,
            eot = self.DFA90_eot,
            eof = self.DFA90_eof,
            min = self.DFA90_min,
            max = self.DFA90_max,
            accept = self.DFA90_accept,
            special = self.DFA90_special,
            transition = self.DFA90_transition
            )

        self.dfa91 = self.DFA91(
            self, 91,
            eot = self.DFA91_eot,
            eof = self.DFA91_eof,
            min = self.DFA91_min,
            max = self.DFA91_max,
            accept = self.DFA91_accept,
            special = self.DFA91_special,
            transition = self.DFA91_transition
            )

        self.dfa93 = self.DFA93(
            self, 93,
            eot = self.DFA93_eot,
            eof = self.DFA93_eof,
            min = self.DFA93_min,
            max = self.DFA93_max,
            accept = self.DFA93_accept,
            special = self.DFA93_special,
            transition = self.DFA93_transition
            )

        self.dfa94 = self.DFA94(
            self, 94,
            eot = self.DFA94_eot,
            eof = self.DFA94_eof,
            min = self.DFA94_min,
            max = self.DFA94_max,
            accept = self.DFA94_accept,
            special = self.DFA94_special,
            transition = self.DFA94_transition
            )

        self.dfa105 = self.DFA105(
            self, 105,
            eot = self.DFA105_eot,
            eof = self.DFA105_eof,
            min = self.DFA105_min,
            max = self.DFA105_max,
            accept = self.DFA105_accept,
            special = self.DFA105_special,
            transition = self.DFA105_transition
            )

        self.dfa103 = self.DFA103(
            self, 103,
            eot = self.DFA103_eot,
            eof = self.DFA103_eof,
            min = self.DFA103_min,
            max = self.DFA103_max,
            accept = self.DFA103_accept,
            special = self.DFA103_special,
            transition = self.DFA103_transition
            )

        self.dfa113 = self.DFA113(
            self, 113,
            eot = self.DFA113_eot,
            eof = self.DFA113_eof,
            min = self.DFA113_min,
            max = self.DFA113_max,
            accept = self.DFA113_accept,
            special = self.DFA113_special,
            transition = self.DFA113_transition
            )

        self.dfa153 = self.DFA153(
            self, 153,
            eot = self.DFA153_eot,
            eof = self.DFA153_eof,
            min = self.DFA153_min,
            max = self.DFA153_max,
            accept = self.DFA153_accept,
            special = self.DFA153_special,
            transition = self.DFA153_transition
            )

        self.dfa163 = self.DFA163(
            self, 163,
            eot = self.DFA163_eot,
            eof = self.DFA163_eof,
            min = self.DFA163_min,
            max = self.DFA163_max,
            accept = self.DFA163_accept,
            special = self.DFA163_special,
            transition = self.DFA163_transition
            )

        self.dfa160 = self.DFA160(
            self, 160,
            eot = self.DFA160_eot,
            eof = self.DFA160_eof,
            min = self.DFA160_min,
            max = self.DFA160_max,
            accept = self.DFA160_accept,
            special = self.DFA160_special,
            transition = self.DFA160_transition
            )

        self.dfa172 = self.DFA172(
            self, 172,
            eot = self.DFA172_eot,
            eof = self.DFA172_eof,
            min = self.DFA172_min,
            max = self.DFA172_max,
            accept = self.DFA172_accept,
            special = self.DFA172_special,
            transition = self.DFA172_transition
            )






        self._adaptor = None
        self.adaptor = CommonTreeAdaptor()
                


        
    def getTreeAdaptor(self):
        return self._adaptor

    def setTreeAdaptor(self, adaptor):
        self._adaptor = adaptor

    adaptor = property(getTreeAdaptor, setTreeAdaptor)


    class pr_file_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.pr_file_return, self).__init__()

            self.tree = None




    # $ANTLR start "pr_file"
    # sdl92.g:137:1: pr_file : ( use_clause | system_definition | process_definition )+ ;
    def pr_file(self, ):

        retval = self.pr_file_return()
        retval.start = self.input.LT(1)

        root_0 = None

        use_clause1 = None

        system_definition2 = None

        process_definition3 = None



        try:
            try:
                # sdl92.g:138:9: ( ( use_clause | system_definition | process_definition )+ )
                # sdl92.g:138:17: ( use_clause | system_definition | process_definition )+
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:138:17: ( use_clause | system_definition | process_definition )+
                cnt1 = 0
                while True: #loop1
                    alt1 = 4
                    LA1 = self.input.LA(1)
                    if LA1 == 217:
                        LA1_2 = self.input.LA(2)

                        if (LA1_2 == ANSWER or LA1_2 == COMMENT or LA1_2 == CONNECT or LA1_2 == DECISION or LA1_2 == INPUT or (JOIN <= LA1_2 <= LABEL) or LA1_2 == NEXTSTATE or LA1_2 == OUTPUT or (PROCEDURE <= LA1_2 <= PROCEDURE_CALL) or (PROCESS <= LA1_2 <= PROVIDED) or LA1_2 == RETURN or LA1_2 == STATE or LA1_2 == STOP or LA1_2 == TASK or LA1_2 == TEXT or LA1_2 == START) :
                            alt1 = 3
                        elif (LA1_2 == KEEP) :
                            alt1 = 1


                    elif LA1 == USE:
                        alt1 = 1
                    elif LA1 == SYSTEM:
                        alt1 = 2
                    elif LA1 == PROCESS:
                        alt1 = 3

                    if alt1 == 1:
                        # sdl92.g:138:18: use_clause
                        pass 
                        self._state.following.append(self.FOLLOW_use_clause_in_pr_file1277)
                        use_clause1 = self.use_clause()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, use_clause1.tree)


                    elif alt1 == 2:
                        # sdl92.g:139:19: system_definition
                        pass 
                        self._state.following.append(self.FOLLOW_system_definition_in_pr_file1297)
                        system_definition2 = self.system_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, system_definition2.tree)


                    elif alt1 == 3:
                        # sdl92.g:140:19: process_definition
                        pass 
                        self._state.following.append(self.FOLLOW_process_definition_in_pr_file1317)
                        process_definition3 = self.process_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, process_definition3.tree)


                    else:
                        if cnt1 >= 1:
                            break #loop1

                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        eee = EarlyExitException(1, self.input)
                        raise eee

                    cnt1 += 1



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "pr_file"

    class system_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.system_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "system_definition"
    # sdl92.g:143:1: system_definition : SYSTEM system_name end ( entity_in_system )* ENDSYSTEM ( system_name )? end -> ^( SYSTEM system_name ( entity_in_system )* ) ;
    def system_definition(self, ):

        retval = self.system_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SYSTEM4 = None
        ENDSYSTEM8 = None
        system_name5 = None

        end6 = None

        entity_in_system7 = None

        system_name9 = None

        end10 = None


        SYSTEM4_tree = None
        ENDSYSTEM8_tree = None
        stream_ENDSYSTEM = RewriteRuleTokenStream(self._adaptor, "token ENDSYSTEM")
        stream_SYSTEM = RewriteRuleTokenStream(self._adaptor, "token SYSTEM")
        stream_entity_in_system = RewriteRuleSubtreeStream(self._adaptor, "rule entity_in_system")
        stream_system_name = RewriteRuleSubtreeStream(self._adaptor, "rule system_name")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:144:9: ( SYSTEM system_name end ( entity_in_system )* ENDSYSTEM ( system_name )? end -> ^( SYSTEM system_name ( entity_in_system )* ) )
                # sdl92.g:144:17: SYSTEM system_name end ( entity_in_system )* ENDSYSTEM ( system_name )? end
                pass 
                SYSTEM4=self.match(self.input, SYSTEM, self.FOLLOW_SYSTEM_in_system_definition1342) 
                if self._state.backtracking == 0:
                    stream_SYSTEM.add(SYSTEM4)
                self._state.following.append(self.FOLLOW_system_name_in_system_definition1344)
                system_name5 = self.system_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_system_name.add(system_name5.tree)
                self._state.following.append(self.FOLLOW_end_in_system_definition1346)
                end6 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end6.tree)
                # sdl92.g:145:17: ( entity_in_system )*
                while True: #loop2
                    alt2 = 2
                    LA2_0 = self.input.LA(1)

                    if ((BLOCK <= LA2_0 <= CHANNEL) or LA2_0 == PROCEDURE or LA2_0 == SIGNAL or LA2_0 == 217) :
                        alt2 = 1


                    if alt2 == 1:
                        # sdl92.g:0:0: entity_in_system
                        pass 
                        self._state.following.append(self.FOLLOW_entity_in_system_in_system_definition1364)
                        entity_in_system7 = self.entity_in_system()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_entity_in_system.add(entity_in_system7.tree)


                    else:
                        break #loop2
                ENDSYSTEM8=self.match(self.input, ENDSYSTEM, self.FOLLOW_ENDSYSTEM_in_system_definition1383) 
                if self._state.backtracking == 0:
                    stream_ENDSYSTEM.add(ENDSYSTEM8)
                # sdl92.g:146:27: ( system_name )?
                alt3 = 2
                LA3_0 = self.input.LA(1)

                if (LA3_0 == ID) :
                    alt3 = 1
                if alt3 == 1:
                    # sdl92.g:0:0: system_name
                    pass 
                    self._state.following.append(self.FOLLOW_system_name_in_system_definition1385)
                    system_name9 = self.system_name()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_system_name.add(system_name9.tree)



                self._state.following.append(self.FOLLOW_end_in_system_definition1388)
                end10 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end10.tree)

                # AST Rewrite
                # elements: entity_in_system, system_name, SYSTEM
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 147:9: -> ^( SYSTEM system_name ( entity_in_system )* )
                    # sdl92.g:147:17: ^( SYSTEM system_name ( entity_in_system )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_SYSTEM.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_system_name.nextTree())
                    # sdl92.g:147:38: ( entity_in_system )*
                    while stream_entity_in_system.hasNext():
                        self._adaptor.addChild(root_1, stream_entity_in_system.nextTree())


                    stream_entity_in_system.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "system_definition"

    class use_clause_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.use_clause_return, self).__init__()

            self.tree = None




    # $ANTLR start "use_clause"
    # sdl92.g:150:1: use_clause : ( use_asn1 )? USE package_name end -> ^( USE ( use_asn1 )? package_name ) ;
    def use_clause(self, ):

        retval = self.use_clause_return()
        retval.start = self.input.LT(1)

        root_0 = None

        USE12 = None
        use_asn111 = None

        package_name13 = None

        end14 = None


        USE12_tree = None
        stream_USE = RewriteRuleTokenStream(self._adaptor, "token USE")
        stream_use_asn1 = RewriteRuleSubtreeStream(self._adaptor, "rule use_asn1")
        stream_package_name = RewriteRuleSubtreeStream(self._adaptor, "rule package_name")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:151:9: ( ( use_asn1 )? USE package_name end -> ^( USE ( use_asn1 )? package_name ) )
                # sdl92.g:151:17: ( use_asn1 )? USE package_name end
                pass 
                # sdl92.g:151:17: ( use_asn1 )?
                alt4 = 2
                LA4_0 = self.input.LA(1)

                if (LA4_0 == 217) :
                    alt4 = 1
                if alt4 == 1:
                    # sdl92.g:0:0: use_asn1
                    pass 
                    self._state.following.append(self.FOLLOW_use_asn1_in_use_clause1435)
                    use_asn111 = self.use_asn1()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_use_asn1.add(use_asn111.tree)



                USE12=self.match(self.input, USE, self.FOLLOW_USE_in_use_clause1454) 
                if self._state.backtracking == 0:
                    stream_USE.add(USE12)
                self._state.following.append(self.FOLLOW_package_name_in_use_clause1456)
                package_name13 = self.package_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_package_name.add(package_name13.tree)
                self._state.following.append(self.FOLLOW_end_in_use_clause1458)
                end14 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end14.tree)

                # AST Rewrite
                # elements: package_name, USE, use_asn1
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 153:9: -> ^( USE ( use_asn1 )? package_name )
                    # sdl92.g:153:17: ^( USE ( use_asn1 )? package_name )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_USE.nextNode(), root_1)

                    # sdl92.g:153:23: ( use_asn1 )?
                    if stream_use_asn1.hasNext():
                        self._adaptor.addChild(root_1, stream_use_asn1.nextTree())


                    stream_use_asn1.reset();
                    self._adaptor.addChild(root_1, stream_package_name.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "use_clause"

    class entity_in_system_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.entity_in_system_return, self).__init__()

            self.tree = None




    # $ANTLR start "entity_in_system"
    # sdl92.g:159:1: entity_in_system : ( signal_declaration | procedure | channel | block_definition );
    def entity_in_system(self, ):

        retval = self.entity_in_system_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_declaration15 = None

        procedure16 = None

        channel17 = None

        block_definition18 = None



        try:
            try:
                # sdl92.g:160:9: ( signal_declaration | procedure | channel | block_definition )
                alt5 = 4
                LA5 = self.input.LA(1)
                if LA5 == 217:
                    LA5_1 = self.input.LA(2)

                    if (LA5_1 == KEEP) :
                        alt5 = 1
                    elif (LA5_1 == ANSWER or LA5_1 == COMMENT or LA5_1 == CONNECT or LA5_1 == DECISION or LA5_1 == INPUT or (JOIN <= LA5_1 <= LABEL) or LA5_1 == NEXTSTATE or LA5_1 == OUTPUT or (PROCEDURE <= LA5_1 <= PROCEDURE_CALL) or (PROCESS <= LA5_1 <= PROVIDED) or LA5_1 == RETURN or LA5_1 == STATE or LA5_1 == STOP or LA5_1 == TASK or LA5_1 == TEXT or LA5_1 == START) :
                        alt5 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 5, 1, self.input)

                        raise nvae

                elif LA5 == SIGNAL:
                    alt5 = 1
                elif LA5 == PROCEDURE:
                    alt5 = 2
                elif LA5 == CHANNEL:
                    alt5 = 3
                elif LA5 == BLOCK:
                    alt5 = 4
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 5, 0, self.input)

                    raise nvae

                if alt5 == 1:
                    # sdl92.g:160:17: signal_declaration
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_signal_declaration_in_entity_in_system1507)
                    signal_declaration15 = self.signal_declaration()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, signal_declaration15.tree)


                elif alt5 == 2:
                    # sdl92.g:161:19: procedure
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_procedure_in_entity_in_system1527)
                    procedure16 = self.procedure()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, procedure16.tree)


                elif alt5 == 3:
                    # sdl92.g:162:19: channel
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_channel_in_entity_in_system1547)
                    channel17 = self.channel()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, channel17.tree)


                elif alt5 == 4:
                    # sdl92.g:163:19: block_definition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_block_definition_in_entity_in_system1567)
                    block_definition18 = self.block_definition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, block_definition18.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "entity_in_system"

    class signal_declaration_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_declaration_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_declaration"
    # sdl92.g:168:1: signal_declaration : ( paramnames )? SIGNAL signal_id ( input_params )? end -> ^( SIGNAL ( paramnames )? signal_id ( input_params )? ) ;
    def signal_declaration(self, ):

        retval = self.signal_declaration_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SIGNAL20 = None
        paramnames19 = None

        signal_id21 = None

        input_params22 = None

        end23 = None


        SIGNAL20_tree = None
        stream_SIGNAL = RewriteRuleTokenStream(self._adaptor, "token SIGNAL")
        stream_input_params = RewriteRuleSubtreeStream(self._adaptor, "rule input_params")
        stream_paramnames = RewriteRuleSubtreeStream(self._adaptor, "rule paramnames")
        stream_signal_id = RewriteRuleSubtreeStream(self._adaptor, "rule signal_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:169:9: ( ( paramnames )? SIGNAL signal_id ( input_params )? end -> ^( SIGNAL ( paramnames )? signal_id ( input_params )? ) )
                # sdl92.g:169:17: ( paramnames )? SIGNAL signal_id ( input_params )? end
                pass 
                # sdl92.g:169:17: ( paramnames )?
                alt6 = 2
                LA6_0 = self.input.LA(1)

                if (LA6_0 == 217) :
                    alt6 = 1
                if alt6 == 1:
                    # sdl92.g:0:0: paramnames
                    pass 
                    self._state.following.append(self.FOLLOW_paramnames_in_signal_declaration1591)
                    paramnames19 = self.paramnames()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_paramnames.add(paramnames19.tree)



                SIGNAL20=self.match(self.input, SIGNAL, self.FOLLOW_SIGNAL_in_signal_declaration1610) 
                if self._state.backtracking == 0:
                    stream_SIGNAL.add(SIGNAL20)
                self._state.following.append(self.FOLLOW_signal_id_in_signal_declaration1612)
                signal_id21 = self.signal_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_signal_id.add(signal_id21.tree)
                # sdl92.g:170:34: ( input_params )?
                alt7 = 2
                LA7_0 = self.input.LA(1)

                if (LA7_0 == L_PAREN) :
                    alt7 = 1
                if alt7 == 1:
                    # sdl92.g:0:0: input_params
                    pass 
                    self._state.following.append(self.FOLLOW_input_params_in_signal_declaration1614)
                    input_params22 = self.input_params()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_input_params.add(input_params22.tree)



                self._state.following.append(self.FOLLOW_end_in_signal_declaration1617)
                end23 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end23.tree)

                # AST Rewrite
                # elements: signal_id, SIGNAL, input_params, paramnames
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 171:9: -> ^( SIGNAL ( paramnames )? signal_id ( input_params )? )
                    # sdl92.g:171:17: ^( SIGNAL ( paramnames )? signal_id ( input_params )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_SIGNAL.nextNode(), root_1)

                    # sdl92.g:171:26: ( paramnames )?
                    if stream_paramnames.hasNext():
                        self._adaptor.addChild(root_1, stream_paramnames.nextTree())


                    stream_paramnames.reset();
                    self._adaptor.addChild(root_1, stream_signal_id.nextTree())
                    # sdl92.g:171:48: ( input_params )?
                    if stream_input_params.hasNext():
                        self._adaptor.addChild(root_1, stream_input_params.nextTree())


                    stream_input_params.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_declaration"

    class channel_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.channel_return, self).__init__()

            self.tree = None




    # $ANTLR start "channel"
    # sdl92.g:174:1: channel : CHANNEL channel_id ( route )+ ENDCHANNEL end -> ^( CHANNEL channel_id ( route )+ ) ;
    def channel(self, ):

        retval = self.channel_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CHANNEL24 = None
        ENDCHANNEL27 = None
        channel_id25 = None

        route26 = None

        end28 = None


        CHANNEL24_tree = None
        ENDCHANNEL27_tree = None
        stream_CHANNEL = RewriteRuleTokenStream(self._adaptor, "token CHANNEL")
        stream_ENDCHANNEL = RewriteRuleTokenStream(self._adaptor, "token ENDCHANNEL")
        stream_route = RewriteRuleSubtreeStream(self._adaptor, "rule route")
        stream_channel_id = RewriteRuleSubtreeStream(self._adaptor, "rule channel_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:175:9: ( CHANNEL channel_id ( route )+ ENDCHANNEL end -> ^( CHANNEL channel_id ( route )+ ) )
                # sdl92.g:175:17: CHANNEL channel_id ( route )+ ENDCHANNEL end
                pass 
                CHANNEL24=self.match(self.input, CHANNEL, self.FOLLOW_CHANNEL_in_channel1667) 
                if self._state.backtracking == 0:
                    stream_CHANNEL.add(CHANNEL24)
                self._state.following.append(self.FOLLOW_channel_id_in_channel1669)
                channel_id25 = self.channel_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_channel_id.add(channel_id25.tree)
                # sdl92.g:176:17: ( route )+
                cnt8 = 0
                while True: #loop8
                    alt8 = 2
                    LA8_0 = self.input.LA(1)

                    if (LA8_0 == FROM) :
                        alt8 = 1


                    if alt8 == 1:
                        # sdl92.g:0:0: route
                        pass 
                        self._state.following.append(self.FOLLOW_route_in_channel1687)
                        route26 = self.route()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_route.add(route26.tree)


                    else:
                        if cnt8 >= 1:
                            break #loop8

                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        eee = EarlyExitException(8, self.input)
                        raise eee

                    cnt8 += 1
                ENDCHANNEL27=self.match(self.input, ENDCHANNEL, self.FOLLOW_ENDCHANNEL_in_channel1706) 
                if self._state.backtracking == 0:
                    stream_ENDCHANNEL.add(ENDCHANNEL27)
                self._state.following.append(self.FOLLOW_end_in_channel1708)
                end28 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end28.tree)

                # AST Rewrite
                # elements: channel_id, CHANNEL, route
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 178:9: -> ^( CHANNEL channel_id ( route )+ )
                    # sdl92.g:178:17: ^( CHANNEL channel_id ( route )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_CHANNEL.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_channel_id.nextTree())
                    # sdl92.g:178:38: ( route )+
                    if not (stream_route.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_route.hasNext():
                        self._adaptor.addChild(root_1, stream_route.nextTree())


                    stream_route.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "channel"

    class route_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.route_return, self).__init__()

            self.tree = None




    # $ANTLR start "route"
    # sdl92.g:181:1: route : FROM source_id TO dest_id WITH signal_id ( ',' signal_id )* end -> ^( ROUTE source_id dest_id ( signal_id )+ ) ;
    def route(self, ):

        retval = self.route_return()
        retval.start = self.input.LT(1)

        root_0 = None

        FROM29 = None
        TO31 = None
        WITH33 = None
        char_literal35 = None
        source_id30 = None

        dest_id32 = None

        signal_id34 = None

        signal_id36 = None

        end37 = None


        FROM29_tree = None
        TO31_tree = None
        WITH33_tree = None
        char_literal35_tree = None
        stream_FROM = RewriteRuleTokenStream(self._adaptor, "token FROM")
        stream_TO = RewriteRuleTokenStream(self._adaptor, "token TO")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_WITH = RewriteRuleTokenStream(self._adaptor, "token WITH")
        stream_source_id = RewriteRuleSubtreeStream(self._adaptor, "rule source_id")
        stream_dest_id = RewriteRuleSubtreeStream(self._adaptor, "rule dest_id")
        stream_signal_id = RewriteRuleSubtreeStream(self._adaptor, "rule signal_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:182:9: ( FROM source_id TO dest_id WITH signal_id ( ',' signal_id )* end -> ^( ROUTE source_id dest_id ( signal_id )+ ) )
                # sdl92.g:182:17: FROM source_id TO dest_id WITH signal_id ( ',' signal_id )* end
                pass 
                FROM29=self.match(self.input, FROM, self.FOLLOW_FROM_in_route1755) 
                if self._state.backtracking == 0:
                    stream_FROM.add(FROM29)
                self._state.following.append(self.FOLLOW_source_id_in_route1757)
                source_id30 = self.source_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_source_id.add(source_id30.tree)
                TO31=self.match(self.input, TO, self.FOLLOW_TO_in_route1759) 
                if self._state.backtracking == 0:
                    stream_TO.add(TO31)
                self._state.following.append(self.FOLLOW_dest_id_in_route1761)
                dest_id32 = self.dest_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_dest_id.add(dest_id32.tree)
                WITH33=self.match(self.input, WITH, self.FOLLOW_WITH_in_route1763) 
                if self._state.backtracking == 0:
                    stream_WITH.add(WITH33)
                self._state.following.append(self.FOLLOW_signal_id_in_route1765)
                signal_id34 = self.signal_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_signal_id.add(signal_id34.tree)
                # sdl92.g:182:58: ( ',' signal_id )*
                while True: #loop9
                    alt9 = 2
                    LA9_0 = self.input.LA(1)

                    if (LA9_0 == COMMA) :
                        alt9 = 1


                    if alt9 == 1:
                        # sdl92.g:182:59: ',' signal_id
                        pass 
                        char_literal35=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_route1768) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal35)
                        self._state.following.append(self.FOLLOW_signal_id_in_route1770)
                        signal_id36 = self.signal_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_signal_id.add(signal_id36.tree)


                    else:
                        break #loop9
                self._state.following.append(self.FOLLOW_end_in_route1774)
                end37 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end37.tree)

                # AST Rewrite
                # elements: dest_id, source_id, signal_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 183:9: -> ^( ROUTE source_id dest_id ( signal_id )+ )
                    # sdl92.g:183:17: ^( ROUTE source_id dest_id ( signal_id )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ROUTE, "ROUTE"), root_1)

                    self._adaptor.addChild(root_1, stream_source_id.nextTree())
                    self._adaptor.addChild(root_1, stream_dest_id.nextTree())
                    # sdl92.g:183:43: ( signal_id )+
                    if not (stream_signal_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_signal_id.hasNext():
                        self._adaptor.addChild(root_1, stream_signal_id.nextTree())


                    stream_signal_id.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "route"

    class block_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.block_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "block_definition"
    # sdl92.g:186:1: block_definition : BLOCK block_id end ( entity_in_block )* ENDBLOCK end -> ^( BLOCK block_id ( entity_in_block )* ) ;
    def block_definition(self, ):

        retval = self.block_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        BLOCK38 = None
        ENDBLOCK42 = None
        block_id39 = None

        end40 = None

        entity_in_block41 = None

        end43 = None


        BLOCK38_tree = None
        ENDBLOCK42_tree = None
        stream_ENDBLOCK = RewriteRuleTokenStream(self._adaptor, "token ENDBLOCK")
        stream_BLOCK = RewriteRuleTokenStream(self._adaptor, "token BLOCK")
        stream_entity_in_block = RewriteRuleSubtreeStream(self._adaptor, "rule entity_in_block")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        stream_block_id = RewriteRuleSubtreeStream(self._adaptor, "rule block_id")
        try:
            try:
                # sdl92.g:187:9: ( BLOCK block_id end ( entity_in_block )* ENDBLOCK end -> ^( BLOCK block_id ( entity_in_block )* ) )
                # sdl92.g:187:17: BLOCK block_id end ( entity_in_block )* ENDBLOCK end
                pass 
                BLOCK38=self.match(self.input, BLOCK, self.FOLLOW_BLOCK_in_block_definition1823) 
                if self._state.backtracking == 0:
                    stream_BLOCK.add(BLOCK38)
                self._state.following.append(self.FOLLOW_block_id_in_block_definition1825)
                block_id39 = self.block_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_block_id.add(block_id39.tree)
                self._state.following.append(self.FOLLOW_end_in_block_definition1827)
                end40 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end40.tree)
                # sdl92.g:188:17: ( entity_in_block )*
                while True: #loop10
                    alt10 = 2
                    LA10_0 = self.input.LA(1)

                    if (LA10_0 == BLOCK or LA10_0 == CONNECT or LA10_0 == PROCESS or LA10_0 == SIGNAL or LA10_0 == SIGNALROUTE or LA10_0 == 217) :
                        alt10 = 1


                    if alt10 == 1:
                        # sdl92.g:0:0: entity_in_block
                        pass 
                        self._state.following.append(self.FOLLOW_entity_in_block_in_block_definition1845)
                        entity_in_block41 = self.entity_in_block()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_entity_in_block.add(entity_in_block41.tree)


                    else:
                        break #loop10
                ENDBLOCK42=self.match(self.input, ENDBLOCK, self.FOLLOW_ENDBLOCK_in_block_definition1864) 
                if self._state.backtracking == 0:
                    stream_ENDBLOCK.add(ENDBLOCK42)
                self._state.following.append(self.FOLLOW_end_in_block_definition1866)
                end43 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end43.tree)

                # AST Rewrite
                # elements: block_id, entity_in_block, BLOCK
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 190:9: -> ^( BLOCK block_id ( entity_in_block )* )
                    # sdl92.g:190:17: ^( BLOCK block_id ( entity_in_block )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_BLOCK.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_block_id.nextTree())
                    # sdl92.g:190:34: ( entity_in_block )*
                    while stream_entity_in_block.hasNext():
                        self._adaptor.addChild(root_1, stream_entity_in_block.nextTree())


                    stream_entity_in_block.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "block_definition"

    class entity_in_block_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.entity_in_block_return, self).__init__()

            self.tree = None




    # $ANTLR start "entity_in_block"
    # sdl92.g:197:1: entity_in_block : ( signal_declaration | signalroute | connection | block_definition | process_definition );
    def entity_in_block(self, ):

        retval = self.entity_in_block_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_declaration44 = None

        signalroute45 = None

        connection46 = None

        block_definition47 = None

        process_definition48 = None



        try:
            try:
                # sdl92.g:198:9: ( signal_declaration | signalroute | connection | block_definition | process_definition )
                alt11 = 5
                LA11 = self.input.LA(1)
                if LA11 == 217:
                    LA11_1 = self.input.LA(2)

                    if (LA11_1 == KEEP) :
                        alt11 = 1
                    elif (LA11_1 == ANSWER or LA11_1 == COMMENT or LA11_1 == CONNECT or LA11_1 == DECISION or LA11_1 == INPUT or (JOIN <= LA11_1 <= LABEL) or LA11_1 == NEXTSTATE or LA11_1 == OUTPUT or (PROCEDURE <= LA11_1 <= PROCEDURE_CALL) or (PROCESS <= LA11_1 <= PROVIDED) or LA11_1 == RETURN or LA11_1 == STATE or LA11_1 == STOP or LA11_1 == TASK or LA11_1 == TEXT or LA11_1 == START) :
                        alt11 = 5
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 11, 1, self.input)

                        raise nvae

                elif LA11 == SIGNAL:
                    alt11 = 1
                elif LA11 == SIGNALROUTE:
                    alt11 = 2
                elif LA11 == CONNECT:
                    alt11 = 3
                elif LA11 == BLOCK:
                    alt11 = 4
                elif LA11 == PROCESS:
                    alt11 = 5
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 11, 0, self.input)

                    raise nvae

                if alt11 == 1:
                    # sdl92.g:198:17: signal_declaration
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_signal_declaration_in_entity_in_block1915)
                    signal_declaration44 = self.signal_declaration()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, signal_declaration44.tree)


                elif alt11 == 2:
                    # sdl92.g:199:19: signalroute
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_signalroute_in_entity_in_block1935)
                    signalroute45 = self.signalroute()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, signalroute45.tree)


                elif alt11 == 3:
                    # sdl92.g:200:19: connection
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_connection_in_entity_in_block1955)
                    connection46 = self.connection()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, connection46.tree)


                elif alt11 == 4:
                    # sdl92.g:201:19: block_definition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_block_definition_in_entity_in_block1975)
                    block_definition47 = self.block_definition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, block_definition47.tree)


                elif alt11 == 5:
                    # sdl92.g:202:19: process_definition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_process_definition_in_entity_in_block1995)
                    process_definition48 = self.process_definition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, process_definition48.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "entity_in_block"

    class signalroute_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signalroute_return, self).__init__()

            self.tree = None




    # $ANTLR start "signalroute"
    # sdl92.g:205:1: signalroute : SIGNALROUTE route_id ( route )+ -> ^( SIGNALROUTE route_id ( route )+ ) ;
    def signalroute(self, ):

        retval = self.signalroute_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SIGNALROUTE49 = None
        route_id50 = None

        route51 = None


        SIGNALROUTE49_tree = None
        stream_SIGNALROUTE = RewriteRuleTokenStream(self._adaptor, "token SIGNALROUTE")
        stream_route_id = RewriteRuleSubtreeStream(self._adaptor, "rule route_id")
        stream_route = RewriteRuleSubtreeStream(self._adaptor, "rule route")
        try:
            try:
                # sdl92.g:206:9: ( SIGNALROUTE route_id ( route )+ -> ^( SIGNALROUTE route_id ( route )+ ) )
                # sdl92.g:206:17: SIGNALROUTE route_id ( route )+
                pass 
                SIGNALROUTE49=self.match(self.input, SIGNALROUTE, self.FOLLOW_SIGNALROUTE_in_signalroute2018) 
                if self._state.backtracking == 0:
                    stream_SIGNALROUTE.add(SIGNALROUTE49)
                self._state.following.append(self.FOLLOW_route_id_in_signalroute2020)
                route_id50 = self.route_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_route_id.add(route_id50.tree)
                # sdl92.g:207:17: ( route )+
                cnt12 = 0
                while True: #loop12
                    alt12 = 2
                    LA12_0 = self.input.LA(1)

                    if (LA12_0 == FROM) :
                        alt12 = 1


                    if alt12 == 1:
                        # sdl92.g:0:0: route
                        pass 
                        self._state.following.append(self.FOLLOW_route_in_signalroute2038)
                        route51 = self.route()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_route.add(route51.tree)


                    else:
                        if cnt12 >= 1:
                            break #loop12

                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        eee = EarlyExitException(12, self.input)
                        raise eee

                    cnt12 += 1

                # AST Rewrite
                # elements: route, SIGNALROUTE, route_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 208:9: -> ^( SIGNALROUTE route_id ( route )+ )
                    # sdl92.g:208:17: ^( SIGNALROUTE route_id ( route )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_SIGNALROUTE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_route_id.nextTree())
                    # sdl92.g:208:40: ( route )+
                    if not (stream_route.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_route.hasNext():
                        self._adaptor.addChild(root_1, stream_route.nextTree())


                    stream_route.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signalroute"

    class connection_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.connection_return, self).__init__()

            self.tree = None




    # $ANTLR start "connection"
    # sdl92.g:211:1: connection : CONNECT channel_id AND route_id end -> ^( CONNECTION channel_id route_id ) ;
    def connection(self, ):

        retval = self.connection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CONNECT52 = None
        AND54 = None
        channel_id53 = None

        route_id55 = None

        end56 = None


        CONNECT52_tree = None
        AND54_tree = None
        stream_CONNECT = RewriteRuleTokenStream(self._adaptor, "token CONNECT")
        stream_AND = RewriteRuleTokenStream(self._adaptor, "token AND")
        stream_route_id = RewriteRuleSubtreeStream(self._adaptor, "rule route_id")
        stream_channel_id = RewriteRuleSubtreeStream(self._adaptor, "rule channel_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:212:9: ( CONNECT channel_id AND route_id end -> ^( CONNECTION channel_id route_id ) )
                # sdl92.g:212:17: CONNECT channel_id AND route_id end
                pass 
                CONNECT52=self.match(self.input, CONNECT, self.FOLLOW_CONNECT_in_connection2086) 
                if self._state.backtracking == 0:
                    stream_CONNECT.add(CONNECT52)
                self._state.following.append(self.FOLLOW_channel_id_in_connection2088)
                channel_id53 = self.channel_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_channel_id.add(channel_id53.tree)
                AND54=self.match(self.input, AND, self.FOLLOW_AND_in_connection2090) 
                if self._state.backtracking == 0:
                    stream_AND.add(AND54)
                self._state.following.append(self.FOLLOW_route_id_in_connection2092)
                route_id55 = self.route_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_route_id.add(route_id55.tree)
                self._state.following.append(self.FOLLOW_end_in_connection2094)
                end56 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end56.tree)

                # AST Rewrite
                # elements: route_id, channel_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 213:9: -> ^( CONNECTION channel_id route_id )
                    # sdl92.g:213:17: ^( CONNECTION channel_id route_id )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CONNECTION, "CONNECTION"), root_1)

                    self._adaptor.addChild(root_1, stream_channel_id.nextTree())
                    self._adaptor.addChild(root_1, stream_route_id.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "connection"

    class process_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.process_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "process_definition"
    # sdl92.g:216:1: process_definition : ( PROCESS process_id ( number_of_instances )? REFERENCED end -> ^( PROCESS process_id ( number_of_instances )? REFERENCED ) | ( cif )? PROCESS process_id ( number_of_instances )? end ( text_area | procedure | composite_state )* ( processBody )? ENDPROCESS ( process_id )? end -> ^( PROCESS ( cif )? process_id ( number_of_instances )? ( text_area )* ( procedure )* ( composite_state )* ( processBody )? ) );
    def process_definition(self, ):

        retval = self.process_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PROCESS57 = None
        REFERENCED60 = None
        PROCESS63 = None
        ENDPROCESS71 = None
        process_id58 = None

        number_of_instances59 = None

        end61 = None

        cif62 = None

        process_id64 = None

        number_of_instances65 = None

        end66 = None

        text_area67 = None

        procedure68 = None

        composite_state69 = None

        processBody70 = None

        process_id72 = None

        end73 = None


        PROCESS57_tree = None
        REFERENCED60_tree = None
        PROCESS63_tree = None
        ENDPROCESS71_tree = None
        stream_REFERENCED = RewriteRuleTokenStream(self._adaptor, "token REFERENCED")
        stream_PROCESS = RewriteRuleTokenStream(self._adaptor, "token PROCESS")
        stream_ENDPROCESS = RewriteRuleTokenStream(self._adaptor, "token ENDPROCESS")
        stream_composite_state = RewriteRuleSubtreeStream(self._adaptor, "rule composite_state")
        stream_process_id = RewriteRuleSubtreeStream(self._adaptor, "rule process_id")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_processBody = RewriteRuleSubtreeStream(self._adaptor, "rule processBody")
        stream_text_area = RewriteRuleSubtreeStream(self._adaptor, "rule text_area")
        stream_number_of_instances = RewriteRuleSubtreeStream(self._adaptor, "rule number_of_instances")
        stream_procedure = RewriteRuleSubtreeStream(self._adaptor, "rule procedure")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:217:9: ( PROCESS process_id ( number_of_instances )? REFERENCED end -> ^( PROCESS process_id ( number_of_instances )? REFERENCED ) | ( cif )? PROCESS process_id ( number_of_instances )? end ( text_area | procedure | composite_state )* ( processBody )? ENDPROCESS ( process_id )? end -> ^( PROCESS ( cif )? process_id ( number_of_instances )? ( text_area )* ( procedure )* ( composite_state )* ( processBody )? ) )
                alt19 = 2
                alt19 = self.dfa19.predict(self.input)
                if alt19 == 1:
                    # sdl92.g:217:17: PROCESS process_id ( number_of_instances )? REFERENCED end
                    pass 
                    PROCESS57=self.match(self.input, PROCESS, self.FOLLOW_PROCESS_in_process_definition2140) 
                    if self._state.backtracking == 0:
                        stream_PROCESS.add(PROCESS57)
                    self._state.following.append(self.FOLLOW_process_id_in_process_definition2142)
                    process_id58 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_process_id.add(process_id58.tree)
                    # sdl92.g:217:36: ( number_of_instances )?
                    alt13 = 2
                    LA13_0 = self.input.LA(1)

                    if (LA13_0 == L_PAREN) :
                        alt13 = 1
                    if alt13 == 1:
                        # sdl92.g:0:0: number_of_instances
                        pass 
                        self._state.following.append(self.FOLLOW_number_of_instances_in_process_definition2144)
                        number_of_instances59 = self.number_of_instances()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_number_of_instances.add(number_of_instances59.tree)



                    REFERENCED60=self.match(self.input, REFERENCED, self.FOLLOW_REFERENCED_in_process_definition2147) 
                    if self._state.backtracking == 0:
                        stream_REFERENCED.add(REFERENCED60)
                    self._state.following.append(self.FOLLOW_end_in_process_definition2149)
                    end61 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end61.tree)

                    # AST Rewrite
                    # elements: REFERENCED, process_id, PROCESS, number_of_instances
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 218:9: -> ^( PROCESS process_id ( number_of_instances )? REFERENCED )
                        # sdl92.g:218:17: ^( PROCESS process_id ( number_of_instances )? REFERENCED )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_PROCESS.nextNode(), root_1)

                        self._adaptor.addChild(root_1, stream_process_id.nextTree())
                        # sdl92.g:218:38: ( number_of_instances )?
                        if stream_number_of_instances.hasNext():
                            self._adaptor.addChild(root_1, stream_number_of_instances.nextTree())


                        stream_number_of_instances.reset();
                        self._adaptor.addChild(root_1, stream_REFERENCED.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt19 == 2:
                    # sdl92.g:219:19: ( cif )? PROCESS process_id ( number_of_instances )? end ( text_area | procedure | composite_state )* ( processBody )? ENDPROCESS ( process_id )? end
                    pass 
                    # sdl92.g:219:19: ( cif )?
                    alt14 = 2
                    LA14_0 = self.input.LA(1)

                    if (LA14_0 == 217) :
                        alt14 = 1
                    if alt14 == 1:
                        # sdl92.g:0:0: cif
                        pass 
                        self._state.following.append(self.FOLLOW_cif_in_process_definition2195)
                        cif62 = self.cif()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_cif.add(cif62.tree)



                    PROCESS63=self.match(self.input, PROCESS, self.FOLLOW_PROCESS_in_process_definition2198) 
                    if self._state.backtracking == 0:
                        stream_PROCESS.add(PROCESS63)
                    self._state.following.append(self.FOLLOW_process_id_in_process_definition2200)
                    process_id64 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_process_id.add(process_id64.tree)
                    # sdl92.g:219:43: ( number_of_instances )?
                    alt15 = 2
                    LA15_0 = self.input.LA(1)

                    if (LA15_0 == L_PAREN) :
                        alt15 = 1
                    if alt15 == 1:
                        # sdl92.g:0:0: number_of_instances
                        pass 
                        self._state.following.append(self.FOLLOW_number_of_instances_in_process_definition2202)
                        number_of_instances65 = self.number_of_instances()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_number_of_instances.add(number_of_instances65.tree)



                    self._state.following.append(self.FOLLOW_end_in_process_definition2205)
                    end66 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end66.tree)
                    # sdl92.g:220:17: ( text_area | procedure | composite_state )*
                    while True: #loop16
                        alt16 = 4
                        LA16 = self.input.LA(1)
                        if LA16 == 217:
                            LA16_1 = self.input.LA(2)

                            if (self.synpred24_sdl92()) :
                                alt16 = 1
                            elif (self.synpred25_sdl92()) :
                                alt16 = 2


                        elif LA16 == STATE:
                            LA16_3 = self.input.LA(2)

                            if (self.synpred26_sdl92()) :
                                alt16 = 3


                        elif LA16 == PROCEDURE:
                            alt16 = 2

                        if alt16 == 1:
                            # sdl92.g:220:18: text_area
                            pass 
                            self._state.following.append(self.FOLLOW_text_area_in_process_definition2224)
                            text_area67 = self.text_area()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_text_area.add(text_area67.tree)


                        elif alt16 == 2:
                            # sdl92.g:220:30: procedure
                            pass 
                            self._state.following.append(self.FOLLOW_procedure_in_process_definition2228)
                            procedure68 = self.procedure()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_procedure.add(procedure68.tree)


                        elif alt16 == 3:
                            # sdl92.g:220:42: composite_state
                            pass 
                            self._state.following.append(self.FOLLOW_composite_state_in_process_definition2232)
                            composite_state69 = self.composite_state()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_composite_state.add(composite_state69.tree)


                        else:
                            break #loop16
                    # sdl92.g:221:17: ( processBody )?
                    alt17 = 2
                    LA17_0 = self.input.LA(1)

                    if (LA17_0 == CONNECTION or LA17_0 == STATE or LA17_0 == START or LA17_0 == 217) :
                        alt17 = 1
                    elif (LA17_0 == ENDPROCESS) :
                        LA17_2 = self.input.LA(2)

                        if (self.synpred27_sdl92()) :
                            alt17 = 1
                    if alt17 == 1:
                        # sdl92.g:0:0: processBody
                        pass 
                        self._state.following.append(self.FOLLOW_processBody_in_process_definition2252)
                        processBody70 = self.processBody()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_processBody.add(processBody70.tree)



                    ENDPROCESS71=self.match(self.input, ENDPROCESS, self.FOLLOW_ENDPROCESS_in_process_definition2255) 
                    if self._state.backtracking == 0:
                        stream_ENDPROCESS.add(ENDPROCESS71)
                    # sdl92.g:221:41: ( process_id )?
                    alt18 = 2
                    LA18_0 = self.input.LA(1)

                    if (LA18_0 == ID) :
                        alt18 = 1
                    if alt18 == 1:
                        # sdl92.g:0:0: process_id
                        pass 
                        self._state.following.append(self.FOLLOW_process_id_in_process_definition2257)
                        process_id72 = self.process_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_process_id.add(process_id72.tree)



                    self._state.following.append(self.FOLLOW_end_in_process_definition2276)
                    end73 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end73.tree)

                    # AST Rewrite
                    # elements: processBody, composite_state, number_of_instances, process_id, cif, PROCESS, procedure, text_area
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 223:9: -> ^( PROCESS ( cif )? process_id ( number_of_instances )? ( text_area )* ( procedure )* ( composite_state )* ( processBody )? )
                        # sdl92.g:223:17: ^( PROCESS ( cif )? process_id ( number_of_instances )? ( text_area )* ( procedure )* ( composite_state )* ( processBody )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_PROCESS.nextNode(), root_1)

                        # sdl92.g:223:27: ( cif )?
                        if stream_cif.hasNext():
                            self._adaptor.addChild(root_1, stream_cif.nextTree())


                        stream_cif.reset();
                        self._adaptor.addChild(root_1, stream_process_id.nextTree())
                        # sdl92.g:223:43: ( number_of_instances )?
                        if stream_number_of_instances.hasNext():
                            self._adaptor.addChild(root_1, stream_number_of_instances.nextTree())


                        stream_number_of_instances.reset();
                        # sdl92.g:224:17: ( text_area )*
                        while stream_text_area.hasNext():
                            self._adaptor.addChild(root_1, stream_text_area.nextTree())


                        stream_text_area.reset();
                        # sdl92.g:224:28: ( procedure )*
                        while stream_procedure.hasNext():
                            self._adaptor.addChild(root_1, stream_procedure.nextTree())


                        stream_procedure.reset();
                        # sdl92.g:224:39: ( composite_state )*
                        while stream_composite_state.hasNext():
                            self._adaptor.addChild(root_1, stream_composite_state.nextTree())


                        stream_composite_state.reset();
                        # sdl92.g:224:56: ( processBody )?
                        if stream_processBody.hasNext():
                            self._adaptor.addChild(root_1, stream_processBody.nextTree())


                        stream_processBody.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "process_definition"

    class procedure_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure"
    # sdl92.g:229:1: procedure : ( cif )? PROCEDURE procedure_id end ( fpar )? ( text_area | procedure )* ( ( ( processBody )? ENDPROCEDURE ( procedure_id )? ) | EXTERNAL ) end -> ^( PROCEDURE ( cif )? procedure_id ( end )? ( fpar )? ( text_area )* ( procedure )* ( processBody )? ( EXTERNAL )? ) ;
    def procedure(self, ):

        retval = self.procedure_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PROCEDURE75 = None
        ENDPROCEDURE82 = None
        EXTERNAL84 = None
        cif74 = None

        procedure_id76 = None

        end77 = None

        fpar78 = None

        text_area79 = None

        procedure80 = None

        processBody81 = None

        procedure_id83 = None

        end85 = None


        PROCEDURE75_tree = None
        ENDPROCEDURE82_tree = None
        EXTERNAL84_tree = None
        stream_EXTERNAL = RewriteRuleTokenStream(self._adaptor, "token EXTERNAL")
        stream_ENDPROCEDURE = RewriteRuleTokenStream(self._adaptor, "token ENDPROCEDURE")
        stream_PROCEDURE = RewriteRuleTokenStream(self._adaptor, "token PROCEDURE")
        stream_procedure_id = RewriteRuleSubtreeStream(self._adaptor, "rule procedure_id")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_fpar = RewriteRuleSubtreeStream(self._adaptor, "rule fpar")
        stream_processBody = RewriteRuleSubtreeStream(self._adaptor, "rule processBody")
        stream_text_area = RewriteRuleSubtreeStream(self._adaptor, "rule text_area")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        stream_procedure = RewriteRuleSubtreeStream(self._adaptor, "rule procedure")
        try:
            try:
                # sdl92.g:230:9: ( ( cif )? PROCEDURE procedure_id end ( fpar )? ( text_area | procedure )* ( ( ( processBody )? ENDPROCEDURE ( procedure_id )? ) | EXTERNAL ) end -> ^( PROCEDURE ( cif )? procedure_id ( end )? ( fpar )? ( text_area )* ( procedure )* ( processBody )? ( EXTERNAL )? ) )
                # sdl92.g:230:17: ( cif )? PROCEDURE procedure_id end ( fpar )? ( text_area | procedure )* ( ( ( processBody )? ENDPROCEDURE ( procedure_id )? ) | EXTERNAL ) end
                pass 
                # sdl92.g:230:17: ( cif )?
                alt20 = 2
                LA20_0 = self.input.LA(1)

                if (LA20_0 == 217) :
                    alt20 = 1
                if alt20 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_procedure2356)
                    cif74 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif74.tree)



                PROCEDURE75=self.match(self.input, PROCEDURE, self.FOLLOW_PROCEDURE_in_procedure2375) 
                if self._state.backtracking == 0:
                    stream_PROCEDURE.add(PROCEDURE75)
                self._state.following.append(self.FOLLOW_procedure_id_in_procedure2377)
                procedure_id76 = self.procedure_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_procedure_id.add(procedure_id76.tree)
                self._state.following.append(self.FOLLOW_end_in_procedure2379)
                end77 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end77.tree)
                # sdl92.g:232:17: ( fpar )?
                alt21 = 2
                LA21_0 = self.input.LA(1)

                if (LA21_0 == FPAR) :
                    alt21 = 1
                if alt21 == 1:
                    # sdl92.g:0:0: fpar
                    pass 
                    self._state.following.append(self.FOLLOW_fpar_in_procedure2397)
                    fpar78 = self.fpar()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_fpar.add(fpar78.tree)



                # sdl92.g:233:17: ( text_area | procedure )*
                while True: #loop22
                    alt22 = 3
                    LA22_0 = self.input.LA(1)

                    if (LA22_0 == 217) :
                        LA22_1 = self.input.LA(2)

                        if (self.synpred31_sdl92()) :
                            alt22 = 1
                        elif (self.synpred32_sdl92()) :
                            alt22 = 2


                    elif (LA22_0 == PROCEDURE) :
                        alt22 = 2


                    if alt22 == 1:
                        # sdl92.g:233:18: text_area
                        pass 
                        self._state.following.append(self.FOLLOW_text_area_in_procedure2417)
                        text_area79 = self.text_area()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_text_area.add(text_area79.tree)


                    elif alt22 == 2:
                        # sdl92.g:233:30: procedure
                        pass 
                        self._state.following.append(self.FOLLOW_procedure_in_procedure2421)
                        procedure80 = self.procedure()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_procedure.add(procedure80.tree)


                    else:
                        break #loop22
                # sdl92.g:234:17: ( ( ( processBody )? ENDPROCEDURE ( procedure_id )? ) | EXTERNAL )
                alt25 = 2
                LA25_0 = self.input.LA(1)

                if (LA25_0 == EOF or LA25_0 == CONNECTION or LA25_0 == STATE or (ENDPROCESS <= LA25_0 <= ENDPROCEDURE) or LA25_0 == START or LA25_0 == 217) :
                    alt25 = 1
                elif (LA25_0 == EXTERNAL) :
                    alt25 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 25, 0, self.input)

                    raise nvae

                if alt25 == 1:
                    # sdl92.g:234:18: ( ( processBody )? ENDPROCEDURE ( procedure_id )? )
                    pass 
                    # sdl92.g:234:18: ( ( processBody )? ENDPROCEDURE ( procedure_id )? )
                    # sdl92.g:234:19: ( processBody )? ENDPROCEDURE ( procedure_id )?
                    pass 
                    # sdl92.g:234:19: ( processBody )?
                    alt23 = 2
                    LA23_0 = self.input.LA(1)

                    if (LA23_0 == CONNECTION or LA23_0 == STATE or LA23_0 == START or LA23_0 == 217) :
                        alt23 = 1
                    elif (LA23_0 == ENDPROCEDURE) :
                        LA23_2 = self.input.LA(2)

                        if (self.synpred33_sdl92()) :
                            alt23 = 1
                    if alt23 == 1:
                        # sdl92.g:0:0: processBody
                        pass 
                        self._state.following.append(self.FOLLOW_processBody_in_procedure2443)
                        processBody81 = self.processBody()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_processBody.add(processBody81.tree)



                    ENDPROCEDURE82=self.match(self.input, ENDPROCEDURE, self.FOLLOW_ENDPROCEDURE_in_procedure2446) 
                    if self._state.backtracking == 0:
                        stream_ENDPROCEDURE.add(ENDPROCEDURE82)
                    # sdl92.g:234:45: ( procedure_id )?
                    alt24 = 2
                    LA24_0 = self.input.LA(1)

                    if (LA24_0 == ID) :
                        alt24 = 1
                    if alt24 == 1:
                        # sdl92.g:0:0: procedure_id
                        pass 
                        self._state.following.append(self.FOLLOW_procedure_id_in_procedure2448)
                        procedure_id83 = self.procedure_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_procedure_id.add(procedure_id83.tree)








                elif alt25 == 2:
                    # sdl92.g:234:62: EXTERNAL
                    pass 
                    EXTERNAL84=self.match(self.input, EXTERNAL, self.FOLLOW_EXTERNAL_in_procedure2454) 
                    if self._state.backtracking == 0:
                        stream_EXTERNAL.add(EXTERNAL84)



                self._state.following.append(self.FOLLOW_end_in_procedure2473)
                end85 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end85.tree)

                # AST Rewrite
                # elements: processBody, cif, procedure, fpar, EXTERNAL, end, PROCEDURE, text_area, procedure_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 236:9: -> ^( PROCEDURE ( cif )? procedure_id ( end )? ( fpar )? ( text_area )* ( procedure )* ( processBody )? ( EXTERNAL )? )
                    # sdl92.g:236:17: ^( PROCEDURE ( cif )? procedure_id ( end )? ( fpar )? ( text_area )* ( procedure )* ( processBody )? ( EXTERNAL )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PROCEDURE.nextNode(), root_1)

                    # sdl92.g:236:29: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    self._adaptor.addChild(root_1, stream_procedure_id.nextTree())
                    # sdl92.g:236:47: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    # sdl92.g:236:52: ( fpar )?
                    if stream_fpar.hasNext():
                        self._adaptor.addChild(root_1, stream_fpar.nextTree())


                    stream_fpar.reset();
                    # sdl92.g:237:17: ( text_area )*
                    while stream_text_area.hasNext():
                        self._adaptor.addChild(root_1, stream_text_area.nextTree())


                    stream_text_area.reset();
                    # sdl92.g:237:28: ( procedure )*
                    while stream_procedure.hasNext():
                        self._adaptor.addChild(root_1, stream_procedure.nextTree())


                    stream_procedure.reset();
                    # sdl92.g:237:39: ( processBody )?
                    if stream_processBody.hasNext():
                        self._adaptor.addChild(root_1, stream_processBody.nextTree())


                    stream_processBody.reset();
                    # sdl92.g:237:52: ( EXTERNAL )?
                    if stream_EXTERNAL.hasNext():
                        self._adaptor.addChild(root_1, stream_EXTERNAL.nextNode())


                    stream_EXTERNAL.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure"

    class fpar_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.fpar_return, self).__init__()

            self.tree = None




    # $ANTLR start "fpar"
    # sdl92.g:241:1: fpar : FPAR formal_variable_param ( ',' formal_variable_param )* end -> ^( FPAR ( formal_variable_param )+ ) ;
    def fpar(self, ):

        retval = self.fpar_return()
        retval.start = self.input.LT(1)

        root_0 = None

        FPAR86 = None
        char_literal88 = None
        formal_variable_param87 = None

        formal_variable_param89 = None

        end90 = None


        FPAR86_tree = None
        char_literal88_tree = None
        stream_FPAR = RewriteRuleTokenStream(self._adaptor, "token FPAR")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        stream_formal_variable_param = RewriteRuleSubtreeStream(self._adaptor, "rule formal_variable_param")
        try:
            try:
                # sdl92.g:242:9: ( FPAR formal_variable_param ( ',' formal_variable_param )* end -> ^( FPAR ( formal_variable_param )+ ) )
                # sdl92.g:242:17: FPAR formal_variable_param ( ',' formal_variable_param )* end
                pass 
                FPAR86=self.match(self.input, FPAR, self.FOLLOW_FPAR_in_fpar2555) 
                if self._state.backtracking == 0:
                    stream_FPAR.add(FPAR86)
                self._state.following.append(self.FOLLOW_formal_variable_param_in_fpar2557)
                formal_variable_param87 = self.formal_variable_param()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_formal_variable_param.add(formal_variable_param87.tree)
                # sdl92.g:243:17: ( ',' formal_variable_param )*
                while True: #loop26
                    alt26 = 2
                    LA26_0 = self.input.LA(1)

                    if (LA26_0 == COMMA) :
                        alt26 = 1


                    if alt26 == 1:
                        # sdl92.g:243:18: ',' formal_variable_param
                        pass 
                        char_literal88=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_fpar2576) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal88)
                        self._state.following.append(self.FOLLOW_formal_variable_param_in_fpar2578)
                        formal_variable_param89 = self.formal_variable_param()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_formal_variable_param.add(formal_variable_param89.tree)


                    else:
                        break #loop26
                self._state.following.append(self.FOLLOW_end_in_fpar2598)
                end90 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end90.tree)

                # AST Rewrite
                # elements: formal_variable_param, FPAR
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 245:9: -> ^( FPAR ( formal_variable_param )+ )
                    # sdl92.g:245:17: ^( FPAR ( formal_variable_param )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_FPAR.nextNode(), root_1)

                    # sdl92.g:245:24: ( formal_variable_param )+
                    if not (stream_formal_variable_param.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_formal_variable_param.hasNext():
                        self._adaptor.addChild(root_1, stream_formal_variable_param.nextTree())


                    stream_formal_variable_param.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "fpar"

    class formal_variable_param_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.formal_variable_param_return, self).__init__()

            self.tree = None




    # $ANTLR start "formal_variable_param"
    # sdl92.g:248:1: formal_variable_param : ( INOUT | IN )? variable_id ( ',' variable_id )* sort -> ^( PARAM ( INOUT )? ( IN )? ( variable_id )+ sort ) ;
    def formal_variable_param(self, ):

        retval = self.formal_variable_param_return()
        retval.start = self.input.LT(1)

        root_0 = None

        INOUT91 = None
        IN92 = None
        char_literal94 = None
        variable_id93 = None

        variable_id95 = None

        sort96 = None


        INOUT91_tree = None
        IN92_tree = None
        char_literal94_tree = None
        stream_IN = RewriteRuleTokenStream(self._adaptor, "token IN")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_INOUT = RewriteRuleTokenStream(self._adaptor, "token INOUT")
        stream_sort = RewriteRuleSubtreeStream(self._adaptor, "rule sort")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        try:
            try:
                # sdl92.g:249:9: ( ( INOUT | IN )? variable_id ( ',' variable_id )* sort -> ^( PARAM ( INOUT )? ( IN )? ( variable_id )+ sort ) )
                # sdl92.g:249:17: ( INOUT | IN )? variable_id ( ',' variable_id )* sort
                pass 
                # sdl92.g:249:17: ( INOUT | IN )?
                alt27 = 3
                LA27_0 = self.input.LA(1)

                if (LA27_0 == INOUT) :
                    alt27 = 1
                elif (LA27_0 == IN) :
                    alt27 = 2
                if alt27 == 1:
                    # sdl92.g:249:18: INOUT
                    pass 
                    INOUT91=self.match(self.input, INOUT, self.FOLLOW_INOUT_in_formal_variable_param2644) 
                    if self._state.backtracking == 0:
                        stream_INOUT.add(INOUT91)


                elif alt27 == 2:
                    # sdl92.g:249:26: IN
                    pass 
                    IN92=self.match(self.input, IN, self.FOLLOW_IN_in_formal_variable_param2648) 
                    if self._state.backtracking == 0:
                        stream_IN.add(IN92)



                self._state.following.append(self.FOLLOW_variable_id_in_formal_variable_param2668)
                variable_id93 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id93.tree)
                # sdl92.g:250:29: ( ',' variable_id )*
                while True: #loop28
                    alt28 = 2
                    LA28_0 = self.input.LA(1)

                    if (LA28_0 == COMMA) :
                        alt28 = 1


                    if alt28 == 1:
                        # sdl92.g:250:30: ',' variable_id
                        pass 
                        char_literal94=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_formal_variable_param2671) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal94)
                        self._state.following.append(self.FOLLOW_variable_id_in_formal_variable_param2673)
                        variable_id95 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id95.tree)


                    else:
                        break #loop28
                self._state.following.append(self.FOLLOW_sort_in_formal_variable_param2677)
                sort96 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort96.tree)

                # AST Rewrite
                # elements: variable_id, sort, IN, INOUT
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 251:9: -> ^( PARAM ( INOUT )? ( IN )? ( variable_id )+ sort )
                    # sdl92.g:251:17: ^( PARAM ( INOUT )? ( IN )? ( variable_id )+ sort )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAM, "PARAM"), root_1)

                    # sdl92.g:251:25: ( INOUT )?
                    if stream_INOUT.hasNext():
                        self._adaptor.addChild(root_1, stream_INOUT.nextNode())


                    stream_INOUT.reset();
                    # sdl92.g:251:32: ( IN )?
                    if stream_IN.hasNext():
                        self._adaptor.addChild(root_1, stream_IN.nextNode())


                    stream_IN.reset();
                    # sdl92.g:251:36: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()
                    self._adaptor.addChild(root_1, stream_sort.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "formal_variable_param"

    class text_area_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.text_area_return, self).__init__()

            self.tree = None




    # $ANTLR start "text_area"
    # sdl92.g:255:1: text_area : cif ( content )? cif_end_text -> ^( TEXTAREA cif ( content )? cif_end_text ) ;
    def text_area(self, ):

        retval = self.text_area_return()
        retval.start = self.input.LT(1)

        root_0 = None

        cif97 = None

        content98 = None

        cif_end_text99 = None


        stream_content = RewriteRuleSubtreeStream(self._adaptor, "rule content")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_cif_end_text = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end_text")
        try:
            try:
                # sdl92.g:256:9: ( cif ( content )? cif_end_text -> ^( TEXTAREA cif ( content )? cif_end_text ) )
                # sdl92.g:256:17: cif ( content )? cif_end_text
                pass 
                self._state.following.append(self.FOLLOW_cif_in_text_area2731)
                cif97 = self.cif()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif.add(cif97.tree)
                # sdl92.g:257:17: ( content )?
                alt29 = 2
                LA29_0 = self.input.LA(1)

                if (LA29_0 == 217) :
                    LA29_1 = self.input.LA(2)

                    if (self.synpred40_sdl92()) :
                        alt29 = 1
                elif (LA29_0 == DCL or LA29_0 == FPAR or LA29_0 == NEWTYPE or LA29_0 == PROCEDURE or LA29_0 == SYNONYM or LA29_0 == SYNTYPE or LA29_0 == TIMER) :
                    alt29 = 1
                if alt29 == 1:
                    # sdl92.g:0:0: content
                    pass 
                    self._state.following.append(self.FOLLOW_content_in_text_area2749)
                    content98 = self.content()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_content.add(content98.tree)



                self._state.following.append(self.FOLLOW_cif_end_text_in_text_area2768)
                cif_end_text99 = self.cif_end_text()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end_text.add(cif_end_text99.tree)

                # AST Rewrite
                # elements: cif, cif_end_text, content
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 259:9: -> ^( TEXTAREA cif ( content )? cif_end_text )
                    # sdl92.g:259:17: ^( TEXTAREA cif ( content )? cif_end_text )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TEXTAREA, "TEXTAREA"), root_1)

                    self._adaptor.addChild(root_1, stream_cif.nextTree())
                    # sdl92.g:259:32: ( content )?
                    if stream_content.hasNext():
                        self._adaptor.addChild(root_1, stream_content.nextTree())


                    stream_content.reset();
                    self._adaptor.addChild(root_1, stream_cif_end_text.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "text_area"

    class content_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.content_return, self).__init__()

            self.tree = None




    # $ANTLR start "content"
    # sdl92.g:264:1: content : ( procedure | fpar | timer_declaration | syntype_definition | newtype_definition | variable_definition | synonym_definition )* -> ^( TEXTAREA_CONTENT ( fpar )* ( procedure )* ( variable_definition )* ( syntype_definition )* ( newtype_definition )* ( timer_declaration )* ( synonym_definition )* ) ;
    def content(self, ):

        retval = self.content_return()
        retval.start = self.input.LT(1)

        root_0 = None

        procedure100 = None

        fpar101 = None

        timer_declaration102 = None

        syntype_definition103 = None

        newtype_definition104 = None

        variable_definition105 = None

        synonym_definition106 = None


        stream_timer_declaration = RewriteRuleSubtreeStream(self._adaptor, "rule timer_declaration")
        stream_syntype_definition = RewriteRuleSubtreeStream(self._adaptor, "rule syntype_definition")
        stream_variable_definition = RewriteRuleSubtreeStream(self._adaptor, "rule variable_definition")
        stream_synonym_definition = RewriteRuleSubtreeStream(self._adaptor, "rule synonym_definition")
        stream_fpar = RewriteRuleSubtreeStream(self._adaptor, "rule fpar")
        stream_newtype_definition = RewriteRuleSubtreeStream(self._adaptor, "rule newtype_definition")
        stream_procedure = RewriteRuleSubtreeStream(self._adaptor, "rule procedure")
        try:
            try:
                # sdl92.g:265:9: ( ( procedure | fpar | timer_declaration | syntype_definition | newtype_definition | variable_definition | synonym_definition )* -> ^( TEXTAREA_CONTENT ( fpar )* ( procedure )* ( variable_definition )* ( syntype_definition )* ( newtype_definition )* ( timer_declaration )* ( synonym_definition )* ) )
                # sdl92.g:265:18: ( procedure | fpar | timer_declaration | syntype_definition | newtype_definition | variable_definition | synonym_definition )*
                pass 
                # sdl92.g:265:18: ( procedure | fpar | timer_declaration | syntype_definition | newtype_definition | variable_definition | synonym_definition )*
                while True: #loop30
                    alt30 = 8
                    alt30 = self.dfa30.predict(self.input)
                    if alt30 == 1:
                        # sdl92.g:265:19: procedure
                        pass 
                        self._state.following.append(self.FOLLOW_procedure_in_content2821)
                        procedure100 = self.procedure()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_procedure.add(procedure100.tree)


                    elif alt30 == 2:
                        # sdl92.g:266:20: fpar
                        pass 
                        self._state.following.append(self.FOLLOW_fpar_in_content2842)
                        fpar101 = self.fpar()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_fpar.add(fpar101.tree)


                    elif alt30 == 3:
                        # sdl92.g:267:20: timer_declaration
                        pass 
                        self._state.following.append(self.FOLLOW_timer_declaration_in_content2863)
                        timer_declaration102 = self.timer_declaration()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_timer_declaration.add(timer_declaration102.tree)


                    elif alt30 == 4:
                        # sdl92.g:268:20: syntype_definition
                        pass 
                        self._state.following.append(self.FOLLOW_syntype_definition_in_content2884)
                        syntype_definition103 = self.syntype_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_syntype_definition.add(syntype_definition103.tree)


                    elif alt30 == 5:
                        # sdl92.g:269:20: newtype_definition
                        pass 
                        self._state.following.append(self.FOLLOW_newtype_definition_in_content2905)
                        newtype_definition104 = self.newtype_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_newtype_definition.add(newtype_definition104.tree)


                    elif alt30 == 6:
                        # sdl92.g:270:20: variable_definition
                        pass 
                        self._state.following.append(self.FOLLOW_variable_definition_in_content2926)
                        variable_definition105 = self.variable_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_definition.add(variable_definition105.tree)


                    elif alt30 == 7:
                        # sdl92.g:271:20: synonym_definition
                        pass 
                        self._state.following.append(self.FOLLOW_synonym_definition_in_content2947)
                        synonym_definition106 = self.synonym_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_synonym_definition.add(synonym_definition106.tree)


                    else:
                        break #loop30

                # AST Rewrite
                # elements: synonym_definition, fpar, variable_definition, newtype_definition, syntype_definition, procedure, timer_declaration
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 272:9: -> ^( TEXTAREA_CONTENT ( fpar )* ( procedure )* ( variable_definition )* ( syntype_definition )* ( newtype_definition )* ( timer_declaration )* ( synonym_definition )* )
                    # sdl92.g:272:18: ^( TEXTAREA_CONTENT ( fpar )* ( procedure )* ( variable_definition )* ( syntype_definition )* ( newtype_definition )* ( timer_declaration )* ( synonym_definition )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TEXTAREA_CONTENT, "TEXTAREA_CONTENT"), root_1)

                    # sdl92.g:272:37: ( fpar )*
                    while stream_fpar.hasNext():
                        self._adaptor.addChild(root_1, stream_fpar.nextTree())


                    stream_fpar.reset();
                    # sdl92.g:272:43: ( procedure )*
                    while stream_procedure.hasNext():
                        self._adaptor.addChild(root_1, stream_procedure.nextTree())


                    stream_procedure.reset();
                    # sdl92.g:272:54: ( variable_definition )*
                    while stream_variable_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_definition.nextTree())


                    stream_variable_definition.reset();
                    # sdl92.g:273:20: ( syntype_definition )*
                    while stream_syntype_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_syntype_definition.nextTree())


                    stream_syntype_definition.reset();
                    # sdl92.g:273:40: ( newtype_definition )*
                    while stream_newtype_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_newtype_definition.nextTree())


                    stream_newtype_definition.reset();
                    # sdl92.g:273:60: ( timer_declaration )*
                    while stream_timer_declaration.hasNext():
                        self._adaptor.addChild(root_1, stream_timer_declaration.nextTree())


                    stream_timer_declaration.reset();
                    # sdl92.g:274:20: ( synonym_definition )*
                    while stream_synonym_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_synonym_definition.nextTree())


                    stream_synonym_definition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "content"

    class timer_declaration_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.timer_declaration_return, self).__init__()

            self.tree = None




    # $ANTLR start "timer_declaration"
    # sdl92.g:277:1: timer_declaration : TIMER timer_id ( ',' timer_id )* end -> ^( TIMER ( timer_id )+ ) ;
    def timer_declaration(self, ):

        retval = self.timer_declaration_return()
        retval.start = self.input.LT(1)

        root_0 = None

        TIMER107 = None
        char_literal109 = None
        timer_id108 = None

        timer_id110 = None

        end111 = None


        TIMER107_tree = None
        char_literal109_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_TIMER = RewriteRuleTokenStream(self._adaptor, "token TIMER")
        stream_timer_id = RewriteRuleSubtreeStream(self._adaptor, "rule timer_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:278:9: ( TIMER timer_id ( ',' timer_id )* end -> ^( TIMER ( timer_id )+ ) )
                # sdl92.g:278:17: TIMER timer_id ( ',' timer_id )* end
                pass 
                TIMER107=self.match(self.input, TIMER, self.FOLLOW_TIMER_in_timer_declaration3051) 
                if self._state.backtracking == 0:
                    stream_TIMER.add(TIMER107)
                self._state.following.append(self.FOLLOW_timer_id_in_timer_declaration3053)
                timer_id108 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_timer_id.add(timer_id108.tree)
                # sdl92.g:279:17: ( ',' timer_id )*
                while True: #loop31
                    alt31 = 2
                    LA31_0 = self.input.LA(1)

                    if (LA31_0 == COMMA) :
                        alt31 = 1


                    if alt31 == 1:
                        # sdl92.g:279:18: ',' timer_id
                        pass 
                        char_literal109=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_timer_declaration3072) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal109)
                        self._state.following.append(self.FOLLOW_timer_id_in_timer_declaration3074)
                        timer_id110 = self.timer_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_timer_id.add(timer_id110.tree)


                    else:
                        break #loop31
                self._state.following.append(self.FOLLOW_end_in_timer_declaration3094)
                end111 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end111.tree)

                # AST Rewrite
                # elements: TIMER, timer_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 281:9: -> ^( TIMER ( timer_id )+ )
                    # sdl92.g:281:17: ^( TIMER ( timer_id )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_TIMER.nextNode(), root_1)

                    # sdl92.g:281:25: ( timer_id )+
                    if not (stream_timer_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_timer_id.hasNext():
                        self._adaptor.addChild(root_1, stream_timer_id.nextTree())


                    stream_timer_id.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "timer_declaration"

    class syntype_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.syntype_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "syntype_definition"
    # sdl92.g:283:1: syntype_definition : SYNTYPE syntype_name '=' parent_sort ( CONSTANTS ( range_condition ( ',' range_condition )* ) )? ENDSYNTYPE ( syntype_name )? end -> ^( SYNTYPE syntype_name parent_sort ( range_condition )* ) ;
    def syntype_definition(self, ):

        retval = self.syntype_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SYNTYPE112 = None
        char_literal114 = None
        CONSTANTS116 = None
        char_literal118 = None
        ENDSYNTYPE120 = None
        syntype_name113 = None

        parent_sort115 = None

        range_condition117 = None

        range_condition119 = None

        syntype_name121 = None

        end122 = None


        SYNTYPE112_tree = None
        char_literal114_tree = None
        CONSTANTS116_tree = None
        char_literal118_tree = None
        ENDSYNTYPE120_tree = None
        stream_CONSTANTS = RewriteRuleTokenStream(self._adaptor, "token CONSTANTS")
        stream_EQ = RewriteRuleTokenStream(self._adaptor, "token EQ")
        stream_SYNTYPE = RewriteRuleTokenStream(self._adaptor, "token SYNTYPE")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_ENDSYNTYPE = RewriteRuleTokenStream(self._adaptor, "token ENDSYNTYPE")
        stream_syntype_name = RewriteRuleSubtreeStream(self._adaptor, "rule syntype_name")
        stream_parent_sort = RewriteRuleSubtreeStream(self._adaptor, "rule parent_sort")
        stream_range_condition = RewriteRuleSubtreeStream(self._adaptor, "rule range_condition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:284:9: ( SYNTYPE syntype_name '=' parent_sort ( CONSTANTS ( range_condition ( ',' range_condition )* ) )? ENDSYNTYPE ( syntype_name )? end -> ^( SYNTYPE syntype_name parent_sort ( range_condition )* ) )
                # sdl92.g:284:17: SYNTYPE syntype_name '=' parent_sort ( CONSTANTS ( range_condition ( ',' range_condition )* ) )? ENDSYNTYPE ( syntype_name )? end
                pass 
                SYNTYPE112=self.match(self.input, SYNTYPE, self.FOLLOW_SYNTYPE_in_syntype_definition3138) 
                if self._state.backtracking == 0:
                    stream_SYNTYPE.add(SYNTYPE112)
                self._state.following.append(self.FOLLOW_syntype_name_in_syntype_definition3140)
                syntype_name113 = self.syntype_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_syntype_name.add(syntype_name113.tree)
                char_literal114=self.match(self.input, EQ, self.FOLLOW_EQ_in_syntype_definition3142) 
                if self._state.backtracking == 0:
                    stream_EQ.add(char_literal114)
                self._state.following.append(self.FOLLOW_parent_sort_in_syntype_definition3144)
                parent_sort115 = self.parent_sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_parent_sort.add(parent_sort115.tree)
                # sdl92.g:285:17: ( CONSTANTS ( range_condition ( ',' range_condition )* ) )?
                alt33 = 2
                LA33_0 = self.input.LA(1)

                if (LA33_0 == CONSTANTS) :
                    alt33 = 1
                if alt33 == 1:
                    # sdl92.g:285:18: CONSTANTS ( range_condition ( ',' range_condition )* )
                    pass 
                    CONSTANTS116=self.match(self.input, CONSTANTS, self.FOLLOW_CONSTANTS_in_syntype_definition3163) 
                    if self._state.backtracking == 0:
                        stream_CONSTANTS.add(CONSTANTS116)
                    # sdl92.g:285:28: ( range_condition ( ',' range_condition )* )
                    # sdl92.g:285:29: range_condition ( ',' range_condition )*
                    pass 
                    self._state.following.append(self.FOLLOW_range_condition_in_syntype_definition3166)
                    range_condition117 = self.range_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_range_condition.add(range_condition117.tree)
                    # sdl92.g:285:45: ( ',' range_condition )*
                    while True: #loop32
                        alt32 = 2
                        LA32_0 = self.input.LA(1)

                        if (LA32_0 == COMMA) :
                            alt32 = 1


                        if alt32 == 1:
                            # sdl92.g:285:46: ',' range_condition
                            pass 
                            char_literal118=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_syntype_definition3169) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal118)
                            self._state.following.append(self.FOLLOW_range_condition_in_syntype_definition3171)
                            range_condition119 = self.range_condition()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_range_condition.add(range_condition119.tree)


                        else:
                            break #loop32






                ENDSYNTYPE120=self.match(self.input, ENDSYNTYPE, self.FOLLOW_ENDSYNTYPE_in_syntype_definition3195) 
                if self._state.backtracking == 0:
                    stream_ENDSYNTYPE.add(ENDSYNTYPE120)
                # sdl92.g:286:28: ( syntype_name )?
                alt34 = 2
                LA34_0 = self.input.LA(1)

                if (LA34_0 == ID) :
                    alt34 = 1
                if alt34 == 1:
                    # sdl92.g:0:0: syntype_name
                    pass 
                    self._state.following.append(self.FOLLOW_syntype_name_in_syntype_definition3197)
                    syntype_name121 = self.syntype_name()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_syntype_name.add(syntype_name121.tree)



                self._state.following.append(self.FOLLOW_end_in_syntype_definition3200)
                end122 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end122.tree)

                # AST Rewrite
                # elements: range_condition, syntype_name, parent_sort, SYNTYPE
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 287:9: -> ^( SYNTYPE syntype_name parent_sort ( range_condition )* )
                    # sdl92.g:287:17: ^( SYNTYPE syntype_name parent_sort ( range_condition )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_SYNTYPE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_syntype_name.nextTree())
                    self._adaptor.addChild(root_1, stream_parent_sort.nextTree())
                    # sdl92.g:287:52: ( range_condition )*
                    while stream_range_condition.hasNext():
                        self._adaptor.addChild(root_1, stream_range_condition.nextTree())


                    stream_range_condition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "syntype_definition"

    class syntype_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.syntype_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "syntype_name"
    # sdl92.g:289:1: syntype_name : sort ;
    def syntype_name(self, ):

        retval = self.syntype_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        sort123 = None



        try:
            try:
                # sdl92.g:290:9: ( sort )
                # sdl92.g:290:17: sort
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_sort_in_syntype_name3248)
                sort123 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, sort123.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "syntype_name"

    class parent_sort_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.parent_sort_return, self).__init__()

            self.tree = None




    # $ANTLR start "parent_sort"
    # sdl92.g:292:1: parent_sort : sort ;
    def parent_sort(self, ):

        retval = self.parent_sort_return()
        retval.start = self.input.LT(1)

        root_0 = None

        sort124 = None



        try:
            try:
                # sdl92.g:293:9: ( sort )
                # sdl92.g:293:17: sort
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_sort_in_parent_sort3270)
                sort124 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, sort124.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "parent_sort"

    class newtype_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.newtype_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "newtype_definition"
    # sdl92.g:295:1: newtype_definition : NEWTYPE type_name ( array_definition | structure_definition )? ENDNEWTYPE ( type_name )? end -> ^( NEWTYPE type_name ( array_definition )* ( structure_definition )* ) ;
    def newtype_definition(self, ):

        retval = self.newtype_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        NEWTYPE125 = None
        ENDNEWTYPE129 = None
        type_name126 = None

        array_definition127 = None

        structure_definition128 = None

        type_name130 = None

        end131 = None


        NEWTYPE125_tree = None
        ENDNEWTYPE129_tree = None
        stream_NEWTYPE = RewriteRuleTokenStream(self._adaptor, "token NEWTYPE")
        stream_ENDNEWTYPE = RewriteRuleTokenStream(self._adaptor, "token ENDNEWTYPE")
        stream_structure_definition = RewriteRuleSubtreeStream(self._adaptor, "rule structure_definition")
        stream_type_name = RewriteRuleSubtreeStream(self._adaptor, "rule type_name")
        stream_array_definition = RewriteRuleSubtreeStream(self._adaptor, "rule array_definition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:296:9: ( NEWTYPE type_name ( array_definition | structure_definition )? ENDNEWTYPE ( type_name )? end -> ^( NEWTYPE type_name ( array_definition )* ( structure_definition )* ) )
                # sdl92.g:296:17: NEWTYPE type_name ( array_definition | structure_definition )? ENDNEWTYPE ( type_name )? end
                pass 
                NEWTYPE125=self.match(self.input, NEWTYPE, self.FOLLOW_NEWTYPE_in_newtype_definition3292) 
                if self._state.backtracking == 0:
                    stream_NEWTYPE.add(NEWTYPE125)
                self._state.following.append(self.FOLLOW_type_name_in_newtype_definition3294)
                type_name126 = self.type_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_type_name.add(type_name126.tree)
                # sdl92.g:296:35: ( array_definition | structure_definition )?
                alt35 = 3
                LA35_0 = self.input.LA(1)

                if (LA35_0 == ARRAY) :
                    alt35 = 1
                elif (LA35_0 == STRUCT) :
                    alt35 = 2
                if alt35 == 1:
                    # sdl92.g:296:36: array_definition
                    pass 
                    self._state.following.append(self.FOLLOW_array_definition_in_newtype_definition3297)
                    array_definition127 = self.array_definition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_array_definition.add(array_definition127.tree)


                elif alt35 == 2:
                    # sdl92.g:296:53: structure_definition
                    pass 
                    self._state.following.append(self.FOLLOW_structure_definition_in_newtype_definition3299)
                    structure_definition128 = self.structure_definition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_structure_definition.add(structure_definition128.tree)



                ENDNEWTYPE129=self.match(self.input, ENDNEWTYPE, self.FOLLOW_ENDNEWTYPE_in_newtype_definition3319) 
                if self._state.backtracking == 0:
                    stream_ENDNEWTYPE.add(ENDNEWTYPE129)
                # sdl92.g:297:28: ( type_name )?
                alt36 = 2
                LA36_0 = self.input.LA(1)

                if (LA36_0 == ID) :
                    alt36 = 1
                if alt36 == 1:
                    # sdl92.g:0:0: type_name
                    pass 
                    self._state.following.append(self.FOLLOW_type_name_in_newtype_definition3321)
                    type_name130 = self.type_name()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_type_name.add(type_name130.tree)



                self._state.following.append(self.FOLLOW_end_in_newtype_definition3324)
                end131 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end131.tree)

                # AST Rewrite
                # elements: NEWTYPE, structure_definition, type_name, array_definition
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 298:9: -> ^( NEWTYPE type_name ( array_definition )* ( structure_definition )* )
                    # sdl92.g:298:17: ^( NEWTYPE type_name ( array_definition )* ( structure_definition )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_NEWTYPE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_type_name.nextTree())
                    # sdl92.g:298:37: ( array_definition )*
                    while stream_array_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_array_definition.nextTree())


                    stream_array_definition.reset();
                    # sdl92.g:298:55: ( structure_definition )*
                    while stream_structure_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_structure_definition.nextTree())


                    stream_structure_definition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "newtype_definition"

    class type_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.type_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "type_name"
    # sdl92.g:301:1: type_name : sort ;
    def type_name(self, ):

        retval = self.type_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        sort132 = None



        try:
            try:
                # sdl92.g:302:9: ( sort )
                # sdl92.g:302:17: sort
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_sort_in_type_name3374)
                sort132 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, sort132.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "type_name"

    class array_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.array_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "array_definition"
    # sdl92.g:304:1: array_definition : ARRAY '(' sort ',' sort ')' -> ^( ARRAY sort sort ) ;
    def array_definition(self, ):

        retval = self.array_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ARRAY133 = None
        char_literal134 = None
        char_literal136 = None
        char_literal138 = None
        sort135 = None

        sort137 = None


        ARRAY133_tree = None
        char_literal134_tree = None
        char_literal136_tree = None
        char_literal138_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_ARRAY = RewriteRuleTokenStream(self._adaptor, "token ARRAY")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_sort = RewriteRuleSubtreeStream(self._adaptor, "rule sort")
        try:
            try:
                # sdl92.g:305:9: ( ARRAY '(' sort ',' sort ')' -> ^( ARRAY sort sort ) )
                # sdl92.g:305:17: ARRAY '(' sort ',' sort ')'
                pass 
                ARRAY133=self.match(self.input, ARRAY, self.FOLLOW_ARRAY_in_array_definition3396) 
                if self._state.backtracking == 0:
                    stream_ARRAY.add(ARRAY133)
                char_literal134=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_array_definition3398) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal134)
                self._state.following.append(self.FOLLOW_sort_in_array_definition3400)
                sort135 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort135.tree)
                char_literal136=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_array_definition3402) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(char_literal136)
                self._state.following.append(self.FOLLOW_sort_in_array_definition3404)
                sort137 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort137.tree)
                char_literal138=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_array_definition3406) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal138)

                # AST Rewrite
                # elements: ARRAY, sort, sort
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 306:9: -> ^( ARRAY sort sort )
                    # sdl92.g:306:17: ^( ARRAY sort sort )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ARRAY.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_sort.nextTree())
                    self._adaptor.addChild(root_1, stream_sort.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "array_definition"

    class structure_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.structure_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "structure_definition"
    # sdl92.g:308:1: structure_definition : STRUCT field_list end -> ^( STRUCT field_list ) ;
    def structure_definition(self, ):

        retval = self.structure_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STRUCT139 = None
        field_list140 = None

        end141 = None


        STRUCT139_tree = None
        stream_STRUCT = RewriteRuleTokenStream(self._adaptor, "token STRUCT")
        stream_field_list = RewriteRuleSubtreeStream(self._adaptor, "rule field_list")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:309:9: ( STRUCT field_list end -> ^( STRUCT field_list ) )
                # sdl92.g:309:17: STRUCT field_list end
                pass 
                STRUCT139=self.match(self.input, STRUCT, self.FOLLOW_STRUCT_in_structure_definition3451) 
                if self._state.backtracking == 0:
                    stream_STRUCT.add(STRUCT139)
                self._state.following.append(self.FOLLOW_field_list_in_structure_definition3453)
                field_list140 = self.field_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_field_list.add(field_list140.tree)
                self._state.following.append(self.FOLLOW_end_in_structure_definition3455)
                end141 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end141.tree)

                # AST Rewrite
                # elements: field_list, STRUCT
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 310:9: -> ^( STRUCT field_list )
                    # sdl92.g:310:17: ^( STRUCT field_list )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_STRUCT.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_field_list.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "structure_definition"

    class field_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_list"
    # sdl92.g:312:1: field_list : field_definition ( end field_definition )* -> ^( FIELDS ( field_definition )+ ) ;
    def field_list(self, ):

        retval = self.field_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        field_definition142 = None

        end143 = None

        field_definition144 = None


        stream_field_definition = RewriteRuleSubtreeStream(self._adaptor, "rule field_definition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:313:9: ( field_definition ( end field_definition )* -> ^( FIELDS ( field_definition )+ ) )
                # sdl92.g:313:17: field_definition ( end field_definition )*
                pass 
                self._state.following.append(self.FOLLOW_field_definition_in_field_list3498)
                field_definition142 = self.field_definition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_field_definition.add(field_definition142.tree)
                # sdl92.g:313:34: ( end field_definition )*
                while True: #loop37
                    alt37 = 2
                    alt37 = self.dfa37.predict(self.input)
                    if alt37 == 1:
                        # sdl92.g:313:35: end field_definition
                        pass 
                        self._state.following.append(self.FOLLOW_end_in_field_list3501)
                        end143 = self.end()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_end.add(end143.tree)
                        self._state.following.append(self.FOLLOW_field_definition_in_field_list3503)
                        field_definition144 = self.field_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_field_definition.add(field_definition144.tree)


                    else:
                        break #loop37

                # AST Rewrite
                # elements: field_definition
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 314:9: -> ^( FIELDS ( field_definition )+ )
                    # sdl92.g:314:17: ^( FIELDS ( field_definition )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FIELDS, "FIELDS"), root_1)

                    # sdl92.g:314:26: ( field_definition )+
                    if not (stream_field_definition.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_field_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_field_definition.nextTree())


                    stream_field_definition.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_list"

    class field_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_definition"
    # sdl92.g:316:1: field_definition : field_name ( ',' field_name )* sort -> ^( FIELD ( field_name )+ sort ) ;
    def field_definition(self, ):

        retval = self.field_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal146 = None
        field_name145 = None

        field_name147 = None

        sort148 = None


        char_literal146_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_field_name = RewriteRuleSubtreeStream(self._adaptor, "rule field_name")
        stream_sort = RewriteRuleSubtreeStream(self._adaptor, "rule sort")
        try:
            try:
                # sdl92.g:317:9: ( field_name ( ',' field_name )* sort -> ^( FIELD ( field_name )+ sort ) )
                # sdl92.g:317:17: field_name ( ',' field_name )* sort
                pass 
                self._state.following.append(self.FOLLOW_field_name_in_field_definition3549)
                field_name145 = self.field_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_field_name.add(field_name145.tree)
                # sdl92.g:317:28: ( ',' field_name )*
                while True: #loop38
                    alt38 = 2
                    LA38_0 = self.input.LA(1)

                    if (LA38_0 == COMMA) :
                        alt38 = 1


                    if alt38 == 1:
                        # sdl92.g:317:29: ',' field_name
                        pass 
                        char_literal146=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_field_definition3552) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal146)
                        self._state.following.append(self.FOLLOW_field_name_in_field_definition3554)
                        field_name147 = self.field_name()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_field_name.add(field_name147.tree)


                    else:
                        break #loop38
                self._state.following.append(self.FOLLOW_sort_in_field_definition3558)
                sort148 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort148.tree)

                # AST Rewrite
                # elements: sort, field_name
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 318:9: -> ^( FIELD ( field_name )+ sort )
                    # sdl92.g:318:17: ^( FIELD ( field_name )+ sort )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FIELD, "FIELD"), root_1)

                    # sdl92.g:318:25: ( field_name )+
                    if not (stream_field_name.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_field_name.hasNext():
                        self._adaptor.addChild(root_1, stream_field_name.nextTree())


                    stream_field_name.reset()
                    self._adaptor.addChild(root_1, stream_sort.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_definition"

    class variable_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable_definition"
    # sdl92.g:320:1: variable_definition : DCL variables_of_sort ( ',' variables_of_sort )* end -> ^( DCL ( variables_of_sort )+ ) ;
    def variable_definition(self, ):

        retval = self.variable_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DCL149 = None
        char_literal151 = None
        variables_of_sort150 = None

        variables_of_sort152 = None

        end153 = None


        DCL149_tree = None
        char_literal151_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_DCL = RewriteRuleTokenStream(self._adaptor, "token DCL")
        stream_variables_of_sort = RewriteRuleSubtreeStream(self._adaptor, "rule variables_of_sort")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:321:9: ( DCL variables_of_sort ( ',' variables_of_sort )* end -> ^( DCL ( variables_of_sort )+ ) )
                # sdl92.g:321:17: DCL variables_of_sort ( ',' variables_of_sort )* end
                pass 
                DCL149=self.match(self.input, DCL, self.FOLLOW_DCL_in_variable_definition3604) 
                if self._state.backtracking == 0:
                    stream_DCL.add(DCL149)
                self._state.following.append(self.FOLLOW_variables_of_sort_in_variable_definition3606)
                variables_of_sort150 = self.variables_of_sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variables_of_sort.add(variables_of_sort150.tree)
                # sdl92.g:322:17: ( ',' variables_of_sort )*
                while True: #loop39
                    alt39 = 2
                    LA39_0 = self.input.LA(1)

                    if (LA39_0 == COMMA) :
                        alt39 = 1


                    if alt39 == 1:
                        # sdl92.g:322:18: ',' variables_of_sort
                        pass 
                        char_literal151=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_variable_definition3625) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal151)
                        self._state.following.append(self.FOLLOW_variables_of_sort_in_variable_definition3627)
                        variables_of_sort152 = self.variables_of_sort()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variables_of_sort.add(variables_of_sort152.tree)


                    else:
                        break #loop39
                self._state.following.append(self.FOLLOW_end_in_variable_definition3647)
                end153 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end153.tree)

                # AST Rewrite
                # elements: DCL, variables_of_sort
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 324:9: -> ^( DCL ( variables_of_sort )+ )
                    # sdl92.g:324:17: ^( DCL ( variables_of_sort )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_DCL.nextNode(), root_1)

                    # sdl92.g:324:23: ( variables_of_sort )+
                    if not (stream_variables_of_sort.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variables_of_sort.hasNext():
                        self._adaptor.addChild(root_1, stream_variables_of_sort.nextTree())


                    stream_variables_of_sort.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable_definition"

    class synonym_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.synonym_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "synonym_definition"
    # sdl92.g:326:1: synonym_definition : internal_synonym_definition ;
    def synonym_definition(self, ):

        retval = self.synonym_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        internal_synonym_definition154 = None



        try:
            try:
                # sdl92.g:327:9: ( internal_synonym_definition )
                # sdl92.g:327:17: internal_synonym_definition
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_internal_synonym_definition_in_synonym_definition3691)
                internal_synonym_definition154 = self.internal_synonym_definition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, internal_synonym_definition154.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "synonym_definition"

    class internal_synonym_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.internal_synonym_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "internal_synonym_definition"
    # sdl92.g:329:1: internal_synonym_definition : SYNONYM synonym_definition_item ( ',' synonym_definition_item )* end -> ^( SYNONYM_LIST ( synonym_definition_item )+ ) ;
    def internal_synonym_definition(self, ):

        retval = self.internal_synonym_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SYNONYM155 = None
        char_literal157 = None
        synonym_definition_item156 = None

        synonym_definition_item158 = None

        end159 = None


        SYNONYM155_tree = None
        char_literal157_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_SYNONYM = RewriteRuleTokenStream(self._adaptor, "token SYNONYM")
        stream_synonym_definition_item = RewriteRuleSubtreeStream(self._adaptor, "rule synonym_definition_item")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:330:9: ( SYNONYM synonym_definition_item ( ',' synonym_definition_item )* end -> ^( SYNONYM_LIST ( synonym_definition_item )+ ) )
                # sdl92.g:330:17: SYNONYM synonym_definition_item ( ',' synonym_definition_item )* end
                pass 
                SYNONYM155=self.match(self.input, SYNONYM, self.FOLLOW_SYNONYM_in_internal_synonym_definition3713) 
                if self._state.backtracking == 0:
                    stream_SYNONYM.add(SYNONYM155)
                self._state.following.append(self.FOLLOW_synonym_definition_item_in_internal_synonym_definition3715)
                synonym_definition_item156 = self.synonym_definition_item()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_synonym_definition_item.add(synonym_definition_item156.tree)
                # sdl92.g:330:49: ( ',' synonym_definition_item )*
                while True: #loop40
                    alt40 = 2
                    LA40_0 = self.input.LA(1)

                    if (LA40_0 == COMMA) :
                        alt40 = 1


                    if alt40 == 1:
                        # sdl92.g:330:50: ',' synonym_definition_item
                        pass 
                        char_literal157=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_internal_synonym_definition3718) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal157)
                        self._state.following.append(self.FOLLOW_synonym_definition_item_in_internal_synonym_definition3720)
                        synonym_definition_item158 = self.synonym_definition_item()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_synonym_definition_item.add(synonym_definition_item158.tree)


                    else:
                        break #loop40
                self._state.following.append(self.FOLLOW_end_in_internal_synonym_definition3740)
                end159 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end159.tree)

                # AST Rewrite
                # elements: synonym_definition_item
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 332:9: -> ^( SYNONYM_LIST ( synonym_definition_item )+ )
                    # sdl92.g:332:17: ^( SYNONYM_LIST ( synonym_definition_item )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SYNONYM_LIST, "SYNONYM_LIST"), root_1)

                    # sdl92.g:332:32: ( synonym_definition_item )+
                    if not (stream_synonym_definition_item.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_synonym_definition_item.hasNext():
                        self._adaptor.addChild(root_1, stream_synonym_definition_item.nextTree())


                    stream_synonym_definition_item.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "internal_synonym_definition"

    class synonym_definition_item_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.synonym_definition_item_return, self).__init__()

            self.tree = None




    # $ANTLR start "synonym_definition_item"
    # sdl92.g:334:1: synonym_definition_item : sort sort '=' ground_expression -> ^( SYNONYM sort sort ground_expression ) ;
    def synonym_definition_item(self, ):

        retval = self.synonym_definition_item_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal162 = None
        sort160 = None

        sort161 = None

        ground_expression163 = None


        char_literal162_tree = None
        stream_EQ = RewriteRuleTokenStream(self._adaptor, "token EQ")
        stream_sort = RewriteRuleSubtreeStream(self._adaptor, "rule sort")
        stream_ground_expression = RewriteRuleSubtreeStream(self._adaptor, "rule ground_expression")
        try:
            try:
                # sdl92.g:335:9: ( sort sort '=' ground_expression -> ^( SYNONYM sort sort ground_expression ) )
                # sdl92.g:335:17: sort sort '=' ground_expression
                pass 
                self._state.following.append(self.FOLLOW_sort_in_synonym_definition_item3784)
                sort160 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort160.tree)
                self._state.following.append(self.FOLLOW_sort_in_synonym_definition_item3786)
                sort161 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort161.tree)
                char_literal162=self.match(self.input, EQ, self.FOLLOW_EQ_in_synonym_definition_item3788) 
                if self._state.backtracking == 0:
                    stream_EQ.add(char_literal162)
                self._state.following.append(self.FOLLOW_ground_expression_in_synonym_definition_item3790)
                ground_expression163 = self.ground_expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_ground_expression.add(ground_expression163.tree)

                # AST Rewrite
                # elements: sort, ground_expression, sort
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 336:9: -> ^( SYNONYM sort sort ground_expression )
                    # sdl92.g:336:17: ^( SYNONYM sort sort ground_expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SYNONYM, "SYNONYM"), root_1)

                    self._adaptor.addChild(root_1, stream_sort.nextTree())
                    self._adaptor.addChild(root_1, stream_sort.nextTree())
                    self._adaptor.addChild(root_1, stream_ground_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "synonym_definition_item"

    class variables_of_sort_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variables_of_sort_return, self).__init__()

            self.tree = None




    # $ANTLR start "variables_of_sort"
    # sdl92.g:338:1: variables_of_sort : variable_id ( ',' variable_id )* sort ( ':=' ground_expression )? -> ^( VARIABLES ( variable_id )+ sort ( ground_expression )? ) ;
    def variables_of_sort(self, ):

        retval = self.variables_of_sort_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal165 = None
        string_literal168 = None
        variable_id164 = None

        variable_id166 = None

        sort167 = None

        ground_expression169 = None


        char_literal165_tree = None
        string_literal168_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_ASSIG_OP = RewriteRuleTokenStream(self._adaptor, "token ASSIG_OP")
        stream_sort = RewriteRuleSubtreeStream(self._adaptor, "rule sort")
        stream_ground_expression = RewriteRuleSubtreeStream(self._adaptor, "rule ground_expression")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        try:
            try:
                # sdl92.g:339:9: ( variable_id ( ',' variable_id )* sort ( ':=' ground_expression )? -> ^( VARIABLES ( variable_id )+ sort ( ground_expression )? ) )
                # sdl92.g:339:17: variable_id ( ',' variable_id )* sort ( ':=' ground_expression )?
                pass 
                self._state.following.append(self.FOLLOW_variable_id_in_variables_of_sort3837)
                variable_id164 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id164.tree)
                # sdl92.g:339:29: ( ',' variable_id )*
                while True: #loop41
                    alt41 = 2
                    LA41_0 = self.input.LA(1)

                    if (LA41_0 == COMMA) :
                        alt41 = 1


                    if alt41 == 1:
                        # sdl92.g:339:30: ',' variable_id
                        pass 
                        char_literal165=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_variables_of_sort3840) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal165)
                        self._state.following.append(self.FOLLOW_variable_id_in_variables_of_sort3842)
                        variable_id166 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id166.tree)


                    else:
                        break #loop41
                self._state.following.append(self.FOLLOW_sort_in_variables_of_sort3846)
                sort167 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort167.tree)
                # sdl92.g:339:53: ( ':=' ground_expression )?
                alt42 = 2
                LA42_0 = self.input.LA(1)

                if (LA42_0 == ASSIG_OP) :
                    alt42 = 1
                if alt42 == 1:
                    # sdl92.g:339:54: ':=' ground_expression
                    pass 
                    string_literal168=self.match(self.input, ASSIG_OP, self.FOLLOW_ASSIG_OP_in_variables_of_sort3849) 
                    if self._state.backtracking == 0:
                        stream_ASSIG_OP.add(string_literal168)
                    self._state.following.append(self.FOLLOW_ground_expression_in_variables_of_sort3851)
                    ground_expression169 = self.ground_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_ground_expression.add(ground_expression169.tree)




                # AST Rewrite
                # elements: variable_id, ground_expression, sort
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 340:9: -> ^( VARIABLES ( variable_id )+ sort ( ground_expression )? )
                    # sdl92.g:340:17: ^( VARIABLES ( variable_id )+ sort ( ground_expression )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VARIABLES, "VARIABLES"), root_1)

                    # sdl92.g:340:29: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()
                    self._adaptor.addChild(root_1, stream_sort.nextTree())
                    # sdl92.g:340:47: ( ground_expression )?
                    if stream_ground_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_ground_expression.nextTree())


                    stream_ground_expression.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variables_of_sort"

    class ground_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.ground_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "ground_expression"
    # sdl92.g:343:1: ground_expression : expression -> ^( GROUND expression ) ;
    def ground_expression(self, ):

        retval = self.ground_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        expression170 = None


        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:344:9: ( expression -> ^( GROUND expression ) )
                # sdl92.g:344:17: expression
                pass 
                self._state.following.append(self.FOLLOW_expression_in_ground_expression3903)
                expression170 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression170.tree)

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 345:9: -> ^( GROUND expression )
                    # sdl92.g:345:17: ^( GROUND expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(GROUND, "GROUND"), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "ground_expression"

    class number_of_instances_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.number_of_instances_return, self).__init__()

            self.tree = None




    # $ANTLR start "number_of_instances"
    # sdl92.g:348:1: number_of_instances : '(' initial_number= INT ',' maximum_number= INT ')' -> ^( NUMBER_OF_INSTANCES $initial_number $maximum_number) ;
    def number_of_instances(self, ):

        retval = self.number_of_instances_return()
        retval.start = self.input.LT(1)

        root_0 = None

        initial_number = None
        maximum_number = None
        char_literal171 = None
        char_literal172 = None
        char_literal173 = None

        initial_number_tree = None
        maximum_number_tree = None
        char_literal171_tree = None
        char_literal172_tree = None
        char_literal173_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")

        try:
            try:
                # sdl92.g:349:9: ( '(' initial_number= INT ',' maximum_number= INT ')' -> ^( NUMBER_OF_INSTANCES $initial_number $maximum_number) )
                # sdl92.g:349:17: '(' initial_number= INT ',' maximum_number= INT ')'
                pass 
                char_literal171=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_number_of_instances3947) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal171)
                initial_number=self.match(self.input, INT, self.FOLLOW_INT_in_number_of_instances3951) 
                if self._state.backtracking == 0:
                    stream_INT.add(initial_number)
                char_literal172=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_number_of_instances3953) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(char_literal172)
                maximum_number=self.match(self.input, INT, self.FOLLOW_INT_in_number_of_instances3957) 
                if self._state.backtracking == 0:
                    stream_INT.add(maximum_number)
                char_literal173=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_number_of_instances3959) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal173)

                # AST Rewrite
                # elements: maximum_number, initial_number
                # token labels: maximum_number, initial_number
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_maximum_number = RewriteRuleTokenStream(self._adaptor, "token maximum_number", maximum_number)
                    stream_initial_number = RewriteRuleTokenStream(self._adaptor, "token initial_number", initial_number)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 350:9: -> ^( NUMBER_OF_INSTANCES $initial_number $maximum_number)
                    # sdl92.g:350:17: ^( NUMBER_OF_INSTANCES $initial_number $maximum_number)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(NUMBER_OF_INSTANCES, "NUMBER_OF_INSTANCES"), root_1)

                    self._adaptor.addChild(root_1, stream_initial_number.nextNode())
                    self._adaptor.addChild(root_1, stream_maximum_number.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "number_of_instances"

    class processBody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.processBody_return, self).__init__()

            self.tree = None




    # $ANTLR start "processBody"
    # sdl92.g:353:1: processBody : ( start )? ( state | floating_label )* ;
    def processBody(self, ):

        retval = self.processBody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        start174 = None

        state175 = None

        floating_label176 = None



        try:
            try:
                # sdl92.g:354:9: ( ( start )? ( state | floating_label )* )
                # sdl92.g:354:17: ( start )? ( state | floating_label )*
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:354:17: ( start )?
                alt43 = 2
                alt43 = self.dfa43.predict(self.input)
                if alt43 == 1:
                    # sdl92.g:0:0: start
                    pass 
                    self._state.following.append(self.FOLLOW_start_in_processBody4007)
                    start174 = self.start()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, start174.tree)



                # sdl92.g:354:24: ( state | floating_label )*
                while True: #loop44
                    alt44 = 3
                    alt44 = self.dfa44.predict(self.input)
                    if alt44 == 1:
                        # sdl92.g:354:25: state
                        pass 
                        self._state.following.append(self.FOLLOW_state_in_processBody4011)
                        state175 = self.state()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, state175.tree)


                    elif alt44 == 2:
                        # sdl92.g:354:33: floating_label
                        pass 
                        self._state.following.append(self.FOLLOW_floating_label_in_processBody4015)
                        floating_label176 = self.floating_label()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, floating_label176.tree)


                    else:
                        break #loop44



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "processBody"

    class start_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.start_return, self).__init__()

            self.tree = None




    # $ANTLR start "start"
    # sdl92.g:357:1: start : ( cif )? ( hyperlink )? START (name= state_entry_point_name )? end ( transition )? -> ^( START ( cif )? ( hyperlink )? ( $name)? ( end )? ( transition )? ) ;
    def start(self, ):

        retval = self.start_return()
        retval.start = self.input.LT(1)

        root_0 = None

        START179 = None
        name = None

        cif177 = None

        hyperlink178 = None

        end180 = None

        transition181 = None


        START179_tree = None
        stream_START = RewriteRuleTokenStream(self._adaptor, "token START")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_state_entry_point_name = RewriteRuleSubtreeStream(self._adaptor, "rule state_entry_point_name")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:358:9: ( ( cif )? ( hyperlink )? START (name= state_entry_point_name )? end ( transition )? -> ^( START ( cif )? ( hyperlink )? ( $name)? ( end )? ( transition )? ) )
                # sdl92.g:358:17: ( cif )? ( hyperlink )? START (name= state_entry_point_name )? end ( transition )?
                pass 
                # sdl92.g:358:17: ( cif )?
                alt45 = 2
                LA45_0 = self.input.LA(1)

                if (LA45_0 == 217) :
                    LA45_1 = self.input.LA(2)

                    if (LA45_1 == ANSWER or LA45_1 == COMMENT or LA45_1 == CONNECT or LA45_1 == DECISION or LA45_1 == INPUT or (JOIN <= LA45_1 <= LABEL) or LA45_1 == NEXTSTATE or LA45_1 == OUTPUT or (PROCEDURE <= LA45_1 <= PROCEDURE_CALL) or (PROCESS <= LA45_1 <= PROVIDED) or LA45_1 == RETURN or LA45_1 == STATE or LA45_1 == STOP or LA45_1 == TASK or LA45_1 == TEXT or LA45_1 == START) :
                        alt45 = 1
                if alt45 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_start4040)
                    cif177 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif177.tree)



                # sdl92.g:359:17: ( hyperlink )?
                alt46 = 2
                LA46_0 = self.input.LA(1)

                if (LA46_0 == 217) :
                    alt46 = 1
                if alt46 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_start4059)
                    hyperlink178 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink178.tree)



                START179=self.match(self.input, START, self.FOLLOW_START_in_start4078) 
                if self._state.backtracking == 0:
                    stream_START.add(START179)
                # sdl92.g:360:27: (name= state_entry_point_name )?
                alt47 = 2
                LA47_0 = self.input.LA(1)

                if (LA47_0 == ID) :
                    alt47 = 1
                if alt47 == 1:
                    # sdl92.g:0:0: name= state_entry_point_name
                    pass 
                    self._state.following.append(self.FOLLOW_state_entry_point_name_in_start4082)
                    name = self.state_entry_point_name()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_state_entry_point_name.add(name.tree)



                self._state.following.append(self.FOLLOW_end_in_start4085)
                end180 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end180.tree)
                # sdl92.g:361:17: ( transition )?
                alt48 = 2
                alt48 = self.dfa48.predict(self.input)
                if alt48 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_start4103)
                    transition181 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition181.tree)




                # AST Rewrite
                # elements: name, hyperlink, cif, end, transition, START
                # token labels: 
                # rule labels: retval, name
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if name is not None:
                        stream_name = RewriteRuleSubtreeStream(self._adaptor, "rule name", name.tree)
                    else:
                        stream_name = RewriteRuleSubtreeStream(self._adaptor, "token name", None)


                    root_0 = self._adaptor.nil()
                    # 362:9: -> ^( START ( cif )? ( hyperlink )? ( $name)? ( end )? ( transition )? )
                    # sdl92.g:362:17: ^( START ( cif )? ( hyperlink )? ( $name)? ( end )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_START.nextNode(), root_1)

                    # sdl92.g:362:25: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:362:30: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:362:41: ( $name)?
                    if stream_name.hasNext():
                        self._adaptor.addChild(root_1, stream_name.nextTree())


                    stream_name.reset();
                    # sdl92.g:362:48: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    # sdl92.g:362:53: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "start"

    class floating_label_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.floating_label_return, self).__init__()

            self.tree = None




    # $ANTLR start "floating_label"
    # sdl92.g:365:1: floating_label : ( cif )? ( hyperlink )? CONNECTION connector_name ':' ( transition )? ( cif_end_label )? ENDCONNECTION SEMI -> ^( FLOATING_LABEL ( cif )? ( hyperlink )? connector_name ( transition )? ) ;
    def floating_label(self, ):

        retval = self.floating_label_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CONNECTION184 = None
        char_literal186 = None
        ENDCONNECTION189 = None
        SEMI190 = None
        cif182 = None

        hyperlink183 = None

        connector_name185 = None

        transition187 = None

        cif_end_label188 = None


        CONNECTION184_tree = None
        char_literal186_tree = None
        ENDCONNECTION189_tree = None
        SEMI190_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_ENDCONNECTION = RewriteRuleTokenStream(self._adaptor, "token ENDCONNECTION")
        stream_CONNECTION = RewriteRuleTokenStream(self._adaptor, "token CONNECTION")
        stream_SEMI = RewriteRuleTokenStream(self._adaptor, "token SEMI")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_cif_end_label = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end_label")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_connector_name = RewriteRuleSubtreeStream(self._adaptor, "rule connector_name")
        try:
            try:
                # sdl92.g:366:9: ( ( cif )? ( hyperlink )? CONNECTION connector_name ':' ( transition )? ( cif_end_label )? ENDCONNECTION SEMI -> ^( FLOATING_LABEL ( cif )? ( hyperlink )? connector_name ( transition )? ) )
                # sdl92.g:366:17: ( cif )? ( hyperlink )? CONNECTION connector_name ':' ( transition )? ( cif_end_label )? ENDCONNECTION SEMI
                pass 
                # sdl92.g:366:17: ( cif )?
                alt49 = 2
                LA49_0 = self.input.LA(1)

                if (LA49_0 == 217) :
                    LA49_1 = self.input.LA(2)

                    if (LA49_1 == ANSWER or LA49_1 == COMMENT or LA49_1 == CONNECT or LA49_1 == DECISION or LA49_1 == INPUT or (JOIN <= LA49_1 <= LABEL) or LA49_1 == NEXTSTATE or LA49_1 == OUTPUT or (PROCEDURE <= LA49_1 <= PROCEDURE_CALL) or (PROCESS <= LA49_1 <= PROVIDED) or LA49_1 == RETURN or LA49_1 == STATE or LA49_1 == STOP or LA49_1 == TASK or LA49_1 == TEXT or LA49_1 == START) :
                        alt49 = 1
                if alt49 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_floating_label4162)
                    cif182 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif182.tree)



                # sdl92.g:367:17: ( hyperlink )?
                alt50 = 2
                LA50_0 = self.input.LA(1)

                if (LA50_0 == 217) :
                    alt50 = 1
                if alt50 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_floating_label4181)
                    hyperlink183 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink183.tree)



                CONNECTION184=self.match(self.input, CONNECTION, self.FOLLOW_CONNECTION_in_floating_label4200) 
                if self._state.backtracking == 0:
                    stream_CONNECTION.add(CONNECTION184)
                self._state.following.append(self.FOLLOW_connector_name_in_floating_label4202)
                connector_name185 = self.connector_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_connector_name.add(connector_name185.tree)
                char_literal186=self.match(self.input, 212, self.FOLLOW_212_in_floating_label4204) 
                if self._state.backtracking == 0:
                    stream_212.add(char_literal186)
                # sdl92.g:369:17: ( transition )?
                alt51 = 2
                LA51_0 = self.input.LA(1)

                if (LA51_0 == 217) :
                    LA51_1 = self.input.LA(2)

                    if (LA51_1 == ANSWER or LA51_1 == COMMENT or LA51_1 == CONNECT or LA51_1 == DECISION or LA51_1 == INPUT or (JOIN <= LA51_1 <= LABEL) or LA51_1 == NEXTSTATE or LA51_1 == OUTPUT or (PROCEDURE <= LA51_1 <= PROCEDURE_CALL) or (PROCESS <= LA51_1 <= PROVIDED) or LA51_1 == RETURN or LA51_1 == STATE or LA51_1 == STOP or LA51_1 == TASK or LA51_1 == TEXT or LA51_1 == START or LA51_1 == KEEP) :
                        alt51 = 1
                elif (LA51_0 == ALTERNATIVE or LA51_0 == DECISION or LA51_0 == EXPORT or LA51_0 == FOR or LA51_0 == JOIN or LA51_0 == NEXTSTATE or LA51_0 == OUTPUT or (RESET <= LA51_0 <= RETURN) or LA51_0 == SET or (STOP <= LA51_0 <= STRING) or LA51_0 == TASK or LA51_0 == CALL or LA51_0 == CREATE or LA51_0 == ID) :
                    alt51 = 1
                if alt51 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_floating_label4222)
                    transition187 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition187.tree)



                # sdl92.g:370:17: ( cif_end_label )?
                alt52 = 2
                LA52_0 = self.input.LA(1)

                if (LA52_0 == 217) :
                    alt52 = 1
                if alt52 == 1:
                    # sdl92.g:0:0: cif_end_label
                    pass 
                    self._state.following.append(self.FOLLOW_cif_end_label_in_floating_label4241)
                    cif_end_label188 = self.cif_end_label()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif_end_label.add(cif_end_label188.tree)



                ENDCONNECTION189=self.match(self.input, ENDCONNECTION, self.FOLLOW_ENDCONNECTION_in_floating_label4260) 
                if self._state.backtracking == 0:
                    stream_ENDCONNECTION.add(ENDCONNECTION189)
                SEMI190=self.match(self.input, SEMI, self.FOLLOW_SEMI_in_floating_label4262) 
                if self._state.backtracking == 0:
                    stream_SEMI.add(SEMI190)

                # AST Rewrite
                # elements: hyperlink, connector_name, transition, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 372:9: -> ^( FLOATING_LABEL ( cif )? ( hyperlink )? connector_name ( transition )? )
                    # sdl92.g:372:17: ^( FLOATING_LABEL ( cif )? ( hyperlink )? connector_name ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FLOATING_LABEL, "FLOATING_LABEL"), root_1)

                    # sdl92.g:372:34: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:372:39: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    self._adaptor.addChild(root_1, stream_connector_name.nextTree())
                    # sdl92.g:372:65: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "floating_label"

    class state_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_return, self).__init__()

            self.tree = None




    # $ANTLR start "state"
    # sdl92.g:375:1: state : ( cif )? ( hyperlink )? STATE statelist e= end ( state_part )* ENDSTATE ( statename )? f= end -> ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* ) ;
    def state(self, ):

        retval = self.state_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STATE193 = None
        ENDSTATE196 = None
        e = None

        f = None

        cif191 = None

        hyperlink192 = None

        statelist194 = None

        state_part195 = None

        statename197 = None


        STATE193_tree = None
        ENDSTATE196_tree = None
        stream_STATE = RewriteRuleTokenStream(self._adaptor, "token STATE")
        stream_ENDSTATE = RewriteRuleTokenStream(self._adaptor, "token ENDSTATE")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_statelist = RewriteRuleSubtreeStream(self._adaptor, "rule statelist")
        stream_state_part = RewriteRuleSubtreeStream(self._adaptor, "rule state_part")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:376:9: ( ( cif )? ( hyperlink )? STATE statelist e= end ( state_part )* ENDSTATE ( statename )? f= end -> ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* ) )
                # sdl92.g:376:17: ( cif )? ( hyperlink )? STATE statelist e= end ( state_part )* ENDSTATE ( statename )? f= end
                pass 
                # sdl92.g:376:17: ( cif )?
                alt53 = 2
                LA53_0 = self.input.LA(1)

                if (LA53_0 == 217) :
                    LA53_1 = self.input.LA(2)

                    if (LA53_1 == ANSWER or LA53_1 == COMMENT or LA53_1 == CONNECT or LA53_1 == DECISION or LA53_1 == INPUT or (JOIN <= LA53_1 <= LABEL) or LA53_1 == NEXTSTATE or LA53_1 == OUTPUT or (PROCEDURE <= LA53_1 <= PROCEDURE_CALL) or (PROCESS <= LA53_1 <= PROVIDED) or LA53_1 == RETURN or LA53_1 == STATE or LA53_1 == STOP or LA53_1 == TASK or LA53_1 == TEXT or LA53_1 == START) :
                        alt53 = 1
                if alt53 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_state4315)
                    cif191 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif191.tree)



                # sdl92.g:377:17: ( hyperlink )?
                alt54 = 2
                LA54_0 = self.input.LA(1)

                if (LA54_0 == 217) :
                    alt54 = 1
                if alt54 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_state4334)
                    hyperlink192 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink192.tree)



                STATE193=self.match(self.input, STATE, self.FOLLOW_STATE_in_state4353) 
                if self._state.backtracking == 0:
                    stream_STATE.add(STATE193)
                self._state.following.append(self.FOLLOW_statelist_in_state4355)
                statelist194 = self.statelist()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_statelist.add(statelist194.tree)
                self._state.following.append(self.FOLLOW_end_in_state4359)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                # sdl92.g:379:17: ( state_part )*
                while True: #loop55
                    alt55 = 2
                    LA55_0 = self.input.LA(1)

                    if (LA55_0 == CONNECT or LA55_0 == INPUT or LA55_0 == PROVIDED or LA55_0 == SAVE or LA55_0 == 217) :
                        alt55 = 1


                    if alt55 == 1:
                        # sdl92.g:379:18: state_part
                        pass 
                        self._state.following.append(self.FOLLOW_state_part_in_state4378)
                        state_part195 = self.state_part()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_state_part.add(state_part195.tree)


                    else:
                        break #loop55
                ENDSTATE196=self.match(self.input, ENDSTATE, self.FOLLOW_ENDSTATE_in_state4398) 
                if self._state.backtracking == 0:
                    stream_ENDSTATE.add(ENDSTATE196)
                # sdl92.g:380:26: ( statename )?
                alt56 = 2
                LA56_0 = self.input.LA(1)

                if (LA56_0 == ID) :
                    alt56 = 1
                if alt56 == 1:
                    # sdl92.g:0:0: statename
                    pass 
                    self._state.following.append(self.FOLLOW_statename_in_state4400)
                    statename197 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_statename.add(statename197.tree)



                self._state.following.append(self.FOLLOW_end_in_state4405)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: e, cif, STATE, state_part, statelist, hyperlink
                # token labels: 
                # rule labels: retval, e
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if e is not None:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "rule e", e.tree)
                    else:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "token e", None)


                    root_0 = self._adaptor.nil()
                    # 381:9: -> ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* )
                    # sdl92.g:381:17: ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_STATE.nextNode(), root_1)

                    # sdl92.g:381:25: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:381:30: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:381:41: ( $e)?
                    if stream_e.hasNext():
                        self._adaptor.addChild(root_1, stream_e.nextTree())


                    stream_e.reset();
                    self._adaptor.addChild(root_1, stream_statelist.nextTree())
                    # sdl92.g:381:55: ( state_part )*
                    while stream_state_part.hasNext():
                        self._adaptor.addChild(root_1, stream_state_part.nextTree())


                    stream_state_part.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state"

    class statelist_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.statelist_return, self).__init__()

            self.tree = None




    # $ANTLR start "statelist"
    # sdl92.g:384:1: statelist : ( ( ( statename ) ( ',' statename )* ) -> ^( STATELIST ( statename )+ ) | ASTERISK ( exception_state )? -> ^( ASTERISK ( exception_state )? ) );
    def statelist(self, ):

        retval = self.statelist_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal199 = None
        ASTERISK201 = None
        statename198 = None

        statename200 = None

        exception_state202 = None


        char_literal199_tree = None
        ASTERISK201_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_ASTERISK = RewriteRuleTokenStream(self._adaptor, "token ASTERISK")
        stream_exception_state = RewriteRuleSubtreeStream(self._adaptor, "rule exception_state")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        try:
            try:
                # sdl92.g:385:9: ( ( ( statename ) ( ',' statename )* ) -> ^( STATELIST ( statename )+ ) | ASTERISK ( exception_state )? -> ^( ASTERISK ( exception_state )? ) )
                alt59 = 2
                LA59_0 = self.input.LA(1)

                if (LA59_0 == ID) :
                    alt59 = 1
                elif (LA59_0 == ASTERISK) :
                    alt59 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 59, 0, self.input)

                    raise nvae

                if alt59 == 1:
                    # sdl92.g:385:17: ( ( statename ) ( ',' statename )* )
                    pass 
                    # sdl92.g:385:17: ( ( statename ) ( ',' statename )* )
                    # sdl92.g:385:18: ( statename ) ( ',' statename )*
                    pass 
                    # sdl92.g:385:18: ( statename )
                    # sdl92.g:385:19: statename
                    pass 
                    self._state.following.append(self.FOLLOW_statename_in_statelist4464)
                    statename198 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_statename.add(statename198.tree)



                    # sdl92.g:385:29: ( ',' statename )*
                    while True: #loop57
                        alt57 = 2
                        LA57_0 = self.input.LA(1)

                        if (LA57_0 == COMMA) :
                            alt57 = 1


                        if alt57 == 1:
                            # sdl92.g:385:30: ',' statename
                            pass 
                            char_literal199=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_statelist4467) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal199)
                            self._state.following.append(self.FOLLOW_statename_in_statelist4469)
                            statename200 = self.statename()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_statename.add(statename200.tree)


                        else:
                            break #loop57




                    # AST Rewrite
                    # elements: statename
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 386:9: -> ^( STATELIST ( statename )+ )
                        # sdl92.g:386:17: ^( STATELIST ( statename )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(STATELIST, "STATELIST"), root_1)

                        # sdl92.g:386:29: ( statename )+
                        if not (stream_statename.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_statename.hasNext():
                            self._adaptor.addChild(root_1, stream_statename.nextTree())


                        stream_statename.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt59 == 2:
                    # sdl92.g:387:19: ASTERISK ( exception_state )?
                    pass 
                    ASTERISK201=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_statelist4514) 
                    if self._state.backtracking == 0:
                        stream_ASTERISK.add(ASTERISK201)
                    # sdl92.g:387:28: ( exception_state )?
                    alt58 = 2
                    LA58_0 = self.input.LA(1)

                    if (LA58_0 == L_PAREN) :
                        alt58 = 1
                    if alt58 == 1:
                        # sdl92.g:0:0: exception_state
                        pass 
                        self._state.following.append(self.FOLLOW_exception_state_in_statelist4516)
                        exception_state202 = self.exception_state()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_exception_state.add(exception_state202.tree)




                    # AST Rewrite
                    # elements: ASTERISK, exception_state
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 388:9: -> ^( ASTERISK ( exception_state )? )
                        # sdl92.g:388:17: ^( ASTERISK ( exception_state )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_ASTERISK.nextNode(), root_1)

                        # sdl92.g:388:28: ( exception_state )?
                        if stream_exception_state.hasNext():
                            self._adaptor.addChild(root_1, stream_exception_state.nextTree())


                        stream_exception_state.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "statelist"

    class exception_state_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.exception_state_return, self).__init__()

            self.tree = None




    # $ANTLR start "exception_state"
    # sdl92.g:391:1: exception_state : '(' statename ( ',' statename )* ')' -> ( statename )+ ;
    def exception_state(self, ):

        retval = self.exception_state_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal203 = None
        char_literal205 = None
        char_literal207 = None
        statename204 = None

        statename206 = None


        char_literal203_tree = None
        char_literal205_tree = None
        char_literal207_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        try:
            try:
                # sdl92.g:392:9: ( '(' statename ( ',' statename )* ')' -> ( statename )+ )
                # sdl92.g:392:17: '(' statename ( ',' statename )* ')'
                pass 
                char_literal203=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_exception_state4562) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal203)
                self._state.following.append(self.FOLLOW_statename_in_exception_state4564)
                statename204 = self.statename()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_statename.add(statename204.tree)
                # sdl92.g:392:31: ( ',' statename )*
                while True: #loop60
                    alt60 = 2
                    LA60_0 = self.input.LA(1)

                    if (LA60_0 == COMMA) :
                        alt60 = 1


                    if alt60 == 1:
                        # sdl92.g:392:32: ',' statename
                        pass 
                        char_literal205=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_exception_state4567) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal205)
                        self._state.following.append(self.FOLLOW_statename_in_exception_state4569)
                        statename206 = self.statename()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_statename.add(statename206.tree)


                    else:
                        break #loop60
                char_literal207=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_exception_state4573) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal207)

                # AST Rewrite
                # elements: statename
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 393:9: -> ( statename )+
                    # sdl92.g:393:17: ( statename )+
                    if not (stream_statename.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_statename.hasNext():
                        self._adaptor.addChild(root_0, stream_statename.nextTree())


                    stream_statename.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "exception_state"

    class composite_state_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.composite_state_return, self).__init__()

            self.tree = None




    # $ANTLR start "composite_state"
    # sdl92.g:396:1: composite_state : STATE statename e= end SUBSTRUCTURE ( connection_points )* body= composite_state_body ENDSUBSTRUCTURE ( statename )? f= end -> ^( COMPOSITE_STATE statename ( connection_points )* $body ( $e)? ) ;
    def composite_state(self, ):

        retval = self.composite_state_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STATE208 = None
        SUBSTRUCTURE210 = None
        ENDSUBSTRUCTURE212 = None
        e = None

        body = None

        f = None

        statename209 = None

        connection_points211 = None

        statename213 = None


        STATE208_tree = None
        SUBSTRUCTURE210_tree = None
        ENDSUBSTRUCTURE212_tree = None
        stream_STATE = RewriteRuleTokenStream(self._adaptor, "token STATE")
        stream_ENDSUBSTRUCTURE = RewriteRuleTokenStream(self._adaptor, "token ENDSUBSTRUCTURE")
        stream_SUBSTRUCTURE = RewriteRuleTokenStream(self._adaptor, "token SUBSTRUCTURE")
        stream_connection_points = RewriteRuleSubtreeStream(self._adaptor, "rule connection_points")
        stream_composite_state_body = RewriteRuleSubtreeStream(self._adaptor, "rule composite_state_body")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:397:9: ( STATE statename e= end SUBSTRUCTURE ( connection_points )* body= composite_state_body ENDSUBSTRUCTURE ( statename )? f= end -> ^( COMPOSITE_STATE statename ( connection_points )* $body ( $e)? ) )
                # sdl92.g:397:17: STATE statename e= end SUBSTRUCTURE ( connection_points )* body= composite_state_body ENDSUBSTRUCTURE ( statename )? f= end
                pass 
                STATE208=self.match(self.input, STATE, self.FOLLOW_STATE_in_composite_state4614) 
                if self._state.backtracking == 0:
                    stream_STATE.add(STATE208)
                self._state.following.append(self.FOLLOW_statename_in_composite_state4616)
                statename209 = self.statename()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_statename.add(statename209.tree)
                self._state.following.append(self.FOLLOW_end_in_composite_state4620)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                SUBSTRUCTURE210=self.match(self.input, SUBSTRUCTURE, self.FOLLOW_SUBSTRUCTURE_in_composite_state4638) 
                if self._state.backtracking == 0:
                    stream_SUBSTRUCTURE.add(SUBSTRUCTURE210)
                # sdl92.g:399:17: ( connection_points )*
                while True: #loop61
                    alt61 = 2
                    LA61_0 = self.input.LA(1)

                    if (LA61_0 == IN or LA61_0 == OUT) :
                        alt61 = 1


                    if alt61 == 1:
                        # sdl92.g:0:0: connection_points
                        pass 
                        self._state.following.append(self.FOLLOW_connection_points_in_composite_state4656)
                        connection_points211 = self.connection_points()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_connection_points.add(connection_points211.tree)


                    else:
                        break #loop61
                self._state.following.append(self.FOLLOW_composite_state_body_in_composite_state4677)
                body = self.composite_state_body()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_composite_state_body.add(body.tree)
                ENDSUBSTRUCTURE212=self.match(self.input, ENDSUBSTRUCTURE, self.FOLLOW_ENDSUBSTRUCTURE_in_composite_state4695) 
                if self._state.backtracking == 0:
                    stream_ENDSUBSTRUCTURE.add(ENDSUBSTRUCTURE212)
                # sdl92.g:401:33: ( statename )?
                alt62 = 2
                LA62_0 = self.input.LA(1)

                if (LA62_0 == ID) :
                    alt62 = 1
                if alt62 == 1:
                    # sdl92.g:0:0: statename
                    pass 
                    self._state.following.append(self.FOLLOW_statename_in_composite_state4697)
                    statename213 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_statename.add(statename213.tree)



                self._state.following.append(self.FOLLOW_end_in_composite_state4702)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: e, connection_points, statename, body
                # token labels: 
                # rule labels: body, retval, e
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if body is not None:
                        stream_body = RewriteRuleSubtreeStream(self._adaptor, "rule body", body.tree)
                    else:
                        stream_body = RewriteRuleSubtreeStream(self._adaptor, "token body", None)


                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if e is not None:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "rule e", e.tree)
                    else:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "token e", None)


                    root_0 = self._adaptor.nil()
                    # 402:9: -> ^( COMPOSITE_STATE statename ( connection_points )* $body ( $e)? )
                    # sdl92.g:402:17: ^( COMPOSITE_STATE statename ( connection_points )* $body ( $e)? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(COMPOSITE_STATE, "COMPOSITE_STATE"), root_1)

                    self._adaptor.addChild(root_1, stream_statename.nextTree())
                    # sdl92.g:402:45: ( connection_points )*
                    while stream_connection_points.hasNext():
                        self._adaptor.addChild(root_1, stream_connection_points.nextTree())


                    stream_connection_points.reset();
                    self._adaptor.addChild(root_1, stream_body.nextTree())
                    # sdl92.g:402:70: ( $e)?
                    if stream_e.hasNext():
                        self._adaptor.addChild(root_1, stream_e.nextTree())


                    stream_e.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "composite_state"

    class connection_points_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.connection_points_return, self).__init__()

            self.tree = None




    # $ANTLR start "connection_points"
    # sdl92.g:405:1: connection_points : ( IN state_entry_exit_points end -> ^( IN state_entry_exit_points ( end )? ) | OUT state_entry_exit_points end -> ^( OUT state_entry_exit_points ( end )? ) );
    def connection_points(self, ):

        retval = self.connection_points_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IN214 = None
        OUT217 = None
        state_entry_exit_points215 = None

        end216 = None

        state_entry_exit_points218 = None

        end219 = None


        IN214_tree = None
        OUT217_tree = None
        stream_IN = RewriteRuleTokenStream(self._adaptor, "token IN")
        stream_OUT = RewriteRuleTokenStream(self._adaptor, "token OUT")
        stream_state_entry_exit_points = RewriteRuleSubtreeStream(self._adaptor, "rule state_entry_exit_points")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:406:9: ( IN state_entry_exit_points end -> ^( IN state_entry_exit_points ( end )? ) | OUT state_entry_exit_points end -> ^( OUT state_entry_exit_points ( end )? ) )
                alt63 = 2
                LA63_0 = self.input.LA(1)

                if (LA63_0 == IN) :
                    alt63 = 1
                elif (LA63_0 == OUT) :
                    alt63 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 63, 0, self.input)

                    raise nvae

                if alt63 == 1:
                    # sdl92.g:406:17: IN state_entry_exit_points end
                    pass 
                    IN214=self.match(self.input, IN, self.FOLLOW_IN_in_connection_points4756) 
                    if self._state.backtracking == 0:
                        stream_IN.add(IN214)
                    self._state.following.append(self.FOLLOW_state_entry_exit_points_in_connection_points4758)
                    state_entry_exit_points215 = self.state_entry_exit_points()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_state_entry_exit_points.add(state_entry_exit_points215.tree)
                    self._state.following.append(self.FOLLOW_end_in_connection_points4760)
                    end216 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end216.tree)

                    # AST Rewrite
                    # elements: state_entry_exit_points, IN, end
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 407:9: -> ^( IN state_entry_exit_points ( end )? )
                        # sdl92.g:407:17: ^( IN state_entry_exit_points ( end )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_IN.nextNode(), root_1)

                        self._adaptor.addChild(root_1, stream_state_entry_exit_points.nextTree())
                        # sdl92.g:407:46: ( end )?
                        if stream_end.hasNext():
                            self._adaptor.addChild(root_1, stream_end.nextTree())


                        stream_end.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt63 == 2:
                    # sdl92.g:408:19: OUT state_entry_exit_points end
                    pass 
                    OUT217=self.match(self.input, OUT, self.FOLLOW_OUT_in_connection_points4804) 
                    if self._state.backtracking == 0:
                        stream_OUT.add(OUT217)
                    self._state.following.append(self.FOLLOW_state_entry_exit_points_in_connection_points4806)
                    state_entry_exit_points218 = self.state_entry_exit_points()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_state_entry_exit_points.add(state_entry_exit_points218.tree)
                    self._state.following.append(self.FOLLOW_end_in_connection_points4808)
                    end219 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end219.tree)

                    # AST Rewrite
                    # elements: state_entry_exit_points, OUT, end
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 409:9: -> ^( OUT state_entry_exit_points ( end )? )
                        # sdl92.g:409:17: ^( OUT state_entry_exit_points ( end )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_OUT.nextNode(), root_1)

                        self._adaptor.addChild(root_1, stream_state_entry_exit_points.nextTree())
                        # sdl92.g:409:47: ( end )?
                        if stream_end.hasNext():
                            self._adaptor.addChild(root_1, stream_end.nextTree())


                        stream_end.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "connection_points"

    class state_entry_exit_points_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_entry_exit_points_return, self).__init__()

            self.tree = None




    # $ANTLR start "state_entry_exit_points"
    # sdl92.g:412:1: state_entry_exit_points : '(' statename ( ',' statename )* ')' -> ( statename )+ ;
    def state_entry_exit_points(self, ):

        retval = self.state_entry_exit_points_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal220 = None
        char_literal222 = None
        char_literal224 = None
        statename221 = None

        statename223 = None


        char_literal220_tree = None
        char_literal222_tree = None
        char_literal224_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        try:
            try:
                # sdl92.g:413:9: ( '(' statename ( ',' statename )* ')' -> ( statename )+ )
                # sdl92.g:413:17: '(' statename ( ',' statename )* ')'
                pass 
                char_literal220=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_state_entry_exit_points4855) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal220)
                self._state.following.append(self.FOLLOW_statename_in_state_entry_exit_points4857)
                statename221 = self.statename()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_statename.add(statename221.tree)
                # sdl92.g:413:31: ( ',' statename )*
                while True: #loop64
                    alt64 = 2
                    LA64_0 = self.input.LA(1)

                    if (LA64_0 == COMMA) :
                        alt64 = 1


                    if alt64 == 1:
                        # sdl92.g:413:32: ',' statename
                        pass 
                        char_literal222=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_state_entry_exit_points4860) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal222)
                        self._state.following.append(self.FOLLOW_statename_in_state_entry_exit_points4862)
                        statename223 = self.statename()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_statename.add(statename223.tree)


                    else:
                        break #loop64
                char_literal224=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_state_entry_exit_points4866) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal224)

                # AST Rewrite
                # elements: statename
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 414:9: -> ( statename )+
                    # sdl92.g:414:17: ( statename )+
                    if not (stream_statename.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_statename.hasNext():
                        self._adaptor.addChild(root_0, stream_statename.nextTree())


                    stream_statename.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state_entry_exit_points"

    class composite_state_body_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.composite_state_body_return, self).__init__()

            self.tree = None




    # $ANTLR start "composite_state_body"
    # sdl92.g:417:1: composite_state_body : ( text_area | procedure | composite_state )* ( start )* ( state | floating_label )* ;
    def composite_state_body(self, ):

        retval = self.composite_state_body_return()
        retval.start = self.input.LT(1)

        root_0 = None

        text_area225 = None

        procedure226 = None

        composite_state227 = None

        start228 = None

        state229 = None

        floating_label230 = None



        try:
            try:
                # sdl92.g:418:9: ( ( text_area | procedure | composite_state )* ( start )* ( state | floating_label )* )
                # sdl92.g:418:17: ( text_area | procedure | composite_state )* ( start )* ( state | floating_label )*
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:418:17: ( text_area | procedure | composite_state )*
                while True: #loop65
                    alt65 = 4
                    LA65 = self.input.LA(1)
                    if LA65 == 217:
                        LA65_1 = self.input.LA(2)

                        if (self.synpred84_sdl92()) :
                            alt65 = 1
                        elif (self.synpred85_sdl92()) :
                            alt65 = 2


                    elif LA65 == STATE:
                        LA65_3 = self.input.LA(2)

                        if (self.synpred86_sdl92()) :
                            alt65 = 3


                    elif LA65 == PROCEDURE:
                        alt65 = 2

                    if alt65 == 1:
                        # sdl92.g:418:18: text_area
                        pass 
                        self._state.following.append(self.FOLLOW_text_area_in_composite_state_body4908)
                        text_area225 = self.text_area()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, text_area225.tree)


                    elif alt65 == 2:
                        # sdl92.g:418:30: procedure
                        pass 
                        self._state.following.append(self.FOLLOW_procedure_in_composite_state_body4912)
                        procedure226 = self.procedure()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, procedure226.tree)


                    elif alt65 == 3:
                        # sdl92.g:418:42: composite_state
                        pass 
                        self._state.following.append(self.FOLLOW_composite_state_in_composite_state_body4916)
                        composite_state227 = self.composite_state()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, composite_state227.tree)


                    else:
                        break #loop65
                # sdl92.g:419:17: ( start )*
                while True: #loop66
                    alt66 = 2
                    alt66 = self.dfa66.predict(self.input)
                    if alt66 == 1:
                        # sdl92.g:0:0: start
                        pass 
                        self._state.following.append(self.FOLLOW_start_in_composite_state_body4936)
                        start228 = self.start()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, start228.tree)


                    else:
                        break #loop66
                # sdl92.g:419:24: ( state | floating_label )*
                while True: #loop67
                    alt67 = 3
                    alt67 = self.dfa67.predict(self.input)
                    if alt67 == 1:
                        # sdl92.g:419:25: state
                        pass 
                        self._state.following.append(self.FOLLOW_state_in_composite_state_body4940)
                        state229 = self.state()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, state229.tree)


                    elif alt67 == 2:
                        # sdl92.g:419:33: floating_label
                        pass 
                        self._state.following.append(self.FOLLOW_floating_label_in_composite_state_body4944)
                        floating_label230 = self.floating_label()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, floating_label230.tree)


                    else:
                        break #loop67



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "composite_state_body"

    class state_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "state_part"
    # sdl92.g:422:1: state_part : ( input_part | save_part | spontaneous_transition | continuous_signal | connect_part );
    def state_part(self, ):

        retval = self.state_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        input_part231 = None

        save_part232 = None

        spontaneous_transition233 = None

        continuous_signal234 = None

        connect_part235 = None



        try:
            try:
                # sdl92.g:423:9: ( input_part | save_part | spontaneous_transition | continuous_signal | connect_part )
                alt68 = 5
                alt68 = self.dfa68.predict(self.input)
                if alt68 == 1:
                    # sdl92.g:423:17: input_part
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_input_part_in_state_part4969)
                    input_part231 = self.input_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, input_part231.tree)


                elif alt68 == 2:
                    # sdl92.g:425:19: save_part
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_save_part_in_state_part5006)
                    save_part232 = self.save_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, save_part232.tree)


                elif alt68 == 3:
                    # sdl92.g:426:19: spontaneous_transition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_spontaneous_transition_in_state_part5041)
                    spontaneous_transition233 = self.spontaneous_transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, spontaneous_transition233.tree)


                elif alt68 == 4:
                    # sdl92.g:427:19: continuous_signal
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_continuous_signal_in_state_part5061)
                    continuous_signal234 = self.continuous_signal()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, continuous_signal234.tree)


                elif alt68 == 5:
                    # sdl92.g:428:19: connect_part
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_connect_part_in_state_part5088)
                    connect_part235 = self.connect_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, connect_part235.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state_part"

    class connect_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.connect_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "connect_part"
    # sdl92.g:432:1: connect_part : ( cif )? ( hyperlink )? CONNECT ( connect_list )? end ( transition )? -> ^( CONNECT ( cif )? ( hyperlink )? ( connect_list )? ( end )? ( transition )? ) ;
    def connect_part(self, ):

        retval = self.connect_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CONNECT238 = None
        cif236 = None

        hyperlink237 = None

        connect_list239 = None

        end240 = None

        transition241 = None


        CONNECT238_tree = None
        stream_CONNECT = RewriteRuleTokenStream(self._adaptor, "token CONNECT")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_connect_list = RewriteRuleSubtreeStream(self._adaptor, "rule connect_list")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:433:9: ( ( cif )? ( hyperlink )? CONNECT ( connect_list )? end ( transition )? -> ^( CONNECT ( cif )? ( hyperlink )? ( connect_list )? ( end )? ( transition )? ) )
                # sdl92.g:433:17: ( cif )? ( hyperlink )? CONNECT ( connect_list )? end ( transition )?
                pass 
                # sdl92.g:433:17: ( cif )?
                alt69 = 2
                LA69_0 = self.input.LA(1)

                if (LA69_0 == 217) :
                    LA69_1 = self.input.LA(2)

                    if (LA69_1 == ANSWER or LA69_1 == COMMENT or LA69_1 == CONNECT or LA69_1 == DECISION or LA69_1 == INPUT or (JOIN <= LA69_1 <= LABEL) or LA69_1 == NEXTSTATE or LA69_1 == OUTPUT or (PROCEDURE <= LA69_1 <= PROCEDURE_CALL) or (PROCESS <= LA69_1 <= PROVIDED) or LA69_1 == RETURN or LA69_1 == STATE or LA69_1 == STOP or LA69_1 == TASK or LA69_1 == TEXT or LA69_1 == START) :
                        alt69 = 1
                if alt69 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_connect_part5112)
                    cif236 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif236.tree)



                # sdl92.g:434:17: ( hyperlink )?
                alt70 = 2
                LA70_0 = self.input.LA(1)

                if (LA70_0 == 217) :
                    alt70 = 1
                if alt70 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_connect_part5131)
                    hyperlink237 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink237.tree)



                CONNECT238=self.match(self.input, CONNECT, self.FOLLOW_CONNECT_in_connect_part5150) 
                if self._state.backtracking == 0:
                    stream_CONNECT.add(CONNECT238)
                # sdl92.g:435:25: ( connect_list )?
                alt71 = 2
                LA71_0 = self.input.LA(1)

                if (LA71_0 == ASTERISK or LA71_0 == ID) :
                    alt71 = 1
                if alt71 == 1:
                    # sdl92.g:0:0: connect_list
                    pass 
                    self._state.following.append(self.FOLLOW_connect_list_in_connect_part5152)
                    connect_list239 = self.connect_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_connect_list.add(connect_list239.tree)



                self._state.following.append(self.FOLLOW_end_in_connect_part5155)
                end240 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end240.tree)
                # sdl92.g:436:17: ( transition )?
                alt72 = 2
                alt72 = self.dfa72.predict(self.input)
                if alt72 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_connect_part5173)
                    transition241 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition241.tree)




                # AST Rewrite
                # elements: transition, hyperlink, end, cif, connect_list, CONNECT
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 437:9: -> ^( CONNECT ( cif )? ( hyperlink )? ( connect_list )? ( end )? ( transition )? )
                    # sdl92.g:437:17: ^( CONNECT ( cif )? ( hyperlink )? ( connect_list )? ( end )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_CONNECT.nextNode(), root_1)

                    # sdl92.g:437:27: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:437:32: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:437:43: ( connect_list )?
                    if stream_connect_list.hasNext():
                        self._adaptor.addChild(root_1, stream_connect_list.nextTree())


                    stream_connect_list.reset();
                    # sdl92.g:437:57: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    # sdl92.g:437:62: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "connect_part"

    class connect_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.connect_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "connect_list"
    # sdl92.g:440:1: connect_list : ( state_exit_point_name ( ',' state_exit_point_name )* -> ( state_exit_point_name )+ | ASTERISK );
    def connect_list(self, ):

        retval = self.connect_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal243 = None
        ASTERISK245 = None
        state_exit_point_name242 = None

        state_exit_point_name244 = None


        char_literal243_tree = None
        ASTERISK245_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_state_exit_point_name = RewriteRuleSubtreeStream(self._adaptor, "rule state_exit_point_name")
        try:
            try:
                # sdl92.g:441:9: ( state_exit_point_name ( ',' state_exit_point_name )* -> ( state_exit_point_name )+ | ASTERISK )
                alt74 = 2
                LA74_0 = self.input.LA(1)

                if (LA74_0 == ID) :
                    alt74 = 1
                elif (LA74_0 == ASTERISK) :
                    alt74 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 74, 0, self.input)

                    raise nvae

                if alt74 == 1:
                    # sdl92.g:441:17: state_exit_point_name ( ',' state_exit_point_name )*
                    pass 
                    self._state.following.append(self.FOLLOW_state_exit_point_name_in_connect_list5231)
                    state_exit_point_name242 = self.state_exit_point_name()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_state_exit_point_name.add(state_exit_point_name242.tree)
                    # sdl92.g:441:39: ( ',' state_exit_point_name )*
                    while True: #loop73
                        alt73 = 2
                        LA73_0 = self.input.LA(1)

                        if (LA73_0 == COMMA) :
                            alt73 = 1


                        if alt73 == 1:
                            # sdl92.g:441:40: ',' state_exit_point_name
                            pass 
                            char_literal243=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_connect_list5234) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal243)
                            self._state.following.append(self.FOLLOW_state_exit_point_name_in_connect_list5236)
                            state_exit_point_name244 = self.state_exit_point_name()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_state_exit_point_name.add(state_exit_point_name244.tree)


                        else:
                            break #loop73

                    # AST Rewrite
                    # elements: state_exit_point_name
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 442:17: -> ( state_exit_point_name )+
                        # sdl92.g:442:20: ( state_exit_point_name )+
                        if not (stream_state_exit_point_name.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_state_exit_point_name.hasNext():
                            self._adaptor.addChild(root_0, stream_state_exit_point_name.nextTree())


                        stream_state_exit_point_name.reset()



                        retval.tree = root_0


                elif alt74 == 2:
                    # sdl92.g:443:19: ASTERISK
                    pass 
                    root_0 = self._adaptor.nil()

                    ASTERISK245=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_connect_list5279)
                    if self._state.backtracking == 0:

                        ASTERISK245_tree = self._adaptor.createWithPayload(ASTERISK245)
                        self._adaptor.addChild(root_0, ASTERISK245_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "connect_list"

    class spontaneous_transition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.spontaneous_transition_return, self).__init__()

            self.tree = None




    # $ANTLR start "spontaneous_transition"
    # sdl92.g:446:1: spontaneous_transition : ( cif )? ( hyperlink )? INPUT NONE end ( enabling_condition )? transition -> ^( INPUT_NONE ( cif )? ( hyperlink )? transition ) ;
    def spontaneous_transition(self, ):

        retval = self.spontaneous_transition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        INPUT248 = None
        NONE249 = None
        cif246 = None

        hyperlink247 = None

        end250 = None

        enabling_condition251 = None

        transition252 = None


        INPUT248_tree = None
        NONE249_tree = None
        stream_INPUT = RewriteRuleTokenStream(self._adaptor, "token INPUT")
        stream_NONE = RewriteRuleTokenStream(self._adaptor, "token NONE")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_enabling_condition = RewriteRuleSubtreeStream(self._adaptor, "rule enabling_condition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:447:9: ( ( cif )? ( hyperlink )? INPUT NONE end ( enabling_condition )? transition -> ^( INPUT_NONE ( cif )? ( hyperlink )? transition ) )
                # sdl92.g:447:17: ( cif )? ( hyperlink )? INPUT NONE end ( enabling_condition )? transition
                pass 
                # sdl92.g:447:17: ( cif )?
                alt75 = 2
                LA75_0 = self.input.LA(1)

                if (LA75_0 == 217) :
                    LA75_1 = self.input.LA(2)

                    if (LA75_1 == ANSWER or LA75_1 == COMMENT or LA75_1 == CONNECT or LA75_1 == DECISION or LA75_1 == INPUT or (JOIN <= LA75_1 <= LABEL) or LA75_1 == NEXTSTATE or LA75_1 == OUTPUT or (PROCEDURE <= LA75_1 <= PROCEDURE_CALL) or (PROCESS <= LA75_1 <= PROVIDED) or LA75_1 == RETURN or LA75_1 == STATE or LA75_1 == STOP or LA75_1 == TASK or LA75_1 == TEXT or LA75_1 == START) :
                        alt75 = 1
                if alt75 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_spontaneous_transition5302)
                    cif246 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif246.tree)



                # sdl92.g:448:17: ( hyperlink )?
                alt76 = 2
                LA76_0 = self.input.LA(1)

                if (LA76_0 == 217) :
                    alt76 = 1
                if alt76 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_spontaneous_transition5321)
                    hyperlink247 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink247.tree)



                INPUT248=self.match(self.input, INPUT, self.FOLLOW_INPUT_in_spontaneous_transition5340) 
                if self._state.backtracking == 0:
                    stream_INPUT.add(INPUT248)
                NONE249=self.match(self.input, NONE, self.FOLLOW_NONE_in_spontaneous_transition5342) 
                if self._state.backtracking == 0:
                    stream_NONE.add(NONE249)
                self._state.following.append(self.FOLLOW_end_in_spontaneous_transition5344)
                end250 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end250.tree)
                # sdl92.g:450:17: ( enabling_condition )?
                alt77 = 2
                LA77_0 = self.input.LA(1)

                if (LA77_0 == PROVIDED) :
                    alt77 = 1
                if alt77 == 1:
                    # sdl92.g:0:0: enabling_condition
                    pass 
                    self._state.following.append(self.FOLLOW_enabling_condition_in_spontaneous_transition5362)
                    enabling_condition251 = self.enabling_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_enabling_condition.add(enabling_condition251.tree)



                self._state.following.append(self.FOLLOW_transition_in_spontaneous_transition5381)
                transition252 = self.transition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_transition.add(transition252.tree)

                # AST Rewrite
                # elements: cif, transition, hyperlink
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 452:9: -> ^( INPUT_NONE ( cif )? ( hyperlink )? transition )
                    # sdl92.g:452:17: ^( INPUT_NONE ( cif )? ( hyperlink )? transition )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(INPUT_NONE, "INPUT_NONE"), root_1)

                    # sdl92.g:452:30: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:452:35: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    self._adaptor.addChild(root_1, stream_transition.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "spontaneous_transition"

    class enabling_condition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.enabling_condition_return, self).__init__()

            self.tree = None




    # $ANTLR start "enabling_condition"
    # sdl92.g:455:1: enabling_condition : PROVIDED expression end -> ^( PROVIDED expression ) ;
    def enabling_condition(self, ):

        retval = self.enabling_condition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PROVIDED253 = None
        expression254 = None

        end255 = None


        PROVIDED253_tree = None
        stream_PROVIDED = RewriteRuleTokenStream(self._adaptor, "token PROVIDED")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:456:9: ( PROVIDED expression end -> ^( PROVIDED expression ) )
                # sdl92.g:456:17: PROVIDED expression end
                pass 
                PROVIDED253=self.match(self.input, PROVIDED, self.FOLLOW_PROVIDED_in_enabling_condition5431) 
                if self._state.backtracking == 0:
                    stream_PROVIDED.add(PROVIDED253)
                self._state.following.append(self.FOLLOW_expression_in_enabling_condition5433)
                expression254 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression254.tree)
                self._state.following.append(self.FOLLOW_end_in_enabling_condition5435)
                end255 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end255.tree)

                # AST Rewrite
                # elements: expression, PROVIDED
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 457:9: -> ^( PROVIDED expression )
                    # sdl92.g:457:17: ^( PROVIDED expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PROVIDED.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "enabling_condition"

    class continuous_signal_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.continuous_signal_return, self).__init__()

            self.tree = None




    # $ANTLR start "continuous_signal"
    # sdl92.g:460:1: continuous_signal : PROVIDED expression end ( PRIORITY integer_literal_name= INT end )? transition -> ^( PROVIDED expression ( $integer_literal_name)? transition ) ;
    def continuous_signal(self, ):

        retval = self.continuous_signal_return()
        retval.start = self.input.LT(1)

        root_0 = None

        integer_literal_name = None
        PROVIDED256 = None
        PRIORITY259 = None
        expression257 = None

        end258 = None

        end260 = None

        transition261 = None


        integer_literal_name_tree = None
        PROVIDED256_tree = None
        PRIORITY259_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_PRIORITY = RewriteRuleTokenStream(self._adaptor, "token PRIORITY")
        stream_PROVIDED = RewriteRuleTokenStream(self._adaptor, "token PROVIDED")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:461:9: ( PROVIDED expression end ( PRIORITY integer_literal_name= INT end )? transition -> ^( PROVIDED expression ( $integer_literal_name)? transition ) )
                # sdl92.g:461:17: PROVIDED expression end ( PRIORITY integer_literal_name= INT end )? transition
                pass 
                PROVIDED256=self.match(self.input, PROVIDED, self.FOLLOW_PROVIDED_in_continuous_signal5479) 
                if self._state.backtracking == 0:
                    stream_PROVIDED.add(PROVIDED256)
                self._state.following.append(self.FOLLOW_expression_in_continuous_signal5481)
                expression257 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression257.tree)
                self._state.following.append(self.FOLLOW_end_in_continuous_signal5483)
                end258 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end258.tree)
                # sdl92.g:462:17: ( PRIORITY integer_literal_name= INT end )?
                alt78 = 2
                LA78_0 = self.input.LA(1)

                if (LA78_0 == PRIORITY) :
                    alt78 = 1
                if alt78 == 1:
                    # sdl92.g:462:18: PRIORITY integer_literal_name= INT end
                    pass 
                    PRIORITY259=self.match(self.input, PRIORITY, self.FOLLOW_PRIORITY_in_continuous_signal5502) 
                    if self._state.backtracking == 0:
                        stream_PRIORITY.add(PRIORITY259)
                    integer_literal_name=self.match(self.input, INT, self.FOLLOW_INT_in_continuous_signal5506) 
                    if self._state.backtracking == 0:
                        stream_INT.add(integer_literal_name)
                    self._state.following.append(self.FOLLOW_end_in_continuous_signal5508)
                    end260 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end260.tree)



                self._state.following.append(self.FOLLOW_transition_in_continuous_signal5528)
                transition261 = self.transition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_transition.add(transition261.tree)

                # AST Rewrite
                # elements: integer_literal_name, PROVIDED, transition, expression
                # token labels: integer_literal_name
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_integer_literal_name = RewriteRuleTokenStream(self._adaptor, "token integer_literal_name", integer_literal_name)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 464:9: -> ^( PROVIDED expression ( $integer_literal_name)? transition )
                    # sdl92.g:464:17: ^( PROVIDED expression ( $integer_literal_name)? transition )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PROVIDED.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())
                    # sdl92.g:464:39: ( $integer_literal_name)?
                    if stream_integer_literal_name.hasNext():
                        self._adaptor.addChild(root_1, stream_integer_literal_name.nextNode())


                    stream_integer_literal_name.reset();
                    self._adaptor.addChild(root_1, stream_transition.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "continuous_signal"

    class save_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.save_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "save_part"
    # sdl92.g:467:1: save_part : SAVE save_list end -> ^( SAVE save_list ) ;
    def save_part(self, ):

        retval = self.save_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SAVE262 = None
        save_list263 = None

        end264 = None


        SAVE262_tree = None
        stream_SAVE = RewriteRuleTokenStream(self._adaptor, "token SAVE")
        stream_save_list = RewriteRuleSubtreeStream(self._adaptor, "rule save_list")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:468:9: ( SAVE save_list end -> ^( SAVE save_list ) )
                # sdl92.g:468:17: SAVE save_list end
                pass 
                SAVE262=self.match(self.input, SAVE, self.FOLLOW_SAVE_in_save_part5578) 
                if self._state.backtracking == 0:
                    stream_SAVE.add(SAVE262)
                self._state.following.append(self.FOLLOW_save_list_in_save_part5580)
                save_list263 = self.save_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_save_list.add(save_list263.tree)
                self._state.following.append(self.FOLLOW_end_in_save_part5598)
                end264 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end264.tree)

                # AST Rewrite
                # elements: SAVE, save_list
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 470:9: -> ^( SAVE save_list )
                    # sdl92.g:470:17: ^( SAVE save_list )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_SAVE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_save_list.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "save_part"

    class save_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.save_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "save_list"
    # sdl92.g:473:1: save_list : ( signal_list | asterisk_save_list );
    def save_list(self, ):

        retval = self.save_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_list265 = None

        asterisk_save_list266 = None



        try:
            try:
                # sdl92.g:474:9: ( signal_list | asterisk_save_list )
                alt79 = 2
                LA79_0 = self.input.LA(1)

                if (LA79_0 == ID) :
                    alt79 = 1
                elif (LA79_0 == ASTERISK) :
                    alt79 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 79, 0, self.input)

                    raise nvae

                if alt79 == 1:
                    # sdl92.g:474:17: signal_list
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_signal_list_in_save_list5642)
                    signal_list265 = self.signal_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, signal_list265.tree)


                elif alt79 == 2:
                    # sdl92.g:475:19: asterisk_save_list
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_asterisk_save_list_in_save_list5662)
                    asterisk_save_list266 = self.asterisk_save_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, asterisk_save_list266.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "save_list"

    class asterisk_save_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.asterisk_save_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "asterisk_save_list"
    # sdl92.g:478:1: asterisk_save_list : ASTERISK ;
    def asterisk_save_list(self, ):

        retval = self.asterisk_save_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ASTERISK267 = None

        ASTERISK267_tree = None

        try:
            try:
                # sdl92.g:479:9: ( ASTERISK )
                # sdl92.g:479:17: ASTERISK
                pass 
                root_0 = self._adaptor.nil()

                ASTERISK267=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_asterisk_save_list5685)
                if self._state.backtracking == 0:

                    ASTERISK267_tree = self._adaptor.createWithPayload(ASTERISK267)
                    self._adaptor.addChild(root_0, ASTERISK267_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "asterisk_save_list"

    class signal_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_list"
    # sdl92.g:482:1: signal_list : signal_item ( ',' signal_item )* -> ^( SIGNAL_LIST ( signal_item )+ ) ;
    def signal_list(self, ):

        retval = self.signal_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal269 = None
        signal_item268 = None

        signal_item270 = None


        char_literal269_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_signal_item = RewriteRuleSubtreeStream(self._adaptor, "rule signal_item")
        try:
            try:
                # sdl92.g:483:9: ( signal_item ( ',' signal_item )* -> ^( SIGNAL_LIST ( signal_item )+ ) )
                # sdl92.g:483:17: signal_item ( ',' signal_item )*
                pass 
                self._state.following.append(self.FOLLOW_signal_item_in_signal_list5708)
                signal_item268 = self.signal_item()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_signal_item.add(signal_item268.tree)
                # sdl92.g:483:29: ( ',' signal_item )*
                while True: #loop80
                    alt80 = 2
                    LA80_0 = self.input.LA(1)

                    if (LA80_0 == COMMA) :
                        alt80 = 1


                    if alt80 == 1:
                        # sdl92.g:483:30: ',' signal_item
                        pass 
                        char_literal269=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_signal_list5711) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal269)
                        self._state.following.append(self.FOLLOW_signal_item_in_signal_list5713)
                        signal_item270 = self.signal_item()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_signal_item.add(signal_item270.tree)


                    else:
                        break #loop80

                # AST Rewrite
                # elements: signal_item
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 484:9: -> ^( SIGNAL_LIST ( signal_item )+ )
                    # sdl92.g:484:17: ^( SIGNAL_LIST ( signal_item )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SIGNAL_LIST, "SIGNAL_LIST"), root_1)

                    # sdl92.g:484:31: ( signal_item )+
                    if not (stream_signal_item.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_signal_item.hasNext():
                        self._adaptor.addChild(root_1, stream_signal_item.nextTree())


                    stream_signal_item.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_list"

    class signal_item_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_item_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_item"
    # sdl92.g:490:1: signal_item : signal_id ;
    def signal_item(self, ):

        retval = self.signal_item_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_id271 = None



        try:
            try:
                # sdl92.g:491:9: ( signal_id )
                # sdl92.g:491:17: signal_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_signal_id_in_signal_item5763)
                signal_id271 = self.signal_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, signal_id271.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_item"

    class input_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.input_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "input_part"
    # sdl92.g:511:1: input_part : ( cif )? ( hyperlink )? INPUT inputlist end ( enabling_condition )? ( transition )? -> ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? ) ;
    def input_part(self, ):

        retval = self.input_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        INPUT274 = None
        cif272 = None

        hyperlink273 = None

        inputlist275 = None

        end276 = None

        enabling_condition277 = None

        transition278 = None


        INPUT274_tree = None
        stream_INPUT = RewriteRuleTokenStream(self._adaptor, "token INPUT")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_inputlist = RewriteRuleSubtreeStream(self._adaptor, "rule inputlist")
        stream_enabling_condition = RewriteRuleSubtreeStream(self._adaptor, "rule enabling_condition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:512:9: ( ( cif )? ( hyperlink )? INPUT inputlist end ( enabling_condition )? ( transition )? -> ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? ) )
                # sdl92.g:512:17: ( cif )? ( hyperlink )? INPUT inputlist end ( enabling_condition )? ( transition )?
                pass 
                # sdl92.g:512:17: ( cif )?
                alt81 = 2
                LA81_0 = self.input.LA(1)

                if (LA81_0 == 217) :
                    LA81_1 = self.input.LA(2)

                    if (LA81_1 == ANSWER or LA81_1 == COMMENT or LA81_1 == CONNECT or LA81_1 == DECISION or LA81_1 == INPUT or (JOIN <= LA81_1 <= LABEL) or LA81_1 == NEXTSTATE or LA81_1 == OUTPUT or (PROCEDURE <= LA81_1 <= PROCEDURE_CALL) or (PROCESS <= LA81_1 <= PROVIDED) or LA81_1 == RETURN or LA81_1 == STATE or LA81_1 == STOP or LA81_1 == TASK or LA81_1 == TEXT or LA81_1 == START) :
                        alt81 = 1
                if alt81 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_input_part5792)
                    cif272 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif272.tree)



                # sdl92.g:513:17: ( hyperlink )?
                alt82 = 2
                LA82_0 = self.input.LA(1)

                if (LA82_0 == 217) :
                    alt82 = 1
                if alt82 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_input_part5811)
                    hyperlink273 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink273.tree)



                INPUT274=self.match(self.input, INPUT, self.FOLLOW_INPUT_in_input_part5830) 
                if self._state.backtracking == 0:
                    stream_INPUT.add(INPUT274)
                self._state.following.append(self.FOLLOW_inputlist_in_input_part5832)
                inputlist275 = self.inputlist()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_inputlist.add(inputlist275.tree)
                self._state.following.append(self.FOLLOW_end_in_input_part5834)
                end276 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end276.tree)
                # sdl92.g:515:17: ( enabling_condition )?
                alt83 = 2
                alt83 = self.dfa83.predict(self.input)
                if alt83 == 1:
                    # sdl92.g:0:0: enabling_condition
                    pass 
                    self._state.following.append(self.FOLLOW_enabling_condition_in_input_part5852)
                    enabling_condition277 = self.enabling_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_enabling_condition.add(enabling_condition277.tree)



                # sdl92.g:516:17: ( transition )?
                alt84 = 2
                alt84 = self.dfa84.predict(self.input)
                if alt84 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_input_part5871)
                    transition278 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition278.tree)




                # AST Rewrite
                # elements: INPUT, enabling_condition, cif, hyperlink, end, transition, inputlist
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 517:9: -> ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? )
                    # sdl92.g:517:17: ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_INPUT.nextNode(), root_1)

                    # sdl92.g:517:25: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:517:30: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:517:41: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_inputlist.nextTree())
                    # sdl92.g:518:27: ( enabling_condition )?
                    if stream_enabling_condition.hasNext():
                        self._adaptor.addChild(root_1, stream_enabling_condition.nextTree())


                    stream_enabling_condition.reset();
                    # sdl92.g:518:47: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "input_part"

    class inputlist_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.inputlist_return, self).__init__()

            self.tree = None




    # $ANTLR start "inputlist"
    # sdl92.g:523:1: inputlist : ( ASTERISK | ( stimulus ( ',' stimulus )* ) -> ^( INPUTLIST ( stimulus )+ ) );
    def inputlist(self, ):

        retval = self.inputlist_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ASTERISK279 = None
        char_literal281 = None
        stimulus280 = None

        stimulus282 = None


        ASTERISK279_tree = None
        char_literal281_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_stimulus = RewriteRuleSubtreeStream(self._adaptor, "rule stimulus")
        try:
            try:
                # sdl92.g:524:9: ( ASTERISK | ( stimulus ( ',' stimulus )* ) -> ^( INPUTLIST ( stimulus )+ ) )
                alt86 = 2
                LA86_0 = self.input.LA(1)

                if (LA86_0 == ASTERISK) :
                    alt86 = 1
                elif (LA86_0 == ID) :
                    alt86 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 86, 0, self.input)

                    raise nvae

                if alt86 == 1:
                    # sdl92.g:524:17: ASTERISK
                    pass 
                    root_0 = self._adaptor.nil()

                    ASTERISK279=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_inputlist5949)
                    if self._state.backtracking == 0:

                        ASTERISK279_tree = self._adaptor.createWithPayload(ASTERISK279)
                        self._adaptor.addChild(root_0, ASTERISK279_tree)



                elif alt86 == 2:
                    # sdl92.g:525:19: ( stimulus ( ',' stimulus )* )
                    pass 
                    # sdl92.g:525:19: ( stimulus ( ',' stimulus )* )
                    # sdl92.g:525:20: stimulus ( ',' stimulus )*
                    pass 
                    self._state.following.append(self.FOLLOW_stimulus_in_inputlist5970)
                    stimulus280 = self.stimulus()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_stimulus.add(stimulus280.tree)
                    # sdl92.g:525:29: ( ',' stimulus )*
                    while True: #loop85
                        alt85 = 2
                        LA85_0 = self.input.LA(1)

                        if (LA85_0 == COMMA) :
                            alt85 = 1


                        if alt85 == 1:
                            # sdl92.g:525:30: ',' stimulus
                            pass 
                            char_literal281=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_inputlist5973) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal281)
                            self._state.following.append(self.FOLLOW_stimulus_in_inputlist5975)
                            stimulus282 = self.stimulus()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_stimulus.add(stimulus282.tree)


                        else:
                            break #loop85




                    # AST Rewrite
                    # elements: stimulus
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 526:9: -> ^( INPUTLIST ( stimulus )+ )
                        # sdl92.g:526:17: ^( INPUTLIST ( stimulus )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(INPUTLIST, "INPUTLIST"), root_1)

                        # sdl92.g:526:29: ( stimulus )+
                        if not (stream_stimulus.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_stimulus.hasNext():
                            self._adaptor.addChild(root_1, stream_stimulus.nextTree())


                        stream_stimulus.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "inputlist"

    class stimulus_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.stimulus_return, self).__init__()

            self.tree = None




    # $ANTLR start "stimulus"
    # sdl92.g:529:1: stimulus : stimulus_id ( input_params )? ;
    def stimulus(self, ):

        retval = self.stimulus_return()
        retval.start = self.input.LT(1)

        root_0 = None

        stimulus_id283 = None

        input_params284 = None



        try:
            try:
                # sdl92.g:530:9: ( stimulus_id ( input_params )? )
                # sdl92.g:530:17: stimulus_id ( input_params )?
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_stimulus_id_in_stimulus6023)
                stimulus_id283 = self.stimulus_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, stimulus_id283.tree)
                # sdl92.g:530:29: ( input_params )?
                alt87 = 2
                LA87_0 = self.input.LA(1)

                if (LA87_0 == L_PAREN) :
                    alt87 = 1
                if alt87 == 1:
                    # sdl92.g:0:0: input_params
                    pass 
                    self._state.following.append(self.FOLLOW_input_params_in_stimulus6025)
                    input_params284 = self.input_params()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, input_params284.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "stimulus"

    class input_params_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.input_params_return, self).__init__()

            self.tree = None




    # $ANTLR start "input_params"
    # sdl92.g:533:1: input_params : L_PAREN variable_id ( ',' variable_id )* R_PAREN -> ^( PARAMS ( variable_id )+ ) ;
    def input_params(self, ):

        retval = self.input_params_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN285 = None
        char_literal287 = None
        R_PAREN289 = None
        variable_id286 = None

        variable_id288 = None


        L_PAREN285_tree = None
        char_literal287_tree = None
        R_PAREN289_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        try:
            try:
                # sdl92.g:534:9: ( L_PAREN variable_id ( ',' variable_id )* R_PAREN -> ^( PARAMS ( variable_id )+ ) )
                # sdl92.g:534:17: L_PAREN variable_id ( ',' variable_id )* R_PAREN
                pass 
                L_PAREN285=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_input_params6049) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN285)
                self._state.following.append(self.FOLLOW_variable_id_in_input_params6051)
                variable_id286 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id286.tree)
                # sdl92.g:534:37: ( ',' variable_id )*
                while True: #loop88
                    alt88 = 2
                    LA88_0 = self.input.LA(1)

                    if (LA88_0 == COMMA) :
                        alt88 = 1


                    if alt88 == 1:
                        # sdl92.g:534:38: ',' variable_id
                        pass 
                        char_literal287=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_input_params6054) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal287)
                        self._state.following.append(self.FOLLOW_variable_id_in_input_params6056)
                        variable_id288 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id288.tree)


                    else:
                        break #loop88
                R_PAREN289=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_input_params6060) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN289)

                # AST Rewrite
                # elements: variable_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 535:9: -> ^( PARAMS ( variable_id )+ )
                    # sdl92.g:535:17: ^( PARAMS ( variable_id )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAMS, "PARAMS"), root_1)

                    # sdl92.g:535:26: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "input_params"

    class transition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.transition_return, self).__init__()

            self.tree = None




    # $ANTLR start "transition"
    # sdl92.g:538:1: transition : ( ( action )+ ( label )? ( terminator_statement )? -> ^( TRANSITION ( action )+ ( label )? ( terminator_statement )? ) | terminator_statement -> ^( TRANSITION terminator_statement ) );
    def transition(self, ):

        retval = self.transition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        action290 = None

        label291 = None

        terminator_statement292 = None

        terminator_statement293 = None


        stream_terminator_statement = RewriteRuleSubtreeStream(self._adaptor, "rule terminator_statement")
        stream_action = RewriteRuleSubtreeStream(self._adaptor, "rule action")
        stream_label = RewriteRuleSubtreeStream(self._adaptor, "rule label")
        try:
            try:
                # sdl92.g:539:9: ( ( action )+ ( label )? ( terminator_statement )? -> ^( TRANSITION ( action )+ ( label )? ( terminator_statement )? ) | terminator_statement -> ^( TRANSITION terminator_statement ) )
                alt92 = 2
                alt92 = self.dfa92.predict(self.input)
                if alt92 == 1:
                    # sdl92.g:539:17: ( action )+ ( label )? ( terminator_statement )?
                    pass 
                    # sdl92.g:539:17: ( action )+
                    cnt89 = 0
                    while True: #loop89
                        alt89 = 2
                        alt89 = self.dfa89.predict(self.input)
                        if alt89 == 1:
                            # sdl92.g:0:0: action
                            pass 
                            self._state.following.append(self.FOLLOW_action_in_transition6105)
                            action290 = self.action()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_action.add(action290.tree)


                        else:
                            if cnt89 >= 1:
                                break #loop89

                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            eee = EarlyExitException(89, self.input)
                            raise eee

                        cnt89 += 1
                    # sdl92.g:539:25: ( label )?
                    alt90 = 2
                    alt90 = self.dfa90.predict(self.input)
                    if alt90 == 1:
                        # sdl92.g:0:0: label
                        pass 
                        self._state.following.append(self.FOLLOW_label_in_transition6108)
                        label291 = self.label()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_label.add(label291.tree)



                    # sdl92.g:539:32: ( terminator_statement )?
                    alt91 = 2
                    alt91 = self.dfa91.predict(self.input)
                    if alt91 == 1:
                        # sdl92.g:0:0: terminator_statement
                        pass 
                        self._state.following.append(self.FOLLOW_terminator_statement_in_transition6111)
                        terminator_statement292 = self.terminator_statement()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_terminator_statement.add(terminator_statement292.tree)




                    # AST Rewrite
                    # elements: label, terminator_statement, action
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 540:9: -> ^( TRANSITION ( action )+ ( label )? ( terminator_statement )? )
                        # sdl92.g:540:17: ^( TRANSITION ( action )+ ( label )? ( terminator_statement )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TRANSITION, "TRANSITION"), root_1)

                        # sdl92.g:540:30: ( action )+
                        if not (stream_action.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_action.hasNext():
                            self._adaptor.addChild(root_1, stream_action.nextTree())


                        stream_action.reset()
                        # sdl92.g:540:38: ( label )?
                        if stream_label.hasNext():
                            self._adaptor.addChild(root_1, stream_label.nextTree())


                        stream_label.reset();
                        # sdl92.g:540:45: ( terminator_statement )?
                        if stream_terminator_statement.hasNext():
                            self._adaptor.addChild(root_1, stream_terminator_statement.nextTree())


                        stream_terminator_statement.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt92 == 2:
                    # sdl92.g:541:19: terminator_statement
                    pass 
                    self._state.following.append(self.FOLLOW_terminator_statement_in_transition6160)
                    terminator_statement293 = self.terminator_statement()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_terminator_statement.add(terminator_statement293.tree)

                    # AST Rewrite
                    # elements: terminator_statement
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 542:9: -> ^( TRANSITION terminator_statement )
                        # sdl92.g:542:17: ^( TRANSITION terminator_statement )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TRANSITION, "TRANSITION"), root_1)

                        self._adaptor.addChild(root_1, stream_terminator_statement.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "transition"

    class action_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.action_return, self).__init__()

            self.tree = None




    # $ANTLR start "action"
    # sdl92.g:545:1: action : ( label )? ( task | task_body | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call ) ;
    def action(self, ):

        retval = self.action_return()
        retval.start = self.input.LT(1)

        root_0 = None

        label294 = None

        task295 = None

        task_body296 = None

        output297 = None

        create_request298 = None

        decision299 = None

        transition_option300 = None

        set_timer301 = None

        reset_timer302 = None

        export303 = None

        procedure_call304 = None



        try:
            try:
                # sdl92.g:546:9: ( ( label )? ( task | task_body | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call ) )
                # sdl92.g:546:17: ( label )? ( task | task_body | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call )
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:546:17: ( label )?
                alt93 = 2
                alt93 = self.dfa93.predict(self.input)
                if alt93 == 1:
                    # sdl92.g:0:0: label
                    pass 
                    self._state.following.append(self.FOLLOW_label_in_action6204)
                    label294 = self.label()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, label294.tree)



                # sdl92.g:547:17: ( task | task_body | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call )
                alt94 = 10
                alt94 = self.dfa94.predict(self.input)
                if alt94 == 1:
                    # sdl92.g:547:18: task
                    pass 
                    self._state.following.append(self.FOLLOW_task_in_action6224)
                    task295 = self.task()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, task295.tree)


                elif alt94 == 2:
                    # sdl92.g:548:19: task_body
                    pass 
                    self._state.following.append(self.FOLLOW_task_body_in_action6244)
                    task_body296 = self.task_body()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, task_body296.tree)


                elif alt94 == 3:
                    # sdl92.g:549:19: output
                    pass 
                    self._state.following.append(self.FOLLOW_output_in_action6264)
                    output297 = self.output()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, output297.tree)


                elif alt94 == 4:
                    # sdl92.g:550:19: create_request
                    pass 
                    self._state.following.append(self.FOLLOW_create_request_in_action6284)
                    create_request298 = self.create_request()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, create_request298.tree)


                elif alt94 == 5:
                    # sdl92.g:551:19: decision
                    pass 
                    self._state.following.append(self.FOLLOW_decision_in_action6304)
                    decision299 = self.decision()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, decision299.tree)


                elif alt94 == 6:
                    # sdl92.g:552:19: transition_option
                    pass 
                    self._state.following.append(self.FOLLOW_transition_option_in_action6324)
                    transition_option300 = self.transition_option()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, transition_option300.tree)


                elif alt94 == 7:
                    # sdl92.g:553:19: set_timer
                    pass 
                    self._state.following.append(self.FOLLOW_set_timer_in_action6344)
                    set_timer301 = self.set_timer()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, set_timer301.tree)


                elif alt94 == 8:
                    # sdl92.g:554:19: reset_timer
                    pass 
                    self._state.following.append(self.FOLLOW_reset_timer_in_action6364)
                    reset_timer302 = self.reset_timer()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, reset_timer302.tree)


                elif alt94 == 9:
                    # sdl92.g:555:19: export
                    pass 
                    self._state.following.append(self.FOLLOW_export_in_action6384)
                    export303 = self.export()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, export303.tree)


                elif alt94 == 10:
                    # sdl92.g:556:19: procedure_call
                    pass 
                    self._state.following.append(self.FOLLOW_procedure_call_in_action6409)
                    procedure_call304 = self.procedure_call()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, procedure_call304.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "action"

    class export_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.export_return, self).__init__()

            self.tree = None




    # $ANTLR start "export"
    # sdl92.g:558:1: export : EXPORT L_PAREN variable_id ( COMMA variable_id )* R_PAREN end -> ^( EXPORT ( variable_id )+ ) ;
    def export(self, ):

        retval = self.export_return()
        retval.start = self.input.LT(1)

        root_0 = None

        EXPORT305 = None
        L_PAREN306 = None
        COMMA308 = None
        R_PAREN310 = None
        variable_id307 = None

        variable_id309 = None

        end311 = None


        EXPORT305_tree = None
        L_PAREN306_tree = None
        COMMA308_tree = None
        R_PAREN310_tree = None
        stream_EXPORT = RewriteRuleTokenStream(self._adaptor, "token EXPORT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:559:9: ( EXPORT L_PAREN variable_id ( COMMA variable_id )* R_PAREN end -> ^( EXPORT ( variable_id )+ ) )
                # sdl92.g:559:17: EXPORT L_PAREN variable_id ( COMMA variable_id )* R_PAREN end
                pass 
                EXPORT305=self.match(self.input, EXPORT, self.FOLLOW_EXPORT_in_export6432) 
                if self._state.backtracking == 0:
                    stream_EXPORT.add(EXPORT305)
                L_PAREN306=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_export6450) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN306)
                self._state.following.append(self.FOLLOW_variable_id_in_export6452)
                variable_id307 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id307.tree)
                # sdl92.g:560:37: ( COMMA variable_id )*
                while True: #loop95
                    alt95 = 2
                    LA95_0 = self.input.LA(1)

                    if (LA95_0 == COMMA) :
                        alt95 = 1


                    if alt95 == 1:
                        # sdl92.g:560:38: COMMA variable_id
                        pass 
                        COMMA308=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_export6455) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(COMMA308)
                        self._state.following.append(self.FOLLOW_variable_id_in_export6457)
                        variable_id309 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id309.tree)


                    else:
                        break #loop95
                R_PAREN310=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_export6461) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN310)
                self._state.following.append(self.FOLLOW_end_in_export6479)
                end311 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end311.tree)

                # AST Rewrite
                # elements: EXPORT, variable_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 562:9: -> ^( EXPORT ( variable_id )+ )
                    # sdl92.g:562:17: ^( EXPORT ( variable_id )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_EXPORT.nextNode(), root_1)

                    # sdl92.g:562:26: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "export"

    class procedure_call_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_call_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure_call"
    # sdl92.g:573:1: procedure_call : ( cif )? ( hyperlink )? CALL procedure_call_body end -> ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body ) ;
    def procedure_call(self, ):

        retval = self.procedure_call_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CALL314 = None
        cif312 = None

        hyperlink313 = None

        procedure_call_body315 = None

        end316 = None


        CALL314_tree = None
        stream_CALL = RewriteRuleTokenStream(self._adaptor, "token CALL")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_procedure_call_body = RewriteRuleSubtreeStream(self._adaptor, "rule procedure_call_body")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:574:9: ( ( cif )? ( hyperlink )? CALL procedure_call_body end -> ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body ) )
                # sdl92.g:574:17: ( cif )? ( hyperlink )? CALL procedure_call_body end
                pass 
                # sdl92.g:574:17: ( cif )?
                alt96 = 2
                LA96_0 = self.input.LA(1)

                if (LA96_0 == 217) :
                    LA96_1 = self.input.LA(2)

                    if (LA96_1 == ANSWER or LA96_1 == COMMENT or LA96_1 == CONNECT or LA96_1 == DECISION or LA96_1 == INPUT or (JOIN <= LA96_1 <= LABEL) or LA96_1 == NEXTSTATE or LA96_1 == OUTPUT or (PROCEDURE <= LA96_1 <= PROCEDURE_CALL) or (PROCESS <= LA96_1 <= PROVIDED) or LA96_1 == RETURN or LA96_1 == STATE or LA96_1 == STOP or LA96_1 == TASK or LA96_1 == TEXT or LA96_1 == START) :
                        alt96 = 1
                if alt96 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_procedure_call6527)
                    cif312 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif312.tree)



                # sdl92.g:575:17: ( hyperlink )?
                alt97 = 2
                LA97_0 = self.input.LA(1)

                if (LA97_0 == 217) :
                    alt97 = 1
                if alt97 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_procedure_call6546)
                    hyperlink313 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink313.tree)



                CALL314=self.match(self.input, CALL, self.FOLLOW_CALL_in_procedure_call6565) 
                if self._state.backtracking == 0:
                    stream_CALL.add(CALL314)
                self._state.following.append(self.FOLLOW_procedure_call_body_in_procedure_call6567)
                procedure_call_body315 = self.procedure_call_body()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_procedure_call_body.add(procedure_call_body315.tree)
                self._state.following.append(self.FOLLOW_end_in_procedure_call6569)
                end316 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end316.tree)

                # AST Rewrite
                # elements: procedure_call_body, cif, end, hyperlink
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 577:9: -> ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body )
                    # sdl92.g:577:17: ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PROCEDURE_CALL, "PROCEDURE_CALL"), root_1)

                    # sdl92.g:577:34: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:577:39: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:577:50: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_procedure_call_body.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure_call"

    class procedure_call_body_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_call_body_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure_call_body"
    # sdl92.g:580:1: procedure_call_body : procedure_id ( actual_parameters )? -> ^( OUTPUT_BODY procedure_id ( actual_parameters )? ) ;
    def procedure_call_body(self, ):

        retval = self.procedure_call_body_return()
        retval.start = self.input.LT(1)

        root_0 = None

        procedure_id317 = None

        actual_parameters318 = None


        stream_procedure_id = RewriteRuleSubtreeStream(self._adaptor, "rule procedure_id")
        stream_actual_parameters = RewriteRuleSubtreeStream(self._adaptor, "rule actual_parameters")
        try:
            try:
                # sdl92.g:581:9: ( procedure_id ( actual_parameters )? -> ^( OUTPUT_BODY procedure_id ( actual_parameters )? ) )
                # sdl92.g:581:17: procedure_id ( actual_parameters )?
                pass 
                self._state.following.append(self.FOLLOW_procedure_id_in_procedure_call_body6622)
                procedure_id317 = self.procedure_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_procedure_id.add(procedure_id317.tree)
                # sdl92.g:581:30: ( actual_parameters )?
                alt98 = 2
                LA98_0 = self.input.LA(1)

                if (LA98_0 == L_PAREN) :
                    alt98 = 1
                if alt98 == 1:
                    # sdl92.g:0:0: actual_parameters
                    pass 
                    self._state.following.append(self.FOLLOW_actual_parameters_in_procedure_call_body6624)
                    actual_parameters318 = self.actual_parameters()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_actual_parameters.add(actual_parameters318.tree)




                # AST Rewrite
                # elements: actual_parameters, procedure_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 582:9: -> ^( OUTPUT_BODY procedure_id ( actual_parameters )? )
                    # sdl92.g:582:17: ^( OUTPUT_BODY procedure_id ( actual_parameters )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OUTPUT_BODY, "OUTPUT_BODY"), root_1)

                    self._adaptor.addChild(root_1, stream_procedure_id.nextTree())
                    # sdl92.g:582:44: ( actual_parameters )?
                    if stream_actual_parameters.hasNext():
                        self._adaptor.addChild(root_1, stream_actual_parameters.nextTree())


                    stream_actual_parameters.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure_call_body"

    class set_timer_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.set_timer_return, self).__init__()

            self.tree = None




    # $ANTLR start "set_timer"
    # sdl92.g:585:1: set_timer : SET set_statement ( COMMA set_statement )* end -> ( set_statement )+ ;
    def set_timer(self, ):

        retval = self.set_timer_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SET319 = None
        COMMA321 = None
        set_statement320 = None

        set_statement322 = None

        end323 = None


        SET319_tree = None
        COMMA321_tree = None
        stream_SET = RewriteRuleTokenStream(self._adaptor, "token SET")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_set_statement = RewriteRuleSubtreeStream(self._adaptor, "rule set_statement")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:586:9: ( SET set_statement ( COMMA set_statement )* end -> ( set_statement )+ )
                # sdl92.g:586:17: SET set_statement ( COMMA set_statement )* end
                pass 
                SET319=self.match(self.input, SET, self.FOLLOW_SET_in_set_timer6672) 
                if self._state.backtracking == 0:
                    stream_SET.add(SET319)
                self._state.following.append(self.FOLLOW_set_statement_in_set_timer6674)
                set_statement320 = self.set_statement()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_set_statement.add(set_statement320.tree)
                # sdl92.g:586:35: ( COMMA set_statement )*
                while True: #loop99
                    alt99 = 2
                    LA99_0 = self.input.LA(1)

                    if (LA99_0 == COMMA) :
                        alt99 = 1


                    if alt99 == 1:
                        # sdl92.g:586:36: COMMA set_statement
                        pass 
                        COMMA321=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_set_timer6677) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(COMMA321)
                        self._state.following.append(self.FOLLOW_set_statement_in_set_timer6679)
                        set_statement322 = self.set_statement()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_set_statement.add(set_statement322.tree)


                    else:
                        break #loop99
                self._state.following.append(self.FOLLOW_end_in_set_timer6699)
                end323 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end323.tree)

                # AST Rewrite
                # elements: set_statement
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 588:9: -> ( set_statement )+
                    # sdl92.g:588:17: ( set_statement )+
                    if not (stream_set_statement.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_set_statement.hasNext():
                        self._adaptor.addChild(root_0, stream_set_statement.nextTree())


                    stream_set_statement.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "set_timer"

    class set_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.set_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "set_statement"
    # sdl92.g:591:1: set_statement : L_PAREN ( expression COMMA )? timer_id R_PAREN -> ^( SET ( expression )? timer_id ) ;
    def set_statement(self, ):

        retval = self.set_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN324 = None
        COMMA326 = None
        R_PAREN328 = None
        expression325 = None

        timer_id327 = None


        L_PAREN324_tree = None
        COMMA326_tree = None
        R_PAREN328_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_timer_id = RewriteRuleSubtreeStream(self._adaptor, "rule timer_id")
        try:
            try:
                # sdl92.g:592:9: ( L_PAREN ( expression COMMA )? timer_id R_PAREN -> ^( SET ( expression )? timer_id ) )
                # sdl92.g:592:17: L_PAREN ( expression COMMA )? timer_id R_PAREN
                pass 
                L_PAREN324=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_set_statement6740) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN324)
                # sdl92.g:592:25: ( expression COMMA )?
                alt100 = 2
                LA100_0 = self.input.LA(1)

                if (LA100_0 == BITSTR or LA100_0 == FLOAT or LA100_0 == IF or LA100_0 == OCTSTR or LA100_0 == STRING or LA100_0 == INT or LA100_0 == L_PAREN or LA100_0 == DASH or (NOT <= LA100_0 <= MINUS_INFINITY) or LA100_0 == L_BRACKET) :
                    alt100 = 1
                elif (LA100_0 == ID) :
                    LA100_2 = self.input.LA(2)

                    if (LA100_2 == IN or LA100_2 == AND or LA100_2 == ASTERISK or LA100_2 == L_PAREN or LA100_2 == COMMA or (EQ <= LA100_2 <= GE) or (IMPLIES <= LA100_2 <= REM) or (212 <= LA100_2 <= 213)) :
                        alt100 = 1
                if alt100 == 1:
                    # sdl92.g:592:26: expression COMMA
                    pass 
                    self._state.following.append(self.FOLLOW_expression_in_set_statement6743)
                    expression325 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression325.tree)
                    COMMA326=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_set_statement6745) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA326)



                self._state.following.append(self.FOLLOW_timer_id_in_set_statement6749)
                timer_id327 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_timer_id.add(timer_id327.tree)
                R_PAREN328=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_set_statement6751) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN328)

                # AST Rewrite
                # elements: expression, timer_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 593:9: -> ^( SET ( expression )? timer_id )
                    # sdl92.g:593:17: ^( SET ( expression )? timer_id )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SET, "SET"), root_1)

                    # sdl92.g:593:23: ( expression )?
                    if stream_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_expression.nextTree())


                    stream_expression.reset();
                    self._adaptor.addChild(root_1, stream_timer_id.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "set_statement"

    class reset_timer_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.reset_timer_return, self).__init__()

            self.tree = None




    # $ANTLR start "reset_timer"
    # sdl92.g:597:1: reset_timer : RESET reset_statement ( ',' reset_statement )* end -> ( reset_statement )+ ;
    def reset_timer(self, ):

        retval = self.reset_timer_return()
        retval.start = self.input.LT(1)

        root_0 = None

        RESET329 = None
        char_literal331 = None
        reset_statement330 = None

        reset_statement332 = None

        end333 = None


        RESET329_tree = None
        char_literal331_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_RESET = RewriteRuleTokenStream(self._adaptor, "token RESET")
        stream_reset_statement = RewriteRuleSubtreeStream(self._adaptor, "rule reset_statement")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:598:9: ( RESET reset_statement ( ',' reset_statement )* end -> ( reset_statement )+ )
                # sdl92.g:598:17: RESET reset_statement ( ',' reset_statement )* end
                pass 
                RESET329=self.match(self.input, RESET, self.FOLLOW_RESET_in_reset_timer6807) 
                if self._state.backtracking == 0:
                    stream_RESET.add(RESET329)
                self._state.following.append(self.FOLLOW_reset_statement_in_reset_timer6809)
                reset_statement330 = self.reset_statement()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_reset_statement.add(reset_statement330.tree)
                # sdl92.g:598:39: ( ',' reset_statement )*
                while True: #loop101
                    alt101 = 2
                    LA101_0 = self.input.LA(1)

                    if (LA101_0 == COMMA) :
                        alt101 = 1


                    if alt101 == 1:
                        # sdl92.g:598:40: ',' reset_statement
                        pass 
                        char_literal331=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_reset_timer6812) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal331)
                        self._state.following.append(self.FOLLOW_reset_statement_in_reset_timer6814)
                        reset_statement332 = self.reset_statement()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_reset_statement.add(reset_statement332.tree)


                    else:
                        break #loop101
                self._state.following.append(self.FOLLOW_end_in_reset_timer6834)
                end333 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end333.tree)

                # AST Rewrite
                # elements: reset_statement
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 600:9: -> ( reset_statement )+
                    # sdl92.g:600:17: ( reset_statement )+
                    if not (stream_reset_statement.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_reset_statement.hasNext():
                        self._adaptor.addChild(root_0, stream_reset_statement.nextTree())


                    stream_reset_statement.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "reset_timer"

    class reset_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.reset_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "reset_statement"
    # sdl92.g:603:1: reset_statement : timer_id ( '(' expression_list ')' )? -> ^( RESET timer_id ( expression_list )? ) ;
    def reset_statement(self, ):

        retval = self.reset_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal335 = None
        char_literal337 = None
        timer_id334 = None

        expression_list336 = None


        char_literal335_tree = None
        char_literal337_tree = None
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression_list = RewriteRuleSubtreeStream(self._adaptor, "rule expression_list")
        stream_timer_id = RewriteRuleSubtreeStream(self._adaptor, "rule timer_id")
        try:
            try:
                # sdl92.g:604:9: ( timer_id ( '(' expression_list ')' )? -> ^( RESET timer_id ( expression_list )? ) )
                # sdl92.g:604:17: timer_id ( '(' expression_list ')' )?
                pass 
                self._state.following.append(self.FOLLOW_timer_id_in_reset_statement6875)
                timer_id334 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_timer_id.add(timer_id334.tree)
                # sdl92.g:604:26: ( '(' expression_list ')' )?
                alt102 = 2
                LA102_0 = self.input.LA(1)

                if (LA102_0 == L_PAREN) :
                    alt102 = 1
                if alt102 == 1:
                    # sdl92.g:604:27: '(' expression_list ')'
                    pass 
                    char_literal335=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_reset_statement6878) 
                    if self._state.backtracking == 0:
                        stream_L_PAREN.add(char_literal335)
                    self._state.following.append(self.FOLLOW_expression_list_in_reset_statement6880)
                    expression_list336 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression_list.add(expression_list336.tree)
                    char_literal337=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_reset_statement6882) 
                    if self._state.backtracking == 0:
                        stream_R_PAREN.add(char_literal337)




                # AST Rewrite
                # elements: timer_id, expression_list
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 605:9: -> ^( RESET timer_id ( expression_list )? )
                    # sdl92.g:605:17: ^( RESET timer_id ( expression_list )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(RESET, "RESET"), root_1)

                    self._adaptor.addChild(root_1, stream_timer_id.nextTree())
                    # sdl92.g:605:34: ( expression_list )?
                    if stream_expression_list.hasNext():
                        self._adaptor.addChild(root_1, stream_expression_list.nextTree())


                    stream_expression_list.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "reset_statement"

    class transition_option_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.transition_option_return, self).__init__()

            self.tree = None




    # $ANTLR start "transition_option"
    # sdl92.g:608:1: transition_option : ALTERNATIVE alternative_question e= end answer_part alternative_part ENDALTERNATIVE f= end -> ^( ALTERNATIVE answer_part alternative_part ) ;
    def transition_option(self, ):

        retval = self.transition_option_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ALTERNATIVE338 = None
        ENDALTERNATIVE342 = None
        e = None

        f = None

        alternative_question339 = None

        answer_part340 = None

        alternative_part341 = None


        ALTERNATIVE338_tree = None
        ENDALTERNATIVE342_tree = None
        stream_ALTERNATIVE = RewriteRuleTokenStream(self._adaptor, "token ALTERNATIVE")
        stream_ENDALTERNATIVE = RewriteRuleTokenStream(self._adaptor, "token ENDALTERNATIVE")
        stream_alternative_question = RewriteRuleSubtreeStream(self._adaptor, "rule alternative_question")
        stream_answer_part = RewriteRuleSubtreeStream(self._adaptor, "rule answer_part")
        stream_alternative_part = RewriteRuleSubtreeStream(self._adaptor, "rule alternative_part")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:609:9: ( ALTERNATIVE alternative_question e= end answer_part alternative_part ENDALTERNATIVE f= end -> ^( ALTERNATIVE answer_part alternative_part ) )
                # sdl92.g:609:17: ALTERNATIVE alternative_question e= end answer_part alternative_part ENDALTERNATIVE f= end
                pass 
                ALTERNATIVE338=self.match(self.input, ALTERNATIVE, self.FOLLOW_ALTERNATIVE_in_transition_option6931) 
                if self._state.backtracking == 0:
                    stream_ALTERNATIVE.add(ALTERNATIVE338)
                self._state.following.append(self.FOLLOW_alternative_question_in_transition_option6933)
                alternative_question339 = self.alternative_question()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_alternative_question.add(alternative_question339.tree)
                self._state.following.append(self.FOLLOW_end_in_transition_option6937)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                self._state.following.append(self.FOLLOW_answer_part_in_transition_option6955)
                answer_part340 = self.answer_part()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_answer_part.add(answer_part340.tree)
                self._state.following.append(self.FOLLOW_alternative_part_in_transition_option6973)
                alternative_part341 = self.alternative_part()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_alternative_part.add(alternative_part341.tree)
                ENDALTERNATIVE342=self.match(self.input, ENDALTERNATIVE, self.FOLLOW_ENDALTERNATIVE_in_transition_option6991) 
                if self._state.backtracking == 0:
                    stream_ENDALTERNATIVE.add(ENDALTERNATIVE342)
                self._state.following.append(self.FOLLOW_end_in_transition_option6995)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: ALTERNATIVE, alternative_part, answer_part
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 613:9: -> ^( ALTERNATIVE answer_part alternative_part )
                    # sdl92.g:613:17: ^( ALTERNATIVE answer_part alternative_part )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ALTERNATIVE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_answer_part.nextTree())
                    self._adaptor.addChild(root_1, stream_alternative_part.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "transition_option"

    class alternative_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.alternative_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "alternative_part"
    # sdl92.g:616:1: alternative_part : ( ( ( answer_part )+ ( else_part )? ) -> ( answer_part )+ ( else_part )? | else_part -> else_part );
    def alternative_part(self, ):

        retval = self.alternative_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        answer_part343 = None

        else_part344 = None

        else_part345 = None


        stream_answer_part = RewriteRuleSubtreeStream(self._adaptor, "rule answer_part")
        stream_else_part = RewriteRuleSubtreeStream(self._adaptor, "rule else_part")
        try:
            try:
                # sdl92.g:617:9: ( ( ( answer_part )+ ( else_part )? ) -> ( answer_part )+ ( else_part )? | else_part -> else_part )
                alt105 = 2
                alt105 = self.dfa105.predict(self.input)
                if alt105 == 1:
                    # sdl92.g:617:17: ( ( answer_part )+ ( else_part )? )
                    pass 
                    # sdl92.g:617:17: ( ( answer_part )+ ( else_part )? )
                    # sdl92.g:617:18: ( answer_part )+ ( else_part )?
                    pass 
                    # sdl92.g:617:18: ( answer_part )+
                    cnt103 = 0
                    while True: #loop103
                        alt103 = 2
                        alt103 = self.dfa103.predict(self.input)
                        if alt103 == 1:
                            # sdl92.g:0:0: answer_part
                            pass 
                            self._state.following.append(self.FOLLOW_answer_part_in_alternative_part7042)
                            answer_part343 = self.answer_part()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_answer_part.add(answer_part343.tree)


                        else:
                            if cnt103 >= 1:
                                break #loop103

                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            eee = EarlyExitException(103, self.input)
                            raise eee

                        cnt103 += 1
                    # sdl92.g:617:31: ( else_part )?
                    alt104 = 2
                    LA104_0 = self.input.LA(1)

                    if (LA104_0 == ELSE or LA104_0 == 217) :
                        alt104 = 1
                    if alt104 == 1:
                        # sdl92.g:0:0: else_part
                        pass 
                        self._state.following.append(self.FOLLOW_else_part_in_alternative_part7045)
                        else_part344 = self.else_part()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_else_part.add(else_part344.tree)







                    # AST Rewrite
                    # elements: answer_part, else_part
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 618:9: -> ( answer_part )+ ( else_part )?
                        # sdl92.g:618:17: ( answer_part )+
                        if not (stream_answer_part.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_answer_part.hasNext():
                            self._adaptor.addChild(root_0, stream_answer_part.nextTree())


                        stream_answer_part.reset()
                        # sdl92.g:618:30: ( else_part )?
                        if stream_else_part.hasNext():
                            self._adaptor.addChild(root_0, stream_else_part.nextTree())


                        stream_else_part.reset();



                        retval.tree = root_0


                elif alt105 == 2:
                    # sdl92.g:619:19: else_part
                    pass 
                    self._state.following.append(self.FOLLOW_else_part_in_alternative_part7088)
                    else_part345 = self.else_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_else_part.add(else_part345.tree)

                    # AST Rewrite
                    # elements: else_part
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 620:9: -> else_part
                        self._adaptor.addChild(root_0, stream_else_part.nextTree())



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "alternative_part"

    class alternative_question_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.alternative_question_return, self).__init__()

            self.tree = None




    # $ANTLR start "alternative_question"
    # sdl92.g:623:1: alternative_question : ( expression | informal_text );
    def alternative_question(self, ):

        retval = self.alternative_question_return()
        retval.start = self.input.LT(1)

        root_0 = None

        expression346 = None

        informal_text347 = None



        try:
            try:
                # sdl92.g:624:9: ( expression | informal_text )
                alt106 = 2
                LA106_0 = self.input.LA(1)

                if (LA106_0 == BITSTR or LA106_0 == FLOAT or LA106_0 == IF or LA106_0 == OCTSTR or LA106_0 == INT or LA106_0 == L_PAREN or LA106_0 == ID or LA106_0 == DASH or (NOT <= LA106_0 <= MINUS_INFINITY) or LA106_0 == L_BRACKET) :
                    alt106 = 1
                elif (LA106_0 == STRING) :
                    LA106_2 = self.input.LA(2)

                    if (self.synpred139_sdl92()) :
                        alt106 = 1
                    elif (True) :
                        alt106 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 106, 2, self.input)

                        raise nvae

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 106, 0, self.input)

                    raise nvae

                if alt106 == 1:
                    # sdl92.g:624:17: expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_expression_in_alternative_question7128)
                    expression346 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, expression346.tree)


                elif alt106 == 2:
                    # sdl92.g:625:19: informal_text
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_informal_text_in_alternative_question7148)
                    informal_text347 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, informal_text347.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "alternative_question"

    class decision_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.decision_return, self).__init__()

            self.tree = None




    # $ANTLR start "decision"
    # sdl92.g:628:1: decision : ( cif )? ( hyperlink )? DECISION question e= end ( answer_part )? ( alternative_part )? ENDDECISION f= end -> ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? ) ;
    def decision(self, ):

        retval = self.decision_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DECISION350 = None
        ENDDECISION354 = None
        e = None

        f = None

        cif348 = None

        hyperlink349 = None

        question351 = None

        answer_part352 = None

        alternative_part353 = None


        DECISION350_tree = None
        ENDDECISION354_tree = None
        stream_DECISION = RewriteRuleTokenStream(self._adaptor, "token DECISION")
        stream_ENDDECISION = RewriteRuleTokenStream(self._adaptor, "token ENDDECISION")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_answer_part = RewriteRuleSubtreeStream(self._adaptor, "rule answer_part")
        stream_question = RewriteRuleSubtreeStream(self._adaptor, "rule question")
        stream_alternative_part = RewriteRuleSubtreeStream(self._adaptor, "rule alternative_part")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:629:9: ( ( cif )? ( hyperlink )? DECISION question e= end ( answer_part )? ( alternative_part )? ENDDECISION f= end -> ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? ) )
                # sdl92.g:629:17: ( cif )? ( hyperlink )? DECISION question e= end ( answer_part )? ( alternative_part )? ENDDECISION f= end
                pass 
                # sdl92.g:629:17: ( cif )?
                alt107 = 2
                LA107_0 = self.input.LA(1)

                if (LA107_0 == 217) :
                    LA107_1 = self.input.LA(2)

                    if (LA107_1 == ANSWER or LA107_1 == COMMENT or LA107_1 == CONNECT or LA107_1 == DECISION or LA107_1 == INPUT or (JOIN <= LA107_1 <= LABEL) or LA107_1 == NEXTSTATE or LA107_1 == OUTPUT or (PROCEDURE <= LA107_1 <= PROCEDURE_CALL) or (PROCESS <= LA107_1 <= PROVIDED) or LA107_1 == RETURN or LA107_1 == STATE or LA107_1 == STOP or LA107_1 == TASK or LA107_1 == TEXT or LA107_1 == START) :
                        alt107 = 1
                if alt107 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_decision7171)
                    cif348 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif348.tree)



                # sdl92.g:630:17: ( hyperlink )?
                alt108 = 2
                LA108_0 = self.input.LA(1)

                if (LA108_0 == 217) :
                    alt108 = 1
                if alt108 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_decision7190)
                    hyperlink349 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink349.tree)



                DECISION350=self.match(self.input, DECISION, self.FOLLOW_DECISION_in_decision7209) 
                if self._state.backtracking == 0:
                    stream_DECISION.add(DECISION350)
                self._state.following.append(self.FOLLOW_question_in_decision7211)
                question351 = self.question()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_question.add(question351.tree)
                self._state.following.append(self.FOLLOW_end_in_decision7215)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                # sdl92.g:632:17: ( answer_part )?
                alt109 = 2
                LA109_0 = self.input.LA(1)

                if (LA109_0 == 217) :
                    LA109_1 = self.input.LA(2)

                    if (self.synpred142_sdl92()) :
                        alt109 = 1
                elif (LA109_0 == L_PAREN) :
                    LA109_2 = self.input.LA(2)

                    if (self.synpred142_sdl92()) :
                        alt109 = 1
                if alt109 == 1:
                    # sdl92.g:0:0: answer_part
                    pass 
                    self._state.following.append(self.FOLLOW_answer_part_in_decision7233)
                    answer_part352 = self.answer_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_answer_part.add(answer_part352.tree)



                # sdl92.g:633:17: ( alternative_part )?
                alt110 = 2
                LA110_0 = self.input.LA(1)

                if (LA110_0 == ELSE or LA110_0 == L_PAREN or LA110_0 == 217) :
                    alt110 = 1
                if alt110 == 1:
                    # sdl92.g:0:0: alternative_part
                    pass 
                    self._state.following.append(self.FOLLOW_alternative_part_in_decision7252)
                    alternative_part353 = self.alternative_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_alternative_part.add(alternative_part353.tree)



                ENDDECISION354=self.match(self.input, ENDDECISION, self.FOLLOW_ENDDECISION_in_decision7271) 
                if self._state.backtracking == 0:
                    stream_ENDDECISION.add(ENDDECISION354)
                self._state.following.append(self.FOLLOW_end_in_decision7275)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: question, hyperlink, alternative_part, answer_part, cif, e, DECISION
                # token labels: 
                # rule labels: retval, e
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if e is not None:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "rule e", e.tree)
                    else:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "token e", None)


                    root_0 = self._adaptor.nil()
                    # 635:9: -> ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? )
                    # sdl92.g:635:17: ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_DECISION.nextNode(), root_1)

                    # sdl92.g:635:28: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:635:33: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:635:44: ( $e)?
                    if stream_e.hasNext():
                        self._adaptor.addChild(root_1, stream_e.nextTree())


                    stream_e.reset();
                    self._adaptor.addChild(root_1, stream_question.nextTree())
                    # sdl92.g:636:17: ( answer_part )?
                    if stream_answer_part.hasNext():
                        self._adaptor.addChild(root_1, stream_answer_part.nextTree())


                    stream_answer_part.reset();
                    # sdl92.g:636:30: ( alternative_part )?
                    if stream_alternative_part.hasNext():
                        self._adaptor.addChild(root_1, stream_alternative_part.nextTree())


                    stream_alternative_part.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "decision"

    class answer_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.answer_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "answer_part"
    # sdl92.g:639:1: answer_part : ( cif )? ( hyperlink )? L_PAREN answer R_PAREN ':' ( transition )? -> ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? ) ;
    def answer_part(self, ):

        retval = self.answer_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN357 = None
        R_PAREN359 = None
        char_literal360 = None
        cif355 = None

        hyperlink356 = None

        answer358 = None

        transition361 = None


        L_PAREN357_tree = None
        R_PAREN359_tree = None
        char_literal360_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_answer = RewriteRuleSubtreeStream(self._adaptor, "rule answer")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        try:
            try:
                # sdl92.g:640:9: ( ( cif )? ( hyperlink )? L_PAREN answer R_PAREN ':' ( transition )? -> ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? ) )
                # sdl92.g:640:17: ( cif )? ( hyperlink )? L_PAREN answer R_PAREN ':' ( transition )?
                pass 
                # sdl92.g:640:17: ( cif )?
                alt111 = 2
                LA111_0 = self.input.LA(1)

                if (LA111_0 == 217) :
                    LA111_1 = self.input.LA(2)

                    if (LA111_1 == ANSWER or LA111_1 == COMMENT or LA111_1 == CONNECT or LA111_1 == DECISION or LA111_1 == INPUT or (JOIN <= LA111_1 <= LABEL) or LA111_1 == NEXTSTATE or LA111_1 == OUTPUT or (PROCEDURE <= LA111_1 <= PROCEDURE_CALL) or (PROCESS <= LA111_1 <= PROVIDED) or LA111_1 == RETURN or LA111_1 == STATE or LA111_1 == STOP or LA111_1 == TASK or LA111_1 == TEXT or LA111_1 == START) :
                        alt111 = 1
                if alt111 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_answer_part7351)
                    cif355 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif355.tree)



                # sdl92.g:641:17: ( hyperlink )?
                alt112 = 2
                LA112_0 = self.input.LA(1)

                if (LA112_0 == 217) :
                    alt112 = 1
                if alt112 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_answer_part7370)
                    hyperlink356 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink356.tree)



                L_PAREN357=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_answer_part7389) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN357)
                self._state.following.append(self.FOLLOW_answer_in_answer_part7391)
                answer358 = self.answer()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_answer.add(answer358.tree)
                R_PAREN359=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_answer_part7393) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN359)
                char_literal360=self.match(self.input, 212, self.FOLLOW_212_in_answer_part7395) 
                if self._state.backtracking == 0:
                    stream_212.add(char_literal360)
                # sdl92.g:642:44: ( transition )?
                alt113 = 2
                alt113 = self.dfa113.predict(self.input)
                if alt113 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_answer_part7397)
                    transition361 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition361.tree)




                # AST Rewrite
                # elements: cif, hyperlink, transition, answer
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 643:9: -> ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? )
                    # sdl92.g:643:17: ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ANSWER, "ANSWER"), root_1)

                    # sdl92.g:643:26: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:643:31: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    self._adaptor.addChild(root_1, stream_answer.nextTree())
                    # sdl92.g:643:49: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "answer_part"

    class answer_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.answer_return, self).__init__()

            self.tree = None




    # $ANTLR start "answer"
    # sdl92.g:646:1: answer : ( range_condition | informal_text );
    def answer(self, ):

        retval = self.answer_return()
        retval.start = self.input.LT(1)

        root_0 = None

        range_condition362 = None

        informal_text363 = None



        try:
            try:
                # sdl92.g:647:9: ( range_condition | informal_text )
                alt114 = 2
                LA114_0 = self.input.LA(1)

                if (LA114_0 == BITSTR or LA114_0 == FLOAT or LA114_0 == IF or LA114_0 == OCTSTR or LA114_0 == INT or LA114_0 == L_PAREN or (EQ <= LA114_0 <= GE) or LA114_0 == ID or LA114_0 == DASH or (NOT <= LA114_0 <= MINUS_INFINITY) or LA114_0 == L_BRACKET) :
                    alt114 = 1
                elif (LA114_0 == STRING) :
                    LA114_2 = self.input.LA(2)

                    if (self.synpred147_sdl92()) :
                        alt114 = 1
                    elif (True) :
                        alt114 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 114, 2, self.input)

                        raise nvae

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 114, 0, self.input)

                    raise nvae

                if alt114 == 1:
                    # sdl92.g:647:17: range_condition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_range_condition_in_answer7451)
                    range_condition362 = self.range_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, range_condition362.tree)


                elif alt114 == 2:
                    # sdl92.g:648:19: informal_text
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_informal_text_in_answer7471)
                    informal_text363 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, informal_text363.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "answer"

    class else_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.else_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "else_part"
    # sdl92.g:651:1: else_part : ( cif )? ( hyperlink )? ELSE ':' ( transition )? -> ^( ELSE ( cif )? ( hyperlink )? ( transition )? ) ;
    def else_part(self, ):

        retval = self.else_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ELSE366 = None
        char_literal367 = None
        cif364 = None

        hyperlink365 = None

        transition368 = None


        ELSE366_tree = None
        char_literal367_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_ELSE = RewriteRuleTokenStream(self._adaptor, "token ELSE")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        try:
            try:
                # sdl92.g:652:9: ( ( cif )? ( hyperlink )? ELSE ':' ( transition )? -> ^( ELSE ( cif )? ( hyperlink )? ( transition )? ) )
                # sdl92.g:652:17: ( cif )? ( hyperlink )? ELSE ':' ( transition )?
                pass 
                # sdl92.g:652:17: ( cif )?
                alt115 = 2
                LA115_0 = self.input.LA(1)

                if (LA115_0 == 217) :
                    LA115_1 = self.input.LA(2)

                    if (LA115_1 == ANSWER or LA115_1 == COMMENT or LA115_1 == CONNECT or LA115_1 == DECISION or LA115_1 == INPUT or (JOIN <= LA115_1 <= LABEL) or LA115_1 == NEXTSTATE or LA115_1 == OUTPUT or (PROCEDURE <= LA115_1 <= PROCEDURE_CALL) or (PROCESS <= LA115_1 <= PROVIDED) or LA115_1 == RETURN or LA115_1 == STATE or LA115_1 == STOP or LA115_1 == TASK or LA115_1 == TEXT or LA115_1 == START) :
                        alt115 = 1
                if alt115 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_else_part7494)
                    cif364 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif364.tree)



                # sdl92.g:653:17: ( hyperlink )?
                alt116 = 2
                LA116_0 = self.input.LA(1)

                if (LA116_0 == 217) :
                    alt116 = 1
                if alt116 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_else_part7513)
                    hyperlink365 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink365.tree)



                ELSE366=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_else_part7532) 
                if self._state.backtracking == 0:
                    stream_ELSE.add(ELSE366)
                char_literal367=self.match(self.input, 212, self.FOLLOW_212_in_else_part7534) 
                if self._state.backtracking == 0:
                    stream_212.add(char_literal367)
                # sdl92.g:654:26: ( transition )?
                alt117 = 2
                LA117_0 = self.input.LA(1)

                if (LA117_0 == ALTERNATIVE or LA117_0 == DECISION or LA117_0 == EXPORT or LA117_0 == FOR or LA117_0 == JOIN or LA117_0 == NEXTSTATE or LA117_0 == OUTPUT or (RESET <= LA117_0 <= RETURN) or LA117_0 == SET or (STOP <= LA117_0 <= STRING) or LA117_0 == TASK or LA117_0 == CALL or LA117_0 == CREATE or LA117_0 == ID or LA117_0 == 217) :
                    alt117 = 1
                if alt117 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_else_part7536)
                    transition368 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition368.tree)




                # AST Rewrite
                # elements: hyperlink, ELSE, transition, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 655:9: -> ^( ELSE ( cif )? ( hyperlink )? ( transition )? )
                    # sdl92.g:655:17: ^( ELSE ( cif )? ( hyperlink )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ELSE.nextNode(), root_1)

                    # sdl92.g:655:24: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:655:29: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:655:40: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "else_part"

    class question_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.question_return, self).__init__()

            self.tree = None




    # $ANTLR start "question"
    # sdl92.g:658:1: question : ( expression -> ^( QUESTION expression ) | informal_text -> informal_text | ANY -> ^( ANY ) );
    def question(self, ):

        retval = self.question_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ANY371 = None
        expression369 = None

        informal_text370 = None


        ANY371_tree = None
        stream_ANY = RewriteRuleTokenStream(self._adaptor, "token ANY")
        stream_informal_text = RewriteRuleSubtreeStream(self._adaptor, "rule informal_text")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:659:9: ( expression -> ^( QUESTION expression ) | informal_text -> informal_text | ANY -> ^( ANY ) )
                alt118 = 3
                LA118 = self.input.LA(1)
                if LA118 == BITSTR or LA118 == FLOAT or LA118 == IF or LA118 == OCTSTR or LA118 == INT or LA118 == L_PAREN or LA118 == ID or LA118 == DASH or LA118 == NOT or LA118 == TRUE or LA118 == FALSE or LA118 == NULL or LA118 == PLUS_INFINITY or LA118 == MINUS_INFINITY or LA118 == L_BRACKET:
                    alt118 = 1
                elif LA118 == STRING:
                    LA118_2 = self.input.LA(2)

                    if (self.synpred151_sdl92()) :
                        alt118 = 1
                    elif (self.synpred152_sdl92()) :
                        alt118 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 118, 2, self.input)

                        raise nvae

                elif LA118 == ANY:
                    alt118 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 118, 0, self.input)

                    raise nvae

                if alt118 == 1:
                    # sdl92.g:659:17: expression
                    pass 
                    self._state.following.append(self.FOLLOW_expression_in_question7588)
                    expression369 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression369.tree)

                    # AST Rewrite
                    # elements: expression
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 660:9: -> ^( QUESTION expression )
                        # sdl92.g:660:17: ^( QUESTION expression )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(QUESTION, "QUESTION"), root_1)

                        self._adaptor.addChild(root_1, stream_expression.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt118 == 2:
                    # sdl92.g:661:19: informal_text
                    pass 
                    self._state.following.append(self.FOLLOW_informal_text_in_question7629)
                    informal_text370 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_informal_text.add(informal_text370.tree)

                    # AST Rewrite
                    # elements: informal_text
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 662:9: -> informal_text
                        self._adaptor.addChild(root_0, stream_informal_text.nextTree())



                        retval.tree = root_0


                elif alt118 == 3:
                    # sdl92.g:663:19: ANY
                    pass 
                    ANY371=self.match(self.input, ANY, self.FOLLOW_ANY_in_question7666) 
                    if self._state.backtracking == 0:
                        stream_ANY.add(ANY371)

                    # AST Rewrite
                    # elements: ANY
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 664:9: -> ^( ANY )
                        # sdl92.g:664:17: ^( ANY )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_ANY.nextNode(), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "question"

    class range_condition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.range_condition_return, self).__init__()

            self.tree = None




    # $ANTLR start "range_condition"
    # sdl92.g:667:1: range_condition : ( closed_range | open_range ) ;
    def range_condition(self, ):

        retval = self.range_condition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        closed_range372 = None

        open_range373 = None



        try:
            try:
                # sdl92.g:668:9: ( ( closed_range | open_range ) )
                # sdl92.g:668:17: ( closed_range | open_range )
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:668:17: ( closed_range | open_range )
                alt119 = 2
                LA119_0 = self.input.LA(1)

                if (LA119_0 == INT) :
                    LA119_1 = self.input.LA(2)

                    if (LA119_1 == 212) :
                        alt119 = 1
                    elif (LA119_1 == EOF or LA119_1 == ENDSYNTYPE or LA119_1 == IN or LA119_1 == AND or LA119_1 == ASTERISK or (R_PAREN <= LA119_1 <= COMMA) or (EQ <= LA119_1 <= GE) or (IMPLIES <= LA119_1 <= REM)) :
                        alt119 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 119, 1, self.input)

                        raise nvae

                elif (LA119_0 == BITSTR or LA119_0 == FLOAT or LA119_0 == IF or LA119_0 == OCTSTR or LA119_0 == STRING or LA119_0 == L_PAREN or (EQ <= LA119_0 <= GE) or LA119_0 == ID or LA119_0 == DASH or (NOT <= LA119_0 <= MINUS_INFINITY) or LA119_0 == L_BRACKET) :
                    alt119 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 119, 0, self.input)

                    raise nvae

                if alt119 == 1:
                    # sdl92.g:668:18: closed_range
                    pass 
                    self._state.following.append(self.FOLLOW_closed_range_in_range_condition7709)
                    closed_range372 = self.closed_range()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, closed_range372.tree)


                elif alt119 == 2:
                    # sdl92.g:668:33: open_range
                    pass 
                    self._state.following.append(self.FOLLOW_open_range_in_range_condition7713)
                    open_range373 = self.open_range()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, open_range373.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "range_condition"

    class closed_range_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.closed_range_return, self).__init__()

            self.tree = None




    # $ANTLR start "closed_range"
    # sdl92.g:672:1: closed_range : a= INT ':' b= INT -> ^( CLOSED_RANGE $a $b) ;
    def closed_range(self, ):

        retval = self.closed_range_return()
        retval.start = self.input.LT(1)

        root_0 = None

        a = None
        b = None
        char_literal374 = None

        a_tree = None
        b_tree = None
        char_literal374_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")

        try:
            try:
                # sdl92.g:673:9: (a= INT ':' b= INT -> ^( CLOSED_RANGE $a $b) )
                # sdl92.g:673:17: a= INT ':' b= INT
                pass 
                a=self.match(self.input, INT, self.FOLLOW_INT_in_closed_range7756) 
                if self._state.backtracking == 0:
                    stream_INT.add(a)
                char_literal374=self.match(self.input, 212, self.FOLLOW_212_in_closed_range7758) 
                if self._state.backtracking == 0:
                    stream_212.add(char_literal374)
                b=self.match(self.input, INT, self.FOLLOW_INT_in_closed_range7762) 
                if self._state.backtracking == 0:
                    stream_INT.add(b)

                # AST Rewrite
                # elements: b, a
                # token labels: b, a
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_b = RewriteRuleTokenStream(self._adaptor, "token b", b)
                    stream_a = RewriteRuleTokenStream(self._adaptor, "token a", a)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 674:9: -> ^( CLOSED_RANGE $a $b)
                    # sdl92.g:674:17: ^( CLOSED_RANGE $a $b)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CLOSED_RANGE, "CLOSED_RANGE"), root_1)

                    self._adaptor.addChild(root_1, stream_a.nextNode())
                    self._adaptor.addChild(root_1, stream_b.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "closed_range"

    class open_range_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.open_range_return, self).__init__()

            self.tree = None




    # $ANTLR start "open_range"
    # sdl92.g:677:1: open_range : ( constant -> constant | ( ( EQ | NEQ | GT | LT | LE | GE ) constant ) -> ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant ) );
    def open_range(self, ):

        retval = self.open_range_return()
        retval.start = self.input.LT(1)

        root_0 = None

        EQ376 = None
        NEQ377 = None
        GT378 = None
        LT379 = None
        LE380 = None
        GE381 = None
        constant375 = None

        constant382 = None


        EQ376_tree = None
        NEQ377_tree = None
        GT378_tree = None
        LT379_tree = None
        LE380_tree = None
        GE381_tree = None
        stream_GT = RewriteRuleTokenStream(self._adaptor, "token GT")
        stream_GE = RewriteRuleTokenStream(self._adaptor, "token GE")
        stream_LT = RewriteRuleTokenStream(self._adaptor, "token LT")
        stream_NEQ = RewriteRuleTokenStream(self._adaptor, "token NEQ")
        stream_EQ = RewriteRuleTokenStream(self._adaptor, "token EQ")
        stream_LE = RewriteRuleTokenStream(self._adaptor, "token LE")
        stream_constant = RewriteRuleSubtreeStream(self._adaptor, "rule constant")
        try:
            try:
                # sdl92.g:678:9: ( constant -> constant | ( ( EQ | NEQ | GT | LT | LE | GE ) constant ) -> ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant ) )
                alt121 = 2
                LA121_0 = self.input.LA(1)

                if (LA121_0 == BITSTR or LA121_0 == FLOAT or LA121_0 == IF or LA121_0 == OCTSTR or LA121_0 == STRING or LA121_0 == INT or LA121_0 == L_PAREN or LA121_0 == ID or LA121_0 == DASH or (NOT <= LA121_0 <= MINUS_INFINITY) or LA121_0 == L_BRACKET) :
                    alt121 = 1
                elif ((EQ <= LA121_0 <= GE)) :
                    alt121 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 121, 0, self.input)

                    raise nvae

                if alt121 == 1:
                    # sdl92.g:678:17: constant
                    pass 
                    self._state.following.append(self.FOLLOW_constant_in_open_range7810)
                    constant375 = self.constant()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_constant.add(constant375.tree)

                    # AST Rewrite
                    # elements: constant
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 679:9: -> constant
                        self._adaptor.addChild(root_0, stream_constant.nextTree())



                        retval.tree = root_0


                elif alt121 == 2:
                    # sdl92.g:680:19: ( ( EQ | NEQ | GT | LT | LE | GE ) constant )
                    pass 
                    # sdl92.g:680:19: ( ( EQ | NEQ | GT | LT | LE | GE ) constant )
                    # sdl92.g:680:21: ( EQ | NEQ | GT | LT | LE | GE ) constant
                    pass 
                    # sdl92.g:680:21: ( EQ | NEQ | GT | LT | LE | GE )
                    alt120 = 6
                    LA120 = self.input.LA(1)
                    if LA120 == EQ:
                        alt120 = 1
                    elif LA120 == NEQ:
                        alt120 = 2
                    elif LA120 == GT:
                        alt120 = 3
                    elif LA120 == LT:
                        alt120 = 4
                    elif LA120 == LE:
                        alt120 = 5
                    elif LA120 == GE:
                        alt120 = 6
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 120, 0, self.input)

                        raise nvae

                    if alt120 == 1:
                        # sdl92.g:680:22: EQ
                        pass 
                        EQ376=self.match(self.input, EQ, self.FOLLOW_EQ_in_open_range7850) 
                        if self._state.backtracking == 0:
                            stream_EQ.add(EQ376)


                    elif alt120 == 2:
                        # sdl92.g:680:25: NEQ
                        pass 
                        NEQ377=self.match(self.input, NEQ, self.FOLLOW_NEQ_in_open_range7852) 
                        if self._state.backtracking == 0:
                            stream_NEQ.add(NEQ377)


                    elif alt120 == 3:
                        # sdl92.g:680:29: GT
                        pass 
                        GT378=self.match(self.input, GT, self.FOLLOW_GT_in_open_range7854) 
                        if self._state.backtracking == 0:
                            stream_GT.add(GT378)


                    elif alt120 == 4:
                        # sdl92.g:680:32: LT
                        pass 
                        LT379=self.match(self.input, LT, self.FOLLOW_LT_in_open_range7856) 
                        if self._state.backtracking == 0:
                            stream_LT.add(LT379)


                    elif alt120 == 5:
                        # sdl92.g:680:35: LE
                        pass 
                        LE380=self.match(self.input, LE, self.FOLLOW_LE_in_open_range7858) 
                        if self._state.backtracking == 0:
                            stream_LE.add(LE380)


                    elif alt120 == 6:
                        # sdl92.g:680:38: GE
                        pass 
                        GE381=self.match(self.input, GE, self.FOLLOW_GE_in_open_range7860) 
                        if self._state.backtracking == 0:
                            stream_GE.add(GE381)



                    self._state.following.append(self.FOLLOW_constant_in_open_range7863)
                    constant382 = self.constant()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_constant.add(constant382.tree)




                    # AST Rewrite
                    # elements: GE, constant, NEQ, EQ, LT, LE, GT
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 681:9: -> ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant )
                        # sdl92.g:681:17: ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OPEN_RANGE, "OPEN_RANGE"), root_1)

                        # sdl92.g:681:30: ( EQ )?
                        if stream_EQ.hasNext():
                            self._adaptor.addChild(root_1, stream_EQ.nextNode())


                        stream_EQ.reset();
                        # sdl92.g:681:34: ( NEQ )?
                        if stream_NEQ.hasNext():
                            self._adaptor.addChild(root_1, stream_NEQ.nextNode())


                        stream_NEQ.reset();
                        # sdl92.g:681:39: ( GT )?
                        if stream_GT.hasNext():
                            self._adaptor.addChild(root_1, stream_GT.nextNode())


                        stream_GT.reset();
                        # sdl92.g:681:43: ( LT )?
                        if stream_LT.hasNext():
                            self._adaptor.addChild(root_1, stream_LT.nextNode())


                        stream_LT.reset();
                        # sdl92.g:681:47: ( LE )?
                        if stream_LE.hasNext():
                            self._adaptor.addChild(root_1, stream_LE.nextNode())


                        stream_LE.reset();
                        # sdl92.g:681:51: ( GE )?
                        if stream_GE.hasNext():
                            self._adaptor.addChild(root_1, stream_GE.nextNode())


                        stream_GE.reset();
                        self._adaptor.addChild(root_1, stream_constant.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "open_range"

    class constant_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.constant_return, self).__init__()

            self.tree = None




    # $ANTLR start "constant"
    # sdl92.g:684:1: constant : expression -> ^( CONSTANT expression ) ;
    def constant(self, ):

        retval = self.constant_return()
        retval.start = self.input.LT(1)

        root_0 = None

        expression383 = None


        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:685:9: ( expression -> ^( CONSTANT expression ) )
                # sdl92.g:685:17: expression
                pass 
                self._state.following.append(self.FOLLOW_expression_in_constant7926)
                expression383 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression383.tree)

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 686:9: -> ^( CONSTANT expression )
                    # sdl92.g:686:17: ^( CONSTANT expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CONSTANT, "CONSTANT"), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "constant"

    class create_request_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.create_request_return, self).__init__()

            self.tree = None




    # $ANTLR start "create_request"
    # sdl92.g:689:1: create_request : CREATE createbody ( actual_parameters )? end -> ^( CREATE createbody ( actual_parameters )? ) ;
    def create_request(self, ):

        retval = self.create_request_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CREATE384 = None
        createbody385 = None

        actual_parameters386 = None

        end387 = None


        CREATE384_tree = None
        stream_CREATE = RewriteRuleTokenStream(self._adaptor, "token CREATE")
        stream_createbody = RewriteRuleSubtreeStream(self._adaptor, "rule createbody")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        stream_actual_parameters = RewriteRuleSubtreeStream(self._adaptor, "rule actual_parameters")
        try:
            try:
                # sdl92.g:690:9: ( CREATE createbody ( actual_parameters )? end -> ^( CREATE createbody ( actual_parameters )? ) )
                # sdl92.g:690:17: CREATE createbody ( actual_parameters )? end
                pass 
                CREATE384=self.match(self.input, CREATE, self.FOLLOW_CREATE_in_create_request7970) 
                if self._state.backtracking == 0:
                    stream_CREATE.add(CREATE384)
                self._state.following.append(self.FOLLOW_createbody_in_create_request7988)
                createbody385 = self.createbody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_createbody.add(createbody385.tree)
                # sdl92.g:692:17: ( actual_parameters )?
                alt122 = 2
                LA122_0 = self.input.LA(1)

                if (LA122_0 == L_PAREN) :
                    alt122 = 1
                if alt122 == 1:
                    # sdl92.g:0:0: actual_parameters
                    pass 
                    self._state.following.append(self.FOLLOW_actual_parameters_in_create_request8006)
                    actual_parameters386 = self.actual_parameters()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_actual_parameters.add(actual_parameters386.tree)



                self._state.following.append(self.FOLLOW_end_in_create_request8025)
                end387 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end387.tree)

                # AST Rewrite
                # elements: actual_parameters, createbody, CREATE
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 694:9: -> ^( CREATE createbody ( actual_parameters )? )
                    # sdl92.g:694:17: ^( CREATE createbody ( actual_parameters )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_CREATE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_createbody.nextTree())
                    # sdl92.g:694:37: ( actual_parameters )?
                    if stream_actual_parameters.hasNext():
                        self._adaptor.addChild(root_1, stream_actual_parameters.nextTree())


                    stream_actual_parameters.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "create_request"

    class createbody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.createbody_return, self).__init__()

            self.tree = None




    # $ANTLR start "createbody"
    # sdl92.g:697:1: createbody : ( process_id | THIS );
    def createbody(self, ):

        retval = self.createbody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        THIS389 = None
        process_id388 = None


        THIS389_tree = None

        try:
            try:
                # sdl92.g:698:9: ( process_id | THIS )
                alt123 = 2
                LA123_0 = self.input.LA(1)

                if (LA123_0 == ID) :
                    alt123 = 1
                elif (LA123_0 == THIS) :
                    alt123 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 123, 0, self.input)

                    raise nvae

                if alt123 == 1:
                    # sdl92.g:698:17: process_id
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_process_id_in_createbody8072)
                    process_id388 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, process_id388.tree)


                elif alt123 == 2:
                    # sdl92.g:699:19: THIS
                    pass 
                    root_0 = self._adaptor.nil()

                    THIS389=self.match(self.input, THIS, self.FOLLOW_THIS_in_createbody8092)
                    if self._state.backtracking == 0:

                        THIS389_tree = self._adaptor.createWithPayload(THIS389)
                        self._adaptor.addChild(root_0, THIS389_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "createbody"

    class output_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.output_return, self).__init__()

            self.tree = None




    # $ANTLR start "output"
    # sdl92.g:702:1: output : ( cif )? ( hyperlink )? OUTPUT outputbody end -> ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody ) ;
    def output(self, ):

        retval = self.output_return()
        retval.start = self.input.LT(1)

        root_0 = None

        OUTPUT392 = None
        cif390 = None

        hyperlink391 = None

        outputbody393 = None

        end394 = None


        OUTPUT392_tree = None
        stream_OUTPUT = RewriteRuleTokenStream(self._adaptor, "token OUTPUT")
        stream_outputbody = RewriteRuleSubtreeStream(self._adaptor, "rule outputbody")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:703:9: ( ( cif )? ( hyperlink )? OUTPUT outputbody end -> ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody ) )
                # sdl92.g:703:17: ( cif )? ( hyperlink )? OUTPUT outputbody end
                pass 
                # sdl92.g:703:17: ( cif )?
                alt124 = 2
                LA124_0 = self.input.LA(1)

                if (LA124_0 == 217) :
                    LA124_1 = self.input.LA(2)

                    if (LA124_1 == ANSWER or LA124_1 == COMMENT or LA124_1 == CONNECT or LA124_1 == DECISION or LA124_1 == INPUT or (JOIN <= LA124_1 <= LABEL) or LA124_1 == NEXTSTATE or LA124_1 == OUTPUT or (PROCEDURE <= LA124_1 <= PROCEDURE_CALL) or (PROCESS <= LA124_1 <= PROVIDED) or LA124_1 == RETURN or LA124_1 == STATE or LA124_1 == STOP or LA124_1 == TASK or LA124_1 == TEXT or LA124_1 == START) :
                        alt124 = 1
                if alt124 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_output8115)
                    cif390 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif390.tree)



                # sdl92.g:704:17: ( hyperlink )?
                alt125 = 2
                LA125_0 = self.input.LA(1)

                if (LA125_0 == 217) :
                    alt125 = 1
                if alt125 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_output8134)
                    hyperlink391 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink391.tree)



                OUTPUT392=self.match(self.input, OUTPUT, self.FOLLOW_OUTPUT_in_output8153) 
                if self._state.backtracking == 0:
                    stream_OUTPUT.add(OUTPUT392)
                self._state.following.append(self.FOLLOW_outputbody_in_output8155)
                outputbody393 = self.outputbody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_outputbody.add(outputbody393.tree)
                self._state.following.append(self.FOLLOW_end_in_output8157)
                end394 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end394.tree)

                # AST Rewrite
                # elements: end, hyperlink, outputbody, OUTPUT, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 706:9: -> ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody )
                    # sdl92.g:706:17: ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_OUTPUT.nextNode(), root_1)

                    # sdl92.g:706:26: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:706:31: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:706:42: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_outputbody.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "output"

    class outputbody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.outputbody_return, self).__init__()

            self.tree = None




    # $ANTLR start "outputbody"
    # sdl92.g:709:1: outputbody : outputstmt ( ',' outputstmt )* ( to_part )? -> ^( OUTPUT_BODY ( outputstmt )+ ( to_part )? ) ;
    def outputbody(self, ):

        retval = self.outputbody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal396 = None
        outputstmt395 = None

        outputstmt397 = None

        to_part398 = None


        char_literal396_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_outputstmt = RewriteRuleSubtreeStream(self._adaptor, "rule outputstmt")
        stream_to_part = RewriteRuleSubtreeStream(self._adaptor, "rule to_part")
        try:
            try:
                # sdl92.g:710:9: ( outputstmt ( ',' outputstmt )* ( to_part )? -> ^( OUTPUT_BODY ( outputstmt )+ ( to_part )? ) )
                # sdl92.g:710:17: outputstmt ( ',' outputstmt )* ( to_part )?
                pass 
                self._state.following.append(self.FOLLOW_outputstmt_in_outputbody8210)
                outputstmt395 = self.outputstmt()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_outputstmt.add(outputstmt395.tree)
                # sdl92.g:710:28: ( ',' outputstmt )*
                while True: #loop126
                    alt126 = 2
                    LA126_0 = self.input.LA(1)

                    if (LA126_0 == COMMA) :
                        alt126 = 1


                    if alt126 == 1:
                        # sdl92.g:710:29: ',' outputstmt
                        pass 
                        char_literal396=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_outputbody8213) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal396)
                        self._state.following.append(self.FOLLOW_outputstmt_in_outputbody8215)
                        outputstmt397 = self.outputstmt()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_outputstmt.add(outputstmt397.tree)


                    else:
                        break #loop126
                # sdl92.g:710:46: ( to_part )?
                alt127 = 2
                LA127_0 = self.input.LA(1)

                if (LA127_0 == TO) :
                    alt127 = 1
                if alt127 == 1:
                    # sdl92.g:0:0: to_part
                    pass 
                    self._state.following.append(self.FOLLOW_to_part_in_outputbody8219)
                    to_part398 = self.to_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_to_part.add(to_part398.tree)




                # AST Rewrite
                # elements: outputstmt, to_part
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 711:9: -> ^( OUTPUT_BODY ( outputstmt )+ ( to_part )? )
                    # sdl92.g:711:17: ^( OUTPUT_BODY ( outputstmt )+ ( to_part )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OUTPUT_BODY, "OUTPUT_BODY"), root_1)

                    # sdl92.g:711:31: ( outputstmt )+
                    if not (stream_outputstmt.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_outputstmt.hasNext():
                        self._adaptor.addChild(root_1, stream_outputstmt.nextTree())


                    stream_outputstmt.reset()
                    # sdl92.g:711:43: ( to_part )?
                    if stream_to_part.hasNext():
                        self._adaptor.addChild(root_1, stream_to_part.nextTree())


                    stream_to_part.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "outputbody"

    class outputstmt_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.outputstmt_return, self).__init__()

            self.tree = None




    # $ANTLR start "outputstmt"
    # sdl92.g:716:1: outputstmt : signal_id ( actual_parameters )? ;
    def outputstmt(self, ):

        retval = self.outputstmt_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_id399 = None

        actual_parameters400 = None



        try:
            try:
                # sdl92.g:717:9: ( signal_id ( actual_parameters )? )
                # sdl92.g:717:17: signal_id ( actual_parameters )?
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_signal_id_in_outputstmt8272)
                signal_id399 = self.signal_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, signal_id399.tree)
                # sdl92.g:718:17: ( actual_parameters )?
                alt128 = 2
                LA128_0 = self.input.LA(1)

                if (LA128_0 == L_PAREN) :
                    alt128 = 1
                if alt128 == 1:
                    # sdl92.g:0:0: actual_parameters
                    pass 
                    self._state.following.append(self.FOLLOW_actual_parameters_in_outputstmt8290)
                    actual_parameters400 = self.actual_parameters()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, actual_parameters400.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "outputstmt"

    class to_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.to_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "to_part"
    # sdl92.g:720:1: to_part : ( TO destination ) -> ^( TO destination ) ;
    def to_part(self, ):

        retval = self.to_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        TO401 = None
        destination402 = None


        TO401_tree = None
        stream_TO = RewriteRuleTokenStream(self._adaptor, "token TO")
        stream_destination = RewriteRuleSubtreeStream(self._adaptor, "rule destination")
        try:
            try:
                # sdl92.g:721:9: ( ( TO destination ) -> ^( TO destination ) )
                # sdl92.g:721:17: ( TO destination )
                pass 
                # sdl92.g:721:17: ( TO destination )
                # sdl92.g:721:18: TO destination
                pass 
                TO401=self.match(self.input, TO, self.FOLLOW_TO_in_to_part8314) 
                if self._state.backtracking == 0:
                    stream_TO.add(TO401)
                self._state.following.append(self.FOLLOW_destination_in_to_part8316)
                destination402 = self.destination()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_destination.add(destination402.tree)




                # AST Rewrite
                # elements: destination, TO
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 722:9: -> ^( TO destination )
                    # sdl92.g:722:17: ^( TO destination )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_TO.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_destination.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "to_part"

    class via_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.via_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "via_part"
    # sdl92.g:724:1: via_part : VIA viabody -> ^( VIA viabody ) ;
    def via_part(self, ):

        retval = self.via_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        VIA403 = None
        viabody404 = None


        VIA403_tree = None
        stream_VIA = RewriteRuleTokenStream(self._adaptor, "token VIA")
        stream_viabody = RewriteRuleSubtreeStream(self._adaptor, "rule viabody")
        try:
            try:
                # sdl92.g:725:9: ( VIA viabody -> ^( VIA viabody ) )
                # sdl92.g:725:17: VIA viabody
                pass 
                VIA403=self.match(self.input, VIA, self.FOLLOW_VIA_in_via_part8360) 
                if self._state.backtracking == 0:
                    stream_VIA.add(VIA403)
                self._state.following.append(self.FOLLOW_viabody_in_via_part8362)
                viabody404 = self.viabody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_viabody.add(viabody404.tree)

                # AST Rewrite
                # elements: viabody, VIA
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 726:9: -> ^( VIA viabody )
                    # sdl92.g:726:17: ^( VIA viabody )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_VIA.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_viabody.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "via_part"

    class viabody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.viabody_return, self).__init__()

            self.tree = None




    # $ANTLR start "viabody"
    # sdl92.g:730:1: viabody : ( ALL -> ^( ALL ) | via_path -> ^( VIAPATH via_path ) );
    def viabody(self, ):

        retval = self.viabody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ALL405 = None
        via_path406 = None


        ALL405_tree = None
        stream_ALL = RewriteRuleTokenStream(self._adaptor, "token ALL")
        stream_via_path = RewriteRuleSubtreeStream(self._adaptor, "rule via_path")
        try:
            try:
                # sdl92.g:731:9: ( ALL -> ^( ALL ) | via_path -> ^( VIAPATH via_path ) )
                alt129 = 2
                LA129_0 = self.input.LA(1)

                if (LA129_0 == ALL) :
                    alt129 = 1
                elif (LA129_0 == ID) :
                    alt129 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 129, 0, self.input)

                    raise nvae

                if alt129 == 1:
                    # sdl92.g:731:17: ALL
                    pass 
                    ALL405=self.match(self.input, ALL, self.FOLLOW_ALL_in_viabody8407) 
                    if self._state.backtracking == 0:
                        stream_ALL.add(ALL405)

                    # AST Rewrite
                    # elements: ALL
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 732:9: -> ^( ALL )
                        # sdl92.g:732:17: ^( ALL )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_ALL.nextNode(), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt129 == 2:
                    # sdl92.g:733:19: via_path
                    pass 
                    self._state.following.append(self.FOLLOW_via_path_in_viabody8446)
                    via_path406 = self.via_path()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_via_path.add(via_path406.tree)

                    # AST Rewrite
                    # elements: via_path
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 734:9: -> ^( VIAPATH via_path )
                        # sdl92.g:734:17: ^( VIAPATH via_path )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VIAPATH, "VIAPATH"), root_1)

                        self._adaptor.addChild(root_1, stream_via_path.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "viabody"

    class destination_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.destination_return, self).__init__()

            self.tree = None




    # $ANTLR start "destination"
    # sdl92.g:737:1: destination : ( pid_expression | process_id | THIS );
    def destination(self, ):

        retval = self.destination_return()
        retval.start = self.input.LT(1)

        root_0 = None

        THIS409 = None
        pid_expression407 = None

        process_id408 = None


        THIS409_tree = None

        try:
            try:
                # sdl92.g:738:9: ( pid_expression | process_id | THIS )
                alt130 = 3
                LA130 = self.input.LA(1)
                if LA130 == P or LA130 == S or LA130 == O:
                    alt130 = 1
                elif LA130 == ID:
                    alt130 = 2
                elif LA130 == THIS:
                    alt130 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 130, 0, self.input)

                    raise nvae

                if alt130 == 1:
                    # sdl92.g:738:17: pid_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_pid_expression_in_destination8490)
                    pid_expression407 = self.pid_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, pid_expression407.tree)


                elif alt130 == 2:
                    # sdl92.g:739:19: process_id
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_process_id_in_destination8510)
                    process_id408 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, process_id408.tree)


                elif alt130 == 3:
                    # sdl92.g:740:19: THIS
                    pass 
                    root_0 = self._adaptor.nil()

                    THIS409=self.match(self.input, THIS, self.FOLLOW_THIS_in_destination8530)
                    if self._state.backtracking == 0:

                        THIS409_tree = self._adaptor.createWithPayload(THIS409)
                        self._adaptor.addChild(root_0, THIS409_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "destination"

    class via_path_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.via_path_return, self).__init__()

            self.tree = None




    # $ANTLR start "via_path"
    # sdl92.g:743:1: via_path : via_path_element ( ',' via_path_element )* -> ( via_path_element )+ ;
    def via_path(self, ):

        retval = self.via_path_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal411 = None
        via_path_element410 = None

        via_path_element412 = None


        char_literal411_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_via_path_element = RewriteRuleSubtreeStream(self._adaptor, "rule via_path_element")
        try:
            try:
                # sdl92.g:744:9: ( via_path_element ( ',' via_path_element )* -> ( via_path_element )+ )
                # sdl92.g:744:17: via_path_element ( ',' via_path_element )*
                pass 
                self._state.following.append(self.FOLLOW_via_path_element_in_via_path8553)
                via_path_element410 = self.via_path_element()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_via_path_element.add(via_path_element410.tree)
                # sdl92.g:744:34: ( ',' via_path_element )*
                while True: #loop131
                    alt131 = 2
                    LA131_0 = self.input.LA(1)

                    if (LA131_0 == COMMA) :
                        alt131 = 1


                    if alt131 == 1:
                        # sdl92.g:744:35: ',' via_path_element
                        pass 
                        char_literal411=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_via_path8556) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal411)
                        self._state.following.append(self.FOLLOW_via_path_element_in_via_path8558)
                        via_path_element412 = self.via_path_element()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_via_path_element.add(via_path_element412.tree)


                    else:
                        break #loop131

                # AST Rewrite
                # elements: via_path_element
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 745:9: -> ( via_path_element )+
                    # sdl92.g:745:17: ( via_path_element )+
                    if not (stream_via_path_element.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_via_path_element.hasNext():
                        self._adaptor.addChild(root_0, stream_via_path_element.nextTree())


                    stream_via_path_element.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "via_path"

    class via_path_element_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.via_path_element_return, self).__init__()

            self.tree = None




    # $ANTLR start "via_path_element"
    # sdl92.g:748:1: via_path_element : ID ;
    def via_path_element(self, ):

        retval = self.via_path_element_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID413 = None

        ID413_tree = None

        try:
            try:
                # sdl92.g:749:9: ( ID )
                # sdl92.g:749:17: ID
                pass 
                root_0 = self._adaptor.nil()

                ID413=self.match(self.input, ID, self.FOLLOW_ID_in_via_path_element8601)
                if self._state.backtracking == 0:

                    ID413_tree = self._adaptor.createWithPayload(ID413)
                    self._adaptor.addChild(root_0, ID413_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "via_path_element"

    class actual_parameters_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.actual_parameters_return, self).__init__()

            self.tree = None




    # $ANTLR start "actual_parameters"
    # sdl92.g:752:1: actual_parameters : '(' expression ( ',' expression )* ')' -> ^( PARAMS ( expression )+ ) ;
    def actual_parameters(self, ):

        retval = self.actual_parameters_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal414 = None
        char_literal416 = None
        char_literal418 = None
        expression415 = None

        expression417 = None


        char_literal414_tree = None
        char_literal416_tree = None
        char_literal418_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:753:9: ( '(' expression ( ',' expression )* ')' -> ^( PARAMS ( expression )+ ) )
                # sdl92.g:753:16: '(' expression ( ',' expression )* ')'
                pass 
                char_literal414=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_actual_parameters8624) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal414)
                self._state.following.append(self.FOLLOW_expression_in_actual_parameters8626)
                expression415 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression415.tree)
                # sdl92.g:753:31: ( ',' expression )*
                while True: #loop132
                    alt132 = 2
                    LA132_0 = self.input.LA(1)

                    if (LA132_0 == COMMA) :
                        alt132 = 1


                    if alt132 == 1:
                        # sdl92.g:753:32: ',' expression
                        pass 
                        char_literal416=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_actual_parameters8629) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal416)
                        self._state.following.append(self.FOLLOW_expression_in_actual_parameters8631)
                        expression417 = self.expression()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_expression.add(expression417.tree)


                    else:
                        break #loop132
                char_literal418=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_actual_parameters8635) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal418)

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 754:9: -> ^( PARAMS ( expression )+ )
                    # sdl92.g:754:16: ^( PARAMS ( expression )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAMS, "PARAMS"), root_1)

                    # sdl92.g:754:25: ( expression )+
                    if not (stream_expression.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_expression.nextTree())


                    stream_expression.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "actual_parameters"

    class task_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.task_return, self).__init__()

            self.tree = None




    # $ANTLR start "task"
    # sdl92.g:757:1: task : ( cif )? ( hyperlink )? TASK ( task_body )? end -> ^( TASK ( cif )? ( hyperlink )? ( end )? ( task_body )? ) ;
    def task(self, ):

        retval = self.task_return()
        retval.start = self.input.LT(1)

        root_0 = None

        TASK421 = None
        cif419 = None

        hyperlink420 = None

        task_body422 = None

        end423 = None


        TASK421_tree = None
        stream_TASK = RewriteRuleTokenStream(self._adaptor, "token TASK")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_task_body = RewriteRuleSubtreeStream(self._adaptor, "rule task_body")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:758:9: ( ( cif )? ( hyperlink )? TASK ( task_body )? end -> ^( TASK ( cif )? ( hyperlink )? ( end )? ( task_body )? ) )
                # sdl92.g:758:17: ( cif )? ( hyperlink )? TASK ( task_body )? end
                pass 
                # sdl92.g:758:17: ( cif )?
                alt133 = 2
                LA133_0 = self.input.LA(1)

                if (LA133_0 == 217) :
                    LA133_1 = self.input.LA(2)

                    if (LA133_1 == ANSWER or LA133_1 == COMMENT or LA133_1 == CONNECT or LA133_1 == DECISION or LA133_1 == INPUT or (JOIN <= LA133_1 <= LABEL) or LA133_1 == NEXTSTATE or LA133_1 == OUTPUT or (PROCEDURE <= LA133_1 <= PROCEDURE_CALL) or (PROCESS <= LA133_1 <= PROVIDED) or LA133_1 == RETURN or LA133_1 == STATE or LA133_1 == STOP or LA133_1 == TASK or LA133_1 == TEXT or LA133_1 == START) :
                        alt133 = 1
                if alt133 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_task8679)
                    cif419 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif419.tree)



                # sdl92.g:759:17: ( hyperlink )?
                alt134 = 2
                LA134_0 = self.input.LA(1)

                if (LA134_0 == 217) :
                    alt134 = 1
                if alt134 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_task8698)
                    hyperlink420 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink420.tree)



                TASK421=self.match(self.input, TASK, self.FOLLOW_TASK_in_task8717) 
                if self._state.backtracking == 0:
                    stream_TASK.add(TASK421)
                # sdl92.g:760:22: ( task_body )?
                alt135 = 2
                LA135_0 = self.input.LA(1)

                if (LA135_0 == FOR or LA135_0 == STRING or LA135_0 == ID) :
                    alt135 = 1
                if alt135 == 1:
                    # sdl92.g:0:0: task_body
                    pass 
                    self._state.following.append(self.FOLLOW_task_body_in_task8719)
                    task_body422 = self.task_body()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_task_body.add(task_body422.tree)



                self._state.following.append(self.FOLLOW_end_in_task8722)
                end423 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end423.tree)

                # AST Rewrite
                # elements: TASK, task_body, end, hyperlink, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 761:9: -> ^( TASK ( cif )? ( hyperlink )? ( end )? ( task_body )? )
                    # sdl92.g:761:17: ^( TASK ( cif )? ( hyperlink )? ( end )? ( task_body )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_TASK.nextNode(), root_1)

                    # sdl92.g:761:24: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:761:29: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:761:40: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    # sdl92.g:761:45: ( task_body )?
                    if stream_task_body.hasNext():
                        self._adaptor.addChild(root_1, stream_task_body.nextTree())


                    stream_task_body.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "task"

    class task_body_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.task_body_return, self).__init__()

            self.tree = None




    # $ANTLR start "task_body"
    # sdl92.g:764:1: task_body : ( ( assignement_statement ( ',' assignement_statement )* ) -> ^( TASK_BODY ( assignement_statement )+ ) | ( informal_text ( ',' informal_text )* ) -> ^( TASK_BODY ( informal_text )+ ) | ( forloop ( ',' forloop )* ) -> ^( TASK_BODY ( forloop )+ ) );
    def task_body(self, ):

        retval = self.task_body_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal425 = None
        char_literal428 = None
        char_literal431 = None
        assignement_statement424 = None

        assignement_statement426 = None

        informal_text427 = None

        informal_text429 = None

        forloop430 = None

        forloop432 = None


        char_literal425_tree = None
        char_literal428_tree = None
        char_literal431_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_informal_text = RewriteRuleSubtreeStream(self._adaptor, "rule informal_text")
        stream_assignement_statement = RewriteRuleSubtreeStream(self._adaptor, "rule assignement_statement")
        stream_forloop = RewriteRuleSubtreeStream(self._adaptor, "rule forloop")
        try:
            try:
                # sdl92.g:765:9: ( ( assignement_statement ( ',' assignement_statement )* ) -> ^( TASK_BODY ( assignement_statement )+ ) | ( informal_text ( ',' informal_text )* ) -> ^( TASK_BODY ( informal_text )+ ) | ( forloop ( ',' forloop )* ) -> ^( TASK_BODY ( forloop )+ ) )
                alt139 = 3
                LA139 = self.input.LA(1)
                if LA139 == ID:
                    alt139 = 1
                elif LA139 == STRING:
                    alt139 = 2
                elif LA139 == FOR:
                    alt139 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 139, 0, self.input)

                    raise nvae

                if alt139 == 1:
                    # sdl92.g:765:17: ( assignement_statement ( ',' assignement_statement )* )
                    pass 
                    # sdl92.g:765:17: ( assignement_statement ( ',' assignement_statement )* )
                    # sdl92.g:765:18: assignement_statement ( ',' assignement_statement )*
                    pass 
                    self._state.following.append(self.FOLLOW_assignement_statement_in_task_body8777)
                    assignement_statement424 = self.assignement_statement()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_assignement_statement.add(assignement_statement424.tree)
                    # sdl92.g:765:40: ( ',' assignement_statement )*
                    while True: #loop136
                        alt136 = 2
                        LA136_0 = self.input.LA(1)

                        if (LA136_0 == COMMA) :
                            alt136 = 1


                        if alt136 == 1:
                            # sdl92.g:765:41: ',' assignement_statement
                            pass 
                            char_literal425=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_task_body8780) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal425)
                            self._state.following.append(self.FOLLOW_assignement_statement_in_task_body8782)
                            assignement_statement426 = self.assignement_statement()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_assignement_statement.add(assignement_statement426.tree)


                        else:
                            break #loop136




                    # AST Rewrite
                    # elements: assignement_statement
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 766:9: -> ^( TASK_BODY ( assignement_statement )+ )
                        # sdl92.g:766:17: ^( TASK_BODY ( assignement_statement )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TASK_BODY, "TASK_BODY"), root_1)

                        # sdl92.g:766:29: ( assignement_statement )+
                        if not (stream_assignement_statement.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_assignement_statement.hasNext():
                            self._adaptor.addChild(root_1, stream_assignement_statement.nextTree())


                        stream_assignement_statement.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt139 == 2:
                    # sdl92.g:767:19: ( informal_text ( ',' informal_text )* )
                    pass 
                    # sdl92.g:767:19: ( informal_text ( ',' informal_text )* )
                    # sdl92.g:767:20: informal_text ( ',' informal_text )*
                    pass 
                    self._state.following.append(self.FOLLOW_informal_text_in_task_body8828)
                    informal_text427 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_informal_text.add(informal_text427.tree)
                    # sdl92.g:767:34: ( ',' informal_text )*
                    while True: #loop137
                        alt137 = 2
                        LA137_0 = self.input.LA(1)

                        if (LA137_0 == COMMA) :
                            alt137 = 1


                        if alt137 == 1:
                            # sdl92.g:767:35: ',' informal_text
                            pass 
                            char_literal428=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_task_body8831) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal428)
                            self._state.following.append(self.FOLLOW_informal_text_in_task_body8833)
                            informal_text429 = self.informal_text()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_informal_text.add(informal_text429.tree)


                        else:
                            break #loop137




                    # AST Rewrite
                    # elements: informal_text
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 768:9: -> ^( TASK_BODY ( informal_text )+ )
                        # sdl92.g:768:17: ^( TASK_BODY ( informal_text )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TASK_BODY, "TASK_BODY"), root_1)

                        # sdl92.g:768:29: ( informal_text )+
                        if not (stream_informal_text.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_informal_text.hasNext():
                            self._adaptor.addChild(root_1, stream_informal_text.nextTree())


                        stream_informal_text.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt139 == 3:
                    # sdl92.g:769:19: ( forloop ( ',' forloop )* )
                    pass 
                    # sdl92.g:769:19: ( forloop ( ',' forloop )* )
                    # sdl92.g:769:20: forloop ( ',' forloop )*
                    pass 
                    self._state.following.append(self.FOLLOW_forloop_in_task_body8879)
                    forloop430 = self.forloop()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_forloop.add(forloop430.tree)
                    # sdl92.g:769:28: ( ',' forloop )*
                    while True: #loop138
                        alt138 = 2
                        LA138_0 = self.input.LA(1)

                        if (LA138_0 == COMMA) :
                            alt138 = 1


                        if alt138 == 1:
                            # sdl92.g:769:29: ',' forloop
                            pass 
                            char_literal431=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_task_body8882) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal431)
                            self._state.following.append(self.FOLLOW_forloop_in_task_body8884)
                            forloop432 = self.forloop()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_forloop.add(forloop432.tree)


                        else:
                            break #loop138




                    # AST Rewrite
                    # elements: forloop
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 770:9: -> ^( TASK_BODY ( forloop )+ )
                        # sdl92.g:770:17: ^( TASK_BODY ( forloop )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TASK_BODY, "TASK_BODY"), root_1)

                        # sdl92.g:770:29: ( forloop )+
                        if not (stream_forloop.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_forloop.hasNext():
                            self._adaptor.addChild(root_1, stream_forloop.nextTree())


                        stream_forloop.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "task_body"

    class forloop_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.forloop_return, self).__init__()

            self.tree = None




    # $ANTLR start "forloop"
    # sdl92.g:774:1: forloop : FOR variable_id IN ( variable | range ) ':' ( transition )? ENDFOR -> ^( FOR variable_id ( variable )? ( range )? ( transition )? ) ;
    def forloop(self, ):

        retval = self.forloop_return()
        retval.start = self.input.LT(1)

        root_0 = None

        FOR433 = None
        IN435 = None
        char_literal438 = None
        ENDFOR440 = None
        variable_id434 = None

        variable436 = None

        range437 = None

        transition439 = None


        FOR433_tree = None
        IN435_tree = None
        char_literal438_tree = None
        ENDFOR440_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_ENDFOR = RewriteRuleTokenStream(self._adaptor, "token ENDFOR")
        stream_FOR = RewriteRuleTokenStream(self._adaptor, "token FOR")
        stream_IN = RewriteRuleTokenStream(self._adaptor, "token IN")
        stream_range = RewriteRuleSubtreeStream(self._adaptor, "rule range")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        stream_variable = RewriteRuleSubtreeStream(self._adaptor, "rule variable")
        try:
            try:
                # sdl92.g:775:9: ( FOR variable_id IN ( variable | range ) ':' ( transition )? ENDFOR -> ^( FOR variable_id ( variable )? ( range )? ( transition )? ) )
                # sdl92.g:775:17: FOR variable_id IN ( variable | range ) ':' ( transition )? ENDFOR
                pass 
                FOR433=self.match(self.input, FOR, self.FOLLOW_FOR_in_forloop8941) 
                if self._state.backtracking == 0:
                    stream_FOR.add(FOR433)
                self._state.following.append(self.FOLLOW_variable_id_in_forloop8943)
                variable_id434 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id434.tree)
                IN435=self.match(self.input, IN, self.FOLLOW_IN_in_forloop8945) 
                if self._state.backtracking == 0:
                    stream_IN.add(IN435)
                # sdl92.g:775:36: ( variable | range )
                alt140 = 2
                LA140_0 = self.input.LA(1)

                if (LA140_0 == ID) :
                    alt140 = 1
                elif (LA140_0 == RANGE) :
                    alt140 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 140, 0, self.input)

                    raise nvae

                if alt140 == 1:
                    # sdl92.g:775:37: variable
                    pass 
                    self._state.following.append(self.FOLLOW_variable_in_forloop8948)
                    variable436 = self.variable()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_variable.add(variable436.tree)


                elif alt140 == 2:
                    # sdl92.g:775:48: range
                    pass 
                    self._state.following.append(self.FOLLOW_range_in_forloop8952)
                    range437 = self.range()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_range.add(range437.tree)



                char_literal438=self.match(self.input, 212, self.FOLLOW_212_in_forloop8955) 
                if self._state.backtracking == 0:
                    stream_212.add(char_literal438)
                # sdl92.g:776:17: ( transition )?
                alt141 = 2
                LA141_0 = self.input.LA(1)

                if (LA141_0 == ALTERNATIVE or LA141_0 == DECISION or LA141_0 == EXPORT or LA141_0 == FOR or LA141_0 == JOIN or LA141_0 == NEXTSTATE or LA141_0 == OUTPUT or (RESET <= LA141_0 <= RETURN) or LA141_0 == SET or (STOP <= LA141_0 <= STRING) or LA141_0 == TASK or LA141_0 == CALL or LA141_0 == CREATE or LA141_0 == ID or LA141_0 == 217) :
                    alt141 = 1
                if alt141 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_forloop8973)
                    transition439 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition439.tree)



                ENDFOR440=self.match(self.input, ENDFOR, self.FOLLOW_ENDFOR_in_forloop8992) 
                if self._state.backtracking == 0:
                    stream_ENDFOR.add(ENDFOR440)

                # AST Rewrite
                # elements: variable, transition, variable_id, range, FOR
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 778:9: -> ^( FOR variable_id ( variable )? ( range )? ( transition )? )
                    # sdl92.g:778:17: ^( FOR variable_id ( variable )? ( range )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_FOR.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_variable_id.nextTree())
                    # sdl92.g:778:35: ( variable )?
                    if stream_variable.hasNext():
                        self._adaptor.addChild(root_1, stream_variable.nextTree())


                    stream_variable.reset();
                    # sdl92.g:778:45: ( range )?
                    if stream_range.hasNext():
                        self._adaptor.addChild(root_1, stream_range.nextTree())


                    stream_range.reset();
                    # sdl92.g:778:52: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "forloop"

    class range_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.range_return, self).__init__()

            self.tree = None




    # $ANTLR start "range"
    # sdl92.g:780:1: range : RANGE L_PAREN a= ground_expression ( COMMA b= ground_expression )? ( COMMA step= INT )? R_PAREN -> ^( RANGE $a ( $b)? ( $step)? ) ;
    def range(self, ):

        retval = self.range_return()
        retval.start = self.input.LT(1)

        root_0 = None

        step = None
        RANGE441 = None
        L_PAREN442 = None
        COMMA443 = None
        COMMA444 = None
        R_PAREN445 = None
        a = None

        b = None


        step_tree = None
        RANGE441_tree = None
        L_PAREN442_tree = None
        COMMA443_tree = None
        COMMA444_tree = None
        R_PAREN445_tree = None
        stream_RANGE = RewriteRuleTokenStream(self._adaptor, "token RANGE")
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_ground_expression = RewriteRuleSubtreeStream(self._adaptor, "rule ground_expression")
        try:
            try:
                # sdl92.g:781:9: ( RANGE L_PAREN a= ground_expression ( COMMA b= ground_expression )? ( COMMA step= INT )? R_PAREN -> ^( RANGE $a ( $b)? ( $step)? ) )
                # sdl92.g:781:17: RANGE L_PAREN a= ground_expression ( COMMA b= ground_expression )? ( COMMA step= INT )? R_PAREN
                pass 
                RANGE441=self.match(self.input, RANGE, self.FOLLOW_RANGE_in_range9044) 
                if self._state.backtracking == 0:
                    stream_RANGE.add(RANGE441)
                L_PAREN442=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_range9062) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN442)
                self._state.following.append(self.FOLLOW_ground_expression_in_range9066)
                a = self.ground_expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_ground_expression.add(a.tree)
                # sdl92.g:783:17: ( COMMA b= ground_expression )?
                alt142 = 2
                LA142_0 = self.input.LA(1)

                if (LA142_0 == COMMA) :
                    LA142_1 = self.input.LA(2)

                    if (LA142_1 == INT) :
                        LA142_3 = self.input.LA(3)

                        if (self.synpred182_sdl92()) :
                            alt142 = 1
                    elif (LA142_1 == BITSTR or LA142_1 == FLOAT or LA142_1 == IF or LA142_1 == OCTSTR or LA142_1 == STRING or LA142_1 == L_PAREN or LA142_1 == ID or LA142_1 == DASH or (NOT <= LA142_1 <= MINUS_INFINITY) or LA142_1 == L_BRACKET) :
                        alt142 = 1
                if alt142 == 1:
                    # sdl92.g:783:18: COMMA b= ground_expression
                    pass 
                    COMMA443=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_range9085) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA443)
                    self._state.following.append(self.FOLLOW_ground_expression_in_range9089)
                    b = self.ground_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_ground_expression.add(b.tree)



                # sdl92.g:783:46: ( COMMA step= INT )?
                alt143 = 2
                LA143_0 = self.input.LA(1)

                if (LA143_0 == COMMA) :
                    alt143 = 1
                if alt143 == 1:
                    # sdl92.g:783:47: COMMA step= INT
                    pass 
                    COMMA444=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_range9094) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA444)
                    step=self.match(self.input, INT, self.FOLLOW_INT_in_range9098) 
                    if self._state.backtracking == 0:
                        stream_INT.add(step)



                R_PAREN445=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_range9118) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN445)

                # AST Rewrite
                # elements: step, RANGE, b, a
                # token labels: step
                # rule labels: retval, b, a
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_step = RewriteRuleTokenStream(self._adaptor, "token step", step)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if b is not None:
                        stream_b = RewriteRuleSubtreeStream(self._adaptor, "rule b", b.tree)
                    else:
                        stream_b = RewriteRuleSubtreeStream(self._adaptor, "token b", None)


                    if a is not None:
                        stream_a = RewriteRuleSubtreeStream(self._adaptor, "rule a", a.tree)
                    else:
                        stream_a = RewriteRuleSubtreeStream(self._adaptor, "token a", None)


                    root_0 = self._adaptor.nil()
                    # 785:9: -> ^( RANGE $a ( $b)? ( $step)? )
                    # sdl92.g:785:17: ^( RANGE $a ( $b)? ( $step)? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_RANGE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_a.nextTree())
                    # sdl92.g:785:28: ( $b)?
                    if stream_b.hasNext():
                        self._adaptor.addChild(root_1, stream_b.nextTree())


                    stream_b.reset();
                    # sdl92.g:785:32: ( $step)?
                    if stream_step.hasNext():
                        self._adaptor.addChild(root_1, stream_step.nextNode())


                    stream_step.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "range"

    class assignement_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.assignement_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "assignement_statement"
    # sdl92.g:787:1: assignement_statement : variable ':=' expression -> ^( ASSIGN variable expression ) ;
    def assignement_statement(self, ):

        retval = self.assignement_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal447 = None
        variable446 = None

        expression448 = None


        string_literal447_tree = None
        stream_ASSIG_OP = RewriteRuleTokenStream(self._adaptor, "token ASSIG_OP")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_variable = RewriteRuleSubtreeStream(self._adaptor, "rule variable")
        try:
            try:
                # sdl92.g:788:9: ( variable ':=' expression -> ^( ASSIGN variable expression ) )
                # sdl92.g:788:17: variable ':=' expression
                pass 
                self._state.following.append(self.FOLLOW_variable_in_assignement_statement9170)
                variable446 = self.variable()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable.add(variable446.tree)
                string_literal447=self.match(self.input, ASSIG_OP, self.FOLLOW_ASSIG_OP_in_assignement_statement9172) 
                if self._state.backtracking == 0:
                    stream_ASSIG_OP.add(string_literal447)
                self._state.following.append(self.FOLLOW_expression_in_assignement_statement9174)
                expression448 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression448.tree)

                # AST Rewrite
                # elements: expression, variable
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 789:9: -> ^( ASSIGN variable expression )
                    # sdl92.g:789:17: ^( ASSIGN variable expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ASSIGN, "ASSIGN"), root_1)

                    self._adaptor.addChild(root_1, stream_variable.nextTree())
                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "assignement_statement"

    class variable_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable"
    # sdl92.g:793:1: variable : ( ID ( primary_params )+ -> ^( PATH ID ( primary_params )+ ) | ID -> ^( VARIABLE ID ) );
    def variable(self, ):

        retval = self.variable_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID449 = None
        ID451 = None
        primary_params450 = None


        ID449_tree = None
        ID451_tree = None
        stream_ID = RewriteRuleTokenStream(self._adaptor, "token ID")
        stream_primary_params = RewriteRuleSubtreeStream(self._adaptor, "rule primary_params")
        try:
            try:
                # sdl92.g:794:9: ( ID ( primary_params )+ -> ^( PATH ID ( primary_params )+ ) | ID -> ^( VARIABLE ID ) )
                alt145 = 2
                LA145_0 = self.input.LA(1)

                if (LA145_0 == ID) :
                    LA145_1 = self.input.LA(2)

                    if (LA145_1 == L_PAREN or LA145_1 == 213) :
                        alt145 = 1
                    elif (LA145_1 == EOF or LA145_1 == ASSIG_OP or LA145_1 == 212) :
                        alt145 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 145, 1, self.input)

                        raise nvae

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 145, 0, self.input)

                    raise nvae

                if alt145 == 1:
                    # sdl92.g:794:17: ID ( primary_params )+
                    pass 
                    ID449=self.match(self.input, ID, self.FOLLOW_ID_in_variable9221) 
                    if self._state.backtracking == 0:
                        stream_ID.add(ID449)
                    # sdl92.g:794:20: ( primary_params )+
                    cnt144 = 0
                    while True: #loop144
                        alt144 = 2
                        LA144_0 = self.input.LA(1)

                        if (LA144_0 == L_PAREN or LA144_0 == 213) :
                            alt144 = 1


                        if alt144 == 1:
                            # sdl92.g:0:0: primary_params
                            pass 
                            self._state.following.append(self.FOLLOW_primary_params_in_variable9223)
                            primary_params450 = self.primary_params()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_primary_params.add(primary_params450.tree)


                        else:
                            if cnt144 >= 1:
                                break #loop144

                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            eee = EarlyExitException(144, self.input)
                            raise eee

                        cnt144 += 1

                    # AST Rewrite
                    # elements: primary_params, ID
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 794:40: -> ^( PATH ID ( primary_params )+ )
                        # sdl92.g:794:44: ^( PATH ID ( primary_params )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PATH, "PATH"), root_1)

                        self._adaptor.addChild(root_1, stream_ID.nextNode())
                        # sdl92.g:794:54: ( primary_params )+
                        if not (stream_primary_params.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_primary_params.hasNext():
                            self._adaptor.addChild(root_1, stream_primary_params.nextTree())


                        stream_primary_params.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt145 == 2:
                    # sdl92.g:795:17: ID
                    pass 
                    ID451=self.match(self.input, ID, self.FOLLOW_ID_in_variable9258) 
                    if self._state.backtracking == 0:
                        stream_ID.add(ID451)

                    # AST Rewrite
                    # elements: ID
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 795:40: -> ^( VARIABLE ID )
                        # sdl92.g:795:44: ^( VARIABLE ID )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VARIABLE, "VARIABLE"), root_1)

                        self._adaptor.addChild(root_1, stream_ID.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable"

    class field_selection_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_selection_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_selection"
    # sdl92.g:798:1: field_selection : ( ( '!' | '.' ) field_name ) ;
    def field_selection(self, ):

        retval = self.field_selection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set452 = None
        field_name453 = None


        set452_tree = None

        try:
            try:
                # sdl92.g:799:9: ( ( ( '!' | '.' ) field_name ) )
                # sdl92.g:799:17: ( ( '!' | '.' ) field_name )
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:799:17: ( ( '!' | '.' ) field_name )
                # sdl92.g:799:18: ( '!' | '.' ) field_name
                pass 
                set452 = self.input.LT(1)
                if self.input.LA(1) == DOT or self.input.LA(1) == 213:
                    self.input.consume()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, self._adaptor.createWithPayload(set452))
                    self._state.errorRecovery = False

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    mse = MismatchedSetException(None, self.input)
                    raise mse


                self._state.following.append(self.FOLLOW_field_name_in_field_selection9317)
                field_name453 = self.field_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, field_name453.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_selection"

    class expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "expression"
    # sdl92.g:801:1: expression : binary_expression ;
    def expression(self, ):

        retval = self.expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        binary_expression454 = None



        try:
            try:
                # sdl92.g:802:9: ( binary_expression )
                # sdl92.g:802:17: binary_expression
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_binary_expression_in_expression9340)
                binary_expression454 = self.binary_expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, binary_expression454.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "expression"

    class binary_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.binary_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "binary_expression"
    # sdl92.g:804:1: binary_expression : binary_expression_0 ( IMPLIES binary_expression_0 )* ;
    def binary_expression(self, ):

        retval = self.binary_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IMPLIES456 = None
        binary_expression_0455 = None

        binary_expression_0457 = None


        IMPLIES456_tree = None

        try:
            try:
                # sdl92.g:805:9: ( binary_expression_0 ( IMPLIES binary_expression_0 )* )
                # sdl92.g:805:17: binary_expression_0 ( IMPLIES binary_expression_0 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_binary_expression_0_in_binary_expression9362)
                binary_expression_0455 = self.binary_expression_0()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, binary_expression_0455.tree)
                # sdl92.g:805:37: ( IMPLIES binary_expression_0 )*
                while True: #loop146
                    alt146 = 2
                    LA146_0 = self.input.LA(1)

                    if (LA146_0 == IMPLIES) :
                        LA146_2 = self.input.LA(2)

                        if (self.synpred187_sdl92()) :
                            alt146 = 1




                    if alt146 == 1:
                        # sdl92.g:805:39: IMPLIES binary_expression_0
                        pass 
                        IMPLIES456=self.match(self.input, IMPLIES, self.FOLLOW_IMPLIES_in_binary_expression9366)
                        if self._state.backtracking == 0:

                            IMPLIES456_tree = self._adaptor.createWithPayload(IMPLIES456)
                            root_0 = self._adaptor.becomeRoot(IMPLIES456_tree, root_0)

                        self._state.following.append(self.FOLLOW_binary_expression_0_in_binary_expression9369)
                        binary_expression_0457 = self.binary_expression_0()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, binary_expression_0457.tree)


                    else:
                        break #loop146



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "binary_expression"

    class binary_expression_0_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.binary_expression_0_return, self).__init__()

            self.tree = None




    # $ANTLR start "binary_expression_0"
    # sdl92.g:806:1: binary_expression_0 : binary_expression_1 ( ( ( OR ( ELSE )? ) | XOR ) binary_expression_1 )* ;
    def binary_expression_0(self, ):

        retval = self.binary_expression_0_return()
        retval.start = self.input.LT(1)

        root_0 = None

        OR459 = None
        ELSE460 = None
        XOR461 = None
        binary_expression_1458 = None

        binary_expression_1462 = None


        OR459_tree = None
        ELSE460_tree = None
        XOR461_tree = None

        try:
            try:
                # sdl92.g:807:9: ( binary_expression_1 ( ( ( OR ( ELSE )? ) | XOR ) binary_expression_1 )* )
                # sdl92.g:807:17: binary_expression_1 ( ( ( OR ( ELSE )? ) | XOR ) binary_expression_1 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_binary_expression_1_in_binary_expression_09392)
                binary_expression_1458 = self.binary_expression_1()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, binary_expression_1458.tree)
                # sdl92.g:807:37: ( ( ( OR ( ELSE )? ) | XOR ) binary_expression_1 )*
                while True: #loop149
                    alt149 = 2
                    LA149_0 = self.input.LA(1)

                    if (LA149_0 == OR) :
                        LA149_2 = self.input.LA(2)

                        if (self.synpred190_sdl92()) :
                            alt149 = 1


                    elif (LA149_0 == XOR) :
                        LA149_3 = self.input.LA(2)

                        if (self.synpred190_sdl92()) :
                            alt149 = 1




                    if alt149 == 1:
                        # sdl92.g:807:38: ( ( OR ( ELSE )? ) | XOR ) binary_expression_1
                        pass 
                        # sdl92.g:807:38: ( ( OR ( ELSE )? ) | XOR )
                        alt148 = 2
                        LA148_0 = self.input.LA(1)

                        if (LA148_0 == OR) :
                            alt148 = 1
                        elif (LA148_0 == XOR) :
                            alt148 = 2
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 148, 0, self.input)

                            raise nvae

                        if alt148 == 1:
                            # sdl92.g:807:40: ( OR ( ELSE )? )
                            pass 
                            # sdl92.g:807:40: ( OR ( ELSE )? )
                            # sdl92.g:807:41: OR ( ELSE )?
                            pass 
                            OR459=self.match(self.input, OR, self.FOLLOW_OR_in_binary_expression_09398)
                            if self._state.backtracking == 0:

                                OR459_tree = self._adaptor.createWithPayload(OR459)
                                root_0 = self._adaptor.becomeRoot(OR459_tree, root_0)

                            # sdl92.g:807:45: ( ELSE )?
                            alt147 = 2
                            LA147_0 = self.input.LA(1)

                            if (LA147_0 == ELSE) :
                                alt147 = 1
                            if alt147 == 1:
                                # sdl92.g:0:0: ELSE
                                pass 
                                ELSE460=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_binary_expression_09401)
                                if self._state.backtracking == 0:

                                    ELSE460_tree = self._adaptor.createWithPayload(ELSE460)
                                    self._adaptor.addChild(root_0, ELSE460_tree)









                        elif alt148 == 2:
                            # sdl92.g:807:54: XOR
                            pass 
                            XOR461=self.match(self.input, XOR, self.FOLLOW_XOR_in_binary_expression_09407)
                            if self._state.backtracking == 0:

                                XOR461_tree = self._adaptor.createWithPayload(XOR461)
                                root_0 = self._adaptor.becomeRoot(XOR461_tree, root_0)




                        self._state.following.append(self.FOLLOW_binary_expression_1_in_binary_expression_09412)
                        binary_expression_1462 = self.binary_expression_1()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, binary_expression_1462.tree)


                    else:
                        break #loop149



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "binary_expression_0"

    class binary_expression_1_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.binary_expression_1_return, self).__init__()

            self.tree = None




    # $ANTLR start "binary_expression_1"
    # sdl92.g:808:1: binary_expression_1 : binary_expression_2 ( AND ( THEN )? binary_expression_2 )* ;
    def binary_expression_1(self, ):

        retval = self.binary_expression_1_return()
        retval.start = self.input.LT(1)

        root_0 = None

        AND464 = None
        THEN465 = None
        binary_expression_2463 = None

        binary_expression_2466 = None


        AND464_tree = None
        THEN465_tree = None

        try:
            try:
                # sdl92.g:809:9: ( binary_expression_2 ( AND ( THEN )? binary_expression_2 )* )
                # sdl92.g:809:17: binary_expression_2 ( AND ( THEN )? binary_expression_2 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_binary_expression_2_in_binary_expression_19435)
                binary_expression_2463 = self.binary_expression_2()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, binary_expression_2463.tree)
                # sdl92.g:809:37: ( AND ( THEN )? binary_expression_2 )*
                while True: #loop151
                    alt151 = 2
                    LA151_0 = self.input.LA(1)

                    if (LA151_0 == AND) :
                        LA151_2 = self.input.LA(2)

                        if (self.synpred192_sdl92()) :
                            alt151 = 1




                    if alt151 == 1:
                        # sdl92.g:809:39: AND ( THEN )? binary_expression_2
                        pass 
                        AND464=self.match(self.input, AND, self.FOLLOW_AND_in_binary_expression_19439)
                        if self._state.backtracking == 0:

                            AND464_tree = self._adaptor.createWithPayload(AND464)
                            root_0 = self._adaptor.becomeRoot(AND464_tree, root_0)

                        # sdl92.g:809:44: ( THEN )?
                        alt150 = 2
                        LA150_0 = self.input.LA(1)

                        if (LA150_0 == THEN) :
                            alt150 = 1
                        if alt150 == 1:
                            # sdl92.g:0:0: THEN
                            pass 
                            THEN465=self.match(self.input, THEN, self.FOLLOW_THEN_in_binary_expression_19442)
                            if self._state.backtracking == 0:

                                THEN465_tree = self._adaptor.createWithPayload(THEN465)
                                self._adaptor.addChild(root_0, THEN465_tree)




                        self._state.following.append(self.FOLLOW_binary_expression_2_in_binary_expression_19445)
                        binary_expression_2466 = self.binary_expression_2()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, binary_expression_2466.tree)


                    else:
                        break #loop151



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "binary_expression_1"

    class binary_expression_2_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.binary_expression_2_return, self).__init__()

            self.tree = None




    # $ANTLR start "binary_expression_2"
    # sdl92.g:810:1: binary_expression_2 : binary_expression_3 ( ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3 )* ;
    def binary_expression_2(self, ):

        retval = self.binary_expression_2_return()
        retval.start = self.input.LT(1)

        root_0 = None

        EQ468 = None
        NEQ469 = None
        GT470 = None
        GE471 = None
        LT472 = None
        LE473 = None
        IN474 = None
        binary_expression_3467 = None

        binary_expression_3475 = None


        EQ468_tree = None
        NEQ469_tree = None
        GT470_tree = None
        GE471_tree = None
        LT472_tree = None
        LE473_tree = None
        IN474_tree = None

        try:
            try:
                # sdl92.g:811:9: ( binary_expression_3 ( ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3 )* )
                # sdl92.g:811:17: binary_expression_3 ( ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_binary_expression_3_in_binary_expression_29468)
                binary_expression_3467 = self.binary_expression_3()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, binary_expression_3467.tree)
                # sdl92.g:811:37: ( ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3 )*
                while True: #loop153
                    alt153 = 2
                    alt153 = self.dfa153.predict(self.input)
                    if alt153 == 1:
                        # sdl92.g:811:38: ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3
                        pass 
                        # sdl92.g:811:38: ( EQ | NEQ | GT | GE | LT | LE | IN )
                        alt152 = 7
                        LA152 = self.input.LA(1)
                        if LA152 == EQ:
                            alt152 = 1
                        elif LA152 == NEQ:
                            alt152 = 2
                        elif LA152 == GT:
                            alt152 = 3
                        elif LA152 == GE:
                            alt152 = 4
                        elif LA152 == LT:
                            alt152 = 5
                        elif LA152 == LE:
                            alt152 = 6
                        elif LA152 == IN:
                            alt152 = 7
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 152, 0, self.input)

                            raise nvae

                        if alt152 == 1:
                            # sdl92.g:811:40: EQ
                            pass 
                            EQ468=self.match(self.input, EQ, self.FOLLOW_EQ_in_binary_expression_29473)
                            if self._state.backtracking == 0:

                                EQ468_tree = self._adaptor.createWithPayload(EQ468)
                                root_0 = self._adaptor.becomeRoot(EQ468_tree, root_0)



                        elif alt152 == 2:
                            # sdl92.g:811:46: NEQ
                            pass 
                            NEQ469=self.match(self.input, NEQ, self.FOLLOW_NEQ_in_binary_expression_29478)
                            if self._state.backtracking == 0:

                                NEQ469_tree = self._adaptor.createWithPayload(NEQ469)
                                root_0 = self._adaptor.becomeRoot(NEQ469_tree, root_0)



                        elif alt152 == 3:
                            # sdl92.g:811:53: GT
                            pass 
                            GT470=self.match(self.input, GT, self.FOLLOW_GT_in_binary_expression_29483)
                            if self._state.backtracking == 0:

                                GT470_tree = self._adaptor.createWithPayload(GT470)
                                root_0 = self._adaptor.becomeRoot(GT470_tree, root_0)



                        elif alt152 == 4:
                            # sdl92.g:811:59: GE
                            pass 
                            GE471=self.match(self.input, GE, self.FOLLOW_GE_in_binary_expression_29488)
                            if self._state.backtracking == 0:

                                GE471_tree = self._adaptor.createWithPayload(GE471)
                                root_0 = self._adaptor.becomeRoot(GE471_tree, root_0)



                        elif alt152 == 5:
                            # sdl92.g:811:65: LT
                            pass 
                            LT472=self.match(self.input, LT, self.FOLLOW_LT_in_binary_expression_29493)
                            if self._state.backtracking == 0:

                                LT472_tree = self._adaptor.createWithPayload(LT472)
                                root_0 = self._adaptor.becomeRoot(LT472_tree, root_0)



                        elif alt152 == 6:
                            # sdl92.g:811:71: LE
                            pass 
                            LE473=self.match(self.input, LE, self.FOLLOW_LE_in_binary_expression_29498)
                            if self._state.backtracking == 0:

                                LE473_tree = self._adaptor.createWithPayload(LE473)
                                root_0 = self._adaptor.becomeRoot(LE473_tree, root_0)



                        elif alt152 == 7:
                            # sdl92.g:811:77: IN
                            pass 
                            IN474=self.match(self.input, IN, self.FOLLOW_IN_in_binary_expression_29503)
                            if self._state.backtracking == 0:

                                IN474_tree = self._adaptor.createWithPayload(IN474)
                                root_0 = self._adaptor.becomeRoot(IN474_tree, root_0)




                        self._state.following.append(self.FOLLOW_binary_expression_3_in_binary_expression_29508)
                        binary_expression_3475 = self.binary_expression_3()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, binary_expression_3475.tree)


                    else:
                        break #loop153



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "binary_expression_2"

    class binary_expression_3_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.binary_expression_3_return, self).__init__()

            self.tree = None




    # $ANTLR start "binary_expression_3"
    # sdl92.g:812:1: binary_expression_3 : binary_expression_4 ( ( PLUS | DASH | APPEND ) binary_expression_4 )* ;
    def binary_expression_3(self, ):

        retval = self.binary_expression_3_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PLUS477 = None
        DASH478 = None
        APPEND479 = None
        binary_expression_4476 = None

        binary_expression_4480 = None


        PLUS477_tree = None
        DASH478_tree = None
        APPEND479_tree = None

        try:
            try:
                # sdl92.g:813:9: ( binary_expression_4 ( ( PLUS | DASH | APPEND ) binary_expression_4 )* )
                # sdl92.g:813:17: binary_expression_4 ( ( PLUS | DASH | APPEND ) binary_expression_4 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_binary_expression_4_in_binary_expression_39531)
                binary_expression_4476 = self.binary_expression_4()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, binary_expression_4476.tree)
                # sdl92.g:813:37: ( ( PLUS | DASH | APPEND ) binary_expression_4 )*
                while True: #loop155
                    alt155 = 2
                    LA155 = self.input.LA(1)
                    if LA155 == PLUS:
                        LA155_2 = self.input.LA(2)

                        if (self.synpred202_sdl92()) :
                            alt155 = 1


                    elif LA155 == DASH:
                        LA155_3 = self.input.LA(2)

                        if (self.synpred202_sdl92()) :
                            alt155 = 1


                    elif LA155 == APPEND:
                        LA155_4 = self.input.LA(2)

                        if (self.synpred202_sdl92()) :
                            alt155 = 1



                    if alt155 == 1:
                        # sdl92.g:813:38: ( PLUS | DASH | APPEND ) binary_expression_4
                        pass 
                        # sdl92.g:813:38: ( PLUS | DASH | APPEND )
                        alt154 = 3
                        LA154 = self.input.LA(1)
                        if LA154 == PLUS:
                            alt154 = 1
                        elif LA154 == DASH:
                            alt154 = 2
                        elif LA154 == APPEND:
                            alt154 = 3
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 154, 0, self.input)

                            raise nvae

                        if alt154 == 1:
                            # sdl92.g:813:40: PLUS
                            pass 
                            PLUS477=self.match(self.input, PLUS, self.FOLLOW_PLUS_in_binary_expression_39536)
                            if self._state.backtracking == 0:

                                PLUS477_tree = self._adaptor.createWithPayload(PLUS477)
                                root_0 = self._adaptor.becomeRoot(PLUS477_tree, root_0)



                        elif alt154 == 2:
                            # sdl92.g:813:48: DASH
                            pass 
                            DASH478=self.match(self.input, DASH, self.FOLLOW_DASH_in_binary_expression_39541)
                            if self._state.backtracking == 0:

                                DASH478_tree = self._adaptor.createWithPayload(DASH478)
                                root_0 = self._adaptor.becomeRoot(DASH478_tree, root_0)



                        elif alt154 == 3:
                            # sdl92.g:813:56: APPEND
                            pass 
                            APPEND479=self.match(self.input, APPEND, self.FOLLOW_APPEND_in_binary_expression_39546)
                            if self._state.backtracking == 0:

                                APPEND479_tree = self._adaptor.createWithPayload(APPEND479)
                                root_0 = self._adaptor.becomeRoot(APPEND479_tree, root_0)




                        self._state.following.append(self.FOLLOW_binary_expression_4_in_binary_expression_39551)
                        binary_expression_4480 = self.binary_expression_4()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, binary_expression_4480.tree)


                    else:
                        break #loop155



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "binary_expression_3"

    class binary_expression_4_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.binary_expression_4_return, self).__init__()

            self.tree = None




    # $ANTLR start "binary_expression_4"
    # sdl92.g:814:1: binary_expression_4 : unary_expression ( ( ASTERISK | DIV | MOD | REM ) unary_expression )* ;
    def binary_expression_4(self, ):

        retval = self.binary_expression_4_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ASTERISK482 = None
        DIV483 = None
        MOD484 = None
        REM485 = None
        unary_expression481 = None

        unary_expression486 = None


        ASTERISK482_tree = None
        DIV483_tree = None
        MOD484_tree = None
        REM485_tree = None

        try:
            try:
                # sdl92.g:815:9: ( unary_expression ( ( ASTERISK | DIV | MOD | REM ) unary_expression )* )
                # sdl92.g:815:17: unary_expression ( ( ASTERISK | DIV | MOD | REM ) unary_expression )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_unary_expression_in_binary_expression_49574)
                unary_expression481 = self.unary_expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, unary_expression481.tree)
                # sdl92.g:815:34: ( ( ASTERISK | DIV | MOD | REM ) unary_expression )*
                while True: #loop157
                    alt157 = 2
                    LA157 = self.input.LA(1)
                    if LA157 == ASTERISK:
                        LA157_2 = self.input.LA(2)

                        if (self.synpred206_sdl92()) :
                            alt157 = 1


                    elif LA157 == DIV:
                        LA157_3 = self.input.LA(2)

                        if (self.synpred206_sdl92()) :
                            alt157 = 1


                    elif LA157 == MOD:
                        LA157_4 = self.input.LA(2)

                        if (self.synpred206_sdl92()) :
                            alt157 = 1


                    elif LA157 == REM:
                        LA157_5 = self.input.LA(2)

                        if (self.synpred206_sdl92()) :
                            alt157 = 1



                    if alt157 == 1:
                        # sdl92.g:815:35: ( ASTERISK | DIV | MOD | REM ) unary_expression
                        pass 
                        # sdl92.g:815:35: ( ASTERISK | DIV | MOD | REM )
                        alt156 = 4
                        LA156 = self.input.LA(1)
                        if LA156 == ASTERISK:
                            alt156 = 1
                        elif LA156 == DIV:
                            alt156 = 2
                        elif LA156 == MOD:
                            alt156 = 3
                        elif LA156 == REM:
                            alt156 = 4
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 156, 0, self.input)

                            raise nvae

                        if alt156 == 1:
                            # sdl92.g:815:37: ASTERISK
                            pass 
                            ASTERISK482=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_binary_expression_49579)
                            if self._state.backtracking == 0:

                                ASTERISK482_tree = self._adaptor.createWithPayload(ASTERISK482)
                                root_0 = self._adaptor.becomeRoot(ASTERISK482_tree, root_0)



                        elif alt156 == 2:
                            # sdl92.g:815:49: DIV
                            pass 
                            DIV483=self.match(self.input, DIV, self.FOLLOW_DIV_in_binary_expression_49584)
                            if self._state.backtracking == 0:

                                DIV483_tree = self._adaptor.createWithPayload(DIV483)
                                root_0 = self._adaptor.becomeRoot(DIV483_tree, root_0)



                        elif alt156 == 3:
                            # sdl92.g:815:56: MOD
                            pass 
                            MOD484=self.match(self.input, MOD, self.FOLLOW_MOD_in_binary_expression_49589)
                            if self._state.backtracking == 0:

                                MOD484_tree = self._adaptor.createWithPayload(MOD484)
                                root_0 = self._adaptor.becomeRoot(MOD484_tree, root_0)



                        elif alt156 == 4:
                            # sdl92.g:815:63: REM
                            pass 
                            REM485=self.match(self.input, REM, self.FOLLOW_REM_in_binary_expression_49594)
                            if self._state.backtracking == 0:

                                REM485_tree = self._adaptor.createWithPayload(REM485)
                                root_0 = self._adaptor.becomeRoot(REM485_tree, root_0)




                        self._state.following.append(self.FOLLOW_unary_expression_in_binary_expression_49599)
                        unary_expression486 = self.unary_expression()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, unary_expression486.tree)


                    else:
                        break #loop157



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "binary_expression_4"

    class unary_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.unary_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "unary_expression"
    # sdl92.g:817:1: unary_expression : ( primary_expression | NOT unary_expression | DASH unary_expression -> ^( NEG unary_expression ) );
    def unary_expression(self, ):

        retval = self.unary_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        NOT488 = None
        DASH490 = None
        primary_expression487 = None

        unary_expression489 = None

        unary_expression491 = None


        NOT488_tree = None
        DASH490_tree = None
        stream_DASH = RewriteRuleTokenStream(self._adaptor, "token DASH")
        stream_unary_expression = RewriteRuleSubtreeStream(self._adaptor, "rule unary_expression")
        try:
            try:
                # sdl92.g:818:9: ( primary_expression | NOT unary_expression | DASH unary_expression -> ^( NEG unary_expression ) )
                alt158 = 3
                LA158 = self.input.LA(1)
                if LA158 == BITSTR or LA158 == FLOAT or LA158 == IF or LA158 == OCTSTR or LA158 == STRING or LA158 == INT or LA158 == L_PAREN or LA158 == ID or LA158 == TRUE or LA158 == FALSE or LA158 == NULL or LA158 == PLUS_INFINITY or LA158 == MINUS_INFINITY or LA158 == L_BRACKET:
                    alt158 = 1
                elif LA158 == NOT:
                    alt158 = 2
                elif LA158 == DASH:
                    alt158 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 158, 0, self.input)

                    raise nvae

                if alt158 == 1:
                    # sdl92.g:818:17: primary_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_primary_expression_in_unary_expression9623)
                    primary_expression487 = self.primary_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, primary_expression487.tree)


                elif alt158 == 2:
                    # sdl92.g:819:17: NOT unary_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    NOT488=self.match(self.input, NOT, self.FOLLOW_NOT_in_unary_expression9641)
                    if self._state.backtracking == 0:

                        NOT488_tree = self._adaptor.createWithPayload(NOT488)
                        root_0 = self._adaptor.becomeRoot(NOT488_tree, root_0)

                    self._state.following.append(self.FOLLOW_unary_expression_in_unary_expression9644)
                    unary_expression489 = self.unary_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, unary_expression489.tree)


                elif alt158 == 3:
                    # sdl92.g:820:17: DASH unary_expression
                    pass 
                    DASH490=self.match(self.input, DASH, self.FOLLOW_DASH_in_unary_expression9662) 
                    if self._state.backtracking == 0:
                        stream_DASH.add(DASH490)
                    self._state.following.append(self.FOLLOW_unary_expression_in_unary_expression9664)
                    unary_expression491 = self.unary_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_unary_expression.add(unary_expression491.tree)

                    # AST Rewrite
                    # elements: unary_expression
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 820:39: -> ^( NEG unary_expression )
                        # sdl92.g:820:42: ^( NEG unary_expression )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(NEG, "NEG"), root_1)

                        self._adaptor.addChild(root_1, stream_unary_expression.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "unary_expression"

    class primary_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.primary_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "primary_expression"
    # sdl92.g:822:1: primary_expression : ( primary -> ^( PRIMARY primary ) | '(' expression ')' -> ^( PAREN expression ) | conditional_ground_expression );
    def primary_expression(self, ):

        retval = self.primary_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal493 = None
        char_literal495 = None
        primary492 = None

        expression494 = None

        conditional_ground_expression496 = None


        char_literal493_tree = None
        char_literal495_tree = None
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_primary = RewriteRuleSubtreeStream(self._adaptor, "rule primary")
        try:
            try:
                # sdl92.g:823:9: ( primary -> ^( PRIMARY primary ) | '(' expression ')' -> ^( PAREN expression ) | conditional_ground_expression )
                alt159 = 3
                LA159 = self.input.LA(1)
                if LA159 == BITSTR or LA159 == FLOAT or LA159 == OCTSTR or LA159 == STRING or LA159 == INT or LA159 == ID or LA159 == TRUE or LA159 == FALSE or LA159 == NULL or LA159 == PLUS_INFINITY or LA159 == MINUS_INFINITY or LA159 == L_BRACKET:
                    alt159 = 1
                elif LA159 == L_PAREN:
                    alt159 = 2
                elif LA159 == IF:
                    alt159 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 159, 0, self.input)

                    raise nvae

                if alt159 == 1:
                    # sdl92.g:823:17: primary
                    pass 
                    self._state.following.append(self.FOLLOW_primary_in_primary_expression9694)
                    primary492 = self.primary()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_primary.add(primary492.tree)

                    # AST Rewrite
                    # elements: primary
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 823:47: -> ^( PRIMARY primary )
                        # sdl92.g:823:50: ^( PRIMARY primary )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PRIMARY, "PRIMARY"), root_1)

                        self._adaptor.addChild(root_1, stream_primary.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt159 == 2:
                    # sdl92.g:824:17: '(' expression ')'
                    pass 
                    char_literal493=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_primary_expression9742) 
                    if self._state.backtracking == 0:
                        stream_L_PAREN.add(char_literal493)
                    self._state.following.append(self.FOLLOW_expression_in_primary_expression9744)
                    expression494 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression494.tree)
                    char_literal495=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_primary_expression9746) 
                    if self._state.backtracking == 0:
                        stream_R_PAREN.add(char_literal495)

                    # AST Rewrite
                    # elements: expression
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 824:47: -> ^( PAREN expression )
                        # sdl92.g:824:50: ^( PAREN expression )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PAREN, "PAREN"), root_1)

                        self._adaptor.addChild(root_1, stream_expression.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt159 == 3:
                    # sdl92.g:825:17: conditional_ground_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_conditional_ground_expression_in_primary_expression9783)
                    conditional_ground_expression496 = self.conditional_ground_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, conditional_ground_expression496.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "primary_expression"

    class primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "primary"
    # sdl92.g:828:1: primary : ( BITSTR | OCTSTR | TRUE | FALSE | STRING | NULL | PLUS_INFINITY | MINUS_INFINITY | INT | FLOAT | ID ':' expression -> ^( CHOICE ID expression ) | ID ( primary_params )+ -> ^( PATH ID ( primary_params )+ ) | ID -> ^( VARIABLE ID ) | '{' '}' -> ^( EMPTYSTR ) | '{' MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT '}' -> ^( FLOAT2 $mant $bas $exp) | '{' named_value ( COMMA named_value )* '}' -> ^( SEQUENCE ( named_value )+ ) | '{' primary ( COMMA primary )* '}' -> ^( SEQOF ( primary )+ ) );
    def primary(self, ):

        retval = self.primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        mant = None
        bas = None
        exp = None
        BITSTR497 = None
        OCTSTR498 = None
        TRUE499 = None
        FALSE500 = None
        STRING501 = None
        NULL502 = None
        PLUS_INFINITY503 = None
        MINUS_INFINITY504 = None
        INT505 = None
        FLOAT506 = None
        ID507 = None
        char_literal508 = None
        ID510 = None
        ID512 = None
        char_literal513 = None
        char_literal514 = None
        char_literal515 = None
        MANTISSA516 = None
        COMMA517 = None
        BASE518 = None
        COMMA519 = None
        EXPONENT520 = None
        char_literal521 = None
        char_literal522 = None
        COMMA524 = None
        char_literal526 = None
        char_literal527 = None
        COMMA529 = None
        char_literal531 = None
        expression509 = None

        primary_params511 = None

        named_value523 = None

        named_value525 = None

        primary528 = None

        primary530 = None


        mant_tree = None
        bas_tree = None
        exp_tree = None
        BITSTR497_tree = None
        OCTSTR498_tree = None
        TRUE499_tree = None
        FALSE500_tree = None
        STRING501_tree = None
        NULL502_tree = None
        PLUS_INFINITY503_tree = None
        MINUS_INFINITY504_tree = None
        INT505_tree = None
        FLOAT506_tree = None
        ID507_tree = None
        char_literal508_tree = None
        ID510_tree = None
        ID512_tree = None
        char_literal513_tree = None
        char_literal514_tree = None
        char_literal515_tree = None
        MANTISSA516_tree = None
        COMMA517_tree = None
        BASE518_tree = None
        COMMA519_tree = None
        EXPONENT520_tree = None
        char_literal521_tree = None
        char_literal522_tree = None
        COMMA524_tree = None
        char_literal526_tree = None
        char_literal527_tree = None
        COMMA529_tree = None
        char_literal531_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_BASE = RewriteRuleTokenStream(self._adaptor, "token BASE")
        stream_MANTISSA = RewriteRuleTokenStream(self._adaptor, "token MANTISSA")
        stream_EXPONENT = RewriteRuleTokenStream(self._adaptor, "token EXPONENT")
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_L_BRACKET = RewriteRuleTokenStream(self._adaptor, "token L_BRACKET")
        stream_ID = RewriteRuleTokenStream(self._adaptor, "token ID")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_BRACKET = RewriteRuleTokenStream(self._adaptor, "token R_BRACKET")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_primary = RewriteRuleSubtreeStream(self._adaptor, "rule primary")
        stream_primary_params = RewriteRuleSubtreeStream(self._adaptor, "rule primary_params")
        stream_named_value = RewriteRuleSubtreeStream(self._adaptor, "rule named_value")
        try:
            try:
                # sdl92.g:829:9: ( BITSTR | OCTSTR | TRUE | FALSE | STRING | NULL | PLUS_INFINITY | MINUS_INFINITY | INT | FLOAT | ID ':' expression -> ^( CHOICE ID expression ) | ID ( primary_params )+ -> ^( PATH ID ( primary_params )+ ) | ID -> ^( VARIABLE ID ) | '{' '}' -> ^( EMPTYSTR ) | '{' MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT '}' -> ^( FLOAT2 $mant $bas $exp) | '{' named_value ( COMMA named_value )* '}' -> ^( SEQUENCE ( named_value )+ ) | '{' primary ( COMMA primary )* '}' -> ^( SEQOF ( primary )+ ) )
                alt163 = 17
                alt163 = self.dfa163.predict(self.input)
                if alt163 == 1:
                    # sdl92.g:829:17: BITSTR
                    pass 
                    root_0 = self._adaptor.nil()

                    BITSTR497=self.match(self.input, BITSTR, self.FOLLOW_BITSTR_in_primary9814)
                    if self._state.backtracking == 0:

                        BITSTR497_tree = self._adaptor.createWithPayload(BITSTR497)
                        root_0 = self._adaptor.becomeRoot(BITSTR497_tree, root_0)



                elif alt163 == 2:
                    # sdl92.g:830:17: OCTSTR
                    pass 
                    root_0 = self._adaptor.nil()

                    OCTSTR498=self.match(self.input, OCTSTR, self.FOLLOW_OCTSTR_in_primary9833)
                    if self._state.backtracking == 0:

                        OCTSTR498_tree = self._adaptor.createWithPayload(OCTSTR498)
                        root_0 = self._adaptor.becomeRoot(OCTSTR498_tree, root_0)



                elif alt163 == 3:
                    # sdl92.g:831:17: TRUE
                    pass 
                    root_0 = self._adaptor.nil()

                    TRUE499=self.match(self.input, TRUE, self.FOLLOW_TRUE_in_primary9852)
                    if self._state.backtracking == 0:

                        TRUE499_tree = self._adaptor.createWithPayload(TRUE499)
                        root_0 = self._adaptor.becomeRoot(TRUE499_tree, root_0)



                elif alt163 == 4:
                    # sdl92.g:832:17: FALSE
                    pass 
                    root_0 = self._adaptor.nil()

                    FALSE500=self.match(self.input, FALSE, self.FOLLOW_FALSE_in_primary9871)
                    if self._state.backtracking == 0:

                        FALSE500_tree = self._adaptor.createWithPayload(FALSE500)
                        root_0 = self._adaptor.becomeRoot(FALSE500_tree, root_0)



                elif alt163 == 5:
                    # sdl92.g:833:17: STRING
                    pass 
                    root_0 = self._adaptor.nil()

                    STRING501=self.match(self.input, STRING, self.FOLLOW_STRING_in_primary9890)
                    if self._state.backtracking == 0:

                        STRING501_tree = self._adaptor.createWithPayload(STRING501)
                        self._adaptor.addChild(root_0, STRING501_tree)



                elif alt163 == 6:
                    # sdl92.g:834:17: NULL
                    pass 
                    root_0 = self._adaptor.nil()

                    NULL502=self.match(self.input, NULL, self.FOLLOW_NULL_in_primary9908)
                    if self._state.backtracking == 0:

                        NULL502_tree = self._adaptor.createWithPayload(NULL502)
                        root_0 = self._adaptor.becomeRoot(NULL502_tree, root_0)



                elif alt163 == 7:
                    # sdl92.g:835:17: PLUS_INFINITY
                    pass 
                    root_0 = self._adaptor.nil()

                    PLUS_INFINITY503=self.match(self.input, PLUS_INFINITY, self.FOLLOW_PLUS_INFINITY_in_primary9927)
                    if self._state.backtracking == 0:

                        PLUS_INFINITY503_tree = self._adaptor.createWithPayload(PLUS_INFINITY503)
                        root_0 = self._adaptor.becomeRoot(PLUS_INFINITY503_tree, root_0)



                elif alt163 == 8:
                    # sdl92.g:836:17: MINUS_INFINITY
                    pass 
                    root_0 = self._adaptor.nil()

                    MINUS_INFINITY504=self.match(self.input, MINUS_INFINITY, self.FOLLOW_MINUS_INFINITY_in_primary9946)
                    if self._state.backtracking == 0:

                        MINUS_INFINITY504_tree = self._adaptor.createWithPayload(MINUS_INFINITY504)
                        root_0 = self._adaptor.becomeRoot(MINUS_INFINITY504_tree, root_0)



                elif alt163 == 9:
                    # sdl92.g:837:17: INT
                    pass 
                    root_0 = self._adaptor.nil()

                    INT505=self.match(self.input, INT, self.FOLLOW_INT_in_primary9965)
                    if self._state.backtracking == 0:

                        INT505_tree = self._adaptor.createWithPayload(INT505)
                        root_0 = self._adaptor.becomeRoot(INT505_tree, root_0)



                elif alt163 == 10:
                    # sdl92.g:838:17: FLOAT
                    pass 
                    root_0 = self._adaptor.nil()

                    FLOAT506=self.match(self.input, FLOAT, self.FOLLOW_FLOAT_in_primary9984)
                    if self._state.backtracking == 0:

                        FLOAT506_tree = self._adaptor.createWithPayload(FLOAT506)
                        root_0 = self._adaptor.becomeRoot(FLOAT506_tree, root_0)



                elif alt163 == 11:
                    # sdl92.g:839:17: ID ':' expression
                    pass 
                    ID507=self.match(self.input, ID, self.FOLLOW_ID_in_primary10003) 
                    if self._state.backtracking == 0:
                        stream_ID.add(ID507)
                    char_literal508=self.match(self.input, 212, self.FOLLOW_212_in_primary10005) 
                    if self._state.backtracking == 0:
                        stream_212.add(char_literal508)
                    self._state.following.append(self.FOLLOW_expression_in_primary10007)
                    expression509 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression509.tree)

                    # AST Rewrite
                    # elements: ID, expression
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 839:45: -> ^( CHOICE ID expression )
                        # sdl92.g:839:48: ^( CHOICE ID expression )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CHOICE, "CHOICE"), root_1)

                        self._adaptor.addChild(root_1, stream_ID.nextNode())
                        self._adaptor.addChild(root_1, stream_expression.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt163 == 12:
                    # sdl92.g:840:17: ID ( primary_params )+
                    pass 
                    ID510=self.match(self.input, ID, self.FOLLOW_ID_in_primary10045) 
                    if self._state.backtracking == 0:
                        stream_ID.add(ID510)
                    # sdl92.g:840:20: ( primary_params )+
                    cnt160 = 0
                    while True: #loop160
                        alt160 = 2
                        alt160 = self.dfa160.predict(self.input)
                        if alt160 == 1:
                            # sdl92.g:0:0: primary_params
                            pass 
                            self._state.following.append(self.FOLLOW_primary_params_in_primary10047)
                            primary_params511 = self.primary_params()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_primary_params.add(primary_params511.tree)


                        else:
                            if cnt160 >= 1:
                                break #loop160

                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            eee = EarlyExitException(160, self.input)
                            raise eee

                        cnt160 += 1

                    # AST Rewrite
                    # elements: ID, primary_params
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 840:45: -> ^( PATH ID ( primary_params )+ )
                        # sdl92.g:840:48: ^( PATH ID ( primary_params )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PATH, "PATH"), root_1)

                        self._adaptor.addChild(root_1, stream_ID.nextNode())
                        # sdl92.g:840:58: ( primary_params )+
                        if not (stream_primary_params.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_primary_params.hasNext():
                            self._adaptor.addChild(root_1, stream_primary_params.nextTree())


                        stream_primary_params.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt163 == 13:
                    # sdl92.g:841:17: ID
                    pass 
                    ID512=self.match(self.input, ID, self.FOLLOW_ID_in_primary10086) 
                    if self._state.backtracking == 0:
                        stream_ID.add(ID512)

                    # AST Rewrite
                    # elements: ID
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 841:45: -> ^( VARIABLE ID )
                        # sdl92.g:841:48: ^( VARIABLE ID )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VARIABLE, "VARIABLE"), root_1)

                        self._adaptor.addChild(root_1, stream_ID.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt163 == 14:
                    # sdl92.g:842:17: '{' '}'
                    pass 
                    char_literal513=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_primary10137) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(char_literal513)
                    char_literal514=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_primary10139) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(char_literal514)

                    # AST Rewrite
                    # elements: 
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 842:45: -> ^( EMPTYSTR )
                        # sdl92.g:842:48: ^( EMPTYSTR )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(EMPTYSTR, "EMPTYSTR"), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt163 == 15:
                    # sdl92.g:843:17: '{' MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT '}'
                    pass 
                    char_literal515=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_primary10183) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(char_literal515)
                    MANTISSA516=self.match(self.input, MANTISSA, self.FOLLOW_MANTISSA_in_primary10201) 
                    if self._state.backtracking == 0:
                        stream_MANTISSA.add(MANTISSA516)
                    mant=self.match(self.input, INT, self.FOLLOW_INT_in_primary10205) 
                    if self._state.backtracking == 0:
                        stream_INT.add(mant)
                    COMMA517=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_primary10207) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA517)
                    BASE518=self.match(self.input, BASE, self.FOLLOW_BASE_in_primary10225) 
                    if self._state.backtracking == 0:
                        stream_BASE.add(BASE518)
                    bas=self.match(self.input, INT, self.FOLLOW_INT_in_primary10229) 
                    if self._state.backtracking == 0:
                        stream_INT.add(bas)
                    COMMA519=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_primary10231) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA519)
                    EXPONENT520=self.match(self.input, EXPONENT, self.FOLLOW_EXPONENT_in_primary10249) 
                    if self._state.backtracking == 0:
                        stream_EXPONENT.add(EXPONENT520)
                    exp=self.match(self.input, INT, self.FOLLOW_INT_in_primary10253) 
                    if self._state.backtracking == 0:
                        stream_INT.add(exp)
                    char_literal521=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_primary10271) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(char_literal521)

                    # AST Rewrite
                    # elements: exp, bas, mant
                    # token labels: exp, mant, bas
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0
                        stream_exp = RewriteRuleTokenStream(self._adaptor, "token exp", exp)
                        stream_mant = RewriteRuleTokenStream(self._adaptor, "token mant", mant)
                        stream_bas = RewriteRuleTokenStream(self._adaptor, "token bas", bas)

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 847:45: -> ^( FLOAT2 $mant $bas $exp)
                        # sdl92.g:847:48: ^( FLOAT2 $mant $bas $exp)
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FLOAT2, "FLOAT2"), root_1)

                        self._adaptor.addChild(root_1, stream_mant.nextNode())
                        self._adaptor.addChild(root_1, stream_bas.nextNode())
                        self._adaptor.addChild(root_1, stream_exp.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt163 == 16:
                    # sdl92.g:848:17: '{' named_value ( COMMA named_value )* '}'
                    pass 
                    char_literal522=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_primary10328) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(char_literal522)
                    self._state.following.append(self.FOLLOW_named_value_in_primary10346)
                    named_value523 = self.named_value()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_named_value.add(named_value523.tree)
                    # sdl92.g:849:29: ( COMMA named_value )*
                    while True: #loop161
                        alt161 = 2
                        LA161_0 = self.input.LA(1)

                        if (LA161_0 == COMMA) :
                            alt161 = 1


                        if alt161 == 1:
                            # sdl92.g:849:30: COMMA named_value
                            pass 
                            COMMA524=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_primary10349) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(COMMA524)
                            self._state.following.append(self.FOLLOW_named_value_in_primary10351)
                            named_value525 = self.named_value()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_named_value.add(named_value525.tree)


                        else:
                            break #loop161
                    char_literal526=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_primary10371) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(char_literal526)

                    # AST Rewrite
                    # elements: named_value
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 850:45: -> ^( SEQUENCE ( named_value )+ )
                        # sdl92.g:850:48: ^( SEQUENCE ( named_value )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SEQUENCE, "SEQUENCE"), root_1)

                        # sdl92.g:850:59: ( named_value )+
                        if not (stream_named_value.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_named_value.hasNext():
                            self._adaptor.addChild(root_1, stream_named_value.nextTree())


                        stream_named_value.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt163 == 17:
                    # sdl92.g:851:17: '{' primary ( COMMA primary )* '}'
                    pass 
                    char_literal527=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_primary10422) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(char_literal527)
                    self._state.following.append(self.FOLLOW_primary_in_primary10440)
                    primary528 = self.primary()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_primary.add(primary528.tree)
                    # sdl92.g:852:25: ( COMMA primary )*
                    while True: #loop162
                        alt162 = 2
                        LA162_0 = self.input.LA(1)

                        if (LA162_0 == COMMA) :
                            alt162 = 1


                        if alt162 == 1:
                            # sdl92.g:852:26: COMMA primary
                            pass 
                            COMMA529=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_primary10443) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(COMMA529)
                            self._state.following.append(self.FOLLOW_primary_in_primary10445)
                            primary530 = self.primary()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_primary.add(primary530.tree)


                        else:
                            break #loop162
                    char_literal531=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_primary10465) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(char_literal531)

                    # AST Rewrite
                    # elements: primary
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 853:45: -> ^( SEQOF ( primary )+ )
                        # sdl92.g:853:48: ^( SEQOF ( primary )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SEQOF, "SEQOF"), root_1)

                        # sdl92.g:853:56: ( primary )+
                        if not (stream_primary.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_primary.hasNext():
                            self._adaptor.addChild(root_1, stream_primary.nextTree())


                        stream_primary.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "primary"

    class informal_text_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.informal_text_return, self).__init__()

            self.tree = None




    # $ANTLR start "informal_text"
    # sdl92.g:856:1: informal_text : STRING -> ^( INFORMAL_TEXT STRING ) ;
    def informal_text(self, ):

        retval = self.informal_text_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STRING532 = None

        STRING532_tree = None
        stream_STRING = RewriteRuleTokenStream(self._adaptor, "token STRING")

        try:
            try:
                # sdl92.g:857:9: ( STRING -> ^( INFORMAL_TEXT STRING ) )
                # sdl92.g:857:18: STRING
                pass 
                STRING532=self.match(self.input, STRING, self.FOLLOW_STRING_in_informal_text10530) 
                if self._state.backtracking == 0:
                    stream_STRING.add(STRING532)

                # AST Rewrite
                # elements: STRING
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 858:9: -> ^( INFORMAL_TEXT STRING )
                    # sdl92.g:858:18: ^( INFORMAL_TEXT STRING )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(INFORMAL_TEXT, "INFORMAL_TEXT"), root_1)

                    self._adaptor.addChild(root_1, stream_STRING.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "informal_text"

    class named_value_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.named_value_return, self).__init__()

            self.tree = None




    # $ANTLR start "named_value"
    # sdl92.g:862:1: named_value : ID expression ;
    def named_value(self, ):

        retval = self.named_value_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID533 = None
        expression534 = None


        ID533_tree = None

        try:
            try:
                # sdl92.g:863:9: ( ID expression )
                # sdl92.g:863:17: ID expression
                pass 
                root_0 = self._adaptor.nil()

                ID533=self.match(self.input, ID, self.FOLLOW_ID_in_named_value10576)
                if self._state.backtracking == 0:

                    ID533_tree = self._adaptor.createWithPayload(ID533)
                    self._adaptor.addChild(root_0, ID533_tree)

                self._state.following.append(self.FOLLOW_expression_in_named_value10578)
                expression534 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression534.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "named_value"

    class primary_params_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.primary_params_return, self).__init__()

            self.tree = None




    # $ANTLR start "primary_params"
    # sdl92.g:866:1: primary_params : ( '(' expression_list ')' -> ^( PARAMS expression_list ) | '!' literal_id -> ^( FIELD_NAME literal_id ) );
    def primary_params(self, ):

        retval = self.primary_params_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal535 = None
        char_literal537 = None
        char_literal538 = None
        expression_list536 = None

        literal_id539 = None


        char_literal535_tree = None
        char_literal537_tree = None
        char_literal538_tree = None
        stream_213 = RewriteRuleTokenStream(self._adaptor, "token 213")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression_list = RewriteRuleSubtreeStream(self._adaptor, "rule expression_list")
        stream_literal_id = RewriteRuleSubtreeStream(self._adaptor, "rule literal_id")
        try:
            try:
                # sdl92.g:867:9: ( '(' expression_list ')' -> ^( PARAMS expression_list ) | '!' literal_id -> ^( FIELD_NAME literal_id ) )
                alt164 = 2
                LA164_0 = self.input.LA(1)

                if (LA164_0 == L_PAREN) :
                    alt164 = 1
                elif (LA164_0 == 213) :
                    alt164 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 164, 0, self.input)

                    raise nvae

                if alt164 == 1:
                    # sdl92.g:867:16: '(' expression_list ')'
                    pass 
                    char_literal535=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_primary_params10600) 
                    if self._state.backtracking == 0:
                        stream_L_PAREN.add(char_literal535)
                    self._state.following.append(self.FOLLOW_expression_list_in_primary_params10602)
                    expression_list536 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression_list.add(expression_list536.tree)
                    char_literal537=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_primary_params10604) 
                    if self._state.backtracking == 0:
                        stream_R_PAREN.add(char_literal537)

                    # AST Rewrite
                    # elements: expression_list
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 868:9: -> ^( PARAMS expression_list )
                        # sdl92.g:868:16: ^( PARAMS expression_list )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAMS, "PARAMS"), root_1)

                        self._adaptor.addChild(root_1, stream_expression_list.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt164 == 2:
                    # sdl92.g:869:18: '!' literal_id
                    pass 
                    char_literal538=self.match(self.input, 213, self.FOLLOW_213_in_primary_params10643) 
                    if self._state.backtracking == 0:
                        stream_213.add(char_literal538)
                    self._state.following.append(self.FOLLOW_literal_id_in_primary_params10645)
                    literal_id539 = self.literal_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_literal_id.add(literal_id539.tree)

                    # AST Rewrite
                    # elements: literal_id
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 870:9: -> ^( FIELD_NAME literal_id )
                        # sdl92.g:870:16: ^( FIELD_NAME literal_id )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FIELD_NAME, "FIELD_NAME"), root_1)

                        self._adaptor.addChild(root_1, stream_literal_id.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "primary_params"

    class indexed_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.indexed_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "indexed_primary"
    # sdl92.g:883:1: indexed_primary : primary '(' expression_list ')' ;
    def indexed_primary(self, ):

        retval = self.indexed_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal541 = None
        char_literal543 = None
        primary540 = None

        expression_list542 = None


        char_literal541_tree = None
        char_literal543_tree = None

        try:
            try:
                # sdl92.g:884:9: ( primary '(' expression_list ')' )
                # sdl92.g:884:17: primary '(' expression_list ')'
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_primary_in_indexed_primary10692)
                primary540 = self.primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, primary540.tree)
                char_literal541=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_indexed_primary10694)
                if self._state.backtracking == 0:

                    char_literal541_tree = self._adaptor.createWithPayload(char_literal541)
                    self._adaptor.addChild(root_0, char_literal541_tree)

                self._state.following.append(self.FOLLOW_expression_list_in_indexed_primary10696)
                expression_list542 = self.expression_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression_list542.tree)
                char_literal543=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_indexed_primary10698)
                if self._state.backtracking == 0:

                    char_literal543_tree = self._adaptor.createWithPayload(char_literal543)
                    self._adaptor.addChild(root_0, char_literal543_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "indexed_primary"

    class field_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_primary"
    # sdl92.g:887:1: field_primary : primary field_selection ;
    def field_primary(self, ):

        retval = self.field_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        primary544 = None

        field_selection545 = None



        try:
            try:
                # sdl92.g:888:9: ( primary field_selection )
                # sdl92.g:888:17: primary field_selection
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_primary_in_field_primary10721)
                primary544 = self.primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, primary544.tree)
                self._state.following.append(self.FOLLOW_field_selection_in_field_primary10723)
                field_selection545 = self.field_selection()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, field_selection545.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_primary"

    class structure_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.structure_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "structure_primary"
    # sdl92.g:891:1: structure_primary : '(.' expression_list '.)' ;
    def structure_primary(self, ):

        retval = self.structure_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal546 = None
        string_literal548 = None
        expression_list547 = None


        string_literal546_tree = None
        string_literal548_tree = None

        try:
            try:
                # sdl92.g:892:9: ( '(.' expression_list '.)' )
                # sdl92.g:892:17: '(.' expression_list '.)'
                pass 
                root_0 = self._adaptor.nil()

                string_literal546=self.match(self.input, 214, self.FOLLOW_214_in_structure_primary10746)
                if self._state.backtracking == 0:

                    string_literal546_tree = self._adaptor.createWithPayload(string_literal546)
                    self._adaptor.addChild(root_0, string_literal546_tree)

                self._state.following.append(self.FOLLOW_expression_list_in_structure_primary10748)
                expression_list547 = self.expression_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression_list547.tree)
                string_literal548=self.match(self.input, 215, self.FOLLOW_215_in_structure_primary10750)
                if self._state.backtracking == 0:

                    string_literal548_tree = self._adaptor.createWithPayload(string_literal548)
                    self._adaptor.addChild(root_0, string_literal548_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "structure_primary"

    class active_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.active_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "active_expression"
    # sdl92.g:897:1: active_expression : active_primary ;
    def active_expression(self, ):

        retval = self.active_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        active_primary549 = None



        try:
            try:
                # sdl92.g:898:9: ( active_primary )
                # sdl92.g:898:17: active_primary
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_active_primary_in_active_expression10775)
                active_primary549 = self.active_primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, active_primary549.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "active_expression"

    class active_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.active_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "active_primary"
    # sdl92.g:901:1: active_primary : ( variable_access | operator_application | conditional_expression | imperative_operator | '(' active_expression ')' | 'ERROR' );
    def active_primary(self, ):

        retval = self.active_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal554 = None
        char_literal556 = None
        string_literal557 = None
        variable_access550 = None

        operator_application551 = None

        conditional_expression552 = None

        imperative_operator553 = None

        active_expression555 = None


        char_literal554_tree = None
        char_literal556_tree = None
        string_literal557_tree = None

        try:
            try:
                # sdl92.g:902:9: ( variable_access | operator_application | conditional_expression | imperative_operator | '(' active_expression ')' | 'ERROR' )
                alt165 = 6
                LA165 = self.input.LA(1)
                if LA165 == ID:
                    LA165_1 = self.input.LA(2)

                    if (LA165_1 == L_PAREN) :
                        alt165 = 2
                    elif ((R_PAREN <= LA165_1 <= COMMA)) :
                        alt165 = 1
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 165, 1, self.input)

                        raise nvae

                elif LA165 == IF:
                    alt165 = 3
                elif LA165 == ANY or LA165 == ACTIVE or LA165 == IMPORT or LA165 == VIEW or LA165 == N or LA165 == P or LA165 == S or LA165 == O:
                    alt165 = 4
                elif LA165 == L_PAREN:
                    alt165 = 5
                elif LA165 == 216:
                    alt165 = 6
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 165, 0, self.input)

                    raise nvae

                if alt165 == 1:
                    # sdl92.g:902:17: variable_access
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_variable_access_in_active_primary10798)
                    variable_access550 = self.variable_access()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, variable_access550.tree)


                elif alt165 == 2:
                    # sdl92.g:903:19: operator_application
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_operator_application_in_active_primary10818)
                    operator_application551 = self.operator_application()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, operator_application551.tree)


                elif alt165 == 3:
                    # sdl92.g:904:19: conditional_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_conditional_expression_in_active_primary10838)
                    conditional_expression552 = self.conditional_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, conditional_expression552.tree)


                elif alt165 == 4:
                    # sdl92.g:905:19: imperative_operator
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_imperative_operator_in_active_primary10858)
                    imperative_operator553 = self.imperative_operator()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, imperative_operator553.tree)


                elif alt165 == 5:
                    # sdl92.g:906:19: '(' active_expression ')'
                    pass 
                    root_0 = self._adaptor.nil()

                    char_literal554=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_active_primary10878)
                    if self._state.backtracking == 0:

                        char_literal554_tree = self._adaptor.createWithPayload(char_literal554)
                        self._adaptor.addChild(root_0, char_literal554_tree)

                    self._state.following.append(self.FOLLOW_active_expression_in_active_primary10880)
                    active_expression555 = self.active_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, active_expression555.tree)
                    char_literal556=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_active_primary10882)
                    if self._state.backtracking == 0:

                        char_literal556_tree = self._adaptor.createWithPayload(char_literal556)
                        self._adaptor.addChild(root_0, char_literal556_tree)



                elif alt165 == 6:
                    # sdl92.g:907:19: 'ERROR'
                    pass 
                    root_0 = self._adaptor.nil()

                    string_literal557=self.match(self.input, 216, self.FOLLOW_216_in_active_primary10902)
                    if self._state.backtracking == 0:

                        string_literal557_tree = self._adaptor.createWithPayload(string_literal557)
                        self._adaptor.addChild(root_0, string_literal557_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "active_primary"

    class imperative_operator_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.imperative_operator_return, self).__init__()

            self.tree = None




    # $ANTLR start "imperative_operator"
    # sdl92.g:911:1: imperative_operator : ( now_expression | import_expression | pid_expression | view_expression | timer_active_expression | anyvalue_expression );
    def imperative_operator(self, ):

        retval = self.imperative_operator_return()
        retval.start = self.input.LT(1)

        root_0 = None

        now_expression558 = None

        import_expression559 = None

        pid_expression560 = None

        view_expression561 = None

        timer_active_expression562 = None

        anyvalue_expression563 = None



        try:
            try:
                # sdl92.g:912:9: ( now_expression | import_expression | pid_expression | view_expression | timer_active_expression | anyvalue_expression )
                alt166 = 6
                LA166 = self.input.LA(1)
                if LA166 == N:
                    alt166 = 1
                elif LA166 == IMPORT:
                    alt166 = 2
                elif LA166 == P or LA166 == S or LA166 == O:
                    alt166 = 3
                elif LA166 == VIEW:
                    alt166 = 4
                elif LA166 == ACTIVE:
                    alt166 = 5
                elif LA166 == ANY:
                    alt166 = 6
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 166, 0, self.input)

                    raise nvae

                if alt166 == 1:
                    # sdl92.g:912:17: now_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_now_expression_in_imperative_operator10929)
                    now_expression558 = self.now_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, now_expression558.tree)


                elif alt166 == 2:
                    # sdl92.g:913:19: import_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_import_expression_in_imperative_operator10949)
                    import_expression559 = self.import_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, import_expression559.tree)


                elif alt166 == 3:
                    # sdl92.g:914:19: pid_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_pid_expression_in_imperative_operator10969)
                    pid_expression560 = self.pid_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, pid_expression560.tree)


                elif alt166 == 4:
                    # sdl92.g:915:19: view_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_view_expression_in_imperative_operator10989)
                    view_expression561 = self.view_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, view_expression561.tree)


                elif alt166 == 5:
                    # sdl92.g:916:19: timer_active_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_timer_active_expression_in_imperative_operator11009)
                    timer_active_expression562 = self.timer_active_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, timer_active_expression562.tree)


                elif alt166 == 6:
                    # sdl92.g:917:19: anyvalue_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_anyvalue_expression_in_imperative_operator11029)
                    anyvalue_expression563 = self.anyvalue_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, anyvalue_expression563.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "imperative_operator"

    class timer_active_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.timer_active_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "timer_active_expression"
    # sdl92.g:920:1: timer_active_expression : ACTIVE '(' timer_id ( '(' expression_list ')' )? ')' ;
    def timer_active_expression(self, ):

        retval = self.timer_active_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ACTIVE564 = None
        char_literal565 = None
        char_literal567 = None
        char_literal569 = None
        char_literal570 = None
        timer_id566 = None

        expression_list568 = None


        ACTIVE564_tree = None
        char_literal565_tree = None
        char_literal567_tree = None
        char_literal569_tree = None
        char_literal570_tree = None

        try:
            try:
                # sdl92.g:921:9: ( ACTIVE '(' timer_id ( '(' expression_list ')' )? ')' )
                # sdl92.g:921:17: ACTIVE '(' timer_id ( '(' expression_list ')' )? ')'
                pass 
                root_0 = self._adaptor.nil()

                ACTIVE564=self.match(self.input, ACTIVE, self.FOLLOW_ACTIVE_in_timer_active_expression11052)
                if self._state.backtracking == 0:

                    ACTIVE564_tree = self._adaptor.createWithPayload(ACTIVE564)
                    self._adaptor.addChild(root_0, ACTIVE564_tree)

                char_literal565=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_timer_active_expression11054)
                if self._state.backtracking == 0:

                    char_literal565_tree = self._adaptor.createWithPayload(char_literal565)
                    self._adaptor.addChild(root_0, char_literal565_tree)

                self._state.following.append(self.FOLLOW_timer_id_in_timer_active_expression11056)
                timer_id566 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, timer_id566.tree)
                # sdl92.g:921:37: ( '(' expression_list ')' )?
                alt167 = 2
                LA167_0 = self.input.LA(1)

                if (LA167_0 == L_PAREN) :
                    alt167 = 1
                if alt167 == 1:
                    # sdl92.g:921:38: '(' expression_list ')'
                    pass 
                    char_literal567=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_timer_active_expression11059)
                    if self._state.backtracking == 0:

                        char_literal567_tree = self._adaptor.createWithPayload(char_literal567)
                        self._adaptor.addChild(root_0, char_literal567_tree)

                    self._state.following.append(self.FOLLOW_expression_list_in_timer_active_expression11061)
                    expression_list568 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, expression_list568.tree)
                    char_literal569=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_timer_active_expression11063)
                    if self._state.backtracking == 0:

                        char_literal569_tree = self._adaptor.createWithPayload(char_literal569)
                        self._adaptor.addChild(root_0, char_literal569_tree)




                char_literal570=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_timer_active_expression11067)
                if self._state.backtracking == 0:

                    char_literal570_tree = self._adaptor.createWithPayload(char_literal570)
                    self._adaptor.addChild(root_0, char_literal570_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "timer_active_expression"

    class anyvalue_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.anyvalue_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "anyvalue_expression"
    # sdl92.g:924:1: anyvalue_expression : ANY '(' sort ')' ;
    def anyvalue_expression(self, ):

        retval = self.anyvalue_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ANY571 = None
        char_literal572 = None
        char_literal574 = None
        sort573 = None


        ANY571_tree = None
        char_literal572_tree = None
        char_literal574_tree = None

        try:
            try:
                # sdl92.g:925:9: ( ANY '(' sort ')' )
                # sdl92.g:925:17: ANY '(' sort ')'
                pass 
                root_0 = self._adaptor.nil()

                ANY571=self.match(self.input, ANY, self.FOLLOW_ANY_in_anyvalue_expression11090)
                if self._state.backtracking == 0:

                    ANY571_tree = self._adaptor.createWithPayload(ANY571)
                    self._adaptor.addChild(root_0, ANY571_tree)

                char_literal572=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_anyvalue_expression11092)
                if self._state.backtracking == 0:

                    char_literal572_tree = self._adaptor.createWithPayload(char_literal572)
                    self._adaptor.addChild(root_0, char_literal572_tree)

                self._state.following.append(self.FOLLOW_sort_in_anyvalue_expression11094)
                sort573 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, sort573.tree)
                char_literal574=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_anyvalue_expression11096)
                if self._state.backtracking == 0:

                    char_literal574_tree = self._adaptor.createWithPayload(char_literal574)
                    self._adaptor.addChild(root_0, char_literal574_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "anyvalue_expression"

    class sort_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.sort_return, self).__init__()

            self.tree = None




    # $ANTLR start "sort"
    # sdl92.g:928:1: sort : sort_id -> ^( SORT sort_id ) ;
    def sort(self, ):

        retval = self.sort_return()
        retval.start = self.input.LT(1)

        root_0 = None

        sort_id575 = None


        stream_sort_id = RewriteRuleSubtreeStream(self._adaptor, "rule sort_id")
        try:
            try:
                # sdl92.g:928:9: ( sort_id -> ^( SORT sort_id ) )
                # sdl92.g:928:17: sort_id
                pass 
                self._state.following.append(self.FOLLOW_sort_id_in_sort11114)
                sort_id575 = self.sort_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort_id.add(sort_id575.tree)

                # AST Rewrite
                # elements: sort_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 929:9: -> ^( SORT sort_id )
                    # sdl92.g:929:17: ^( SORT sort_id )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SORT, "SORT"), root_1)

                    self._adaptor.addChild(root_1, stream_sort_id.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "sort"

    class syntype_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.syntype_return, self).__init__()

            self.tree = None




    # $ANTLR start "syntype"
    # sdl92.g:932:1: syntype : syntype_id ;
    def syntype(self, ):

        retval = self.syntype_return()
        retval.start = self.input.LT(1)

        root_0 = None

        syntype_id576 = None



        try:
            try:
                # sdl92.g:932:9: ( syntype_id )
                # sdl92.g:932:17: syntype_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_syntype_id_in_syntype11150)
                syntype_id576 = self.syntype_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, syntype_id576.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "syntype"

    class import_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.import_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "import_expression"
    # sdl92.g:935:1: import_expression : IMPORT '(' remote_variable_id ( ',' destination )? ')' ;
    def import_expression(self, ):

        retval = self.import_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IMPORT577 = None
        char_literal578 = None
        char_literal580 = None
        char_literal582 = None
        remote_variable_id579 = None

        destination581 = None


        IMPORT577_tree = None
        char_literal578_tree = None
        char_literal580_tree = None
        char_literal582_tree = None

        try:
            try:
                # sdl92.g:936:9: ( IMPORT '(' remote_variable_id ( ',' destination )? ')' )
                # sdl92.g:936:17: IMPORT '(' remote_variable_id ( ',' destination )? ')'
                pass 
                root_0 = self._adaptor.nil()

                IMPORT577=self.match(self.input, IMPORT, self.FOLLOW_IMPORT_in_import_expression11173)
                if self._state.backtracking == 0:

                    IMPORT577_tree = self._adaptor.createWithPayload(IMPORT577)
                    self._adaptor.addChild(root_0, IMPORT577_tree)

                char_literal578=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_import_expression11175)
                if self._state.backtracking == 0:

                    char_literal578_tree = self._adaptor.createWithPayload(char_literal578)
                    self._adaptor.addChild(root_0, char_literal578_tree)

                self._state.following.append(self.FOLLOW_remote_variable_id_in_import_expression11177)
                remote_variable_id579 = self.remote_variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, remote_variable_id579.tree)
                # sdl92.g:936:47: ( ',' destination )?
                alt168 = 2
                LA168_0 = self.input.LA(1)

                if (LA168_0 == COMMA) :
                    alt168 = 1
                if alt168 == 1:
                    # sdl92.g:936:48: ',' destination
                    pass 
                    char_literal580=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_import_expression11180)
                    if self._state.backtracking == 0:

                        char_literal580_tree = self._adaptor.createWithPayload(char_literal580)
                        self._adaptor.addChild(root_0, char_literal580_tree)

                    self._state.following.append(self.FOLLOW_destination_in_import_expression11182)
                    destination581 = self.destination()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, destination581.tree)



                char_literal582=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_import_expression11186)
                if self._state.backtracking == 0:

                    char_literal582_tree = self._adaptor.createWithPayload(char_literal582)
                    self._adaptor.addChild(root_0, char_literal582_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "import_expression"

    class view_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.view_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "view_expression"
    # sdl92.g:939:1: view_expression : VIEW '(' view_id ( ',' pid_expression )? ')' ;
    def view_expression(self, ):

        retval = self.view_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        VIEW583 = None
        char_literal584 = None
        char_literal586 = None
        char_literal588 = None
        view_id585 = None

        pid_expression587 = None


        VIEW583_tree = None
        char_literal584_tree = None
        char_literal586_tree = None
        char_literal588_tree = None

        try:
            try:
                # sdl92.g:940:9: ( VIEW '(' view_id ( ',' pid_expression )? ')' )
                # sdl92.g:940:17: VIEW '(' view_id ( ',' pid_expression )? ')'
                pass 
                root_0 = self._adaptor.nil()

                VIEW583=self.match(self.input, VIEW, self.FOLLOW_VIEW_in_view_expression11209)
                if self._state.backtracking == 0:

                    VIEW583_tree = self._adaptor.createWithPayload(VIEW583)
                    self._adaptor.addChild(root_0, VIEW583_tree)

                char_literal584=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_view_expression11211)
                if self._state.backtracking == 0:

                    char_literal584_tree = self._adaptor.createWithPayload(char_literal584)
                    self._adaptor.addChild(root_0, char_literal584_tree)

                self._state.following.append(self.FOLLOW_view_id_in_view_expression11213)
                view_id585 = self.view_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, view_id585.tree)
                # sdl92.g:940:34: ( ',' pid_expression )?
                alt169 = 2
                LA169_0 = self.input.LA(1)

                if (LA169_0 == COMMA) :
                    alt169 = 1
                if alt169 == 1:
                    # sdl92.g:940:35: ',' pid_expression
                    pass 
                    char_literal586=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_view_expression11216)
                    if self._state.backtracking == 0:

                        char_literal586_tree = self._adaptor.createWithPayload(char_literal586)
                        self._adaptor.addChild(root_0, char_literal586_tree)

                    self._state.following.append(self.FOLLOW_pid_expression_in_view_expression11218)
                    pid_expression587 = self.pid_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, pid_expression587.tree)



                char_literal588=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_view_expression11222)
                if self._state.backtracking == 0:

                    char_literal588_tree = self._adaptor.createWithPayload(char_literal588)
                    self._adaptor.addChild(root_0, char_literal588_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "view_expression"

    class variable_access_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_access_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable_access"
    # sdl92.g:943:1: variable_access : variable_id ;
    def variable_access(self, ):

        retval = self.variable_access_return()
        retval.start = self.input.LT(1)

        root_0 = None

        variable_id589 = None



        try:
            try:
                # sdl92.g:944:9: ( variable_id )
                # sdl92.g:944:17: variable_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_variable_id_in_variable_access11245)
                variable_id589 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, variable_id589.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable_access"

    class operator_application_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operator_application_return, self).__init__()

            self.tree = None




    # $ANTLR start "operator_application"
    # sdl92.g:947:1: operator_application : operator_id '(' active_expression_list ')' ;
    def operator_application(self, ):

        retval = self.operator_application_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal591 = None
        char_literal593 = None
        operator_id590 = None

        active_expression_list592 = None


        char_literal591_tree = None
        char_literal593_tree = None

        try:
            try:
                # sdl92.g:948:9: ( operator_id '(' active_expression_list ')' )
                # sdl92.g:948:17: operator_id '(' active_expression_list ')'
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operator_id_in_operator_application11268)
                operator_id590 = self.operator_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operator_id590.tree)
                char_literal591=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_operator_application11270)
                if self._state.backtracking == 0:

                    char_literal591_tree = self._adaptor.createWithPayload(char_literal591)
                    self._adaptor.addChild(root_0, char_literal591_tree)

                self._state.following.append(self.FOLLOW_active_expression_list_in_operator_application11271)
                active_expression_list592 = self.active_expression_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, active_expression_list592.tree)
                char_literal593=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_operator_application11273)
                if self._state.backtracking == 0:

                    char_literal593_tree = self._adaptor.createWithPayload(char_literal593)
                    self._adaptor.addChild(root_0, char_literal593_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operator_application"

    class active_expression_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.active_expression_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "active_expression_list"
    # sdl92.g:951:1: active_expression_list : active_expression ( ',' expression_list )? ;
    def active_expression_list(self, ):

        retval = self.active_expression_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal595 = None
        active_expression594 = None

        expression_list596 = None


        char_literal595_tree = None

        try:
            try:
                # sdl92.g:952:9: ( active_expression ( ',' expression_list )? )
                # sdl92.g:952:17: active_expression ( ',' expression_list )?
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_active_expression_in_active_expression_list11296)
                active_expression594 = self.active_expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, active_expression594.tree)
                # sdl92.g:952:35: ( ',' expression_list )?
                alt170 = 2
                LA170_0 = self.input.LA(1)

                if (LA170_0 == COMMA) :
                    alt170 = 1
                if alt170 == 1:
                    # sdl92.g:952:36: ',' expression_list
                    pass 
                    char_literal595=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_active_expression_list11299)
                    if self._state.backtracking == 0:

                        char_literal595_tree = self._adaptor.createWithPayload(char_literal595)
                        self._adaptor.addChild(root_0, char_literal595_tree)

                    self._state.following.append(self.FOLLOW_expression_list_in_active_expression_list11301)
                    expression_list596 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, expression_list596.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "active_expression_list"

    class conditional_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.conditional_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "conditional_expression"
    # sdl92.g:963:1: conditional_expression : IF expression THEN expression ELSE expression FI ;
    def conditional_expression(self, ):

        retval = self.conditional_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IF597 = None
        THEN599 = None
        ELSE601 = None
        FI603 = None
        expression598 = None

        expression600 = None

        expression602 = None


        IF597_tree = None
        THEN599_tree = None
        ELSE601_tree = None
        FI603_tree = None

        try:
            try:
                # sdl92.g:964:9: ( IF expression THEN expression ELSE expression FI )
                # sdl92.g:964:17: IF expression THEN expression ELSE expression FI
                pass 
                root_0 = self._adaptor.nil()

                IF597=self.match(self.input, IF, self.FOLLOW_IF_in_conditional_expression11333)
                if self._state.backtracking == 0:

                    IF597_tree = self._adaptor.createWithPayload(IF597)
                    self._adaptor.addChild(root_0, IF597_tree)

                self._state.following.append(self.FOLLOW_expression_in_conditional_expression11335)
                expression598 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression598.tree)
                THEN599=self.match(self.input, THEN, self.FOLLOW_THEN_in_conditional_expression11337)
                if self._state.backtracking == 0:

                    THEN599_tree = self._adaptor.createWithPayload(THEN599)
                    self._adaptor.addChild(root_0, THEN599_tree)

                self._state.following.append(self.FOLLOW_expression_in_conditional_expression11339)
                expression600 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression600.tree)
                ELSE601=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_conditional_expression11341)
                if self._state.backtracking == 0:

                    ELSE601_tree = self._adaptor.createWithPayload(ELSE601)
                    self._adaptor.addChild(root_0, ELSE601_tree)

                self._state.following.append(self.FOLLOW_expression_in_conditional_expression11343)
                expression602 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression602.tree)
                FI603=self.match(self.input, FI, self.FOLLOW_FI_in_conditional_expression11345)
                if self._state.backtracking == 0:

                    FI603_tree = self._adaptor.createWithPayload(FI603)
                    self._adaptor.addChild(root_0, FI603_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "conditional_expression"

    class external_synonym_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.external_synonym_return, self).__init__()

            self.tree = None




    # $ANTLR start "external_synonym"
    # sdl92.g:970:1: external_synonym : external_synonym_id ;
    def external_synonym(self, ):

        retval = self.external_synonym_return()
        retval.start = self.input.LT(1)

        root_0 = None

        external_synonym_id604 = None



        try:
            try:
                # sdl92.g:971:9: ( external_synonym_id )
                # sdl92.g:971:17: external_synonym_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_external_synonym_id_in_external_synonym11371)
                external_synonym_id604 = self.external_synonym_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, external_synonym_id604.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "external_synonym"

    class conditional_ground_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.conditional_ground_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "conditional_ground_expression"
    # sdl92.g:974:1: conditional_ground_expression : IF ifexpr= expression THEN thenexpr= expression ELSE elseexpr= expression FI -> ^( IFTHENELSE $ifexpr $thenexpr $elseexpr) ;
    def conditional_ground_expression(self, ):

        retval = self.conditional_ground_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IF605 = None
        THEN606 = None
        ELSE607 = None
        FI608 = None
        ifexpr = None

        thenexpr = None

        elseexpr = None


        IF605_tree = None
        THEN606_tree = None
        ELSE607_tree = None
        FI608_tree = None
        stream_THEN = RewriteRuleTokenStream(self._adaptor, "token THEN")
        stream_IF = RewriteRuleTokenStream(self._adaptor, "token IF")
        stream_ELSE = RewriteRuleTokenStream(self._adaptor, "token ELSE")
        stream_FI = RewriteRuleTokenStream(self._adaptor, "token FI")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:975:9: ( IF ifexpr= expression THEN thenexpr= expression ELSE elseexpr= expression FI -> ^( IFTHENELSE $ifexpr $thenexpr $elseexpr) )
                # sdl92.g:975:17: IF ifexpr= expression THEN thenexpr= expression ELSE elseexpr= expression FI
                pass 
                IF605=self.match(self.input, IF, self.FOLLOW_IF_in_conditional_ground_expression11394) 
                if self._state.backtracking == 0:
                    stream_IF.add(IF605)
                self._state.following.append(self.FOLLOW_expression_in_conditional_ground_expression11398)
                ifexpr = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(ifexpr.tree)
                THEN606=self.match(self.input, THEN, self.FOLLOW_THEN_in_conditional_ground_expression11416) 
                if self._state.backtracking == 0:
                    stream_THEN.add(THEN606)
                self._state.following.append(self.FOLLOW_expression_in_conditional_ground_expression11420)
                thenexpr = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(thenexpr.tree)
                ELSE607=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_conditional_ground_expression11438) 
                if self._state.backtracking == 0:
                    stream_ELSE.add(ELSE607)
                self._state.following.append(self.FOLLOW_expression_in_conditional_ground_expression11442)
                elseexpr = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(elseexpr.tree)
                FI608=self.match(self.input, FI, self.FOLLOW_FI_in_conditional_ground_expression11444) 
                if self._state.backtracking == 0:
                    stream_FI.add(FI608)

                # AST Rewrite
                # elements: thenexpr, elseexpr, ifexpr
                # token labels: 
                # rule labels: elseexpr, retval, ifexpr, thenexpr
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if elseexpr is not None:
                        stream_elseexpr = RewriteRuleSubtreeStream(self._adaptor, "rule elseexpr", elseexpr.tree)
                    else:
                        stream_elseexpr = RewriteRuleSubtreeStream(self._adaptor, "token elseexpr", None)


                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if ifexpr is not None:
                        stream_ifexpr = RewriteRuleSubtreeStream(self._adaptor, "rule ifexpr", ifexpr.tree)
                    else:
                        stream_ifexpr = RewriteRuleSubtreeStream(self._adaptor, "token ifexpr", None)


                    if thenexpr is not None:
                        stream_thenexpr = RewriteRuleSubtreeStream(self._adaptor, "rule thenexpr", thenexpr.tree)
                    else:
                        stream_thenexpr = RewriteRuleSubtreeStream(self._adaptor, "token thenexpr", None)


                    root_0 = self._adaptor.nil()
                    # 978:9: -> ^( IFTHENELSE $ifexpr $thenexpr $elseexpr)
                    # sdl92.g:978:17: ^( IFTHENELSE $ifexpr $thenexpr $elseexpr)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(IFTHENELSE, "IFTHENELSE"), root_1)

                    self._adaptor.addChild(root_1, stream_ifexpr.nextTree())
                    self._adaptor.addChild(root_1, stream_thenexpr.nextTree())
                    self._adaptor.addChild(root_1, stream_elseexpr.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "conditional_ground_expression"

    class expression_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.expression_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "expression_list"
    # sdl92.g:981:1: expression_list : expression ( ',' expression )* -> ( expression )+ ;
    def expression_list(self, ):

        retval = self.expression_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal610 = None
        expression609 = None

        expression611 = None


        char_literal610_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:982:9: ( expression ( ',' expression )* -> ( expression )+ )
                # sdl92.g:982:17: expression ( ',' expression )*
                pass 
                self._state.following.append(self.FOLLOW_expression_in_expression_list11495)
                expression609 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression609.tree)
                # sdl92.g:982:28: ( ',' expression )*
                while True: #loop171
                    alt171 = 2
                    LA171_0 = self.input.LA(1)

                    if (LA171_0 == COMMA) :
                        alt171 = 1


                    if alt171 == 1:
                        # sdl92.g:982:29: ',' expression
                        pass 
                        char_literal610=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_expression_list11498) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal610)
                        self._state.following.append(self.FOLLOW_expression_in_expression_list11500)
                        expression611 = self.expression()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_expression.add(expression611.tree)


                    else:
                        break #loop171

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 983:9: -> ( expression )+
                    # sdl92.g:983:17: ( expression )+
                    if not (stream_expression.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_expression.hasNext():
                        self._adaptor.addChild(root_0, stream_expression.nextTree())


                    stream_expression.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "expression_list"

    class terminator_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.terminator_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "terminator_statement"
    # sdl92.g:986:1: terminator_statement : ( label )? ( cif )? ( hyperlink )? terminator end -> ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator ) ;
    def terminator_statement(self, ):

        retval = self.terminator_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        label612 = None

        cif613 = None

        hyperlink614 = None

        terminator615 = None

        end616 = None


        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_terminator = RewriteRuleSubtreeStream(self._adaptor, "rule terminator")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_label = RewriteRuleSubtreeStream(self._adaptor, "rule label")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:987:9: ( ( label )? ( cif )? ( hyperlink )? terminator end -> ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator ) )
                # sdl92.g:987:17: ( label )? ( cif )? ( hyperlink )? terminator end
                pass 
                # sdl92.g:987:17: ( label )?
                alt172 = 2
                alt172 = self.dfa172.predict(self.input)
                if alt172 == 1:
                    # sdl92.g:0:0: label
                    pass 
                    self._state.following.append(self.FOLLOW_label_in_terminator_statement11543)
                    label612 = self.label()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_label.add(label612.tree)



                # sdl92.g:988:17: ( cif )?
                alt173 = 2
                LA173_0 = self.input.LA(1)

                if (LA173_0 == 217) :
                    LA173_1 = self.input.LA(2)

                    if (LA173_1 == ANSWER or LA173_1 == COMMENT or LA173_1 == CONNECT or LA173_1 == DECISION or LA173_1 == INPUT or (JOIN <= LA173_1 <= LABEL) or LA173_1 == NEXTSTATE or LA173_1 == OUTPUT or (PROCEDURE <= LA173_1 <= PROCEDURE_CALL) or (PROCESS <= LA173_1 <= PROVIDED) or LA173_1 == RETURN or LA173_1 == STATE or LA173_1 == STOP or LA173_1 == TASK or LA173_1 == TEXT or LA173_1 == START) :
                        alt173 = 1
                if alt173 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_terminator_statement11562)
                    cif613 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif613.tree)



                # sdl92.g:989:17: ( hyperlink )?
                alt174 = 2
                LA174_0 = self.input.LA(1)

                if (LA174_0 == 217) :
                    alt174 = 1
                if alt174 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_terminator_statement11581)
                    hyperlink614 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink614.tree)



                self._state.following.append(self.FOLLOW_terminator_in_terminator_statement11600)
                terminator615 = self.terminator()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_terminator.add(terminator615.tree)
                self._state.following.append(self.FOLLOW_end_in_terminator_statement11618)
                end616 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end616.tree)

                # AST Rewrite
                # elements: end, cif, hyperlink, terminator, label
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 992:9: -> ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator )
                    # sdl92.g:992:17: ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TERMINATOR, "TERMINATOR"), root_1)

                    # sdl92.g:992:30: ( label )?
                    if stream_label.hasNext():
                        self._adaptor.addChild(root_1, stream_label.nextTree())


                    stream_label.reset();
                    # sdl92.g:992:37: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:992:42: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:992:53: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_terminator.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "terminator_statement"

    class label_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.label_return, self).__init__()

            self.tree = None




    # $ANTLR start "label"
    # sdl92.g:994:1: label : ( cif )? connector_name ':' -> ^( LABEL ( cif )? connector_name ) ;
    def label(self, ):

        retval = self.label_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal619 = None
        cif617 = None

        connector_name618 = None


        char_literal619_tree = None
        stream_212 = RewriteRuleTokenStream(self._adaptor, "token 212")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_connector_name = RewriteRuleSubtreeStream(self._adaptor, "rule connector_name")
        try:
            try:
                # sdl92.g:995:9: ( ( cif )? connector_name ':' -> ^( LABEL ( cif )? connector_name ) )
                # sdl92.g:995:17: ( cif )? connector_name ':'
                pass 
                # sdl92.g:995:17: ( cif )?
                alt175 = 2
                LA175_0 = self.input.LA(1)

                if (LA175_0 == 217) :
                    alt175 = 1
                if alt175 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_label11673)
                    cif617 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif617.tree)



                self._state.following.append(self.FOLLOW_connector_name_in_label11676)
                connector_name618 = self.connector_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_connector_name.add(connector_name618.tree)
                char_literal619=self.match(self.input, 212, self.FOLLOW_212_in_label11678) 
                if self._state.backtracking == 0:
                    stream_212.add(char_literal619)

                # AST Rewrite
                # elements: connector_name, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 996:9: -> ^( LABEL ( cif )? connector_name )
                    # sdl92.g:996:17: ^( LABEL ( cif )? connector_name )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(LABEL, "LABEL"), root_1)

                    # sdl92.g:996:25: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    self._adaptor.addChild(root_1, stream_connector_name.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "label"

    class terminator_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.terminator_return, self).__init__()

            self.tree = None




    # $ANTLR start "terminator"
    # sdl92.g:999:1: terminator : ( nextstate | join | stop | return_stmt );
    def terminator(self, ):

        retval = self.terminator_return()
        retval.start = self.input.LT(1)

        root_0 = None

        nextstate620 = None

        join621 = None

        stop622 = None

        return_stmt623 = None



        try:
            try:
                # sdl92.g:1000:9: ( nextstate | join | stop | return_stmt )
                alt176 = 4
                LA176 = self.input.LA(1)
                if LA176 == NEXTSTATE:
                    alt176 = 1
                elif LA176 == JOIN:
                    alt176 = 2
                elif LA176 == STOP:
                    alt176 = 3
                elif LA176 == RETURN:
                    alt176 = 4
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 176, 0, self.input)

                    raise nvae

                if alt176 == 1:
                    # sdl92.g:1000:17: nextstate
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_nextstate_in_terminator11725)
                    nextstate620 = self.nextstate()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, nextstate620.tree)


                elif alt176 == 2:
                    # sdl92.g:1000:29: join
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_join_in_terminator11729)
                    join621 = self.join()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, join621.tree)


                elif alt176 == 3:
                    # sdl92.g:1000:36: stop
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_stop_in_terminator11733)
                    stop622 = self.stop()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, stop622.tree)


                elif alt176 == 4:
                    # sdl92.g:1000:43: return_stmt
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_return_stmt_in_terminator11737)
                    return_stmt623 = self.return_stmt()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, return_stmt623.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "terminator"

    class join_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.join_return, self).__init__()

            self.tree = None




    # $ANTLR start "join"
    # sdl92.g:1003:1: join : JOIN connector_name -> ^( JOIN connector_name ) ;
    def join(self, ):

        retval = self.join_return()
        retval.start = self.input.LT(1)

        root_0 = None

        JOIN624 = None
        connector_name625 = None


        JOIN624_tree = None
        stream_JOIN = RewriteRuleTokenStream(self._adaptor, "token JOIN")
        stream_connector_name = RewriteRuleSubtreeStream(self._adaptor, "rule connector_name")
        try:
            try:
                # sdl92.g:1004:9: ( JOIN connector_name -> ^( JOIN connector_name ) )
                # sdl92.g:1004:18: JOIN connector_name
                pass 
                JOIN624=self.match(self.input, JOIN, self.FOLLOW_JOIN_in_join11761) 
                if self._state.backtracking == 0:
                    stream_JOIN.add(JOIN624)
                self._state.following.append(self.FOLLOW_connector_name_in_join11763)
                connector_name625 = self.connector_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_connector_name.add(connector_name625.tree)

                # AST Rewrite
                # elements: connector_name, JOIN
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1005:9: -> ^( JOIN connector_name )
                    # sdl92.g:1005:18: ^( JOIN connector_name )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_JOIN.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_connector_name.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "join"

    class stop_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.stop_return, self).__init__()

            self.tree = None




    # $ANTLR start "stop"
    # sdl92.g:1008:1: stop : STOP ;
    def stop(self, ):

        retval = self.stop_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STOP626 = None

        STOP626_tree = None

        try:
            try:
                # sdl92.g:1008:9: ( STOP )
                # sdl92.g:1008:17: STOP
                pass 
                root_0 = self._adaptor.nil()

                STOP626=self.match(self.input, STOP, self.FOLLOW_STOP_in_stop11803)
                if self._state.backtracking == 0:

                    STOP626_tree = self._adaptor.createWithPayload(STOP626)
                    self._adaptor.addChild(root_0, STOP626_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "stop"

    class return_stmt_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.return_stmt_return, self).__init__()

            self.tree = None




    # $ANTLR start "return_stmt"
    # sdl92.g:1011:1: return_stmt : RETURN ( expression )? -> ^( RETURN ( expression )? ) ;
    def return_stmt(self, ):

        retval = self.return_stmt_return()
        retval.start = self.input.LT(1)

        root_0 = None

        RETURN627 = None
        expression628 = None


        RETURN627_tree = None
        stream_RETURN = RewriteRuleTokenStream(self._adaptor, "token RETURN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:1012:9: ( RETURN ( expression )? -> ^( RETURN ( expression )? ) )
                # sdl92.g:1012:17: RETURN ( expression )?
                pass 
                RETURN627=self.match(self.input, RETURN, self.FOLLOW_RETURN_in_return_stmt11826) 
                if self._state.backtracking == 0:
                    stream_RETURN.add(RETURN627)
                # sdl92.g:1012:24: ( expression )?
                alt177 = 2
                LA177_0 = self.input.LA(1)

                if (LA177_0 == BITSTR or LA177_0 == FLOAT or LA177_0 == IF or LA177_0 == OCTSTR or LA177_0 == STRING or LA177_0 == INT or LA177_0 == L_PAREN or LA177_0 == ID or LA177_0 == DASH or (NOT <= LA177_0 <= MINUS_INFINITY) or LA177_0 == L_BRACKET) :
                    alt177 = 1
                if alt177 == 1:
                    # sdl92.g:0:0: expression
                    pass 
                    self._state.following.append(self.FOLLOW_expression_in_return_stmt11828)
                    expression628 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression628.tree)




                # AST Rewrite
                # elements: RETURN, expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1013:9: -> ^( RETURN ( expression )? )
                    # sdl92.g:1013:17: ^( RETURN ( expression )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_RETURN.nextNode(), root_1)

                    # sdl92.g:1013:26: ( expression )?
                    if stream_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_expression.nextTree())


                    stream_expression.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "return_stmt"

    class nextstate_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.nextstate_return, self).__init__()

            self.tree = None




    # $ANTLR start "nextstate"
    # sdl92.g:1016:1: nextstate : NEXTSTATE nextstatebody -> ^( NEXTSTATE nextstatebody ) ;
    def nextstate(self, ):

        retval = self.nextstate_return()
        retval.start = self.input.LT(1)

        root_0 = None

        NEXTSTATE629 = None
        nextstatebody630 = None


        NEXTSTATE629_tree = None
        stream_NEXTSTATE = RewriteRuleTokenStream(self._adaptor, "token NEXTSTATE")
        stream_nextstatebody = RewriteRuleSubtreeStream(self._adaptor, "rule nextstatebody")
        try:
            try:
                # sdl92.g:1017:9: ( NEXTSTATE nextstatebody -> ^( NEXTSTATE nextstatebody ) )
                # sdl92.g:1017:17: NEXTSTATE nextstatebody
                pass 
                NEXTSTATE629=self.match(self.input, NEXTSTATE, self.FOLLOW_NEXTSTATE_in_nextstate11874) 
                if self._state.backtracking == 0:
                    stream_NEXTSTATE.add(NEXTSTATE629)
                self._state.following.append(self.FOLLOW_nextstatebody_in_nextstate11876)
                nextstatebody630 = self.nextstatebody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_nextstatebody.add(nextstatebody630.tree)

                # AST Rewrite
                # elements: nextstatebody, NEXTSTATE
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1018:9: -> ^( NEXTSTATE nextstatebody )
                    # sdl92.g:1018:17: ^( NEXTSTATE nextstatebody )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_NEXTSTATE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_nextstatebody.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "nextstate"

    class nextstatebody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.nextstatebody_return, self).__init__()

            self.tree = None




    # $ANTLR start "nextstatebody"
    # sdl92.g:1021:1: nextstatebody : ( statename ( via )? | dash_nextstate );
    def nextstatebody(self, ):

        retval = self.nextstatebody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        statename631 = None

        via632 = None

        dash_nextstate633 = None



        try:
            try:
                # sdl92.g:1022:9: ( statename ( via )? | dash_nextstate )
                alt179 = 2
                LA179_0 = self.input.LA(1)

                if (LA179_0 == ID) :
                    alt179 = 1
                elif (LA179_0 == DASH) :
                    alt179 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 179, 0, self.input)

                    raise nvae

                if alt179 == 1:
                    # sdl92.g:1022:17: statename ( via )?
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_statename_in_nextstatebody11920)
                    statename631 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, statename631.tree)
                    # sdl92.g:1022:27: ( via )?
                    alt178 = 2
                    LA178_0 = self.input.LA(1)

                    if (LA178_0 == VIA) :
                        alt178 = 1
                    if alt178 == 1:
                        # sdl92.g:0:0: via
                        pass 
                        self._state.following.append(self.FOLLOW_via_in_nextstatebody11922)
                        via632 = self.via()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, via632.tree)





                elif alt179 == 2:
                    # sdl92.g:1023:19: dash_nextstate
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_dash_nextstate_in_nextstatebody11943)
                    dash_nextstate633 = self.dash_nextstate()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, dash_nextstate633.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "nextstatebody"

    class via_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.via_return, self).__init__()

            self.tree = None




    # $ANTLR start "via"
    # sdl92.g:1026:1: via : VIA state_entry_point_name -> ^( VIA state_entry_point_name ) ;
    def via(self, ):

        retval = self.via_return()
        retval.start = self.input.LT(1)

        root_0 = None

        VIA634 = None
        state_entry_point_name635 = None


        VIA634_tree = None
        stream_VIA = RewriteRuleTokenStream(self._adaptor, "token VIA")
        stream_state_entry_point_name = RewriteRuleSubtreeStream(self._adaptor, "rule state_entry_point_name")
        try:
            try:
                # sdl92.g:1026:9: ( VIA state_entry_point_name -> ^( VIA state_entry_point_name ) )
                # sdl92.g:1026:17: VIA state_entry_point_name
                pass 
                VIA634=self.match(self.input, VIA, self.FOLLOW_VIA_in_via11962) 
                if self._state.backtracking == 0:
                    stream_VIA.add(VIA634)
                self._state.following.append(self.FOLLOW_state_entry_point_name_in_via11964)
                state_entry_point_name635 = self.state_entry_point_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_state_entry_point_name.add(state_entry_point_name635.tree)

                # AST Rewrite
                # elements: state_entry_point_name, VIA
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1027:9: -> ^( VIA state_entry_point_name )
                    # sdl92.g:1027:17: ^( VIA state_entry_point_name )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_VIA.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_state_entry_point_name.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "via"

    class end_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.end_return, self).__init__()

            self.tree = None




    # $ANTLR start "end"
    # sdl92.g:1030:1: end : ( ( cif )? ( hyperlink )? COMMENT STRING )? SEMI -> ( ^( COMMENT ( cif )? ( hyperlink )? STRING ) )? ;
    def end(self, ):

        retval = self.end_return()
        retval.start = self.input.LT(1)

        root_0 = None

        COMMENT638 = None
        STRING639 = None
        SEMI640 = None
        cif636 = None

        hyperlink637 = None


        COMMENT638_tree = None
        STRING639_tree = None
        SEMI640_tree = None
        stream_COMMENT = RewriteRuleTokenStream(self._adaptor, "token COMMENT")
        stream_SEMI = RewriteRuleTokenStream(self._adaptor, "token SEMI")
        stream_STRING = RewriteRuleTokenStream(self._adaptor, "token STRING")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        try:
            try:
                # sdl92.g:1031:9: ( ( ( cif )? ( hyperlink )? COMMENT STRING )? SEMI -> ( ^( COMMENT ( cif )? ( hyperlink )? STRING ) )? )
                # sdl92.g:1031:13: ( ( cif )? ( hyperlink )? COMMENT STRING )? SEMI
                pass 
                # sdl92.g:1031:13: ( ( cif )? ( hyperlink )? COMMENT STRING )?
                alt182 = 2
                LA182_0 = self.input.LA(1)

                if (LA182_0 == COMMENT or LA182_0 == 217) :
                    alt182 = 1
                if alt182 == 1:
                    # sdl92.g:1031:14: ( cif )? ( hyperlink )? COMMENT STRING
                    pass 
                    # sdl92.g:1031:14: ( cif )?
                    alt180 = 2
                    LA180_0 = self.input.LA(1)

                    if (LA180_0 == 217) :
                        LA180_1 = self.input.LA(2)

                        if (LA180_1 == ANSWER or LA180_1 == COMMENT or LA180_1 == CONNECT or LA180_1 == DECISION or LA180_1 == INPUT or (JOIN <= LA180_1 <= LABEL) or LA180_1 == NEXTSTATE or LA180_1 == OUTPUT or (PROCEDURE <= LA180_1 <= PROCEDURE_CALL) or (PROCESS <= LA180_1 <= PROVIDED) or LA180_1 == RETURN or LA180_1 == STATE or LA180_1 == STOP or LA180_1 == TASK or LA180_1 == TEXT or LA180_1 == START) :
                            alt180 = 1
                    if alt180 == 1:
                        # sdl92.g:0:0: cif
                        pass 
                        self._state.following.append(self.FOLLOW_cif_in_end12005)
                        cif636 = self.cif()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_cif.add(cif636.tree)



                    # sdl92.g:1031:19: ( hyperlink )?
                    alt181 = 2
                    LA181_0 = self.input.LA(1)

                    if (LA181_0 == 217) :
                        alt181 = 1
                    if alt181 == 1:
                        # sdl92.g:0:0: hyperlink
                        pass 
                        self._state.following.append(self.FOLLOW_hyperlink_in_end12008)
                        hyperlink637 = self.hyperlink()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_hyperlink.add(hyperlink637.tree)



                    COMMENT638=self.match(self.input, COMMENT, self.FOLLOW_COMMENT_in_end12011) 
                    if self._state.backtracking == 0:
                        stream_COMMENT.add(COMMENT638)
                    STRING639=self.match(self.input, STRING, self.FOLLOW_STRING_in_end12013) 
                    if self._state.backtracking == 0:
                        stream_STRING.add(STRING639)



                SEMI640=self.match(self.input, SEMI, self.FOLLOW_SEMI_in_end12017) 
                if self._state.backtracking == 0:
                    stream_SEMI.add(SEMI640)

                # AST Rewrite
                # elements: hyperlink, COMMENT, STRING, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1032:9: -> ( ^( COMMENT ( cif )? ( hyperlink )? STRING ) )?
                    # sdl92.g:1032:12: ( ^( COMMENT ( cif )? ( hyperlink )? STRING ) )?
                    if stream_hyperlink.hasNext() or stream_COMMENT.hasNext() or stream_STRING.hasNext() or stream_cif.hasNext():
                        # sdl92.g:1032:12: ^( COMMENT ( cif )? ( hyperlink )? STRING )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_COMMENT.nextNode(), root_1)

                        # sdl92.g:1032:22: ( cif )?
                        if stream_cif.hasNext():
                            self._adaptor.addChild(root_1, stream_cif.nextTree())


                        stream_cif.reset();
                        # sdl92.g:1032:27: ( hyperlink )?
                        if stream_hyperlink.hasNext():
                            self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                        stream_hyperlink.reset();
                        self._adaptor.addChild(root_1, stream_STRING.nextNode())

                        self._adaptor.addChild(root_0, root_1)


                    stream_hyperlink.reset();
                    stream_COMMENT.reset();
                    stream_STRING.reset();
                    stream_cif.reset();



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "end"

    class cif_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif"
    # sdl92.g:1035:1: cif : cif_decl symbolname L_PAREN x= INT COMMA y= INT R_PAREN COMMA L_PAREN width= INT COMMA height= INT R_PAREN cif_end -> ^( CIF $x $y $width $height) ;
    def cif(self, ):

        retval = self.cif_return()
        retval.start = self.input.LT(1)

        root_0 = None

        x = None
        y = None
        width = None
        height = None
        L_PAREN643 = None
        COMMA644 = None
        R_PAREN645 = None
        COMMA646 = None
        L_PAREN647 = None
        COMMA648 = None
        R_PAREN649 = None
        cif_decl641 = None

        symbolname642 = None

        cif_end650 = None


        x_tree = None
        y_tree = None
        width_tree = None
        height_tree = None
        L_PAREN643_tree = None
        COMMA644_tree = None
        R_PAREN645_tree = None
        COMMA646_tree = None
        L_PAREN647_tree = None
        COMMA648_tree = None
        R_PAREN649_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_symbolname = RewriteRuleSubtreeStream(self._adaptor, "rule symbolname")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:1036:9: ( cif_decl symbolname L_PAREN x= INT COMMA y= INT R_PAREN COMMA L_PAREN width= INT COMMA height= INT R_PAREN cif_end -> ^( CIF $x $y $width $height) )
                # sdl92.g:1036:17: cif_decl symbolname L_PAREN x= INT COMMA y= INT R_PAREN COMMA L_PAREN width= INT COMMA height= INT R_PAREN cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_cif12063)
                cif_decl641 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl641.tree)
                self._state.following.append(self.FOLLOW_symbolname_in_cif12065)
                symbolname642 = self.symbolname()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_symbolname.add(symbolname642.tree)
                L_PAREN643=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_cif12083) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN643)
                x=self.match(self.input, INT, self.FOLLOW_INT_in_cif12087) 
                if self._state.backtracking == 0:
                    stream_INT.add(x)
                COMMA644=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_cif12089) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(COMMA644)
                y=self.match(self.input, INT, self.FOLLOW_INT_in_cif12093) 
                if self._state.backtracking == 0:
                    stream_INT.add(y)
                R_PAREN645=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_cif12095) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN645)
                COMMA646=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_cif12113) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(COMMA646)
                L_PAREN647=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_cif12131) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN647)
                width=self.match(self.input, INT, self.FOLLOW_INT_in_cif12135) 
                if self._state.backtracking == 0:
                    stream_INT.add(width)
                COMMA648=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_cif12137) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(COMMA648)
                height=self.match(self.input, INT, self.FOLLOW_INT_in_cif12141) 
                if self._state.backtracking == 0:
                    stream_INT.add(height)
                R_PAREN649=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_cif12143) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN649)
                self._state.following.append(self.FOLLOW_cif_end_in_cif12161)
                cif_end650 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end650.tree)

                # AST Rewrite
                # elements: width, y, height, x
                # token labels: height, width, y, x
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_height = RewriteRuleTokenStream(self._adaptor, "token height", height)
                    stream_width = RewriteRuleTokenStream(self._adaptor, "token width", width)
                    stream_y = RewriteRuleTokenStream(self._adaptor, "token y", y)
                    stream_x = RewriteRuleTokenStream(self._adaptor, "token x", x)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1041:9: -> ^( CIF $x $y $width $height)
                    # sdl92.g:1041:17: ^( CIF $x $y $width $height)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CIF, "CIF"), root_1)

                    self._adaptor.addChild(root_1, stream_x.nextNode())
                    self._adaptor.addChild(root_1, stream_y.nextNode())
                    self._adaptor.addChild(root_1, stream_width.nextNode())
                    self._adaptor.addChild(root_1, stream_height.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif"

    class hyperlink_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.hyperlink_return, self).__init__()

            self.tree = None




    # $ANTLR start "hyperlink"
    # sdl92.g:1044:1: hyperlink : cif_decl KEEP SPECIFIC GEODE HYPERLINK STRING cif_end -> ^( HYPERLINK STRING ) ;
    def hyperlink(self, ):

        retval = self.hyperlink_return()
        retval.start = self.input.LT(1)

        root_0 = None

        KEEP652 = None
        SPECIFIC653 = None
        GEODE654 = None
        HYPERLINK655 = None
        STRING656 = None
        cif_decl651 = None

        cif_end657 = None


        KEEP652_tree = None
        SPECIFIC653_tree = None
        GEODE654_tree = None
        HYPERLINK655_tree = None
        STRING656_tree = None
        stream_SPECIFIC = RewriteRuleTokenStream(self._adaptor, "token SPECIFIC")
        stream_KEEP = RewriteRuleTokenStream(self._adaptor, "token KEEP")
        stream_HYPERLINK = RewriteRuleTokenStream(self._adaptor, "token HYPERLINK")
        stream_GEODE = RewriteRuleTokenStream(self._adaptor, "token GEODE")
        stream_STRING = RewriteRuleTokenStream(self._adaptor, "token STRING")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:1045:9: ( cif_decl KEEP SPECIFIC GEODE HYPERLINK STRING cif_end -> ^( HYPERLINK STRING ) )
                # sdl92.g:1045:17: cif_decl KEEP SPECIFIC GEODE HYPERLINK STRING cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_hyperlink12215)
                cif_decl651 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl651.tree)
                KEEP652=self.match(self.input, KEEP, self.FOLLOW_KEEP_in_hyperlink12217) 
                if self._state.backtracking == 0:
                    stream_KEEP.add(KEEP652)
                SPECIFIC653=self.match(self.input, SPECIFIC, self.FOLLOW_SPECIFIC_in_hyperlink12219) 
                if self._state.backtracking == 0:
                    stream_SPECIFIC.add(SPECIFIC653)
                GEODE654=self.match(self.input, GEODE, self.FOLLOW_GEODE_in_hyperlink12221) 
                if self._state.backtracking == 0:
                    stream_GEODE.add(GEODE654)
                HYPERLINK655=self.match(self.input, HYPERLINK, self.FOLLOW_HYPERLINK_in_hyperlink12223) 
                if self._state.backtracking == 0:
                    stream_HYPERLINK.add(HYPERLINK655)
                STRING656=self.match(self.input, STRING, self.FOLLOW_STRING_in_hyperlink12225) 
                if self._state.backtracking == 0:
                    stream_STRING.add(STRING656)
                self._state.following.append(self.FOLLOW_cif_end_in_hyperlink12243)
                cif_end657 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end657.tree)

                # AST Rewrite
                # elements: STRING, HYPERLINK
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1047:9: -> ^( HYPERLINK STRING )
                    # sdl92.g:1047:17: ^( HYPERLINK STRING )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_HYPERLINK.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_STRING.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "hyperlink"

    class paramnames_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.paramnames_return, self).__init__()

            self.tree = None




    # $ANTLR start "paramnames"
    # sdl92.g:1056:1: paramnames : cif_decl KEEP SPECIFIC GEODE PARAMNAMES ( field_name )+ cif_end -> ^( PARAMNAMES ( field_name )+ ) ;
    def paramnames(self, ):

        retval = self.paramnames_return()
        retval.start = self.input.LT(1)

        root_0 = None

        KEEP659 = None
        SPECIFIC660 = None
        GEODE661 = None
        PARAMNAMES662 = None
        cif_decl658 = None

        field_name663 = None

        cif_end664 = None


        KEEP659_tree = None
        SPECIFIC660_tree = None
        GEODE661_tree = None
        PARAMNAMES662_tree = None
        stream_SPECIFIC = RewriteRuleTokenStream(self._adaptor, "token SPECIFIC")
        stream_PARAMNAMES = RewriteRuleTokenStream(self._adaptor, "token PARAMNAMES")
        stream_KEEP = RewriteRuleTokenStream(self._adaptor, "token KEEP")
        stream_GEODE = RewriteRuleTokenStream(self._adaptor, "token GEODE")
        stream_field_name = RewriteRuleSubtreeStream(self._adaptor, "rule field_name")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:1057:9: ( cif_decl KEEP SPECIFIC GEODE PARAMNAMES ( field_name )+ cif_end -> ^( PARAMNAMES ( field_name )+ ) )
                # sdl92.g:1057:17: cif_decl KEEP SPECIFIC GEODE PARAMNAMES ( field_name )+ cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_paramnames12288)
                cif_decl658 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl658.tree)
                KEEP659=self.match(self.input, KEEP, self.FOLLOW_KEEP_in_paramnames12290) 
                if self._state.backtracking == 0:
                    stream_KEEP.add(KEEP659)
                SPECIFIC660=self.match(self.input, SPECIFIC, self.FOLLOW_SPECIFIC_in_paramnames12292) 
                if self._state.backtracking == 0:
                    stream_SPECIFIC.add(SPECIFIC660)
                GEODE661=self.match(self.input, GEODE, self.FOLLOW_GEODE_in_paramnames12294) 
                if self._state.backtracking == 0:
                    stream_GEODE.add(GEODE661)
                PARAMNAMES662=self.match(self.input, PARAMNAMES, self.FOLLOW_PARAMNAMES_in_paramnames12296) 
                if self._state.backtracking == 0:
                    stream_PARAMNAMES.add(PARAMNAMES662)
                # sdl92.g:1057:57: ( field_name )+
                cnt183 = 0
                while True: #loop183
                    alt183 = 2
                    LA183_0 = self.input.LA(1)

                    if (LA183_0 == ID) :
                        alt183 = 1


                    if alt183 == 1:
                        # sdl92.g:0:0: field_name
                        pass 
                        self._state.following.append(self.FOLLOW_field_name_in_paramnames12298)
                        field_name663 = self.field_name()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_field_name.add(field_name663.tree)


                    else:
                        if cnt183 >= 1:
                            break #loop183

                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        eee = EarlyExitException(183, self.input)
                        raise eee

                    cnt183 += 1
                self._state.following.append(self.FOLLOW_cif_end_in_paramnames12301)
                cif_end664 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end664.tree)

                # AST Rewrite
                # elements: PARAMNAMES, field_name
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1058:9: -> ^( PARAMNAMES ( field_name )+ )
                    # sdl92.g:1058:17: ^( PARAMNAMES ( field_name )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PARAMNAMES.nextNode(), root_1)

                    # sdl92.g:1058:30: ( field_name )+
                    if not (stream_field_name.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_field_name.hasNext():
                        self._adaptor.addChild(root_1, stream_field_name.nextTree())


                    stream_field_name.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "paramnames"

    class use_asn1_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.use_asn1_return, self).__init__()

            self.tree = None




    # $ANTLR start "use_asn1"
    # sdl92.g:1065:1: use_asn1 : cif_decl KEEP SPECIFIC GEODE ASNFILENAME STRING cif_end -> ^( ASN1 STRING ) ;
    def use_asn1(self, ):

        retval = self.use_asn1_return()
        retval.start = self.input.LT(1)

        root_0 = None

        KEEP666 = None
        SPECIFIC667 = None
        GEODE668 = None
        ASNFILENAME669 = None
        STRING670 = None
        cif_decl665 = None

        cif_end671 = None


        KEEP666_tree = None
        SPECIFIC667_tree = None
        GEODE668_tree = None
        ASNFILENAME669_tree = None
        STRING670_tree = None
        stream_ASNFILENAME = RewriteRuleTokenStream(self._adaptor, "token ASNFILENAME")
        stream_SPECIFIC = RewriteRuleTokenStream(self._adaptor, "token SPECIFIC")
        stream_KEEP = RewriteRuleTokenStream(self._adaptor, "token KEEP")
        stream_GEODE = RewriteRuleTokenStream(self._adaptor, "token GEODE")
        stream_STRING = RewriteRuleTokenStream(self._adaptor, "token STRING")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:1066:9: ( cif_decl KEEP SPECIFIC GEODE ASNFILENAME STRING cif_end -> ^( ASN1 STRING ) )
                # sdl92.g:1066:17: cif_decl KEEP SPECIFIC GEODE ASNFILENAME STRING cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_use_asn112348)
                cif_decl665 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl665.tree)
                KEEP666=self.match(self.input, KEEP, self.FOLLOW_KEEP_in_use_asn112350) 
                if self._state.backtracking == 0:
                    stream_KEEP.add(KEEP666)
                SPECIFIC667=self.match(self.input, SPECIFIC, self.FOLLOW_SPECIFIC_in_use_asn112352) 
                if self._state.backtracking == 0:
                    stream_SPECIFIC.add(SPECIFIC667)
                GEODE668=self.match(self.input, GEODE, self.FOLLOW_GEODE_in_use_asn112354) 
                if self._state.backtracking == 0:
                    stream_GEODE.add(GEODE668)
                ASNFILENAME669=self.match(self.input, ASNFILENAME, self.FOLLOW_ASNFILENAME_in_use_asn112356) 
                if self._state.backtracking == 0:
                    stream_ASNFILENAME.add(ASNFILENAME669)
                STRING670=self.match(self.input, STRING, self.FOLLOW_STRING_in_use_asn112358) 
                if self._state.backtracking == 0:
                    stream_STRING.add(STRING670)
                self._state.following.append(self.FOLLOW_cif_end_in_use_asn112360)
                cif_end671 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end671.tree)

                # AST Rewrite
                # elements: STRING
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1067:9: -> ^( ASN1 STRING )
                    # sdl92.g:1067:17: ^( ASN1 STRING )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ASN1, "ASN1"), root_1)

                    self._adaptor.addChild(root_1, stream_STRING.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "use_asn1"

    class symbolname_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.symbolname_return, self).__init__()

            self.tree = None




    # $ANTLR start "symbolname"
    # sdl92.g:1070:1: symbolname : ( START | INPUT | OUTPUT | STATE | PROCEDURE | PROCESS | PROCEDURE_CALL | STOP | RETURN | DECISION | TEXT | TASK | NEXTSTATE | ANSWER | PROVIDED | COMMENT | LABEL | JOIN | CONNECT );
    def symbolname(self, ):

        retval = self.symbolname_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set672 = None

        set672_tree = None

        try:
            try:
                # sdl92.g:1071:9: ( START | INPUT | OUTPUT | STATE | PROCEDURE | PROCESS | PROCEDURE_CALL | STOP | RETURN | DECISION | TEXT | TASK | NEXTSTATE | ANSWER | PROVIDED | COMMENT | LABEL | JOIN | CONNECT )
                # sdl92.g:
                pass 
                root_0 = self._adaptor.nil()

                set672 = self.input.LT(1)
                if self.input.LA(1) == ANSWER or self.input.LA(1) == COMMENT or self.input.LA(1) == CONNECT or self.input.LA(1) == DECISION or self.input.LA(1) == INPUT or (JOIN <= self.input.LA(1) <= LABEL) or self.input.LA(1) == NEXTSTATE or self.input.LA(1) == OUTPUT or (PROCEDURE <= self.input.LA(1) <= PROCEDURE_CALL) or (PROCESS <= self.input.LA(1) <= PROVIDED) or self.input.LA(1) == RETURN or self.input.LA(1) == STATE or self.input.LA(1) == STOP or self.input.LA(1) == TASK or self.input.LA(1) == TEXT or self.input.LA(1) == START:
                    self.input.consume()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, self._adaptor.createWithPayload(set672))
                    self._state.errorRecovery = False

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    mse = MismatchedSetException(None, self.input)
                    raise mse





                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "symbolname"

    class cif_decl_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_decl_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_decl"
    # sdl92.g:1092:1: cif_decl : '/* CIF' ;
    def cif_decl(self, ):

        retval = self.cif_decl_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal673 = None

        string_literal673_tree = None

        try:
            try:
                # sdl92.g:1093:9: ( '/* CIF' )
                # sdl92.g:1093:17: '/* CIF'
                pass 
                root_0 = self._adaptor.nil()

                string_literal673=self.match(self.input, 217, self.FOLLOW_217_in_cif_decl12787)
                if self._state.backtracking == 0:

                    string_literal673_tree = self._adaptor.createWithPayload(string_literal673)
                    self._adaptor.addChild(root_0, string_literal673_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_decl"

    class cif_end_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_end_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_end"
    # sdl92.g:1096:1: cif_end : '*/' ;
    def cif_end(self, ):

        retval = self.cif_end_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal674 = None

        string_literal674_tree = None

        try:
            try:
                # sdl92.g:1097:9: ( '*/' )
                # sdl92.g:1097:17: '*/'
                pass 
                root_0 = self._adaptor.nil()

                string_literal674=self.match(self.input, 218, self.FOLLOW_218_in_cif_end12810)
                if self._state.backtracking == 0:

                    string_literal674_tree = self._adaptor.createWithPayload(string_literal674)
                    self._adaptor.addChild(root_0, string_literal674_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_end"

    class cif_end_text_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_end_text_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_end_text"
    # sdl92.g:1100:1: cif_end_text : cif_decl ENDTEXT cif_end -> ^( ENDTEXT ) ;
    def cif_end_text(self, ):

        retval = self.cif_end_text_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ENDTEXT676 = None
        cif_decl675 = None

        cif_end677 = None


        ENDTEXT676_tree = None
        stream_ENDTEXT = RewriteRuleTokenStream(self._adaptor, "token ENDTEXT")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:1101:9: ( cif_decl ENDTEXT cif_end -> ^( ENDTEXT ) )
                # sdl92.g:1101:17: cif_decl ENDTEXT cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_cif_end_text12833)
                cif_decl675 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl675.tree)
                ENDTEXT676=self.match(self.input, ENDTEXT, self.FOLLOW_ENDTEXT_in_cif_end_text12835) 
                if self._state.backtracking == 0:
                    stream_ENDTEXT.add(ENDTEXT676)
                self._state.following.append(self.FOLLOW_cif_end_in_cif_end_text12837)
                cif_end677 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end677.tree)

                # AST Rewrite
                # elements: ENDTEXT
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 1102:9: -> ^( ENDTEXT )
                    # sdl92.g:1102:17: ^( ENDTEXT )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ENDTEXT.nextNode(), root_1)

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_end_text"

    class cif_end_label_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_end_label_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_end_label"
    # sdl92.g:1104:1: cif_end_label : cif_decl END LABEL cif_end ;
    def cif_end_label(self, ):

        retval = self.cif_end_label_return()
        retval.start = self.input.LT(1)

        root_0 = None

        END679 = None
        LABEL680 = None
        cif_decl678 = None

        cif_end681 = None


        END679_tree = None
        LABEL680_tree = None

        try:
            try:
                # sdl92.g:1105:9: ( cif_decl END LABEL cif_end )
                # sdl92.g:1105:17: cif_decl END LABEL cif_end
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_cif_decl_in_cif_end_label12878)
                cif_decl678 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, cif_decl678.tree)
                END679=self.match(self.input, END, self.FOLLOW_END_in_cif_end_label12880)
                if self._state.backtracking == 0:

                    END679_tree = self._adaptor.createWithPayload(END679)
                    self._adaptor.addChild(root_0, END679_tree)

                LABEL680=self.match(self.input, LABEL, self.FOLLOW_LABEL_in_cif_end_label12882)
                if self._state.backtracking == 0:

                    LABEL680_tree = self._adaptor.createWithPayload(LABEL680)
                    self._adaptor.addChild(root_0, LABEL680_tree)

                self._state.following.append(self.FOLLOW_cif_end_in_cif_end_label12884)
                cif_end681 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, cif_end681.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_end_label"

    class dash_nextstate_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.dash_nextstate_return, self).__init__()

            self.tree = None




    # $ANTLR start "dash_nextstate"
    # sdl92.g:1108:1: dash_nextstate : DASH ;
    def dash_nextstate(self, ):

        retval = self.dash_nextstate_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DASH682 = None

        DASH682_tree = None

        try:
            try:
                # sdl92.g:1108:17: ( DASH )
                # sdl92.g:1108:25: DASH
                pass 
                root_0 = self._adaptor.nil()

                DASH682=self.match(self.input, DASH, self.FOLLOW_DASH_in_dash_nextstate12900)
                if self._state.backtracking == 0:

                    DASH682_tree = self._adaptor.createWithPayload(DASH682)
                    self._adaptor.addChild(root_0, DASH682_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "dash_nextstate"

    class connector_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.connector_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "connector_name"
    # sdl92.g:1109:1: connector_name : ID ;
    def connector_name(self, ):

        retval = self.connector_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID683 = None

        ID683_tree = None

        try:
            try:
                # sdl92.g:1109:17: ( ID )
                # sdl92.g:1109:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID683=self.match(self.input, ID, self.FOLLOW_ID_in_connector_name12914)
                if self._state.backtracking == 0:

                    ID683_tree = self._adaptor.createWithPayload(ID683)
                    self._adaptor.addChild(root_0, ID683_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "connector_name"

    class signal_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_id"
    # sdl92.g:1110:1: signal_id : ID ;
    def signal_id(self, ):

        retval = self.signal_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID684 = None

        ID684_tree = None

        try:
            try:
                # sdl92.g:1110:17: ( ID )
                # sdl92.g:1110:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID684=self.match(self.input, ID, self.FOLLOW_ID_in_signal_id12933)
                if self._state.backtracking == 0:

                    ID684_tree = self._adaptor.createWithPayload(ID684)
                    self._adaptor.addChild(root_0, ID684_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_id"

    class statename_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.statename_return, self).__init__()

            self.tree = None




    # $ANTLR start "statename"
    # sdl92.g:1111:1: statename : ID ;
    def statename(self, ):

        retval = self.statename_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID685 = None

        ID685_tree = None

        try:
            try:
                # sdl92.g:1111:17: ( ID )
                # sdl92.g:1111:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID685=self.match(self.input, ID, self.FOLLOW_ID_in_statename12952)
                if self._state.backtracking == 0:

                    ID685_tree = self._adaptor.createWithPayload(ID685)
                    self._adaptor.addChild(root_0, ID685_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "statename"

    class state_exit_point_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_exit_point_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "state_exit_point_name"
    # sdl92.g:1112:1: state_exit_point_name : ID ;
    def state_exit_point_name(self, ):

        retval = self.state_exit_point_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID686 = None

        ID686_tree = None

        try:
            try:
                # sdl92.g:1113:17: ( ID )
                # sdl92.g:1113:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID686=self.match(self.input, ID, self.FOLLOW_ID_in_state_exit_point_name12981)
                if self._state.backtracking == 0:

                    ID686_tree = self._adaptor.createWithPayload(ID686)
                    self._adaptor.addChild(root_0, ID686_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state_exit_point_name"

    class state_entry_point_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_entry_point_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "state_entry_point_name"
    # sdl92.g:1114:1: state_entry_point_name : ID ;
    def state_entry_point_name(self, ):

        retval = self.state_entry_point_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID687 = None

        ID687_tree = None

        try:
            try:
                # sdl92.g:1115:17: ( ID )
                # sdl92.g:1115:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID687=self.match(self.input, ID, self.FOLLOW_ID_in_state_entry_point_name13010)
                if self._state.backtracking == 0:

                    ID687_tree = self._adaptor.createWithPayload(ID687)
                    self._adaptor.addChild(root_0, ID687_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state_entry_point_name"

    class variable_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable_id"
    # sdl92.g:1116:1: variable_id : ID ;
    def variable_id(self, ):

        retval = self.variable_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID688 = None

        ID688_tree = None

        try:
            try:
                # sdl92.g:1116:17: ( ID )
                # sdl92.g:1116:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID688=self.match(self.input, ID, self.FOLLOW_ID_in_variable_id13027)
                if self._state.backtracking == 0:

                    ID688_tree = self._adaptor.createWithPayload(ID688)
                    self._adaptor.addChild(root_0, ID688_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable_id"

    class literal_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.literal_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "literal_id"
    # sdl92.g:1117:1: literal_id : ( ID | INT );
    def literal_id(self, ):

        retval = self.literal_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set689 = None

        set689_tree = None

        try:
            try:
                # sdl92.g:1117:17: ( ID | INT )
                # sdl92.g:
                pass 
                root_0 = self._adaptor.nil()

                set689 = self.input.LT(1)
                if self.input.LA(1) == INT or self.input.LA(1) == ID:
                    self.input.consume()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, self._adaptor.createWithPayload(set689))
                    self._state.errorRecovery = False

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    mse = MismatchedSetException(None, self.input)
                    raise mse





                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "literal_id"

    class process_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.process_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "process_id"
    # sdl92.g:1118:1: process_id : ID ;
    def process_id(self, ):

        retval = self.process_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID690 = None

        ID690_tree = None

        try:
            try:
                # sdl92.g:1118:17: ( ID )
                # sdl92.g:1118:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID690=self.match(self.input, ID, self.FOLLOW_ID_in_process_id13067)
                if self._state.backtracking == 0:

                    ID690_tree = self._adaptor.createWithPayload(ID690)
                    self._adaptor.addChild(root_0, ID690_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "process_id"

    class system_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.system_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "system_name"
    # sdl92.g:1119:1: system_name : ID ;
    def system_name(self, ):

        retval = self.system_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID691 = None

        ID691_tree = None

        try:
            try:
                # sdl92.g:1119:17: ( ID )
                # sdl92.g:1119:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID691=self.match(self.input, ID, self.FOLLOW_ID_in_system_name13084)
                if self._state.backtracking == 0:

                    ID691_tree = self._adaptor.createWithPayload(ID691)
                    self._adaptor.addChild(root_0, ID691_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "system_name"

    class package_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.package_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "package_name"
    # sdl92.g:1120:1: package_name : ID ;
    def package_name(self, ):

        retval = self.package_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID692 = None

        ID692_tree = None

        try:
            try:
                # sdl92.g:1120:17: ( ID )
                # sdl92.g:1120:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID692=self.match(self.input, ID, self.FOLLOW_ID_in_package_name13100)
                if self._state.backtracking == 0:

                    ID692_tree = self._adaptor.createWithPayload(ID692)
                    self._adaptor.addChild(root_0, ID692_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "package_name"

    class priority_signal_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.priority_signal_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "priority_signal_id"
    # sdl92.g:1121:1: priority_signal_id : ID ;
    def priority_signal_id(self, ):

        retval = self.priority_signal_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID693 = None

        ID693_tree = None

        try:
            try:
                # sdl92.g:1122:17: ( ID )
                # sdl92.g:1122:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID693=self.match(self.input, ID, self.FOLLOW_ID_in_priority_signal_id13129)
                if self._state.backtracking == 0:

                    ID693_tree = self._adaptor.createWithPayload(ID693)
                    self._adaptor.addChild(root_0, ID693_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "priority_signal_id"

    class signal_list_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_list_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_list_id"
    # sdl92.g:1123:1: signal_list_id : ID ;
    def signal_list_id(self, ):

        retval = self.signal_list_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID694 = None

        ID694_tree = None

        try:
            try:
                # sdl92.g:1123:17: ( ID )
                # sdl92.g:1123:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID694=self.match(self.input, ID, self.FOLLOW_ID_in_signal_list_id13143)
                if self._state.backtracking == 0:

                    ID694_tree = self._adaptor.createWithPayload(ID694)
                    self._adaptor.addChild(root_0, ID694_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_list_id"

    class timer_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.timer_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "timer_id"
    # sdl92.g:1124:1: timer_id : ID ;
    def timer_id(self, ):

        retval = self.timer_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID695 = None

        ID695_tree = None

        try:
            try:
                # sdl92.g:1124:17: ( ID )
                # sdl92.g:1124:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID695=self.match(self.input, ID, self.FOLLOW_ID_in_timer_id13163)
                if self._state.backtracking == 0:

                    ID695_tree = self._adaptor.createWithPayload(ID695)
                    self._adaptor.addChild(root_0, ID695_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "timer_id"

    class field_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_name"
    # sdl92.g:1125:1: field_name : ID ;
    def field_name(self, ):

        retval = self.field_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID696 = None

        ID696_tree = None

        try:
            try:
                # sdl92.g:1125:17: ( ID )
                # sdl92.g:1125:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID696=self.match(self.input, ID, self.FOLLOW_ID_in_field_name13181)
                if self._state.backtracking == 0:

                    ID696_tree = self._adaptor.createWithPayload(ID696)
                    self._adaptor.addChild(root_0, ID696_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_name"

    class signal_route_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_route_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_route_id"
    # sdl92.g:1126:1: signal_route_id : ID ;
    def signal_route_id(self, ):

        retval = self.signal_route_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID697 = None

        ID697_tree = None

        try:
            try:
                # sdl92.g:1126:17: ( ID )
                # sdl92.g:1126:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID697=self.match(self.input, ID, self.FOLLOW_ID_in_signal_route_id13194)
                if self._state.backtracking == 0:

                    ID697_tree = self._adaptor.createWithPayload(ID697)
                    self._adaptor.addChild(root_0, ID697_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_route_id"

    class channel_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.channel_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "channel_id"
    # sdl92.g:1127:1: channel_id : ID ;
    def channel_id(self, ):

        retval = self.channel_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID698 = None

        ID698_tree = None

        try:
            try:
                # sdl92.g:1127:17: ( ID )
                # sdl92.g:1127:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID698=self.match(self.input, ID, self.FOLLOW_ID_in_channel_id13212)
                if self._state.backtracking == 0:

                    ID698_tree = self._adaptor.createWithPayload(ID698)
                    self._adaptor.addChild(root_0, ID698_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "channel_id"

    class route_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.route_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "route_id"
    # sdl92.g:1128:1: route_id : ID ;
    def route_id(self, ):

        retval = self.route_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID699 = None

        ID699_tree = None

        try:
            try:
                # sdl92.g:1128:17: ( ID )
                # sdl92.g:1128:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID699=self.match(self.input, ID, self.FOLLOW_ID_in_route_id13232)
                if self._state.backtracking == 0:

                    ID699_tree = self._adaptor.createWithPayload(ID699)
                    self._adaptor.addChild(root_0, ID699_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "route_id"

    class block_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.block_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "block_id"
    # sdl92.g:1129:1: block_id : ID ;
    def block_id(self, ):

        retval = self.block_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID700 = None

        ID700_tree = None

        try:
            try:
                # sdl92.g:1129:17: ( ID )
                # sdl92.g:1129:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID700=self.match(self.input, ID, self.FOLLOW_ID_in_block_id13252)
                if self._state.backtracking == 0:

                    ID700_tree = self._adaptor.createWithPayload(ID700)
                    self._adaptor.addChild(root_0, ID700_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "block_id"

    class source_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.source_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "source_id"
    # sdl92.g:1130:1: source_id : ID ;
    def source_id(self, ):

        retval = self.source_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID701 = None

        ID701_tree = None

        try:
            try:
                # sdl92.g:1130:17: ( ID )
                # sdl92.g:1130:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID701=self.match(self.input, ID, self.FOLLOW_ID_in_source_id13271)
                if self._state.backtracking == 0:

                    ID701_tree = self._adaptor.createWithPayload(ID701)
                    self._adaptor.addChild(root_0, ID701_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "source_id"

    class dest_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.dest_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "dest_id"
    # sdl92.g:1131:1: dest_id : ID ;
    def dest_id(self, ):

        retval = self.dest_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID702 = None

        ID702_tree = None

        try:
            try:
                # sdl92.g:1131:17: ( ID )
                # sdl92.g:1131:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID702=self.match(self.input, ID, self.FOLLOW_ID_in_dest_id13292)
                if self._state.backtracking == 0:

                    ID702_tree = self._adaptor.createWithPayload(ID702)
                    self._adaptor.addChild(root_0, ID702_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "dest_id"

    class gate_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.gate_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "gate_id"
    # sdl92.g:1132:1: gate_id : ID ;
    def gate_id(self, ):

        retval = self.gate_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID703 = None

        ID703_tree = None

        try:
            try:
                # sdl92.g:1132:17: ( ID )
                # sdl92.g:1132:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID703=self.match(self.input, ID, self.FOLLOW_ID_in_gate_id13313)
                if self._state.backtracking == 0:

                    ID703_tree = self._adaptor.createWithPayload(ID703)
                    self._adaptor.addChild(root_0, ID703_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "gate_id"

    class procedure_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure_id"
    # sdl92.g:1133:1: procedure_id : ID ;
    def procedure_id(self, ):

        retval = self.procedure_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID704 = None

        ID704_tree = None

        try:
            try:
                # sdl92.g:1133:17: ( ID )
                # sdl92.g:1133:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID704=self.match(self.input, ID, self.FOLLOW_ID_in_procedure_id13329)
                if self._state.backtracking == 0:

                    ID704_tree = self._adaptor.createWithPayload(ID704)
                    self._adaptor.addChild(root_0, ID704_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure_id"

    class remote_procedure_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.remote_procedure_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "remote_procedure_id"
    # sdl92.g:1134:1: remote_procedure_id : ID ;
    def remote_procedure_id(self, ):

        retval = self.remote_procedure_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID705 = None

        ID705_tree = None

        try:
            try:
                # sdl92.g:1135:17: ( ID )
                # sdl92.g:1135:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID705=self.match(self.input, ID, self.FOLLOW_ID_in_remote_procedure_id13358)
                if self._state.backtracking == 0:

                    ID705_tree = self._adaptor.createWithPayload(ID705)
                    self._adaptor.addChild(root_0, ID705_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "remote_procedure_id"

    class operator_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operator_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "operator_id"
    # sdl92.g:1136:1: operator_id : ID ;
    def operator_id(self, ):

        retval = self.operator_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID706 = None

        ID706_tree = None

        try:
            try:
                # sdl92.g:1136:17: ( ID )
                # sdl92.g:1136:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID706=self.match(self.input, ID, self.FOLLOW_ID_in_operator_id13375)
                if self._state.backtracking == 0:

                    ID706_tree = self._adaptor.createWithPayload(ID706)
                    self._adaptor.addChild(root_0, ID706_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operator_id"

    class synonym_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.synonym_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "synonym_id"
    # sdl92.g:1137:1: synonym_id : ID ;
    def synonym_id(self, ):

        retval = self.synonym_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID707 = None

        ID707_tree = None

        try:
            try:
                # sdl92.g:1137:17: ( ID )
                # sdl92.g:1137:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID707=self.match(self.input, ID, self.FOLLOW_ID_in_synonym_id13393)
                if self._state.backtracking == 0:

                    ID707_tree = self._adaptor.createWithPayload(ID707)
                    self._adaptor.addChild(root_0, ID707_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "synonym_id"

    class external_synonym_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.external_synonym_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "external_synonym_id"
    # sdl92.g:1138:1: external_synonym_id : ID ;
    def external_synonym_id(self, ):

        retval = self.external_synonym_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID708 = None

        ID708_tree = None

        try:
            try:
                # sdl92.g:1139:17: ( ID )
                # sdl92.g:1139:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID708=self.match(self.input, ID, self.FOLLOW_ID_in_external_synonym_id13422)
                if self._state.backtracking == 0:

                    ID708_tree = self._adaptor.createWithPayload(ID708)
                    self._adaptor.addChild(root_0, ID708_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "external_synonym_id"

    class remote_variable_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.remote_variable_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "remote_variable_id"
    # sdl92.g:1140:1: remote_variable_id : ID ;
    def remote_variable_id(self, ):

        retval = self.remote_variable_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID709 = None

        ID709_tree = None

        try:
            try:
                # sdl92.g:1141:17: ( ID )
                # sdl92.g:1141:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID709=self.match(self.input, ID, self.FOLLOW_ID_in_remote_variable_id13451)
                if self._state.backtracking == 0:

                    ID709_tree = self._adaptor.createWithPayload(ID709)
                    self._adaptor.addChild(root_0, ID709_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "remote_variable_id"

    class view_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.view_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "view_id"
    # sdl92.g:1142:1: view_id : ID ;
    def view_id(self, ):

        retval = self.view_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID710 = None

        ID710_tree = None

        try:
            try:
                # sdl92.g:1142:17: ( ID )
                # sdl92.g:1142:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID710=self.match(self.input, ID, self.FOLLOW_ID_in_view_id13472)
                if self._state.backtracking == 0:

                    ID710_tree = self._adaptor.createWithPayload(ID710)
                    self._adaptor.addChild(root_0, ID710_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "view_id"

    class sort_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.sort_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "sort_id"
    # sdl92.g:1143:1: sort_id : ID ;
    def sort_id(self, ):

        retval = self.sort_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID711 = None

        ID711_tree = None

        try:
            try:
                # sdl92.g:1143:17: ( ID )
                # sdl92.g:1143:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID711=self.match(self.input, ID, self.FOLLOW_ID_in_sort_id13493)
                if self._state.backtracking == 0:

                    ID711_tree = self._adaptor.createWithPayload(ID711)
                    self._adaptor.addChild(root_0, ID711_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "sort_id"

    class syntype_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.syntype_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "syntype_id"
    # sdl92.g:1144:1: syntype_id : ID ;
    def syntype_id(self, ):

        retval = self.syntype_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID712 = None

        ID712_tree = None

        try:
            try:
                # sdl92.g:1144:17: ( ID )
                # sdl92.g:1144:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID712=self.match(self.input, ID, self.FOLLOW_ID_in_syntype_id13511)
                if self._state.backtracking == 0:

                    ID712_tree = self._adaptor.createWithPayload(ID712)
                    self._adaptor.addChild(root_0, ID712_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "syntype_id"

    class stimulus_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.stimulus_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "stimulus_id"
    # sdl92.g:1145:1: stimulus_id : ID ;
    def stimulus_id(self, ):

        retval = self.stimulus_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID713 = None

        ID713_tree = None

        try:
            try:
                # sdl92.g:1145:17: ( ID )
                # sdl92.g:1145:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID713=self.match(self.input, ID, self.FOLLOW_ID_in_stimulus_id13528)
                if self._state.backtracking == 0:

                    ID713_tree = self._adaptor.createWithPayload(ID713)
                    self._adaptor.addChild(root_0, ID713_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "stimulus_id"

    class pid_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.pid_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "pid_expression"
    # sdl92.g:1180:1: pid_expression : ( S E L F | P A R E N T | O F F S P R I N G | S E N D E R );
    def pid_expression(self, ):

        retval = self.pid_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        S714 = None
        E715 = None
        L716 = None
        F717 = None
        P718 = None
        A719 = None
        R720 = None
        E721 = None
        N722 = None
        T723 = None
        O724 = None
        F725 = None
        F726 = None
        S727 = None
        P728 = None
        R729 = None
        I730 = None
        N731 = None
        G732 = None
        S733 = None
        E734 = None
        N735 = None
        D736 = None
        E737 = None
        R738 = None

        S714_tree = None
        E715_tree = None
        L716_tree = None
        F717_tree = None
        P718_tree = None
        A719_tree = None
        R720_tree = None
        E721_tree = None
        N722_tree = None
        T723_tree = None
        O724_tree = None
        F725_tree = None
        F726_tree = None
        S727_tree = None
        P728_tree = None
        R729_tree = None
        I730_tree = None
        N731_tree = None
        G732_tree = None
        S733_tree = None
        E734_tree = None
        N735_tree = None
        D736_tree = None
        E737_tree = None
        R738_tree = None

        try:
            try:
                # sdl92.g:1181:17: ( S E L F | P A R E N T | O F F S P R I N G | S E N D E R )
                alt184 = 4
                LA184 = self.input.LA(1)
                if LA184 == S:
                    LA184_1 = self.input.LA(2)

                    if (LA184_1 == E) :
                        LA184_4 = self.input.LA(3)

                        if (LA184_4 == L) :
                            alt184 = 1
                        elif (LA184_4 == N) :
                            alt184 = 4
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 184, 4, self.input)

                            raise nvae

                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 184, 1, self.input)

                        raise nvae

                elif LA184 == P:
                    alt184 = 2
                elif LA184 == O:
                    alt184 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 184, 0, self.input)

                    raise nvae

                if alt184 == 1:
                    # sdl92.g:1181:25: S E L F
                    pass 
                    root_0 = self._adaptor.nil()

                    S714=self.match(self.input, S, self.FOLLOW_S_in_pid_expression14562)
                    if self._state.backtracking == 0:

                        S714_tree = self._adaptor.createWithPayload(S714)
                        self._adaptor.addChild(root_0, S714_tree)

                    E715=self.match(self.input, E, self.FOLLOW_E_in_pid_expression14564)
                    if self._state.backtracking == 0:

                        E715_tree = self._adaptor.createWithPayload(E715)
                        self._adaptor.addChild(root_0, E715_tree)

                    L716=self.match(self.input, L, self.FOLLOW_L_in_pid_expression14566)
                    if self._state.backtracking == 0:

                        L716_tree = self._adaptor.createWithPayload(L716)
                        self._adaptor.addChild(root_0, L716_tree)

                    F717=self.match(self.input, F, self.FOLLOW_F_in_pid_expression14568)
                    if self._state.backtracking == 0:

                        F717_tree = self._adaptor.createWithPayload(F717)
                        self._adaptor.addChild(root_0, F717_tree)



                elif alt184 == 2:
                    # sdl92.g:1182:25: P A R E N T
                    pass 
                    root_0 = self._adaptor.nil()

                    P718=self.match(self.input, P, self.FOLLOW_P_in_pid_expression14594)
                    if self._state.backtracking == 0:

                        P718_tree = self._adaptor.createWithPayload(P718)
                        self._adaptor.addChild(root_0, P718_tree)

                    A719=self.match(self.input, A, self.FOLLOW_A_in_pid_expression14596)
                    if self._state.backtracking == 0:

                        A719_tree = self._adaptor.createWithPayload(A719)
                        self._adaptor.addChild(root_0, A719_tree)

                    R720=self.match(self.input, R, self.FOLLOW_R_in_pid_expression14598)
                    if self._state.backtracking == 0:

                        R720_tree = self._adaptor.createWithPayload(R720)
                        self._adaptor.addChild(root_0, R720_tree)

                    E721=self.match(self.input, E, self.FOLLOW_E_in_pid_expression14600)
                    if self._state.backtracking == 0:

                        E721_tree = self._adaptor.createWithPayload(E721)
                        self._adaptor.addChild(root_0, E721_tree)

                    N722=self.match(self.input, N, self.FOLLOW_N_in_pid_expression14602)
                    if self._state.backtracking == 0:

                        N722_tree = self._adaptor.createWithPayload(N722)
                        self._adaptor.addChild(root_0, N722_tree)

                    T723=self.match(self.input, T, self.FOLLOW_T_in_pid_expression14604)
                    if self._state.backtracking == 0:

                        T723_tree = self._adaptor.createWithPayload(T723)
                        self._adaptor.addChild(root_0, T723_tree)



                elif alt184 == 3:
                    # sdl92.g:1183:25: O F F S P R I N G
                    pass 
                    root_0 = self._adaptor.nil()

                    O724=self.match(self.input, O, self.FOLLOW_O_in_pid_expression14630)
                    if self._state.backtracking == 0:

                        O724_tree = self._adaptor.createWithPayload(O724)
                        self._adaptor.addChild(root_0, O724_tree)

                    F725=self.match(self.input, F, self.FOLLOW_F_in_pid_expression14632)
                    if self._state.backtracking == 0:

                        F725_tree = self._adaptor.createWithPayload(F725)
                        self._adaptor.addChild(root_0, F725_tree)

                    F726=self.match(self.input, F, self.FOLLOW_F_in_pid_expression14634)
                    if self._state.backtracking == 0:

                        F726_tree = self._adaptor.createWithPayload(F726)
                        self._adaptor.addChild(root_0, F726_tree)

                    S727=self.match(self.input, S, self.FOLLOW_S_in_pid_expression14636)
                    if self._state.backtracking == 0:

                        S727_tree = self._adaptor.createWithPayload(S727)
                        self._adaptor.addChild(root_0, S727_tree)

                    P728=self.match(self.input, P, self.FOLLOW_P_in_pid_expression14638)
                    if self._state.backtracking == 0:

                        P728_tree = self._adaptor.createWithPayload(P728)
                        self._adaptor.addChild(root_0, P728_tree)

                    R729=self.match(self.input, R, self.FOLLOW_R_in_pid_expression14640)
                    if self._state.backtracking == 0:

                        R729_tree = self._adaptor.createWithPayload(R729)
                        self._adaptor.addChild(root_0, R729_tree)

                    I730=self.match(self.input, I, self.FOLLOW_I_in_pid_expression14642)
                    if self._state.backtracking == 0:

                        I730_tree = self._adaptor.createWithPayload(I730)
                        self._adaptor.addChild(root_0, I730_tree)

                    N731=self.match(self.input, N, self.FOLLOW_N_in_pid_expression14644)
                    if self._state.backtracking == 0:

                        N731_tree = self._adaptor.createWithPayload(N731)
                        self._adaptor.addChild(root_0, N731_tree)

                    G732=self.match(self.input, G, self.FOLLOW_G_in_pid_expression14646)
                    if self._state.backtracking == 0:

                        G732_tree = self._adaptor.createWithPayload(G732)
                        self._adaptor.addChild(root_0, G732_tree)



                elif alt184 == 4:
                    # sdl92.g:1184:25: S E N D E R
                    pass 
                    root_0 = self._adaptor.nil()

                    S733=self.match(self.input, S, self.FOLLOW_S_in_pid_expression14672)
                    if self._state.backtracking == 0:

                        S733_tree = self._adaptor.createWithPayload(S733)
                        self._adaptor.addChild(root_0, S733_tree)

                    E734=self.match(self.input, E, self.FOLLOW_E_in_pid_expression14674)
                    if self._state.backtracking == 0:

                        E734_tree = self._adaptor.createWithPayload(E734)
                        self._adaptor.addChild(root_0, E734_tree)

                    N735=self.match(self.input, N, self.FOLLOW_N_in_pid_expression14676)
                    if self._state.backtracking == 0:

                        N735_tree = self._adaptor.createWithPayload(N735)
                        self._adaptor.addChild(root_0, N735_tree)

                    D736=self.match(self.input, D, self.FOLLOW_D_in_pid_expression14678)
                    if self._state.backtracking == 0:

                        D736_tree = self._adaptor.createWithPayload(D736)
                        self._adaptor.addChild(root_0, D736_tree)

                    E737=self.match(self.input, E, self.FOLLOW_E_in_pid_expression14680)
                    if self._state.backtracking == 0:

                        E737_tree = self._adaptor.createWithPayload(E737)
                        self._adaptor.addChild(root_0, E737_tree)

                    R738=self.match(self.input, R, self.FOLLOW_R_in_pid_expression14682)
                    if self._state.backtracking == 0:

                        R738_tree = self._adaptor.createWithPayload(R738)
                        self._adaptor.addChild(root_0, R738_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "pid_expression"

    class now_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.now_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "now_expression"
    # sdl92.g:1185:1: now_expression : N O W ;
    def now_expression(self, ):

        retval = self.now_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        N739 = None
        O740 = None
        W741 = None

        N739_tree = None
        O740_tree = None
        W741_tree = None

        try:
            try:
                # sdl92.g:1185:17: ( N O W )
                # sdl92.g:1185:25: N O W
                pass 
                root_0 = self._adaptor.nil()

                N739=self.match(self.input, N, self.FOLLOW_N_in_now_expression14696)
                if self._state.backtracking == 0:

                    N739_tree = self._adaptor.createWithPayload(N739)
                    self._adaptor.addChild(root_0, N739_tree)

                O740=self.match(self.input, O, self.FOLLOW_O_in_now_expression14698)
                if self._state.backtracking == 0:

                    O740_tree = self._adaptor.createWithPayload(O740)
                    self._adaptor.addChild(root_0, O740_tree)

                W741=self.match(self.input, W, self.FOLLOW_W_in_now_expression14700)
                if self._state.backtracking == 0:

                    W741_tree = self._adaptor.createWithPayload(W741)
                    self._adaptor.addChild(root_0, W741_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "now_expression"

    # $ANTLR start "synpred24_sdl92"
    def synpred24_sdl92_fragment(self, ):
        # sdl92.g:220:18: ( text_area )
        # sdl92.g:220:18: text_area
        pass 
        self._state.following.append(self.FOLLOW_text_area_in_synpred24_sdl922224)
        self.text_area()

        self._state.following.pop()


    # $ANTLR end "synpred24_sdl92"



    # $ANTLR start "synpred25_sdl92"
    def synpred25_sdl92_fragment(self, ):
        # sdl92.g:220:30: ( procedure )
        # sdl92.g:220:30: procedure
        pass 
        self._state.following.append(self.FOLLOW_procedure_in_synpred25_sdl922228)
        self.procedure()

        self._state.following.pop()


    # $ANTLR end "synpred25_sdl92"



    # $ANTLR start "synpred26_sdl92"
    def synpred26_sdl92_fragment(self, ):
        # sdl92.g:220:42: ( composite_state )
        # sdl92.g:220:42: composite_state
        pass 
        self._state.following.append(self.FOLLOW_composite_state_in_synpred26_sdl922232)
        self.composite_state()

        self._state.following.pop()


    # $ANTLR end "synpred26_sdl92"



    # $ANTLR start "synpred27_sdl92"
    def synpred27_sdl92_fragment(self, ):
        # sdl92.g:221:17: ( processBody )
        # sdl92.g:221:17: processBody
        pass 
        self._state.following.append(self.FOLLOW_processBody_in_synpred27_sdl922252)
        self.processBody()

        self._state.following.pop()


    # $ANTLR end "synpred27_sdl92"



    # $ANTLR start "synpred31_sdl92"
    def synpred31_sdl92_fragment(self, ):
        # sdl92.g:233:18: ( text_area )
        # sdl92.g:233:18: text_area
        pass 
        self._state.following.append(self.FOLLOW_text_area_in_synpred31_sdl922417)
        self.text_area()

        self._state.following.pop()


    # $ANTLR end "synpred31_sdl92"



    # $ANTLR start "synpred32_sdl92"
    def synpred32_sdl92_fragment(self, ):
        # sdl92.g:233:30: ( procedure )
        # sdl92.g:233:30: procedure
        pass 
        self._state.following.append(self.FOLLOW_procedure_in_synpred32_sdl922421)
        self.procedure()

        self._state.following.pop()


    # $ANTLR end "synpred32_sdl92"



    # $ANTLR start "synpred33_sdl92"
    def synpred33_sdl92_fragment(self, ):
        # sdl92.g:234:19: ( processBody )
        # sdl92.g:234:19: processBody
        pass 
        self._state.following.append(self.FOLLOW_processBody_in_synpred33_sdl922443)
        self.processBody()

        self._state.following.pop()


    # $ANTLR end "synpred33_sdl92"



    # $ANTLR start "synpred40_sdl92"
    def synpred40_sdl92_fragment(self, ):
        # sdl92.g:257:17: ( content )
        # sdl92.g:257:17: content
        pass 
        self._state.following.append(self.FOLLOW_content_in_synpred40_sdl922749)
        self.content()

        self._state.following.pop()


    # $ANTLR end "synpred40_sdl92"



    # $ANTLR start "synpred84_sdl92"
    def synpred84_sdl92_fragment(self, ):
        # sdl92.g:418:18: ( text_area )
        # sdl92.g:418:18: text_area
        pass 
        self._state.following.append(self.FOLLOW_text_area_in_synpred84_sdl924908)
        self.text_area()

        self._state.following.pop()


    # $ANTLR end "synpred84_sdl92"



    # $ANTLR start "synpred85_sdl92"
    def synpred85_sdl92_fragment(self, ):
        # sdl92.g:418:30: ( procedure )
        # sdl92.g:418:30: procedure
        pass 
        self._state.following.append(self.FOLLOW_procedure_in_synpred85_sdl924912)
        self.procedure()

        self._state.following.pop()


    # $ANTLR end "synpred85_sdl92"



    # $ANTLR start "synpred86_sdl92"
    def synpred86_sdl92_fragment(self, ):
        # sdl92.g:418:42: ( composite_state )
        # sdl92.g:418:42: composite_state
        pass 
        self._state.following.append(self.FOLLOW_composite_state_in_synpred86_sdl924916)
        self.composite_state()

        self._state.following.pop()


    # $ANTLR end "synpred86_sdl92"



    # $ANTLR start "synpred108_sdl92"
    def synpred108_sdl92_fragment(self, ):
        # sdl92.g:515:17: ( enabling_condition )
        # sdl92.g:515:17: enabling_condition
        pass 
        self._state.following.append(self.FOLLOW_enabling_condition_in_synpred108_sdl925852)
        self.enabling_condition()

        self._state.following.pop()


    # $ANTLR end "synpred108_sdl92"



    # $ANTLR start "synpred115_sdl92"
    def synpred115_sdl92_fragment(self, ):
        # sdl92.g:539:25: ( label )
        # sdl92.g:539:25: label
        pass 
        self._state.following.append(self.FOLLOW_label_in_synpred115_sdl926108)
        self.label()

        self._state.following.pop()


    # $ANTLR end "synpred115_sdl92"



    # $ANTLR start "synpred139_sdl92"
    def synpred139_sdl92_fragment(self, ):
        # sdl92.g:624:17: ( expression )
        # sdl92.g:624:17: expression
        pass 
        self._state.following.append(self.FOLLOW_expression_in_synpred139_sdl927128)
        self.expression()

        self._state.following.pop()


    # $ANTLR end "synpred139_sdl92"



    # $ANTLR start "synpred142_sdl92"
    def synpred142_sdl92_fragment(self, ):
        # sdl92.g:632:17: ( answer_part )
        # sdl92.g:632:17: answer_part
        pass 
        self._state.following.append(self.FOLLOW_answer_part_in_synpred142_sdl927233)
        self.answer_part()

        self._state.following.pop()


    # $ANTLR end "synpred142_sdl92"



    # $ANTLR start "synpred147_sdl92"
    def synpred147_sdl92_fragment(self, ):
        # sdl92.g:647:17: ( range_condition )
        # sdl92.g:647:17: range_condition
        pass 
        self._state.following.append(self.FOLLOW_range_condition_in_synpred147_sdl927451)
        self.range_condition()

        self._state.following.pop()


    # $ANTLR end "synpred147_sdl92"



    # $ANTLR start "synpred151_sdl92"
    def synpred151_sdl92_fragment(self, ):
        # sdl92.g:659:17: ( expression )
        # sdl92.g:659:17: expression
        pass 
        self._state.following.append(self.FOLLOW_expression_in_synpred151_sdl927588)
        self.expression()

        self._state.following.pop()


    # $ANTLR end "synpred151_sdl92"



    # $ANTLR start "synpred152_sdl92"
    def synpred152_sdl92_fragment(self, ):
        # sdl92.g:661:19: ( informal_text )
        # sdl92.g:661:19: informal_text
        pass 
        self._state.following.append(self.FOLLOW_informal_text_in_synpred152_sdl927629)
        self.informal_text()

        self._state.following.pop()


    # $ANTLR end "synpred152_sdl92"



    # $ANTLR start "synpred182_sdl92"
    def synpred182_sdl92_fragment(self, ):
        # sdl92.g:783:18: ( COMMA b= ground_expression )
        # sdl92.g:783:18: COMMA b= ground_expression
        pass 
        self.match(self.input, COMMA, self.FOLLOW_COMMA_in_synpred182_sdl929085)
        self._state.following.append(self.FOLLOW_ground_expression_in_synpred182_sdl929089)
        b = self.ground_expression()

        self._state.following.pop()


    # $ANTLR end "synpred182_sdl92"



    # $ANTLR start "synpred187_sdl92"
    def synpred187_sdl92_fragment(self, ):
        # sdl92.g:805:39: ( IMPLIES binary_expression_0 )
        # sdl92.g:805:39: IMPLIES binary_expression_0
        pass 
        self.match(self.input, IMPLIES, self.FOLLOW_IMPLIES_in_synpred187_sdl929366)
        self._state.following.append(self.FOLLOW_binary_expression_0_in_synpred187_sdl929369)
        self.binary_expression_0()

        self._state.following.pop()


    # $ANTLR end "synpred187_sdl92"



    # $ANTLR start "synpred190_sdl92"
    def synpred190_sdl92_fragment(self, ):
        # sdl92.g:807:38: ( ( ( OR ( ELSE )? ) | XOR ) binary_expression_1 )
        # sdl92.g:807:38: ( ( OR ( ELSE )? ) | XOR ) binary_expression_1
        pass 
        # sdl92.g:807:38: ( ( OR ( ELSE )? ) | XOR )
        alt201 = 2
        LA201_0 = self.input.LA(1)

        if (LA201_0 == OR) :
            alt201 = 1
        elif (LA201_0 == XOR) :
            alt201 = 2
        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            nvae = NoViableAltException("", 201, 0, self.input)

            raise nvae

        if alt201 == 1:
            # sdl92.g:807:40: ( OR ( ELSE )? )
            pass 
            # sdl92.g:807:40: ( OR ( ELSE )? )
            # sdl92.g:807:41: OR ( ELSE )?
            pass 
            self.match(self.input, OR, self.FOLLOW_OR_in_synpred190_sdl929398)
            # sdl92.g:807:45: ( ELSE )?
            alt200 = 2
            LA200_0 = self.input.LA(1)

            if (LA200_0 == ELSE) :
                alt200 = 1
            if alt200 == 1:
                # sdl92.g:0:0: ELSE
                pass 
                self.match(self.input, ELSE, self.FOLLOW_ELSE_in_synpred190_sdl929401)








        elif alt201 == 2:
            # sdl92.g:807:54: XOR
            pass 
            self.match(self.input, XOR, self.FOLLOW_XOR_in_synpred190_sdl929407)



        self._state.following.append(self.FOLLOW_binary_expression_1_in_synpred190_sdl929412)
        self.binary_expression_1()

        self._state.following.pop()


    # $ANTLR end "synpred190_sdl92"



    # $ANTLR start "synpred192_sdl92"
    def synpred192_sdl92_fragment(self, ):
        # sdl92.g:809:39: ( AND ( THEN )? binary_expression_2 )
        # sdl92.g:809:39: AND ( THEN )? binary_expression_2
        pass 
        self.match(self.input, AND, self.FOLLOW_AND_in_synpred192_sdl929439)
        # sdl92.g:809:44: ( THEN )?
        alt202 = 2
        LA202_0 = self.input.LA(1)

        if (LA202_0 == THEN) :
            alt202 = 1
        if alt202 == 1:
            # sdl92.g:0:0: THEN
            pass 
            self.match(self.input, THEN, self.FOLLOW_THEN_in_synpred192_sdl929442)



        self._state.following.append(self.FOLLOW_binary_expression_2_in_synpred192_sdl929445)
        self.binary_expression_2()

        self._state.following.pop()


    # $ANTLR end "synpred192_sdl92"



    # $ANTLR start "synpred199_sdl92"
    def synpred199_sdl92_fragment(self, ):
        # sdl92.g:811:38: ( ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3 )
        # sdl92.g:811:38: ( EQ | NEQ | GT | GE | LT | LE | IN ) binary_expression_3
        pass 
        if self.input.LA(1) == IN or (EQ <= self.input.LA(1) <= GE):
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_binary_expression_3_in_synpred199_sdl929508)
        self.binary_expression_3()

        self._state.following.pop()


    # $ANTLR end "synpred199_sdl92"



    # $ANTLR start "synpred202_sdl92"
    def synpred202_sdl92_fragment(self, ):
        # sdl92.g:813:38: ( ( PLUS | DASH | APPEND ) binary_expression_4 )
        # sdl92.g:813:38: ( PLUS | DASH | APPEND ) binary_expression_4
        pass 
        if (PLUS <= self.input.LA(1) <= APPEND):
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_binary_expression_4_in_synpred202_sdl929551)
        self.binary_expression_4()

        self._state.following.pop()


    # $ANTLR end "synpred202_sdl92"



    # $ANTLR start "synpred206_sdl92"
    def synpred206_sdl92_fragment(self, ):
        # sdl92.g:815:35: ( ( ASTERISK | DIV | MOD | REM ) unary_expression )
        # sdl92.g:815:35: ( ASTERISK | DIV | MOD | REM ) unary_expression
        pass 
        if self.input.LA(1) == ASTERISK or (DIV <= self.input.LA(1) <= REM):
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_unary_expression_in_synpred206_sdl929599)
        self.unary_expression()

        self._state.following.pop()


    # $ANTLR end "synpred206_sdl92"



    # $ANTLR start "synpred221_sdl92"
    def synpred221_sdl92_fragment(self, ):
        # sdl92.g:839:17: ( ID ':' expression )
        # sdl92.g:839:17: ID ':' expression
        pass 
        self.match(self.input, ID, self.FOLLOW_ID_in_synpred221_sdl9210003)
        self.match(self.input, 212, self.FOLLOW_212_in_synpred221_sdl9210005)
        self._state.following.append(self.FOLLOW_expression_in_synpred221_sdl9210007)
        self.expression()

        self._state.following.pop()


    # $ANTLR end "synpred221_sdl92"



    # $ANTLR start "synpred222_sdl92"
    def synpred222_sdl92_fragment(self, ):
        # sdl92.g:840:20: ( primary_params )
        # sdl92.g:840:20: primary_params
        pass 
        self._state.following.append(self.FOLLOW_primary_params_in_synpred222_sdl9210047)
        self.primary_params()

        self._state.following.pop()


    # $ANTLR end "synpred222_sdl92"



    # $ANTLR start "synpred223_sdl92"
    def synpred223_sdl92_fragment(self, ):
        # sdl92.g:840:17: ( ID ( primary_params )+ )
        # sdl92.g:840:17: ID ( primary_params )+
        pass 
        self.match(self.input, ID, self.FOLLOW_ID_in_synpred223_sdl9210045)
        # sdl92.g:840:20: ( primary_params )+
        cnt203 = 0
        while True: #loop203
            alt203 = 2
            LA203_0 = self.input.LA(1)

            if (LA203_0 == L_PAREN or LA203_0 == 213) :
                alt203 = 1


            if alt203 == 1:
                # sdl92.g:0:0: primary_params
                pass 
                self._state.following.append(self.FOLLOW_primary_params_in_synpred223_sdl9210047)
                self.primary_params()

                self._state.following.pop()


            else:
                if cnt203 >= 1:
                    break #loop203

                if self._state.backtracking > 0:
                    raise BacktrackingFailed

                eee = EarlyExitException(203, self.input)
                raise eee

            cnt203 += 1


    # $ANTLR end "synpred223_sdl92"



    # $ANTLR start "synpred224_sdl92"
    def synpred224_sdl92_fragment(self, ):
        # sdl92.g:841:17: ( ID )
        # sdl92.g:841:17: ID
        pass 
        self.match(self.input, ID, self.FOLLOW_ID_in_synpred224_sdl9210086)


    # $ANTLR end "synpred224_sdl92"



    # $ANTLR start "synpred225_sdl92"
    def synpred225_sdl92_fragment(self, ):
        # sdl92.g:842:17: ( '{' '}' )
        # sdl92.g:842:17: '{' '}'
        pass 
        self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_synpred225_sdl9210137)
        self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_synpred225_sdl9210139)


    # $ANTLR end "synpred225_sdl92"



    # $ANTLR start "synpred226_sdl92"
    def synpred226_sdl92_fragment(self, ):
        # sdl92.g:843:17: ( '{' MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT '}' )
        # sdl92.g:843:17: '{' MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT '}'
        pass 
        self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_synpred226_sdl9210183)
        self.match(self.input, MANTISSA, self.FOLLOW_MANTISSA_in_synpred226_sdl9210201)
        mant=self.match(self.input, INT, self.FOLLOW_INT_in_synpred226_sdl9210205)
        self.match(self.input, COMMA, self.FOLLOW_COMMA_in_synpred226_sdl9210207)
        self.match(self.input, BASE, self.FOLLOW_BASE_in_synpred226_sdl9210225)
        bas=self.match(self.input, INT, self.FOLLOW_INT_in_synpred226_sdl9210229)
        self.match(self.input, COMMA, self.FOLLOW_COMMA_in_synpred226_sdl9210231)
        self.match(self.input, EXPONENT, self.FOLLOW_EXPONENT_in_synpred226_sdl9210249)
        exp=self.match(self.input, INT, self.FOLLOW_INT_in_synpred226_sdl9210253)
        self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_synpred226_sdl9210271)


    # $ANTLR end "synpred226_sdl92"



    # $ANTLR start "synpred228_sdl92"
    def synpred228_sdl92_fragment(self, ):
        # sdl92.g:848:17: ( '{' named_value ( COMMA named_value )* '}' )
        # sdl92.g:848:17: '{' named_value ( COMMA named_value )* '}'
        pass 
        self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_synpred228_sdl9210328)
        self._state.following.append(self.FOLLOW_named_value_in_synpred228_sdl9210346)
        self.named_value()

        self._state.following.pop()
        # sdl92.g:849:29: ( COMMA named_value )*
        while True: #loop204
            alt204 = 2
            LA204_0 = self.input.LA(1)

            if (LA204_0 == COMMA) :
                alt204 = 1


            if alt204 == 1:
                # sdl92.g:849:30: COMMA named_value
                pass 
                self.match(self.input, COMMA, self.FOLLOW_COMMA_in_synpred228_sdl9210349)
                self._state.following.append(self.FOLLOW_named_value_in_synpred228_sdl9210351)
                self.named_value()

                self._state.following.pop()


            else:
                break #loop204
        self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_synpred228_sdl9210371)


    # $ANTLR end "synpred228_sdl92"




    # Delegated rules

    def synpred202_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred202_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred190_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred190_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred85_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred85_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred27_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred27_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred32_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred32_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred108_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred108_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred84_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred84_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred31_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred31_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred182_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred182_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred206_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred206_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred187_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred187_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred223_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred223_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred147_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred147_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred199_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred199_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred25_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred25_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred24_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred24_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred26_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred26_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred139_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred139_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred142_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred142_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred152_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred152_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred224_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred224_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred192_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred192_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred115_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred115_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred228_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred228_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred225_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred225_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred221_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred221_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred86_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred86_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred226_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred226_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred33_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred33_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred40_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred40_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred222_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred222_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred151_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred151_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success



    # lookup tables for DFA #19

    DFA19_eot = DFA.unpack(
        u"\12\uffff"
        )

    DFA19_eof = DFA.unpack(
        u"\12\uffff"
        )

    DFA19_min = DFA.unpack(
        u"\1\111\1\u0095\1\uffff\1\21\1\173\1\uffff\1\u0088\1\173\1\u0087"
        u"\1\21"
        )

    DFA19_max = DFA.unpack(
        u"\1\u00d9\1\u0095\1\uffff\1\u00d9\1\173\1\uffff\1\u0088\1\173\1"
        u"\u0087\1\u00d9"
        )

    DFA19_accept = DFA.unpack(
        u"\2\uffff\1\2\2\uffff\1\1\4\uffff"
        )

    DFA19_special = DFA.unpack(
        u"\12\uffff"
        )

            
    DFA19_transition = [
        DFA.unpack(u"\1\1\u008f\uffff\1\2"),
        DFA.unpack(u"\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\2\146\uffff\1\5\5\uffff\1\2\7\uffff\1\4\122\uffff"
        u"\1\2"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\2\146\uffff\1\5\5\uffff\1\2\132\uffff\1\2")
    ]

    # class definition for DFA #19

    class DFA19(DFA):
        pass


    # lookup tables for DFA #30

    DFA30_eot = DFA.unpack(
        u"\12\uffff"
        )

    DFA30_eof = DFA.unpack(
        u"\1\2\11\uffff"
        )

    DFA30_min = DFA.unpack(
        u"\1\27\1\7\10\uffff"
        )

    DFA30_max = DFA.unpack(
        u"\1\u00d9\1\174\10\uffff"
        )

    DFA30_accept = DFA.unpack(
        u"\2\uffff\1\10\1\1\1\2\1\3\1\4\1\5\1\6\1\7"
        )

    DFA30_special = DFA.unpack(
        u"\12\uffff"
        )

            
    DFA30_transition = [
        DFA.unpack(u"\1\10\22\uffff\1\4\16\uffff\1\7\14\uffff\1\3\26\uffff"
        u"\1\11\1\uffff\1\6\10\uffff\1\5\160\uffff\1\1"),
        DFA.unpack(u"\1\3\11\uffff\1\3\1\uffff\1\3\4\uffff\1\3\5\uffff\1"
        u"\2\23\uffff\1\3\2\uffff\2\3\3\uffff\1\3\3\uffff\1\3\7\uffff\2\3"
        u"\1\uffff\2\3\3\uffff\1\3\10\uffff\1\3\2\uffff\1\3\6\uffff\1\3\2"
        u"\uffff\1\3\27\uffff\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #30

    class DFA30(DFA):
        pass


    # lookup tables for DFA #37

    DFA37_eot = DFA.unpack(
        u"\33\uffff"
        )

    DFA37_eof = DFA.unpack(
        u"\3\uffff\1\10\27\uffff"
        )

    DFA37_min = DFA.unpack(
        u"\1\21\1\7\1\133\1\34\1\u00ad\1\u0086\1\176\2\uffff\1\u00ae\1\173"
        u"\1\54\1\u0088\1\133\1\173\1\u00da\1\u0087\1\21\1\u0088\1\u0086"
        u"\1\173\1\u0088\1\173\1\u0087\1\u00da\1\21\1\u00ac"
        )

    DFA37_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\1\133\1\u0095\1\u00ad\1\u0086\1\176\2\uffff\1"
        u"\u00ae\1\173\1\54\1\u0088\1\133\1\173\1\u00da\1\u0087\1\21\1\u0088"
        u"\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA37_accept = DFA.unpack(
        u"\7\uffff\1\1\1\2\22\uffff"
        )

    DFA37_special = DFA.unpack(
        u"\33\uffff"
        )

            
    DFA37_transition = [
        DFA.unpack(u"\1\2\154\uffff\1\3\132\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\10\170\uffff\1\7"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\2"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\2\u00c7\uffff\1\32"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #37

    class DFA37(DFA):
        pass


    # lookup tables for DFA #43

    DFA43_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA43_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA43_min = DFA.unpack(
        u"\1\24\1\7\2\uffff\1\u0086\1\u00ad\1\173\1\u00ae\1\u0088\1\54\1"
        u"\173\1\133\1\u0087\1\u00da\1\u0088\1\24\1\u0086\1\173\1\u0088\1"
        u"\173\1\u0087\1\u00da\1\24\1\u00ac"
        )

    DFA43_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u0086\1\u00ad\1\173\1\u00ae\1\u0088"
        u"\1\54\1\173\1\133\1\u0087\1\u00da\1\u0088\1\174\1\u0086\1\173\1"
        u"\u0088\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA43_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA43_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA43_transition = [
        DFA.unpack(u"\1\3\102\uffff\1\3\41\uffff\2\3\1\uffff\1\2\134\uffff"
        u"\1\1"),
        DFA.unpack(u"\1\4\11\uffff\1\4\1\uffff\1\4\4\uffff\1\4\31\uffff"
        u"\1\4\2\uffff\2\4\3\uffff\1\4\3\uffff\1\4\7\uffff\2\4\1\uffff\2"
        u"\4\3\uffff\1\4\10\uffff\1\4\2\uffff\1\4\6\uffff\1\4\2\uffff\1\4"
        u"\27\uffff\1\4\57\uffff\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\3\102\uffff\1\3\44\uffff\1\2"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\102\uffff\1\3\44\uffff\1\2\134\uffff\1\27"),
        DFA.unpack(u"\1\5")
    ]

    # class definition for DFA #43

    class DFA43(DFA):
        pass


    # lookup tables for DFA #44

    DFA44_eot = DFA.unpack(
        u"\31\uffff"
        )

    DFA44_eof = DFA.unpack(
        u"\1\1\30\uffff"
        )

    DFA44_min = DFA.unpack(
        u"\1\24\1\uffff\1\7\2\uffff\1\u0086\1\u00ad\1\173\1\u00ae\1\u0088"
        u"\1\54\1\173\1\133\1\u0087\1\u00da\1\u0088\1\24\1\u0086\1\173\1"
        u"\u0088\1\173\1\u0087\1\u00da\1\24\1\u00ac"
        )

    DFA44_max = DFA.unpack(
        u"\1\u00d9\1\uffff\1\u00ac\2\uffff\1\u0086\1\u00ad\1\173\1\u00ae"
        u"\1\u0088\1\54\1\173\1\133\1\u0087\1\u00da\1\u0088\1\127\1\u0086"
        u"\1\173\1\u0088\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA44_accept = DFA.unpack(
        u"\1\uffff\1\3\1\uffff\1\1\1\2\24\uffff"
        )

    DFA44_special = DFA.unpack(
        u"\31\uffff"
        )

            
    DFA44_transition = [
        DFA.unpack(u"\1\4\102\uffff\1\3\41\uffff\2\1\136\uffff\1\2"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\6"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\4\102\uffff\1\3"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\4\102\uffff\1\3\u0081\uffff\1\30"),
        DFA.unpack(u"\1\6")
    ]

    # class definition for DFA #44

    class DFA44(DFA):
        pass


    # lookup tables for DFA #48

    DFA48_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA48_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA48_min = DFA.unpack(
        u"\1\6\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1\133"
        u"\1\173\1\u00da\1\u0087\1\24\1\u0088\1\u0086\1\173\1\u0088\1\173"
        u"\1\u0087\1\u00da\1\24\1\u00ac"
        )

    DFA48_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\u0089\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA48_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA48_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA48_transition = [
        DFA.unpack(u"\1\2\15\uffff\1\3\3\uffff\1\2\6\uffff\1\2\11\uffff\1"
        u"\2\13\uffff\1\2\4\uffff\1\2\3\uffff\1\2\16\uffff\2\2\4\uffff\1"
        u"\2\3\uffff\1\3\2\uffff\2\2\5\uffff\1\2\27\uffff\2\3\1\uffff\1\3"
        u"\5\uffff\1\3\6\uffff\1\2\11\uffff\1\2\1\uffff\1\2\103\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\3\3\uffff\1\2\34\uffff\1\2\4\uffff\1\2\3\uffff\1"
        u"\2\17\uffff\1\2\10\uffff\1\3\2\uffff\1\2\6\uffff\1\2\32\uffff\1"
        u"\3\14\uffff\1\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\3\uffff\1\2\34\uffff\1\2\4\uffff\1\2\3\uffff\1"
        u"\2\17\uffff\1\2\10\uffff\1\3\2\uffff\1\2\6\uffff\1\2\32\uffff\1"
        u"\3\14\uffff\1\2\13\uffff\1\2\103\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #48

    class DFA48(DFA):
        pass


    # lookup tables for DFA #66

    DFA66_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA66_eof = DFA.unpack(
        u"\30\uffff"
        )

    DFA66_min = DFA.unpack(
        u"\1\24\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1"
        u"\133\1\173\1\u00da\1\u0087\1\24\1\u0088\1\u0086\1\173\1\u0088\1"
        u"\173\1\u0087\1\u00da\1\24\1\u00ac"
        )

    DFA66_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\174\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA66_accept = DFA.unpack(
        u"\2\uffff\1\2\1\1\24\uffff"
        )

    DFA66_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA66_transition = [
        DFA.unpack(u"\1\2\102\uffff\1\2\44\uffff\1\3\5\uffff\1\2\126\uffff"
        u"\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\2\102\uffff\1\2\44\uffff\1\3"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\2\102\uffff\1\2\44\uffff\1\3\134\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #66

    class DFA66(DFA):
        pass


    # lookup tables for DFA #67

    DFA67_eot = DFA.unpack(
        u"\31\uffff"
        )

    DFA67_eof = DFA.unpack(
        u"\31\uffff"
        )

    DFA67_min = DFA.unpack(
        u"\1\24\1\uffff\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1"
        u"\u0088\1\133\1\173\1\u00da\1\u0087\1\24\1\u0088\1\u0086\1\173\1"
        u"\u0088\1\173\1\u0087\1\u00da\1\24\1\u00ac"
        )

    DFA67_max = DFA.unpack(
        u"\1\u00d9\1\uffff\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173"
        u"\1\54\1\u0088\1\133\1\173\1\u00da\1\u0087\1\127\1\u0088\1\u0086"
        u"\1\173\1\u0088\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA67_accept = DFA.unpack(
        u"\1\uffff\1\3\1\uffff\1\1\1\2\24\uffff"
        )

    DFA67_special = DFA.unpack(
        u"\31\uffff"
        )

            
    DFA67_transition = [
        DFA.unpack(u"\1\4\102\uffff\1\3\52\uffff\1\1\126\uffff\1\2"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6\11\uffff\1\6\1\uffff\1\6\4\uffff\1\6\31\uffff"
        u"\1\6\2\uffff\2\6\3\uffff\1\6\3\uffff\1\6\7\uffff\2\6\1\uffff\2"
        u"\6\3\uffff\1\6\10\uffff\1\6\2\uffff\1\6\6\uffff\1\6\2\uffff\1\6"
        u"\27\uffff\1\6\57\uffff\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\4\102\uffff\1\3"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\4\102\uffff\1\3\u0081\uffff\1\30"),
        DFA.unpack(u"\1\5")
    ]

    # class definition for DFA #67

    class DFA67(DFA):
        pass


    # lookup tables for DFA #68

    DFA68_eot = DFA.unpack(
        u"\34\uffff"
        )

    DFA68_eof = DFA.unpack(
        u"\34\uffff"
        )

    DFA68_min = DFA.unpack(
        u"\1\23\1\7\1\u0080\3\uffff\1\u00ad\1\u0086\2\uffff\1\u00ae\1\173"
        u"\1\54\1\u0088\1\133\1\173\1\u00da\1\u0087\1\23\1\u0088\1\u0086"
        u"\1\173\1\u0088\1\173\1\u0087\1\u00da\1\23\1\u00ac"
        )

    DFA68_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\1\u0095\3\uffff\1\u00ad\1\u0086\2\uffff\1\u00ae"
        u"\1\173\1\54\1\u0088\1\133\1\173\1\u00da\1\u0087\1\62\1\u0088\1"
        u"\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA68_accept = DFA.unpack(
        u"\3\uffff\1\2\1\4\1\5\2\uffff\1\3\1\1\22\uffff"
        )

    DFA68_special = DFA.unpack(
        u"\34\uffff"
        )

            
    DFA68_transition = [
        DFA.unpack(u"\1\5\36\uffff\1\2\27\uffff\1\4\5\uffff\1\3\u0088\uffff"
        u"\1\1"),
        DFA.unpack(u"\1\7\11\uffff\1\7\1\uffff\1\7\4\uffff\1\7\31\uffff"
        u"\1\7\2\uffff\2\7\3\uffff\1\7\3\uffff\1\7\7\uffff\2\7\1\uffff\2"
        u"\7\3\uffff\1\7\10\uffff\1\7\2\uffff\1\7\6\uffff\1\7\2\uffff\1\7"
        u"\27\uffff\1\7\57\uffff\1\6"),
        DFA.unpack(u"\1\11\3\uffff\1\10\20\uffff\1\11"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\5\36\uffff\1\2"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\5\36\uffff\1\2\u00a6\uffff\1\33"),
        DFA.unpack(u"\1\6")
    ]

    # class definition for DFA #68

    class DFA68(DFA):
        pass


    # lookup tables for DFA #72

    DFA72_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA72_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA72_min = DFA.unpack(
        u"\1\6\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1\133"
        u"\1\173\1\u00da\1\u0087\1\23\1\u0088\1\u0086\1\173\1\u0088\1\173"
        u"\1\u0087\1\u00da\1\23\1\u00ac"
        )

    DFA72_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\u0089\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA72_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA72_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA72_transition = [
        DFA.unpack(u"\1\2\14\uffff\1\3\4\uffff\1\2\6\uffff\1\2\11\uffff\1"
        u"\2\10\uffff\1\3\2\uffff\1\2\4\uffff\1\2\3\uffff\1\2\13\uffff\1"
        u"\3\2\uffff\2\2\1\uffff\1\3\2\uffff\1\2\6\uffff\2\2\5\uffff\1\2"
        u"\35\uffff\1\3\11\uffff\1\2\11\uffff\1\2\1\uffff\1\2\103\uffff\1"
        u"\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\3\4\uffff\1\2\31\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\3\uffff\1\2\17\uffff\1\2\13\uffff\1\2\6\uffff\1\2\47\uffff\1"
        u"\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\4\uffff\1\2\31\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\3\uffff\1\2\17\uffff\1\2\13\uffff\1\2\6\uffff\1\2\47\uffff\1"
        u"\2\13\uffff\1\2\103\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #72

    class DFA72(DFA):
        pass


    # lookup tables for DFA #83

    DFA83_eot = DFA.unpack(
        u"\31\uffff"
        )

    DFA83_eof = DFA.unpack(
        u"\1\2\30\uffff"
        )

    DFA83_min = DFA.unpack(
        u"\1\6\1\0\27\uffff"
        )

    DFA83_max = DFA.unpack(
        u"\1\u00d9\1\0\27\uffff"
        )

    DFA83_accept = DFA.unpack(
        u"\2\uffff\1\2\25\uffff\1\1"
        )

    DFA83_special = DFA.unpack(
        u"\1\uffff\1\0\27\uffff"
        )

            
    DFA83_transition = [
        DFA.unpack(u"\1\2\14\uffff\1\2\4\uffff\1\2\6\uffff\1\2\11\uffff\1"
        u"\2\10\uffff\1\2\2\uffff\1\2\4\uffff\1\2\3\uffff\1\2\13\uffff\1"
        u"\1\2\uffff\2\2\1\uffff\1\2\2\uffff\1\2\6\uffff\2\2\5\uffff\1\2"
        u"\35\uffff\1\2\11\uffff\1\2\11\uffff\1\2\1\uffff\1\2\103\uffff\1"
        u"\2"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #83

    class DFA83(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA83_1 = input.LA(1)

                 
                index83_1 = input.index()
                input.rewind()
                s = -1
                if (self.synpred108_sdl92()):
                    s = 24

                elif (True):
                    s = 2

                 
                input.seek(index83_1)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 83, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #84

    DFA84_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA84_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA84_min = DFA.unpack(
        u"\1\6\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1\133"
        u"\1\173\1\u00da\1\u0087\1\23\1\u0088\1\u0086\1\173\1\u0088\1\173"
        u"\1\u0087\1\u00da\1\23\1\u00ac"
        )

    DFA84_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\u0089\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA84_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA84_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA84_transition = [
        DFA.unpack(u"\1\2\14\uffff\1\3\4\uffff\1\2\6\uffff\1\2\11\uffff\1"
        u"\2\10\uffff\1\3\2\uffff\1\2\4\uffff\1\2\3\uffff\1\2\13\uffff\1"
        u"\3\2\uffff\2\2\1\uffff\1\3\2\uffff\1\2\6\uffff\2\2\5\uffff\1\2"
        u"\35\uffff\1\3\11\uffff\1\2\11\uffff\1\2\1\uffff\1\2\103\uffff\1"
        u"\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\3\4\uffff\1\2\31\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\3\uffff\1\2\17\uffff\1\2\13\uffff\1\2\6\uffff\1\2\47\uffff\1"
        u"\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\4\uffff\1\2\31\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\3\uffff\1\2\17\uffff\1\2\13\uffff\1\2\6\uffff\1\2\47\uffff\1"
        u"\2\13\uffff\1\2\103\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #84

    class DFA84(DFA):
        pass


    # lookup tables for DFA #92

    DFA92_eot = DFA.unpack(
        u"\51\uffff"
        )

    DFA92_eof = DFA.unpack(
        u"\51\uffff"
        )

    DFA92_min = DFA.unpack(
        u"\1\6\1\7\1\u0086\2\uffff\1\u0086\1\u00ad\1\6\1\173\1\u00ae\1\7"
        u"\1\u0088\1\54\1\u0086\1\173\1\133\1\173\1\u0087\1\u00da\2\u0088"
        u"\1\30\1\173\1\u0086\1\u0087\1\173\2\u0088\1\u0086\2\173\1\u0087"
        u"\1\u0088\1\u00da\1\173\1\30\1\u0087\1\u00d4\1\u00ac\1\u00da\1\30"
        )

    DFA92_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\1\u00d5\2\uffff\1\u0086\1\u00ad\1\u00d9\1\173"
        u"\1\u00ae\1\u00ac\1\u0088\1\54\1\u0086\1\173\1\133\1\173\1\u0087"
        u"\1\u00da\2\u0088\1\u0089\1\173\1\u0086\1\u0087\1\173\2\u0088\1"
        u"\u0086\2\173\1\u0087\1\u0088\1\u00da\1\173\1\u00d9\1\u0087\1\u00d4"
        u"\1\u00ac\1\u00da\1\u00d9"
        )

    DFA92_accept = DFA.unpack(
        u"\3\uffff\1\1\1\2\44\uffff"
        )

    DFA92_special = DFA.unpack(
        u"\51\uffff"
        )

            
    DFA92_transition = [
        DFA.unpack(u"\1\3\21\uffff\1\3\6\uffff\1\3\11\uffff\1\3\13\uffff"
        u"\1\4\4\uffff\1\4\3\uffff\1\3\16\uffff\1\3\1\4\4\uffff\1\3\6\uffff"
        u"\1\4\1\3\5\uffff\1\3\47\uffff\1\3\11\uffff\1\3\1\uffff\1\2\103"
        u"\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\6"),
        DFA.unpack(u"\1\3\52\uffff\1\3\42\uffff\1\7\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\3\21\uffff\1\3\6\uffff\1\3\11\uffff\1\3\13\uffff"
        u"\1\4\4\uffff\1\4\3\uffff\1\3\16\uffff\1\3\1\4\4\uffff\1\3\6\uffff"
        u"\1\4\1\3\5\uffff\1\3\47\uffff\1\3\11\uffff\1\3\1\uffff\1\3\103"
        u"\uffff\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15\11\uffff\1\15\1\uffff\1\15\4\uffff\1\15\31\uffff"
        u"\1\15\2\uffff\2\15\3\uffff\1\15\3\uffff\1\15\7\uffff\2\15\1\uffff"
        u"\2\15\3\uffff\1\15\10\uffff\1\15\2\uffff\1\15\6\uffff\1\15\2\uffff"
        u"\1\15\27\uffff\1\15\57\uffff\1\6"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\3\34\uffff\1\4\4\uffff\1\4\3\uffff\1\3\17\uffff"
        u"\1\4\13\uffff\1\4\6\uffff\1\3\47\uffff\1\3"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\37"),
        DFA.unpack(u"\1\40"),
        DFA.unpack(u"\1\41"),
        DFA.unpack(u"\1\42"),
        DFA.unpack(u"\1\43"),
        DFA.unpack(u"\1\44"),
        DFA.unpack(u"\1\3\34\uffff\1\4\4\uffff\1\4\3\uffff\1\3\17\uffff"
        u"\1\4\13\uffff\1\4\6\uffff\1\3\47\uffff\1\3\13\uffff\1\45\103\uffff"
        u"\1\46"),
        DFA.unpack(u"\1\47"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\50"),
        DFA.unpack(u"\1\3\34\uffff\1\4\4\uffff\1\4\3\uffff\1\3\17\uffff"
        u"\1\4\13\uffff\1\4\6\uffff\1\3\47\uffff\1\3\117\uffff\1\46")
    ]

    # class definition for DFA #92

    class DFA92(DFA):
        pass


    # lookup tables for DFA #89

    DFA89_eot = DFA.unpack(
        u"\52\uffff"
        )

    DFA89_eof = DFA.unpack(
        u"\1\3\6\uffff\1\3\42\uffff"
        )

    DFA89_min = DFA.unpack(
        u"\1\6\1\7\1\u0086\2\uffff\1\u0086\1\u00ad\1\6\1\173\1\u00ae\1\7"
        u"\1\u0086\1\u0088\1\54\1\u0086\1\173\1\133\1\173\1\u0087\1\u00da"
        u"\2\u0088\1\23\1\173\1\u0086\1\u0087\1\173\2\u0088\1\u0086\2\173"
        u"\1\u0087\1\u0088\1\u00da\1\173\1\23\1\u0087\1\u00ac\1\u00d4\1\u00da"
        u"\1\23"
        )

    DFA89_max = DFA.unpack(
        u"\1\u00d9\1\u00b0\1\u00d5\2\uffff\1\u0086\1\u00ad\1\u00d9\1\173"
        u"\1\u00ae\1\u00b0\1\u00d5\1\u0088\1\54\1\u0086\1\173\1\133\1\173"
        u"\1\u0087\1\u00da\2\u0088\1\u0089\1\173\1\u0086\1\u0087\1\173\2"
        u"\u0088\1\u0086\2\173\1\u0087\1\u0088\1\u00da\1\173\1\u00d9\1\u0087"
        u"\1\u00ac\1\u00d4\1\u00da\1\u00d9"
        )

    DFA89_accept = DFA.unpack(
        u"\3\uffff\1\2\1\1\45\uffff"
        )

    DFA89_special = DFA.unpack(
        u"\52\uffff"
        )

            
    DFA89_transition = [
        DFA.unpack(u"\1\4\14\uffff\2\3\3\uffff\1\4\1\uffff\1\3\4\uffff\1"
        u"\4\11\uffff\1\4\10\uffff\1\3\2\uffff\1\3\4\uffff\1\3\3\uffff\1"
        u"\4\13\uffff\1\3\2\uffff\1\4\1\3\1\uffff\1\3\2\uffff\1\4\3\uffff"
        u"\1\3\2\uffff\1\3\1\4\5\uffff\1\4\27\uffff\2\3\1\uffff\2\3\1\uffff"
        u"\1\3\2\uffff\1\3\3\uffff\1\3\2\uffff\1\4\2\3\7\uffff\1\4\1\uffff"
        u"\1\2\1\3\102\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\6\3\uffff\1\3"),
        DFA.unpack(u"\1\4\52\uffff\1\4\42\uffff\1\7\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\4\14\uffff\2\3\3\uffff\1\4\1\uffff\1\3\4\uffff\1"
        u"\4\11\uffff\1\4\10\uffff\1\3\2\uffff\1\3\4\uffff\1\3\3\uffff\1"
        u"\4\13\uffff\1\3\2\uffff\1\4\1\3\1\uffff\1\3\2\uffff\1\4\3\uffff"
        u"\1\3\2\uffff\1\3\1\4\5\uffff\1\4\27\uffff\2\3\1\uffff\2\3\1\uffff"
        u"\1\3\2\uffff\1\3\3\uffff\1\3\2\uffff\1\4\2\3\7\uffff\1\4\1\uffff"
        u"\1\13\1\3\102\uffff\1\12"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16\11\uffff\1\16\1\uffff\1\16\4\uffff\1\16\31\uffff"
        u"\1\16\2\uffff\2\16\3\uffff\1\16\3\uffff\1\16\7\uffff\2\16\1\uffff"
        u"\2\16\3\uffff\1\16\10\uffff\1\16\2\uffff\1\16\6\uffff\1\16\2\uffff"
        u"\1\16\27\uffff\1\16\57\uffff\1\6\3\uffff\1\3"),
        DFA.unpack(u"\1\4\52\uffff\1\4\42\uffff\1\3\1\4"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\2\3\3\uffff\1\4\1\uffff\1\3\27\uffff\1\3\2\uffff\1"
        u"\3\4\uffff\1\3\3\uffff\1\4\17\uffff\1\3\10\uffff\1\3\2\uffff\1"
        u"\3\6\uffff\1\4\32\uffff\1\3\11\uffff\1\3\2\uffff\1\4"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\37"),
        DFA.unpack(u"\1\40"),
        DFA.unpack(u"\1\41"),
        DFA.unpack(u"\1\42"),
        DFA.unpack(u"\1\43"),
        DFA.unpack(u"\1\44"),
        DFA.unpack(u"\1\45"),
        DFA.unpack(u"\2\3\3\uffff\1\4\1\uffff\1\3\27\uffff\1\3\2\uffff\1"
        u"\3\4\uffff\1\3\3\uffff\1\4\17\uffff\1\3\10\uffff\1\3\2\uffff\1"
        u"\3\6\uffff\1\4\32\uffff\1\3\11\uffff\1\3\2\uffff\1\4\13\uffff\1"
        u"\47\103\uffff\1\46"),
        DFA.unpack(u"\1\50"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\51"),
        DFA.unpack(u"\2\3\3\uffff\1\4\1\uffff\1\3\27\uffff\1\3\2\uffff\1"
        u"\3\4\uffff\1\3\3\uffff\1\4\17\uffff\1\3\10\uffff\1\3\2\uffff\1"
        u"\3\6\uffff\1\4\32\uffff\1\3\11\uffff\1\3\2\uffff\1\4\13\uffff\1"
        u"\3\103\uffff\1\46")
    ]

    # class definition for DFA #89

    class DFA89(DFA):
        pass


    # lookup tables for DFA #90

    DFA90_eot = DFA.unpack(
        u"\23\uffff"
        )

    DFA90_eof = DFA.unpack(
        u"\1\3\22\uffff"
        )

    DFA90_min = DFA.unpack(
        u"\1\23\1\7\1\u00d4\1\uffff\1\u0086\1\0\1\173\1\uffff\1\u0088\1\173"
        u"\1\u0087\1\u0088\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da\1"
        u"\23"
        )

    DFA90_max = DFA.unpack(
        u"\1\u00d9\1\u00b0\1\u00d4\1\uffff\1\u0086\1\0\1\173\1\uffff\1\u0088"
        u"\1\173\1\u0087\1\u0088\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da"
        u"\1\u00d9"
        )

    DFA90_accept = DFA.unpack(
        u"\3\uffff\1\2\3\uffff\1\1\13\uffff"
        )

    DFA90_special = DFA.unpack(
        u"\5\uffff\1\0\15\uffff"
        )

            
    DFA90_transition = [
        DFA.unpack(u"\2\3\5\uffff\1\3\27\uffff\1\3\2\uffff\1\3\4\uffff\1"
        u"\3\17\uffff\1\3\3\uffff\1\3\1\uffff\1\3\6\uffff\1\3\2\uffff\1\3"
        u"\36\uffff\2\3\1\uffff\2\3\1\uffff\1\3\2\uffff\1\3\3\uffff\1\3\3"
        u"\uffff\2\3\11\uffff\1\2\1\3\102\uffff\1\1"),
        DFA.unpack(u"\1\4\11\uffff\1\4\1\uffff\1\4\4\uffff\1\4\31\uffff"
        u"\1\4\2\uffff\2\4\3\uffff\1\4\3\uffff\1\4\7\uffff\2\4\1\uffff\2"
        u"\4\3\uffff\1\4\10\uffff\1\4\2\uffff\1\4\6\uffff\1\4\2\uffff\1\4"
        u"\27\uffff\1\4\57\uffff\1\3\3\uffff\1\3"),
        DFA.unpack(u"\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\2\3\5\uffff\1\3\27\uffff\1\3\2\uffff\1\3\4\uffff\1"
        u"\3\23\uffff\1\3\10\uffff\1\3\2\uffff\1\3\41\uffff\1\3\11\uffff"
        u"\1\3\16\uffff\1\2\103\uffff\1\3")
    ]

    # class definition for DFA #90

    class DFA90(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA90_5 = input.LA(1)

                 
                index90_5 = input.index()
                input.rewind()
                s = -1
                if (self.synpred115_sdl92()):
                    s = 7

                elif (True):
                    s = 3

                 
                input.seek(index90_5)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 90, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #91

    DFA91_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA91_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA91_min = DFA.unpack(
        u"\1\23\1\7\2\uffff\1\u0086\1\u00ad\1\173\1\u00ae\1\u0088\1\54\1"
        u"\173\1\133\1\u0087\1\u00da\1\u0088\1\23\1\u0086\1\173\1\u0088\1"
        u"\173\1\u0087\1\u00da\1\23\1\u00ac"
        )

    DFA91_max = DFA.unpack(
        u"\1\u00d9\1\u00b0\2\uffff\1\u0086\1\u00ad\1\173\1\u00ae\1\u0088"
        u"\1\54\1\173\1\133\1\u0087\1\u00da\1\u0088\2\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA91_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA91_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA91_transition = [
        DFA.unpack(u"\2\3\5\uffff\1\3\27\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\17\uffff\1\3\3\uffff\1\2\1\uffff\1\3\6\uffff\1\3\2\uffff\1\2"
        u"\36\uffff\2\3\1\uffff\2\3\1\uffff\1\3\2\uffff\1\3\3\uffff\1\3\3"
        u"\uffff\2\3\11\uffff\1\2\1\3\102\uffff\1\1"),
        DFA.unpack(u"\1\4\11\uffff\1\4\1\uffff\1\4\4\uffff\1\4\31\uffff"
        u"\1\4\2\uffff\2\4\3\uffff\1\4\3\uffff\1\4\7\uffff\2\4\1\uffff\2"
        u"\4\3\uffff\1\4\10\uffff\1\4\2\uffff\1\4\6\uffff\1\4\2\uffff\1\4"
        u"\27\uffff\1\4\57\uffff\1\5\3\uffff\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\2\3\5\uffff\1\3\27\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\23\uffff\1\2\10\uffff\1\3\2\uffff\1\2\41\uffff\1\3\11\uffff"
        u"\1\3"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\2\3\5\uffff\1\3\27\uffff\1\3\2\uffff\1\2\4\uffff\1"
        u"\2\23\uffff\1\2\10\uffff\1\3\2\uffff\1\2\41\uffff\1\3\11\uffff"
        u"\1\3\16\uffff\1\2\103\uffff\1\27"),
        DFA.unpack(u"\1\5")
    ]

    # class definition for DFA #91

    class DFA91(DFA):
        pass


    # lookup tables for DFA #93

    DFA93_eot = DFA.unpack(
        u"\22\uffff"
        )

    DFA93_eof = DFA.unpack(
        u"\22\uffff"
        )

    DFA93_min = DFA.unpack(
        u"\1\6\1\7\1\u0086\1\uffff\1\u0086\1\uffff\1\173\1\u0088\1\173\1"
        u"\u0087\1\u0088\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da\1\30"
        )

    DFA93_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\1\u00d5\1\uffff\1\u0086\1\uffff\1\173\1\u0088"
        u"\1\173\1\u0087\1\u0088\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da"
        u"\1\u00d9"
        )

    DFA93_accept = DFA.unpack(
        u"\3\uffff\1\2\1\uffff\1\1\14\uffff"
        )

    DFA93_special = DFA.unpack(
        u"\22\uffff"
        )

            
    DFA93_transition = [
        DFA.unpack(u"\1\3\21\uffff\1\3\6\uffff\1\3\11\uffff\1\3\24\uffff"
        u"\1\3\16\uffff\1\3\5\uffff\1\3\7\uffff\1\3\5\uffff\1\3\47\uffff"
        u"\1\3\11\uffff\1\3\1\uffff\1\2\103\uffff\1\1"),
        DFA.unpack(u"\1\4\11\uffff\1\4\1\uffff\1\4\4\uffff\1\4\31\uffff"
        u"\1\4\2\uffff\2\4\3\uffff\1\4\3\uffff\1\4\7\uffff\2\4\1\uffff\2"
        u"\4\3\uffff\1\4\10\uffff\1\4\2\uffff\1\4\6\uffff\1\4\2\uffff\1\4"
        u"\27\uffff\1\4\57\uffff\1\3"),
        DFA.unpack(u"\1\3\52\uffff\1\3\42\uffff\1\5\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\3\45\uffff\1\3\42\uffff\1\3\47\uffff\1\3\13\uffff"
        u"\1\5\103\uffff\1\3")
    ]

    # class definition for DFA #93

    class DFA93(DFA):
        pass


    # lookup tables for DFA #94

    DFA94_eot = DFA.unpack(
        u"\40\uffff"
        )

    DFA94_eof = DFA.unpack(
        u"\40\uffff"
        )

    DFA94_min = DFA.unpack(
        u"\1\6\1\7\12\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1"
        u"\133\1\173\1\u00da\1\u0087\1\30\1\u0088\1\u0086\1\173\1\u0088\1"
        u"\173\1\u0087\1\u00da\1\30\1\u00ac"
        )

    DFA94_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\12\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1"
        u"\u0088\1\133\1\173\1\u00da\1\u0087\1\u0089\1\u0088\1\u0086\1\173"
        u"\1\u0088\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA94_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\1\3\1\4\1\5\1\6\1\7\1\10\1\11\1\12\24\uffff"
        )

    DFA94_special = DFA.unpack(
        u"\40\uffff"
        )

            
    DFA94_transition = [
        DFA.unpack(u"\1\7\21\uffff\1\6\6\uffff\1\12\11\uffff\1\3\24\uffff"
        u"\1\4\16\uffff\1\11\5\uffff\1\10\7\uffff\1\3\5\uffff\1\2\47\uffff"
        u"\1\13\11\uffff\1\5\1\uffff\1\3\103\uffff\1\1"),
        DFA.unpack(u"\1\15\11\uffff\1\15\1\uffff\1\15\4\uffff\1\15\31\uffff"
        u"\1\15\2\uffff\2\15\3\uffff\1\15\3\uffff\1\15\7\uffff\2\15\1\uffff"
        u"\2\15\3\uffff\1\15\10\uffff\1\15\2\uffff\1\15\6\uffff\1\15\2\uffff"
        u"\1\15\27\uffff\1\15\57\uffff\1\14"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\6\45\uffff\1\4\42\uffff\1\2\47\uffff\1\13"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\6\45\uffff\1\4\42\uffff\1\2\47\uffff\1\13\117\uffff"
        u"\1\37"),
        DFA.unpack(u"\1\14")
    ]

    # class definition for DFA #94

    class DFA94(DFA):
        pass


    # lookup tables for DFA #105

    DFA105_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA105_eof = DFA.unpack(
        u"\30\uffff"
        )

    DFA105_min = DFA.unpack(
        u"\1\32\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1"
        u"\133\1\173\1\u00da\1\u0087\1\32\1\u0088\1\u0086\1\173\1\u0088\1"
        u"\173\1\u0087\1\u00da\1\32\1\u00ac"
        )

    DFA105_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\u0086\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA105_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA105_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA105_transition = [
        DFA.unpack(u"\1\3\153\uffff\1\2\122\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\3\153\uffff\1\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\153\uffff\1\2\122\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #105

    class DFA105(DFA):
        pass


    # lookup tables for DFA #103

    DFA103_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA103_eof = DFA.unpack(
        u"\1\2\27\uffff"
        )

    DFA103_min = DFA.unpack(
        u"\1\32\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1"
        u"\133\1\173\1\u00da\1\u0087\1\32\1\u0088\1\u0086\1\173\1\u0088\1"
        u"\173\1\u0087\1\u00da\1\32\1\u00ac"
        )

    DFA103_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\u0086\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA103_accept = DFA.unpack(
        u"\2\uffff\1\2\1\1\24\uffff"
        )

    DFA103_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA103_transition = [
        DFA.unpack(u"\1\2\153\uffff\1\3\3\uffff\2\2\115\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\2\153\uffff\1\3"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\2\153\uffff\1\3\122\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #103

    class DFA103(DFA):
        pass


    # lookup tables for DFA #113

    DFA113_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA113_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA113_min = DFA.unpack(
        u"\1\6\1\7\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088\1\133"
        u"\1\173\1\u00da\1\u0087\1\30\1\u0088\1\u0086\1\173\1\u0088\1\173"
        u"\1\u0087\1\u00da\1\30\1\u00ac"
        )

    DFA113_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u00ad\1\u0086\1\u00ae\1\173\1\54\1\u0088"
        u"\1\133\1\173\1\u00da\1\u0087\1\u0089\1\u0088\1\u0086\1\173\1\u0088"
        u"\1\173\1\u0087\1\u00da\1\u00d9\1\u00ac"
        )

    DFA113_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA113_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA113_transition = [
        DFA.unpack(u"\1\2\21\uffff\1\2\1\uffff\1\3\4\uffff\1\2\11\uffff\1"
        u"\2\13\uffff\1\2\4\uffff\1\2\3\uffff\1\2\16\uffff\2\2\4\uffff\1"
        u"\2\6\uffff\2\2\5\uffff\1\2\44\uffff\1\3\2\uffff\1\2\2\3\7\uffff"
        u"\1\2\1\uffff\1\2\103\uffff\1\1"),
        DFA.unpack(u"\1\5\11\uffff\1\5\1\uffff\1\5\4\uffff\1\5\31\uffff"
        u"\1\5\2\uffff\2\5\3\uffff\1\5\3\uffff\1\5\7\uffff\2\5\1\uffff\2"
        u"\5\3\uffff\1\5\10\uffff\1\5\2\uffff\1\5\6\uffff\1\5\2\uffff\1\5"
        u"\27\uffff\1\5\57\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\2\1\uffff\1\3\32\uffff\1\2\4\uffff\1\2\3\uffff\1"
        u"\2\17\uffff\1\2\13\uffff\1\2\6\uffff\1\2\44\uffff\1\3\2\uffff\1"
        u"\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\2\1\uffff\1\3\32\uffff\1\2\4\uffff\1\2\3\uffff\1"
        u"\2\17\uffff\1\2\13\uffff\1\2\6\uffff\1\2\44\uffff\1\3\2\uffff\1"
        u"\2\13\uffff\1\2\103\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #113

    class DFA113(DFA):
        pass


    # lookup tables for DFA #153

    DFA153_eot = DFA.unpack(
        u"\12\uffff"
        )

    DFA153_eof = DFA.unpack(
        u"\1\1\11\uffff"
        )

    DFA153_min = DFA.unpack(
        u"\1\6\1\uffff\7\0\1\uffff"
        )

    DFA153_max = DFA.unpack(
        u"\1\u00d9\1\uffff\7\0\1\uffff"
        )

    DFA153_accept = DFA.unpack(
        u"\1\uffff\1\2\7\uffff\1\1"
        )

    DFA153_special = DFA.unpack(
        u"\2\uffff\1\3\1\5\1\0\1\6\1\1\1\4\1\2\1\uffff"
        )

            
    DFA153_transition = [
        DFA.unpack(u"\1\1\12\uffff\1\1\1\uffff\2\1\3\uffff\1\1\1\uffff\1"
        u"\1\2\uffff\1\1\1\uffff\1\1\2\uffff\1\1\6\uffff\1\1\5\uffff\1\10"
        u"\2\uffff\1\1\2\uffff\1\1\4\uffff\1\1\3\uffff\1\1\13\uffff\1\1\2"
        u"\uffff\2\1\1\uffff\1\1\2\uffff\1\1\3\uffff\1\1\2\uffff\2\1\5\uffff"
        u"\1\1\5\uffff\1\1\17\uffff\1\1\1\uffff\2\1\1\uffff\5\1\1\uffff\1"
        u"\1\3\uffff\6\1\1\uffff\1\2\1\3\1\4\1\6\1\7\1\5\1\1\1\uffff\13\1"
        u"\23\uffff\1\1\30\uffff\1\1\10\uffff\1\1\1\uffff\1\1\1\uffff\1\1"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"")
    ]

    # class definition for DFA #153

    class DFA153(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA153_4 = input.LA(1)

                 
                index153_4 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_4)
                if s >= 0:
                    return s
            elif s == 1: 
                LA153_6 = input.LA(1)

                 
                index153_6 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_6)
                if s >= 0:
                    return s
            elif s == 2: 
                LA153_8 = input.LA(1)

                 
                index153_8 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_8)
                if s >= 0:
                    return s
            elif s == 3: 
                LA153_2 = input.LA(1)

                 
                index153_2 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_2)
                if s >= 0:
                    return s
            elif s == 4: 
                LA153_7 = input.LA(1)

                 
                index153_7 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_7)
                if s >= 0:
                    return s
            elif s == 5: 
                LA153_3 = input.LA(1)

                 
                index153_3 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_3)
                if s >= 0:
                    return s
            elif s == 6: 
                LA153_5 = input.LA(1)

                 
                index153_5 = input.index()
                input.rewind()
                s = -1
                if (self.synpred199_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index153_5)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 153, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #163

    DFA163_eot = DFA.unpack(
        u"\24\uffff"
        )

    DFA163_eof = DFA.unpack(
        u"\24\uffff"
        )

    DFA163_min = DFA.unpack(
        u"\1\13\12\uffff\2\0\7\uffff"
        )

    DFA163_max = DFA.unpack(
        u"\1\u00b2\12\uffff\2\0\7\uffff"
        )

    DFA163_accept = DFA.unpack(
        u"\1\uffff\1\1\1\2\1\3\1\4\1\5\1\6\1\7\1\10\1\11\1\12\2\uffff\1\13"
        u"\1\14\1\15\1\16\1\17\1\20\1\21"
        )

    DFA163_special = DFA.unpack(
        u"\13\uffff\1\0\1\1\7\uffff"
        )

            
    DFA163_transition = [
        DFA.unpack(u"\1\1\33\uffff\1\12\24\uffff\1\2\36\uffff\1\5\37\uffff"
        u"\1\11\31\uffff\1\13\13\uffff\1\3\1\4\1\6\1\7\1\10\14\uffff\1\14"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #163

    class DFA163(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA163_11 = input.LA(1)

                 
                index163_11 = input.index()
                input.rewind()
                s = -1
                if (self.synpred221_sdl92()):
                    s = 13

                elif (self.synpred223_sdl92()):
                    s = 14

                elif (self.synpred224_sdl92()):
                    s = 15

                 
                input.seek(index163_11)
                if s >= 0:
                    return s
            elif s == 1: 
                LA163_12 = input.LA(1)

                 
                index163_12 = input.index()
                input.rewind()
                s = -1
                if (self.synpred225_sdl92()):
                    s = 16

                elif (self.synpred226_sdl92()):
                    s = 17

                elif (self.synpred228_sdl92()):
                    s = 18

                elif (True):
                    s = 19

                 
                input.seek(index163_12)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 163, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #160

    DFA160_eot = DFA.unpack(
        u"\102\uffff"
        )

    DFA160_eof = DFA.unpack(
        u"\1\1\101\uffff"
        )

    DFA160_min = DFA.unpack(
        u"\1\6\52\uffff\1\0\23\uffff\1\0\2\uffff"
        )

    DFA160_max = DFA.unpack(
        u"\1\u00d9\52\uffff\1\0\23\uffff\1\0\2\uffff"
        )

    DFA160_accept = DFA.unpack(
        u"\1\uffff\1\2\77\uffff\1\1"
        )

    DFA160_special = DFA.unpack(
        u"\53\uffff\1\0\23\uffff\1\1\2\uffff"
        )

            
    DFA160_transition = [
        DFA.unpack(u"\1\1\12\uffff\1\1\1\uffff\2\1\3\uffff\1\1\1\uffff\1"
        u"\1\2\uffff\1\1\1\uffff\1\1\2\uffff\1\1\6\uffff\1\1\5\uffff\1\1"
        u"\2\uffff\1\1\2\uffff\1\1\4\uffff\1\1\3\uffff\1\1\13\uffff\1\1\2"
        u"\uffff\2\1\1\uffff\1\1\2\uffff\1\1\3\uffff\1\1\2\uffff\2\1\5\uffff"
        u"\1\1\5\uffff\1\1\17\uffff\1\1\1\uffff\2\1\1\uffff\5\1\1\uffff\1"
        u"\1\3\uffff\1\53\5\1\1\uffff\7\1\1\uffff\13\1\23\uffff\1\1\30\uffff"
        u"\1\1\10\uffff\1\77\1\uffff\1\1\1\uffff\1\1"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #160

    class DFA160(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA160_43 = input.LA(1)

                 
                index160_43 = input.index()
                input.rewind()
                s = -1
                if (self.synpred222_sdl92()):
                    s = 65

                elif (True):
                    s = 1

                 
                input.seek(index160_43)
                if s >= 0:
                    return s
            elif s == 1: 
                LA160_63 = input.LA(1)

                 
                index160_63 = input.index()
                input.rewind()
                s = -1
                if (self.synpred222_sdl92()):
                    s = 65

                elif (True):
                    s = 1

                 
                input.seek(index160_63)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 160, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #172

    DFA172_eot = DFA.unpack(
        u"\21\uffff"
        )

    DFA172_eof = DFA.unpack(
        u"\21\uffff"
        )

    DFA172_min = DFA.unpack(
        u"\1\65\1\7\2\uffff\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u0088\1"
        u"\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da\1\65"
        )

    DFA172_max = DFA.unpack(
        u"\1\u00d9\1\u00ac\2\uffff\1\u0086\1\173\1\u0088\1\173\1\u0087\1"
        u"\u0088\1\u0086\1\173\1\u0088\1\173\1\u0087\1\u00da\1\u00d9"
        )

    DFA172_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\15\uffff"
        )

    DFA172_special = DFA.unpack(
        u"\21\uffff"
        )

            
    DFA172_transition = [
        DFA.unpack(u"\1\3\4\uffff\1\3\23\uffff\1\3\13\uffff\1\3\72\uffff"
        u"\1\2\103\uffff\1\1"),
        DFA.unpack(u"\1\4\11\uffff\1\4\1\uffff\1\4\4\uffff\1\4\31\uffff"
        u"\1\4\2\uffff\2\4\3\uffff\1\4\3\uffff\1\4\7\uffff\2\4\1\uffff\2"
        u"\4\3\uffff\1\4\10\uffff\1\4\2\uffff\1\4\6\uffff\1\4\2\uffff\1\4"
        u"\27\uffff\1\4\57\uffff\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\5"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\3\4\uffff\1\3\23\uffff\1\3\13\uffff\1\3\72\uffff"
        u"\1\2\103\uffff\1\3")
    ]

    # class definition for DFA #172

    class DFA172(DFA):
        pass


 

    FOLLOW_use_clause_in_pr_file1277 = frozenset([1, 73, 96, 107, 217])
    FOLLOW_system_definition_in_pr_file1297 = frozenset([1, 73, 96, 107, 217])
    FOLLOW_process_definition_in_pr_file1317 = frozenset([1, 73, 96, 107, 217])
    FOLLOW_SYSTEM_in_system_definition1342 = frozenset([149])
    FOLLOW_system_name_in_system_definition1344 = frozenset([17, 126, 217])
    FOLLOW_end_in_system_definition1346 = frozenset([12, 13, 70, 84, 113, 217])
    FOLLOW_entity_in_system_in_system_definition1364 = frozenset([12, 13, 70, 84, 113, 217])
    FOLLOW_ENDSYSTEM_in_system_definition1383 = frozenset([17, 126, 149, 217])
    FOLLOW_system_name_in_system_definition1385 = frozenset([17, 126, 217])
    FOLLOW_end_in_system_definition1388 = frozenset([1])
    FOLLOW_use_asn1_in_use_clause1435 = frozenset([107])
    FOLLOW_USE_in_use_clause1454 = frozenset([149])
    FOLLOW_package_name_in_use_clause1456 = frozenset([17, 126, 217])
    FOLLOW_end_in_use_clause1458 = frozenset([1])
    FOLLOW_signal_declaration_in_entity_in_system1507 = frozenset([1])
    FOLLOW_procedure_in_entity_in_system1527 = frozenset([1])
    FOLLOW_channel_in_entity_in_system1547 = frozenset([1])
    FOLLOW_block_definition_in_entity_in_system1567 = frozenset([1])
    FOLLOW_paramnames_in_signal_declaration1591 = frozenset([84])
    FOLLOW_SIGNAL_in_signal_declaration1610 = frozenset([149])
    FOLLOW_signal_id_in_signal_declaration1612 = frozenset([17, 126, 134, 217])
    FOLLOW_input_params_in_signal_declaration1614 = frozenset([17, 126, 217])
    FOLLOW_end_in_signal_declaration1617 = frozenset([1])
    FOLLOW_CHANNEL_in_channel1667 = frozenset([149])
    FOLLOW_channel_id_in_channel1669 = frozenset([115])
    FOLLOW_route_in_channel1687 = frozenset([114, 115])
    FOLLOW_ENDCHANNEL_in_channel1706 = frozenset([17, 126, 217])
    FOLLOW_end_in_channel1708 = frozenset([1])
    FOLLOW_FROM_in_route1755 = frozenset([149])
    FOLLOW_source_id_in_route1757 = frozenset([105])
    FOLLOW_TO_in_route1759 = frozenset([149])
    FOLLOW_dest_id_in_route1761 = frozenset([116])
    FOLLOW_WITH_in_route1763 = frozenset([149])
    FOLLOW_signal_id_in_route1765 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_route1768 = frozenset([149])
    FOLLOW_signal_id_in_route1770 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_route1774 = frozenset([1])
    FOLLOW_BLOCK_in_block_definition1823 = frozenset([149])
    FOLLOW_block_id_in_block_definition1825 = frozenset([17, 126, 217])
    FOLLOW_end_in_block_definition1827 = frozenset([12, 13, 19, 70, 73, 84, 96, 107, 117, 118, 217])
    FOLLOW_entity_in_block_in_block_definition1845 = frozenset([12, 13, 19, 70, 73, 84, 96, 107, 117, 118, 217])
    FOLLOW_ENDBLOCK_in_block_definition1864 = frozenset([17, 126, 217])
    FOLLOW_end_in_block_definition1866 = frozenset([1])
    FOLLOW_signal_declaration_in_entity_in_block1915 = frozenset([1])
    FOLLOW_signalroute_in_entity_in_block1935 = frozenset([1])
    FOLLOW_connection_in_entity_in_block1955 = frozenset([1])
    FOLLOW_block_definition_in_entity_in_block1975 = frozenset([1])
    FOLLOW_process_definition_in_entity_in_block1995 = frozenset([1])
    FOLLOW_SIGNALROUTE_in_signalroute2018 = frozenset([149])
    FOLLOW_route_id_in_signalroute2020 = frozenset([115])
    FOLLOW_route_in_signalroute2038 = frozenset([1, 115])
    FOLLOW_CONNECT_in_connection2086 = frozenset([149])
    FOLLOW_channel_id_in_connection2088 = frozenset([119])
    FOLLOW_AND_in_connection2090 = frozenset([149])
    FOLLOW_route_id_in_connection2092 = frozenset([17, 126, 217])
    FOLLOW_end_in_connection2094 = frozenset([1])
    FOLLOW_PROCESS_in_process_definition2140 = frozenset([149])
    FOLLOW_process_id_in_process_definition2142 = frozenset([120, 134])
    FOLLOW_number_of_instances_in_process_definition2144 = frozenset([120])
    FOLLOW_REFERENCED_in_process_definition2147 = frozenset([17, 126, 217])
    FOLLOW_end_in_process_definition2149 = frozenset([1])
    FOLLOW_cif_in_process_definition2195 = frozenset([73])
    FOLLOW_PROCESS_in_process_definition2198 = frozenset([149])
    FOLLOW_process_id_in_process_definition2200 = frozenset([17, 126, 134, 217])
    FOLLOW_number_of_instances_in_process_definition2202 = frozenset([17, 126, 217])
    FOLLOW_end_in_process_definition2205 = frozenset([20, 70, 87, 121, 124, 217])
    FOLLOW_text_area_in_process_definition2224 = frozenset([20, 70, 87, 121, 124, 217])
    FOLLOW_procedure_in_process_definition2228 = frozenset([20, 70, 87, 121, 124, 217])
    FOLLOW_composite_state_in_process_definition2232 = frozenset([20, 70, 87, 121, 124, 217])
    FOLLOW_processBody_in_process_definition2252 = frozenset([121])
    FOLLOW_ENDPROCESS_in_process_definition2255 = frozenset([17, 126, 149, 217])
    FOLLOW_process_id_in_process_definition2257 = frozenset([17, 126, 217])
    FOLLOW_end_in_process_definition2276 = frozenset([1])
    FOLLOW_cif_in_procedure2356 = frozenset([70])
    FOLLOW_PROCEDURE_in_procedure2375 = frozenset([149])
    FOLLOW_procedure_id_in_procedure2377 = frozenset([17, 126, 217])
    FOLLOW_end_in_procedure2379 = frozenset([20, 33, 42, 70, 87, 122, 124, 217])
    FOLLOW_fpar_in_procedure2397 = frozenset([20, 33, 70, 87, 122, 124, 217])
    FOLLOW_text_area_in_procedure2417 = frozenset([20, 33, 70, 87, 122, 124, 217])
    FOLLOW_procedure_in_procedure2421 = frozenset([20, 33, 70, 87, 122, 124, 217])
    FOLLOW_processBody_in_procedure2443 = frozenset([122])
    FOLLOW_ENDPROCEDURE_in_procedure2446 = frozenset([17, 126, 149, 217])
    FOLLOW_procedure_id_in_procedure2448 = frozenset([17, 126, 217])
    FOLLOW_EXTERNAL_in_procedure2454 = frozenset([17, 126, 217])
    FOLLOW_end_in_procedure2473 = frozenset([1])
    FOLLOW_FPAR_in_fpar2555 = frozenset([47, 49, 149])
    FOLLOW_formal_variable_param_in_fpar2557 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_fpar2576 = frozenset([47, 49, 149])
    FOLLOW_formal_variable_param_in_fpar2578 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_fpar2598 = frozenset([1])
    FOLLOW_INOUT_in_formal_variable_param2644 = frozenset([47, 49, 149])
    FOLLOW_IN_in_formal_variable_param2648 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_formal_variable_param2668 = frozenset([136, 149])
    FOLLOW_COMMA_in_formal_variable_param2671 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_formal_variable_param2673 = frozenset([136, 149])
    FOLLOW_sort_in_formal_variable_param2677 = frozenset([1])
    FOLLOW_cif_in_text_area2731 = frozenset([23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_content_in_text_area2749 = frozenset([23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_cif_end_text_in_text_area2768 = frozenset([1])
    FOLLOW_procedure_in_content2821 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_fpar_in_content2842 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_timer_declaration_in_content2863 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_syntype_definition_in_content2884 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_newtype_definition_in_content2905 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_variable_definition_in_content2926 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_synonym_definition_in_content2947 = frozenset([1, 23, 42, 57, 70, 93, 95, 104, 217])
    FOLLOW_TIMER_in_timer_declaration3051 = frozenset([149])
    FOLLOW_timer_id_in_timer_declaration3053 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_timer_declaration3072 = frozenset([149])
    FOLLOW_timer_id_in_timer_declaration3074 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_timer_declaration3094 = frozenset([1])
    FOLLOW_SYNTYPE_in_syntype_definition3138 = frozenset([136, 149])
    FOLLOW_syntype_name_in_syntype_definition3140 = frozenset([141])
    FOLLOW_EQ_in_syntype_definition3142 = frozenset([136, 149])
    FOLLOW_parent_sort_in_syntype_definition3144 = frozenset([22, 29])
    FOLLOW_CONSTANTS_in_syntype_definition3163 = frozenset([11, 39, 45, 60, 91, 123, 134, 141, 142, 143, 144, 145, 146, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_range_condition_in_syntype_definition3166 = frozenset([29, 136])
    FOLLOW_COMMA_in_syntype_definition3169 = frozenset([11, 39, 45, 60, 91, 123, 134, 141, 142, 143, 144, 145, 146, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_range_condition_in_syntype_definition3171 = frozenset([29, 136])
    FOLLOW_ENDSYNTYPE_in_syntype_definition3195 = frozenset([17, 126, 136, 149, 217])
    FOLLOW_syntype_name_in_syntype_definition3197 = frozenset([17, 126, 217])
    FOLLOW_end_in_syntype_definition3200 = frozenset([1])
    FOLLOW_sort_in_syntype_name3248 = frozenset([1])
    FOLLOW_sort_in_parent_sort3270 = frozenset([1])
    FOLLOW_NEWTYPE_in_newtype_definition3292 = frozenset([136, 149])
    FOLLOW_type_name_in_newtype_definition3294 = frozenset([8, 28, 92])
    FOLLOW_array_definition_in_newtype_definition3297 = frozenset([28])
    FOLLOW_structure_definition_in_newtype_definition3299 = frozenset([28])
    FOLLOW_ENDNEWTYPE_in_newtype_definition3319 = frozenset([17, 126, 136, 149, 217])
    FOLLOW_type_name_in_newtype_definition3321 = frozenset([17, 126, 217])
    FOLLOW_end_in_newtype_definition3324 = frozenset([1])
    FOLLOW_sort_in_type_name3374 = frozenset([1])
    FOLLOW_ARRAY_in_array_definition3396 = frozenset([134])
    FOLLOW_L_PAREN_in_array_definition3398 = frozenset([136, 149])
    FOLLOW_sort_in_array_definition3400 = frozenset([136])
    FOLLOW_COMMA_in_array_definition3402 = frozenset([136, 149])
    FOLLOW_sort_in_array_definition3404 = frozenset([135])
    FOLLOW_R_PAREN_in_array_definition3406 = frozenset([1])
    FOLLOW_STRUCT_in_structure_definition3451 = frozenset([149])
    FOLLOW_field_list_in_structure_definition3453 = frozenset([17, 126, 217])
    FOLLOW_end_in_structure_definition3455 = frozenset([1])
    FOLLOW_field_definition_in_field_list3498 = frozenset([1, 17, 126, 217])
    FOLLOW_end_in_field_list3501 = frozenset([149])
    FOLLOW_field_definition_in_field_list3503 = frozenset([1, 17, 126, 217])
    FOLLOW_field_name_in_field_definition3549 = frozenset([136, 149])
    FOLLOW_COMMA_in_field_definition3552 = frozenset([149])
    FOLLOW_field_name_in_field_definition3554 = frozenset([136, 149])
    FOLLOW_sort_in_field_definition3558 = frozenset([1])
    FOLLOW_DCL_in_variable_definition3604 = frozenset([47, 49, 149])
    FOLLOW_variables_of_sort_in_variable_definition3606 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_variable_definition3625 = frozenset([47, 49, 149])
    FOLLOW_variables_of_sort_in_variable_definition3627 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_variable_definition3647 = frozenset([1])
    FOLLOW_internal_synonym_definition_in_synonym_definition3691 = frozenset([1])
    FOLLOW_SYNONYM_in_internal_synonym_definition3713 = frozenset([136, 149])
    FOLLOW_synonym_definition_item_in_internal_synonym_definition3715 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_internal_synonym_definition3718 = frozenset([136, 149])
    FOLLOW_synonym_definition_item_in_internal_synonym_definition3720 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_internal_synonym_definition3740 = frozenset([1])
    FOLLOW_sort_in_synonym_definition_item3784 = frozenset([136, 149])
    FOLLOW_sort_in_synonym_definition_item3786 = frozenset([141])
    FOLLOW_EQ_in_synonym_definition_item3788 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ground_expression_in_synonym_definition_item3790 = frozenset([1])
    FOLLOW_variable_id_in_variables_of_sort3837 = frozenset([136, 149])
    FOLLOW_COMMA_in_variables_of_sort3840 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_variables_of_sort3842 = frozenset([136, 149])
    FOLLOW_sort_in_variables_of_sort3846 = frozenset([1, 177])
    FOLLOW_ASSIG_OP_in_variables_of_sort3849 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ground_expression_in_variables_of_sort3851 = frozenset([1])
    FOLLOW_expression_in_ground_expression3903 = frozenset([1])
    FOLLOW_L_PAREN_in_number_of_instances3947 = frozenset([123])
    FOLLOW_INT_in_number_of_instances3951 = frozenset([136])
    FOLLOW_COMMA_in_number_of_instances3953 = frozenset([123])
    FOLLOW_INT_in_number_of_instances3957 = frozenset([135])
    FOLLOW_R_PAREN_in_number_of_instances3959 = frozenset([1])
    FOLLOW_start_in_processBody4007 = frozenset([1, 20, 87, 217])
    FOLLOW_state_in_processBody4011 = frozenset([1, 20, 87, 217])
    FOLLOW_floating_label_in_processBody4015 = frozenset([1, 20, 87, 217])
    FOLLOW_cif_in_start4040 = frozenset([124, 217])
    FOLLOW_hyperlink_in_start4059 = frozenset([124])
    FOLLOW_START_in_start4078 = frozenset([17, 126, 149, 217])
    FOLLOW_state_entry_point_name_in_start4082 = frozenset([17, 126, 217])
    FOLLOW_end_in_start4085 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_start4103 = frozenset([1])
    FOLLOW_cif_in_floating_label4162 = frozenset([20, 217])
    FOLLOW_hyperlink_in_floating_label4181 = frozenset([20])
    FOLLOW_CONNECTION_in_floating_label4200 = frozenset([149, 217])
    FOLLOW_connector_name_in_floating_label4202 = frozenset([212])
    FOLLOW_212_in_floating_label4204 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 125, 137, 147, 149, 217])
    FOLLOW_transition_in_floating_label4222 = frozenset([125, 217])
    FOLLOW_cif_end_label_in_floating_label4241 = frozenset([125])
    FOLLOW_ENDCONNECTION_in_floating_label4260 = frozenset([126])
    FOLLOW_SEMI_in_floating_label4262 = frozenset([1])
    FOLLOW_cif_in_state4315 = frozenset([87, 217])
    FOLLOW_hyperlink_in_state4334 = frozenset([87])
    FOLLOW_STATE_in_state4353 = frozenset([128, 149])
    FOLLOW_statelist_in_state4355 = frozenset([17, 126, 217])
    FOLLOW_end_in_state4359 = frozenset([19, 50, 74, 80, 127, 217])
    FOLLOW_state_part_in_state4378 = frozenset([19, 50, 74, 80, 127, 217])
    FOLLOW_ENDSTATE_in_state4398 = frozenset([17, 126, 149, 217])
    FOLLOW_statename_in_state4400 = frozenset([17, 126, 217])
    FOLLOW_end_in_state4405 = frozenset([1])
    FOLLOW_statename_in_statelist4464 = frozenset([1, 136])
    FOLLOW_COMMA_in_statelist4467 = frozenset([149])
    FOLLOW_statename_in_statelist4469 = frozenset([1, 136])
    FOLLOW_ASTERISK_in_statelist4514 = frozenset([1, 134])
    FOLLOW_exception_state_in_statelist4516 = frozenset([1])
    FOLLOW_L_PAREN_in_exception_state4562 = frozenset([149])
    FOLLOW_statename_in_exception_state4564 = frozenset([135, 136])
    FOLLOW_COMMA_in_exception_state4567 = frozenset([149])
    FOLLOW_statename_in_exception_state4569 = frozenset([135, 136])
    FOLLOW_R_PAREN_in_exception_state4573 = frozenset([1])
    FOLLOW_STATE_in_composite_state4614 = frozenset([149])
    FOLLOW_statename_in_composite_state4616 = frozenset([17, 126, 217])
    FOLLOW_end_in_composite_state4620 = frozenset([129])
    FOLLOW_SUBSTRUCTURE_in_composite_state4638 = frozenset([20, 47, 70, 87, 124, 130, 131, 217])
    FOLLOW_connection_points_in_composite_state4656 = frozenset([20, 47, 70, 87, 124, 130, 131, 217])
    FOLLOW_composite_state_body_in_composite_state4677 = frozenset([130])
    FOLLOW_ENDSUBSTRUCTURE_in_composite_state4695 = frozenset([17, 126, 149, 217])
    FOLLOW_statename_in_composite_state4697 = frozenset([17, 126, 217])
    FOLLOW_end_in_composite_state4702 = frozenset([1])
    FOLLOW_IN_in_connection_points4756 = frozenset([134])
    FOLLOW_state_entry_exit_points_in_connection_points4758 = frozenset([17, 126, 217])
    FOLLOW_end_in_connection_points4760 = frozenset([1])
    FOLLOW_OUT_in_connection_points4804 = frozenset([134])
    FOLLOW_state_entry_exit_points_in_connection_points4806 = frozenset([17, 126, 217])
    FOLLOW_end_in_connection_points4808 = frozenset([1])
    FOLLOW_L_PAREN_in_state_entry_exit_points4855 = frozenset([149])
    FOLLOW_statename_in_state_entry_exit_points4857 = frozenset([135, 136])
    FOLLOW_COMMA_in_state_entry_exit_points4860 = frozenset([149])
    FOLLOW_statename_in_state_entry_exit_points4862 = frozenset([135, 136])
    FOLLOW_R_PAREN_in_state_entry_exit_points4866 = frozenset([1])
    FOLLOW_text_area_in_composite_state_body4908 = frozenset([1, 20, 70, 87, 124, 217])
    FOLLOW_procedure_in_composite_state_body4912 = frozenset([1, 20, 70, 87, 124, 217])
    FOLLOW_composite_state_in_composite_state_body4916 = frozenset([1, 20, 70, 87, 124, 217])
    FOLLOW_start_in_composite_state_body4936 = frozenset([1, 20, 87, 124, 217])
    FOLLOW_state_in_composite_state_body4940 = frozenset([1, 20, 87, 217])
    FOLLOW_floating_label_in_composite_state_body4944 = frozenset([1, 20, 87, 217])
    FOLLOW_input_part_in_state_part4969 = frozenset([1])
    FOLLOW_save_part_in_state_part5006 = frozenset([1])
    FOLLOW_spontaneous_transition_in_state_part5041 = frozenset([1])
    FOLLOW_continuous_signal_in_state_part5061 = frozenset([1])
    FOLLOW_connect_part_in_state_part5088 = frozenset([1])
    FOLLOW_cif_in_connect_part5112 = frozenset([19, 217])
    FOLLOW_hyperlink_in_connect_part5131 = frozenset([19])
    FOLLOW_CONNECT_in_connect_part5150 = frozenset([17, 126, 128, 149, 217])
    FOLLOW_connect_list_in_connect_part5152 = frozenset([17, 126, 217])
    FOLLOW_end_in_connect_part5155 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_connect_part5173 = frozenset([1])
    FOLLOW_state_exit_point_name_in_connect_list5231 = frozenset([1, 136])
    FOLLOW_COMMA_in_connect_list5234 = frozenset([149])
    FOLLOW_state_exit_point_name_in_connect_list5236 = frozenset([1, 136])
    FOLLOW_ASTERISK_in_connect_list5279 = frozenset([1])
    FOLLOW_cif_in_spontaneous_transition5302 = frozenset([50, 217])
    FOLLOW_hyperlink_in_spontaneous_transition5321 = frozenset([50])
    FOLLOW_INPUT_in_spontaneous_transition5340 = frozenset([132])
    FOLLOW_NONE_in_spontaneous_transition5342 = frozenset([17, 126, 217])
    FOLLOW_end_in_spontaneous_transition5344 = frozenset([6, 24, 31, 41, 53, 58, 62, 74, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_enabling_condition_in_spontaneous_transition5362 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_spontaneous_transition5381 = frozenset([1])
    FOLLOW_PROVIDED_in_enabling_condition5431 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_enabling_condition5433 = frozenset([17, 126, 217])
    FOLLOW_end_in_enabling_condition5435 = frozenset([1])
    FOLLOW_PROVIDED_in_continuous_signal5479 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_continuous_signal5481 = frozenset([17, 126, 217])
    FOLLOW_end_in_continuous_signal5483 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 133, 137, 147, 149, 217])
    FOLLOW_PRIORITY_in_continuous_signal5502 = frozenset([123])
    FOLLOW_INT_in_continuous_signal5506 = frozenset([17, 126, 217])
    FOLLOW_end_in_continuous_signal5508 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_continuous_signal5528 = frozenset([1])
    FOLLOW_SAVE_in_save_part5578 = frozenset([128, 149])
    FOLLOW_save_list_in_save_part5580 = frozenset([17, 126, 217])
    FOLLOW_end_in_save_part5598 = frozenset([1])
    FOLLOW_signal_list_in_save_list5642 = frozenset([1])
    FOLLOW_asterisk_save_list_in_save_list5662 = frozenset([1])
    FOLLOW_ASTERISK_in_asterisk_save_list5685 = frozenset([1])
    FOLLOW_signal_item_in_signal_list5708 = frozenset([1, 136])
    FOLLOW_COMMA_in_signal_list5711 = frozenset([149])
    FOLLOW_signal_item_in_signal_list5713 = frozenset([1, 136])
    FOLLOW_signal_id_in_signal_item5763 = frozenset([1])
    FOLLOW_cif_in_input_part5792 = frozenset([50, 217])
    FOLLOW_hyperlink_in_input_part5811 = frozenset([50])
    FOLLOW_INPUT_in_input_part5830 = frozenset([128, 149])
    FOLLOW_inputlist_in_input_part5832 = frozenset([17, 126, 217])
    FOLLOW_end_in_input_part5834 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 74, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_enabling_condition_in_input_part5852 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_input_part5871 = frozenset([1])
    FOLLOW_ASTERISK_in_inputlist5949 = frozenset([1])
    FOLLOW_stimulus_in_inputlist5970 = frozenset([1, 136])
    FOLLOW_COMMA_in_inputlist5973 = frozenset([128, 149])
    FOLLOW_stimulus_in_inputlist5975 = frozenset([1, 136])
    FOLLOW_stimulus_id_in_stimulus6023 = frozenset([1, 134])
    FOLLOW_input_params_in_stimulus6025 = frozenset([1])
    FOLLOW_L_PAREN_in_input_params6049 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_input_params6051 = frozenset([135, 136])
    FOLLOW_COMMA_in_input_params6054 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_input_params6056 = frozenset([135, 136])
    FOLLOW_R_PAREN_in_input_params6060 = frozenset([1])
    FOLLOW_action_in_transition6105 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_label_in_transition6108 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_terminator_statement_in_transition6111 = frozenset([1])
    FOLLOW_terminator_statement_in_transition6160 = frozenset([1])
    FOLLOW_label_in_action6204 = frozenset([6, 24, 31, 41, 62, 77, 83, 91, 97, 137, 147, 149, 217])
    FOLLOW_task_in_action6224 = frozenset([1])
    FOLLOW_task_body_in_action6244 = frozenset([1])
    FOLLOW_output_in_action6264 = frozenset([1])
    FOLLOW_create_request_in_action6284 = frozenset([1])
    FOLLOW_decision_in_action6304 = frozenset([1])
    FOLLOW_transition_option_in_action6324 = frozenset([1])
    FOLLOW_set_timer_in_action6344 = frozenset([1])
    FOLLOW_reset_timer_in_action6364 = frozenset([1])
    FOLLOW_export_in_action6384 = frozenset([1])
    FOLLOW_procedure_call_in_action6409 = frozenset([1])
    FOLLOW_EXPORT_in_export6432 = frozenset([134])
    FOLLOW_L_PAREN_in_export6450 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_export6452 = frozenset([135, 136])
    FOLLOW_COMMA_in_export6455 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_export6457 = frozenset([135, 136])
    FOLLOW_R_PAREN_in_export6461 = frozenset([17, 126, 217])
    FOLLOW_end_in_export6479 = frozenset([1])
    FOLLOW_cif_in_procedure_call6527 = frozenset([137, 217])
    FOLLOW_hyperlink_in_procedure_call6546 = frozenset([137])
    FOLLOW_CALL_in_procedure_call6565 = frozenset([149])
    FOLLOW_procedure_call_body_in_procedure_call6567 = frozenset([17, 126, 217])
    FOLLOW_end_in_procedure_call6569 = frozenset([1])
    FOLLOW_procedure_id_in_procedure_call_body6622 = frozenset([1, 134])
    FOLLOW_actual_parameters_in_procedure_call_body6624 = frozenset([1])
    FOLLOW_SET_in_set_timer6672 = frozenset([134])
    FOLLOW_set_statement_in_set_timer6674 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_set_timer6677 = frozenset([134])
    FOLLOW_set_statement_in_set_timer6679 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_set_timer6699 = frozenset([1])
    FOLLOW_L_PAREN_in_set_statement6740 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_set_statement6743 = frozenset([136])
    FOLLOW_COMMA_in_set_statement6745 = frozenset([149])
    FOLLOW_timer_id_in_set_statement6749 = frozenset([135])
    FOLLOW_R_PAREN_in_set_statement6751 = frozenset([1])
    FOLLOW_RESET_in_reset_timer6807 = frozenset([149])
    FOLLOW_reset_statement_in_reset_timer6809 = frozenset([17, 126, 136, 217])
    FOLLOW_COMMA_in_reset_timer6812 = frozenset([149])
    FOLLOW_reset_statement_in_reset_timer6814 = frozenset([17, 126, 136, 217])
    FOLLOW_end_in_reset_timer6834 = frozenset([1])
    FOLLOW_timer_id_in_reset_statement6875 = frozenset([1, 134])
    FOLLOW_L_PAREN_in_reset_statement6878 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_list_in_reset_statement6880 = frozenset([135])
    FOLLOW_R_PAREN_in_reset_statement6882 = frozenset([1])
    FOLLOW_ALTERNATIVE_in_transition_option6931 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_alternative_question_in_transition_option6933 = frozenset([17, 126, 217])
    FOLLOW_end_in_transition_option6937 = frozenset([134, 217])
    FOLLOW_answer_part_in_transition_option6955 = frozenset([26, 134, 217])
    FOLLOW_alternative_part_in_transition_option6973 = frozenset([138])
    FOLLOW_ENDALTERNATIVE_in_transition_option6991 = frozenset([17, 126, 217])
    FOLLOW_end_in_transition_option6995 = frozenset([1])
    FOLLOW_answer_part_in_alternative_part7042 = frozenset([1, 26, 134, 217])
    FOLLOW_else_part_in_alternative_part7045 = frozenset([1])
    FOLLOW_else_part_in_alternative_part7088 = frozenset([1])
    FOLLOW_expression_in_alternative_question7128 = frozenset([1])
    FOLLOW_informal_text_in_alternative_question7148 = frozenset([1])
    FOLLOW_cif_in_decision7171 = frozenset([24, 217])
    FOLLOW_hyperlink_in_decision7190 = frozenset([24])
    FOLLOW_DECISION_in_decision7209 = frozenset([11, 39, 45, 60, 91, 123, 134, 140, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_question_in_decision7211 = frozenset([17, 126, 217])
    FOLLOW_end_in_decision7215 = frozenset([26, 134, 139, 217])
    FOLLOW_answer_part_in_decision7233 = frozenset([26, 134, 139, 217])
    FOLLOW_alternative_part_in_decision7252 = frozenset([139])
    FOLLOW_ENDDECISION_in_decision7271 = frozenset([17, 126, 217])
    FOLLOW_end_in_decision7275 = frozenset([1])
    FOLLOW_cif_in_answer_part7351 = frozenset([134, 217])
    FOLLOW_hyperlink_in_answer_part7370 = frozenset([134])
    FOLLOW_L_PAREN_in_answer_part7389 = frozenset([11, 39, 45, 60, 91, 123, 134, 141, 142, 143, 144, 145, 146, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_answer_in_answer_part7391 = frozenset([135])
    FOLLOW_R_PAREN_in_answer_part7393 = frozenset([212])
    FOLLOW_212_in_answer_part7395 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_answer_part7397 = frozenset([1])
    FOLLOW_range_condition_in_answer7451 = frozenset([1])
    FOLLOW_informal_text_in_answer7471 = frozenset([1])
    FOLLOW_cif_in_else_part7494 = frozenset([26, 217])
    FOLLOW_hyperlink_in_else_part7513 = frozenset([26])
    FOLLOW_ELSE_in_else_part7532 = frozenset([212])
    FOLLOW_212_in_else_part7534 = frozenset([1, 6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_transition_in_else_part7536 = frozenset([1])
    FOLLOW_expression_in_question7588 = frozenset([1])
    FOLLOW_informal_text_in_question7629 = frozenset([1])
    FOLLOW_ANY_in_question7666 = frozenset([1])
    FOLLOW_closed_range_in_range_condition7709 = frozenset([1])
    FOLLOW_open_range_in_range_condition7713 = frozenset([1])
    FOLLOW_INT_in_closed_range7756 = frozenset([212])
    FOLLOW_212_in_closed_range7758 = frozenset([123])
    FOLLOW_INT_in_closed_range7762 = frozenset([1])
    FOLLOW_constant_in_open_range7810 = frozenset([1])
    FOLLOW_EQ_in_open_range7850 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_NEQ_in_open_range7852 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_GT_in_open_range7854 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_LT_in_open_range7856 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_LE_in_open_range7858 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_GE_in_open_range7860 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_constant_in_open_range7863 = frozenset([1])
    FOLLOW_expression_in_constant7926 = frozenset([1])
    FOLLOW_CREATE_in_create_request7970 = frozenset([148, 149])
    FOLLOW_createbody_in_create_request7988 = frozenset([17, 126, 134, 217])
    FOLLOW_actual_parameters_in_create_request8006 = frozenset([17, 126, 217])
    FOLLOW_end_in_create_request8025 = frozenset([1])
    FOLLOW_process_id_in_createbody8072 = frozenset([1])
    FOLLOW_THIS_in_createbody8092 = frozenset([1])
    FOLLOW_cif_in_output8115 = frozenset([62, 217])
    FOLLOW_hyperlink_in_output8134 = frozenset([62])
    FOLLOW_OUTPUT_in_output8153 = frozenset([149])
    FOLLOW_outputbody_in_output8155 = frozenset([17, 126, 217])
    FOLLOW_end_in_output8157 = frozenset([1])
    FOLLOW_outputstmt_in_outputbody8210 = frozenset([1, 105, 136])
    FOLLOW_COMMA_in_outputbody8213 = frozenset([149])
    FOLLOW_outputstmt_in_outputbody8215 = frozenset([1, 105, 136])
    FOLLOW_to_part_in_outputbody8219 = frozenset([1])
    FOLLOW_signal_id_in_outputstmt8272 = frozenset([1, 134])
    FOLLOW_actual_parameters_in_outputstmt8290 = frozenset([1])
    FOLLOW_TO_in_to_part8314 = frozenset([148, 149, 188, 191, 195])
    FOLLOW_destination_in_to_part8316 = frozenset([1])
    FOLLOW_VIA_in_via_part8360 = frozenset([5, 149])
    FOLLOW_viabody_in_via_part8362 = frozenset([1])
    FOLLOW_ALL_in_viabody8407 = frozenset([1])
    FOLLOW_via_path_in_viabody8446 = frozenset([1])
    FOLLOW_pid_expression_in_destination8490 = frozenset([1])
    FOLLOW_process_id_in_destination8510 = frozenset([1])
    FOLLOW_THIS_in_destination8530 = frozenset([1])
    FOLLOW_via_path_element_in_via_path8553 = frozenset([1, 136])
    FOLLOW_COMMA_in_via_path8556 = frozenset([5, 149])
    FOLLOW_via_path_element_in_via_path8558 = frozenset([1, 136])
    FOLLOW_ID_in_via_path_element8601 = frozenset([1])
    FOLLOW_L_PAREN_in_actual_parameters8624 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_actual_parameters8626 = frozenset([135, 136])
    FOLLOW_COMMA_in_actual_parameters8629 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_actual_parameters8631 = frozenset([135, 136])
    FOLLOW_R_PAREN_in_actual_parameters8635 = frozenset([1])
    FOLLOW_cif_in_task8679 = frozenset([97, 217])
    FOLLOW_hyperlink_in_task8698 = frozenset([97])
    FOLLOW_TASK_in_task8717 = frozenset([17, 41, 91, 126, 149, 217])
    FOLLOW_task_body_in_task8719 = frozenset([17, 126, 217])
    FOLLOW_end_in_task8722 = frozenset([1])
    FOLLOW_assignement_statement_in_task_body8777 = frozenset([1, 136])
    FOLLOW_COMMA_in_task_body8780 = frozenset([149])
    FOLLOW_assignement_statement_in_task_body8782 = frozenset([1, 136])
    FOLLOW_informal_text_in_task_body8828 = frozenset([1, 136])
    FOLLOW_COMMA_in_task_body8831 = frozenset([91])
    FOLLOW_informal_text_in_task_body8833 = frozenset([1, 136])
    FOLLOW_forloop_in_task_body8879 = frozenset([1, 136])
    FOLLOW_COMMA_in_task_body8882 = frozenset([41, 91, 149])
    FOLLOW_forloop_in_task_body8884 = frozenset([1, 136])
    FOLLOW_FOR_in_forloop8941 = frozenset([47, 49, 149])
    FOLLOW_variable_id_in_forloop8943 = frozenset([47])
    FOLLOW_IN_in_forloop8945 = frozenset([76, 149])
    FOLLOW_variable_in_forloop8948 = frozenset([212])
    FOLLOW_range_in_forloop8952 = frozenset([212])
    FOLLOW_212_in_forloop8955 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 150, 217])
    FOLLOW_transition_in_forloop8973 = frozenset([150])
    FOLLOW_ENDFOR_in_forloop8992 = frozenset([1])
    FOLLOW_RANGE_in_range9044 = frozenset([134])
    FOLLOW_L_PAREN_in_range9062 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ground_expression_in_range9066 = frozenset([135, 136])
    FOLLOW_COMMA_in_range9085 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ground_expression_in_range9089 = frozenset([135, 136])
    FOLLOW_COMMA_in_range9094 = frozenset([123])
    FOLLOW_INT_in_range9098 = frozenset([135])
    FOLLOW_R_PAREN_in_range9118 = frozenset([1])
    FOLLOW_variable_in_assignement_statement9170 = frozenset([177])
    FOLLOW_ASSIG_OP_in_assignement_statement9172 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_assignement_statement9174 = frozenset([1])
    FOLLOW_ID_in_variable9221 = frozenset([134, 213])
    FOLLOW_primary_params_in_variable9223 = frozenset([1, 134, 213])
    FOLLOW_ID_in_variable9258 = frozenset([1])
    FOLLOW_set_in_field_selection9311 = frozenset([149])
    FOLLOW_field_name_in_field_selection9317 = frozenset([1])
    FOLLOW_binary_expression_in_expression9340 = frozenset([1])
    FOLLOW_binary_expression_0_in_binary_expression9362 = frozenset([1, 151])
    FOLLOW_IMPLIES_in_binary_expression9366 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_0_in_binary_expression9369 = frozenset([1, 151])
    FOLLOW_binary_expression_1_in_binary_expression_09392 = frozenset([1, 152, 153])
    FOLLOW_OR_in_binary_expression_09398 = frozenset([11, 26, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ELSE_in_binary_expression_09401 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_XOR_in_binary_expression_09407 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_1_in_binary_expression_09412 = frozenset([1, 152, 153])
    FOLLOW_binary_expression_2_in_binary_expression_19435 = frozenset([1, 119])
    FOLLOW_AND_in_binary_expression_19439 = frozenset([11, 39, 45, 60, 91, 103, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_THEN_in_binary_expression_19442 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_2_in_binary_expression_19445 = frozenset([1, 119])
    FOLLOW_binary_expression_3_in_binary_expression_29468 = frozenset([1, 47, 141, 142, 143, 144, 145, 146])
    FOLLOW_EQ_in_binary_expression_29473 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_NEQ_in_binary_expression_29478 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_GT_in_binary_expression_29483 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_GE_in_binary_expression_29488 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_LT_in_binary_expression_29493 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_LE_in_binary_expression_29498 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_IN_in_binary_expression_29503 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_3_in_binary_expression_29508 = frozenset([1, 47, 141, 142, 143, 144, 145, 146])
    FOLLOW_binary_expression_4_in_binary_expression_39531 = frozenset([1, 154, 155, 156])
    FOLLOW_PLUS_in_binary_expression_39536 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_DASH_in_binary_expression_39541 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_APPEND_in_binary_expression_39546 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_4_in_binary_expression_39551 = frozenset([1, 154, 155, 156])
    FOLLOW_unary_expression_in_binary_expression_49574 = frozenset([1, 128, 157, 158, 159])
    FOLLOW_ASTERISK_in_binary_expression_49579 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_DIV_in_binary_expression_49584 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_MOD_in_binary_expression_49589 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_REM_in_binary_expression_49594 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_unary_expression_in_binary_expression_49599 = frozenset([1, 128, 157, 158, 159])
    FOLLOW_primary_expression_in_unary_expression9623 = frozenset([1])
    FOLLOW_NOT_in_unary_expression9641 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_unary_expression_in_unary_expression9644 = frozenset([1])
    FOLLOW_DASH_in_unary_expression9662 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_unary_expression_in_unary_expression9664 = frozenset([1])
    FOLLOW_primary_in_primary_expression9694 = frozenset([1])
    FOLLOW_L_PAREN_in_primary_expression9742 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_primary_expression9744 = frozenset([135])
    FOLLOW_R_PAREN_in_primary_expression9746 = frozenset([1])
    FOLLOW_conditional_ground_expression_in_primary_expression9783 = frozenset([1])
    FOLLOW_BITSTR_in_primary9814 = frozenset([1])
    FOLLOW_OCTSTR_in_primary9833 = frozenset([1])
    FOLLOW_TRUE_in_primary9852 = frozenset([1])
    FOLLOW_FALSE_in_primary9871 = frozenset([1])
    FOLLOW_STRING_in_primary9890 = frozenset([1])
    FOLLOW_NULL_in_primary9908 = frozenset([1])
    FOLLOW_PLUS_INFINITY_in_primary9927 = frozenset([1])
    FOLLOW_MINUS_INFINITY_in_primary9946 = frozenset([1])
    FOLLOW_INT_in_primary9965 = frozenset([1])
    FOLLOW_FLOAT_in_primary9984 = frozenset([1])
    FOLLOW_ID_in_primary10003 = frozenset([212])
    FOLLOW_212_in_primary10005 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_primary10007 = frozenset([1])
    FOLLOW_ID_in_primary10045 = frozenset([134, 213])
    FOLLOW_primary_params_in_primary10047 = frozenset([1, 134, 213])
    FOLLOW_ID_in_primary10086 = frozenset([1])
    FOLLOW_L_BRACKET_in_primary10137 = frozenset([179])
    FOLLOW_R_BRACKET_in_primary10139 = frozenset([1])
    FOLLOW_L_BRACKET_in_primary10183 = frozenset([166])
    FOLLOW_MANTISSA_in_primary10201 = frozenset([123])
    FOLLOW_INT_in_primary10205 = frozenset([136])
    FOLLOW_COMMA_in_primary10207 = frozenset([167])
    FOLLOW_BASE_in_primary10225 = frozenset([123])
    FOLLOW_INT_in_primary10229 = frozenset([136])
    FOLLOW_COMMA_in_primary10231 = frozenset([168])
    FOLLOW_EXPONENT_in_primary10249 = frozenset([123])
    FOLLOW_INT_in_primary10253 = frozenset([179])
    FOLLOW_R_BRACKET_in_primary10271 = frozenset([1])
    FOLLOW_L_BRACKET_in_primary10328 = frozenset([149])
    FOLLOW_named_value_in_primary10346 = frozenset([136, 179])
    FOLLOW_COMMA_in_primary10349 = frozenset([149])
    FOLLOW_named_value_in_primary10351 = frozenset([136, 179])
    FOLLOW_R_BRACKET_in_primary10371 = frozenset([1])
    FOLLOW_L_BRACKET_in_primary10422 = frozenset([11, 39, 60, 91, 123, 149, 161, 162, 163, 164, 165, 178])
    FOLLOW_primary_in_primary10440 = frozenset([136, 179])
    FOLLOW_COMMA_in_primary10443 = frozenset([11, 39, 60, 91, 123, 149, 161, 162, 163, 164, 165, 178])
    FOLLOW_primary_in_primary10445 = frozenset([136, 179])
    FOLLOW_R_BRACKET_in_primary10465 = frozenset([1])
    FOLLOW_STRING_in_informal_text10530 = frozenset([1])
    FOLLOW_ID_in_named_value10576 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_named_value10578 = frozenset([1])
    FOLLOW_L_PAREN_in_primary_params10600 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_list_in_primary_params10602 = frozenset([135])
    FOLLOW_R_PAREN_in_primary_params10604 = frozenset([1])
    FOLLOW_213_in_primary_params10643 = frozenset([123, 149])
    FOLLOW_literal_id_in_primary_params10645 = frozenset([1])
    FOLLOW_primary_in_indexed_primary10692 = frozenset([134])
    FOLLOW_L_PAREN_in_indexed_primary10694 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_list_in_indexed_primary10696 = frozenset([135])
    FOLLOW_R_PAREN_in_indexed_primary10698 = frozenset([1])
    FOLLOW_primary_in_field_primary10721 = frozenset([204, 213])
    FOLLOW_field_selection_in_field_primary10723 = frozenset([1])
    FOLLOW_214_in_structure_primary10746 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_list_in_structure_primary10748 = frozenset([215])
    FOLLOW_215_in_structure_primary10750 = frozenset([1])
    FOLLOW_active_primary_in_active_expression10775 = frozenset([1])
    FOLLOW_variable_access_in_active_primary10798 = frozenset([1])
    FOLLOW_operator_application_in_active_primary10818 = frozenset([1])
    FOLLOW_conditional_expression_in_active_primary10838 = frozenset([1])
    FOLLOW_imperative_operator_in_active_primary10858 = frozenset([1])
    FOLLOW_L_PAREN_in_active_primary10878 = frozenset([45, 47, 49, 134, 140, 149, 169, 170, 171, 181, 188, 191, 195, 216])
    FOLLOW_active_expression_in_active_primary10880 = frozenset([135])
    FOLLOW_R_PAREN_in_active_primary10882 = frozenset([1])
    FOLLOW_216_in_active_primary10902 = frozenset([1])
    FOLLOW_now_expression_in_imperative_operator10929 = frozenset([1])
    FOLLOW_import_expression_in_imperative_operator10949 = frozenset([1])
    FOLLOW_pid_expression_in_imperative_operator10969 = frozenset([1])
    FOLLOW_view_expression_in_imperative_operator10989 = frozenset([1])
    FOLLOW_timer_active_expression_in_imperative_operator11009 = frozenset([1])
    FOLLOW_anyvalue_expression_in_imperative_operator11029 = frozenset([1])
    FOLLOW_ACTIVE_in_timer_active_expression11052 = frozenset([134])
    FOLLOW_L_PAREN_in_timer_active_expression11054 = frozenset([149])
    FOLLOW_timer_id_in_timer_active_expression11056 = frozenset([134, 135])
    FOLLOW_L_PAREN_in_timer_active_expression11059 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_list_in_timer_active_expression11061 = frozenset([135])
    FOLLOW_R_PAREN_in_timer_active_expression11063 = frozenset([135])
    FOLLOW_R_PAREN_in_timer_active_expression11067 = frozenset([1])
    FOLLOW_ANY_in_anyvalue_expression11090 = frozenset([134])
    FOLLOW_L_PAREN_in_anyvalue_expression11092 = frozenset([136, 149])
    FOLLOW_sort_in_anyvalue_expression11094 = frozenset([135])
    FOLLOW_R_PAREN_in_anyvalue_expression11096 = frozenset([1])
    FOLLOW_sort_id_in_sort11114 = frozenset([1])
    FOLLOW_syntype_id_in_syntype11150 = frozenset([1])
    FOLLOW_IMPORT_in_import_expression11173 = frozenset([134])
    FOLLOW_L_PAREN_in_import_expression11175 = frozenset([149])
    FOLLOW_remote_variable_id_in_import_expression11177 = frozenset([135, 136])
    FOLLOW_COMMA_in_import_expression11180 = frozenset([148, 149, 188, 191, 195])
    FOLLOW_destination_in_import_expression11182 = frozenset([135])
    FOLLOW_R_PAREN_in_import_expression11186 = frozenset([1])
    FOLLOW_VIEW_in_view_expression11209 = frozenset([134])
    FOLLOW_L_PAREN_in_view_expression11211 = frozenset([149])
    FOLLOW_view_id_in_view_expression11213 = frozenset([135, 136])
    FOLLOW_COMMA_in_view_expression11216 = frozenset([188, 191, 195])
    FOLLOW_pid_expression_in_view_expression11218 = frozenset([135])
    FOLLOW_R_PAREN_in_view_expression11222 = frozenset([1])
    FOLLOW_variable_id_in_variable_access11245 = frozenset([1])
    FOLLOW_operator_id_in_operator_application11268 = frozenset([134])
    FOLLOW_L_PAREN_in_operator_application11270 = frozenset([45, 47, 49, 134, 140, 149, 169, 170, 171, 181, 188, 191, 195, 216])
    FOLLOW_active_expression_list_in_operator_application11271 = frozenset([135])
    FOLLOW_R_PAREN_in_operator_application11273 = frozenset([1])
    FOLLOW_active_expression_in_active_expression_list11296 = frozenset([1, 136])
    FOLLOW_COMMA_in_active_expression_list11299 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_list_in_active_expression_list11301 = frozenset([1])
    FOLLOW_IF_in_conditional_expression11333 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_conditional_expression11335 = frozenset([103])
    FOLLOW_THEN_in_conditional_expression11337 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_conditional_expression11339 = frozenset([26])
    FOLLOW_ELSE_in_conditional_expression11341 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_conditional_expression11343 = frozenset([34])
    FOLLOW_FI_in_conditional_expression11345 = frozenset([1])
    FOLLOW_external_synonym_id_in_external_synonym11371 = frozenset([1])
    FOLLOW_IF_in_conditional_ground_expression11394 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_conditional_ground_expression11398 = frozenset([103])
    FOLLOW_THEN_in_conditional_ground_expression11416 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_conditional_ground_expression11420 = frozenset([26])
    FOLLOW_ELSE_in_conditional_ground_expression11438 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_conditional_ground_expression11442 = frozenset([34])
    FOLLOW_FI_in_conditional_ground_expression11444 = frozenset([1])
    FOLLOW_expression_in_expression_list11495 = frozenset([1, 136])
    FOLLOW_COMMA_in_expression_list11498 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_expression_list11500 = frozenset([1, 136])
    FOLLOW_label_in_terminator_statement11543 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_cif_in_terminator_statement11562 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_hyperlink_in_terminator_statement11581 = frozenset([6, 24, 31, 41, 53, 58, 62, 77, 78, 83, 90, 91, 97, 137, 147, 149, 217])
    FOLLOW_terminator_in_terminator_statement11600 = frozenset([17, 126, 217])
    FOLLOW_end_in_terminator_statement11618 = frozenset([1])
    FOLLOW_cif_in_label11673 = frozenset([149, 217])
    FOLLOW_connector_name_in_label11676 = frozenset([212])
    FOLLOW_212_in_label11678 = frozenset([1])
    FOLLOW_nextstate_in_terminator11725 = frozenset([1])
    FOLLOW_join_in_terminator11729 = frozenset([1])
    FOLLOW_stop_in_terminator11733 = frozenset([1])
    FOLLOW_return_stmt_in_terminator11737 = frozenset([1])
    FOLLOW_JOIN_in_join11761 = frozenset([149, 217])
    FOLLOW_connector_name_in_join11763 = frozenset([1])
    FOLLOW_STOP_in_stop11803 = frozenset([1])
    FOLLOW_RETURN_in_return_stmt11826 = frozenset([1, 11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_return_stmt11828 = frozenset([1])
    FOLLOW_NEXTSTATE_in_nextstate11874 = frozenset([149, 155])
    FOLLOW_nextstatebody_in_nextstate11876 = frozenset([1])
    FOLLOW_statename_in_nextstatebody11920 = frozenset([1, 111])
    FOLLOW_via_in_nextstatebody11922 = frozenset([1])
    FOLLOW_dash_nextstate_in_nextstatebody11943 = frozenset([1])
    FOLLOW_VIA_in_via11962 = frozenset([149])
    FOLLOW_state_entry_point_name_in_via11964 = frozenset([1])
    FOLLOW_cif_in_end12005 = frozenset([17, 217])
    FOLLOW_hyperlink_in_end12008 = frozenset([17])
    FOLLOW_COMMENT_in_end12011 = frozenset([91])
    FOLLOW_STRING_in_end12013 = frozenset([126])
    FOLLOW_SEMI_in_end12017 = frozenset([1])
    FOLLOW_cif_decl_in_cif12063 = frozenset([7, 17, 19, 24, 50, 53, 54, 58, 62, 70, 71, 73, 74, 78, 87, 90, 97, 100, 124])
    FOLLOW_symbolname_in_cif12065 = frozenset([134])
    FOLLOW_L_PAREN_in_cif12083 = frozenset([123])
    FOLLOW_INT_in_cif12087 = frozenset([136])
    FOLLOW_COMMA_in_cif12089 = frozenset([123])
    FOLLOW_INT_in_cif12093 = frozenset([135])
    FOLLOW_R_PAREN_in_cif12095 = frozenset([136])
    FOLLOW_COMMA_in_cif12113 = frozenset([134])
    FOLLOW_L_PAREN_in_cif12131 = frozenset([123])
    FOLLOW_INT_in_cif12135 = frozenset([136])
    FOLLOW_COMMA_in_cif12137 = frozenset([123])
    FOLLOW_INT_in_cif12141 = frozenset([135])
    FOLLOW_R_PAREN_in_cif12143 = frozenset([218])
    FOLLOW_cif_end_in_cif12161 = frozenset([1])
    FOLLOW_cif_decl_in_hyperlink12215 = frozenset([172])
    FOLLOW_KEEP_in_hyperlink12217 = frozenset([173])
    FOLLOW_SPECIFIC_in_hyperlink12219 = frozenset([174])
    FOLLOW_GEODE_in_hyperlink12221 = frozenset([44])
    FOLLOW_HYPERLINK_in_hyperlink12223 = frozenset([91])
    FOLLOW_STRING_in_hyperlink12225 = frozenset([218])
    FOLLOW_cif_end_in_hyperlink12243 = frozenset([1])
    FOLLOW_cif_decl_in_paramnames12288 = frozenset([172])
    FOLLOW_KEEP_in_paramnames12290 = frozenset([173])
    FOLLOW_SPECIFIC_in_paramnames12292 = frozenset([174])
    FOLLOW_GEODE_in_paramnames12294 = frozenset([65])
    FOLLOW_PARAMNAMES_in_paramnames12296 = frozenset([149])
    FOLLOW_field_name_in_paramnames12298 = frozenset([149, 218])
    FOLLOW_cif_end_in_paramnames12301 = frozenset([1])
    FOLLOW_cif_decl_in_use_asn112348 = frozenset([172])
    FOLLOW_KEEP_in_use_asn112350 = frozenset([173])
    FOLLOW_SPECIFIC_in_use_asn112352 = frozenset([174])
    FOLLOW_GEODE_in_use_asn112354 = frozenset([175])
    FOLLOW_ASNFILENAME_in_use_asn112356 = frozenset([91])
    FOLLOW_STRING_in_use_asn112358 = frozenset([218])
    FOLLOW_cif_end_in_use_asn112360 = frozenset([1])
    FOLLOW_set_in_symbolname0 = frozenset([1])
    FOLLOW_217_in_cif_decl12787 = frozenset([1])
    FOLLOW_218_in_cif_end12810 = frozenset([1])
    FOLLOW_cif_decl_in_cif_end_text12833 = frozenset([30])
    FOLLOW_ENDTEXT_in_cif_end_text12835 = frozenset([218])
    FOLLOW_cif_end_in_cif_end_text12837 = frozenset([1])
    FOLLOW_cif_decl_in_cif_end_label12878 = frozenset([176])
    FOLLOW_END_in_cif_end_label12880 = frozenset([54])
    FOLLOW_LABEL_in_cif_end_label12882 = frozenset([218])
    FOLLOW_cif_end_in_cif_end_label12884 = frozenset([1])
    FOLLOW_DASH_in_dash_nextstate12900 = frozenset([1])
    FOLLOW_ID_in_connector_name12914 = frozenset([1])
    FOLLOW_ID_in_signal_id12933 = frozenset([1])
    FOLLOW_ID_in_statename12952 = frozenset([1])
    FOLLOW_ID_in_state_exit_point_name12981 = frozenset([1])
    FOLLOW_ID_in_state_entry_point_name13010 = frozenset([1])
    FOLLOW_ID_in_variable_id13027 = frozenset([1])
    FOLLOW_set_in_literal_id0 = frozenset([1])
    FOLLOW_ID_in_process_id13067 = frozenset([1])
    FOLLOW_ID_in_system_name13084 = frozenset([1])
    FOLLOW_ID_in_package_name13100 = frozenset([1])
    FOLLOW_ID_in_priority_signal_id13129 = frozenset([1])
    FOLLOW_ID_in_signal_list_id13143 = frozenset([1])
    FOLLOW_ID_in_timer_id13163 = frozenset([1])
    FOLLOW_ID_in_field_name13181 = frozenset([1])
    FOLLOW_ID_in_signal_route_id13194 = frozenset([1])
    FOLLOW_ID_in_channel_id13212 = frozenset([1])
    FOLLOW_ID_in_route_id13232 = frozenset([1])
    FOLLOW_ID_in_block_id13252 = frozenset([1])
    FOLLOW_ID_in_source_id13271 = frozenset([1])
    FOLLOW_ID_in_dest_id13292 = frozenset([1])
    FOLLOW_ID_in_gate_id13313 = frozenset([1])
    FOLLOW_ID_in_procedure_id13329 = frozenset([1])
    FOLLOW_ID_in_remote_procedure_id13358 = frozenset([1])
    FOLLOW_ID_in_operator_id13375 = frozenset([1])
    FOLLOW_ID_in_synonym_id13393 = frozenset([1])
    FOLLOW_ID_in_external_synonym_id13422 = frozenset([1])
    FOLLOW_ID_in_remote_variable_id13451 = frozenset([1])
    FOLLOW_ID_in_view_id13472 = frozenset([1])
    FOLLOW_ID_in_sort_id13493 = frozenset([1])
    FOLLOW_ID_in_syntype_id13511 = frozenset([1])
    FOLLOW_ID_in_stimulus_id13528 = frozenset([1])
    FOLLOW_S_in_pid_expression14562 = frozenset([186])
    FOLLOW_E_in_pid_expression14564 = frozenset([185])
    FOLLOW_L_in_pid_expression14566 = frozenset([193])
    FOLLOW_F_in_pid_expression14568 = frozenset([1])
    FOLLOW_P_in_pid_expression14594 = frozenset([180])
    FOLLOW_A_in_pid_expression14596 = frozenset([189])
    FOLLOW_R_in_pid_expression14598 = frozenset([186])
    FOLLOW_E_in_pid_expression14600 = frozenset([181])
    FOLLOW_N_in_pid_expression14602 = frozenset([197])
    FOLLOW_T_in_pid_expression14604 = frozenset([1])
    FOLLOW_O_in_pid_expression14630 = frozenset([193])
    FOLLOW_F_in_pid_expression14632 = frozenset([193])
    FOLLOW_F_in_pid_expression14634 = frozenset([191])
    FOLLOW_S_in_pid_expression14636 = frozenset([188])
    FOLLOW_P_in_pid_expression14638 = frozenset([189])
    FOLLOW_R_in_pid_expression14640 = frozenset([192])
    FOLLOW_I_in_pid_expression14642 = frozenset([181])
    FOLLOW_N_in_pid_expression14644 = frozenset([194])
    FOLLOW_G_in_pid_expression14646 = frozenset([1])
    FOLLOW_S_in_pid_expression14672 = frozenset([186])
    FOLLOW_E_in_pid_expression14674 = frozenset([181])
    FOLLOW_N_in_pid_expression14676 = frozenset([183])
    FOLLOW_D_in_pid_expression14678 = frozenset([186])
    FOLLOW_E_in_pid_expression14680 = frozenset([189])
    FOLLOW_R_in_pid_expression14682 = frozenset([1])
    FOLLOW_N_in_now_expression14696 = frozenset([195])
    FOLLOW_O_in_now_expression14698 = frozenset([201])
    FOLLOW_W_in_now_expression14700 = frozenset([1])
    FOLLOW_text_area_in_synpred24_sdl922224 = frozenset([1])
    FOLLOW_procedure_in_synpred25_sdl922228 = frozenset([1])
    FOLLOW_composite_state_in_synpred26_sdl922232 = frozenset([1])
    FOLLOW_processBody_in_synpred27_sdl922252 = frozenset([1])
    FOLLOW_text_area_in_synpred31_sdl922417 = frozenset([1])
    FOLLOW_procedure_in_synpred32_sdl922421 = frozenset([1])
    FOLLOW_processBody_in_synpred33_sdl922443 = frozenset([1])
    FOLLOW_content_in_synpred40_sdl922749 = frozenset([1])
    FOLLOW_text_area_in_synpred84_sdl924908 = frozenset([1])
    FOLLOW_procedure_in_synpred85_sdl924912 = frozenset([1])
    FOLLOW_composite_state_in_synpred86_sdl924916 = frozenset([1])
    FOLLOW_enabling_condition_in_synpred108_sdl925852 = frozenset([1])
    FOLLOW_label_in_synpred115_sdl926108 = frozenset([1])
    FOLLOW_expression_in_synpred139_sdl927128 = frozenset([1])
    FOLLOW_answer_part_in_synpred142_sdl927233 = frozenset([1])
    FOLLOW_range_condition_in_synpred147_sdl927451 = frozenset([1])
    FOLLOW_expression_in_synpred151_sdl927588 = frozenset([1])
    FOLLOW_informal_text_in_synpred152_sdl927629 = frozenset([1])
    FOLLOW_COMMA_in_synpred182_sdl929085 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ground_expression_in_synpred182_sdl929089 = frozenset([1])
    FOLLOW_IMPLIES_in_synpred187_sdl929366 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_0_in_synpred187_sdl929369 = frozenset([1])
    FOLLOW_OR_in_synpred190_sdl929398 = frozenset([11, 26, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_ELSE_in_synpred190_sdl929401 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_XOR_in_synpred190_sdl929407 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_1_in_synpred190_sdl929412 = frozenset([1])
    FOLLOW_AND_in_synpred192_sdl929439 = frozenset([11, 39, 45, 60, 91, 103, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_THEN_in_synpred192_sdl929442 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_2_in_synpred192_sdl929445 = frozenset([1])
    FOLLOW_set_in_synpred199_sdl929471 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_3_in_synpred199_sdl929508 = frozenset([1])
    FOLLOW_set_in_synpred202_sdl929534 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_binary_expression_4_in_synpred202_sdl929551 = frozenset([1])
    FOLLOW_set_in_synpred206_sdl929577 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_unary_expression_in_synpred206_sdl929599 = frozenset([1])
    FOLLOW_ID_in_synpred221_sdl9210003 = frozenset([212])
    FOLLOW_212_in_synpred221_sdl9210005 = frozenset([11, 39, 45, 60, 91, 123, 134, 149, 155, 160, 161, 162, 163, 164, 165, 178])
    FOLLOW_expression_in_synpred221_sdl9210007 = frozenset([1])
    FOLLOW_primary_params_in_synpred222_sdl9210047 = frozenset([1])
    FOLLOW_ID_in_synpred223_sdl9210045 = frozenset([134, 213])
    FOLLOW_primary_params_in_synpred223_sdl9210047 = frozenset([1, 134, 213])
    FOLLOW_ID_in_synpred224_sdl9210086 = frozenset([1])
    FOLLOW_L_BRACKET_in_synpred225_sdl9210137 = frozenset([179])
    FOLLOW_R_BRACKET_in_synpred225_sdl9210139 = frozenset([1])
    FOLLOW_L_BRACKET_in_synpred226_sdl9210183 = frozenset([166])
    FOLLOW_MANTISSA_in_synpred226_sdl9210201 = frozenset([123])
    FOLLOW_INT_in_synpred226_sdl9210205 = frozenset([136])
    FOLLOW_COMMA_in_synpred226_sdl9210207 = frozenset([167])
    FOLLOW_BASE_in_synpred226_sdl9210225 = frozenset([123])
    FOLLOW_INT_in_synpred226_sdl9210229 = frozenset([136])
    FOLLOW_COMMA_in_synpred226_sdl9210231 = frozenset([168])
    FOLLOW_EXPONENT_in_synpred226_sdl9210249 = frozenset([123])
    FOLLOW_INT_in_synpred226_sdl9210253 = frozenset([179])
    FOLLOW_R_BRACKET_in_synpred226_sdl9210271 = frozenset([1])
    FOLLOW_L_BRACKET_in_synpred228_sdl9210328 = frozenset([149])
    FOLLOW_named_value_in_synpred228_sdl9210346 = frozenset([136, 179])
    FOLLOW_COMMA_in_synpred228_sdl9210349 = frozenset([149])
    FOLLOW_named_value_in_synpred228_sdl9210351 = frozenset([136, 179])
    FOLLOW_R_BRACKET_in_synpred228_sdl9210371 = frozenset([1])



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import ParserMain
    main = ParserMain("sdl92Lexer", sdl92Parser)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
