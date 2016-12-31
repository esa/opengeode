with orchestrator;
with orchestrator_stop_conditions;
with asn1_iterators;
use  asn1_iterators;
with TASTE_BasicTypes;
use  TASTE_BasicTypes;

with ada.text_io;
use ada.text_io;

procedure test is
    count : natural := 0;

    function check(errno: out natural) return boolean is
        res : Boolean := false;
    begin
        errno := 0;
        res := orchestrator_stop_conditions.p‹property_0;
        count := count + 1;
        return res;
    end;

    procedure check_and_report is
        errno: Natural := 0;
    begin
        if check(errno) then
            put_line("Property " & errno'img & " is not verified, at step " & count'img);
        end if;
    end;

    procedure exhaust_pulse is
        pulse_it : T_Int_pkg.Instance;
        asn1_p   : aliased asn1SccT_Int;
    begin
        for each of pulse_it loop
            asn1_p := asn1SccT_Int'(asn1SccT_Int(each));
            orchestrator.pulse(asn1_p'access);
            check_and_report;
        end loop;
    end;

    procedure exhaust_arr is
        arr_it : T_SeqOf_pkg.Instance;
        asn1_p : aliased asn1SccT_SeqOf;
    begin
        for each of arr_it loop
            asn1_p.Length := each.Length;
            for idx in 1..asn1_p.Length loop
                asn1_p.Data(idx) := asn1SccT_Int'(asn1SccT_Int(each.Data(idx)));
            end loop;
            orchestrator.arr(asn1_p'access);
            check_and_report;
        end loop;
    end;
begin
    put_line("hello");
    orchestrator.startup;
    check_and_report;
    exhaust_pulse;
    exhaust_arr;
    put_line("Executed" & count'img & " functions");
end;
