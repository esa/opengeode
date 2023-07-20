#include <stdio.h>
#include "dataview-uniq.h"

extern void CInitog();

extern void og_PI_go(asn1SccMy_OctStr *);

void og_RI_rezult(asn1SccMy_OctStr *val) 
{
    printf("[C] got something]\n");
}

int main()
{
    asn1SccMy_OctStr toto;

    CInitog();
    og_PI_go(&toto);

    return 0;
}
