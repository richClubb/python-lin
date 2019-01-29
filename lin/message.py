
from lin.linTypes import FrameType, ChecksumType
from lin.utilities import calculatePid


class Message(object):

    def __init__(self, frameId=None, length=None, data=None, frameType=None):

        self.__frameId = frameId

        self.__PID = 0
        if self.__frameId is not None:
            self.__PID = calculatePid(frameId)

        self.__frameType = frameType

        self.__length = length
        self.__data = data

        if self.__data is None:
            self.__data = []
            if self.__length is None:
                self.__length = 0
            else:
                for i in range(0, length):
                    self.__data.append(0)

        if self.__length is None:
            self.__length = len(self.__data)

        if self.__length != len(self.__data):
            raise Exception("Data length not equal to specified length")

        if self.__frameType is None:
            self.__type = FrameType.UNCONDITIONAL


    @property
    def frameId(self):
        return self.__frameId

    @property
    def pid(self):
        return self.__PID

    @property
    def frameType(self):
        return self.__frameType

    @property
    def data(self):
        return self.__data

    @property
    def length(self):
        return self.__length
