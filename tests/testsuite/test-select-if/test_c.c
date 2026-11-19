#include <stdlib.h>
#include "foo.h"

void foo_RI_SET_timer_enabled(const asn1SccT_UInt32 *val) { (void)val; }
void foo_RI_RESET_timer_enabled(void) {}

int main(void)
{
    asn1SccMyInteger val = 42;
    foo_startup();
    foo_PI_keep_sig();
    foo_PI_sig_enabled(&val);
    foo_PI_exp_enabled(&val);
    foo_PI_timer_enabled();
    return 0;
}
