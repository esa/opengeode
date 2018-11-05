from functools import partial

import DV

from Stubs import (
    myassert, Clean, DataStream, COMMON)

class T_UInt32(COMMON):
    def __init__(self, ptr=None):
        super(T_UInt32, self).__init__("T_UInt32", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append(""+str(self.Get()))

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class TASTE_Peek_id(COMMON):
    def __init__(self, ptr=None):
        super(TASTE_Peek_id, self).__init__("TASTE_Peek_id", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append(""+str(self.Get()))

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class TASTE_Peek_id_list(COMMON):
    def __init__(self, ptr=None):
        super(TASTE_Peek_id_list, self).__init__("TASTE_Peek_id_list", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append("{")
        def emitElem(path, i):
            state = self.GetState()
            if i > 0:
                lines.append(",")
            lines.append(" "+str(path[i].Get()))
            self.Reset(state)
        state = self.GetState()
        length = self.GetLength()
        self.Reset(state)
        map(partial(emitElem, self), range(length))
        self.Reset(state)
        lines.append("}")

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class MySetOf(COMMON):
    def __init__(self, ptr=None):
        super(MySetOf, self).__init__("MySetOf", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append("{")
        def emitElem(path, i):
            state = self.GetState()
            if i > 0:
                lines.append(",")
            lines.append(" "+str(path[i].Get()))
            self.Reset(state)
        state = self.GetState()
        length = self.GetLength()
        self.Reset(state)
        map(partial(emitElem, self), range(length))
        self.Reset(state)
        lines.append("}")

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class MySimpleSeq(COMMON):
    # Ordered list of fields:
    children_ordered = ['a', 'b', 'c']

    def __init__(self, ptr=None):
        super(MySimpleSeq, self).__init__("MySimpleSeq", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append("{")
        lines.append("a ")
        lines.append(" "+str(self.a.Get()))
        lines.append(', ')
        lines.append("b ")
        lines.append(" "+str(self.b.Get()!=0).upper())
        lines.append(', ')
        lines.append("c ")
        lines.append(" "+{'1': 'two', '3': 'four', '2': 'three', '0': 'one', '4': 'five'}[str(self.c.Get())])
        lines.append("}")

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class FixedIntList(COMMON):
    def __init__(self, ptr=None):
        super(FixedIntList, self).__init__("FixedIntList", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append("{")
        def emitElem(path, i):
            state = self.GetState()
            if i > 0:
                lines.append(",")
            lines.append(" "+str(path[i].Get()))
            self.Reset(state)
        state = self.GetState()
        length = self.GetLength()
        self.Reset(state)
        map(partial(emitElem, self), range(length))
        self.Reset(state)
        lines.append("}")

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class MySeq(COMMON):
    # Ordered list of fields:
    children_ordered = ['a', 'b']

    def __init__(self, ptr=None):
        super(MySeq, self).__init__("MySeq", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append("{")
        lines.append("a ")
        lines.append(" "+str(self.a.Get()!=0).upper())
        lines.append(', ')
        lines.append("b ")
        if self.b.kind.Get() == DV.a_PRESENT:
         lines.append(" a: ")
         lines.append("  "+str(self.b.a.Get()!=0).upper())
        if self.b.kind.Get() == DV.b_PRESENT:
         lines.append(" b: ")
         lines.append("  "+{'1': 'bb', '0': 'aa'}[str(self.b.b.Get())])
        lines.append("}")

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class MyChoice(COMMON):
    def __init__(self, ptr=None):
        super(MyChoice, self).__init__("MyChoice", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        if self.kind.Get() == DV.a_PRESENT:
         lines.append("a: ")
         lines.append(" "+str(self.a.Get()!=0).upper())
        if self.kind.Get() == DV.b_PRESENT:
         lines.append("b: ")
         lines.append(" "+{'1': 'bb', '0': 'aa'}[str(self.b.Get())])

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class MyEnum(COMMON):
    # Allowed enumerants:
    one = 0
    two = 1
    three = 2
    four = 3
    five = 4
    allowed = [one, two, three, four, five]
    def __init__(self, ptr=None):
        super(MyEnum, self).__init__("MyEnum", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append(""+{'1': 'two', '3': 'four', '2': 'three', '0': 'one', '4': 'five'}[str(self.Get())])

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


class MySeqOf(COMMON):
    def __init__(self, ptr=None):
        super(MySeqOf, self).__init__("MySeqOf", ptr)

    def GSER(self):
        ''' Return the GSER representation of the value '''
        lines = []
        lines.append("{")
        def emitElem(path, i):
            state = self.GetState()
            if i > 0:
                lines.append(",")
            lines.append(" "+str(path[i].Get()))
            self.Reset(state)
        state = self.GetState()
        length = self.GetLength()
        self.Reset(state)
        map(partial(emitElem, self), range(length))
        self.Reset(state)
        lines.append("}")

        return ' '.join(lines)

    def PrintAll(self):
        ''' Display a variable of this type '''
        print(self.GSER() + '\n')


