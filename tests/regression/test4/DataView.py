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
exportedTypes["TASTE-Dataview"] = ["DeepSeq", "MyComplexType", "MyComplexSeqOf", "MyComplexChoice", "MyRefSeqOf", "MyInteger", "MyReal", "MyEnum", "MySeq", "MyChoice", "MySeqOf", "MyPossiblyEmptySeqOf", "MySeqWithEmbeddedSeqOf", "MyOctStr", "MySeqWithEmbeddedSeqOf-a", "MyPossiblyEmptySeqOf-elm", "MySeq-b", "MyComplexChoice-a", "MyComplexSeqOf-elm", "MyComplexType-a", "DeepSeq-a", "DeepSeq-a-b", "MyComplexType-a-x", "MyComplexSeqOf-elm-x", "MyComplexChoice-a-x", "DeepSeq-a-b-d"]
exportedVariables["TASTE-Dataview"] = []
importedModules["TASTE-Dataview"] = []
types["DeepSeq"] = type("DeepSeq", (object,), {
    "Line": 4, "CharPositionInLine": 0, "type": type("DeepSeq_type", (object,), {
        "Line": 4, "CharPositionInLine": 12, "kind": "SequenceType", "Children": {
            "a": type("a", (object,), {
                "Optional": "False", "Line": 5, "CharPositionInLine": 1, "type": type("a_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "DeepSeq-a"
                })
            })
        }
    })
})

types["MyComplexType"] = type("MyComplexType", (object,), {
    "Line": 17, "CharPositionInLine": 0, "type": type("MyComplexType_type", (object,), {
        "Line": 17, "CharPositionInLine": 18, "kind": "SequenceType", "Children": {
            "a": type("a", (object,), {
                "Optional": "False", "Line": 18, "CharPositionInLine": 1, "type": type("a_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyComplexType-a"
                })
            })
        }
    })
})

types["MyComplexSeqOf"] = type("MyComplexSeqOf", (object,), {
    "Line": 21, "CharPositionInLine": 0, "type": type("MyComplexSeqOf_type", (object,), {
        "Line": 21, "CharPositionInLine": 19, "kind": "SequenceOfType", "Min": "2", "Max": "2", "type": type("SeqOf_type", (object,), {
            "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyComplexSeqOf-elm"
        })
    })
})

types["MyComplexChoice"] = type("MyComplexChoice", (object,), {
    "Line": 23, "CharPositionInLine": 0, "type": type("MyComplexChoice_type", (object,), {
        "Line": 23, "CharPositionInLine": 20, "kind": "ChoiceType", "Children": {
            "a": type("MyComplexChoice_a_PRESENT", (object,), {
                "Line": 23, "CharPositionInLine": 29, "EnumID": "MyComplexChoice_a_PRESENT", "type": type("MyComplexChoice_a_PRESENT_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyComplexChoice-a"
                })
            })
        }
    })
})

types["MyRefSeqOf"] = type("MyRefSeqOf", (object,), {
    "Line": 25, "CharPositionInLine": 0, "type": type("MyRefSeqOf_type", (object,), {
        "Line": 25, "CharPositionInLine": 15, "kind": "SequenceType", "Children": {
            "seqof": type("seqof", (object,), {
                "Optional": "False", "Line": 25, "CharPositionInLine": 26, "type": type("seqof_type", (object,), {
                    "Line": 25, "CharPositionInLine": 32, "kind": "ReferenceType", "ReferencedTypeName": "MySeqOf", "Min": "2", "Max": "2"
                })
            })
        }
    })
})

types["MyInteger"] = type("MyInteger", (object,), {
    "Line": 28, "CharPositionInLine": 0, "type": type("MyInteger_type", (object,), {
        "Line": 28, "CharPositionInLine": 16, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["MyReal"] = type("MyReal", (object,), {
    "Line": 30, "CharPositionInLine": 0, "type": type("MyReal_type", (object,), {
        "Line": 30, "CharPositionInLine": 15, "kind": "RealType", "Min": "0", "Max": "1000"
    })
})

types["MyEnum"] = type("MyEnum", (object,), {
    "Line": 32, "CharPositionInLine": 0, "type": type("MyEnum_type", (object,), {
        "Line": 32, "CharPositionInLine": 15, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "hello": type("hello", (object,), {
                "IntValue": 0, "Line": 32, "CharPositionInLine": 28, "EnumID": "hello"
            }),
            "world": type("world", (object,), {
                "IntValue": 1, "Line": 32, "CharPositionInLine": 35, "EnumID": "world"
            }),
            "howareyou": type("howareyou", (object,), {
                "IntValue": 2, "Line": 32, "CharPositionInLine": 42, "EnumID": "howareyou"
            })
        }
    })
})

types["MySeq"] = type("MySeq", (object,), {
    "Line": 34, "CharPositionInLine": 0, "type": type("MySeq_type", (object,), {
        "Line": 34, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "a": type("a", (object,), {
                "Optional": "False", "Line": 35, "CharPositionInLine": 6, "type": type("a_type", (object,), {
                    "Line": 35, "CharPositionInLine": 8, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
                })
            }),
            "b": type("b", (object,), {
                "Optional": "False", "Line": 36, "CharPositionInLine": 6, "type": type("b_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MySeq-b"
                })
            })
        }
    })
})

types["MyChoice"] = type("MyChoice", (object,), {
    "Line": 39, "CharPositionInLine": 0, "type": type("MyChoice_type", (object,), {
        "Line": 39, "CharPositionInLine": 16, "kind": "ChoiceType", "Children": {
            "a": type("MyChoice_a_PRESENT", (object,), {
                "Line": 40, "CharPositionInLine": 6, "EnumID": "MyChoice_a_PRESENT", "type": type("MyChoice_a_PRESENT_type", (object,), {
                    "Line": 40, "CharPositionInLine": 8, "kind": "BooleanType"
                })
            }),
            "b": type("b_PRESENT", (object,), {
                "Line": 41, "CharPositionInLine": 6, "EnumID": "b_PRESENT", "type": type("b_PRESENT_type", (object,), {
                    "Line": 41, "CharPositionInLine": 8, "kind": "ReferenceType", "ReferencedTypeName": "MySeq"
                })
            })
        }
    })
})

types["MySeqOf"] = type("MySeqOf", (object,), {
    "Line": 44, "CharPositionInLine": 0, "type": type("MySeqOf_type", (object,), {
        "Line": 44, "CharPositionInLine": 16, "kind": "SequenceOfType", "Min": "2", "Max": "2", "type": type("SeqOf_type", (object,), {
            "Line": 44, "CharPositionInLine": 39, "kind": "ReferenceType", "ReferencedTypeName": "MyEnum"
        })
    })
})

types["MyPossiblyEmptySeqOf"] = type("MyPossiblyEmptySeqOf", (object,), {
    "Line": 45, "CharPositionInLine": 0, "type": type("MyPossiblyEmptySeqOf_type", (object,), {
        "Line": 45, "CharPositionInLine": 25, "kind": "SequenceOfType", "Min": "0", "Max": "2", "type": type("SeqOf_type", (object,), {
            "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyPossiblyEmptySeqOf-elm", "Min": "1", "Max": "2"
        })
    })
})

types["MySeqWithEmbeddedSeqOf"] = type("MySeqWithEmbeddedSeqOf", (object,), {
    "Line": 47, "CharPositionInLine": 0, "type": type("MySeqWithEmbeddedSeqOf_type", (object,), {
        "Line": 47, "CharPositionInLine": 27, "kind": "SequenceType", "Children": {
            "a": type("a", (object,), {
                "Optional": "False", "Line": 48, "CharPositionInLine": 4, "type": type("a_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MySeqWithEmbeddedSeqOf-a", "Min": "0", "Max": "2"
                })
            })
        }
    })
})

types["MyOctStr"] = type("MyOctStr", (object,), {
    "Line": 51, "CharPositionInLine": 0, "type": type("MyOctStr_type", (object,), {
        "Line": 51, "CharPositionInLine": 16, "kind": "OctetStringType", "Min": "3", "Max": "3"
    })
})

types["MySeqWithEmbeddedSeqOf-a"] = type("MySeqWithEmbeddedSeqOf-a", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MySeqWithEmbeddedSeqOf-a_type", (object,), {
        "Line": 48, "CharPositionInLine": 6, "kind": "SequenceOfType", "Min": "0", "Max": "2", "type": type("SeqOf_type", (object,), {
            "Line": 48, "CharPositionInLine": 30, "kind": "BooleanType"
        })
    })
})

types["MyPossiblyEmptySeqOf-elm"] = type("MyPossiblyEmptySeqOf-elm", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyPossiblyEmptySeqOf-elm_type", (object,), {
        "Line": 45, "CharPositionInLine": 49, "kind": "IntegerType", "Min": "1", "Max": "2"
    })
})

types["MySeq-b"] = type("MySeq-b", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MySeq-b_type", (object,), {
        "Line": 36, "CharPositionInLine": 8, "kind": "EnumeratedType", "Extensible": "False", "ValuesAutoCalculated": "False", "EnumValues": {
            "taste": type("taste", (object,), {
                "IntValue": 1, "Line": 36, "CharPositionInLine": 21, "EnumID": "taste"
            }),
            "welcomes": type("welcomes", (object,), {
                "IntValue": 2, "Line": 36, "CharPositionInLine": 31, "EnumID": "welcomes"
            }),
            "you": type("you", (object,), {
                "IntValue": 3, "Line": 36, "CharPositionInLine": 44, "EnumID": "you"
            })
        }
    })
})

types["MyComplexChoice-a"] = type("MyComplexChoice-a", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyComplexChoice-a_type", (object,), {
        "Line": 23, "CharPositionInLine": 31, "kind": "SequenceType", "Children": {
            "x": type("x", (object,), {
                "Optional": "False", "Line": 23, "CharPositionInLine": 42, "type": type("x_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyComplexChoice-a-x", "Min": "0", "Max": "255"
                })
            })
        }
    })
})

types["MyComplexSeqOf-elm"] = type("MyComplexSeqOf-elm", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyComplexSeqOf-elm_type", (object,), {
        "Line": 21, "CharPositionInLine": 40, "kind": "SequenceType", "Children": {
            "x": type("x", (object,), {
                "Optional": "False", "Line": 21, "CharPositionInLine": 51, "type": type("x_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyComplexSeqOf-elm-x", "Min": "0", "Max": "255"
                })
            })
        }
    })
})

types["MyComplexType-a"] = type("MyComplexType-a", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyComplexType-a_type", (object,), {
        "Line": 18, "CharPositionInLine": 3, "kind": "SequenceType", "Children": {
            "x": type("x", (object,), {
                "Optional": "False", "Line": 18, "CharPositionInLine": 14, "type": type("x_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "MyComplexType-a-x", "Min": "0", "Max": "255"
                })
            }),
            "y": type("y", (object,), {
                "Optional": "False", "Line": 18, "CharPositionInLine": 33, "type": type("y_type", (object,), {
                    "Line": 18, "CharPositionInLine": 35, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
                })
            })
        }
    })
})

types["DeepSeq-a"] = type("DeepSeq-a", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("DeepSeq-a_type", (object,), {
        "Line": 5, "CharPositionInLine": 3, "kind": "SequenceType", "Children": {
            "b": type("b", (object,), {
                "Optional": "False", "Line": 6, "CharPositionInLine": 2, "type": type("b_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "DeepSeq-a-b"
                })
            })
        }
    })
})

types["DeepSeq-a-b"] = type("DeepSeq-a-b", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("DeepSeq-a-b_type", (object,), {
        "Line": 6, "CharPositionInLine": 4, "kind": "SequenceType", "Children": {
            "c": type("c", (object,), {
                "Optional": "False", "Line": 7, "CharPositionInLine": 3, "type": type("c_type", (object,), {
                    "Line": 7, "CharPositionInLine": 5, "kind": "ReferenceType", "ReferencedTypeName": "MyInteger", "Min": "0", "Max": "255"
                })
            }),
            "d": type("d", (object,), {
                "Optional": "False", "Line": 8, "CharPositionInLine": 3, "type": type("d_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "DeepSeq-a-b-d"
                })
            })
        }
    })
})

types["MyComplexType-a-x"] = type("MyComplexType-a-x", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyComplexType-a-x_type", (object,), {
        "Line": 18, "CharPositionInLine": 16, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["MyComplexSeqOf-elm-x"] = type("MyComplexSeqOf-elm-x", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyComplexSeqOf-elm-x_type", (object,), {
        "Line": 21, "CharPositionInLine": 53, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["MyComplexChoice-a-x"] = type("MyComplexChoice-a-x", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("MyComplexChoice-a-x_type", (object,), {
        "Line": 23, "CharPositionInLine": 44, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["DeepSeq-a-b-d"] = type("DeepSeq-a-b-d", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("DeepSeq-a-b-d_type", (object,), {
        "Line": 8, "CharPositionInLine": 5, "kind": "ChoiceType", "Children": {
            "e": type("e_PRESENT", (object,), {
                "Line": 9, "CharPositionInLine": 4, "EnumID": "e_PRESENT", "type": type("e_PRESENT_type", (object,), {
                    "Line": 9, "CharPositionInLine": 6, "kind": "BooleanType"
                })
            })
        }
    })
})
