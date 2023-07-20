#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void CInitorchestrator();

void orchestrator_RI_plot(asn1SccT_Plot * gnc_data) {}
void orchestrator_RI_telemetry() {}
void orchestrator_RI_Get_telemetry() {}
void orchestrator_RI_S_SET_GNC_LV_SIM_CONTEXT_FOR_NEXT_MAJOR_CYCLE(asn1SccT_GNC_LV_SIM_CONTEXT * gnc_lv_sim_context){}
void orchestrator_RI_Scheduler(asn1SccT_INTR * intr) {}
void orchestrator_RI_VESAT_Simulation_Step(asn1SccT_GNC_LV_SIM_INPUTS * gnc_output,asn1SccT_GNC_LV_SIM_CONTEXT * gnc_input){}
void orchestrator_RI_S_JUMP_TO_NEXT_MAJOR_CYCLE() {}
void orchestrator_RI_S_GET_GNC_LV_SIM_INPUTS_FOR_NEXT_MAJOR_CYCLE(asn1SccT_GNC_LV_SIM_INPUTS * gnc_lv_sim_inputs){}

int main()
{
    printf("[C Code] Running test\n");
    CInitorchestrator();
    
    return 0;
}
