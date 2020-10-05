#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void adainit();
extern void orchestrator_startup();
extern void orchestrator_PI_other();
extern void orchestrator_PI_Paramless_TC();
extern char *orchestrator_state();
void orchestrator_RI_peek_list(void *_) {}
void orchestrator_RI_peek_fixed(void *_) {}
void orchestrator_RI_telemetry(void *_){}
//extern char *fixed_value();
//extern int fixed_size();
int main()
{
    char * toto;
    int size;
    int i;
    printf("[C Code] Running test\n");
    adainit();
    orchestrator_startup();
//    toto = fixed_value(); 
    printf("%s\n", orchestrator_state());
    orchestrator_PI_other();
    printf("%s\n", orchestrator_state());
    orchestrator_PI_other();
    printf("%s\n", orchestrator_state());
//    size = fixed_size();
//    printf("Size=%d\n", size);
//    for (i = 0; i<size; i++) printf("%d", toto[i]);
    printf("\n");

    
    return 0;
}

