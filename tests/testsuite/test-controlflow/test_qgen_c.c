#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"

extern void run();

void controlflow_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        printf("%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}

void controlflow_RI_fail(asn1SccCharString *msg) {
    printf("%.*s\n", (int)msg->nCount, msg->arr);
    exit(1);
}

int main() {
    controlflow_initStates();
    controlflow_PI_run();
    return 0;
}

