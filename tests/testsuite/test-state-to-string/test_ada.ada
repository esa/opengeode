with Ada.Text_IO;            use Ada.Text_IO;
with Interfaces.C.Strings;   use Interfaces.C.Strings;
with complexsdl;             use complexsdl;
with testbench2_dataview;    use testbench2_dataview;

procedure test_ada is
begin
   Startup;
   Put_Line (Value (Get_State));
   tick;
   Put_Line (Value (Get_State));
   tick;
   Put_Line (Value (Get_State));
   tick;
   Put_Line (Value (Get_State));
end test_ada;
