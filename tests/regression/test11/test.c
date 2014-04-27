#include <math.h>
#include <stdio.h>

/* Ada code external interface */
extern void og_start();

int main()
{
    printf("[C Code] Running test\n");
    og_start();
    
    return 0;
}

