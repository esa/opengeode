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
exportedTypes["TASTE-Dataview"] = ["Number"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = []
types["Number"] = type("Number", (object,), {
    "Line": 4, "CharPositionInLine": 0, "type": type("Number_type", (object,), {
        "Line": 4, "CharPositionInLine": 14, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})
