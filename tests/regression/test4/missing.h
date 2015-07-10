#include "dataview-uniq.h"

asn1SccMyChoice asn1SccMyChoice_b_set(asn1SccMySeq itm)
{
   asn1SccMyChoice temp;
   temp.kind = b_PRESENT;
   temp.u.b = itm;
   return temp;
}

asn1SccMyChoice asn1SccMyChoice_a_set(flag itm)
{
   asn1SccMyChoice temp;
   temp.kind = MyChoice_a_PRESENT;
   temp.u.a = itm;
   return temp;
}

asn1SccMyPossiblyEmptySeqOf asn1SccMyPossiblyEmptySeqOf_Init()
{
   asn1SccMyPossiblyEmptySeqOf temp;
   asn1SccMyPossiblyEmptySeqOf_Initialize(&temp);
   return temp;
}

asn1SccMyComplexChoice asn1SccMyComplexChoice_a_set(asn1SccMyComplexChoice_a itm)
{
   asn1SccMyComplexChoice temp;
   temp.kind = MyComplexChoice_a_PRESENT;
   temp.u.a = itm;
   return temp;
}


asn1SccDeepSeq_a_b_d asn1SccDeepSeq_a_b_d_e_set(flag itm)
{
   asn1SccDeepSeq_a_b_d temp;
   temp.kind = e_PRESENT;
   temp.u.e = itm;
   return temp;
}
