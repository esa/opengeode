#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void adainit();
void orchestrator_RI_housekeeping(asn1SccMyInteger *toto)
{
    printf("%lld\n", *toto);
}

int main()
{
    printf("[C Code] Running test\n");
    adainit();
    
    return 0;
}

