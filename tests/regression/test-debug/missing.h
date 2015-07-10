#include "dataview-uniq.h"

asn1SccMyChoice asn1SccMyChoice_c1_set(asn1SccBoolean itm)
{
   asn1SccMyChoice temp;
   temp.kind = c1_PRESENT;
   temp.u.c1 = itm; 
   return temp;
}

asn1SccSeqOpt_c asn1SccSeqOpt_c_Init()
{
   asn1SccSeqOpt_c temp;
   asn1SccSeqOpt_c_Initialize(&temp);
   return temp;
}

asn1SccSeqOpt_d asn1SccSeqOpt_d_Init()
{
   asn1SccSeqOpt_d temp;
   asn1SccSeqOpt_d_Initialize(&temp);
   return temp;
}

int asn1SccMyChoice_Kind(asn1SccMyChoice val)
{
   return val.kind;
}
