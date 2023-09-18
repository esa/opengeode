#include <stdio.h>
#include <stdbool.h>
#include "dataview-uniq.h"
#include "challenge.h"
#undef pow
#include <math.h>

void challenge_RI_pow(asn1SccT_UInt32 * a,asn1SccT_UInt32 * b,asn1SccT_UInt32 * res)
{
    double da, db;
    da = (double) *a;
    db = (double) *b;
    *res = (long long)pow(da, db);
}

void challenge_check_queue(bool *res)
{
    *res = false;
}

int main()
{
    printf("Testing parallel states...\n");

    challenge_startup();

    challenge_PI_run();
    challenge_PI_run(); // should have no effect

    challenge_PI_any_one();
    challenge_PI_any_one(); // Complete action
    challenge_PI_any_two();
    challenge_PI_any_two(); // Complete action
    
    return 0;
}

