#include <stdio.h>
#include <stdlib.h>
#include "dataview_uniq.h"

extern void expressions_initStates (void);
extern void expressions_run (void);

void expressions_RI_assert(asn1QGenBoolean *res, asn1QGenCharString *msg) {
    if (!*res) {
        printf("%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}


int main() {
    expressions_initStates();
    expressions_run();
    return 0;
}

