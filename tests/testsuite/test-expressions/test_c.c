#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"
extern void run();
extern void runTransition(int);

void expressions_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        printf("%s\n", msg);
        exit(1);
    }
}


int main() {
    runTransition(0);
    run();
    return 0;
}

