#include <stdio.h>
#include "dataview-uniq.h"

extern void og_startup();
extern void og_go(asn1SccMy_OctStr *);
void og_RI_rezult (asn1SccMy_OctStr *val) 
{
    printf("[C] got something]\n");
}
int main() {
    asn1SccMy_OctStr toto;
    og_startup();
    og_go(&toto);
    return 0;
}
