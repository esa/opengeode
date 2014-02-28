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

asn1Modules.append("TASTE-Dataview")
exportedTypes["TASTE-Dataview"] = ["FCE-SGM-EEPROM", "FCE-SGM-RAM", "FCE-SIT-1", "FCE-SIT-2", "FCE-SIT-3", "FCE-SIT-4", "IMU", "CPST-CNF", "SADT-CNF", "CPSP-CNF", "SADP-CNF", "A-or-B", "D-or-X", "FCE-RECOVERY-STATUS-REGISTER", "FCE-CONTROL-FLAGS-STATUS-REGISTER", "Counter-ty", "Bool-ty", "Valid-ty", "Quaternion-ty", "Angular-rate-ty", "FCE-CONTROL-FLAGS-STATUS-REGISTER-arr-dep-flag", "IMU-cnf-g", "FCE-SIT-4-rc", "FCE-SIT-2-sc-conf", "FCE-SGM-RAM-llobt", "T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = [{"TASTE-BasicTypes":{"ImportedTypes": ["T-Int32","T-UInt32","T-Int8","T-UInt8","T-Boolean"], "ImportedVariables": []}}]
types["FCE-SGM-EEPROM"] = type("FCE-SGM-EEPROM", (object,), {
    "Line": 23, "CharPositionInLine": 0, "type": type("FCE-SGM-EEPROM_type", (object,), {
        "Line": 23, "CharPositionInLine": 19, "kind": "SequenceType", "Children": {
            "sit-1": type("sit-1", (object,), {
                "Optional": "False", "Line": 24, "CharPositionInLine": 4, "type": type("sit-1_type", (object,), {
                    "Line": 24, "CharPositionInLine": 12, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SIT-1"
                })
            }),
            "sit-2": type("sit-2", (object,), {
                "Optional": "False", "Line": 25, "CharPositionInLine": 4, "type": type("sit-2_type", (object,), {
                    "Line": 25, "CharPositionInLine": 12, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SIT-2"
                })
            }),
            "sit-3": type("sit-3", (object,), {
                "Optional": "False", "Line": 26, "CharPositionInLine": 4, "type": type("sit-3_type", (object,), {
                    "Line": 26, "CharPositionInLine": 12, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SIT-3"
                })
            }),
            "sit-4": type("sit-4", (object,), {
                "Optional": "False", "Line": 27, "CharPositionInLine": 4, "type": type("sit-4_type", (object,), {
                    "Line": 27, "CharPositionInLine": 12, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SIT-4"
                })
            })
        }
    })
})

types["FCE-SGM-RAM"] = type("FCE-SGM-RAM", (object,), {
    "Line": 30, "CharPositionInLine": 0, "type": type("FCE-SGM-RAM_type", (object,), {
        "Line": 30, "CharPositionInLine": 16, "kind": "SequenceType", "Children": {
            "llobt": type("llobt", (object,), {
                "Optional": "False", "Line": 31, "CharPositionInLine": 4, "type": type("llobt_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SGM-RAM-llobt", "Min": "0", "Max": "255"
                })
            }),
            "llatt": type("llatt", (object,), {
                "Optional": "False", "Line": 32, "CharPositionInLine": 4, "type": type("llatt_type", (object,), {
                    "Line": 32, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "Quaternion-ty"
                })
            }),
            "llare": type("llare", (object,), {
                "Optional": "False", "Line": 33, "CharPositionInLine": 4, "type": type("llare_type", (object,), {
                    "Line": 33, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "Angular-rate-ty"
                })
            })
        }
    })
})

types["FCE-SIT-1"] = type("FCE-SIT-1", (object,), {
    "Line": 37, "CharPositionInLine": 0, "type": type("FCE-SIT-1_type", (object,), {
        "Line": 37, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "imu-1": type("imu-1", (object,), {
                "Optional": "False", "Line": 38, "CharPositionInLine": 4, "type": type("imu-1_type", (object,), {
                    "Line": 38, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "IMU"
                })
            }),
            "imu-2": type("imu-2", (object,), {
                "Optional": "False", "Line": 39, "CharPositionInLine": 4, "type": type("imu-2_type", (object,), {
                    "Line": 39, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "IMU"
                })
            }),
            "riup-cnf-n": type("riup-cnf-n", (object,), {
                "Optional": "False", "Line": 40, "CharPositionInLine": 4, "type": type("riup-cnf-n_type", (object,), {
                    "Line": 40, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "riup-cnf-r": type("riup-cnf-r", (object,), {
                "Optional": "False", "Line": 41, "CharPositionInLine": 4, "type": type("riup-cnf-r_type", (object,), {
                    "Line": 41, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "riup-cnf-pwr-io-n": type("riup-cnf-pwr-io-n", (object,), {
                "Optional": "False", "Line": 43, "CharPositionInLine": 4, "type": type("riup-cnf-pwr-io-n_type", (object,), {
                    "Line": 43, "CharPositionInLine": 22, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "riup-cnf-pwr-io-r": type("riup-cnf-pwr-io-r", (object,), {
                "Optional": "False", "Line": 44, "CharPositionInLine": 4, "type": type("riup-cnf-pwr-io-r_type", (object,), {
                    "Line": 44, "CharPositionInLine": 22, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "spwr-cnf-n": type("spwr-cnf-n", (object,), {
                "Optional": "False", "Line": 45, "CharPositionInLine": 4, "type": type("spwr-cnf-n_type", (object,), {
                    "Line": 45, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "D-or-X"
                })
            }),
            "spwr-cnf-r": type("spwr-cnf-r", (object,), {
                "Optional": "False", "Line": 46, "CharPositionInLine": 4, "type": type("spwr-cnf-r_type", (object,), {
                    "Line": 46, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "D-or-X"
                })
            }),
            "rium-cnf-n": type("rium-cnf-n", (object,), {
                "Optional": "False", "Line": 47, "CharPositionInLine": 4, "type": type("rium-cnf-n_type", (object,), {
                    "Line": 47, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "rium-cnf-r": type("rium-cnf-r", (object,), {
                "Optional": "False", "Line": 48, "CharPositionInLine": 4, "type": type("rium-cnf-r_type", (object,), {
                    "Line": 48, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "rium-cnf-pwr-io-n": type("rium-cnf-pwr-io-n", (object,), {
                "Optional": "False", "Line": 49, "CharPositionInLine": 4, "type": type("rium-cnf-pwr-io-n_type", (object,), {
                    "Line": 49, "CharPositionInLine": 22, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "rium-cnf-pwr-io-r": type("rium-cnf-pwr-io-r", (object,), {
                "Optional": "False", "Line": 50, "CharPositionInLine": 4, "type": type("rium-cnf-pwr-io-r_type", (object,), {
                    "Line": 50, "CharPositionInLine": 22, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpst": type("cpst", (object,), {
                "Optional": "False", "Line": 51, "CharPositionInLine": 4, "type": type("cpst_type", (object,), {
                    "Line": 51, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "CPST-CNF"
                })
            }),
            "sadt": type("sadt", (object,), {
                "Optional": "False", "Line": 52, "CharPositionInLine": 4, "type": type("sadt_type", (object,), {
                    "Line": 52, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "SADT-CNF"
                })
            }),
            "cpsp": type("cpsp", (object,), {
                "Optional": "False", "Line": 53, "CharPositionInLine": 4, "type": type("cpsp_type", (object,), {
                    "Line": 53, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "CPSP-CNF"
                })
            }),
            "sadp": type("sadp", (object,), {
                "Optional": "False", "Line": 54, "CharPositionInLine": 4, "type": type("sadp_type", (object,), {
                    "Line": 54, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "SADP-CNF"
                })
            })
        }
    })
})

types["FCE-SIT-2"] = type("FCE-SIT-2", (object,), {
    "Line": 57, "CharPositionInLine": 0, "type": type("FCE-SIT-2_type", (object,), {
        "Line": 57, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "is-sep-phase": type("is-sep-phase", (object,), {
                "Optional": "False", "Line": 58, "CharPositionInLine": 4, "type": type("is-sep-phase_type", (object,), {
                    "Line": 58, "CharPositionInLine": 17, "kind": "BooleanType"
                })
            }),
            "sa-is-edge-on-sun-alwd": type("sa-is-edge-on-sun-alwd", (object,), {
                "Optional": "False", "Line": 59, "CharPositionInLine": 4, "type": type("sa-is-edge-on-sun-alwd_type", (object,), {
                    "Line": 59, "CharPositionInLine": 27, "kind": "BooleanType"
                })
            }),
            "sc-conf": type("sc-conf", (object,), {
                "Optional": "False", "Line": 60, "CharPositionInLine": 4, "type": type("sc-conf_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SIT-2-sc-conf"
                })
            })
        }
    })
})

types["FCE-SIT-3"] = type("FCE-SIT-3", (object,), {
    "Line": 63, "CharPositionInLine": 0, "type": type("FCE-SIT-3_type", (object,), {
        "Line": 63, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "null": type("null", (object,), {
                "Optional": "False", "Line": 64, "CharPositionInLine": 4, "type": type("null_type", (object,), {
                    "Line": 64, "CharPositionInLine": 9, "kind": "BooleanType"
                })
            })
        }
    })
})

types["FCE-SIT-4"] = type("FCE-SIT-4", (object,), {
    "Line": 67, "CharPositionInLine": 0, "type": type("FCE-SIT-4_type", (object,), {
        "Line": 67, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "rc": type("rc", (object,), {
                "Optional": "False", "Line": 68, "CharPositionInLine": 4, "type": type("rc_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "FCE-SIT-4-rc", "Min": "1", "Max": "5"
                })
            }),
            "ground-cmd-reset": type("ground-cmd-reset", (object,), {
                "Optional": "False", "Line": 69, "CharPositionInLine": 4, "type": type("ground-cmd-reset_type", (object,), {
                    "Line": 69, "CharPositionInLine": 21, "kind": "BooleanType"
                })
            }),
            "test-mode-counter": type("test-mode-counter", (object,), {
                "Optional": "True", "DefaultValue": "20", "Line": 70, "CharPositionInLine": 4, "type": type("test-mode-counter_type", (object,), {
                    "Line": 70, "CharPositionInLine": 22, "kind": "ReferenceType", "ReferencedTypeName": "Counter-ty", "Min": "0", "Max": "65535"
                })
            })
        }
    })
})

types["IMU"] = type("IMU", (object,), {
    "Line": 73, "CharPositionInLine": 0, "type": type("IMU_type", (object,), {
        "Line": 73, "CharPositionInLine": 8, "kind": "SequenceType", "Children": {
            "cnf-n": type("cnf-n", (object,), {
                "Optional": "False", "Line": 74, "CharPositionInLine": 4, "type": type("cnf-n_type", (object,), {
                    "Line": 74, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cnf-r": type("cnf-r", (object,), {
                "Optional": "False", "Line": 75, "CharPositionInLine": 4, "type": type("cnf-r_type", (object,), {
                    "Line": 75, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cnf-g": type("cnf-g", (object,), {
                "Optional": "False", "Line": 76, "CharPositionInLine": 4, "type": type("cnf-g_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "IMU-cnf-g", "Min": "0", "Max": "100"
                })
            })
        }
    })
})

types["CPST-CNF"] = type("CPST-CNF", (object,), {
    "Line": 79, "CharPositionInLine": 0, "type": type("CPST-CNF_type", (object,), {
        "Line": 79, "CharPositionInLine": 13, "kind": "SequenceType", "Children": {
            "cpst1-cnf-n": type("cpst1-cnf-n", (object,), {
                "Optional": "False", "Line": 80, "CharPositionInLine": 4, "type": type("cpst1-cnf-n_type", (object,), {
                    "Line": 80, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpst2-cnf-n": type("cpst2-cnf-n", (object,), {
                "Optional": "False", "Line": 81, "CharPositionInLine": 4, "type": type("cpst2-cnf-n_type", (object,), {
                    "Line": 81, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpst1-cnf-r": type("cpst1-cnf-r", (object,), {
                "Optional": "False", "Line": 82, "CharPositionInLine": 4, "type": type("cpst1-cnf-r_type", (object,), {
                    "Line": 82, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpst2-cnf-r": type("cpst2-cnf-r", (object,), {
                "Optional": "False", "Line": 83, "CharPositionInLine": 4, "type": type("cpst2-cnf-r_type", (object,), {
                    "Line": 83, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            })
        }
    })
})

types["SADT-CNF"] = type("SADT-CNF", (object,), {
    "Line": 86, "CharPositionInLine": 0, "type": type("SADT-CNF_type", (object,), {
        "Line": 86, "CharPositionInLine": 13, "kind": "SequenceType", "Children": {
            "cnf-n": type("cnf-n", (object,), {
                "Optional": "False", "Line": 87, "CharPositionInLine": 4, "type": type("cnf-n_type", (object,), {
                    "Line": 87, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cnf-r": type("cnf-r", (object,), {
                "Optional": "False", "Line": 88, "CharPositionInLine": 4, "type": type("cnf-r_type", (object,), {
                    "Line": 88, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            })
        }
    })
})

types["CPSP-CNF"] = type("CPSP-CNF", (object,), {
    "Line": 92, "CharPositionInLine": 0, "type": type("CPSP-CNF_type", (object,), {
        "Line": 92, "CharPositionInLine": 13, "kind": "SequenceType", "Children": {
            "cpsp1-cnf-n": type("cpsp1-cnf-n", (object,), {
                "Optional": "False", "Line": 93, "CharPositionInLine": 4, "type": type("cpsp1-cnf-n_type", (object,), {
                    "Line": 93, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpsp2-cnf-n": type("cpsp2-cnf-n", (object,), {
                "Optional": "False", "Line": 94, "CharPositionInLine": 4, "type": type("cpsp2-cnf-n_type", (object,), {
                    "Line": 94, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpsp1-cnf-r": type("cpsp1-cnf-r", (object,), {
                "Optional": "False", "Line": 95, "CharPositionInLine": 4, "type": type("cpsp1-cnf-r_type", (object,), {
                    "Line": 95, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cpsp2-cnf-r": type("cpsp2-cnf-r", (object,), {
                "Optional": "False", "Line": 96, "CharPositionInLine": 4, "type": type("cpsp2-cnf-r_type", (object,), {
                    "Line": 96, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            })
        }
    })
})

types["SADP-CNF"] = type("SADP-CNF", (object,), {
    "Line": 99, "CharPositionInLine": 0, "type": type("SADP-CNF_type", (object,), {
        "Line": 99, "CharPositionInLine": 13, "kind": "SequenceType", "Children": {
            "cnf-n": type("cnf-n", (object,), {
                "Optional": "False", "Line": 100, "CharPositionInLine": 4, "type": type("cnf-n_type", (object,), {
                    "Line": 100, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            }),
            "cnf-r": type("cnf-r", (object,), {
                "Optional": "False", "Line": 101, "CharPositionInLine": 4, "type": type("cnf-r_type", (object,), {
                    "Line": 101, "CharPositionInLine": 10, "kind": "ReferenceType", "ReferencedTypeName": "A-or-B"
                })
            })
        }
    })
})

types["A-or-B"] = type("A-or-B", (object,), {
    "Line": 104, "CharPositionInLine": 0, "type": type("A-or-B_type", (object,), {
        "Line": 104, "CharPositionInLine": 11, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "a": type("a", (object,), {
                "IntValue": 0, "Line": 104, "CharPositionInLine": 23, "EnumID": "a"
            }),
            "b": type("b", (object,), {
                "IntValue": 1, "Line": 104, "CharPositionInLine": 26, "EnumID": "b"
            })
        }
    })
})

types["D-or-X"] = type("D-or-X", (object,), {
    "Line": 105, "CharPositionInLine": 0, "type": type("D-or-X_type", (object,), {
        "Line": 105, "CharPositionInLine": 11, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "d": type("d", (object,), {
                "IntValue": 0, "Line": 105, "CharPositionInLine": 23, "EnumID": "d"
            }),
            "x": type("x", (object,), {
                "IntValue": 1, "Line": 105, "CharPositionInLine": 26, "EnumID": "x"
            })
        }
    })
})

types["FCE-RECOVERY-STATUS-REGISTER"] = type("FCE-RECOVERY-STATUS-REGISTER", (object,), {
    "Line": 108, "CharPositionInLine": 0, "type": type("FCE-RECOVERY-STATUS-REGISTER_type", (object,), {
        "Line": 108, "CharPositionInLine": 33, "kind": "SequenceType", "Children": {
            "l2rec": type("l2rec", (object,), {
                "Optional": "False", "Line": 109, "CharPositionInLine": 4, "type": type("l2rec_type", (object,), {
                    "Line": 109, "CharPositionInLine": 10, "kind": "BooleanType"
                })
            }),
            "l3rec": type("l3rec", (object,), {
                "Optional": "False", "Line": 110, "CharPositionInLine": 4, "type": type("l3rec_type", (object,), {
                    "Line": 110, "CharPositionInLine": 10, "kind": "BooleanType"
                })
            })
        }
    })
})

types["FCE-CONTROL-FLAGS-STATUS-REGISTER"] = type("FCE-CONTROL-FLAGS-STATUS-REGISTER", (object,), {
    "Line": 114, "CharPositionInLine": 0, "type": type("FCE-CONTROL-FLAGS-STATUS-REGISTER_type", (object,), {
        "Line": 114, "CharPositionInLine": 38, "kind": "SequenceType", "Children": {
            "arr-dep-flag": type("arr-dep-flag", (object,), {
                "Optional": "False", "Line": 115, "CharPositionInLine": 4, "type": type("arr-dep-flag_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "FCE-CONTROL-FLAGS-STATUS-REGISTER-arr-dep-flag"
                })
            }),
            "reference-pattern": type("reference-pattern", (object,), {
                "Optional": "False", "Line": 116, "CharPositionInLine": 4, "type": type("reference-pattern_type", (object,), {
                    "Line": 116, "CharPositionInLine": 22, "kind": "ReferenceType", "ReferencedTypeName": "Valid-ty"
                })
            })
        }
    })
})

types["Counter-ty"] = type("Counter-ty", (object,), {
    "Line": 119, "CharPositionInLine": 0, "type": type("Counter-ty_type", (object,), {
        "Line": 119, "CharPositionInLine": 15, "kind": "IntegerType", "Min": "0", "Max": "65535"
    })
})

types["Bool-ty"] = type("Bool-ty", (object,), {
    "Line": 120, "CharPositionInLine": 0, "type": type("Bool-ty_type", (object,), {
        "Line": 120, "CharPositionInLine": 12, "kind": "BooleanType"
    })
})

types["Valid-ty"] = type("Valid-ty", (object,), {
    "Line": 121, "CharPositionInLine": 0, "type": type("Valid-ty_type", (object,), {
        "Line": 121, "CharPositionInLine": 13, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "ok": type("ok", (object,), {
                "IntValue": 0, "Line": 121, "CharPositionInLine": 25, "EnumID": "ok"
            }),
            "nok": type("nok", (object,), {
                "IntValue": 1, "Line": 121, "CharPositionInLine": 29, "EnumID": "nok"
            })
        }
    })
})

types["Quaternion-ty"] = type("Quaternion-ty", (object,), {
    "Line": 122, "CharPositionInLine": 0, "type": type("Quaternion-ty_type", (object,), {
        "Line": 122, "CharPositionInLine": 18, "kind": "BooleanType"
    })
})

types["Angular-rate-ty"] = type("Angular-rate-ty", (object,), {
    "Line": 123, "CharPositionInLine": 0, "type": type("Angular-rate-ty_type", (object,), {
        "Line": 123, "CharPositionInLine": 20, "kind": "BooleanType"
    })
})

types["FCE-CONTROL-FLAGS-STATUS-REGISTER-arr-dep-flag"] = type("FCE-CONTROL-FLAGS-STATUS-REGISTER-arr-dep-flag", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("FCE-CONTROL-FLAGS-STATUS-REGISTER-arr-dep-flag_type", (object,), {
        "Line": 115, "CharPositionInLine": 17, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "majority": type("majority", (object,), {
                "IntValue": 0, "Line": 115, "CharPositionInLine": 29, "EnumID": "majority"
            }),
            "minority": type("minority", (object,), {
                "IntValue": 1, "Line": 115, "CharPositionInLine": 39, "EnumID": "minority"
            })
        }
    })
})

types["IMU-cnf-g"] = type("IMU-cnf-g", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("IMU-cnf-g_type", (object,), {
        "Line": 76, "CharPositionInLine": 10, "kind": "IntegerType", "Min": "0", "Max": "100"
    })
})

types["FCE-SIT-4-rc"] = type("FCE-SIT-4-rc", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("FCE-SIT-4-rc_type", (object,), {
        "Line": 68, "CharPositionInLine": 7, "kind": "IntegerType", "Min": "1", "Max": "5"
    })
})

types["FCE-SIT-2-sc-conf"] = type("FCE-SIT-2-sc-conf", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("FCE-SIT-2-sc-conf_type", (object,), {
        "Line": 60, "CharPositionInLine": 12, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "mcsc": type("mcsc", (object,), {
                "IntValue": 0, "Line": 60, "CharPositionInLine": 24, "EnumID": "mcsc"
            }),
            "mcsa": type("mcsa", (object,), {
                "IntValue": 1, "Line": 60, "CharPositionInLine": 30, "EnumID": "mcsa"
            }),
            "mcso": type("mcso", (object,), {
                "IntValue": 2, "Line": 60, "CharPositionInLine": 36, "EnumID": "mcso"
            }),
            "mpo": type("mpo", (object,), {
                "IntValue": 3, "Line": 60, "CharPositionInLine": 42, "EnumID": "mpo"
            })
        }
    })
})

types["FCE-SGM-RAM-llobt"] = type("FCE-SGM-RAM-llobt", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("FCE-SGM-RAM-llobt_type", (object,), {
        "Line": 31, "CharPositionInLine": 10, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})
