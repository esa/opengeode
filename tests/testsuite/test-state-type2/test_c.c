#include <stdlib.h>
#include <stdbool.h>
#include "foo.h"

extern void CInitfoo(void);

void foo_check_queue(bool* has_pending_msg)
{
    *has_pending_msg = false;
}

int main(void)
{
    CInitfoo();
    foo_PI_pulse();
    foo_PI_pulse();
    foo_PI_pulse();
    exit(0);
}
