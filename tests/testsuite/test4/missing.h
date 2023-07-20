#include "dataview-uniq.h"

asn1SccMyChoice asn1SccMyChoice_b_set(asn1SccMySeq itm)
{
   asn1SccMyChoice temp;
   temp.kind = MyChoice_b_PRESENT;
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
   temp.kind = DeepSeq_a_b_d_e_PRESENT;
   temp.u.e = itm;
   return temp;
}
