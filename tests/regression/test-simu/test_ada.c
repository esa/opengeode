#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void adainit();
void orchestrator_RI_peek_list(void *_) {}
void orchestrator_RI_peek_fixed(void *_) {}
void orchestrator_RI_telemetry(void *_){}
extern char *fixed_value();
//extern int fixed_size();
int main()
{
    char * toto;
    int size;
    int i;
    printf("[C Code] Running test\n");
    adainit();
    toto = fixed_value(); 
//    size = fixed_size();
//    printf("Size=%d\n", size);
//    for (i = 0; i<size; i++) printf("%d", toto[i]);
    printf("\n");

    
    return 0;
}

