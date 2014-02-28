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
exportedTypes["TASTE-Dataview"] = ["MyInteger", "MyReal", "MyEnum", "MySeq", "MyChoice", "MySeqOf", "MyOctStr", "MySeq-b", "T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["TASTE-Dataview"] = ["myVar"]
importedModules["TASTE-Dataview"] = [{"TASTE-BasicTypes":{"ImportedTypes": ["T-Int32","T-UInt32","T-Int8","T-UInt8","T-Boolean"], "ImportedVariables": []}}]
types["MyInteger"] = type("MyInteger", (object,), {
    "Line": 23, "CharPositionInLine": 0, "type": type("MyInteger_type", (object,), {
        "Line": 23, "CharPositionInLine": 16, "kind": "ReferenceType", "ReferencedTypeName": "T-UInt8", "Min": "0", "Max": "255", "ReferencedModName": "TASTE-BasicTypes"
    })
})

types["MyReal"] = type("MyReal", (object,), {
    "Line": 25, "CharPositionInLine": 0, "type": type("MyReal_type", (object,), {
        "Line": 25, "CharPositionInLine": 15, "kind": "RealType", "Min": "0", "Max": "1000"
    })
})

types["MyEnum"] = type("MyEnum", (object,), {
    "Line": 27, "CharPositionInLine": 0, "type": type("MyEnum_type", (object,), {
        "Line": 27, "CharPositionInLine": 15, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "hello": type("hello", (object,), {
                "IntValue": 0, "Line": 27, "CharPositionInLine": 28, "EnumID": "hello"
            }),
            "world": type("world", (object,), {
                "IntValue": 1, "Line": 27, "CharPositionInLine": 35, "EnumID": "world"
            }),
            "howareyou": type("howareyou", (object,), {
                "IntValue": 2, "Line": 27, "CharPositionInLine": 42, "EnumID": "howareyou"
            })
        }
    })
})

types["MySeq"] = type("MySeq", (object,), {
    "Line": 29, "CharPositionInLine": 0, "type": type("MySeq_type", (object,), {
        "Line": 29, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "a": type("a", (object,), {
                "Optional": "False", "Line": 30, "CharPositionInLine": 6, "type": type("a_type", (object,), {
                    "Line": 30, "CharPositionInLine": 8, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
                })
            }),
            "b": type("b", (object,), {
                "Optional": "False", "Line": 31, "CharPositionInLine": 6, "type": type("b_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MySeq-b"
                })
            })
        }
    })
})

types["MyChoice"] = type("MyChoice", (object,), {
    "Line": 34, "CharPositionInLine": 0, "type": type("MyChoice_type", (object,), {
        "Line": 34, "CharPositionInLine": 16, "kind": "ChoiceType", "Children": {
            "a": type("a_PRESENT", (object,), {
                "Line": 35, "CharPositionInLine": 6, "EnumID": "a_PRESENT", "type": type("a_PRESENT_type", (object,), {
                    "Line": 35, "CharPositionInLine": 8, "kind": "BooleanType"
                })
            }),
            "b": type("b_PRESENT", (object,), {
                "Line": 36, "CharPositionInLine": 6, "EnumID": "b_PRESENT", "type": type("b_PRESENT_type", (object,), {
                    "Line": 36, "CharPositionInLine": 8, "kind": "ReferenceType", "ReferencedTypeName": "MySeq"
                })
            })
        }
    })
})

types["MySeqOf"] = type("MySeqOf", (object,), {
    "Line": 39, "CharPositionInLine": 0, "type": type("MySeqOf_type", (object,), {
        "Line": 39, "CharPositionInLine": 16, "kind": "SequenceOfType", "Min": "2", "Max": "2", "type": type("SeqOf_type", (object,), {
            "Line": 39, "CharPositionInLine": 39, "kind": "ReferenceType", "ReferencedTypeName": "MyEnum"
        })
    })
})

types["MyOctStr"] = type("MyOctStr", (object,), {
    "Line": 41, "CharPositionInLine": 0, "type": type("MyOctStr_type", (object,), {
        "Line": 41, "CharPositionInLine": 16, "kind": "OctetStringType", "Min": "3", "Max": "3"
    })
})

types["MySeq-b"] = type("MySeq-b", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MySeq-b_type", (object,), {
        "Line": 31, "CharPositionInLine": 8, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "taste": type("taste", (object,), {
                "IntValue": 1, "Line": 31, "CharPositionInLine": 21, "EnumID": "taste"
            }),
            "welcomes": type("welcomes", (object,), {
                "IntValue": 2, "Line": 31, "CharPositionInLine": 31, "EnumID": "welcomes"
            }),
            "you": type("you", (object,), {
                "IntValue": 3, "Line": 31, "CharPositionInLine": 44, "EnumID": "you"
            })
        }
    })
})
