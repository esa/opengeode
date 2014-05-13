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
exportedTypes["TASTE-Dataview"] = ["Light", "T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = [{"TASTE-BasicTypes":{"ImportedTypes": ["T-Int32","T-UInt32","T-Int8","T-UInt8","T-Boolean"], "ImportedVariables": []}}]
types["Light"] = type("Light", (object,), {
    "Line": 22, "CharPositionInLine": 0, "type": type("Light_type", (object,), {
        "Line": 22, "CharPositionInLine": 14, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "red": type("red", (object,), {
                "IntValue": 0, "Line": 22, "CharPositionInLine": 27, "EnumID": "red"
            }),
            "yellow": type("yellow", (object,), {
                "IntValue": 1, "Line": 22, "CharPositionInLine": 32, "EnumID": "yellow"
            }),
            "green": type("green", (object,), {
                "IntValue": 2, "Line": 22, "CharPositionInLine": 40, "EnumID": "green"
            }),
            "all-off": type("all_off", (object,), {
                "IntValue": 3, "Line": 22, "CharPositionInLine": 47, "EnumID": "all_off"
            })
        }
    })
})
