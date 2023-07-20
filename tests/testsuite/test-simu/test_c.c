#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void CInitorchestrator();

extern void orchestrator_startup();
extern void orchestrator_PI_other();
extern void orchestrator_PI_Paramless_TC();
extern char *orchestrator_state();

void orchestrator_RI_peek_list(void *_) {}
void orchestrator_RI_peek_fixed(void *_) {}
void orchestrator_RI_telemetry(void *_){}

int main()
{
    char * toto;
    int size;
    int i;

    printf("[C Code] Running test\n");

    CInitorchestrator();

    orchestrator_startup();
    printf("%s\n", orchestrator_state());
    orchestrator_PI_other();
    printf("%s\n", orchestrator_state());
    orchestrator_PI_other();
    printf("%s\n", orchestrator_state());
    printf("\n");

    return 0;
}
