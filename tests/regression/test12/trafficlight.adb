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
    type states is (maintenance_yellowon_idle, on_pedestriangreen, on_streetgreen, on_streetprepare, maintenance_yellowoff_idle, off, on_streetattention, on_pedwaiting_waiton_wait_counter, on_pedestrianred, on_streetred);
    state : states;
    on_pedwaiting_START : constant := 10;
    maintenance_yellowoff_START : constant := 16;
    maintenance_yellowon_START : constant := 17;
    on_START : constant := 2;
    on_pedwaiting_waiton_START : constant := 12;
    maintenance_START : constant := 13;
    procedure runTransition(Id: Integer);
    procedure state_start;
    procedure on_pedwaiting_waiton_exit;
    procedure on_pedwaiting_entry;
    procedure maintenance_yellowoff_entry;
    procedure maintenance_yellowon_entry;
    procedure state_start is
        begin
            null;
        end state_start;
    procedure on_pedwaiting_waiton_exit is
        begin
            -- counter := counter + 1 (15,5)
            l_on_pedwaiting_counter := (l_on_pedwaiting_counter + 1);
            -- RETURN  (None,None) at 297, 259
            return;
        end on_pedwaiting_waiton_exit;
        

    procedure on_pedwaiting_entry is
        tmp3 : aliased asn1SccT_Uint32;
        begin
            -- set_timer(500, timeout) (38,5)
            tmp3 := 500;
            SET_timeout(tmp3'access);
            -- counter := 0 (40,5)
            l_on_pedwaiting_counter := 0;
            -- RETURN  (None,None) at 400, 263
            return;
        end on_pedwaiting_entry;
        

    procedure maintenance_yellowoff_entry is
        tmp46 : aliased asn1SccT_Uint32;
        tmp49 : aliased asn1SccLight;
        begin
            -- set_timer(500, timeout) (146,5)
            tmp46 := 500;
            SET_timeout(tmp46'access);
            -- SetTrafficLightColor(all_off) (148,7)
            tmp49 := asn1Sccall_off;
            SetTrafficLightColor(tmp49'access);
            -- RETURN  (None,None) at 197, 185
            return;
        end maintenance_yellowoff_entry;
        

    procedure maintenance_yellowon_entry is
        tmp52 : aliased asn1SccT_Uint32;
        tmp55 : aliased asn1SccLight;
        begin
            -- set_timer(500, timeout) (168,5)
            tmp52 := 500;
            SET_timeout(tmp52'access);
            -- SetTrafficLightColor(yellow) (170,7)
            tmp55 := asn1Sccyellow;
            SetTrafficLightColor(tmp55'access);
            -- RETURN  (None,None) at 309, 274
            return;
        end maintenance_yellowon_entry;
        

    procedure pedestrianRequest(buttonpress: access asn1SccT_Boolean) is
        begin
            case state is
                when maintenance_yellowon_idle =>
                    null;
                when on_pedestriangreen =>
                    null;
                when on_streetgreen =>
                    l_request := buttonpress.all;
                    runTransition(9);
                when on_streetprepare =>
                    null;
                when maintenance_yellowoff_idle =>
                    null;
                when off =>
                    null;
                when on_streetattention =>
                    null;
                when on_pedwaiting_waiton_wait_counter =>
                    null;
                when on_pedestrianred =>
                    null;
                when on_streetred =>
                    null;
                when others =>
                    null;
            end case;
        end pedestrianRequest;
        

    procedure onOff(color: access asn1SccLight) is
        begin
            case state is
                when maintenance_yellowon_idle =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_pedestriangreen =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_streetgreen =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_streetprepare =>
                    l_init_state := color.all;
                    runTransition(1);
                when maintenance_yellowoff_idle =>
                    l_init_state := color.all;
                    runTransition(1);
                when off =>
                    l_init_state := color.all;
                    runTransition(1);
                when on_streetattention =>
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
                when others =>
                    null;
            end case;
        end onOff;
        

    procedure timeout is
        begin
            case state is
                when maintenance_yellowon_idle =>
                    runTransition(15);
                when on_pedestriangreen =>
                    runTransition(5);
                when on_streetgreen =>
                    null;
                when on_streetprepare =>
                    runTransition(3);
                when maintenance_yellowoff_idle =>
                    runTransition(14);
                when off =>
                    null;
                when on_streetattention =>
                    runTransition(7);
                when on_pedwaiting_waiton_wait_counter =>
                    runTransition(11);
                when on_pedestrianred =>
                    runTransition(4);
                when on_streetred =>
                    runTransition(6);
                when others =>
                    null;
            end case;
        end timeout;
        

    procedure runTransition(Id: Integer) is
        trId : Integer := Id;
        tmp26 : aliased asn1SccT_Uint32;
        tmp30 : aliased asn1SccT_Uint32;
        tmp34 : aliased asn1SccT_Uint32;
        tmp38 : aliased asn1SccT_Uint32;
        tmp42 : aliased asn1SccT_Uint32;
        tmp20 : asn1SccLight;
        begin
            while (trId /= -1) loop
                case trId is
                    when 0 =>
                        -- NEXT_STATE Off (213,10) at 298, 100
                        trId := -1;
                        state := Off;
                        goto next_transition;
                    when 1 =>
                        -- DECISION init_state (222,9)
                        -- ANSWER green (224,1)
                        if l_init_state = asn1Sccgreen then
                            -- NEXT_STATE on (226,10) at 379, 290
                            trId := on_START;
                            goto next_transition;
                            -- ANSWER ELSE (None,None)
                        else
                            -- NEXT_STATE Maintenance (230,10) at 465, 290
                            trId := maintenance_START;
                            goto next_transition;
                        end if;
                    when 2 =>
                        -- NEXT_STATE on_StreetGreen (73,10) at 698, 200
                        trId := -1;
                        state := on_StreetGreen;
                        goto next_transition;
                    when 3 =>
                        -- NEXT_STATE on_StreetGreen (80,10) at 1013, 597
                        trId := -1;
                        state := on_StreetGreen;
                        goto next_transition;
                    when 4 =>
                        -- set_timer(2000, timeout) (87,5)
                        tmp26 := 2000;
                        SET_timeout(tmp26'access);
                        -- NEXT_STATE on_StreetPrepare (89,10) at 1013, 492
                        trId := -1;
                        state := on_StreetPrepare;
                        goto next_transition;
                    when 5 =>
                        -- set_timer(5000, timeout) (96,5)
                        tmp30 := 5000;
                        SET_timeout(tmp30'access);
                        -- NEXT_STATE on_PedestrianRed (98,10) at 1013, 337
                        trId := -1;
                        state := on_PedestrianRed;
                        goto next_transition;
                    when 6 =>
                        -- set_timer(7000, timeout) (106,5)
                        tmp34 := 7000;
                        SET_timeout(tmp34'access);
                        -- NEXT_STATE on_PedestrianGreen (108,10) at 684, 778
                        trId := -1;
                        state := on_PedestrianGreen;
                        goto next_transition;
                    when 7 =>
                        -- set_timer(2000, timeout) (115,5)
                        tmp38 := 2000;
                        SET_timeout(tmp38'access);
                        -- NEXT_STATE on_StreetRed (117,10) at 704, 623
                        trId := -1;
                        state := on_StreetRed;
                        goto next_transition;
                    when 8 =>
                        -- set_timer(2000, timeout) (124,5)
                        tmp42 := 2000;
                        SET_timeout(tmp42'access);
                        -- NEXT_STATE on_StreetAttention (126,10) at 680, 468
                        trId := -1;
                        state := on_StreetAttention;
                        goto next_transition;
                    when 9 =>
                        -- NEXT_STATE on_PedWaiting (134,10) at 702, 313
                        trId := on_pedwaiting_START;
                        goto next_transition;
                    when 10 =>
                        -- entry (None,None)
                        on_pedwaiting_entry;
                        -- NEXT_STATE on_pedwaiting_waitOn (47,10) at 348, 180
                        trId := on_pedwaiting_waiton_START;
                        goto next_transition;
                    when 11 =>
                        -- DECISION counter (54,9)
                        -- ANSWER 14 (56,1)
                        if l_on_pedwaiting_counter = 14 then
                            -- RETURN counter_expired (None,None) at 178, 393
                            trId := 6;
                            goto next_transition;
                            -- ANSWER ELSE (None,None)
                        else
                            -- color := if counter mod 2 = 0 then red else all_off fi (62,5)
                            if ((l_on_pedwaiting_counter mod 2) = 0) then
                                tmp20 := asn1Sccred;
                            else
                                tmp20 := asn1Sccall_off;
                            end if;
                            l_on_pedwaiting_color := tmp20;
                            -- SetPedestrianColor(color) (64,7)
                            SetPedestrianColor(l_on_pedwaiting_color'access);
                            -- NEXT_STATE - (66,10) at 410, 493
                            case state is
                                when on_pedwaiting_waiton_wait_counter =>
                                    trId := on_pedwaiting_waiton_START;
                                when others =>
                                    trId := -1;
                            end case;
                            goto next_transition;
                        end if;
                    when 12 =>
                        -- NEXT_STATE on_pedwaiting_waiton_wait_counter (22,10) at 347, 106
                        trId := -1;
                        state := on_pedwaiting_waiton_wait_counter;
                        goto next_transition;
                    when 13 =>
                        -- NEXT_STATE maintenance_YellowOn (186,10) at 522, 251
                        trId := maintenance_yellowon_START;
                        goto next_transition;
                    when 14 =>
                        -- NEXT_STATE maintenance_YellowOn (193,10) at 518, 461
                        trId := maintenance_yellowon_START;
                        goto next_transition;
                    when 15 =>
                        -- NEXT_STATE maintenance_YellowOff (200,10) at 520, 356
                        trId := maintenance_yellowoff_START;
                        goto next_transition;
                    when 16 =>
                        -- entry (None,None)
                        maintenance_yellowoff_entry;
                        -- NEXT_STATE maintenance_yellowoff_idle (155,10) at 348, 487
                        trId := -1;
                        state := maintenance_yellowoff_idle;
                        goto next_transition;
                    when 17 =>
                        -- entry (None,None)
                        maintenance_yellowon_entry;
                        -- NEXT_STATE maintenance_yellowon_idle (177,10) at 489, 381
                        trId := -1;
                        state := maintenance_yellowon_idle;
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