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
exportedTypes["TASTE-Dataview"] = ["Letter", "Cost-ty", "Tree-Elem", "Sons", "Tree", "Path", "Path-elem"]
exportedVariables["TASTE-Dataview"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
importedModules["TASTE-Dataview"] = []

types["Letter"] = type("Letter", (object,), {
    "Line": 5, "CharPositionInLine": 0, "type": type("Letter_type", (object,), {
        "Line": 5, "CharPositionInLine": 11, "kind": "IntegerType", "Min": "0", "Max": "25"
    })
})

types["Cost-ty"] = type("Cost-ty", (object,), {
    "Line": 33, "CharPositionInLine": 0, "type": type("Cost-ty_type", (object,), {
        "Line": 33, "CharPositionInLine": 12, "kind": "IntegerType", "Min": "0", "Max": "255"
    })
})

types["Tree-Elem"] = type("Tree-Elem", (object,), {
    "Line": 35, "CharPositionInLine": 0, "type": type("Tree-Elem_type", (object,), {
        "Line": 35, "CharPositionInLine": 14, "kind": "SequenceType", "Children": {
            "cost": type("cost", (object,), {
                "Optional": "False", "Line": 36, "CharPositionInLine": 4, "type": type("cost_type", (object,), {
                    "Line": 36, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "Cost-ty", "Min": "0", "Max": "255"
                })
            }),
            "son": type("son", (object,), {
                "Optional": "False", "Line": 37, "CharPositionInLine": 4, "type": type("son_type", (object,), {
                    "Line": 37, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
                })
            })
        }
    })
})

types["Sons"] = type("Sons", (object,), {
    "Line": 39, "CharPositionInLine": 0, "type": type("Sons_type", (object,), {
        "Line": 39, "CharPositionInLine": 9, "kind": "SequenceOfType", "Min": "0", "Max": "100", "type": type("SeqOf_type", (object,), {
            "Line": 39, "CharPositionInLine": 37, "kind": "ReferenceType", "ReferencedTypeName": "Tree-Elem"
        })
    })
})

types["Tree"] = type("Tree", (object,), {
    "Line": 40, "CharPositionInLine": 0, "type": type("Tree_type", (object,), {
        "Line": 40, "CharPositionInLine": 9, "kind": "SequenceOfType", "Min": "26", "Max": "26", "type": type("SeqOf_type", (object,), {
            "Line": 40, "CharPositionInLine": 37, "kind": "ReferenceType", "ReferencedTypeName": "Sons", "Min": "0", "Max": "100"
        })
    })
})

types["Path"] = type("Path", (object,), {
    "Line": 42, "CharPositionInLine": 0, "type": type("Path_type", (object,), {
        "Line": 42, "CharPositionInLine": 9, "kind": "SequenceType", "Children": {
            "cost": type("cost", (object,), {
                "Optional": "False", "Line": 43, "CharPositionInLine": 4, "type": type("cost_type", (object,), {
                    "Line": 43, "CharPositionInLine": 9, "kind": "ReferenceType", "ReferencedTypeName": "Cost-ty", "Min": "0", "Max": "255"
                })
            }),
            "elem": type("elem", (object,), {
                "Optional": "False", "Line": 44, "CharPositionInLine": 4, "type": type("elem_type", (object,), {
                    "Line": 0, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Path-elem", "Min": "0", "Max": "255"
                })
            })
        }
    })
})

types["Path-elem"] = type("Path-elem", (object,), {
    "Line": 0, "CharPositionInLine": 0, "type": type("Path-elem_type", (object,), {
        "Line": 44, "CharPositionInLine": 9, "kind": "SequenceOfType", "Min": "0", "Max": "255", "type": type("SeqOf_type", (object,), {
            "Line": 44, "CharPositionInLine": 36, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
        })
    })
})


variables["a"] = type("a", (object,), {
    "Line": 6,
    "CharPositionInLine": 2,
    "varName": "Letter_a",
    "type": type("a_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 0
})

variables["b"] = type("b", (object,), {
    "Line": 7,
    "CharPositionInLine": 2,
    "varName": "Letter_b",
    "type": type("b_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 1
})

variables["c"] = type("c", (object,), {
    "Line": 8,
    "CharPositionInLine": 2,
    "varName": "Letter_c",
    "type": type("c_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 2
})

variables["d"] = type("d", (object,), {
    "Line": 9,
    "CharPositionInLine": 2,
    "varName": "Letter_d",
    "type": type("d_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 3
})

variables["e"] = type("e", (object,), {
    "Line": 10,
    "CharPositionInLine": 2,
    "varName": "Letter_e",
    "type": type("e_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 4
})

variables["f"] = type("f", (object,), {
    "Line": 11,
    "CharPositionInLine": 2,
    "varName": "Letter_f",
    "type": type("f_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 5
})

variables["g"] = type("g", (object,), {
    "Line": 12,
    "CharPositionInLine": 2,
    "varName": "Letter_g",
    "type": type("g_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 6
})

variables["h"] = type("h", (object,), {
    "Line": 13,
    "CharPositionInLine": 2,
    "varName": "Letter_h",
    "type": type("h_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 7
})

variables["i"] = type("i", (object,), {
    "Line": 14,
    "CharPositionInLine": 2,
    "varName": "Letter_i",
    "type": type("i_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 8
})

variables["j"] = type("j", (object,), {
    "Line": 15,
    "CharPositionInLine": 2,
    "varName": "Letter_j",
    "type": type("j_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 9
})

variables["k"] = type("k", (object,), {
    "Line": 16,
    "CharPositionInLine": 2,
    "varName": "Letter_k",
    "type": type("k_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 10
})

variables["l"] = type("l", (object,), {
    "Line": 17,
    "CharPositionInLine": 2,
    "varName": "Letter_l",
    "type": type("l_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 11
})

variables["m"] = type("m", (object,), {
    "Line": 18,
    "CharPositionInLine": 2,
    "varName": "Letter_m",
    "type": type("m_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 12
})

variables["n"] = type("n", (object,), {
    "Line": 19,
    "CharPositionInLine": 2,
    "varName": "Letter_n",
    "type": type("n_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 13
})

variables["o"] = type("o", (object,), {
    "Line": 20,
    "CharPositionInLine": 2,
    "varName": "Letter_o",
    "type": type("o_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 14
})

variables["p"] = type("p", (object,), {
    "Line": 21,
    "CharPositionInLine": 2,
    "varName": "Letter_p",
    "type": type("p_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 15
})

variables["q"] = type("q", (object,), {
    "Line": 22,
    "CharPositionInLine": 2,
    "varName": "Letter_q",
    "type": type("q_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 16
})

variables["r"] = type("r", (object,), {
    "Line": 23,
    "CharPositionInLine": 2,
    "varName": "Letter_r",
    "type": type("r_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 17
})

variables["s"] = type("s", (object,), {
    "Line": 24,
    "CharPositionInLine": 2,
    "varName": "Letter_s",
    "type": type("s_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 18
})

variables["t"] = type("t", (object,), {
    "Line": 25,
    "CharPositionInLine": 2,
    "varName": "Letter_t",
    "type": type("t_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 19
})

variables["u"] = type("u", (object,), {
    "Line": 26,
    "CharPositionInLine": 2,
    "varName": "Letter_u",
    "type": type("u_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 20
})

variables["v"] = type("v", (object,), {
    "Line": 27,
    "CharPositionInLine": 2,
    "varName": "Letter_v",
    "type": type("v_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 21
})

variables["w"] = type("w", (object,), {
    "Line": 28,
    "CharPositionInLine": 2,
    "varName": "Letter_w",
    "type": type("w_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 22
})

variables["x"] = type("x", (object,), {
    "Line": 29,
    "CharPositionInLine": 2,
    "varName": "Letter_x",
    "type": type("x_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 23
})

variables["y"] = type("y", (object,), {
    "Line": 30,
    "CharPositionInLine": 2,
    "varName": "Letter_y",
    "type": type("y_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 24
})

variables["z"] = type("z", (object,), {
    "Line": 31,
    "CharPositionInLine": 2,
    "varName": "Letter_z",
    "type": type("z_type", (object,), {
        "Line": 5, "CharPositionInLine": 0, "kind": "ReferenceType", "ReferencedTypeName": "Letter", "Min": "0", "Max": "25"
    }),
    "value": 25
})
