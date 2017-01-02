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
with ada.strings.hash;

with Ada.containers.hashed_sets;
with Ada.containers.vectors;
use Ada.containers;

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
    backup_ctxt : orchestrator_ctxt_ty;
    -- stop condition set to true when a property is verified
    stop_condition : boolean := false;

    -- Type representing an event (input or output)
    type Interfaces is (start, pulse_pi, arr_pi, paramless_pi);
    type Event_ty (Option: Interfaces) is
        record
            case Option is
                when start =>
                    null;
                when pulse_pi =>
                    Pulse_Param: asn1SccT_Int;
                when arr_pi =>
                    Arr_Param: asn1SccT_SeqOf;
                when paramless_pi =>
                    null;
            end case;
    end record;

    -- Type representing an entry in the state graph (could be generic)
    type Global_State is
        record
            event   : access Event_ty;
            context :        Orchestrator_ctxt_ty;
    end record;

    -- We'll store only pointers to graph states in the set
    type State_Access is access Global_State;

    count : natural := 0;

    procedure save_context is
    begin
        backup_ctxt := orchestrator_ctxt;
    end;

    procedure restore_context is
    begin
        orchestrator_ctxt := backup_ctxt;
    end;

    -- We will store the state graph in a hashed set. Use md5 to hash the
    -- SDL context.
    Ctxt_Size: constant stream_element_offset :=
           orchestrator_ctxt_ty'object_size / stream_element'size;
    type SEA_Pointer is
         access all Stream_Element_Array (1 .. Ctxt_Size);

    function As_SEA_Ptr is
       new Ada.Unchecked_Conversion (System.Address, SEA_Pointer);

    function State_Hash(state: State_Access) return Hash_Type is
        (Ada.Strings.Hash(gnat.md5.digest(as_sea_ptr(state.context'address).all)));

    package State_graph is new Hashed_Sets
                    (Element_Type        => State_Access,
                     Hash                => State_Hash,
                     Equivalent_Elements => "=");

    Grafset : State_graph.Set;

    function Add_to_graph(event : Event_ty;
                          ctxt  : orchestrator_ctxt_ty) return State_Access is
        New_State: constant State_Access := new Global_State;
    begin
        New_State.event := new Event_ty (event.Option);
        New_State.event.all := event;
        New_State.context   := ctxt;
        Grafset.Insert(New_State);
        return New_State;
    end;

    -- Build up a function to retrieve a state in the graph based on the hash
    function Get_Hash(S : State_Access) return Hash_Type is (State_Hash(S));
    function Hash_Hash(N : Hash_Type) return Hash_Type is (Hash_Type(N));
    package State_Keys is new State_graph.Generic_Keys (Key_Type => Hash_Type,
                                                        Key => Get_Hash,
                                                        Hash => Hash_Hash,
                                                        Equivalent_Keys => "=");
    function Retrieve_State (Hash: Hash_Type) return access Global_State is
        C: constant State_graph.Cursor :=
            State_Keys.Find (Grafset, Hash);
    begin
        if State_graph.Has_Element(C) then
            return State_graph.Element(C);
        else
            return Null;
        end if;
    end Retrieve_State;


    -- Check all properties in one go, and if one fails, set errno
    function check_properties(errno: out natural) return boolean is
        res : Boolean := false;
    begin
        errno := 0;
        res := orchestrator_stop_conditions.pÜproperty_0;
        count := count + 1;
        return res;
    end;

    -- Report the result of the property check to the user
    procedure check_and_report is
        errno: Natural := 0;
    begin
        if check_properties(errno) then
            put_line("Property " & errno'img & " is verified, at step " & count'img);
            stop_condition := true;
        end if;
    end;

    subtype Vect_Count is Positive range 1 .. 1000;
    package Lists is new Vectors (Element_Type => State_Access,
                                  Index_type   => Vect_Count);
    use Lists;

    queue   : Lists.Vector;
    qcursor : Lists.Cursor := queue.First;
    visited : Lists.Vector;


    -- One function per PI to exhaust the interface parameters
    procedure exhaust_pulse is
        pulse_it : T_Int_pkg.Instance;
        asn1_p   : aliased asn1SccT_Int;
        event    : Event_ty (pulse_pi);
        SA       : State_Access;
    begin
        for each of pulse_it loop
            stop_condition := false;
            save_context;
            event.pulse_param := asn1SccT_Int(each);
            asn1_p := asn1SccT_Int'(event.pulse_param);
            orchestrator.pulse(asn1_p'access);
            SA := Add_to_graph(event => event,
                               ctxt  => orchestrator_ctxt);
            check_and_report;
            restore_context;
            if visited.find(SA) = Lists.No_Element then
                visited.append(SA);
--               if stop_condition = false then
--                   queue.append(SA);
--               end if;
            end if;
        end loop;
    end;

    procedure exhaust_arr is
        arr_it : T_SeqOf_pkg.Instance;
        asn1_p : aliased asn1SccT_SeqOf;
        event  : Event_ty (arr_pi);
        SA     : State_Access;
    begin
        for each of arr_it loop
            save_context;
            asn1_p.Length := each.Length;
            for idx in 1..asn1_p.Length loop
                asn1_p.Data(idx) := asn1SccT_Int'(asn1SccT_Int(each.Data(idx)));
            end loop;
            event.Arr_Param := asn1_p;
            orchestrator.arr(asn1_p'access);
            SA := Add_to_graph(event => event,
                               ctxt  => orchestrator_ctxt);
            check_and_report;
            restore_context;
        end loop;
    end;

    procedure exhaust_paramless is
        event  : Event_ty (paramless_pi);
        SA     : State_Access;
    begin
        save_context;
        orchestrator.paramless;
        SA := Add_to_graph(event => event,
                           ctxt  => orchestrator_ctxt);
        check_and_report;
        restore_context;
    end;

    procedure exhaustive_simulation is
    begin
        exhaust_paramless;
        exhaust_pulse;
        exhaust_arr;
    end;

    event : Event_ty(start);
    SA    : State_Access;
begin
    put_line("Exhaustive simulation. Hit Ctrl-C to stop if it is too long...");
    orchestrator.startup;
    check_and_report;
    SA := Add_to_graph(event => event,
                       ctxt  => orchestrator_ctxt);
    queue.append(SA);
    visited.append(SA);
    while queue.Length > 0 loop
        orchestrator_ctxt := queue.Last_Element.context;
        exhaustive_simulation;
        -- discard the event for now (needed to generate MSC)
        queue.delete_last;
    end loop;
    put_line("Executed" & count'img & " functions");
end;
