#include <stdio.h>
#include "dataview-uniq.h"

void myfunction_RI_result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}


int main()
{
    asn1SccT_Int32 test = 5;

    printf("[C Code] Running test\n");
    myfunction_initStates();
    myfunction_PI_start_something(&test);
    return 0;
}


