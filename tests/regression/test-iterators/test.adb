with orchestrator;
with orchestrator_stop_conditions;
with asn1_iterators;
use  asn1_iterators;
with TASTE_BasicTypes;
use  TASTE_BasicTypes;

with ada.text_io;
use ada.text_io;

with gnat.md5;
with ada.streams;
use ada.streams;
with ada.Unchecked_Conversion;
with system;

procedure test is
    -- Reproduce the Context, and import it
    type States is (running, wait);
    type orchestrator_ctxt_Ty is
        record
        state : States;
        initDone : Boolean := False;
        counter : aliased asn1SccT_Int := 0;
        seqof : aliased asn1SccT_SeqOf;
        t : aliased asn1SccT_Int := 0;
    end record;
    orchestrator_ctxt: orchestrator_ctxt_Ty;
    pragma Import (C, orchestrator_ctxt, "orchestrator_ctxt");

    -- To save/restore the context when calling a PI:
    backup_ctxt : orchestrator_ctxT_ty;

    -- Type representing an event (input or output)
    type Interfaces is (pulse_pi, arr_pi, paramless_pi);
    type Event_ty (Option: Interfaces) is
        record
            case Option is
                when pulse_pi =>
                    Pulse_Param: asn1SccT_Int;
                when arr_pi =>
                    Arr_Param: asn1SccT_SeqOf;
                when paramless_pi =>
                    null;
            end case;
    end record;

    -- Type representing an entry in the state graph
    type Graph_State is
        record
            event  : access Event_ty; -- Event causing the transition
            context: orchestrator_ctxt_ty;
    end record;

    count : natural := 0;

    procedure save_context is
    begin
        backup_ctxt := orchestrator_ctxt;
    end;

    procedure restore_context is
    begin
        orchestrator_ctxt := backup_ctxt;
    end;

    -- Check all properties in one go, and if one fails, set errno
    function check_properties(errno: out natural) return boolean is
        res : Boolean := false;
    begin
        errno := 0;
        res := orchestrator_stop_conditions.p‹property_0;
        count := count + 1;
        return res;
    end;

    -- Report the result of the property check to the user
    procedure check_and_report is
        errno: Natural := 0;
    begin
        if check_properties(errno) then
            put_line("Property " & errno'img & " is verified, at step " & count'img);
        end if;
    end;

    -- One function per PI to exhaust the interface parameters
    procedure exhaust_pulse is
        pulse_it : T_Int_pkg.Instance;
        asn1_p   : aliased asn1SccT_Int;
    begin
        for each of pulse_it loop
            save_context;
            asn1_p := asn1SccT_Int'(asn1SccT_Int(each));
            orchestrator.pulse(asn1_p'access);
            check_and_report;
            restore_context;
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
    Ctxt_Size: constant stream_element_offset :=
           orchestrator_ctxt_ty'object_size / stream_element'size;
    type SEA_Pointer is
         access all Stream_Element_Array (1 .. Ctxt_Size);

    function As_SEA_Pointer is
         new Ada.Unchecked_Conversion (System.Address, SEA_Pointer);
begin
    put_line("hello");
    orchestrator.startup;
    check_and_report;
    -- Compute the MD5 of the state, as a hash
    Put_Line (gnat.md5.digest(As_SEA_Pointer (orchestrator_ctxt'Address).all));
    exhaust_pulse;
    exhaust_arr;
    put_line("Executed" & count'img & " functions");
end;
