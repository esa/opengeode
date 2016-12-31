with orchestrator;
with orchestrator_stop_conditions;
with asn1_iterators;

with ada.text_io;
use ada.text_io;

procedure test is
    function check(errno: out natural) return boolean is
    begin
        put_line("checking properties");
        errno := 0;
        return orchestrator_stop_conditions.p‹property_0;
    end;
    errno: Natural := 0;
begin
    put_line("hello");
    orchestrator.startup;
    if check(errno) then
        put_line("Property " & errno'img & " is not verified");
    end if;
end;
