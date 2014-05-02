#include <math.h>
#include <stdio.h>

/* Ada code external interface */
extern void challenge_run();
extern void challenge_any_one();
extern int adainit();

//extern long long l_result;

/* Provide code called by the Ada state machine as external procedure */
void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    adainit();
    printf("[C Code] Calling RUN\n");
    challenge_run();
    printf("[C Code] Calling RUN AGAIN....\n");
    challenge_run();
    //printf("Internal state: %lld\n", l_result);
    printf("[C Code] Calling any_one....\n");
    challenge_any_one();
    printf("[C Code] And finally calling RUN AGAIN....\n");
    challenge_run();
    
    return 0;
}

