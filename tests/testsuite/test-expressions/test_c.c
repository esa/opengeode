#include <stdio.h>
#include "dataview-uniq.h"

extern void CInitexpressions();
extern void expressions_PI_run();

void expressions_RI_assert(asn1SccBoolean * res, asn1SccCharString * msg)
{
    if (*res)
    {
        printf("PASS: %s\n", msg);
    }
    else
    {
        printf("FAIL: %s\n", msg);
    }
}

int main()
{
    CInitexpressions();

    expressions_PI_run();
    
    return 0;
}
