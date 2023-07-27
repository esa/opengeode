#include <stdio.h>
#include "dataview-uniq.h"
#include "og.h"

void og_RI_send_to_uart(asn1SccOctStr * send_to_uart_param)
{   
    printf(send_to_uart_param->nCount >= 0 ? "Received  %ld\n" : "Received %ld\n", send_to_uart_param->nCount);
}

void og_check_queue(bool* has_pending_msg)
{
    printf("Checking queue\n");
    *has_pending_msg = false;
}

int main()
{
    CInitog();

    og_PI_go();

    return 0;
}
