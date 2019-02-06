
# THIS IS CURRENTLY A COPY OF PEAK/LinBus.py - copied to here see that any general transport level methods can be kept apart from the lower level bus API impls
# THIS IS A WIP - only just looking at this and considering at present!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from lin import PLinApi
from lin.bus import BusABC
from ctypes import *
from threading import Thread
from lin.message import Message
from lin.linTypes import FrameTypes, ChecksumTypes, DeviceTypes, ScheduleTypes, LinTpState, LinTpMessageType
from lin.linTypes import LINTP_MAX_PAYLOAD_LENGTH, N_PCI_INDEX, \
    SINGLE_FRAME_DL_INDEX, SINGLE_FRAME_DATA_START_INDEX, \
    FIRST_FRAME_DL_INDEX_HIGH, FIRST_FRAME_DL_INDEX_LOW, FIRST_FRAME_DATA_START_INDEX, \
    CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX, CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX

# WE don't really want UDS stuff in python-lin, but these are common utilities  
# - copying into both for now (Python-UDS and Python-Lin), until a preferred solution is decided upon
from lin import ResettableTimer
from lin import fillArray


# todo: file needs rename to PLinBus
class LinTp(object):  # ... needs to implement the abstract class ../../bus.py

    __metaclass__ = BusABC
	
    def __init__(self, **kwargs):

	    self.__connection = LinBusFactory.LinBusFactory(**kwargs)
		
		"""
        self.bus = PLinApi.PLinApi()
        if self.bus is False: raise Exception("PLIN API Not Loaded")

        # Unset handles - set in the register/connection code further down, or via values passed in ...
        self.hClient = PLinApi.HLINCLIENT(0)
        self.hHw = PLinApi.HLINHW(0)
        self.HwMode = PLinApi.TLIN_HARDWAREMODE_MASTER
        self.HwBaudrate = c_ushort(baudrate)

        # necessary to set up the connection
        result = self.bus.RegisterClient("Embed Master", None, self.hClient)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error registering client")

        self.hHw = PLinApi.HLINHW(1)
        result = self.bus.ConnectClient(self.hClient, self.hHw)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error connecting client")

        result = self.bus.InitializeHardware(self.hClient, self.hHw, PLinApi.TLIN_HARDWAREMODE_MASTER, self.HwBaudrate)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error initialising hardware")

        result = self.bus.RegisterFrameId(self.hClient, self.hHw, 0x3C, 0x3D)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error registering frame id client")

		# NOTE: these bits are either moved down to here from Python-UDS LinTp.py OR need to be retained from the original LinBus.py ....
        self.__maxPduLength = 6

        self.__NAD = int(nodeAddress, 16)
        self.__STMin = float(STMin)
        self.__FrameTimeout = float(FrameTimeout)
		
        self.__recvBuffer = []
        self.__transmitBuffer = None
		
		# We're now at a point where we can create the receive thread used for handling responses. The thread itself is
		# started when the schedule is started (nothing to do otherwise).
        self.receiveThread = Thread(group=None, target=self.__receiveFunction, name="Receive Thread")
        self.receiveThreadActive = False
		"""

        """ NOTE: THESE BITS WERE MARKED AS NEEDING TO BE REMOVED IN THE ORIGINAL LinBus.py -
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
		
    """
    ##
    # @brief a method exposing the LIN connection in case any lower level handling is required in the app(e.g. direct calls to any of the LIN API methods not relevant to UDS).
    def linBus(self):
        return self.__connection

    ##
    # @brief sends a message (via an active LIN Schedule) if supported by the chosen Vendor. Required for UDS operation.
    def send(self, payload):
        self.__connection.send(payload)

    ##
    # @brief returns a response (in response to a send call - see above) if supported by the chosen Vendor. Required for UDS operation.
    def recv(self, timeout_s):
        return self.__connection.recv(... can pass timeout from here if required ...)  # .... implemented in the LIN bus impl, so the rest of function replaced by this

    ##
    # @brief adds a Schedule at the specified index if supported by the chosen Vendor. Exposed to allow customised control of the LIN bus.
    def addSchedule(self, schedule, scheduleIndex):
        self.__connection.addSchedule(schedule, scheduleIndex)

    ##
    # @brief starts the indexed Schedule if supported by the chosen Vendor. Exposed to allow customised control of the LIN bus.
    def startSchedule(self, scheduleIndex):
        self.__connection.startSchedule(scheduleIndex)

    ##
    # @brief pauses the indexed Schedule if supported by the chosen Vendor. Exposed to allow customised control of the LIN bus.
    def pauseSchedule(self, scheduleIndex):
        self.__connection.pauseSchedule(scheduleIndex)

    ##
    # @brief stops the indexed Schedule if supported by the chosen Vendor. Exposed to allow customised control of the LIN bus.
    def stopSchedule(self, scheduleIndex):
        self.__connection.stopSchedule(scheduleIndex)

    ##
    # @brief Wakes up the LIN bus if supported by the chosen Vendor. Exposed to allow customised control of the LIN bus.
    def wakeupBus(self):
        self.__connection.wakeupBus()

    ##
    # @brief Closes the connection if supported by the chosen Vendor. Exposed to allow customised control of the LIN bus.
    def closeConnection(self):
        self.__connection.closeConnection()
	"""

    """
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	ANYTHING higher level that fits in here, can go in the above methods supported. Anything bus level/vendor specific stays below!!!!
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	THE FOLLOWING IS CURRENTLY STILL JUST A COPY OF LinBus.py
	"""

    #????????????????????????????????????????? copied the higher level methods amongst the following down from LinTP.py in UDS, 
    # as we need the send and recv function here to fit the abstracted interface.

    # NOTE: some of this is general to all vendors, so can be moved up to an abstracted wrapper????????????????????
	# also some bits more TP and some more Bus, so a natural split - it's just that TP in the UDS looked too high up.
    # We probably need to see how the Vector API starts working out first.

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
        txPdu = [self.__NAD] + payload
        self.__sendMasterRequest(txPdu)
        self.__transmitBuffer = txPdu

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
    # @brief runs in the receive thread, kicked of in __init__(), to handle receipt of any incoming messages.
    def __receiveFunction(self):
        recvMessage = PLinApi.TLINRcvMsg()

        while(self.receiveThreadActive):
            result = self.bus.Read(self.hClient, recvMessage)
            if result == PLinApi.TLIN_ERROR_OK:
                if recvMessage.ErrorFlags == PLinApi.TLIN_MSGERROR_OK:
                    msg = Message()
                    msg.frameId = recvMessage.FrameId
                    if recvMessage.FrameId == 125:              # ... it would be helpful to replace a lot of the magic numbers  TODO
                        msg.frameId = 0x3D
                    length = recvMessage.Length
                    for i in range(0, length):
                        msg.payload[i] = recvMessage.Data[i]

                    self.__callback_onReceive(msg)

    ##
    # @brief called in the receive thread from __receiveFunction() upon successful message receipt, to process the message and put the result in the buffer for the recv() method.
    def __callback_onReceive(self, msg):
        msgNad = msg.payload[0]
        msgFrameId = msg.frameId
        #print("Received message: frameId={0}".format(msgFrameId))

        if msgNad == self.__NAD:
            if msgFrameId == 0x3C:                             # ... it would be helpful to replace a lot of the magic numbers  TODO
                if msg.payload == self.__transmitBuffer:
                    self.__transmitBuffer = None

            elif msgFrameId == 0x3D or 125:
                self.__recvBuffer.append(msg.payload[1:8])


    ##
    # @brief this start the indexed schedule (e.g. for Python-UDS use we're typically dealing with index value 1 for the Diagnostic schedule)
    def startSchedule(self, index):
        result = self.bus.StartSchedule(self.hClient, self.hHw, index)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error registering client")

        self.receiveThreadActive = True
        self.receiveThread.start()


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
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error adding schedule table")


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

