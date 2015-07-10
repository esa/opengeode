#include <stdio.h>
#include "dataview-uniq.h"

int main() {
    asn1SccMy_OctStr toto;
    CInit();
    runTransition(0);
    go(&toto);
    return 0;
}
