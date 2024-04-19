with og;

procedure test_ada is
    val : boolean := True;
begin
    og.saved_signal(val);
    val := False;
    og.saved_signal(val);
    og.run;
end;
