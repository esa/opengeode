#!/usr/bin/env python
# ASN.1 Data model
# EXPERIMENTAL VERSION
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
asn1Files.append("dataview-uniq.asn")
asn1Modules.append("TASTE-BasicTypes")
exportedTypes["TASTE-BasicTypes"] = ["T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean", "BitString", "OctString", "SeqBit", "SeqBit2"]
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

types["BitString"] = type("BitString", (object,), {
    "Line": 16, "CharPositionInLine": 0, "type": type("BitString_type", (object,), {
        "Line": 16, "CharPositionInLine": 14, "kind": "BitStringType", "Min": "32", "Max": "32"
    })
})

types["OctString"] = type("OctString", (object,), {
    "Line": 17, "CharPositionInLine": 0, "type": type("OctString_type", (object,), {
        "Line": 17, "CharPositionInLine": 14, "kind": "OctetStringType", "Min": "4", "Max": "4"
    })
})

types["SeqBit"] = type("SeqBit", (object,), {
    "Line": 18, "CharPositionInLine": 0, "type": type("SeqBit_type", (object,), {
        "Line": 18, "CharPositionInLine": 11, "kind": "SequenceOfType", "Min": "32", "Max": "32", "type": type("SeqOf_type", (object,), {
            "Line": 18, "CharPositionInLine": 34, "kind": "BooleanType"
        })
    })
})

types["SeqBit2"] = type("SeqBit2", (object,), {
    "Line": 19, "CharPositionInLine": 0, "type": type("SeqBit2_type", (object,), {
        "Line": 19, "CharPositionInLine": 12, "kind": "SequenceOfType", "Min": "1", "Max": "32", "type": type("SeqOf_type", (object,), {
            "Line": 19, "CharPositionInLine": 38, "kind": "BooleanType"
        })
    })
})

asn1Modules.append("TASTE-Dataview")
exportedTypes["TASTE-Dataview"] = ["CountTab", "T-Int32", "T-UInt32", "T-Int8", "T-UInt8", "T-Boolean"]
exportedVariables["TASTE-Dataview"] = ["challenge", "bound", "nb-bit", "val-max", "count-max", "exceed-nb"]
importedModules["TASTE-Dataview"] = [{"TASTE-BasicTypes":{"ImportedTypes": ["T-Int32","T-UInt32","T-Int8","T-UInt8","T-Boolean"], "ImportedVariables": []}}]
types["CountTab"] = type("CountTab", (object,), {
    "Line": 36, "CharPositionInLine": 0, "type": type("CountTab_type", (object,), {
        "Line": 36, "CharPositionInLine": 13, "kind": "SequenceOfType", "Min": "20", "Max": "20", "type": type("SeqOf_type", (object,), {
            "Line": 36, "CharPositionInLine": 40, "kind": "ReferenceType", "ReferencedTypeName": "T-UInt32", "Min": "0", "Max": "4294967295", "ReferencedModName": "TASTE-BasicTypes"
        })
    })
})
