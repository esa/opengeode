#!/usr/bin/env python
# ASN.1 Data model
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
asn1Files.append("./dataview-uniq.asn")
asn1Modules.append("VEGA")
exportedTypes["VEGA"] = ["Simulation-Param", "T-GNC-LV-SIM-CONTEXT", "T-GNC-LV-SIM-INPUTS", "T-FLOAT32", "T-QUAT-FLOAT32", "T-VECT3-FLOAT32", "T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT", "T-TVC-SET-POINT-ENG-VECT", "T-RACS-EV-CMD-VECT", "T-DOUBLE", "T-Plot", "Simulation-Param-command", "T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["VEGA"] = ["size-T-QUAT-COMPONENTS", "size-T-AXIS-3-ID", "size-T-SEQUENCE-ID", "size-T-TVC-SET-POINT-ENG-VECT-IDX", "size-T-ACS-EQPT-ID"]
importedModules["VEGA"] = [{"TASTE-BasicTypes":{"ImportedTypes": ["T-Int32","T-UInt32","T-Int8","T-UInt8","T-Boolean"], "ImportedVariables": []}}]
types["Simulation-Param"] = type("Simulation-Param", (object,), {
    "Line": 8, "CharPositionInLine": 0, "type": type("Simulation-Param_type", (object,), {
        "Line": 8, "CharPositionInLine": 21, "kind": "SequenceType", "Children": {
            "command": type("command", (object,), {
                "Optional": "False", "Line": 9, "CharPositionInLine": 2, "type": type("command_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Simulation-Param-command"
                })
            }),
            "gnc-inputs": type("gnc-inputs", (object,), {
                "Optional": "False", "Line": 16, "CharPositionInLine": 2, "type": type("gnc-inputs_type", (object,), {
                    "Line": 16, "CharPositionInLine": 13, "kind": "ReferenceType", "ReferencedTypeName": "T-GNC-LV-SIM-CONTEXT"
                })
            })
        }
    })
})

types["T-GNC-LV-SIM-CONTEXT"] = type("T-GNC-LV-SIM-CONTEXT", (object,), {
    "Line": 21, "CharPositionInLine": 0, "type": type("T-GNC-LV-SIM-CONTEXT_type", (object,), {
        "Line": 21, "CharPositionInLine": 25, "kind": "SequenceType", "Children": {
            "attitude-quaternion": type("attitude-quaternion", (object,), {
                "Optional": "False", "Line": 22, "CharPositionInLine": 4, "type": type("attitude-quaternion_type", (object,), {
                    "Line": 22, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-QUAT-FLOAT32", "Min": "4", "Max": "4"
                })
            }),
            "ng-vel-incr-irs": type("ng-vel-incr-irs", (object,), {
                "Optional": "False", "Line": 23, "CharPositionInLine": 4, "type": type("ng-vel-incr-irs_type", (object,), {
                    "Line": 23, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            }),
            "ng-vel-incr-accelero": type("ng-vel-incr-accelero", (object,), {
                "Optional": "False", "Line": 24, "CharPositionInLine": 4, "type": type("ng-vel-incr-accelero_type", (object,), {
                    "Line": 24, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            }),
            "filtered-angles-sample-1": type("filtered-angles-sample-1", (object,), {
                "Optional": "False", "Line": 25, "CharPositionInLine": 4, "type": type("filtered-angles-sample-1_type", (object,), {
                    "Line": 25, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            }),
            "filtered-angles-sample-2": type("filtered-angles-sample-2", (object,), {
                "Optional": "False", "Line": 26, "CharPositionInLine": 4, "type": type("filtered-angles-sample-2_type", (object,), {
                    "Line": 26, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "T-VECT3-FLOAT32", "Min": "3", "Max": "3"
                })
            })
        }
    })
})

types["T-GNC-LV-SIM-INPUTS"] = type("T-GNC-LV-SIM-INPUTS", (object,), {
    "Line": 30, "CharPositionInLine": 0, "type": type("T-GNC-LV-SIM-INPUTS_type", (object,), {
        "Line": 30, "CharPositionInLine": 24, "kind": "SequenceType", "Children": {
            "sequ-exec-request-vect": type("sequ-exec-request-vect", (object,), {
                "Optional": "False", "Line": 31, "CharPositionInLine": 4, "type": type("sequ-exec-request-vect_type", (object,), {
                    "Line": 31, "CharPositionInLine": 29, "kind": "ReferenceType", "ReferencedTypeName": "T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT", "Min": "20", "Max": "20"
                })
            }),
            "tvc-set-point-eng-vect": type("tvc-set-point-eng-vect", (object,), {
                "Optional": "False", "Line": 32, "CharPositionInLine": 4, "type": type("tvc-set-point-eng-vect_type", (object,), {
                    "Line": 32, "CharPositionInLine": 28, "kind": "ReferenceType", "ReferencedTypeName": "T-TVC-SET-POINT-ENG-VECT", "Min": "8", "Max": "8"
                })
            }),
            "racs-ev-cmd-vect": type("racs-ev-cmd-vect", (object,), {
                "Optional": "False", "Line": 33, "CharPositionInLine": 4, "type": type("racs-ev-cmd-vect_type", (object,), {
                    "Line": 33, "CharPositionInLine": 28, "kind": "ReferenceType", "ReferencedTypeName": "T-RACS-EV-CMD-VECT", "Min": "6", "Max": "6"
                })
            })
        }
    })
})

types["T-FLOAT32"] = type("T-FLOAT32", (object,), {
    "Line": 38, "CharPositionInLine": 0, "type": type("T-FLOAT32_type", (object,), {
        "Line": 38, "CharPositionInLine": 14, "kind": "ReferenceType", "ReferencedTypeName": "T-DOUBLE", "Min": "-1E+308", "Max": "1E+308"
    })
})

types["T-QUAT-FLOAT32"] = type("T-QUAT-FLOAT32", (object,), {
    "Line": 42, "CharPositionInLine": 0, "type": type("T-QUAT-FLOAT32_type", (object,), {
        "Line": 42, "CharPositionInLine": 19, "kind": "SequenceOfType", "Min": "4", "Max": "4", "type": type("SeqOf_type", (object,), {
            "Line": 42, "CharPositionInLine": 62, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-VECT3-FLOAT32"] = type("T-VECT3-FLOAT32", (object,), {
    "Line": 45, "CharPositionInLine": 0, "type": type("T-VECT3-FLOAT32_type", (object,), {
        "Line": 45, "CharPositionInLine": 20, "kind": "SequenceOfType", "Min": "3", "Max": "3", "type": type("SeqOf_type", (object,), {
            "Line": 45, "CharPositionInLine": 57, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT"] = type("T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT", (object,), {
    "Line": 49, "CharPositionInLine": 0, "type": type("T-HAS-SEQUENCE-EXEC-BEEN-REQUESTED-VECT_type", (object,), {
        "Line": 49, "CharPositionInLine": 44, "kind": "SequenceOfType", "Min": "20", "Max": "20", "type": type("SeqOf_type", (object,), {
            "Line": 49, "CharPositionInLine": 83, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-TVC-SET-POINT-ENG-VECT"] = type("T-TVC-SET-POINT-ENG-VECT", (object,), {
    "Line": 53, "CharPositionInLine": 0, "type": type("T-TVC-SET-POINT-ENG-VECT_type", (object,), {
        "Line": 53, "CharPositionInLine": 29, "kind": "SequenceOfType", "Min": "8", "Max": "8", "type": type("SeqOf_type", (object,), {
            "Line": 53, "CharPositionInLine": 83, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-RACS-EV-CMD-VECT"] = type("T-RACS-EV-CMD-VECT", (object,), {
    "Line": 57, "CharPositionInLine": 0, "type": type("T-RACS-EV-CMD-VECT_type", (object,), {
        "Line": 57, "CharPositionInLine": 23, "kind": "SequenceOfType", "Min": "6", "Max": "6", "type": type("SeqOf_type", (object,), {
            "Line": 57, "CharPositionInLine": 62, "kind": "ReferenceType", "ReferencedTypeName": "T-FLOAT32", "Min": "-1E+308", "Max": "1E+308"
        })
    })
})

types["T-DOUBLE"] = type("T-DOUBLE", (object,), {
    "Line": 61, "CharPositionInLine": 0, "type": type("T-DOUBLE_type", (object,), {
        "Line": 61, "CharPositionInLine": 13, "kind": "RealType", "Min": "-1E+308", "Max": "1E+308"
    })
})

types["T-Plot"] = type("T-Plot", (object,), {
    "Line": 64, "CharPositionInLine": 0, "type": type("T-Plot_type", (object,), {
        "Line": 64, "CharPositionInLine": 11, "kind": "SequenceType", "Children": {
            "major-cycle": type("major-cycle", (object,), {
                "Optional": "False", "Line": 65, "CharPositionInLine": 4, "type": type("major-cycle_type", (object,), {
                    "Line": 65, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "T-UInt32", "Min": "0", "Max": "4294967295", "ReferencedModName": "TASTE-BasicTypes"
                })
            }),
            "subcycle": type("subcycle", (object,), {
                "Optional": "False", "Line": 66, "CharPositionInLine": 4, "type": type("subcycle_type", (object,), {
                    "Line": 66, "CharPositionInLine": 13, "kind": "ReferenceType", "ReferencedTypeName": "T-Int8", "Min": "-128", "Max": "127", "ReferencedModName": "TASTE-BasicTypes"
                })
            }),
            "gnc-inputs": type("gnc-inputs", (object,), {
                "Optional": "False", "Line": 67, "CharPositionInLine": 4, "type": type("gnc-inputs_type", (object,), {
                    "Line": 67, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "T-GNC-LV-SIM-CONTEXT"
                })
            }),
            "gnc-outputs": type("gnc-outputs", (object,), {
                "Optional": "False", "Line": 68, "CharPositionInLine": 4, "type": type("gnc-outputs_type", (object,), {
                    "Line": 68, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "T-GNC-LV-SIM-INPUTS"
                })
            })
        }
    })
})

types["Simulation-Param-command"] = type("Simulation-Param-command", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("Simulation-Param-command_type", (object,), {
        "Line": 9, "CharPositionInLine": 10, "kind": "ChoiceType", "Children": {
            "run-n-steps": type("run_n_steps_PRESENT", (object,), {
                "Line": 10, "CharPositionInLine": 6, "EnumID": "run_n_steps_PRESENT", "type": type("run_n_steps_PRESENT_type", (object,), {
                    "Line": 10, "CharPositionInLine": 18, "kind": "ReferenceType", "ReferencedTypeName": "T-UInt32", "Min": "0", "Max": "4294967295", "ReferencedModName": "TASTE-BasicTypes"
                })
            }),
            "run-n-seconds": type("run_n_seconds_PRESENT", (object,), {
                "Line": 11, "CharPositionInLine": 6, "EnumID": "run_n_seconds_PRESENT", "type": type("run_n_seconds_PRESENT_type", (object,), {
                    "Line": 11, "CharPositionInLine": 20, "kind": "ReferenceType", "ReferencedTypeName": "T-UInt32", "Min": "0", "Max": "4294967295", "ReferencedModName": "TASTE-BasicTypes"
                })
            }),
            "run-forever": type("run_forever_PRESENT", (object,), {
                "Line": 12, "CharPositionInLine": 6, "EnumID": "run_forever_PRESENT", "type": type("run_forever_PRESENT_type", (object,), {
                    "Line": 12, "CharPositionInLine": 18, "kind": "BooleanType"
                })
            }),
            "pause": type("pause_PRESENT", (object,), {
                "Line": 13, "CharPositionInLine": 6, "EnumID": "pause_PRESENT", "type": type("pause_PRESENT_type", (object,), {
                    "Line": 13, "CharPositionInLine": 12, "kind": "BooleanType"
                })
            }),
            "test-gnc": type("test_gnc_PRESENT", (object,), {
                "Line": 14, "CharPositionInLine": 6, "EnumID": "test_gnc_PRESENT", "type": type("test_gnc_PRESENT_type", (object,), {
                    "Line": 14, "CharPositionInLine": 15, "kind": "BooleanType"
                })
            })
        }
    })
})

asn1Modules.append("TASTE-BasicTypes")
exportedTypes["TASTE-BasicTypes"] = ["T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["TASTE-BasicTypes"] = []
importedModules["TASTE-BasicTypes"] = []
types["T-Int32"] = type("T-Int32", (object,), {
    "Line": 79, "CharPositionInLine": 0, "type": type("T-Int32_type", (object,), {
        "Line": 79, "CharPositionInLine": 13, "kind": "IntegerType", "Min": "-2147483648", "Max": "2147483647"
    })
})

types["T-UInt32"] = type("T-UInt32", (object,), {
    "Line": 81, "CharPositionInLine": 0, "type": type("T-UInt32_type", (object,), {
        "Line": 81, "CharPositionInLine": 13, "kind": "IntegerType", "Min": "0", "Max": "4294967295"
    })
})

types["T-Int8"] = type("T-Int8", (object,), {
    "Line": 83, "CharPositionInLine": 0, "type": type("T-Int8_type", (object,), {
        "Line": 83, "CharPositionInLine": 11, "kind": "IntegerType", "Min": "-128", "Max": "127"
    })
})

types["T-UInt8"] = type("T-UInt8", (object,), {
    "Line": 85, "CharPositionInLine": 0, "type": type("T-UInt8_type", (object,), {
        "Line": 85, "CharPositionInLine": 12, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["T-Boolean"] = type("T-Boolean", (object,), {
    "Line": 87, "CharPositionInLine": 0, "type": type("T-Boolean_type", (object,), {
        "Line": 87, "CharPositionInLine": 14, "kind": "BooleanType"
    })
})
