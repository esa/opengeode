#include <math.h>
#include <stdio.h>

extern void challenge_PI_run();
extern void challenge_PI_any_one();
extern int CInitchallenge();

void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

int main()
{
    CInitchallenge();

    challenge_PI_any_one();
    challenge_PI_run();
    challenge_PI_run();
    challenge_PI_any_one();
    
    return 0;
}
