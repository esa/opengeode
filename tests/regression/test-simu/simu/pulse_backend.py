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

tcId = -1
msgQ = False
udp = False
shared_lib = False
ASN1_AST = None # Set by Scenario.py - point to the ASN.1 AST from Python.stg

# Variable containing a signal that is used to send a message via a dll
send_via_dll = None

try:
    import PythonController
except ImportError:
    pass

# External configuration point - user must select between message queues,
# UDP or shared libraries for exchanging messages with the main binary

def setMsgQ():
    global tcId
    global msgQ
    tcId = PythonController.i_pulse
    msgQ = True


def setUDP():
    global udp
    global tcId
    from _InterfaceEnum import i_orchestrator_RI_pulse
    tcId = i_orchestrator_RI_pulse
    udp = True


def setSharedLib(dll=None):
    # The shared library is loaded and initialized by the caller
    global shared_lib
    global pulse_via_shared_lib
    shared_lib = True
    pulse_via_shared_lib = dll.orchestrator_pulse


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
    buffer = ASN1.DataStream(DV.MyEnum_REQUIRED_BYTES_FOR_ACN_ENCODING)

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
    buffer = ASN1.DataStream(DV.MyEnum_REQUIRED_BYTES_FOR_ACN_ENCODING)
    buffer.SetFromPyString(ACN_encodedBuffer)
    decoded_value = ASN1.MyEnum()
    decoded_value.DecodeACN(buffer)
    return decoded_value


def encode_uPER(asnVal):
    ''' Encode the native Asn1Scc structure in uPER '''

    # Check the ASN.1 constraints:
    if not checkConstraints(asnVal): return

    # Create a stream buffer to host the UPER encoded data (for saving to file)
    buffer = ASN1.DataStream(DV.MyEnum_REQUIRED_BYTES_FOR_ENCODING)

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
    buffer = ASN1.DataStream(DV.MyEnum_REQUIRED_BYTES_FOR_ENCODING)
    buffer.SetFromPyString(uPER_encodedBuffer)
    decoded_value = ASN1.MyEnum()
    decoded_value.Decode(buffer)
    return decoded_value



def send_pulse_VN(tc_gser):
    ''' Send the TC with from input parameter in ASN.1 Value Notation '''
    instance = typeInstance()
    vn.valueNotationToCTypes(gser=tc_gser,
                             dest=instance,
                             sort=ASN1_AST['MyEnum'].type,
                             ASN1Mod=ASN1,
                             ASN1_AST=ASN1_AST)

    sendTC(instance)


def sendTC(tc):
    ''' Depending on the configuration, send to msgQ, UDP or shared lib '''
    # tc is a ctypes instance of an ASN.1 type
    if msgQ:
        if checkConstraints(tc):
            try:
                PythonController.Invoke_pulse(tc)
            except IOError:
                raise
    elif udp:
        UPER_TC = encode_uPER(tc)
        if UPER_TC and udpController:
            udpController.UDP_Invoke(tcId, UPER_TC)
        else:
            if log:
                log.error('UPER Encoding or UDP Sending failed')
            else:
                print '[ERROR] UPER Encoding or UDP Sending failed'

    elif shared_lib:
        # TC is sent in native format
        # ptr = ctypes.cast(tc._ptr.__long__(), ctypes.POINTER(ctypes.c_long))
        # pulse_via_shared_lib(ptr)
        # The call to the dll will be done by the SDL handler that manages
        # the Undo stack and the the overal system state
        send_via_dll.dll.emit("pulse",
                              pulse_via_shared_lib,
                              tc)


def fromPysideToASN1(_):
    print('DEPRECATED call to "fromPysideToASN1"')
    # Create a native ASN.1 variable of type MyEnum
    # pulse = ASN1.MyEnum()
    return None

def typeInstance():
    # Create an intance of an ASN.1 ctype
    return ASN1.MyEnum()


def fromASN1ToPyside(_):
    print('DEPRECATED call to "fromASN1ToPyside"')
    return None
