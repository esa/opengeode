with foo;
with DV; use DV;

procedure test_ada is
    val : aliased asn1SccMyInteger := 42;
begin
    foo.keep_sig;
    foo.sig_enabled(val);
    foo.exp_enabled(val);
    foo.timer_enabled;
end test_ada;
