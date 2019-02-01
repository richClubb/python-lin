from lin.linTypes import ChecksumType, FrameType

class FrameSlot(object):

    def __init__(self, delay=None):

        self.__frameId = None
        self.__delay = None
        self.__checksumType = None
        self.__frameType = None # event, sporadic, masterRequest, slaveResponse, unconditional
        self.__collisionScheduleIndex = None # only applies to event
        self.__initialData = None
        self.__length = None

    @property
    def frameId(self):
        return self.__frameId

    @property
    def delay(self):
        return self.__delay

    @property
    def checksumType(self):
        return self.__checksumType

    @property
    def frameType(self):
        return self.__frameType

    @property
    def collisionScheduleIndex(self):
        return self.__collisionScheduleIndex

