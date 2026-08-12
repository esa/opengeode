#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"

extern void CInitog();
extern void og_PI_reset_all(asn1SccMyInteger * reset_all_param);
extern void og_PI_for_a();
extern void og_PI_for_b();
extern void og_PI_exit_aggreg();

int main()
{
    asn1SccMyInteger param = 1;
    CInitog();
    og_PI_for_a();
    og_PI_for_a();
    og_PI_for_a();
    og_PI_for_b();
    og_PI_for_b();
    og_PI_reset_all(&param);
    og_PI_reset_all(&param);
    og_PI_exit_aggreg();

    return 0;
}


