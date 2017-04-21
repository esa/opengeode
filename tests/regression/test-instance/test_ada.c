#include <stdio.h>
#include "dataview-uniq.h"

extern void adainit();

extern void og_go(asn1SccMy_OctStr *);

void og_RI_rezult (asn1SccMy_OctStr *val) 
{
    printf("[C] got something]\n");
}

int main() {
    asn1SccMy_OctStr toto = test_string;  // send "hello"
    adainit();
    og_go(&toto); // will move state to Running
    og_go(&toto); // will display ay
    og_go(&toto); // will display ay
    return 0;
}

