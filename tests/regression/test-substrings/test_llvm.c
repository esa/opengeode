#include <stdio.h>
#include "dataview-uniq.h"

extern void basic_startup();
extern void myfunction_start_something(asn1SccT_Int32 *);

void myfunction_RI_result_data(long long *val)
{
    printf("[C] result_data: %lld\n", *val);
}

int main()
{

    asn1SccT_Int32 test = 5;

    printf("[C Code] Running test\n");
    basic_startup();
    myfunction_start_something(&test);
    return 0;
}
