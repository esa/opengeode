#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"
#include "controlflow.h"

extern void controlflow_startup();
extern void controlflow_PI_run();

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
    controlflow_startup();
    controlflow_PI_run();
    return 0;
}

