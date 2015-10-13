#include <stdio.h>
#include "dataview-uniq.h"
#include "challenge.h"
typedef enum {off, safe, on___hello___wait_in_sub_hello} states_t;
typedef struct
{
   states_t state;
   asn1SccT_UInt32 on___result;
   asn1SccT_UInt8 on___myresult;
   asn1SccT_UInt32 result;
} context_t;
context_t context;
void CInit()
{
   context.on___result = 9;
   context.on___myresult = 4;
   context.result = 0;
}
#define on___via_toto_START 4
#define on___hello___START 7
#define on___START 5
void runTransition(int Id);
void ___on___hello___entry();
void ___on___entry();
void ___on___inner_proc(asn1SccT_UInt8  toto);
void ___on___exit();
void run()
{
   switch(context.state)
   {
      case off:
      {
         runTransition(3);
         break;
      }
      case safe:
      {
         break;
      }
      case on___hello___wait_in_sub_hello:
      {
         runTransition(6);
         break;
      }
      default:
      {
         break;
      }
   }
}

void go_off()
{
   switch(context.state)
   {
      case off:
      {
         break;
      }
      case safe:
      {
         break;
      }
      case on___hello___wait_in_sub_hello:
      {
         break;
      }
      default:
      {
         break;
      }
   }
}

void any_one()
{
   switch(context.state)
   {
      case off:
      {
         break;
      }
      case safe:
      {
         break;
      }
      case on___hello___wait_in_sub_hello:
      {
         break;
      }
      default:
      {
         break;
      }
   }
}

void any_two()
{
   switch(context.state)
   {
      case off:
      {
         break;
      }
      case safe:
      {
         break;
      }
      case on___hello___wait_in_sub_hello:
      {
         break;
      }
      default:
      {
         break;
      }
   }
}

void ___on___hello___entry()
{
   // writeln('8') (14,33)
   printf("8");
   printf("\n");
   // writeln('Hello!') (16,33)
   printf("Hello!");
   printf("\n");
   // RETURN  (None,None) at 195, 286
   return;
}


void ___on___entry()
{
   // writeln('ENTERING NESTED STATE') (46,25)
   printf("ENTERING NESTED STATE");
   printf("\n");
   // RETURN  (None,None) at 208, 178
   return;
}


void ___on___inner_proc(asn1SccT_UInt8  toto)
{
   asn1SccT_Boolean result  = true;
   // JOIN hey_joe (None,None) at None, None
   goto hey_joe;
   // CONNECTION leaving (67,20)
   leaving:
   // RETURN  (None,None) at 496, 347
   return;
   // CONNECTION hey_joe (61,20)
   hey_joe:
   // writeln('10') (63,25)
   printf("10");
   printf("\n");
   // result := false (65,25)
   result = false;
   // JOIN leaving (None,None) at None, None
   goto leaving;
}


void ___on___exit()
{
   // writeln('LEAVING the nested state') (82,25)
   printf("LEAVING the nested state");
   printf("\n");
   // RETURN  (None,None) at 180, 219
   return;
}


void runTransition(int Id)
{
   int trId = Id;
   asn1SccT_UInt32 tmp16;
   asn1SccT_UInt32 tmp17;
   while (trId != -1)
   {
      switch(trId)
      {
         case 0:
         {
            // writeln('1') (152,13)
            printf("1");
            printf("\n");
            // NEXT_STATE OFF (154,18) at -1, 215
            trId = -1;
            context.state = off;
            goto next_transition;
            break;
         }
         case 1:
         {
            // NEXT_STATE Safe (160,22) at 234, 245
            trId = -1;
            context.state = safe;
            goto next_transition;
            break;
         }
         case 2:
         {
            // NEXT_STATE off (164,22) at 144, 245
            trId = -1;
            context.state = off;
            goto next_transition;
            break;
         }
         case 3:
         {
            // writeln('2') (171,17)
            printf("2");
            printf("\n");
            // NEXT_STATE on (173,22) at -32, 371
            // COMMENT Enter substate via entry point (175,12)
            trId = on___START;
            goto next_transition;
            break;
         }
         case 4:
         {
            // entry (None,None)
            ___on___entry();
            // writeln('3') (89,21)
            printf("3");
            printf("\n");
            // exit (None,None)
            ___on___exit();
            // RETURN ret0 (None,None) at 1215, 107
            trId = 1;
            goto next_transition;
            break;
         }
         case 5:
         {
            // entry (None,None)
            ___on___entry();
            // writeln('7') (95,21)
            printf("7");
            printf("\n");
            // JOIN on___inside_label (None,None) at None, None
            goto on___inside_label;
            break;
         }
         case 6:
         {
            // writeln('27 == ', result) (136,25)
            printf("27 == ");
            if((int)(context.on___result) >= 0) printf(" ");
            printf("%d", context.on___result);
            printf("\n");
            // myresult := 88 (138,25)
            context.on___myresult = 88;
            // result := 33 (139,0)
            context.on___result = 33;
            // JOIN on___to_label (141,25) at 24, 229
            goto on___to_label;
            break;
         }
         case 7:
         {
            // entry (None,None)
            ___on___hello___entry();
            // NEXT_STATE on___hello___wait_in_sub_hello (23,34) at 312, 183
            trId = -1;
            context.state = on___hello___wait_in_sub_hello;
            goto next_transition;
            break;
         }
         default:
         {
            break;
         }
      }
      goto next_transition;
      // CONNECTION on___another_floating (114,23)
      on___another_floating:
      // writeln('9') (116,21)
      printf("9");
      printf("\n");
      // myresult := 1 (118,21)
      context.on___myresult = 1;
      // inner_proc(myresult) (120,21)
      ___on___inner_proc(context.on___myresult);
      // exit (None,None)
      ___on___exit();
      // RETURN  (None,None) at 565, 672
      trId = 2;
      goto next_transition;
      // CONNECTION on___to_label (126,23)
      on___to_label:
      // JOIN on___another_floating (128,21) at 159, 374
      goto on___another_floating;
      // CONNECTION on___nslabel (110,16)
      on___nslabel:
      // NEXT_STATE on___hello (112,26) at 938, 416
      trId = on___hello___START;
      goto next_transition;
      // CONNECTION on___inside_label (97,16)
      on___inside_label:
      // pow(3,3, result) (99,21)
      tmp16 = 3;
      tmp17 = 3;
      pow(&tmp16, &tmp17, &context.on___result);
      // DECISION result (-1,-1)
      // ANSWER myresult (103,25)
      if((context.on___result) == context.on___myresult)
      {
         ;
      }
      // ANSWER ELSE (None,None)
      else
      {
         // myresult := 5 (107,33)
         context.on___myresult = 5;
      }
      // JOIN on___nslabel (None,None) at None, None
      goto on___nslabel;
      next_transition:
      ;
   }
}

