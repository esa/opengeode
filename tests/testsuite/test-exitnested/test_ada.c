#include <math.h>
#include <stdio.h>

/* Ada code external interface */
extern void challenge_PI_run();
extern void challenge_PI_go_off();
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
    challenge_PI_run();
    challenge_PI_go_off();
    
    return 0;
}

