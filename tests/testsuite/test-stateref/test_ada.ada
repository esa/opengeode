with complexsdl;
use complexsdl;
with testbench2_dataview;
use testbench2_dataview;

procedure test_ada is
   x : asn1SccMyInteger := 0;
begin
    Startup;
    impulse (x);
    impulse (x);
end test_ada;
