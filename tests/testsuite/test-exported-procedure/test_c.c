#include <stdio.h>
#include "dataview-uniq.h"
extern void CInitog();

extern void og_PI_hehe(asn1SccToto *t, asn1SccType2 *p);
int main()
{
   asn1SccType2 p = false;
   asn1SccToto t = { 42, true };
   printf("%s\n", !p?"OK":"ERROR");
   CInitog();
   og_PI_hehe(&t, &p);
   printf("%s\n", p?"OK":"ERROR");
   return 0;
}
