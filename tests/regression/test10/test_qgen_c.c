#include <math.h>
#include <stdio.h>

/* Provide code called by the Ada state machine as external procedure */
void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    challenge_initStates();
    challenge_PI_run();
    challenge_PI_run();
    //printf("Internal state: %lld\n", l_result);
    challenge_PI_any_one();
    challenge_PI_run();
    return 0;
}


