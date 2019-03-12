#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"


from lin.linTypes import ChecksumType, FrameType

class FrameSlot(object):

    def __init__(self, ldf=None, filename=None, frame_name=None, delay=None):
        self.__ldf = ldf
        self.__frameId = None
        self.__delay = None
        self.__checksumType = None
        self.__frameType = None # event, sporadic, masterRequest, slaveResponse, unconditional
        self.__collisionScheduleIndex = None # only applies to event
        self.__initialData = None
        self.__length = None
		
        # Allowing for different ways of hooking the code together at this stage (can be rationalised later).
		# The caller can either pass a pre-parsed ldf object, or specify an ldf file to parse and use the details from.
        if ldf is none and filename is not None:
            self.__ldf = LdfFile(filename)		

        frameSlotData = self.__ldf.getFrameDetails(frame_name=frame_name)  # ... could be None, in which case it will return an empty table       
        self.__frameId                = frameSlotData[0]
		self.__delay                  = frameSlotData[1]   # from sched table delay
		self.__checksumType           = frameSlotData[2]
		self.__frameType              = frameSlotData[3]
		self.__collisionScheduleIndex = frameSlotData[4]
		self.__initialData            = frameSlotData[5]
		self.__length                 = frameSlotData[6]     


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

