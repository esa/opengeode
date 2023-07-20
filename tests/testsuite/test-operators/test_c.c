#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"

extern void CInitoperators();
extern void operators_PI_run();

void operators_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        fprintf(stderr, "%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}

int main()
{
    CInitoperators();

    operators_PI_run();

    return 0;
}
