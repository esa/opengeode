#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void CInitorchestrator();

void orchestrator_RI_telemetry(void *_){}
void orchestrator_RI_S_SET_GNC_LV_SIM_CONTEXT_FOR_NEXT_MAJOR_CYCLE(void *_){}
void orchestrator_RI_Scheduler(void *_){}
void orchestrator_RI_VESAT_Simulation_Step(void *_){}
void orchestrator_RI_plot(void *_) {}
void orchestrator_RI_S_JUMP_TO_NEXT_MAJOR_CYCLE() {}
void orchestrator_RI_S_GET_GNC_LV_SIM_INPUTS_FOR_NEXT_MAJOR_CYCLE(void *_){}

int main()
{
    printf("[C Code] Running test\n");

    CInitorchestrator();
    
    return 0;
}

