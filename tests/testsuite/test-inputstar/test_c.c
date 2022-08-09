#include <math.h>
#include <stdio.h>

void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    runTransitionchallenge(0);
    challenge_PI_any_one();
    challenge_PI_run();
    challenge_PI_run();
    challenge_PI_any_one();
    return 0;
}


