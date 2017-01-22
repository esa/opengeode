with orchestrator;
use orchestrator;
with orchestrator_stop_conditions;
with asn1_iterators.iterators;
use asn1_iterators.iterators;

with TASTE_BasicTypes;
use TASTE_BasicTypes;


with Ada.Text_IO;
use Ada.Text_IO;

with GNAT.MD5;

with Ada.Streams;
use Ada.Streams;

with Ada.Unchecked_Conversion;
with System;
with Ada.Strings.Hash;

with Ada.Containers.Ordered_Maps;
with Ada.Containers.Ordered_Sets;
with Ada.Containers.Vectors;
use Ada.Containers;

with Ada.Calendar;
use Ada.Calendar;

procedure model_checker is
    subtype Context_ty is orchestrator_ctxt_ty;
    Process_Ctxt : Context_ty renames orchestrator_Ctxt;

    -- To save/restore the context when calling a PI:
    backup_ctxt : Context_ty;
    backup_hash : Hash_Type;
    start_hash  : Hash_Type;

    -- Set a maximum size for vectors (set of states and edges)
    subtype Vect_Count is Positive range 1 .. 1000000;

    -- Type representing an event (input or output)
    type Interfaces is (start, arr_pi, paramless_pi, pulse_pi);
    type Event_ty (Option: Interfaces := start) is
        record
            case Option is
                when start =>
                    null;
                when arr_pi =>
                    arr_Param: aliased asn1SccT_SeqOf;
                when paramless_pi =>
                    null;
                when pulse_pi =>
                    pulse_Param: aliased asn1SccT_Int;
            end case;
    end record;


    procedure Print_Event(Event: Event_ty) is
    begin
         case Event.Option is
            when start =>
                Put_Line("START");
            when arr_pi =>
                Put_Line("Arr {" & T_SeqOf_Pkg.Image(Event.Arr_Param) & " }");
            when paramless_pi =>
                Put_Line("Paramless");
            when pulse_pi =>
                Put_Line(T_Int_Pkg.Image(Event.Pulse_Param));
        end case;
    end;

    -- An edge is made of a past state reference and an event to leave it
    type Edge_ty is
        record
            event   : Event_ty;
            state   : Hash_Type;  -- Previous state reached by event
    end record;

    package Edges_Pkg is new Vectors (Element_Type => Edge_ty,
                                      Index_Type   => Vect_Count);

    -- A state is made of a context and a set of edges leading to it
    type Global_State is
        record
            edges   : Edges_Pkg.Vector := Edges_Pkg.Empty_Vector;
            context : Context_ty;
    end record;

    -- We store only pointers to graph states in the map
    type State_Access is access Global_State;

    -- The state graph itself is stored in a dictionary type (map)
    package State_graph is new Ordered_Maps (Key_Type     => Hash_Type,
                                             Element_Type => State_Access);
    Grafset : State_graph.Map;

    -- State graph index: Use md5 first to get a string representing
    -- the context object, then strings.hash to get a number that can be used
    -- as a map key. This can surely be improved!
    Ctxt_Size: constant stream_element_offset :=
           Context_ty'object_size / stream_element'size;
    type SEA_Pointer is
         access all Stream_Element_Array (1 .. Ctxt_Size);

    function As_SEA_Ptr is
       new Ada.Unchecked_Conversion (System.Address, SEA_Pointer);

    function State_Hash(Context: Context_Ty) return Hash_Type is
        (Ada.Strings.Hash(gnat.md5.digest(as_sea_ptr(Context'Address).all)));

    -- Add a state to the graph: compute the hash (key) and store if not already there
    function Add_to_graph(event : Event_ty) return Hash_Type is
        New_State: State_Access;
        New_Hash : Hash_Type;
        New_Edge : constant Edge_ty := (event => event, state => backup_hash);
    begin
        New_Hash := State_Hash(Process_Ctxt);
        if not Grafset.Contains(Key => New_Hash) then
            New_State := new Global_State;
            New_State.context := Process_Ctxt;
            Grafset.Insert(Key => New_Hash, New_Item => New_State);
        else
            New_State := Grafset.Element(Key => New_Hash);
        end if;
        New_State.edges.append(New_Edge);
        return New_Hash;
    end;

    -- To count the number of calls to the function's provided interfaces
    count : natural := 0;

    -- Vector of hashes (integers) used for the model checking
    package Lists is new Vectors (Element_Type => Hash_Type,
                                  Index_type   => Vect_Count);

    package Sets is new Ordered_Sets(Element_Type => Hash_Type);

    queue   : Lists.Vector;
    visited : Sets.Set;
    properties: Sets.Set;

    -- Check all properties in one go, and if one fails, set errno
    function check_properties(errno: out natural) return boolean is
        res : Boolean := false;
    begin
        errno := 0;
        res := orchestrator_stop_conditions.p‹property_0;
        if res then
            return res;
        end if;
        return res;
    end;

    -- Report the result of the property check to the user
    procedure check_and_report (S_Hash: Hash_Type) is
        errno: Natural := 0;
        stop_condition: boolean := false;
    begin
        if check_properties(errno) then
            put_line("Property " & errno'img & " is verified, at step " & count'img);
            stop_condition := true;
            if properties.Length <= 10 then
                properties.include(s_hash);
            end if;
        end if;
        if not visited.contains(s_hash) then
            visited.insert(s_hash);
            if stop_condition = false then
                queue.append(S_Hash);
            end if;
        end if;
    end;


    -- One function per PI to exhaust the interface parameters
    procedure exhaust_arr is
        arr_it    : T_SeqOf_pkg.Instance;
        event             : Event_ty(arr_pi);
        S_Hash            : Hash_Type;
    begin
        for each of arr_it loop
            T_SeqOf_pkg.To_ASN1(each, event.arr_param);
            orchestrator.arr(event.arr_param'access);
            count := count + 1;
            S_Hash := Add_to_graph(event => event);
            check_and_report(S_Hash);
            Process_Ctxt := backup_ctxt;
            exit when properties.length >= 10;
        end loop;
    end;

    procedure exhaust_paramless is
        event             : Event_ty(paramless_pi);
        S_Hash            : Hash_Type;
    begin
        orchestrator.paramless;
        count := count + 1;
        S_Hash := Add_to_graph(event => event);
        check_and_report(S_Hash);
        Process_Ctxt := backup_ctxt;
    end;

    procedure exhaust_pulse is
        pulse_it    : T_Int_pkg.Instance;
        event             : Event_ty(pulse_pi);
        S_Hash            : Hash_Type;
    begin
        for each of pulse_it loop
            T_Int_pkg.To_ASN1(each, event.pulse_param);
            orchestrator.pulse(event.pulse_param'access);
            count := count + 1;
            S_Hash := Add_to_graph(event => event);
            check_and_report(S_Hash);
            Process_Ctxt := backup_ctxt;
            exit when properties.length >= 10;
        end loop;
    end;

    procedure exhaustive_simulation is
    begin
        backup_ctxt := Process_Ctxt;
        backup_hash := State_Hash(Backup_ctxt);
        if Process_Ctxt.State in running | wait then
            exhaust_arr;
        end if;
        if Process_Ctxt.State in running | wait then
            exhaust_paramless;
        end if;
        if Process_Ctxt.State in running | wait then
            exhaust_pulse;
        end if;
    end;

    procedure Generate_MSC is
        package Loc_Maps is new Ordered_Maps(Key_Type     => Hash_Type,
                                             Element_Type => Boolean);
        package Evt_Lists is new Vectors(Element_Type => Event_ty,
                                         Index_Type   => Vect_Count);
        package Parent_Maps is new Ordered_Maps(Key_Type     => Hash_Type,
                                                Element_Type => Edge_ty);
        function Find_Path(From: Hash_Type) return Evt_Lists.Vector is
            Loc_Q       : Lists.Vector;
            Loc_Visited : Loc_Maps.Map;
            Next_Hash   : Hash_Type;
            State       : State_Access;
            Parent_Map  : Parent_Maps.Map;
            Curr        : Hash_Type;
            Edge        : Edge_Ty;
            Scenario    : Evt_Lists.Vector;
        begin
            Loc_Q.append(From);
            Loc_Visited.Include(Key => From, New_Item => True);
            while not Loc_Q.Is_Empty loop
                Next_Hash := Loc_Q.Last_Element;
                exit when Next_Hash = Start_Hash;
                State := Grafset.Element(Key => Next_Hash);
                for each_edge of State.Edges loop
                    if not Loc_Visited.Contains(each_edge.state) then
                        Loc_Q.append(Each_Edge.state);
                        Loc_Visited.Include(Key      => each_edge.state,
                                            New_Item => True);
                        Parent_Map.Include(Key      => Each_Edge.State,
                                           New_Item => (State => Next_Hash,
                                                        Event => Each_Edge.Event));
                    end if;
                end loop;
                Loc_Q.Delete_Last;
            end loop;
            Curr := Start_Hash;
            Put_Line("Found path!");
            while Parent_Map.Contains(Curr) loop
                Edge := Parent_Map.Element(Curr);
                Curr := Edge.State;
                Scenario.Append(Edge.Event);
            end loop;
            return Scenario;
        end;

        Scenario : Evt_Lists.Vector;
    begin
        for each_hash of properties loop
            put_line("Path from hash " & each_hash'img & " to hash " & start_hash'img);
            Scenario := Find_Path(each_hash);
            for each_evt of Scenario loop
                Print_Event(each_evt);
            end loop;
        end loop;
    end;

    event      : Event_ty(start);
    Start_Time : constant Time := Clock;
begin
    put_line("Exhaustive simulation. Hit Ctrl-C to stop if it is too long...");
    orchestrator.startup;
    Start_Hash := Add_to_graph(event => event);
    check_and_report(Start_Hash);
    queue.append(Start_Hash);
    visited.include(Start_Hash);
    while queue.Length > 0 and properties.length <= 10 loop
        Process_Ctxt := Grafset.Element(Key => queue.Last_Element).Context;
        exhaustive_simulation;
        queue.delete_last;
    end loop;
    if properties.length > 0 then
        Generate_MSC;
    end if;
    put_line("Executed" & count'img & " functions");
    put_line("Visited" & Grafset.Length'img & " states");
    Put_Line("Execution time:" & Duration'Image(Clock - Start_Time) & "s.");
end;
