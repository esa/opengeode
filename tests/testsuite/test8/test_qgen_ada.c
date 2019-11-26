#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void adainit();

void orchestrator_RI_VESAT_one_step(asn1SccT_GNC_LV_SIM_INPUTS *inp)
{
    printf("[C Code] Received T_GNC_LV_SIM_INPUTS\n");
}

int main()
{
    printf("[C Code] Running test\n");
    adainit();
    orchestrator_initStates();
    
    return 0;
}

