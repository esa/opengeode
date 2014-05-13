-- This file was generated automatically: DO NOT MODIFY IT !

with TASTE_BasicTypes;
use TASTE_BasicTypes;
with TASTE_Dataview;
use TASTE_Dataview;

package trafficlight is
    --  Provided interface "pedestrianRequest"
    procedure pedestrianRequest(buttonpress: access asn1SccT_Boolean);
    pragma export(C, pedestrianRequest, "trafficlight_pedestrianRequest");
    --  Provided interface "onOff"
    procedure onOff(color: access asn1SccLight);
    pragma export(C, onOff, "trafficlight_onOff");
    --  Provided interface "timeout"
    procedure timeout;
    pragma export(C, timeout, "trafficlight_timeout");
    --  Required interface "SetTrafficLightColor"
    procedure SetTrafficLightColor(trafficlight_state: access asn1SccLight);
    pragma import(C, SetTrafficLightColor, "trafficlight_RI_SetTrafficLightColor");
    --  Required interface "SetPedestrianColor"
    procedure SetPedestrianColor(pedlight: access asn1SccLight);
    pragma import(C, SetPedestrianColor, "trafficlight_RI_SetPedestrianColor");
    --  Timer timeout SET and RESET functions
    procedure SET_timeout(val: access asn1SccT_UInt32);
    pragma import(C, SET_timeout, "trafficlight_RI_set_timeout");
    procedure RESET_timeout;
    pragma import(C, RESET_timeout, "trafficlight_RI_reset_timeout");
end trafficlight;