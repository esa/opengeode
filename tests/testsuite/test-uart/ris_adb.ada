with Text_IO; use Text_IO;

package body RIs is
   procedure Check_Queue (Result: access Boolean) is
   begin
      Put_Line ("Checking queue");
      Result.all := False;
   end Check_Queue;

   procedure Send_To_UART (Msg: access Taste_dataview.asn1SccOctStr) is
   begin
      Put_Line ("Received " & Msg.Length'Img);
   end;

end RIs;

