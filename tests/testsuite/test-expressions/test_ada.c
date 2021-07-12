#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"

extern void adainit();
extern void expressions_PI_run();

void expressions_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        fprintf(stderr, "%s\n", msg);
        exit(1);
    }
}

int main() {
    adainit();
    expressions_PI_run();
    return 0;
}
