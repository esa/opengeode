#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"

extern void adainit();
extern void controlflow_run();

void controlflow_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        fprintf(stderr, "%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}

void controlflow_RI_fail(asn1SccCharString *msg) {
    fprintf(stderr, "%.*s\n", (int)msg->nCount, msg->arr);
    exit(1);
}

int main() {
    adainit();
    controlflow_run();
    return 0;
}
