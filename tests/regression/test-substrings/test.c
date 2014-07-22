#include <math.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

#include "dataview-uniq.h"

extern void adainit();
extern void myfunction_start_something(asn1SccT_Int32 *);
extern void myfunction_mytimer();


void myfunction_RI_result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}


int main()
{
    asn1SccT_Int32 test = 5;

    printf("[C Code] Running test\n");
    adainit();
    myfunction_start_something(&test);
    return 0;
}

