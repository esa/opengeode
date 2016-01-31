#include <math.h>
#include <stdio.h>

/* Ada code external interface */
extern void challenge_run();
extern void challenge_any_one();
extern int challenge_startup();

//extern long long l_result;

/* Provide code called by the Ada state machine as external procedure */
void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    challenge_startup();
    challenge_run();
    challenge_run();
    //printf("Internal state: %lld\n", l_result);
    challenge_any_one();
    challenge_run();

    return 0;
}
