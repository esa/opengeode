#!/usr/bin/env python
''' test script showing how to view the model's internal state '''
from ctypes import *

# load the shared object
test=CDLL('./liborchestrator.so')
test.liborchestratorinit()

get_value=test.fixed_value
get_value.restype = c_char_p
#get_size = test.fixed_size
#get_size.restype = c_long

#size = get_size()
val = get_value()
#print 'size =', size

# We know the size, cast it to an array of bytes that can then be converted to swig
#as_bytes = cast(val, POINTER((c_byte *size)))
#print 'value =', val, as_bytes.contents[0], as_bytes.contents[1]

