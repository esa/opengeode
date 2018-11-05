#include "dataview-uniq.h"

void operators_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        printf("%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}

int main() {
    operators_initStates();
    operators_PI_run();
    return 0;
}

