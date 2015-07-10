#include "dataview-uniq.h"
#include <math.h>
asn1SccReal pi = M_PI;
asn1SccChoice asn1SccChoice_i_set(asn1SccInteger itm)
{
   asn1SccChoice temp;
   temp.kind = i_PRESENT;
   temp.u.i = itm;
   return temp;
}
