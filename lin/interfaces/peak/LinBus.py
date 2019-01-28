from lin import PLinApi
from ctypes import *
from threading import Thread


class LinMessage(object):

    def __init__(self):

        self.frameId = 0
        self.protectedId = 0
        self.payload = [0, 0, 0, 0, 0, 0, 0, 0]


class LinBus(object):

    def __init__(self, baudrate):

        self.bus = PLinApi.PLinApi()
        if self.bus is False: raise Exception("PLIN API Not Loaded")

        self.hClient = PLinApi.HLINCLIENT(0)
        self.hHw = PLinApi.HLINHW(0)
        self.HwMode = PLinApi.TLIN_HARDWAREMODE_MASTER
        self.HwBaudrate = c_ushort(baudrate)

        result = self.bus.RegisterClient("Embed Master", None, self.hClient)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error registering client")

        self.hHw = PLinApi.HLINHW(1)
        result = self.bus.ConnectClient(self.hClient, self.hHw)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error connecting client")

        result = self.bus.InitializeHardware(self.hClient, self.hHw, PLinApi.TLIN_HARDWAREMODE_MASTER, self.HwBaudrate)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error initialising hardware")

        result = self.bus.RegisterFrameId(self.hClient, self.hHw, 0x3C, 0x3D)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error registering frame id client")

        # configure schedule
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

        result = self.bus.SetSchedule(self.hClient, self.hHw, 1, diagSchedule, 2)

        self.receiveThread = Thread(group=None, target=self.receiveFunction, name="Receive Thread")

        self.receiveThreadActive = False

    def receiveFunction(self):

        recvMessage = PLinApi.TLINRcvMsg()

        while(self.receiveThreadActive):

            result = self.bus.Read(self.hClient, recvMessage)
            if result == PLinApi.TLIN_ERROR_OK:

                if recvMessage.ErrorFlags == PLinApi.TLIN_MSGERROR_OK:
                    msg = LinMessage()
                    msg.frameId = recvMessage.FrameId
                    if recvMessage.FrameId == 125:
                        msg.frameId = 0x3D
                    length = recvMessage.Length
                    for i in range(0, length):
                        msg.payload[i] = recvMessage.Data[i]

                    self.on_message_received(msg)

    def on_message_received(self, msg):

        print("Message Received, should be overwritten")
        print("FrameID: {0}".format(msg.frameId))
        print(msg.payload)

    def startDiagnosticSchedule(self):

        result = self.bus.StartSchedule(self.hClient, self.hHw, 1)
        if result is not PLinApi.TLIN_ERROR_OK: raise Exception("Error registering client")

        self.receiveThreadActive = True
        self.receiveThread.start()

    def sendMasterRequest(self, payload):

        dataLength = len(payload)
        data = (c_ubyte * 8)()

        for i in range(0, 8):
            data[i] = c_ubyte(0)

        for i in range(0, dataLength):
            data[i] = c_ubyte(payload[i])

        self.bus.UpdateByteArray(self.hClient, self.hHw, 0x3C, 0, 8, data)

    def closeConnection(self):

        self.receiveThreadActive = False

        while self.receiveThread.is_alive():
            pass

        self.bus.SuspendSchedule(self.hClient, self.hHw)

        self.bus.ResetHardwareConfig(self.hClient, self.hHw)
        self.bus.RemoveClient(self.hClient)

    def wakeup(self):

        self.bus.XmtWakeUp(self.hClient, self.hHw)

if __name__ == "__main__":

    from time import time
    connection = LinBus(19200)
    connection.startDiagnosticSchedule()

    startTime = time()
    sendTime = startTime
    currTime = startTime

    while (currTime - startTime) < 5:

        if (currTime - sendTime) > 1:
            connection.sendMasterRequest([0, 1, 2, 3, 4, 5, 6, 7])
            sendTime = currTime

        currTime = time()

    connection.closeConnection()

