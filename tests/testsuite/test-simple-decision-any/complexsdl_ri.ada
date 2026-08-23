with Ada.Text_IO;
with Shared_Counts;
package body Complexsdl_RI is
   procedure response(response_param : in out asn1SccMyInteger) is
      Val : constant Integer := Integer(response_param);
   begin
      Ada.Text_IO.Put_Line ("[Ada] response: " & Integer'Image(Val));
      if Val < 1 or Val > 4 then
         Ada.Text_IO.Put_Line ("Error: response value out of bounds: " & Integer'Image(Val));
         raise Program_Error;
      end if;
      Shared_Counts.Counts(Val) := Shared_Counts.Counts(Val) + 1;
   end response;
end Complexsdl_RI;