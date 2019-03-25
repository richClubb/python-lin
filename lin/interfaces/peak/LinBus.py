#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from lin.interfaces.peak.PLinApi import PLinApi, \
HLINCLIENT, HLINHW, \
TLIN_HARDWAREMODE_MASTER, TLIN_ERROR_OK, TLIN_SLOTTYPE_MASTER_REQUEST, TLIN_SLOTTYPE_SLAVE_RESPONSE, \
TLIN_DIRECTION_PUBLISHER, TLIN_CHECKSUMTYPE_CLASSIC, TLIN_CHECKSUMTYPE_ENHANCED, \
FRAME_FLAG_RESPONSE_ENABLE, TLIN_DIRECTION_SUBSCRIBER, TLIN_MSGERROR_OK

from lin.bus import BusABC
from ctypes import *
from threading import Thread
from lin.message import Message
from lin.linTypes import FrameTypes, ChecksumTypes


##
# @brief Currently the code is specific to diagnostic scheduled (pretty much hardcoded at present) - ultimately this needs to be more general.
#
# TODO: well to consider at least - does file need rename to PLinBus??
class LinBus(object):  # ... needs to implement the abstract class ../../bus.py

    __metaclass__ = BusABC
	
    def __init__(self, callback=None, baudrate=19200, **kwargs):   # ... defaulting the params here to values taken from the Python-UDS LIN config.ini file
        self.bus = PLinApi()
        if self.bus is False: raise Exception("PLIN API Not Loaded")

        # Unset handles - set in the register/connection code further down, or via values passed in ...
        self.hClient = HLINCLIENT(0)
        self.hHw = HLINHW(0)
        self.HwMode = TLIN_HARDWAREMODE_MASTER
        self.HwBaudrate = c_ushort(baudrate)

        # Store the reference to the callback function ...
        if callback is None:
            callback = self.__callback_onReceive
        self.__callback = callback

        # necessary to set up the connection
        result = self.bus.RegisterClient("Embed Master", None, self.hClient)
        if result is not TLIN_ERROR_OK: raise Exception("Error registering client")

        self.hHw = HLINHW(1)
        result = self.bus.ConnectClient(self.hClient, self.hHw)
        if result is not TLIN_ERROR_OK: raise Exception("Error connecting client")

        result = self.bus.InitializeHardware(self.hClient, self.hHw, TLIN_HARDWAREMODE_MASTER, self.HwBaudrate)
        if result is not TLIN_ERROR_OK: raise Exception("Error initialising hardware")

        result = self.bus.RegisterFrameId(self.hClient, self.hHw, 0x3C, 0x3D)
        if result is not TLIN_ERROR_OK: raise Exception("Error registering frame id client")
		
		# We're now at a point where we can create the receive thread used for handling responses. The thread itself is
		# started when the schedule is started (nothing to do otherwise).
        self.receiveThread = Thread(group=None, target=self.__receiveFunction, name="Receive Thread")
        self.receiveThreadActive = False

        """
		==================================================================================================================================================
		NOTE: THE following bits are now called when the schedule table frame slots are added - for each frame slot, in the scheduleTable.py module, 
		the addFrame() method further down in this module is called. The addFrame() call, in turn, accesses frame properties to set up the frame and 
		perform the PLinApi SetFrameEntry().
		==================================================================================================================================================
        """
        """ THESE BITS WERE MARKED AS NEEDING TO BE REMOVED IN THE ORIGINAL LinBus.py -  but schedule set up is required from the ldf - move what can be moved
		up to the abstracted LinTp.py in the top directory - 
		THE EQUIV OF ANY SETUP NEEDS TO BE IN THE CALLING APP; in the current test case: in the Python_UDS to set up the diagnostic Schedule
        # configure schedule
        # todo: get this out of the class this is unnecessary - NOTE: the upper wrapper handles schedule adding starting and stoppping 

        ## THESE BITS are now covered by add schedule method ...
        ##masterRequestScheduleSlot = PLinApi.TLINScheduleSlot()
        ##masterRequestScheduleSlot.Type = TLIN_SLOTTYPE_MASTER_REQUEST
        ##masterRequestScheduleSlot.Delay = 10

        ##slaveResponseScheduleSlot = PLinApi.TLINScheduleSlot()
        ##slaveResponseScheduleSlot.Type = TLIN_SLOTTYPE_SLAVE_RESPONSE
        ##slaveResponseScheduleSlot.Delay = 10

        ##diagSchedule = (PLinApi.TLINScheduleSlot * 2)()
        ##diagSchedule[0] = masterRequestScheduleSlot
        #diagSchedule[1] = slaveResponseScheduleSlot

        ## These bits are still to do  - see example at bottom of  LinTp.py (in main section) ...
        masterRequestFrameEntry = PLinApi.TLINFrameEntry()
        masterRequestFrameEntry.FrameId = c_ubyte(0x3C)
        masterRequestFrameEntry.Length = c_ubyte(8)
        masterRequestFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
        masterRequestFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_CLASSIC
        masterRequestFrameEntry.Flags = FRAME_FLAG_RESPONSE_ENABLE
        for i in range(0, 8):
            masterRequestFrameEntry.InitialData[0] = c_ubyte(0)

        slaveResponseFrameEntry = PLinApi.TLINFrameEntry()
        slaveResponseFrameEntry.FrameId = c_ubyte(0x3D)
        slaveResponseFrameEntry.Length = c_ubyte(8)
        slaveResponseFrameEntry.Direction = TLIN_DIRECTION_SUBSCRIBER
        slaveResponseFrameEntry.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_CLASSIC

        slaveResponseFrameEntry = PLinApi.TLINFrameEntry()
        slaveResponseFrameEntry.FrameId = c_ubyte(0x3d)
        slaveResponseFrameEntry.Length = c_ubyte(8)
        slaveResponseFrameEntry.Direction = TLIN_DIRECTION_SUBSCRIBER
        slaveResponseFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED

        result = self.bus.SetFrameEntry(self.hClient, self.hHw, masterRequestFrameEntry)
        result = self.bus.SetFrameEntry(self.hClient, self.hHw, slaveResponseFrameEntry)
        """


    ##
    # @brief assembles the message prior to sending and stores a copy of own message for use when processing any responses
    def transmit(self, payload):
        txPdu = [self.__NAD] + payload
        self.__sendMasterRequest(txPdu)


    ##
    # @brief sends the message over LIN via the low level PLinApi call
    def __sendMasterRequest(self, pdu):
        dataLength = len(pdu)
        data = (c_ubyte * 8)()

        for i in range(0, 8):
            data[i] = c_ubyte(0)

        for i in range(0, dataLength):
            data[i] = c_ubyte(pdu[i])

        self.bus.UpdateByteArray(self.hClient, self.hHw, 0x3C, 0, 8, data)    # ... it would be helpful to replace a lot of the magic numbers  TODO


    ##
    # @brief runs in the receive thread, kicked of in __init__(), to handle receipt of any incoming messages.
    def __receiveFunction(self):
        recvMessage = PLinApi.TLINRcvMsg()

        while(self.receiveThreadActive):
            result = self.bus.Read(self.hClient, recvMessage)
            if result == TLIN_ERROR_OK:
                if recvMessage.ErrorFlags == TLIN_MSGERROR_OK:
                    msg = Message()
                    msg.frameId = recvMessage.FrameId
                    if recvMessage.FrameId == 125:              # ... it would be helpful to replace a lot of the magic numbers  TODO
                        msg.frameId = 0x3D
                    length = recvMessage.Length
                    for i in range(0, length):
                        msg.payload[i] = recvMessage.Data[i]

                    self.__callback(msg, receiveFrameId=msg.frameId) # ... !!!!!!!  where is the correlating sendFrameId? !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    ##
    # @brief called in the receive thread from __receiveFunction() upon successful message receipt, 
    # to process the message and put the result in the buffer for the recv() method.
    # This is a default callback function to trap a missing reference.
    def __callback_onReceive(self, msg, sendFrameId=0x3C, receiveFrameId=0x3D):  # ... defaulting to sending and receiving diagnostic messages
        ##raise NotImplementedError("callback_onReceive function not implemented")

        # This should be overriden (a callback function should be passed to the constructor), but this version will allow some testing, so leaving here for now ...
        msgNad = msg.payload[0]
        msgFrameId = msg.frameId
        print("Received message: frameId={0}".format(msgFrameId))


    ##
    # @brief this function converts the schedule from the python-lin to the bus version
    def addSchedule(self, schedule, index):

        # creates the diagnostic schedule
        diagSchedule = (PLinApi.TLINScheduleSlot * schedule.size)()

        for i in range(schedule.size):
            scheduleSlot = schedule.frameSlots[i]
            outputScheduleSlot = PLinApi.TLINScheduleSlot()

            if scheduleSlot.frameType == FrameTypes.MASTER_REQUEST:
                pass
            elif scheduleSlot.frameType == FrameTypes.SLAVE_RESPONSE:
                pass

            ## set the schedule slot types
            diagSchedule[i] = outputScheduleSlot

        # add the schedule to the hardware
        result = self.bus.SetSchedule(self.hClient, self.hHw, index, diagSchedule, schedule.size)
        if result is not TLIN_ERROR_OK: raise Exception("Error adding schedule table")


    """ 
	I'm not sure if this the right place for this, or if it's correct, but it's a starting point ... needs checking with Richard (TODO)
    """
    ##
    # @brief this function converts the schedule from the python-lin to the bus version
    def addFrame(self, frame):
	    # These bits are still to do  - see example at bottom of  LinTp.py (in main section) ...
        frameEntry = PLinApi.TLINFrameEntry()
        frameEntry.FrameId = frame.frameId
        frameEntry.Length = frame.length
        frameEntry.Direction = TLIN_DIRECTION_PUBLISHER if frame.direction == 'publisher' else TLIN_DIRECTION_SUBSCRIBER
        frameEntry.ChecksumType = TLIN_CHECKSUMTYPE_CLASSIC if frame.checksumType == ChecksumTypes.CLASSIC else TLIN_CHECKSUMTYPE_ENHANCED
        if frame.flags is not None:
            frameEntry.Flags = FRAME_FLAG_RESPONSE_ENABLE # ... this is the only flag I know about at present, so set this if any flag at all is requested!!! Needs a proper solution (TODO)
        frameEntry.InitialData = frame.initialData
        result = self.bus.SetFrameEntry(self.hClient, self.hHw, frameEntry)

    ##
    # @brief this start the indexed schedule (e.g. for Python-UDS use we're typically dealing with index value 1 for the Diagnostic schedule)
    def startSchedule(self, index):
        result = self.bus.StartSchedule(self.hClient, self.hHw, index)
        if result is not TLIN_ERROR_OK: raise Exception("Error registering client: {0}".format(result))

        self.receiveThreadActive = True
        self.receiveThread.start()


    ##
    # @brief this function wakes up the bus
    def wakeupBus(self):
        self.bus.XmtWakeUp(self.hClient, self.hHw)


    ##
    # @brief this function closes the connection to the bus
    def closeConnection(self):

        self.receiveThreadActive = False

        while self.receiveThread.is_alive():
            pass

        self.bus.SuspendSchedule(self.hClient, self.hHw)

        self.bus.ResetHardwareConfig(self.hClient, self.hHw)
        self.bus.RemoveClient(self.hClient)



if __name__ == "__main__":

    from time import time
    connection = LinBus(19200)
    connection.startSchedule(1)  # ... starts the diagnostic schedule (index 1)

    startTime = time()
    sendTime = startTime
    currTime = startTime

    while (currTime - startTime) < 5:

        if (currTime - sendTime) > 1:
            connection.sendMasterRequest([0, 1, 2, 3, 4, 5, 6, 7])
            sendTime = currTime

        currTime = time()

    connection.closeConnection()

