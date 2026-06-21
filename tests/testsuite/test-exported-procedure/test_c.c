#include <stdio.h>
#include "dataview-uniq.h"
extern void CInitog();

extern void og_PI_hehe(asn1SccType2 *p);
int main()
{
   asn1SccType2 p = false;
   printf("%s\n", !p?"OK":"ERROR");
   CInitog();
   og_PI_hehe(&p);
   printf("%s\n", p?"OK":"ERROR");
   return 0;
}
