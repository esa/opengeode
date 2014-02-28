#!/usr/bin/env python
# ASN.1 Data model
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
asn1Files.append("./dataview-uniq.asn")
asn1Modules.append("TASTE-BasicTypes")
exportedTypes["TASTE-BasicTypes"] = ["T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["TASTE-BasicTypes"] = []
importedModules["TASTE-BasicTypes"] = []
types["T-Int32"] = type("T-Int32", (object,), {
    "Line": 6, "CharPositionInLine": 0, "type": type("T-Int32_type", (object,), {
        "Line": 6, "CharPositionInLine": 13, "kind": "IntegerType", "Min": "-2147483648", "Max": "2147483647"
    })
})

types["T-UInt32"] = type("T-UInt32", (object,), {
    "Line": 8, "CharPositionInLine": 0, "type": type("T-UInt32_type", (object,), {
        "Line": 8, "CharPositionInLine": 13, "kind": "IntegerType", "Min": "0", "Max": "4294967295"
    })
})

types["T-Int8"] = type("T-Int8", (object,), {
    "Line": 10, "CharPositionInLine": 0, "type": type("T-Int8_type", (object,), {
        "Line": 10, "CharPositionInLine": 11, "kind": "IntegerType", "Min": "-128", "Max": "127"
    })
})

types["T-UInt8"] = type("T-UInt8", (object,), {
    "Line": 12, "CharPositionInLine": 0, "type": type("T-UInt8_type", (object,), {
        "Line": 12, "CharPositionInLine": 12, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["T-Boolean"] = type("T-Boolean", (object,), {
    "Line": 14, "CharPositionInLine": 0, "type": type("T-Boolean_type", (object,), {
        "Line": 14, "CharPositionInLine": 14, "kind": "BooleanType"
    })
})

asn1Modules.append("VEGA")
exportedTypes["VEGA"] = ["T-GNC-LV-SIM-CONTEXT", "T-GNC-LV-SIM-INPUTS", "T-FLOAT32", "T-QUAT-COMPONENTS", "T-QUAT-FLOAT32", "T-AXIS-3-ID", "T-RANGE-3", "T-VECT3-FLOAT32", "T-SEQUENCE-ID", "T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT", "T-TVC-SET-POINT-ENG-VECT-IDX", "T-TVC-SET-POINT-ENG-VECT", "T-ACS-EQPT-ID", "T-RACS-EV-CMD-VECT", "T-INTR", "T-DOUBLE", "T-Plot", "T-Plot-subcycle", "T-Plot-major-cycle"]
exportedVariables["VEGA"] = ["size-T-QUAT-COMPONENTS", "axis-x-roll", "axis-y-yaw", "axis-z-pitch", "size-T-AXIS-3-ID", "size-T-SEQUENCE-ID", "size-T-TVC-SET-POINT-ENG-VECT-IDX", "size-T-ACS-EQPT-ID"]
importedModules["VEGA"] = []
types["T-GNC-LV-SIM-CONTEXT"] = type("T-GNC-LV-SIM-CONTEXT", (object,), {
    "Line": 23, "CharPositionInLine": 0, "type": type("T-GNC-LV-SIM-CONTEXT_type", (object,), {
        "Line": 23, "CharPositionInLine": 25, "kind": "SequenceType", "Children": {
            "attitude-quaternion": type("attitude-quaternion", (object,), {
                "Optional": "False", "Line": 24, "CharPositionInLine": 4, "type": type("attitude-quaternion_type", (object,), {
                    "Line": 24, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-QUAT-FLOAT32", "Min": "4", "Max": "4"
                })
            }),
            "ng-vel-incr-irs": type("ng-vel-incr-irs", (object,), {
                "Optional": "False", "Line": 25, "CharPositionInLine": 4, "type": type("ng-vel-incr-irs_type", (object,), {
                    "Line": 25, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            }),
            "ng-vel-incr-accelero": type("ng-vel-incr-accelero", (object,), {
                "Optional": "False", "Line": 26, "CharPositionInLine": 4, "type": type("ng-vel-incr-accelero_type", (object,), {
                    "Line": 26, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            }),
            "filtered-angles-sample-1": type("filtered-angles-sample-1", (object,), {
                "Optional": "False", "Line": 27, "CharPositionInLine": 4, "type": type("filtered-angles-sample-1_type", (object,), {
                    "Line": 27, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            }),
            "filtered-angles-sample-2": type("filtered-angles-sample-2", (object,), {
                "Optional": "False", "Line": 28, "CharPositionInLine": 4, "type": type("filtered-angles-sample-2_type", (object,), {
                    "Line": 28, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            })
        }
    })
})

types["T-GNC-LV-SIM-INPUTS"] = type("T-GNC-LV-SIM-INPUTS", (object,), {
    "Line": 32, "CharPositionInLine": 0, "type": type("T-GNC-LV-SIM-INPUTS_type", (object,), {
        "Line": 32, "CharPositionInLine": 24, "kind": "SequenceType", "Children": {
            "sequ-exec-request-vect": type("sequ-exec-request-vect", (object,), {
                "Optional": "False", "Line": 33, "CharPositionInLine": 4, "type": type("sequ-exec-request-vect_type", (object,), {
                    "Line": 33, "CharPositionInLine": 29, "kind": "ReferenceType", "ReferencedTypeName": "T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT", "Min": "20", "Max": "20"
                })
            }),
            "tvc-set-point-eng-vect": type("tvc-set-point-eng-vect", (object,), {
                "Optional": "False", "Line": 34, "CharPositionInLine": 4, "type": type("tvc-set-point-eng-vect_type", (object,), {
                    "Line": 34, "CharPositionInLine": 28, "kind": "ReferenceType", "ReferencedTypeName": "T-TVC-SET-POINT-ENG-VECT", "Min": "8", "Max": "8"
                })
            }),
            "racs-ev-cmd-vect": type("racs-ev-cmd-vect", (object,), {
                "Optional": "False", "Line": 35, "CharPositionInLine": 4, "type": type("racs-ev-cmd-vect_type", (object,), {
                    "Line": 35, "CharPositionInLine": 28, "kind": "ReferenceType", "ReferencedTypeName": "T-RACS-EV-CMD-VECT", "Min": "6", "Max": "6"
                })
            })
        }
    })
})

types["T-FLOAT32"] = type("T-FLOAT32", (object,), {
    "Line": 40, "CharPositionInLine": 0, "type": type("T-FLOAT32_type", (object,), {
        "Line": 40, "CharPositionInLine": 14, "kind": "ReferenceType", "ReferencedTypeName": "T-DOUBLE", "Min": "-1E+308", "Max": "1E+308"
    })
})

types["T-QUAT-COMPONENTS"] = type("T-QUAT-COMPONENTS", (object,), {
    "Line": 43, "CharPositionInLine": 0, "type": type("T-QUAT-COMPONENTS_type", (object,), {
        "Line": 43, "CharPositionInLine": 22, "kind": "IntegerType", "Min": "0", "Max": "3"
    })
})

types["T-QUAT-FLOAT32"] = type("T-QUAT-FLOAT32", (object,), {
    "Line": 46, "CharPositionInLine": 0, "type": type("T-QUAT-FLOAT32_type", (object,), {
        "Line": 46, "CharPositionInLine": 19, "kind": "SequenceOfType", "Min": "4", "Max": "4", "type": type("SeqOf_type", (object,), {
            "Line": 46, "CharPositionInLine": 62, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-AXIS-3-ID"] = type("T-AXIS-3-ID", (object,), {
    "Line": 51, "CharPositionInLine": 0, "type": type("T-AXIS-3-ID_type", (object,), {
        "Line": 51, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "T-RANGE-3", "Min": "0", "Max": "2"
    })
})

types["T-RANGE-3"] = type("T-RANGE-3", (object,), {
    "Line": 55, "CharPositionInLine": 0, "type": type("T-RANGE-3_type", (object,), {
        "Line": 55, "CharPositionInLine": 14, "kind": "IntegerType", "Min": "0", "Max": "2"
    })
})

types["T-VECT3-FLOAT32"] = type("T-VECT3-FLOAT32", (object,), {
    "Line": 57, "CharPositionInLine": 0, "type": type("T-VECT3-FLOAT32_type", (object,), {
        "Line": 57, "CharPositionInLine": 20, "kind": "SequenceOfType", "Min": "3", "Max": "3", "type": type("SeqOf_type", (object,), {
            "Line": 57, "CharPositionInLine": 57, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-SEQUENCE-ID"] = type("T-SEQUENCE-ID", (object,), {
    "Line": 60, "CharPositionInLine": 0, "type": type("T-SEQUENCE-ID_type", (object,), {
        "Line": 60, "CharPositionInLine": 18, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "sequence-id-none": type("sequence_id_none", (object,), {
                "IntValue": 0, "Line": 61, "CharPositionInLine": 6, "EnumID": "sequence_id_none"
            }),
            "command-irs-in-flight-mode": type("command_irs_in_flight_mode", (object,), {
                "IntValue": 1, "Line": 62, "CharPositionInLine": 6, "EnumID": "command_irs_in_flight_mode"
            }),
            "select-uctm-telemetry-format-2": type("select_uctm_telemetry_format_2", (object,), {
                "IntValue": 2, "Line": 63, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_2"
            }),
            "inhibit-bus-repeater-egse-line": type("inhibit_bus_repeater_egse_line", (object,), {
                "IntValue": 3, "Line": 64, "CharPositionInLine": 6, "EnumID": "inhibit_bus_repeater_egse_line"
            }),
            "ignite-p80-motor": type("ignite_p80_motor", (object,), {
                "IntValue": 4, "Line": 65, "CharPositionInLine": 6, "EnumID": "ignite_p80_motor"
            }),
            "select-uctm-telemetry-format-3": type("select_uctm_telemetry_format_3", (object,), {
                "IntValue": 5, "Line": 66, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_3"
            }),
            "select-uctm-telemetry-format-4": type("select_uctm_telemetry_format_4", (object,), {
                "IntValue": 6, "Line": 67, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_4"
            }),
            "open-mea-valves": type("open_mea_valves", (object,), {
                "IntValue": 7, "Line": 68, "CharPositionInLine": 6, "EnumID": "open_mea_valves"
            }),
            "close-mea-valves": type("close_mea_valves", (object,), {
                "IntValue": 8, "Line": 69, "CharPositionInLine": 6, "EnumID": "close_mea_valves"
            }),
            "select-uctm-telemetry-format-5": type("select_uctm_telemetry_format_5", (object,), {
                "IntValue": 9, "Line": 70, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_5"
            }),
            "open-sas-dry-loops": type("open_sas_dry_loops", (object,), {
                "IntValue": 10, "Line": 71, "CharPositionInLine": 6, "EnumID": "open_sas_dry_loops"
            }),
            "select-uctm-telemetry-format-6": type("select_uctm_telemetry_format_6", (object,), {
                "IntValue": 11, "Line": 72, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_6"
            }),
            "select-uctm-telemetry-format-7": type("select_uctm_telemetry_format_7", (object,), {
                "IntValue": 12, "Line": 73, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_7"
            }),
            "passivate-lps-1-2": type("passivate_lps_1_2", (object,), {
                "IntValue": 13, "Line": 74, "CharPositionInLine": 6, "EnumID": "passivate_lps_1_2"
            }),
            "pressurize-lps-1-2": type("pressurize_lps_1_2", (object,), {
                "IntValue": 14, "Line": 75, "CharPositionInLine": 6, "EnumID": "pressurize_lps_1_2"
            }),
            "pressurize-lps-4-6": type("pressurize_lps_4_6", (object,), {
                "IntValue": 15, "Line": 76, "CharPositionInLine": 6, "EnumID": "pressurize_lps_4_6"
            }),
            "pressurize-lps-3-5": type("pressurize_lps_3_5", (object,), {
                "IntValue": 16, "Line": 77, "CharPositionInLine": 6, "EnumID": "pressurize_lps_3_5"
            }),
            "pressurize-lps-hppy": type("pressurize_lps_hppy", (object,), {
                "IntValue": 17, "Line": 78, "CharPositionInLine": 6, "EnumID": "pressurize_lps_hppy"
            }),
            "passivate-lps-3": type("passivate_lps_3", (object,), {
                "IntValue": 18, "Line": 79, "CharPositionInLine": 6, "EnumID": "passivate_lps_3"
            }),
            "passivate-lps-4": type("passivate_lps_4", (object,), {
                "IntValue": 19, "Line": 80, "CharPositionInLine": 6, "EnumID": "passivate_lps_4"
            }),
            "passivate-racs": type("passivate_racs", (object,), {
                "IntValue": 20, "Line": 81, "CharPositionInLine": 6, "EnumID": "passivate_racs"
            }),
            "initiate-racs-system-priming": type("initiate_racs_system_priming", (object,), {
                "IntValue": 21, "Line": 82, "CharPositionInLine": 6, "EnumID": "initiate_racs_system_priming"
            }),
            "set-racs-to-full-operational-mode": type("set_racs_to_full_operational_mode", (object,), {
                "IntValue": 22, "Line": 83, "CharPositionInLine": 6, "EnumID": "set_racs_to_full_operational_mode"
            }),
            "open-lps-evacuation-valves": type("open_lps_evacuation_valves", (object,), {
                "IntValue": 23, "Line": 84, "CharPositionInLine": 6, "EnumID": "open_lps_evacuation_valves"
            }),
            "close-lps-evacuation-valves": type("close_lps_evacuation_valves", (object,), {
                "IntValue": 24, "Line": 85, "CharPositionInLine": 6, "EnumID": "close_lps_evacuation_valves"
            }),
            "separate-multipayload-adapter": type("separate_multipayload_adapter", (object,), {
                "IntValue": 25, "Line": 86, "CharPositionInLine": 6, "EnumID": "separate_multipayload_adapter"
            }),
            "select-uctm-telemetry-format-8": type("select_uctm_telemetry_format_8", (object,), {
                "IntValue": 26, "Line": 87, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_8"
            }),
            "select-uctm-telemetry-format-9": type("select_uctm_telemetry_format_9", (object,), {
                "IntValue": 27, "Line": 88, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_9"
            }),
            "select-uctm-telemetry-format-10": type("select_uctm_telemetry_format_10", (object,), {
                "IntValue": 28, "Line": 89, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_10"
            }),
            "select-uctm-telemetry-format-11": type("select_uctm_telemetry_format_11", (object,), {
                "IntValue": 29, "Line": 90, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_11"
            }),
            "select-uctm-telemetry-format-12": type("select_uctm_telemetry_format_12", (object,), {
                "IntValue": 30, "Line": 91, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_12"
            }),
            "select-uctm-telemetry-format-13": type("select_uctm_telemetry_format_13", (object,), {
                "IntValue": 31, "Line": 92, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_13"
            }),
            "select-uctm-telemetry-format-14": type("select_uctm_telemetry_format_14", (object,), {
                "IntValue": 32, "Line": 93, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_14"
            }),
            "select-uctm-telemetry-format-15": type("select_uctm_telemetry_format_15", (object,), {
                "IntValue": 33, "Line": 94, "CharPositionInLine": 6, "EnumID": "select_uctm_telemetry_format_15"
            }),
            "separate-func-mc": type("separate_func_mc", (object,), {
                "IntValue": 34, "Line": 95, "CharPositionInLine": 6, "EnumID": "separate_func_mc"
            }),
            "separate-func-1": type("separate_func_1", (object,), {
                "IntValue": 35, "Line": 96, "CharPositionInLine": 6, "EnumID": "separate_func_1"
            }),
            "separate-func-2": type("separate_func_2", (object,), {
                "IntValue": 36, "Line": 97, "CharPositionInLine": 6, "EnumID": "separate_func_2"
            }),
            "separate-func-3": type("separate_func_3", (object,), {
                "IntValue": 37, "Line": 98, "CharPositionInLine": 6, "EnumID": "separate_func_3"
            }),
            "inhibit-bus-repeater-pl-line": type("inhibit_bus_repeater_pl_line", (object,), {
                "IntValue": 38, "Line": 99, "CharPositionInLine": 6, "EnumID": "inhibit_bus_repeater_pl_line"
            }),
            "activate-electrical-order-1": type("activate_electrical_order_1", (object,), {
                "IntValue": 39, "Line": 100, "CharPositionInLine": 6, "EnumID": "activate_electrical_order_1"
            }),
            "activate-electrical-order-2": type("activate_electrical_order_2", (object,), {
                "IntValue": 40, "Line": 101, "CharPositionInLine": 6, "EnumID": "activate_electrical_order_2"
            }),
            "activate-electrical-order-3": type("activate_electrical_order_3", (object,), {
                "IntValue": 41, "Line": 102, "CharPositionInLine": 6, "EnumID": "activate_electrical_order_3"
            }),
            "activate-electrical-order-4": type("activate_electrical_order_4", (object,), {
                "IntValue": 42, "Line": 103, "CharPositionInLine": 6, "EnumID": "activate_electrical_order_4"
            }),
            "activate-electrical-order-5": type("activate_electrical_order_5", (object,), {
                "IntValue": 43, "Line": 104, "CharPositionInLine": 6, "EnumID": "activate_electrical_order_5"
            }),
            "deactivate-electrical-order-1": type("deactivate_electrical_order_1", (object,), {
                "IntValue": 44, "Line": 105, "CharPositionInLine": 6, "EnumID": "deactivate_electrical_order_1"
            }),
            "deactivate-electrical-order-2": type("deactivate_electrical_order_2", (object,), {
                "IntValue": 45, "Line": 106, "CharPositionInLine": 6, "EnumID": "deactivate_electrical_order_2"
            }),
            "deactivate-electrical-order-3": type("deactivate_electrical_order_3", (object,), {
                "IntValue": 46, "Line": 107, "CharPositionInLine": 6, "EnumID": "deactivate_electrical_order_3"
            }),
            "deactivate-electrical-order-4": type("deactivate_electrical_order_4", (object,), {
                "IntValue": 47, "Line": 108, "CharPositionInLine": 6, "EnumID": "deactivate_electrical_order_4"
            }),
            "deactivate-electrical-order-5": type("deactivate_electrical_order_5", (object,), {
                "IntValue": 48, "Line": 109, "CharPositionInLine": 6, "EnumID": "deactivate_electrical_order_5"
            }),
            "close-pl-dry-loop-1": type("close_pl_dry_loop_1", (object,), {
                "IntValue": 49, "Line": 110, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_1"
            }),
            "close-pl-dry-loop-2": type("close_pl_dry_loop_2", (object,), {
                "IntValue": 50, "Line": 111, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_2"
            }),
            "close-pl-dry-loop-3": type("close_pl_dry_loop_3", (object,), {
                "IntValue": 51, "Line": 112, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_3"
            }),
            "close-pl-dry-loop-4": type("close_pl_dry_loop_4", (object,), {
                "IntValue": 52, "Line": 113, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_4"
            }),
            "close-pl-dry-loop-5": type("close_pl_dry_loop_5", (object,), {
                "IntValue": 53, "Line": 114, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_5"
            }),
            "close-pl-dry-loop-6": type("close_pl_dry_loop_6", (object,), {
                "IntValue": 54, "Line": 115, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_6"
            }),
            "close-pl-dry-loop-7": type("close_pl_dry_loop_7", (object,), {
                "IntValue": 55, "Line": 116, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_7"
            }),
            "close-pl-dry-loop-8": type("close_pl_dry_loop_8", (object,), {
                "IntValue": 56, "Line": 117, "CharPositionInLine": 6, "EnumID": "close_pl_dry_loop_8"
            }),
            "open-pl-dry-loop-1": type("open_pl_dry_loop_1", (object,), {
                "IntValue": 57, "Line": 118, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_1"
            }),
            "open-pl-dry-loop-2": type("open_pl_dry_loop_2", (object,), {
                "IntValue": 58, "Line": 119, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_2"
            }),
            "open-pl-dry-loop-3": type("open_pl_dry_loop_3", (object,), {
                "IntValue": 59, "Line": 120, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_3"
            }),
            "open-pl-dry-loop-4": type("open_pl_dry_loop_4", (object,), {
                "IntValue": 60, "Line": 121, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_4"
            }),
            "open-pl-dry-loop-5": type("open_pl_dry_loop_5", (object,), {
                "IntValue": 61, "Line": 122, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_5"
            }),
            "open-pl-dry-loop-6": type("open_pl_dry_loop_6", (object,), {
                "IntValue": 62, "Line": 123, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_6"
            }),
            "open-pl-dry-loop-7": type("open_pl_dry_loop_7", (object,), {
                "IntValue": 63, "Line": 124, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_7"
            }),
            "open-pl-dry-loop-8": type("open_pl_dry_loop_8", (object,), {
                "IntValue": 64, "Line": 125, "CharPositionInLine": 6, "EnumID": "open_pl_dry_loop_8"
            }),
            "reactivate-payload-supply-breaker": type("reactivate_payload_supply_breaker", (object,), {
                "IntValue": 65, "Line": 126, "CharPositionInLine": 6, "EnumID": "reactivate_payload_supply_breaker"
            }),
            "rearm-eo-breaker": type("rearm_eo_breaker", (object,), {
                "IntValue": 66, "Line": 127, "CharPositionInLine": 6, "EnumID": "rearm_eo_breaker"
            }),
            "close-spare-dry-loop-14": type("close_spare_dry_loop_14", (object,), {
                "IntValue": 67, "Line": 128, "CharPositionInLine": 6, "EnumID": "close_spare_dry_loop_14"
            }),
            "close-spare-dry-loop-15": type("close_spare_dry_loop_15", (object,), {
                "IntValue": 68, "Line": 129, "CharPositionInLine": 6, "EnumID": "close_spare_dry_loop_15"
            }),
            "close-spare-dry-loop-16": type("close_spare_dry_loop_16", (object,), {
                "IntValue": 69, "Line": 130, "CharPositionInLine": 6, "EnumID": "close_spare_dry_loop_16"
            }),
            "open-spare-dry-loop-14": type("open_spare_dry_loop_14", (object,), {
                "IntValue": 70, "Line": 131, "CharPositionInLine": 6, "EnumID": "open_spare_dry_loop_14"
            }),
            "open-spare-dry-loop-15": type("open_spare_dry_loop_15", (object,), {
                "IntValue": 71, "Line": 132, "CharPositionInLine": 6, "EnumID": "open_spare_dry_loop_15"
            }),
            "open-spare-dry-loop-16": type("open_spare_dry_loop_16", (object,), {
                "IntValue": 72, "Line": 133, "CharPositionInLine": 6, "EnumID": "open_spare_dry_loop_16"
            }),
            "open-spare-dry-loop-17": type("open_spare_dry_loop_17", (object,), {
                "IntValue": 73, "Line": 134, "CharPositionInLine": 6, "EnumID": "open_spare_dry_loop_17"
            }),
            "close-spare-dry-loop-17": type("close_spare_dry_loop_17", (object,), {
                "IntValue": 74, "Line": 135, "CharPositionInLine": 6, "EnumID": "close_spare_dry_loop_17"
            }),
            "open-spare-dry-loop-18": type("open_spare_dry_loop_18", (object,), {
                "IntValue": 75, "Line": 136, "CharPositionInLine": 6, "EnumID": "open_spare_dry_loop_18"
            }),
            "close-spare-dry-loop-18": type("close_spare_dry_loop_18", (object,), {
                "IntValue": 76, "Line": 137, "CharPositionInLine": 6, "EnumID": "close_spare_dry_loop_18"
            }),
            "p80-separation": type("p80_separation", (object,), {
                "IntValue": 77, "Line": 138, "CharPositionInLine": 6, "EnumID": "p80_separation"
            }),
            "z23-ignition": type("z23_ignition", (object,), {
                "IntValue": 78, "Line": 139, "CharPositionInLine": 6, "EnumID": "z23_ignition"
            }),
            "z23-separation": type("z23_separation", (object,), {
                "IntValue": 79, "Line": 140, "CharPositionInLine": 6, "EnumID": "z23_separation"
            }),
            "z9-ignition": type("z9_ignition", (object,), {
                "IntValue": 80, "Line": 141, "CharPositionInLine": 6, "EnumID": "z9_ignition"
            }),
            "z9-separation": type("z9_separation", (object,), {
                "IntValue": 81, "Line": 142, "CharPositionInLine": 6, "EnumID": "z9_separation"
            }),
            "fairing-separation": type("fairing_separation", (object,), {
                "IntValue": 82, "Line": 143, "CharPositionInLine": 6, "EnumID": "fairing_separation"
            }),
            "sequence-unused-83": type("sequence_unused_83", (object,), {
                "IntValue": 83, "Line": 144, "CharPositionInLine": 6, "EnumID": "sequence_unused_83"
            }),
            "sequence-unused-84": type("sequence_unused_84", (object,), {
                "IntValue": 84, "Line": 145, "CharPositionInLine": 6, "EnumID": "sequence_unused_84"
            }),
            "sequence-unused-85": type("sequence_unused_85", (object,), {
                "IntValue": 85, "Line": 146, "CharPositionInLine": 6, "EnumID": "sequence_unused_85"
            }),
            "sequence-unused-86": type("sequence_unused_86", (object,), {
                "IntValue": 86, "Line": 147, "CharPositionInLine": 6, "EnumID": "sequence_unused_86"
            }),
            "sequence-unused-87": type("sequence_unused_87", (object,), {
                "IntValue": 87, "Line": 148, "CharPositionInLine": 6, "EnumID": "sequence_unused_87"
            }),
            "sequence-unused-88": type("sequence_unused_88", (object,), {
                "IntValue": 88, "Line": 149, "CharPositionInLine": 6, "EnumID": "sequence_unused_88"
            }),
            "sequence-unused-89": type("sequence_unused_89", (object,), {
                "IntValue": 89, "Line": 150, "CharPositionInLine": 6, "EnumID": "sequence_unused_89"
            }),
            "sequence-unused-90": type("sequence_unused_90", (object,), {
                "IntValue": 90, "Line": 151, "CharPositionInLine": 6, "EnumID": "sequence_unused_90"
            }),
            "sequence-unused-91": type("sequence_unused_91", (object,), {
                "IntValue": 91, "Line": 152, "CharPositionInLine": 6, "EnumID": "sequence_unused_91"
            }),
            "sequence-unused-92": type("sequence_unused_92", (object,), {
                "IntValue": 92, "Line": 153, "CharPositionInLine": 6, "EnumID": "sequence_unused_92"
            }),
            "sequence-unused-93": type("sequence_unused_93", (object,), {
                "IntValue": 93, "Line": 154, "CharPositionInLine": 6, "EnumID": "sequence_unused_93"
            }),
            "sequence-unused-94": type("sequence_unused_94", (object,), {
                "IntValue": 94, "Line": 155, "CharPositionInLine": 6, "EnumID": "sequence_unused_94"
            }),
            "sequence-unused-95": type("sequence_unused_95", (object,), {
                "IntValue": 95, "Line": 156, "CharPositionInLine": 6, "EnumID": "sequence_unused_95"
            }),
            "sequence-unused-96": type("sequence_unused_96", (object,), {
                "IntValue": 96, "Line": 157, "CharPositionInLine": 6, "EnumID": "sequence_unused_96"
            }),
            "sequence-unused-97": type("sequence_unused_97", (object,), {
                "IntValue": 97, "Line": 158, "CharPositionInLine": 6, "EnumID": "sequence_unused_97"
            }),
            "sequence-unused-98": type("sequence_unused_98", (object,), {
                "IntValue": 98, "Line": 159, "CharPositionInLine": 6, "EnumID": "sequence_unused_98"
            }),
            "sequence-unused-99": type("sequence_unused_99", (object,), {
                "IntValue": 99, "Line": 160, "CharPositionInLine": 6, "EnumID": "sequence_unused_99"
            }),
            "sequence-unused-100": type("sequence_unused_100", (object,), {
                "IntValue": 100, "Line": 161, "CharPositionInLine": 6, "EnumID": "sequence_unused_100"
            })
        }
    })
})

types["T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT"] = type("T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT", (object,), {
    "Line": 167, "CharPositionInLine": 0, "type": type("T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT_type", (object,), {
        "Line": 167, "CharPositionInLine": 44, "kind": "SequenceOfType", "Min": "20", "Max": "20", "type": type("SeqOf_type", (object,), {
            "Line": 167, "CharPositionInLine": 83, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-TVC-SET-POINT-ENG-VECT-IDX"] = type("T-TVC-SET-POINT-ENG-VECT-IDX", (object,), {
    "Line": 170, "CharPositionInLine": 0, "type": type("T-TVC-SET-POINT-ENG-VECT-IDX_type", (object,), {
        "Line": 170, "CharPositionInLine": 33, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "p80-x": type("p80_x", (object,), {
                "IntValue": 0, "Line": 171, "CharPositionInLine": 4, "EnumID": "p80_x"
            }),
            "p80-y": type("p80_y", (object,), {
                "IntValue": 1, "Line": 172, "CharPositionInLine": 4, "EnumID": "p80_y"
            }),
            "z23-x": type("z23_x", (object,), {
                "IntValue": 2, "Line": 173, "CharPositionInLine": 4, "EnumID": "z23_x"
            }),
            "z23-y": type("z23_y", (object,), {
                "IntValue": 3, "Line": 174, "CharPositionInLine": 4, "EnumID": "z23_y"
            }),
            "z09-x": type("z09_x", (object,), {
                "IntValue": 4, "Line": 175, "CharPositionInLine": 4, "EnumID": "z09_x"
            }),
            "z09-y": type("z09_y", (object,), {
                "IntValue": 5, "Line": 176, "CharPositionInLine": 4, "EnumID": "z09_y"
            }),
            "avum-x": type("avum_x", (object,), {
                "IntValue": 6, "Line": 177, "CharPositionInLine": 4, "EnumID": "avum_x"
            }),
            "avum-y": type("avum_y", (object,), {
                "IntValue": 7, "Line": 178, "CharPositionInLine": 4, "EnumID": "avum_y"
            })
        }
    })
})

types["T-TVC-SET-POINT-ENG-VECT"] = type("T-TVC-SET-POINT-ENG-VECT", (object,), {
    "Line": 181, "CharPositionInLine": 0, "type": type("T-TVC-SET-POINT-ENG-VECT_type", (object,), {
        "Line": 181, "CharPositionInLine": 29, "kind": "SequenceOfType", "Min": "8", "Max": "8", "type": type("SeqOf_type", (object,), {
            "Line": 181, "CharPositionInLine": 83, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-ACS-EQPT-ID"] = type("T-ACS-EQPT-ID", (object,), {
    "Line": 184, "CharPositionInLine": 0, "type": type("T-ACS-EQPT-ID_type", (object,), {
        "Line": 184, "CharPositionInLine": 18, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "acs-eqpt-1": type("acs_eqpt_1", (object,), {
                "IntValue": 0, "Line": 185, "CharPositionInLine": 4, "EnumID": "acs_eqpt_1"
            }),
            "acs-eqpt-2": type("acs_eqpt_2", (object,), {
                "IntValue": 1, "Line": 186, "CharPositionInLine": 4, "EnumID": "acs_eqpt_2"
            }),
            "acs-eqpt-3": type("acs_eqpt_3", (object,), {
                "IntValue": 2, "Line": 187, "CharPositionInLine": 4, "EnumID": "acs_eqpt_3"
            }),
            "acs-eqpt-4": type("acs_eqpt_4", (object,), {
                "IntValue": 3, "Line": 188, "CharPositionInLine": 4, "EnumID": "acs_eqpt_4"
            }),
            "acs-eqpt-5": type("acs_eqpt_5", (object,), {
                "IntValue": 4, "Line": 189, "CharPositionInLine": 4, "EnumID": "acs_eqpt_5"
            }),
            "acs-eqpt-6": type("acs_eqpt_6", (object,), {
                "IntValue": 5, "Line": 190, "CharPositionInLine": 4, "EnumID": "acs_eqpt_6"
            })
        }
    })
})

types["T-RACS-EV-CMD-VECT"] = type("T-RACS-EV-CMD-VECT", (object,), {
    "Line": 193, "CharPositionInLine": 0, "type": type("T-RACS-EV-CMD-VECT_type", (object,), {
        "Line": 193, "CharPositionInLine": 23, "kind": "SequenceOfType", "Min": "6", "Max": "6", "type": type("SeqOf_type", (object,), {
            "Line": 193, "CharPositionInLine": 62, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-INTR"] = type("T-INTR", (object,), {
    "Line": 226, "CharPositionInLine": 0, "type": type("T-INTR_type", (object,), {
        "Line": 226, "CharPositionInLine": 11, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "hwe": type("hwe", (object,), {
                "IntValue": 0, "Line": 227, "CharPositionInLine": 4, "EnumID": "hwe"
            }),
            "asg-al3": type("asg_al3", (object,), {
                "IntValue": 1, "Line": 228, "CharPositionInLine": 4, "EnumID": "asg_al3"
            }),
            "asg-al1": type("asg_al1", (object,), {
                "IntValue": 2, "Line": 229, "CharPositionInLine": 4, "EnumID": "asg_al1"
            }),
            "ic-obtpulse4": type("ic_obtpulse4", (object,), {
                "IntValue": 3, "Line": 230, "CharPositionInLine": 4, "EnumID": "ic_obtpulse4"
            }),
            "ic-rtc": type("ic_rtc", (object,), {
                "IntValue": 4, "Line": 231, "CharPositionInLine": 4, "EnumID": "ic_rtc"
            }),
            "ic-utca": type("ic_utca", (object,), {
                "IntValue": 5, "Line": 232, "CharPositionInLine": 4, "EnumID": "ic_utca"
            }),
            "m5-recerr": type("m5_recerr", (object,), {
                "IntValue": 6, "Line": 233, "CharPositionInLine": 4, "EnumID": "m5_recerr"
            }),
            "m5-lberr": type("m5_lberr", (object,), {
                "IntValue": 7, "Line": 234, "CharPositionInLine": 4, "EnumID": "m5_lberr"
            }),
            "m5-dnc": type("m5_dnc", (object,), {
                "IntValue": 8, "Line": 235, "CharPositionInLine": 4, "EnumID": "m5_dnc"
            }),
            "m5-slend": type("m5_slend", (object,), {
                "IntValue": 9, "Line": 236, "CharPositionInLine": 4, "EnumID": "m5_slend"
            }),
            "m5-slimed": type("m5_slimed", (object,), {
                "IntValue": 10, "Line": 237, "CharPositionInLine": 4, "EnumID": "m5_slimed"
            }),
            "m5-slloop": type("m5_slloop", (object,), {
                "IntValue": 11, "Line": 238, "CharPositionInLine": 4, "EnumID": "m5_slloop"
            }),
            "m5-slchok": type("m5_slchok", (object,), {
                "IntValue": 12, "Line": 239, "CharPositionInLine": 4, "EnumID": "m5_slchok"
            }),
            "m5-rtrec": type("m5_rtrec", (object,), {
                "IntValue": 13, "Line": 240, "CharPositionInLine": 4, "EnumID": "m5_rtrec"
            }),
            "m5-rttrn": type("m5_rttrn", (object,), {
                "IntValue": 14, "Line": 241, "CharPositionInLine": 4, "EnumID": "m5_rttrn"
            }),
            "m5-rtbct": type("m5_rtbct", (object,), {
                "IntValue": 15, "Line": 242, "CharPositionInLine": 4, "EnumID": "m5_rtbct"
            }),
            "m5-rtmode": type("m5_rtmode", (object,), {
                "IntValue": 16, "Line": 243, "CharPositionInLine": 4, "EnumID": "m5_rtmode"
            }),
            "m5-rtsync": type("m5_rtsync", (object,), {
                "IntValue": 17, "Line": 244, "CharPositionInLine": 4, "EnumID": "m5_rtsync"
            }),
            "m5-rtrst": type("m5_rtrst", (object,), {
                "IntValue": 18, "Line": 245, "CharPositionInLine": 4, "EnumID": "m5_rtrst"
            }),
            "obt-1hz": type("obt_1hz", (object,), {
                "IntValue": 19, "Line": 246, "CharPositionInLine": 4, "EnumID": "obt_1hz"
            }),
            "obt-syncsw": type("obt_syncsw", (object,), {
                "IntValue": 20, "Line": 247, "CharPositionInLine": 4, "EnumID": "obt_syncsw"
            }),
            "obt-sample1": type("obt_sample1", (object,), {
                "IntValue": 21, "Line": 248, "CharPositionInLine": 4, "EnumID": "obt_sample1"
            }),
            "pim-et": type("pim_et", (object,), {
                "IntValue": 22, "Line": 249, "CharPositionInLine": 4, "EnumID": "pim_et"
            }),
            "wd-wde": type("wd_wde", (object,), {
                "IntValue": 23, "Line": 250, "CharPositionInLine": 4, "EnumID": "wd_wde"
            }),
            "obt-pulse1": type("obt_pulse1", (object,), {
                "IntValue": 24, "Line": 251, "CharPositionInLine": 4, "EnumID": "obt_pulse1"
            }),
            "uart-a": type("uart_a", (object,), {
                "IntValue": 25, "Line": 252, "CharPositionInLine": 4, "EnumID": "uart_a"
            }),
            "uart-b": type("uart_b", (object,), {
                "IntValue": 26, "Line": 253, "CharPositionInLine": 4, "EnumID": "uart_b"
            }),
            "memerr": type("memerr", (object,), {
                "IntValue": 27, "Line": 254, "CharPositionInLine": 4, "EnumID": "memerr"
            }),
            "uart-err": type("uart_err", (object,), {
                "IntValue": 28, "Line": 255, "CharPositionInLine": 4, "EnumID": "uart_err"
            }),
            "dma-err": type("dma_err", (object,), {
                "IntValue": 29, "Line": 256, "CharPositionInLine": 4, "EnumID": "dma_err"
            }),
            "dma-tmo": type("dma_tmo", (object,), {
                "IntValue": 30, "Line": 257, "CharPositionInLine": 4, "EnumID": "dma_tmo"
            }),
            "obt-pulse2": type("obt_pulse2", (object,), {
                "IntValue": 31, "Line": 258, "CharPositionInLine": 4, "EnumID": "obt_pulse2"
            }),
            "obt-pulse3": type("obt_pulse3", (object,), {
                "IntValue": 32, "Line": 259, "CharPositionInLine": 4, "EnumID": "obt_pulse3"
            }),
            "gpt": type("gpt", (object,), {
                "IntValue": 33, "Line": 260, "CharPositionInLine": 4, "EnumID": "gpt"
            }),
            "rtc": type("rtc", (object,), {
                "IntValue": 34, "Line": 261, "CharPositionInLine": 4, "EnumID": "rtc"
            }),
            "obt-pulse4": type("obt_pulse4", (object,), {
                "IntValue": 35, "Line": 262, "CharPositionInLine": 4, "EnumID": "obt_pulse4"
            }),
            "wdtmo": type("wdtmo", (object,), {
                "IntValue": 36, "Line": 263, "CharPositionInLine": 4, "EnumID": "wdtmo"
            })
        }
    })
})

types["T-DOUBLE"] = type("T-DOUBLE", (object,), {
    "Line": 611, "CharPositionInLine": 0, "type": type("T-DOUBLE_type", (object,), {
        "Line": 611, "CharPositionInLine": 13, "kind": "RealType", "Min": "-1E+308", "Max": "1E+308"
    })
})

types["T-Plot"] = type("T-Plot", (object,), {
    "Line": 614, "CharPositionInLine": 0, "type": type("T-Plot_type", (object,), {
        "Line": 614, "CharPositionInLine": 11, "kind": "SequenceType", "Children": {
            "major-cycle": type("major-cycle", (object,), {
                "Optional": "False", "Line": 615, "CharPositionInLine": 4, "type": type("major-cycle_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "T-Plot-major-cycle", "Min": "0", "Max": "9999999999"
                })
            }),
            "subcycle": type("subcycle", (object,), {
                "Optional": "False", "Line": 616, "CharPositionInLine": 4, "type": type("subcycle_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "T-Plot-subcycle", "Min": "0", "Max": "7"
                })
            }),
            "gnc-inputs": type("gnc-inputs", (object,), {
                "Optional": "False", "Line": 617, "CharPositionInLine": 4, "type": type("gnc-inputs_type", (object,), {
                    "Line": 617, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "T-GNC-LV-SIM-CONTEXT"
                })
            }),
            "gnc-outputs": type("gnc-outputs", (object,), {
                "Optional": "False", "Line": 618, "CharPositionInLine": 4, "type": type("gnc-outputs_type", (object,), {
                    "Line": 618, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "T-GNC-LV-SIM-INPUTS"
                })
            })
        }
    })
})

types["T-Plot-subcycle"] = type("T-Plot-subcycle", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("T-Plot-subcycle_type", (object,), {
        "Line": 616, "CharPositionInLine": 13, "kind": "IntegerType", "Min": "0", "Max": "7"
    })
})

types["T-Plot-major-cycle"] = type("T-Plot-major-cycle", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("T-Plot-major-cycle_type", (object,), {
        "Line": 615, "CharPositionInLine": 16, "kind": "IntegerType", "Min": "0", "Max": "9999999999"
    })
})

asn1Modules.append("TASTE-MONITORING")
exportedTypes["TASTE-MONITORING"] = ["TASTE-Peek", "TASTE-Peek-list", "TASTE-Peek-id", "TASTE-Peek-id-list", "TASTE-Monitoring-value", "TASTE-Monitoring", "TASTE-Monitoring-list", "TASTE-Poke-list", "TASTE-Peek-limit", "TASTE-Monitoring-values", "TASTE-Monitoring-value-octet-string", "TASTE-Monitoring-value-real-double", "TASTE-Monitoring-value-real-single", "TASTE-Monitoring-value-int-64", "TASTE-Monitoring-value-int-32", "TASTE-Peek-sample-time", "TASTE-Peek-nb-of-elements", "TASTE-Peek-base-type", "TASTE-Peek-offset", "TASTE-Peek-base-address"]
exportedVariables["TASTE-MONITORING"] = ["empty-peek-list", "empty-poke-list"]
importedModules["TASTE-MONITORING"] = []
types["TASTE-Peek"] = type("TASTE-Peek", (object,), {
    "Line": 638, "CharPositionInLine": 0, "type": type("TASTE-Peek_type", (object,), {
        "Line": 638, "CharPositionInLine": 15, "kind": "SequenceType", "Children": {
            "base-address": type("base-address", (object,), {
                "Optional": "False", "Line": 639, "CharPositionInLine": 1, "type": type("base-address_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-base-address", "Min": "0", "Max": "4294967295"
                })
            }),
            "offset": type("offset", (object,), {
                "Optional": "False", "Line": 640, "CharPositionInLine": 1, "type": type("offset_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-offset", "Min": "-2147483648", "Max": "2147483647"
                })
            }),
            "base-type": type("base-type", (object,), {
                "Optional": "False", "Line": 641, "CharPositionInLine": 1, "type": type("base-type_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-base-type"
                })
            }),
            "nb-of-elements": type("nb-of-elements", (object,), {
                "Optional": "False", "Line": 642, "CharPositionInLine": 1, "type": type("nb-of-elements_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-nb-of-elements", "Min": "1", "Max": "10"
                })
            }),
            "sample-time": type("sample-time", (object,), {
                "Optional": "False", "Line": 643, "CharPositionInLine": 1, "type": type("sample-time_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-sample-time", "Min": "0", "Max": "15"
                })
            })
        }
    })
})

types["TASTE-Peek-list"] = type("TASTE-Peek-list", (object,), {
    "Line": 646, "CharPositionInLine": 0, "type": type("TASTE-Peek-list_type", (object,), {
        "Line": 646, "CharPositionInLine": 20, "kind": "SequenceOfType", "Min": "0", "Max": "5", "type": type("SeqOf_type", (object,), {
            "Line": 646, "CharPositionInLine": 46, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek"
        })
    })
})

types["TASTE-Peek-id"] = type("TASTE-Peek-id", (object,), {
    "Line": 648, "CharPositionInLine": 0, "type": type("TASTE-Peek-id_type", (object,), {
        "Line": 648, "CharPositionInLine": 18, "kind": "IntegerType", "Min": "0", "Max": "4294967295"
    })
})

types["TASTE-Peek-id-list"] = type("TASTE-Peek-id-list", (object,), {
    "Line": 650, "CharPositionInLine": 0, "type": type("TASTE-Peek-id-list_type", (object,), {
        "Line": 650, "CharPositionInLine": 23, "kind": "SequenceOfType", "Min": "1", "Max": "10", "type": type("SeqOf_type", (object,), {
            "Line": 650, "CharPositionInLine": 50, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-id", "Min": "0", "Max": "4294967295"
        })
    })
})

types["TASTE-Monitoring-value"] = type("TASTE-Monitoring-value", (object,), {
    "Line": 652, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-value_type", (object,), {
        "Line": 652, "CharPositionInLine": 27, "kind": "ChoiceType", "Children": {
            "int-32": type("int_32_PRESENT", (object,), {
                "Line": 653, "CharPositionInLine": 1, "EnumID": "int_32_PRESENT", "type": type("int_32_PRESENT_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-value-int-32", "Min": "-2147483648", "Max": "2147483647"
                })
            }),
            "int-64": type("int_64_PRESENT", (object,), {
                "Line": 654, "CharPositionInLine": 1, "EnumID": "int_64_PRESENT", "type": type("int_64_PRESENT_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-value-int-64", "Min": "-9223372036854775807", "Max": "9223372036854775807"
                })
            }),
            "real-single": type("real_single_PRESENT", (object,), {
                "Line": 655, "CharPositionInLine": 1, "EnumID": "real_single_PRESENT", "type": type("real_single_PRESENT_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-value-real-single", "Min": "-1E+38", "Max": "1E+38"
                })
            }),
            "real-double": type("real_double_PRESENT", (object,), {
                "Line": 656, "CharPositionInLine": 1, "EnumID": "real_double_PRESENT", "type": type("real_double_PRESENT_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-value-real-double", "Min": "-1E+308", "Max": "1E+308"
                })
            }),
            "octet-string": type("octet_string_PRESENT", (object,), {
                "Line": 657, "CharPositionInLine": 1, "EnumID": "octet_string_PRESENT", "type": type("octet_string_PRESENT_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-value-octet-string", "Min": "0", "Max": "10"
                })
            })
        }
    })
})

types["TASTE-Monitoring"] = type("TASTE-Monitoring", (object,), {
    "Line": 661, "CharPositionInLine": 0, "type": type("TASTE-Monitoring_type", (object,), {
        "Line": 661, "CharPositionInLine": 21, "kind": "SequenceType", "Children": {
            "id": type("id", (object,), {
                "Optional": "False", "Line": 662, "CharPositionInLine": 1, "type": type("id_type", (object,), {
                    "Line": 662, "CharPositionInLine": 4, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Peek-id", "Min": "0", "Max": "4294967295"
                })
            }),
            "values": type("values", (object,), {
                "Optional": "False", "Line": 663, "CharPositionInLine": 1, "type": type("values_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-values", "Min": "1", "Max": "10"
                })
            })
        }
    })
})

types["TASTE-Monitoring-list"] = type("TASTE-Monitoring-list", (object,), {
    "Line": 666, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-list_type", (object,), {
        "Line": 666, "CharPositionInLine": 26, "kind": "SequenceOfType", "Min": "0", "Max": "5", "type": type("SeqOf_type", (object,), {
            "Line": 666, "CharPositionInLine": 52, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring"
        })
    })
})

types["TASTE-Poke-list"] = type("TASTE-Poke-list", (object,), {
    "Line": 668, "CharPositionInLine": 0, "type": type("TASTE-Poke-list_type", (object,), {
        "Line": 668, "CharPositionInLine": 20, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-list", "Min": "0", "Max": "5"
    })
})

types["TASTE-Peek-limit"] = type("TASTE-Peek-limit", (object,), {
    "Line": 674, "CharPositionInLine": 0, "type": type("TASTE-Peek-limit_type", (object,), {
        "Line": 674, "CharPositionInLine": 21, "kind": "IntegerType", "Min": "0", "Max": "1000"
    })
})

types["TASTE-Monitoring-values"] = type("TASTE-Monitoring-values", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-values_type", (object,), {
        "Line": 663, "CharPositionInLine": 8, "kind": "SequenceOfType", "Min": "1", "Max": "10", "type": type("SeqOf_type", (object,), {
            "Line": 663, "CharPositionInLine": 35, "kind": "ReferenceType", "ReferencedTypeName": "TASTE-Monitoring-value"
        })
    })
})

types["TASTE-Monitoring-value-octet-string"] = type("TASTE-Monitoring-value-octet-string", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-value-octet-string_type", (object,), {
        "Line": 657, "CharPositionInLine": 14, "kind": "OctetStringType", "Min": "0", "Max": "10"
    })
})

types["TASTE-Monitoring-value-real-double"] = type("TASTE-Monitoring-value-real-double", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-value-real-double_type", (object,), {
        "Line": 656, "CharPositionInLine": 14, "kind": "RealType", "Min": "-1E+308", "Max": "1E+308"
    })
})

types["TASTE-Monitoring-value-real-single"] = type("TASTE-Monitoring-value-real-single", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-value-real-single_type", (object,), {
        "Line": 655, "CharPositionInLine": 13, "kind": "RealType", "Min": "-1E+38", "Max": "1E+38"
    })
})

types["TASTE-Monitoring-value-int-64"] = type("TASTE-Monitoring-value-int-64", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-value-int-64_type", (object,), {
        "Line": 654, "CharPositionInLine": 9, "kind": "IntegerType", "Min": "-9223372036854775807", "Max": "9223372036854775807"
    })
})

types["TASTE-Monitoring-value-int-32"] = type("TASTE-Monitoring-value-int-32", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Monitoring-value-int-32_type", (object,), {
        "Line": 653, "CharPositionInLine": 9, "kind": "IntegerType", "Min": "-2147483648", "Max": "2147483647"
    })
})

types["TASTE-Peek-sample-time"] = type("TASTE-Peek-sample-time", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Peek-sample-time_type", (object,), {
        "Line": 643, "CharPositionInLine": 13, "kind": "IntegerType", "Min": "0", "Max": "15"
    })
})

types["TASTE-Peek-nb-of-elements"] = type("TASTE-Peek-nb-of-elements", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Peek-nb-of-elements_type", (object,), {
        "Line": 642, "CharPositionInLine": 16, "kind": "IntegerType", "Min": "1", "Max": "10"
    })
})

types["TASTE-Peek-base-type"] = type("TASTE-Peek-base-type", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Peek-base-type_type", (object,), {
        "Line": 641, "CharPositionInLine": 11, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "int-32": type("int_32", (object,), {
                "IntValue": 0, "Line": 641, "CharPositionInLine": 24, "EnumID": "int_32"
            }),
            "int-64": type("int_64", (object,), {
                "IntValue": 1, "Line": 641, "CharPositionInLine": 32, "EnumID": "int_64"
            }),
            "real-single": type("real_single", (object,), {
                "IntValue": 2, "Line": 641, "CharPositionInLine": 40, "EnumID": "real_single"
            }),
            "real-double": type("real_double", (object,), {
                "IntValue": 3, "Line": 641, "CharPositionInLine": 53, "EnumID": "real_double"
            }),
            "octet-string": type("octet_string", (object,), {
                "IntValue": 4, "Line": 641, "CharPositionInLine": 66, "EnumID": "octet_string"
            })
        }
    })
})

types["TASTE-Peek-offset"] = type("TASTE-Peek-offset", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Peek-offset_type", (object,), {
        "Line": 640, "CharPositionInLine": 9, "kind": "IntegerType", "Min": "-2147483648", "Max": "2147483647"
    })
})

types["TASTE-Peek-base-address"] = type("TASTE-Peek-base-address", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("TASTE-Peek-base-address_type", (object,), {
        "Line": 639, "CharPositionInLine": 14, "kind": "IntegerType", "Min": "0", "Max": "4294967295"
    })
})
