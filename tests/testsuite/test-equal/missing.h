#include "dataview-uniq.h"

asn1SccSeqOf asn1SccSeqOf_Init()
{
   asn1SccSeqOf temp;
   asn1SccSeqOf_Initialize(&temp);
   return temp;
}

asn1SccAChoice asn1SccAChoice_b_set(asn1SccSeqOf itm)
{
   asn1SccAChoice temp;

   temp.kind = b_PRESENT;
   temp.u.b = itm;
   return temp;
}

asn1SccAChoice asn1SccAChoice_a_set(asn1SccT_Bool itm)
{
   asn1SccAChoice temp;

   temp.kind = a_PRESENT;
   temp.u.a = itm;
   return temp;
}
