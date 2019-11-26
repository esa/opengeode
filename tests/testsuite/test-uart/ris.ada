with TASTE_DataView;
use TASTE_DataView;
package ris is
    procedure Send_To_UART (Msg: access Taste_dataview.asn1SccOctStr);
    pragma Export (C, Send_To_UART, "og_RI_send_to_uart");
    procedure Check_Queue (Result: access Boolean);
    pragma Export (C, Check_Queue, "og_check_queue");
end ris;
