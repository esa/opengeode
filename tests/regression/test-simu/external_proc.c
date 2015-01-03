#include <stdio.h>
#include "dataview-uniq.h"

void orchestrator_RI_ExternalProc(asn1SccT_UInt32 *gnc_output, asn1SccT_UInt32 *gnc_input)
{
    *gnc_output = *gnc_input + 1;
}
