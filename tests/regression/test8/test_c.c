#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"
void vesat_one_step(asn1SccT_GNC_LV_SIM_INPUTS *inp)
{
    printf("[C Code] Received T_GNC_LV_SIM_INPUTS\n");
}

int main()
{
    printf("[C Code] Running test\n");
    CInit();
    runTransition(0);

    return 0;
}


