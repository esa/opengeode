from __future__ import absolute_import


import threading, time, sys, os, ctypes

import DV
try:
    PythonAccess = ctypes.cdll.LoadLibrary("./PythonAccess.so")
except OSError:
    folder = os.path.dirname(os.path.abspath(__file__))
    PythonAccess = ctypes.cdll.LoadLibrary(folder + "/PythonAccess.so")
    sys.path.append(folder)
OpenMsgQueueForReading = PythonAccess.OpenMsgQueueForReading
OpenMsgQueueForReading.restype = ctypes.c_int
CloseMsgQueue =  PythonAccess.CloseMsgQueue
GetMsgQueueBufferSize = PythonAccess.GetMsgQueueBufferSize
GetMsgQueueBufferSize.restype = ctypes.c_int
RetrieveMessageFromQueue = PythonAccess.RetrieveMessageFromQueue
RetrieveMessageFromQueue.restype = ctypes.c_int
i_pulse = ctypes.c_int.in_dll(PythonAccess, "ii_pulse").value
SendTC_pulse = PythonAccess.SendTC_pulse
import dataview_uniq_asn
i_telemetry = ctypes.c_int.in_dll(PythonAccess, "ii_telemetry").value
i_peek_list = ctypes.c_int.in_dll(PythonAccess, "ii_peek_list").value
i_peek_fixed = ctypes.c_int.in_dll(PythonAccess, "ii_peek_fixed").value


def Invoke_pulse(var_MyEnum):
    if -1 == SendTC_pulse(var_MyEnum._ptr):
        print 'Failed to send TC: pulse...\n'
        raise IOError("pulse")
class Poll_orchestrator(threading.Thread):
    def run(self):
        self._bDie = False
        while True:
            if self._bDie:
                return
            self._msgQueue = OpenMsgQueueForReading(str(os.geteuid()) + "_orchestrator_PI_Python_queue")
            if (self._msgQueue != -1): break
            print "Communication channel over %d_orchestrator_PI_Python_queue not established yet...\n" % os.geteuid()
            time.sleep(1)
        bufferSize = GetMsgQueueBufferSize(self._msgQueue)
        self._pMem = ctypes.create_string_buffer(bufferSize).raw
        while not self._bDie:
            self.messageReceivedType = RetrieveMessageFromQueue(self._msgQueue, bufferSize, self._pMem)
            if self.messageReceivedType == -1:
                time.sleep(0.01)
                continue
            ProcessTM(self)

def ProcessTM(self):
    if self.messageReceivedType == i_telemetry:
        print "\n"+chr(27)+"[32m" + "Received Telemetry: telemetry" + chr(27) + "[0m\n"
        backup = self._pMem
        # Read the data for param telemetry_param
        var_telemetry_param = dataview_uniq_asn.MyEnum()
        var_telemetry_param.SetData(self._pMem)
        print "Parameter telemetry_param:"
        var_telemetry_param.PrintAll()
        print
        # self._pMem = DV.MovePtrBySizeOf_MyEnum(self._pMem)
        # Revert the pointer to start of the data
        self._pMem = backup
    if self.messageReceivedType == i_peek_list:
        print "\n"+chr(27)+"[32m" + "Received Telemetry: peek_list" + chr(27) + "[0m\n"
        backup = self._pMem
        # Read the data for param peek_list_param
        var_peek_list_param = dataview_uniq_asn.TASTE_Peek_id_list()
        var_peek_list_param.SetData(self._pMem)
        print "Parameter peek_list_param:"
        var_peek_list_param.PrintAll()
        print
        # self._pMem = DV.MovePtrBySizeOf_TASTE_Peek_id_list(self._pMem)
        # Revert the pointer to start of the data
        self._pMem = backup
    if self.messageReceivedType == i_peek_fixed:
        print "\n"+chr(27)+"[32m" + "Received Telemetry: peek_fixed" + chr(27) + "[0m\n"
        backup = self._pMem
        # Read the data for param peek_fixed_param
        var_peek_fixed_param = dataview_uniq_asn.FixedIntList()
        var_peek_fixed_param.SetData(self._pMem)
        print "Parameter peek_fixed_param:"
        var_peek_fixed_param.PrintAll()
        print
        # self._pMem = DV.MovePtrBySizeOf_FixedIntList(self._pMem)
        # Revert the pointer to start of the data
        self._pMem = backup

if __name__ == "__main__":
    poll_orchestrator = Poll_orchestrator()
    poll_orchestrator.start()
    try:
        time.sleep(1e8)
    except:
        poll_orchestrator._bDie = True
        poll_orchestrator.join()