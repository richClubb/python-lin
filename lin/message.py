
from linTypes import FrameTypes, ChecksumTypes
from utilities import calculatePid


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
            self.__type = FrameTypes.UNCONDITIONAL


    @property
    def frameId(self):
        return self.__frameId

    @frameId.setter
    def frameId(self, value):
        self.__frameId = value

    @property
    def pid(self):
        return self.__PID

    @pid.setter
    def pid(self, value):
        self.__PID = value

    @property
    def frameType(self):
        return self.__frameType

    @frameType.setter
    def frameType(self, value):
        self.__frameType = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        if len(value) != self.__length:
            self.__length = len(value)
        self.__data = value

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value
