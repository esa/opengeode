/*
 * Environment glue for the mixed-case process-type regression test.
 *
 * A process TYPE's instance wrapper forwards its required interfaces to
 * <instance>_RI_* functions that TASTE's middleware provides at link time.
 * Here they are stubbed so the generated code can be linked; the point of
 * this test is that the generated C compiles at all (before the fix the
 * instance wrapper called type symbols with the wrong casing).
 */
#include <stdio.h>
#include "dataview-uniq.h"

void child_RI_rezult(const asn1SccPID dest_pid)
{
    (void)dest_pid;
    printf("rezult\n");
}

void child_delete_instance(asn1SccPID id)
{
    (void)id;
}
