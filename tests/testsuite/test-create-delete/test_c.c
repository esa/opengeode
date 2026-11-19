/*
 * Driver for the CREATE / STOP regression test.
 *
 * It also provides the environment glue that TASTE's kazoo templates
 * generate for an instantiable process type:
 *     asn1SccPID <instance>_create_instance(asn1SccPID from);
 *     void       <instance>_delete_instance(asn1SccPID id);
 * Here the glue records the calls so the test can check that CREATE asked
 * the environment to create the instance and that STOP asked it to delete
 * the instance (with the PID stored in "offspring").
 */
#include <stdio.h>
#include "parent.h"

static int create_calls = 0;
static int delete_calls = 0;
static asn1SccPID deleted_pid;

asn1SccPID child_create_instance(asn1SccPID from)
{
    /* The runtime returns the PID of the freshly created instance. */
    create_calls++;
    (void)from;
    return PID_child_1;
}

void parent_delete_instance(asn1SccPID id)
{
    delete_calls++;
    deleted_pid = id;
}

int main(void)
{
    parent_startup();

    /* CREATE Child, then STOP (deletes the instance and clears init_done) */
    parent_PI_go();
    /* The process has stopped: this message must be ignored */
    parent_PI_ping();

    printf("create calls=%d\n", create_calls);
    printf("delete calls=%d\n", delete_calls);
    printf("deleted pid=%d\n", (int)deleted_pid);
    return 0;
}
