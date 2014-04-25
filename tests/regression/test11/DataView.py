#!/usr/bin/env python
# ASN.1 Data model
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
asn1Files.append("./dataview-uniq.asn")
asn1Modules.append("TASTE-Dataview")
exportedTypes["TASTE-Dataview"] = ["Some-Thing", "MyInteger", "My-OctStr", "SeqOf"]
exportedVariables["TASTE-Dataview"] = ["default-seqof", "default-str"]
importedModules["TASTE-Dataview"] = []
types["Some-Thing"] = type("Some-Thing", (object,), {
    "Line": 6, "CharPositionInLine": 0, "type": type("Some-Thing_type", (object,), {
        "Line": 6, "CharPositionInLine": 15, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
    })
})

types["MyInteger"] = type("MyInteger", (object,), {
    "Line": 8, "CharPositionInLine": 0, "type": type("MyInteger_type", (object,), {
        "Line": 8, "CharPositionInLine": 16, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["My-OctStr"] = type("My-OctStr", (object,), {
    "Line": 10, "CharPositionInLine": 0, "type": type("My-OctStr_type", (object,), {
        "Line": 10, "CharPositionInLine": 17, "kind": "OctetStringType", "Min": "0", "Max": "20"
    })
})

types["SeqOf"] = type("SeqOf", (object,), {
    "Line": 12, "CharPositionInLine": 0, "type": type("SeqOf_type", (object,), {
        "Line": 12, "CharPositionInLine": 10, "kind": "SequenceOfType", "Min": "0", "Max": "100", "type": type("SeqOf_type", (object,), {
            "Line": 12, "CharPositionInLine": 37, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
        })
    })
})
