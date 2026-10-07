#include <stdio.h>

#include "complexsdl.h"
#include "complexsdl_datamodel.h"

extern void complexsdl_startup(void);
extern void complexsdl_PI_impulse(asn1SccMyInteger *);

int main(void)
{
    asn1SccMyInteger x = 0;

    complexsdl_startup();

    /* In S1: state = S1 must be true, result 1, then go to S2 */
    complexsdl_PI_impulse(&x);
    /* In S2: state = S1 must be false, result 20, then go back to S1 */
    complexsdl_PI_impulse(&x);

    return 0;
}
