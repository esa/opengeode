#include "dataview-uniq.h"
#include <stdio.h>

extern void CInitog();

extern void og_PI_go(asn1SccMy_OctStr * ze_param);

void og_RI_rezult(asn1SccMy_OctStr * ze_rezult) 
{
    printf("[C] got something]\n");
}

int main()
{
    CInitog();

    asn1SccMy_OctStr toto = test_string;  // send "hello"
    og_PI_go(&toto); // will move state to Running
    og_PI_go(&toto); // will display ay
    og_PI_go(&toto); // will display ay
    
    return 0;
}
