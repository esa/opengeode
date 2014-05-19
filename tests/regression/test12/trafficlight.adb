-- This file was generated automatically: DO NOT MODIFY IT !

with System.IO;
use System.IO;

with TASTE_BasicTypes;
use TASTE_BasicTypes;
with TASTE_Dataview;
use TASTE_Dataview;

with adaasn1rtl;
use adaasn1rtl;

with Interfaces;
use Interfaces;

package body trafficlight is
    l_on_pedwaiting_color : aliased asn1SccLight;
    l_init_state : aliased asn1SccLight;
    l_request : aliased asn1SccT_Boolean;
    l_on_pedwaiting_counter : aliased asn1SccT_UInt8 := 0;
    type states is (on_streetprepare, maintenance_yellowoff_idle, off, maintenance_yellowon_idle, on_pedestriangreen, on_pedwaiting_waiton_wait_counter, on_pedestrianred, on_streetred, on_streetgreen, on_streetattention);
    state : states;
    on_pedwaiting_waiton_START : constant := 17;
    maintenance_yellowoff_START : constant := 5;
    on_pedwaiting_START : constant := 15;
    maintenance_yellowon_START : constant := 6;
    on_START : constant := 7;
    maintenance_START : constant := 2;
    procedure runTransition(Id: Integer);
    procedure state_start;
    procedure maintenance_yellowoff_entry;
    procedure maintenance_yellowon_entry;
    procedure on_pedwaiting_waiton_entry;
    procedure on_pedwaiting_waiton_exit;
    procedure on_pedwaiting_entry;
    procedure state_start is
        begin
            null;
        end state_start;
    procedure maintenance_yellowoff_entry is
        tmp4 : aliased asn1SccT_Uint32;
        tmp7 : aliased asn1SccLight;
        begin
            -- set_timer(500, timeout) (12,5)
            tmp4 := 500;
            SET_timeout(tmp4'access);
            -- SetTrafficLightColor(all_off) (14,7)
            tmp7 := asn1Sccall_off;
            SetTrafficLightColor(tmp7'access);
            -- RETURN  (None,None) at 197, 185
            return;
        end maintenance_yellowoff_entry;
        

    procedure maintenance_yellowon_entry is
        tmp10 : aliased asn1SccT_Uint32;
        tmp13 : aliased asn1SccLight;
        begin
            -- set_timer(500, timeout) (34,5)
            tmp10 := 500;
            SET_timeout(tmp10'access);
            -- SetTrafficLightColor(yellow) (36,7)
            tmp13 := asn1Sccyellow;
            SetTrafficLightColor(tmp13'access);
            -- RETURN  (None,None) at 309, 274
            return;
        end maintenance_yellowon_entry;
        

    procedure on_pedwaiting_waiton_entry is
        tmp20 : aliased asn1SccT_Uint32;
        begin
            -- set_timer(500, timeout) (83,5)
            tmp20 := 500;
            SET_timeout(tmp20'access);
            -- RETURN  (None,None) at 202, 147
            return;
        end on_pedwaiting_waiton_entry;
        

    procedure on_pedwaiting_waiton_exit is
        begin
            -- counter := counter + 1 (92,5)
            l_on_pedwaiting_counter := (l_on_pedwaiting_counter + 1);
            -- RETURN  (None,None) at 297, 259
            return;
        end on_pedwaiting_waiton_exit;
        

    procedure on_pedwaiting_entry is
        begin
            -- writeln('Pedestrian request') (115,5)
            Put_Line("Pedestrian request");
            -- counter := 0 (117,5)
            l_on_pedwaiting_counter := 0;
            -- RETURN  (None,None) at 400, 263
            return;
        end on_pedwaiting_entry;
        

    procedure pedestrianRequest(buttonpress: access asn1SccT_Boolean) is
        begin
            case state is
                when on_streetprepare =>
                    null;
                when maintenance_yellowoff_idle =>
                    null;
                when off =>
                    null;
                when maintenance_yellowon_idle =>
                    null;
                when on_pedestriangreen =>
                    null;
                when on_pedwaiting_waiton_wait_counter =>
                    null;
                when on_pedestrianred =>
                    null;
                when on_streetred =>
                    null;
                when on_streetgreen =>
                    l_request := buttonpress.all;
                    runTransition(14);
                when on_streetattention =>
                    null;
                when others =>
                    null;
            end case;
        end pedestrianRequest;
        

    procedure onOff(color: access asn1SccLight) is
        begin
            case state is
                when on_streetprepare =>
                    l_init_state := color.all;
                    runTransition(1);
                when maintenance_yellowoff_idle =>
                    l_init_state := color.all;
                    runTransition(1);
                when off =>
                    l_init_state := color.all;
                    runTransition(1);
                when maintenance_yellowon_idle =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_pedestriangreen =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_pedwaiting_waiton_wait_counter =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_pedestrianred =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_streetred =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_streetgreen =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_streetattention =>
                    l_init_state := color.all;
                    runTransition(1);
                when others =>
                    null;
            end case;
        end onOff;
        

    procedure timeout is
        begin
            case state is
                when on_streetprepare =>
                    runTransition(8);
                when maintenance_yellowoff_idle =>
                    runTransition(3);
                when off =>
                    null;
                when maintenance_yellowon_idle =>
                    runTransition(4);
                when on_pedestriangreen =>
                    runTransition(10);
                when on_pedwaiting_waiton_wait_counter =>
                    on_pedwaiting_waiton_exit;
                    runTransition(16);
                when on_pedestrianred =>
                    runTransition(9);
                when on_streetred =>
                    runTransition(11);
                when on_streetgreen =>
                    null;
                when on_streetattention =>
                    runTransition(12);
                when others =>
                    null;
            end case;
        end timeout;
        

    procedure runTransition(Id: Integer) is
        trId : Integer := Id;
        tmp80 : aliased asn1SccLight;
        tmp82 : aliased asn1SccLight;
        tmp43 : aliased asn1SccLight;
        tmp46 : aliased asn1SccT_Uint32;
        tmp49 : aliased asn1SccLight;
        tmp52 : aliased asn1SccT_Uint32;
        tmp55 : aliased asn1SccLight;
        tmp58 : aliased asn1SccT_Uint32;
        tmp61 : aliased asn1SccLight;
        tmp64 : aliased asn1SccT_Uint32;
        tmp67 : aliased asn1SccLight;
        tmp72 : aliased asn1SccT_Uint32;
        tmp75 : aliased asn1SccLight;
        tmp38 : asn1SccLight;
        begin
            while (trId /= -1) loop
                case trId is
                    when 0 =>
                        -- NEXT_STATE Off (240,10) at 298, 100
                        trId := -1;
                        state := Off;
                        goto next_transition;
                    when 1 =>
                        -- DECISION init_state (255,9)
                        -- ANSWER green (257,1)
                        if l_init_state = asn1Sccgreen then
                            -- SetPedestrianColor(red) (259,7)
                            tmp80 := asn1Sccred;
                            SetPedestrianColor(tmp80'access);
                            -- SetTrafficLightColor(green) (261,7)
                            tmp82 := asn1Sccgreen;
                            SetTrafficLightColor(tmp82'access);
                            -- NEXT_STATE on (263,10) at 379, 390
                            trId := on_START;
                            goto next_transition;
                            -- ANSWER ELSE (None,None)
                        else
                            -- NEXT_STATE Maintenance (267,10) at 527, 290
                            trId := maintenance_START;
                            goto next_transition;
                        end if;
                    when 2 =>
                        -- writeln('Entering Maintenance') (52,5)
                        Put_Line("Entering Maintenance");
                        -- NEXT_STATE maintenance_YellowOn (54,10) at 740, 354
                        trId := maintenance_yellowon_START;
                        goto next_transition;
                    when 3 =>
                        -- NEXT_STATE maintenance_YellowOn (61,10) at 736, 564
                        trId := maintenance_yellowon_START;
                        goto next_transition;
                    when 4 =>
                        -- NEXT_STATE maintenance_YellowOff (68,10) at 738, 459
                        trId := maintenance_yellowoff_START;
                        goto next_transition;
                    when 5 =>
                        -- entry (None,None)
                        maintenance_yellowoff_entry;
                        -- NEXT_STATE maintenance_yellowoff_idle (21,10) at 348, 487
                        trId := -1;
                        state := maintenance_yellowoff_idle;
                        goto next_transition;
                    when 6 =>
                        -- entry (None,None)
                        maintenance_yellowon_entry;
                        -- NEXT_STATE maintenance_yellowon_idle (43,10) at 489, 381
                        trId := -1;
                        state := maintenance_yellowon_idle;
                        goto next_transition;
                    when 7 =>
                        -- NEXT_STATE on_StreetGreen (152,10) at 698, 200
                        trId := -1;
                        state := on_StreetGreen;
                        goto next_transition;
                    when 8 =>
                        -- SetTrafficLightColor(green) (159,7)
                        tmp43 := asn1Sccgreen;
                        SetTrafficLightColor(tmp43'access);
                        -- NEXT_STATE on_StreetGreen (161,10) at 1013, 747
                        trId := -1;
                        state := on_StreetGreen;
                        goto next_transition;
                    when 9 =>
                        -- set_timer(2000, timeout) (168,5)
                        tmp46 := 2000;
                        SET_timeout(tmp46'access);
                        -- SetTrafficLightColor(yellow) (170,7)
                        tmp49 := asn1Sccyellow;
                        SetTrafficLightColor(tmp49'access);
                        -- NEXT_STATE on_StreetPrepare (172,10) at 1013, 592
                        trId := -1;
                        state := on_StreetPrepare;
                        goto next_transition;
                    when 10 =>
                        -- set_timer(5000, timeout) (179,5)
                        tmp52 := 5000;
                        SET_timeout(tmp52'access);
                        -- SetPedestrianColor(red) (181,7)
                        tmp55 := asn1Sccred;
                        SetPedestrianColor(tmp55'access);
                        -- NEXT_STATE on_PedestrianRed (183,10) at 1013, 387
                        trId := -1;
                        state := on_PedestrianRed;
                        goto next_transition;
                    when 11 =>
                        -- set_timer(7000, timeout) (191,5)
                        tmp58 := 7000;
                        SET_timeout(tmp58'access);
                        -- SetPedestrianColor(green) (193,7)
                        tmp61 := asn1Sccgreen;
                        SetPedestrianColor(tmp61'access);
                        -- NEXT_STATE on_PedestrianGreen (195,10) at 685, 978
                        trId := -1;
                        state := on_PedestrianGreen;
                        goto next_transition;
                    when 12 =>
                        -- set_timer(2000, timeout) (202,5)
                        tmp64 := 2000;
                        SET_timeout(tmp64'access);
                        -- SetTrafficLightColor(red) (204,7)
                        tmp67 := asn1Sccred;
                        SetTrafficLightColor(tmp67'access);
                        -- NEXT_STATE on_StreetRed (206,10) at 704, 773
                        trId := -1;
                        state := on_StreetRed;
                        goto next_transition;
                    when 13 =>
                        -- writeln('counter_expired') (213,5)
                        Put_Line("counter_expired");
                        -- set_timer(2000, timeout) (215,5)
                        tmp72 := 2000;
                        SET_timeout(tmp72'access);
                        -- SetTrafficLightColor(yellow) (217,7)
                        tmp75 := asn1Sccyellow;
                        SetTrafficLightColor(tmp75'access);
                        -- NEXT_STATE on_StreetAttention (219,10) at 679, 568
                        trId := -1;
                        state := on_StreetAttention;
                        goto next_transition;
                    when 14 =>
                        -- NEXT_STATE on_PedWaiting (227,10) at 702, 313
                        trId := on_pedwaiting_START;
                        goto next_transition;
                    when 15 =>
                        -- entry (None,None)
                        on_pedwaiting_entry;
                        -- NEXT_STATE on_pedwaiting_waitOn (124,10) at 348, 180
                        trId := on_pedwaiting_waiton_START;
                        goto next_transition;
                    when 16 =>
                        -- DECISION counter (131,9)
                        -- ANSWER 14 (133,1)
                        if l_on_pedwaiting_counter = 14 then
                            -- writeln('Leaving PedWaiting') (135,5)
                            Put_Line("Leaving PedWaiting");
                            -- RETURN counter_expired (None,None) at 178, 443
                            trId := 13;
                            goto next_transition;
                            -- ANSWER ELSE (None,None)
                        else
                            -- color := if counter mod 2 = 0 then red else all_off fi (141,5)
                            if ((l_on_pedwaiting_counter mod 2) = 0) then
                                tmp38 := asn1Sccred;
                            else
                                tmp38 := asn1Sccall_off;
                            end if;
                            l_on_pedwaiting_color := tmp38;
                            -- SetPedestrianColor(color) (143,7)
                            SetPedestrianColor(l_on_pedwaiting_color'access);
                            -- NEXT_STATE - (145,10) at 465, 493
                            case state is
                                when on_pedwaiting_waiton_wait_counter =>
                                    trId := on_pedwaiting_waiton_START;
                                when others =>
                                    trId := -1;
                            end case;
                            goto next_transition;
                        end if;
                    when 17 =>
                        -- entry (None,None)
                        on_pedwaiting_waiton_entry;
                        -- NEXT_STATE on_pedwaiting_waiton_wait_counter (99,10) at 347, 106
                        trId := -1;
                        state := on_pedwaiting_waiton_wait_counter;
                        goto next_transition;
                    when others =>
                        null;
                end case;
                <<next_transition>>
                null;
            end loop;
        end runTransition;
        

    begin
        runTransition(0);
end trafficlight;