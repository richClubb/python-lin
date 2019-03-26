#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from lin.LinBusFactory import LinBusFactory
from lin.bus import BusABC
from ctypes import *
from lin.message import Message
from lin.linTypes import FrameTypes, ChecksumTypes, DeviceTypes, ScheduleTypes, LinTpState, LinTpMessageType
from lin.linTypes import LINTP_MAX_PAYLOAD_LENGTH, N_PCI_INDEX, \
    SINGLE_FRAME_DL_INDEX, SINGLE_FRAME_DATA_START_INDEX, \
    FIRST_FRAME_DL_INDEX_HIGH, FIRST_FRAME_DL_INDEX_LOW, FIRST_FRAME_DATA_START_INDEX, \
    CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX, CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX

# WE don't really want UDS stuff in python-lin, but these are common utilities  
# - copying into both for now (Python-UDS and Python-Lin), until a preferred solution is decided upon
from Utilities.ResettableTimer import ResettableTimer
from Utilities.UtilityFunctions import fillArray


##
# @brief This class provides a LIN transport, with a clearly defined, simple to use interface. The underlying LIN bus is hidden from the app, although this can
# be exposed upon request, if the app requires low-level handling beyond what is provided automatically.
#
# Note: the initial use-case for Python-LIN is diagnostics, so initially there is a leaning towards diagnostic schedule handling, however the project
# is more general, and so must support full LIN communications beyond just the diagnostic schedule (selection of just diagnostics as an option must be
# maintained though).
#
# Note: This module is based on the PEAK/LinBus.py - copied to here to see that any general transport level methods can be kept apart from the lower level bus API impls
# This is still a WIP, although some separation of methods for this level has been made.
class LinTp(object):  # ... needs to implement the abstract class ../../bus.py

    __metaclass__ = BusABC
	
    def __init__(self, nodeAddress=0x01, STMin=0.001, FrameTimeout=1.0, ldf=None, **kwargs):

        # Mostly we'll be setting up the LIN bus with whatever bus specific arguments are required - passed down via kwarg. In addtion, we'll always need to 
        # specify the callback method to receive the returning responses for local buffering and processing (not sure if this is the correct method/syntax - needs testing)
        linBusFactory = LinBusFactory()
        self.__connection = linBusFactory(callback=self.callback_onReceive, **kwargs)
        # ... note: the kwargs will contain the correct bus type, ensuring that we have the correct one selected.

        # NOTE: these bits are either moved down to here from Python-UDS LinTp.py OR need to be retained from the original LinBus.py ....
        self.__maxPduLength = 6

        self.__NAD = nodeAddress #int(nodeAddress, 16)
        self.__STMin = float(STMin)
        self.__FrameTimeout = float(FrameTimeout)
		
        self.__recvBuffer = []
        self.__transmitBuffer = None
		
        self.__ldf = ldf  
        # ... we need to add something at this layer to parse (and process?) the ldf - we need to be setting up whatever schedule is required (or all?) 
        # e.g. in the python-uds use case, we need the diagnostic schedule setting up as transparently as possible !!!!!!!!!!!!!!!!!!!!!!!!!!!
		
        # This is the setup originally in the peak bus constructor - I'm guessing we need something similar but more generic (and driven from the ldf);
        # any low-level calls will need support at the bus module level for each bus type supported ...
        """ NOTE: THESE BITS WERE MARKED AS NEEDING TO BE REMOVED IN THE ORIGINAL LinBus.py -  but schedule set up is required from the ldf - move what can be moved
		up to the abstracted LinTp.py in the top directory - 
		THE EQUIV OF ANY SETUP NEEDS TO BE IN THE CALLING APP; in the current test case: in the Python_UDS to set up the diagnostic Schedule
        # configure schedule
        # todo: get this out of the class this is unnecessary - NOTE: the upper wrapper handles schedule adding starting and stoppping 
        masterRequestScheduleSlot = PLinApi.TLINScheduleSlot()
        masterRequestScheduleSlot.Type = PLinApi.TLIN_SLOTTYPE_MASTER_REQUEST
        masterRequestScheduleSlot.Delay = 10

        slaveResponseScheduleSlot = PLinApi.TLINScheduleSlot()
        slaveResponseScheduleSlot.Type = PLinApi.TLIN_SLOTTYPE_SLAVE_RESPONSE
        slaveResponseScheduleSlot.Delay = 10

        diagSchedule = (PLinApi.TLINScheduleSlot * 2)()
        diagSchedule[0] = masterRequestScheduleSlot
        diagSchedule[1] = slaveResponseScheduleSlot

        masterRequestFrameEntry = PLinApi.TLINFrameEntry()
        masterRequestFrameEntry.FrameId = c_ubyte(0x3C)
        masterRequestFrameEntry.Length = c_ubyte(8)
        masterRequestFrameEntry.Direction = PLinApi.TLIN_DIRECTION_PUBLISHER
        masterRequestFrameEntry.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_CLASSIC
        masterRequestFrameEntry.Flags = PLinApi.FRAME_FLAG_RESPONSE_ENABLE
        for i in range(0, 8):
            masterRequestFrameEntry.InitialData[0] = c_ubyte(0)

        slaveResponseFrameEntry = PLinApi.TLINFrameEntry()
        slaveResponseFrameEntry.FrameId = c_ubyte(0x3D)
        slaveResponseFrameEntry.Length = c_ubyte(8)
        slaveResponseFrameEntry.Direction = PLinApi.TLIN_DIRECTION_SUBSCRIBER
        slaveResponseFrameEntry.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_CLASSIC

        result = self.bus.SetFrameEntry(self.hClient, self.hHw, masterRequestFrameEntry)
        result = self.bus.SetFrameEntry(self.hClient, self.hHw, slaveResponseFrameEntry)
        """
		
		
    # NOTE: anything general to all vendors, shoukd be here. This is a first attempt at getting the split right, but it will be adapted as more bus interfaces
	# are added for different vendors (the current version of this module is based only on the Peak implementation - Vector API is to come).

    ##
    # @brief sends a message over the LIN bus
    def send(self, message):
        payload = message
        payloadLength = len(payload)

        if payloadLength > LINTP_MAX_PAYLOAD_LENGTH:
            raise Exception("Payload too large for CAN Transport Protocol")

        if payloadLength <= self.__maxPduLength:
            state = LinTpState.SEND_SINGLE_FRAME
        else:
            # we might need a check for functional request as we may not be able to service functional requests for
            # multi frame requests
            state = LinTpState.SEND_FIRST_FRAME
            firstFrameData = payload[0:self.__maxPduLength-1]
            cfBlocks = self.__create_blockList(payload[5:])
            sequenceNumber = 1

        txPdu = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        endOfMessage_flag = False

        # Setup the required timers
        timeoutTimer = ResettableTimer(self.__FrameTimeout)
        stMinTimer = ResettableTimer(self.__STMin)

        self.__clearBufferedMessages()

        timeoutTimer.start()
        while endOfMessage_flag is False:
            rxPdu = self.__getNextBufferedMessage()
            if rxPdu is not None:
                raise Exception("Unexpected receive frame")

            if state == LinTpState.SEND_SINGLE_FRAME:
                txPdu[N_PCI_INDEX] += (LinTpMessageType.SINGLE_FRAME << 4)
                txPdu[SINGLE_FRAME_DL_INDEX] += payloadLength
                txPdu[SINGLE_FRAME_DATA_START_INDEX:] = fillArray(payload, self.__maxPduLength)
                self.__transmit(txPdu)
                endOfMessage_flag = True

            elif state == LinTpState.SEND_FIRST_FRAME:
                payloadLength_highNibble = (payloadLength & 0xF00) >> 8
                payloadLength_lowNibble  = (payloadLength & 0x0FF)
                txPdu[N_PCI_INDEX] += (LinTpMessageType.FIRST_FRAME << 4)
                txPdu[FIRST_FRAME_DL_INDEX_HIGH] += payloadLength_highNibble
                txPdu[FIRST_FRAME_DL_INDEX_LOW] += payloadLength_lowNibble
                txPdu[FIRST_FRAME_DATA_START_INDEX:] = firstFrameData
                self.__transmit(txPdu)
                state = LinTpState.SEND_CONSECUTIVE_FRAME
                stMinTimer.start()
                timeoutTimer.restart()

            elif state == LinTpState.SEND_CONSECUTIVE_FRAME:
                if(
                        stMinTimer.isExpired() and
                        (self.__transmitBuffer is None)
                ):
                    txPdu[N_PCI_INDEX] += (LinTpMessageType.CONSECUTIVE_FRAME << 4)
                    txPdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] += sequenceNumber
                    txPdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:] = cfBlocks.pop(0)
                    self.__transmit(txPdu)
                    sequenceNumber = (sequenceNumber + 1) % 16
                    stMinTimer.restart()
                    timeoutTimer.restart()

                    if len(cfBlocks) == 0:
                        endOfMessage_flag = True

            txPdu = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            sleep(0.001)
            if timeoutTimer.isExpired(): raise Exception("Timeout")


    ##
    # @brief creates the blocklist from the blocksize and payload
    def __create_blockList(self, payload):
        blockList = []
        currBlock = []

        payloadLength = len(payload)
        counter = 0

        for i in range(0, payloadLength):

            currBlock.append(payload[i])
            counter += 1

            if counter == self.__maxPduLength:
                blockList.append(currBlock)
                counter = 0
                currBlock = []

        if len(currBlock) is not 0:
            blockList.append(fillArray(currBlock, self.__maxPduLength))

        return blockList

    ##
    # @brief clear out the receive list - used to reset the list when sending to make way for the expected response
    def __clearBufferedMessages(self):
        self.__recvBuffer = []
        self.__transmitBuffer = None

    ##
    # @brief retrieves the next message from the received message buffers - used to check if the buffer is empty when sending, or populated when receiving.
    # @return list, or None if nothing is on the receive list
    def __getNextBufferedMessage(self):
        length = len(self.__recvBuffer)
        if(length != 0):
            return self.__recvBuffer.pop(0)
        else:
            return None


    ##
    # @brief assembles the message prior to sending and stores a copy of own message for use when processing any responses
    def __transmit(self, payload):
        self.__connection.transmit(payload)  # ... dependant of which bus is used, so leave it to the lower level.
        self.__transmitBuffer = txPdu


    ##
    # @brief returns any complete message (may need assembling) from the message buffer if received within the timeout.
    # Note: the message buffer is filled via the receive thread - see __receiveFunction().
    def recv(self, timeout_s):
        timeoutTimer = ResettableTimer(timeout_s)

        payload = []
        payloadPtr = 0
        payloadLength = None

        sequenceNumberExpected = 1

        endOfMessage_flag = False

        state = LinTpState.IDLE

        timeoutTimer.start()
        while endOfMessage_flag is False:

            rxPdu = self.__getNextBufferedMessage()

            if rxPdu is not None:
                N_PCI = (rxPdu[N_PCI_INDEX] & 0xF0) >> 4
                if state == LinTpState.IDLE:
                    if N_PCI == LinTpMessageType.SINGLE_FRAME:
                        payloadLength = rxPdu[N_PCI_INDEX & 0x0F]
                        payload = rxPdu[SINGLE_FRAME_DATA_START_INDEX: SINGLE_FRAME_DATA_START_INDEX + payloadLength]
                        endOfMessage_flag = True
                    elif N_PCI == LinTpMessageType.FIRST_FRAME:
                        payload = rxPdu[FIRST_FRAME_DATA_START_INDEX:]
                        payloadLength = ((rxPdu[FIRST_FRAME_DL_INDEX_HIGH] & 0x0F) << 8) + rxPdu[
                            FIRST_FRAME_DL_INDEX_LOW]
                        payloadPtr = self.__maxPduLength - 1
                        state = LinTpState.RECEIVING_CONSECUTIVE_FRAME
                        timeoutTimer.restart()
                elif state == LinTpState.RECEIVING_CONSECUTIVE_FRAME:
                    if N_PCI == LinTpMessageType.CONSECUTIVE_FRAME:
                        sequenceNumber = rxPdu[CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX] & 0x0F
                        if sequenceNumber != sequenceNumberExpected:
                            raise Exception("Consecutive frame sequence out of order")
                        else:
                            sequenceNumberExpected = (sequenceNumberExpected + 1) % 16
                        payload += rxPdu[CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX:]
                        payloadPtr += (self.__maxPduLength)
                        timeoutTimer.restart()
                    else:
                        raise Exception("Unexpected PDU received")

            if payloadLength is not None:
                if payloadPtr >= payloadLength:
                    endOfMessage_flag = True

            if timeoutTimer.isExpired():
                raise Exception("Timeout in waiting for message")

        return list(payload[:payloadLength])


    ##
    # @brief called in the receive thread from __receiveFunction() upon successful message receipt, to process the message and put the result in the buffer for the recv() method.
    def callback_onReceive(self, msg, sendFrameId=0x3C, receiveFrameId=0x3D):  # ... defaulting to sending and receiving diagnostic messages (0x3C - master request frame used for diagnostics)
        msgNad = msg.payload[0]
        msgFrameId = msg.frameId
        #print("Received message: frameId={0}".format(msgFrameId))

        if msgNad == self.__NAD:
            if msgFrameId == sendFrameId:                             # ... it would be helpful to replace a lot of the magic numbers  - 0x3C/0x3D are the special diagnostic send/recv frame ids
                if msg.payload == self.__transmitBuffer:
                    self.__transmitBuffer = None

            elif msgFrameId == receiveFrameId or 125:                 # ... 125?
                self.__recvBuffer.append(msg.payload[1:8])


    ##
    # @brief this function converts the schedule from the python-lin to the bus version
    # Note: the bus selected may or may not support this!
    def addSchedule(self, schedule, index):
        self.__connection.addSchedule(schedule, index)  # ... dependant of which bus is used, so leave it to the lower level.


    ##
    # @brief this function allows frame entries to be added at the bus level
    # Note: the bus selected may or may not support this!
    def addFrame(self, frame):
        self.__connection.addFrame(frame)  # ... dependant of which bus is used, so leave it to the lower level.


    ##
    # @brief this starts the indexed schedule (e.g. for Python-UDS use we're typically dealing with index value 1 for the Diagnostic schedule)
    # Note: the bus selected may or may not support this!
    def startSchedule(self, index):
        self.__connection.startSchedule(index)  # ... dependant of which bus is used, so leave it to the lower level.


    ##
    # @brief this pauses the indexed schedule (e.g. for Python-UDS use we're typically dealing with index value 1 for the Diagnostic schedule)
    # Note: the bus selected may or may not support this!
    def pauseSchedule(self, index):
        self.__connection.pauseSchedule(index)  # ... dependant of which bus is used, so leave it to the lower level.


    ##
    # @brief this stops the indexed schedule (e.g. for Python-UDS use we're typically dealing with index value 1 for the Diagnostic schedule)
    # Note: the bus selected may or may not support this!
    def stopSchedule(self, index):
        self.__connection.stopSchedule(index)  # ... dependant of which bus is used, so leave it to the lower level.


    ##
    # @brief this function wakes up the bus
    # Note: the bus selected may or may not support this!
    def wakeupBus(self):
        self.__connection.wakeupBus()  # ... dependant of which bus is used, so leave it to the lower level.



    ##
    # @brief this function closes the connection to the bus
    # Note: the bus selected may or may not support this!
    def closeConnection(self):
        self.__connection.closeConnection()  # ... dependant of which bus is used, so leave it to the lower level.



if __name__ == "__main__":

    from time import time
    connection = LinTp(linBusType="Peak",baudrate=19200) # ... linBusType is passed through in kwargs

    from scheduleTable import ScheduleTable
    from frame import Frame

    # Test 1: use diagnostic entry from an ldf file ...	
    #schedule = ScheduleTable(transport=connection, ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf", diagnostic_schedule=True)
	
    # Test 2: create a diagnostic entry without having an ldf file ...	
    schedule = ScheduleTable(transport=connection, schedule_name="SecurityLIN_Diag", index=1, diagnostic_schedule=True)
    schedule.addFrameSlot(frame=Frame(frame_name='MasterReq',delay=10, frame_id=0x3c, checksumType='classic'))
    schedule.addFrameSlot(frame=Frame(frame_name='SlaveResp',delay=10, frame_id=0x3d, checksumType='classic'))

    # Dump details for the created schedule/frameSlots ...	
    print(("scheduleName:",schedule.scheduleName))
    print("")
    print(("scheduleIndex:",schedule.scheduleIndex))
    print("")
    print(("size:",schedule.size))
    print("")
    for entry in schedule.frameSlots:
        print(("frameName:",entry.frameName,"frameId:",entry.frameId,"delay:",entry.delay,"checktype:",entry.checksumType))
			
    schedule.start()  # ... this now does an implicit add, so no need for that any more
	
    """
	We still need the equivalent of the following from the orig master branch LinBus.py code ..
	These need to be back in LinBus, but vai a method call rather than embedded in the __init__ function, as we may to initiliase any frames, not just these - not sure where they fit - talk to Richard (TODO)
	
The following frame entries are used in the GetFrameEntry() and SetFrameEntry() calls to PLinApi.py - currently we only call SetFrameEntry() in the example calls below (not anywhere else ...

This is a PEAK specific setup of a message frame for sending ....
	    # These bits are still to do  - see example at bottom of  LinTp.py (in main section) ...
        masterRequestFrameEntry = PLinApi.TLINFrameEntry()
        masterRequestFrameEntry.FrameId = c_ubyte(0x3C)
        masterRequestFrameEntry.Length = c_ubyte(8)
        masterRequestFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
        masterRequestFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_CLASSIC
        masterRequestFrameEntry.Flags = FRAME_FLAG_RESPONSE_ENABLE
        for i in range(0, 8):
            masterRequestFrameEntry.InitialData[0] = c_ubyte(0)

This is a PEAK specific setup of a message frame for sending ....
        slaveResponseFrameEntry = PLinApi.TLINFrameEntry()
        slaveResponseFrameEntry.FrameId = c_ubyte(0x3D)
        slaveResponseFrameEntry.Length = c_ubyte(8)
        slaveResponseFrameEntry.Direction = TLIN_DIRECTION_SUBSCRIBER
        slaveResponseFrameEntry.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_CLASSIC

These are the calls that take the above created frame details and set them for use ...
        result = self.bus.SetFrameEntry(self.hClient, self.hHw, masterRequestFrameEntry)
        result = self.bus.SetFrameEntry(self.hClient, self.hHw, slaveResponseFrameEntry)
    """
	

    """ TEST CODE FROM LinTp.py currently commented out as the code is being changed ...
    connection.startSchedule(1)  # ... starts the diagnostic schedule (index 1)

    startTime = time()
    sendTime = startTime
    currTime = startTime

    while (currTime - startTime) < 5:

        if (currTime - sendTime) > 1:
            connection.send([0, 1, 2, 3, 4, 5, 6, 7])
            sendTime = currTime

        currTime = time()
    """
    connection.closeConnection()

