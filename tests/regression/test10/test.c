#include <math.h>
#include <stdio.h>

/* Ada code external interface */
extern void challenge_start();
extern void challenge_run();

/* Provide code called by the Ada state machine as external procedure */
void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    printf("[C Code] Calling START\n");
    challenge_start();
    printf("[C Code] Calling RUN\n");
    challenge_run();
    printf("[C Code] Calling RUN AGAIN....\n");
    challenge_run();
    
    return 0;
}

