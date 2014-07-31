#include <stdio.h>
#include <stdlib.h>
#include "dataview-uniq.h"

extern void expressions_startup();
extern void expressions_run();

void expressions_RI_assert(Boolean *res, CharString *msg) {
    if (!*res) {
        fprintf(stderr, "%.*s\n", (int)msg->nCount, msg->arr);
        exit(1);
    }
}

int main() {
    expressions_startup();
    expressions_run();
    return 0;
}
