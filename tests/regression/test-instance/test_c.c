#include "dataview-uniq.h"
void rezult (asn1SccMy_OctStr *val) 
{
    printf("[C] got something]\n");
}

int main() {
    asn1SccMy_OctStr toto;
    CInit();
    runTransition(0);
    go(&toto);
    return 0;
}


