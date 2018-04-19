#include <math.h>
#include <stdio.h>

extern void challenge_run();
extern void challenge_any_one();
extern void challenge_initStates();

/* Provide code called by the Ada state machine as external procedure */
void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    challenge_initStates();
    challenge_run();
    challenge_run();
    //printf("Internal state: %lld\n", l_result);
    challenge_any_one();
    challenge_run();
    return 0;
}


