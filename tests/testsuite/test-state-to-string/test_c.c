#include <stdio.h>

#include "complexsdl.h"

int main(void)
{
    complexsdl_startup();
    printf("%s\n", complexsdl_state());
    complexsdl_PI_tick();
    printf("%s\n", complexsdl_state());
    complexsdl_PI_tick();
    printf("%s\n", complexsdl_state());
    complexsdl_PI_tick();
    printf("%s\n", complexsdl_state());

    return 0;
}
