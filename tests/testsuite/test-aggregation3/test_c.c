#include <math.h>
#include <stdio.h>

/* Provide code called by the Ada state machine as external procedure */
void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    CInit();
    runTransition(0);
    run();
    run();
    //printf("Internal state: %lld\n", l_result);
    any_one();
    run();
    return 0;
}


