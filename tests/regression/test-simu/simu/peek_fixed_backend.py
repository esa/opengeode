#!/usr/bin/python

import sys
import ctypes
import Queue
import datamodel
import DV
import Stubs
try:
    import vn
    import asn1_python
except ImportError:
    # Support both the old and new installation schemes
    from asn1_value_editor import vn, asn1_python

import dataview_uniq_asn as ASN1

# Optional GUI panel for this message - used to forward received TMs
editor = None


tmId = -1
shared_lib = None

# Class configured by the GUI with a signal to be emitted when a TM is received
tm_callback = None

try:
    import PythonController
except:
    pass

def setMsgQ():
    global tmId
    tmId = PythonController.i_peek_fixed


def setUDP():
    global tmId
    from _InterfaceEnum import i_orchestrator_PI_peek_fixed
    tmId = i_orchestrator_PI_peek_fixed


def peek_fixed(tm_ptr, size):
    """ Callback function when receiving this TM (opengeode-simulator) """
    if editor:
        editor.asn1Instance.SetData(tm_ptr)
        editor.pendingTM = True
        tm_callback.got_tm.emit()


# Callback function prototype - a void* param, and returning nothing
func = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_long)
cmp_func = func(peek_fixed)

def setSharedLib(dll=None):
    # The shared library is loaded and initialized by the caller
    global shared_lib
    shared_lib = dll
    dll.register_peek_fixed(cmp_func)


log = None
statusbar = None
udpController = None


def checkConstraints(asnVal):
    ''' Check if the ASN.1 constraints are respected '''
    # asnVal input is a ctypes instance of an ASN.1 type
    isValid, errCode = asnVal.IsConstraintValid()
    if not isValid:
        errorMsg = datamodel.errCodes[errCode]['name'] + ': Constraint error! Constraint is: ' + datamodel.errCodes[errCode]['constraint']
        if log:
            log.error(errorMsg)
        return False
    else:
        return True


def encode_ACN(asnVal):
    ''' Encore the native Asn1Scc structure in ACN '''

    # Check the ASN.1 constraints:
    if not checkConstraints(asnVal):
        return

    # Create a stream buffer to host the ACN-encoded data (for saving to file)
    buffer = ASN1.DataStream(DV.FixedIntList_REQUIRED_BYTES_FOR_ACN_ENCODING)

    try:
        # Encode the value into the buffer
        asnVal.EncodeACN(buffer)
    except:
        if log:
            log.error('ACN Encoding failed')
        return

    return buffer.GetPyString()


def decode_ACN(ACN_encodedBuffer):
    ''' Decode an ACN buffer and place it in a native Asn1Scc type  '''

    # Create a stream buffer, put the encoded data inside it, and decode from it
    buffer = ASN1.DataStream(DV.FixedIntList_REQUIRED_BYTES_FOR_ACN_ENCODING)
    buffer.SetFromPyString(ACN_encodedBuffer)
    decoded_value = ASN1.FixedIntList()
    decoded_value.DecodeACN(buffer)
    return decoded_value


def encode_uPER(asnVal):
    ''' Encode the native Asn1Scc structure in uPER '''

    # Check the ASN.1 constraints:
    if not checkConstraints(asnVal): return

    # Create a stream buffer to host the UPER encoded data (for saving to file)
    buffer = ASN1.DataStream(DV.FixedIntList_REQUIRED_BYTES_FOR_ENCODING)

    try:
        # Encode the value into the buffer
        asnVal.Encode(buffer)
    except:
        if log:
            log.error('uPER encoding failed')
        else:
            print '[ERROR] uPER encoding failed'
        return

    return buffer.GetPyString()


def decode_uPER(uPER_encodedBuffer):
    ''' Decode an uPER buffer and place it in a native Asn1Scc type  '''

    # Create a stream buffer, put the encoded data inside it, and decode it
    buffer = ASN1.DataStream(DV.FixedIntList_REQUIRED_BYTES_FOR_ENCODING)
    buffer.SetFromPyString(uPER_encodedBuffer)
    decoded_value = ASN1.FixedIntList()
    decoded_value.Decode(buffer)
    return decoded_value


def decode_TM(rawTM):
    ''' Decode a msgQ message (native encoding) '''
    tm = ASN1.FixedIntList()
    tm.SetData(rawTM)
    return tm


def expect(Q, VNvalue, ignoreOther=False, timeout=None):
    ''' Wait for a specific message - optionally ignoring others '''
    while True:
        try:
            (msgId, pDataFromMQ) = Q.get(block=True, timeout=timeout)
        except Queue.Empty:
            # Timeout expired
            raise IOError('Timeout expired')
        if msgId == tmId:
            #expectedValue = '{ peek-fixed ' + VNvalue + ' }'
            expectedValue = VNvalue
            nativeData = decode_TM(pDataFromMQ)
            receivedValue = nativeData.GSER()
            if asn1_python.compareVnValues(receivedValue, expectedValue):
                Q.task_done()
                return
            else:
                Q.task_done()
                raise ValueError('Received peek-fixed with wrong data: '+ vn.format_gser(receivedValue))
        elif not ignoreOther:
            Q.task_done()
            raise TypeError(
                "Expected peek-fixed (%s), but received other (%s)" % (str(tmId), str(msgId)))
        else:
            print 'Received other (%s), but still waiting for peek-fixed' % str(msgId)
            Q.task_done()


def fromPysideToASN1(_):
    print('DEPRECATED call to "fromPysideToASN1"')
    # Create a native ASN.1 variable of type FixedIntList
    # peek_fixed = ASN1.FixedIntList()
    return None

def typeInstance():
    # Create an intance of an ASN.1 ctype
    return ASN1.FixedIntList()


def fromASN1ToPyside(_):
    print('DEPRECATED call to "fromASN1ToPyside"')
    return None
