#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void runTransition(int Id);
void telemetry(asn1SccMyEnum * param){}

int main()
{
    printf("[C Code] Running test\n");
    CInit();
    runTransition(0);
    return 0;
}

