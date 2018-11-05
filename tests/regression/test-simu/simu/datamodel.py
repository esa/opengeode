#!/usr/bin/python

import DV

FVname = "orchestrator"

tc = {}
tm = {}
errCodes = {}

tc["pulse"] = {'nodeTypename': 'MyEnum', 'type': 'ENUMERATED', 'id': 'pulse', 'values':["one", "two", "three", "four", "five"], "valuesInt": {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4}}
tm["telemetry"] = {'nodeTypename': 'MyEnum', 'type': 'ENUMERATED', 'id': 'telemetry', 'values':["one", "two", "three", "four", "five"], "valuesInt": {"one": 0, "two": 1, "three": 2, "four": 3, "five": 4}}
tm["peek_list"] = {'nodeTypename': 'TASTE-Peek-id-list', 'type': 'SEQOF', 'id': 'peek_list', 'minSize': 1, 'maxSize': 10, 'seqoftype':{'nodeTypename': '', 'type': 'INTEGER', 'id': 'peek_list', 'minR': 0, 'maxR': 4294967295}
}
tm["peek_fixed"] = {'nodeTypename': 'FixedIntList', 'type': 'SEQOF', 'id': 'peek_fixed', 'minSize': 3, 'maxSize': 3, 'seqoftype':{'nodeTypename': '', 'type': 'INTEGER', 'id': 'peek_fixed', 'minR': 0, 'maxR': 4294967295}
}
errCodes={1001: {'name': 'T_UInt32', 'constraint': '(0..4294967295)'}, 1002: {'name': 'TASTE_Peek_id', 'constraint': '(0..4294967295)'}, 1003: {'name': 'TASTE_Peek_id_list', 'constraint': '(SIZE(1..10))'}, 1004: {'name': 'FixedIntList', 'constraint': '(SIZE(3))'}, 1005: {'name': 'MyEnum', 'constraint': ''}, 1006: {'name': 'MyEnum_unknown_enumeration_value', 'constraint': ''}, 1007: {'name': 'MySimpleSeq_a', 'constraint': '(0..255)'}, 1008: {'name': 'MySeqOf_elm', 'constraint': '(0..10)'}, 1009: {'name': 'MySeqOf', 'constraint': '(SIZE(1..3))'}, 1010: {'name': 'MySetOf_elm', 'constraint': '(0..10)'}, 1011: {'name': 'MySetOf', 'constraint': '(SIZE(1..3))'}, 1012: {'name': 'MyChoice_b', 'constraint': ''}, 1013: {'name': 'MyChoice_b_unknown_enumeration_value', 'constraint': ''}, 1014: {'name': 'MyChoice_unknown_choice_index', 'constraint': ''}}
