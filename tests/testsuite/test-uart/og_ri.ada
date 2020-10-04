with Text_IO; use Text_IO;
package body og_RI is
   procedure send_to_uart (send_to_uart_param : in out asn1SccOctStr) is 
   begin
      Put_Line ("Received " & Send_To_UART_Param.Length'Img);
   end;
end og_RI;
