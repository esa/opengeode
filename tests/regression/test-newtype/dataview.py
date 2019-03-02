#!/usr/bin/env python
# ASN.1 Data model
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
variables = {}
asn1Files.append("dataview-uniq.asn")
asn1Modules.append("TASTE-Dataview")
exportedTypes["TASTE-Dataview"] = ["MyInteger", "SeqOf"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = []

types["MyInteger"] = type("MyInteger", (object,), {
    "Line": 4, "CharPositionInLine": 14, "type": type("MyInteger_type", (object,), {
        "Line": 4, "CharPositionInLine": 14, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["SeqOf"] = type("SeqOf", (object,), {
    "Line": 5, "CharPositionInLine": 14, "type": type("SeqOf_type", (object,), {
        "Line": 5, "CharPositionInLine": 14, "kind": "SequenceOfType", "Min": "0", "Max": "100", "type": type("SeqOf_type", (object,), {
            "Line": 5, "CharPositionInLine": 41, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
        })
    })
})


