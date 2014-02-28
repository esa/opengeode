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
exportedTypes["TASTE-Dataview"] = ["MyInteger", "MyTest"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = []
types["MyInteger"] = type("MyInteger", (object,), {
    "Line": 4, "CharPositionInLine": 0, "type": type("MyInteger_type", (object,), {
        "Line": 4, "CharPositionInLine": 14, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["MyTest"] = type("MyTest", (object,), {
    "Line": 6, "CharPositionInLine": 0, "type": type("MyTest_type", (object,), {
        "Line": 6, "CharPositionInLine": 11, "kind": "SequenceOfType", "Min": "2", "Max": "2", "type": type("SeqOf_type", (object,), {
            "Line": 6, "CharPositionInLine": 33, "kind": "BooleanType"
        })
    })
})
