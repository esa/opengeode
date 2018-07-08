with TASTE_DataView;
use TASTE_DataView;
package ris is
    procedure Send_To_UART (Msg: Access Taste_dataview.asn1SccOctStr) is null;
    pragma Export (C, Send_To_UART, "og_RI_send_to_uart");
    function Check_Queue return Boolean is (True);
    pragma Export (C, Check_Queue, "og_check_queue");
end ris;
