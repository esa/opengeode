#!/usr/bin/env python

import ogAST

class Generator:
   ''' Main class for generating code from SDL models '''

   def __init__(self, fileName, usedebug, forTaste):
      self.forTaste = forTaste
      self.debug = usedebug
      self.indent = 0 
      self.fileName = fileName

   def indent_increase(self):
      self.indent = self.indent + 3

   def dataPrefix (self):
      if self.forTaste:
         return "asn1Scc"
      else:
         return ""

   def indent_decrease(self):
      self.indent = self.indent - 3

   def indent_write (self, afile):
       t = 0
       while (t < self.indent):
         afile.write (" ")
         t = t + 1

   def write (self, afile, content, indent=True):
       if indent: self.indent_write (afile)
       afile.write (content)

   def mappingReactionFunction (self, process):
       return process.processName+"process"

   def mappingNbOutputsMacro (self, process):
      return process.processName.upper() + "_NB_OUTPUTS"

   def mappingSignal (self, process, signalName):
      return process.processName.lower() + "_" + signalName.lower()

   def mappingTasteVariableIn (self, process):
      return process.processName.lower() + "_helper_in"

   def mappingTasteVariableOut (self, process):
      return process.processName.lower() + "_helper_out"

   def mappingTasteVariableType (self, process):
      return process.processName.lower() + "_data_t"

   def mappingState (self, process, stateName):
      return process.processName.upper() + "_" + stateName.upper()

   def generateTasteSource (self, srcfile, pr):
       inputSignals = pr.inputSignals
       outputSignals = pr.outputSignals

       self.write (srcfile,"#include \""+self.fileName+".h\"\n\n")
       self.write (srcfile,"#include \""+self.fileName+"_taste.h\"\n\n")

       self.write (srcfile,self.mappingTasteVariableType (pr))
       self.write (srcfile," ")
       self.write (srcfile,self.mappingTasteVariableIn (pr))
       self.write (srcfile,";\n")


       self.write (srcfile,self.mappingTasteVariableType (pr))
       self.write (srcfile," ")
       self.write (srcfile,self.mappingTasteVariableOut (pr))
       self.write (srcfile,";\n\n")

       self.write (srcfile,"void " + pr.processName + "_startup (void)\n")
       self.write (srcfile,"{\n")
       self.indent_increase()
       self.write (srcfile,pr.processName+"process_init (&"+self.mappingTasteVariableOut(pr) + ");\n")
       self.write (srcfile,pr.processName+"process_init (&"+self.mappingTasteVariableIn(pr) + ");\n")
       self.indent_decrease()
       self.write (srcfile,"}\n")

       for pr_input in pr.inputSignals:
           signame = pr_input.keys()[0]
           self.write (srcfile,"void " + pr.processName + "_PI_" + signame + " (void) \n")
           self.write (srcfile,"{\n")
           self.indent_increase()
           self.write (srcfile,pr.processName + "_helper_in = " + pr.processName + "_helper_out;\n")
           self.write (srcfile,pr.processName + "_helper_in.input.value = " + pr.processName + "_" + signame + ";\n")
           self.write (srcfile,self.mappingReactionFunction (pr) + " (&"+ self.mappingTasteVariableIn (pr) + ", &"+ self.mappingTasteVariableOut (pr) + ");\n")
           self.indent_decrease()
           self.write (srcfile,"}\n")


   def generateTasteHeader (self, hdrfile, pr):
       inputSignals = pr.inputSignals
       outputSignals = pr.outputSignals
       nbOutputSignals = 0

       declared_inputs = {}

       self.write (hdrfile, "#ifndef __OPENGEODE_TASTE_"+pr.processName.upper() + "_H__\n")
       self.write (hdrfile, "#define __OPENGEODE_TASTE_"+pr.processName.upper() + "_H__\n")
       self.write (hdrfile, "#include \"asn1crt.h\"\n")

       self.write (hdrfile, "#include \"C_ASN1_Types.h\"\n")
       self.write (hdrfile,"#include \""+self.fileName+".h\"\n")

       hdrfile.write ("\n")

       hdrfile.write ("extern ")
       hdrfile.write (pr.processName)
       hdrfile.write ("_data_t ")
       hdrfile.write ("opengeode_")
       hdrfile.write (pr.processName)
       hdrfile.write ("_helper_in;\n")

       hdrfile.write ("extern ")
       hdrfile.write (pr.processName)
       hdrfile.write ("_data_t ")
       hdrfile.write ("opengeode_")
       hdrfile.write (pr.processName)
       hdrfile.write ("_helper_out;\n")


       hdrfile.write ("void " + pr.processName + "_startup (void);\n")

       for pr_input in pr.inputSignals:
           signame = pr_input.keys()[0]
           hdrfile.write ("void " + pr.processName + "_PI_" + signame + "();\n")

       hdrfile.write ("\n")


       self.write (hdrfile,"#endif\n")
 

   def generateHeaderRuntime (self, hdrfile):

       hdrfile.write ("\n")
       hdrfile.write ("#ifndef __OPENGEODE_RUNTIME__")
       hdrfile.write ("\n")
       hdrfile.write ("#define __OPENGEODE_RUNTIME__")
       hdrfile.write ("\n")
       hdrfile.write ("#ifndef OPENGEODE_TRUE\n")
       hdrfile.write ("#define OPENGEODE_TRUE 1\n")
       hdrfile.write ("#endif\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("#ifndef OPENGEODE_FALSE\n")
       hdrfile.write ("#define OPENGEODE_FALSE 0\n")
       hdrfile.write ("#endif\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("#ifndef OPENGEODE_NULL\n")
       hdrfile.write ("#define OPENGEODE_NULL 0\n")
       hdrfile.write ("#endif\n")
       hdrfile.write ("\n")
       hdrfile.write ("#ifdef OPENGEODEDEBUG\n")
       hdrfile.write ("#include <stdio.h>\n")
       hdrfile.write ("#define OPENGEODEDEBUGMSG(s, args...) fprintf(stderr, s, ##args); fflush (stderr);\n")
       hdrfile.write ("#else\n")
       hdrfile.write ("#define OPENGEODEDEBUGMSG(s, args...)\n")
       hdrfile.write ("#endif\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("#ifndef OPENGEODE_MAX_OUTPUTS\n");
       hdrfile.write ("#define OPENGEODE_MAX_OUTPUTS 42\n");
       hdrfile.write ("#endif\n");
       hdrfile.write ("\n")
       hdrfile.write ("\n")

       hdrfile.write ("#define OPENGEODE_OUTPUT_REGISTER_CALLBACK(data,signame,callback) {data.outputs.output_callbacks[signame]=callback;data.outputs.output_mgmt[signame] = OUTPUT_MGMT_CALLBACK;}\n");
       hdrfile.write ("\n")
       hdrfile.write ("\n")

       hdrfile.write ("#define OPENGEODE_OUTPUT_USER_CALLBACK(data,signame,callback) {data.outputs.output_callbacks[signame]=callback;data.outputs.output_mgmt[signame] = OUTPUT_MGMT_USER;}\n");
       hdrfile.write ("\n")
       hdrfile.write ("\n")

       hdrfile.write ("typedef enum\n");
       hdrfile.write ("{\n");
       hdrfile.write ("   OUTPUT_MGMT_NORMAL   = 1,\n");
       hdrfile.write ("   OUTPUT_MGMT_CALLBACK = 2,\n");
       hdrfile.write ("   OUTPUT_MGMT_USER     = 4,\n");
       hdrfile.write ("}opengeode_output_mgmt_kind_t;\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("typedef int opengeode_boolean_t;\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("typedef void (*opengeode_output_callback_t) (void*);\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("#endif /* OpenGeode Runtime */")
       hdrfile.write ("\n")
       hdrfile.write ("\n")
       hdrfile.write ("\n")

   def generateExpression (self, expr):
#       print "expression, left=", expr.left, ",right=",expr.right,"kind=" , expr.kind

       if expr.kind == "primary":
#           print "var=", expr.var, "inputString=", expr.var.inputString, "primaryType=", expr.var.primType
#           print "var=", expr.var, "inputString=", expr.var.inputString, "primaryId=", expr.var.primaryId
           if expr.var.kind == 'enumeratedValue':
              return self.dataPrefix() + expr.inputString
           elif expr.var.primType['Kind'] == 'ReferenceType':
               return "output->vars."+ expr.var.inputString
           else:
               if len (expr.var.primaryId) > 1:
                  s = expr.var.primaryId[0]
                  i = 1
                  while i < len (expr.var.primaryId):
                     s = s + "." + expr.var.primaryId[i]
                     i = i + 1
                  return "output->vars." + s

               else:
                  print "type" , expr.exprType
                  return expr.var.inputString
       else:
           if expr.kind == "assign":
               sign = " = "
           elif expr.kind == "plus":
               sign = " + "
           elif expr.kind == "minus":
               sign = " - "
           elif expr.kind == "mul":
               sign = " * "
           elif expr.kind == "or":
               sign = " | "
           elif expr.kind == "and":
               sign = " & "
           elif expr.kind == "xor":
               sign = " ^ "
           elif expr.kind == "eq":
               sign = " == "
           elif expr.kind == "neq":
               sign = " != "
           elif expr.kind == "gt":
               sign = " > "
           elif expr.kind == "ge":
               sign = " >= "
           elif expr.kind == "lt":
               sign = " < "
           elif expr.kind == "le":
               sign = " <= "
           elif expr.kind == "div":
               sign = " / "
           elif expr.kind == "mod":
               sign = " % "
           elif expr.kind == "append":
               sign = " motimplemented "
           elif expr.kind == "in":
               sign = " notimplemented "
           elif expr.kind == "rem":
               sign = " notimplemented "
           else:
               sign = "unknown"
       return  self.generateExpression (expr.left) + sign + self.generateExpression (expr.right)


   def generateAction (self, srcFile, pr, a):

#       print "   Generate action: ", a.inputString
       if isinstance (a, ogAST.Task):
#           print "   kind=task\n"
           for e in a.assign:
#              print "assign=", e , "inputString", e.inputString , "\n"
              if isinstance (e, ogAST.Expression):
                 self.write (srcFile, self.generateExpression (e) + ";\n")


       if isinstance (a, ogAST.Decision):
#           print "   kind=decision\n"
           decision = a
           op = "na"
#           print "Generating decision"
           if len (a.answers) == 2 and ( (a.answers[0].inputString.lower() == "true") or (a.answers[0].inputString.lower() == "false")) :

             self.write (srcFile,"if ("+self.generateExpression (decision.question)+ ")\n") 
             self.write (srcFile,"{\n")
             self.indent_increase()
             if a.answers[0].inputString.lower() == "true":
               self.generateTransition (srcFile, pr, "none", a.answers[0].transition)
             if a.answers[1].inputString.lower() == "true":
               self.generateTransition (srcFile, pr, "none", a.answers[0].transition)
             self.indent_decrease()
             self.write (srcFile,"}\n")
             self.write (srcFile,"else\n")
             self.write (srcFile,"{\n")
             self.indent_increase()
             if a.answers[0].inputString.lower() == "false":
               self.generateTransition (srcFile, pr, "none", a.answers[1].transition)
             if a.answers[1].inputString.lower() == "false":
               self.generateTransition (srcFile, pr, "none", a.answers[1].transition)
             self.indent_decrease()
             self.write (srcFile,"}\n")
             return


           for answer in a.answers: 
#              print "kind="+ answer.kind
              if answer.kind == "constant":
#                 print "constant=" ,  answer.constant
                 self.write (srcFile,"if ("+self.generateExpression (decision.question)+ " == " + self.generateExpression (answer.constant) + ")\n") 
                 self.write (srcFile,"{\n")
                 self.indent_increase()
                 self.write (srcFile, "/* Start generating answer */\n")
                 self.generateTransition (srcFile, pr, "none", answer.transition)
                 self.write (srcFile, "/* Finish generating answer */\n")
                 self.indent_decrease()
                 self.write (srcFile,"}\n")
#           print "End of generating decision"

       if isinstance (a, ogAST.Output):
#           print "   kind=output\n"
#           print "output activity, kind=", a.kind
           if a.kind == "procedure_call":
               for o in a.output:
                   self.write (srcFile,"OPENGEODEDEBUGMSG (\"Procedure call to function "+ o['outputName'] +" \\n\");\n") 
                   params = ""
                   for p in o['params']: 
                      if params != "": 
                          params = params + ","
                      params = params + "&(" + self.generateExpression (p) + ")"
                   self.write (srcFile, o['outputName'] + " (" + params + ");\n") 
           else:
               for o in a.output:
                  self.write (srcFile,"output->outputs.") 
                  self.write (srcFile,self.mappingSignal(pr, o['outputName']),indent=False) 
                  self.write (srcFile," = OPENGEODE_TRUE;",indent=False) 
                  self.write (srcFile,"\n",indent=False) 
                  if o.has_key('params'):
                     for e in o['params']:
                        self.write (srcFile,"if ((output->outputs.output_mgmt["+self.mappingSignal (pr, o['outputName'])+"] & OUTPUT_MGMT_USER) == 0)\n") 
                        self.write (srcFile,"{\n") 
                        self.indent_increase()
                        self.write (srcFile,"OPENGEODEDEBUGMSG (\"Try to register the output " + self.mappingSignal (pr, o['outputName']) + "\\n\");\n") 

                        self.write (srcFile,"if (output->outputs.outputs_amount < OPENGEODE_MAX_OUTPUTS)\n") 
                        self.write (srcFile,"{\n") 
                        self.indent_increase()
                        self.write (srcFile,"OPENGEODEDEBUGMSG (\"Register the output " + self.mappingSignal (pr, o['outputName']) + "\\n\");\n") 
                        self.write (srcFile,"output->outputs.values." + self.mappingSignal (pr, o['outputName']) + " = " + self.generateExpression (e) + ";\n") 
                        self.write (srcFile,"output->outputs.outputs_order[output->outputs.outputs_amount] = " + self.mappingSignal (pr, o['outputName']) + ";\n") 
                        self.write (srcFile,"output->outputs.outputs_amount = output->outputs.outputs_amount + 1;\n") 
                        self.indent_decrease()
                        self.write (srcFile,"}\n") 

                        self.write (srcFile,"if ((output->outputs.output_mgmt["+self.mappingSignal (pr, o['outputName'])+"] & OUTPUT_MGMT_CALLBACK) == OUTPUT_MGMT_CALLBACK)\n") 
                        self.write (srcFile,"{\n") 
                        self.indent_increase()
                        self.write (srcFile,"OPENGEODEDEBUGMSG (\"Call callback for output " + self.mappingSignal (pr, o['outputName']) + "\\n\");\n") 
                        self.write (srcFile,"output->outputs.output_callbacks["+ self.mappingSignal (pr, o['outputName']) + "](NULL);\n") 
                        self.indent_decrease()
                        self.write (srcFile,"}\n") 

                        self.indent_decrease()
                        self.write (srcFile,"}\n") 
                        self.write (srcFile,"else\n") 
                        self.write (srcFile,"{\n") 
                        self.indent_increase()
                        self.write (srcFile,"OPENGEODEDEBUGMSG (\"Call callback for output " + self.mappingSignal (pr, o['outputName']) + " without registering\\n\");\n") 
                        self.write (srcFile,"output->outputs.output_callbacks["+ self.mappingSignal (pr, o['outputName']) + "](output);\n") 
                        self.indent_decrease()
                        self.write (srcFile,"}\n") 

   def generateTransition (self, srcFile, pr, inputsignal, trans):
       if trans is None:
           return

#       print "Generate transition when receiving signal ( ", inputsignal , "):"
       if hasattr (trans, 'actions') and len (trans.actions) > 0:
#           print "Number of actions=" , len (trans.actions)
           for a in trans.actions:
               self.generateAction (srcFile, pr, a)


       if trans.terminator != None and trans.terminator.kind == "next_state" and trans.terminator.inputString != "-":
           if self.debug:
               self.write (srcFile,"OPENGEODEDEBUGMSG (\"Going to state  " + self.mappingState (pr, trans.terminator.inputString) + "\\n\");\n") 
           self.write (srcFile,"output->state = ") 
           self.write (srcFile,self.mappingState (pr, trans.terminator.inputString),indent=False) 
           self.write (srcFile,";\n",indent=False) 

#       print "End of transition generation for signal " , inputsignal

   def generateStateCase (self, srcFile, pr, stateName):
      inputs = pr.mapping[stateName]
      if isinstance (inputs, int):
          self.generateTransition (srcFile, pr, "", pr.transitions[inputs])

      if isinstance (inputs, list):

          self.write (srcFile,"switch (input->input.value)\n");
          self.write (srcFile,"{\n");
          self.indent_increase()
          for i in inputs:
              for inputSignal in i.inputlist.keys():
                  tidx = i.inputlist[inputSignal]
                  self.write (srcFile,"case (");
                  self.write (srcFile,self.mappingSignal (pr, inputSignal), indent=False);
                  self.write (srcFile,"):\n",indent=False);
                  self.write (srcFile,"{\n");

                  self.indent_increase()
                  self.write (srcFile,"OPENGEODEDEBUGMSG (\"Received signal " + self.mappingSignal (pr, inputSignal) + "\\n\");\n") 
                  # Now, we try to see if the input signal received some values
                  for p in i.parameters:
                      self.write (srcFile,"output->vars." + p + " = " + "input->input.values."+ self.mappingSignal (pr, inputSignal) + ";\n") 
#                      print "input param", p;

                  # We generate the transition - output, switch to next state, etc.
                  self.generateTransition (srcFile, pr, inputSignal, pr.transitions[tidx])

                  self.write (srcFile,"break;\n") 
                  self.indent_decrease()
                  self.write (srcFile,"}\n");

          self.write (srcFile,"default:\n");
          self.write (srcFile,"{\n");

          self.indent_increase()
          if self.debug: self.write (srcFile,"OPENGEODEDEBUGMSG (\"["+pr.processName+"] did not receive any signal\\n\");\n") 
          self.write (srcFile,"break;\n");
          self.indent_decrease()

          self.write (srcFile,"}\n");
          self.indent_decrease()
          self.write (srcFile,"}\n");

   def generateSource (self, srcfile, pr):
       inputSignals = pr.inputSignals
       outputSignals = pr.outputSignals

       self.write (srcfile,"#include \""+pr.processName+"_process.h\"\n")

       #Function that initialize a structure
       self.write (srcfile,"void "+pr.processName+"process_init (" +pr.processName+ "_data_t* toinit)\n")
       self.write (srcfile,"{\n")
       self.indent_increase()


       if len (outputSignals) > 0:
           self.write (srcfile,"int t;\n")
           self.write (srcfile,"for (t = 0 ; t < "+self.mappingNbOutputsMacro (pr)+" ; t++)\n")
           self.write (srcfile,"{\n")
           self.indent_increase()
           self.write (srcfile,"toinit->outputs.output_mgmt[t]       = OUTPUT_MGMT_NORMAL;\n")
           self.write (srcfile,"toinit->outputs.output_callbacks[t]  = OPENGEODE_NULL;\n")
           self.indent_decrease()
           self.write (srcfile,"}\n")

       self.write (srcfile,"toinit->initialized = OPENGEODE_TRUE;\n")

       self.indent_decrease()
       self.write (srcfile,"}\n")
       #end of initialiation structure

       self.write (srcfile,"\n")
       self.write (srcfile,"\n")

       #Function that enable the reaction of the system
       self.write (srcfile,"void "+ self.mappingReactionFunction (pr) + " (" +pr.processName+ "_data_t* input, " +pr.processName+ "_data_t*output)\n")
       self.write (srcfile,"{\n")
       self.indent_increase()

       self.write (srcfile,"output->state = input->state;\n")
       self.write (srcfile,"output->input.value = input->input.value;\n")
       if len (pr.variables) > 0:
           for varname in pr.variables.keys():
               self.write (srcfile,"output->vars." + varname+ " = input->vars."+ varname + ";\n")


       if len (outputSignals) > 0:
           self.write (srcfile,"output->outputs.outputs_amount = 0;\n")

       for pr_output in outputSignals:
           signame = pr_output.keys()[0]
           self.write (srcfile,"output->outputs."+ self.mappingSignal (pr, signame)+" = input->outputs."+ self.mappingSignal(pr, signame)+";\n")

       self.write (srcfile,"\n")
       self.write (srcfile,"switch (input->state)\n")
       self.write (srcfile,"{\n")
       self.indent_increase()
       for pr_state in pr.mapping.keys():
           self.write (srcfile,"case ")
           self.write (srcfile,self.mappingState (pr, pr_state) + ":\n",indent=False)
           self.write (srcfile,"{\n")
           self.indent_increase()
           self.generateStateCase (srcfile, pr, pr_state)
           self.write (srcfile,"break;\n")
           self.indent_decrease()
           self.write (srcfile,"}\n")
       self.indent_decrease()
       self.write (srcfile,"}\n")
       self.indent_decrease()
       self.write (srcfile,"}\n")


   def generateHeader (self, hdrfile, pr):
       inputSignals = pr.inputSignals
       outputSignals = pr.outputSignals
       nbOutputSignals = 0

       declared_inputs = {}

       self.write (hdrfile, "#ifndef __OPENGEODE_"+pr.processName.upper() + "_H__\n")
       self.write (hdrfile, "#define __OPENGEODE_"+pr.processName.upper() + "_H__\n")
       self.write (hdrfile, "#include \"asn1crt.h\"\n")

       if self.forTaste:
           self.write (hdrfile, "#include \"C_ASN1_Types.h\"\n")
       else:
           self.write (hdrfile, "#include \"DataView.h\"\n")

       self.generateHeaderRuntime (hdrfile)

       if len (pr.states) > 0:
           stateid = 1
           states = {}

           for st in pr.states:
               s = st.inputString
               if s.find (",") != -1:
                  tmps = s.rsplit(",")
                  for v in tmps:
                      v = v.replace (" ", "")
                      v = v.replace ("\n", "")
                      states[v] = 1
               else:
                  states[s] = 1

           self.write (hdrfile,"typedef enum\n")
           self.write (hdrfile,"{\n")
           self.indent_increase()
           self.write (hdrfile,pr.processName.upper() + "_START = 0")
           for pr_state in states.keys():
               self.write (hdrfile,",\n",indent=False)
               self.write (hdrfile,self.mappingState (pr, pr_state) + " = ")
               self.write (hdrfile,str(stateid),indent=False)
               stateid = stateid + 1
           self.indent_decrease()
           self.write (hdrfile,"\n} ")
           self.write (hdrfile,pr.processName+"_state_t;\n")
           self.write (hdrfile,"\n\n")

       if len (pr.states) > 0:
           signalid = 0
           self.write (hdrfile,"typedef enum\n")
           self.write (hdrfile,"{\n")
           self.indent_increase()
           self.write (hdrfile,pr.processName.lower() + "_invalid_input = -1")
           for pr_input in pr.inputSignals:
               signame = pr_input.keys()[0]
               self.write (hdrfile,",\n",indent=False)
               self.write (hdrfile,self.mappingSignal (pr, signame) + " = ")
               self.write (hdrfile,str(signalid))
               signalid = signalid + 1
           self.indent_decrease()
           self.write (hdrfile,"\n} ")
           self.write (hdrfile,pr.processName.lower()+"_input_t;\n")
           self.write (hdrfile,"\n\n")

       if len (outputSignals) > 0:
           self.write (hdrfile,"#define " + self.mappingNbOutputsMacro (pr) + " "+ str (len (outputSignals)) + "\n")
           self.write (hdrfile,"\n\n")
           signalid = 0
           self.write (hdrfile,"typedef enum\n")
           self.write (hdrfile,"{\n")
           self.indent_increase()
           self.write (hdrfile,pr.processName.lower() + "_invalid_output = -1")
           for pr_output in outputSignals:
               signame = pr_output.keys()[0]
               self.write (hdrfile,",\n",indent=False)
               self.write (hdrfile,self.mappingSignal (pr, signame) + " = ")
               self.write (hdrfile,str(signalid))
               signalid = signalid + 1
               nbOutputSignals = nbOutputSignals + 1
           self.indent_decrease()
           self.write (hdrfile,"\n} ")
           self.write (hdrfile,pr.processName.lower()+"_output_t;\n")
           self.write (hdrfile,"\n\n")


       if len (outputSignals) > 0:

           self.write (hdrfile,"typedef struct\n")
           self.write (hdrfile,"{\n")
           self.indent_increase()
           for pr_output in outputSignals:
               signame = pr_output.keys()[0]
               self.write (hdrfile,"opengeode_boolean_t "+self.mappingSignal(pr, signame )+";\n")

           self.write (hdrfile,"struct\n")
           self.write (hdrfile,"{\n")
           self.indent_increase()
           self.write (hdrfile, "int "+pr.processName.lower() + "_output_invalid_signal_value;\n");
           for pr_output in outputSignals:
               signame = pr_output.keys()[0]
               if pr_output[signame].has_key ('in') :
                  for paramname in pr_output[signame]['in']:
#                     print "paramname=", paramname
                     sigtype = pr_output[signame]['in'][paramname]['type']
                     self.write (hdrfile, self.dataPrefix () + sigtype + " "+self.mappingSignal(pr, signame)+";\n")
           self.indent_decrease()
           self.write (hdrfile,"}values;\n")
           self.write (hdrfile, "opengeode_output_mgmt_kind_t output_mgmt["+self.mappingNbOutputsMacro (pr)+"];\n")
           self.write (hdrfile, "opengeode_output_callback_t  output_callbacks["+self.mappingNbOutputsMacro (pr)+"];\n")
           self.write (hdrfile, "int outputs_amount;\n")
           self.write (hdrfile, pr.processName.lower()+"_output_t outputs_order[OPENGEODE_MAX_OUTPUTS];\n")
           self.indent_decrease()
           self.write (hdrfile,"}"+pr.processName.lower()+"_outputs_t;\n\n")


       self.write (hdrfile,"typedef struct\n")
       self.write (hdrfile,"{\n")
       self.indent_increase()

       self.write (hdrfile,"opengeode_boolean_t initialized;\n")
       self.write (hdrfile,"" + pr.processName + "_state_t state;\n")

       if len (pr.variables) > 0:
           self.write (hdrfile,"struct\n")
           self.write (hdrfile,"{\n")
           self.indent_increase ()
           for varname in pr.variables.keys():
               self.write (hdrfile, self.dataPrefix() + pr.variables[varname] + " " + varname+";\n")
           self.indent_decrease ()
           self.write (hdrfile, "}vars;\n");


       if len (inputSignals) > 0:
           self.write (hdrfile,"struct\n")
           self.write (hdrfile,"{\n")
           self.indent_increase ()
           self.write (hdrfile,pr.processName.lower()+"_input_t value;\n")
           self.write (hdrfile, "union\n");
           self.write (hdrfile, "{\n");
           self.indent_increase ()
           self.write (hdrfile, "int "+ pr.processName.lower() +"_input_invalid_signal_value;\n");
           for m in pr.mapping.keys():
#               print "m=" , m , "\n"
               inputs = pr.mapping[m]
#               print "inputs=" , inputs , "\n"
#               if isinstance (inputs, int):
#                   print "i=" , inputs , "\n"
               if isinstance (inputs, list):
                   for input in inputs:
#                      print "input instance\n"
                      for p in input.parameters:
                          inputvalue = input.inputlist.keys()[0]

                          if not declared_inputs.has_key(inputvalue):
                              self.write (hdrfile, self.dataPrefix() + pr.variables[p] + " " + self.mappingSignal(pr, inputvalue) + ";\n");

                          declared_inputs[inputvalue] = 1

#                          print "param=" , p , "\n"
#                          print "trans=" , input.transition , "\n"

           self.indent_decrease ()
           self.write (hdrfile, "}values;\n");
           self.indent_decrease ()
           self.write (hdrfile,"}input;\n\n")

       if len (outputSignals) > 0:
           self.write (hdrfile,pr.processName.lower() + "_outputs_t outputs;\n")

       self.indent_decrease()
       self.write (hdrfile,"}")
       self.write (hdrfile,pr.processName)
       self.write (hdrfile,"_data_t;")
       self.write (hdrfile,"\n\n")


       self.write (hdrfile,"void "+pr.processName+"process (" +pr.processName+ "_data_t* input, " +pr.processName+ "_data_t*output);\n")
       self.write (hdrfile,"void "+pr.processName+"process_init (" +pr.processName+ "_data_t* toinit);\n")

       self.write (hdrfile,"#endif\n")
      

   def generate(self, process):
       ''' Generate C code '''
       print "filename" ,  self.fileName

       processName = process.processName

       if not isinstance (self.fileName, str):
          self.fileName = processName + "_process"

       sourceFileName = self.fileName + ".c"
       headerFileName = self.fileName + ".h"

       sourceFile = open (sourceFileName, "w")
       headerFile = open (headerFileName, "w")

       self.indent = 0
       self.generateHeader (headerFile, process)
       self.indent = 0
       self.generateSource (sourceFile, process)

       sourceFile.close()
       headerFile.close()

       if self.forTaste:
          sourceFileName = processName + "_taste.c"
          headerFileName = processName + "_taste.h"

          sourceFile = open (sourceFileName, "w")
          headerFile = open (headerFileName, "w")

          self.indent = 0
          self.generateTasteHeader (headerFile, process)
          self.indent = 0
          self.generateTasteSource (sourceFile, process)

          sourceFile.close()
          headerFile.close()

