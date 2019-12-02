#include "dataview-uniq.h"

void operators_RI_assert(asn1SccBoolean *res, asn1SccCharString *msg) {
    if (!*res) {
        printf("%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}

int main() {
    CInit();
    runTransition(0);
    run();
    return 0;
}

