#include <stdlib.h>
#include <stdbool.h>

extern void CInitfoo(void);

void foo_check_queue(bool* has_pending_msg)
{
    *has_pending_msg = false;
}

int main(void)
{
    CInitfoo();
    exit(0);
}
