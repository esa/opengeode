with Text_IO; use Text_IO;

package body RIs is
   procedure Check_Queue (Result: out Boolean) is
   begin
      Put_Line ("Checking queue");
      Result := False;
   end Check_Queue;
end RIs;

