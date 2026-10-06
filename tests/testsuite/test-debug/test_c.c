/*
 * Driver for the C backend of test-debug.
 *
 * It runs the process startup, which exercises (among other things) the
 * DECISION ANY construct: the startup transition contains two "decision any"
 * statements and the generated C picks a branch with rand().
 *
 * The C output is not compared to a fixed expected file because a decision
 * ANY is non-deterministic by design; the test succeeds as long as the
 * generated code builds and runs.
 */
#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"
#include "orchestrator.h"

/* Required interface used by the model (TASTE would provide it) */
void orchestrator_RI_telemetry(asn1SccMyEnum *telemetry_param) {}

int main()
{
    printf("[C Code] Running test\n");
    orchestrator_startup();
    return 0;
}
