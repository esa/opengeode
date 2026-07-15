with Ada.Text_IO;
with Complexsdl;
with Shared_Counts;
use Shared_Counts;
with TESTBENCH2_DATAVIEW; use TESTBENCH2_DATAVIEW;

procedure Test_Ada is
   Input_Val : aliased asn1SccMyInteger := 42;
begin
   Ada.Text_IO.Put_Line ("[Ada Code] Running test");
   Complexsdl.Startup;
   for I in 1 .. 10 loop
      Complexsdl.impulse(Input_Val);
   end loop;
   
   -- Check that it is not 10 times the same
   for I in 1 .. 4 loop
      if Counts(I) = 10 then
         Ada.Text_IO.Put_Line ("Error: All 10 responses were identical: " & Integer'Image(I));
         raise Program_Error;
      end if;
   end loop;
   Ada.Text_IO.Put_Line ("Ada test completed successfully");
end Test_Ada;
