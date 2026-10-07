#include <math.h>
#include <stdio.h>
#include "dataview-uniq.h"
#include "orchestrator.h"

/* Required interfaces the environment must provide. ExternalProc is
 * implemented in external_proc.c; the others are stubbed because this
 * driver only exercises `other`, which does not call them. */
void orchestrator_RI_peek_list(asn1SccTASTE_Peek_id_list *_) { (void)_; }
void orchestrator_RI_peek_fixed(asn1SccFixedIntList *_) { (void)_; }
void orchestrator_RI_telemetry(asn1SccMyEnum *_) { (void)_; }
void orchestrator_RI_Paramless_TM(void) {}
void orchestrator_RI_SET_myTimer(const asn1SccT_UInt32 *val) { (void)val; }
void orchestrator_RI_RESET_myTimer(void) {}
void orchestrator_RI_VDM(asn1SccFixedIntList *inp, asn1SccFixedIntList *outp)
{
    (void)inp;
    (void)outp;
}
void orchestrator_RI_VDM2(asn1SccT_UInt32 *inp, asn1SccMySimpleSeq *outp)
{
    (void)inp;
    (void)outp;
}

/* Mirrors test_ada.c: one startup (Ada's adainit() elaboration runs the
 * startup transition once), then the current state around two `other`
 * inputs. orchestrator_startup() is the C entry point (it runs CInit). */
int main()
{
    printf("[C Code] Running test\n");

    orchestrator_startup();

    printf("%s\n", orchestrator_state());
    orchestrator_PI_other();
    printf("%s\n", orchestrator_state());
    orchestrator_PI_other();
    printf("%s\n", orchestrator_state());
    printf("\n");

    return 0;
}
