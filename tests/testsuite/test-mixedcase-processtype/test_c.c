/*
 * Driver for the mixed-case process-type regression test.
 *
 * Before the fix, the instance wrapper (child.c) called type-module symbols
 * with the wrong casing (CInitMixedType vs CInitmixedtype, MixedType_PI_go
 * vs mixedtype_PI_go, ...), so this file did not compile. It now does, and
 * the instance's PI runs the type's state machine.
 */
#include <stdio.h>
#include "child.h"

extern void CInitchild(void);
extern void child_PI_go(void);

int main(void)
{
    CInitchild();

    /* Runs the process type's transition: outputs "rezult", then stops. */
    child_PI_go();

    printf("done\n");
    return 0;
}
