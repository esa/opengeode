#include <math.h>
#include <stdio.h>
#include <stdbool.h>

extern void CInitchallenge();

extern void challenge_PI_run();
extern void challenge_PI_any_one();
extern void challenge_PI_any_two();

void challenge_RI_pow(long long *a, long long *b, long long *res)
{
    *res = (long long)pow((double)*a, (double)*b);
}

void challenge_check_queue(bool *res)
{
    *res = false;
}

int main()
{
    printf("Testing parallel states...\n");

    CInitchallenge();

    challenge_PI_run();
    challenge_PI_run(); // should have no effect

    challenge_PI_any_one();
    challenge_PI_any_one(); // Complete action
    challenge_PI_any_two();
    challenge_PI_any_two(); // Complete action
    
    return 0;
}

