#!/usr/bin/env python
# ASN.1 Data model
asn1Files = []
asn1Modules = []
exportedTypes = {}
exportedVariables = {}
importedModules = {}
types = {}
asn1Files.append("dataview-uniq.asn")
asn1Modules.append("TASTE-Dataview")
exportedTypes["TASTE-Dataview"] = ["Int", "Bool", "Float"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = []
types["Int"] = type("Int", (object,), {
    "Line": 4, "CharPositionInLine": 0, "type": type("Int_type", (object,), {
        "Line": 4, "CharPositionInLine": 8, "kind": "IntegerType", "Min": "MIN", "Max": "MAX"
    })
})

types["Bool"] = type("Bool", (object,), {
    "Line": 5, "CharPositionInLine": 0, "type": type("Bool_type", (object,), {
        "Line": 5, "CharPositionInLine": 9, "kind": "BooleanType"
    })
})

types["Float"] = type("Float", (object,), {
    "Line": 6, "CharPositionInLine": 0, "type": type("Float_type", (object,), {
        "Line": 6, "CharPositionInLine": 10, "kind": "RealType", "Min": "MIN", "Max": "MAX"
    })
})
