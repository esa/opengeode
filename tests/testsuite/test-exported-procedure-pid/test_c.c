/*
 * Driver for the "exported procedure + PID type" regression test.
 *
 * Calling the PI of the exported procedure DoIt must run the procedure and
 * then its automatic transition, and the generated code must compile. This
 * used to fail because the transition call passed a destination PID to a
 * function that takes none.
 */
#include <stdio.h>
#include "child.h"

extern void CInitchild(void);
extern void child_PI_DoIt(void);

int main(void)
{
    CInitchild();

    /* Exported procedure DoIt, then its automatic transition */
    child_PI_DoIt();

    return 0;
}
