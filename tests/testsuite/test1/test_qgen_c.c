#include "dataview-uniq.h"
void og_RI_rezult (asn1SccMy_OctStr *val) 
{
    printf("[C] got something]\n");
}

int main() {
    asn1SccMy_OctStr toto;
    og_initStates();
    og_PI_go(&toto);
    return 0;
}


