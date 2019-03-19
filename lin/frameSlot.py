#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from Utilities.LdfParser import LdfFile
from linTypes import ChecksumTypes, FrameTypes

class FrameSlot(object):

    def __init__(self, ldf=None, filename=None, frame_name=None, delay=None):
        self.__ldf = ldf
        self.__frameName = None
        self.__frameId = None
        self.__delay = None
        self.__checksumType = None
        self.__frameType = None # event, sporadic, masterRequest, slaveResponse, unconditional
        self.__collisionScheduleIndex = None # only applies to event
        self.__initialData = None
        self.__length = None
		
        # Allowing for different ways of hooking the code together at this stage (can be rationalised later).
		# The caller can either pass a pre-parsed ldf object, or specify an ldf file to parse and use the details from.
        if ldf is None and filename is not None:
            self.__ldf = LdfFile(filename)		
        if self.__ldf is not None:
            frameSlotData = self.__ldf.getFrameDetails(frame_name=frame_name)  # ... could be None, in which case it will return an empty table
            self.__frameName              = frameSlotData[0]
            self.__frameId                = frameSlotData[1]
            self.__delay                  = frameSlotData[2]   # from sched table delay - this is dependent of schedule table index - i.e. not the same for all schedules! (see real-world ldf examples)
            self.__checksumType           = frameSlotData[3]
            self.__frameType              = frameSlotData[4]
            self.__collisionScheduleIndex = frameSlotData[5]
            self.__initialData            = frameSlotData[6]
            self.__length                 = frameSlotData[7] 

        # Check if delay has been overridden ...
        if delay is not None:
            if self.__delay is None:
                self.__delay = {'selected': None,'unique': [],'by_schedule':{}}
            self.__delay['selected'] = delay


    @property
    def frameName(self):
        return self.__frameName

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




if __name__ == "__main__":
        #frameSlot = FrameSlot()
        #frameSlot = FrameSlot(filename="../../../SecurityLIN_P22_3.5.5.ldf")
        frameSlot = FrameSlot(frame_name='DoorLCommand',filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #frameSlot = FrameSlot(frame_name='DoorLCommand',filename="../../../SecurityLIN_P22_3.5.5.ldf",delay=20)

        print(("frameName:",frameSlot.frameName))
        print(("frameId:",frameSlot.frameId))
        print(("delay:",frameSlot.delay))
        print(("checksumType:",frameSlot.checksumType))
        print(("frameType:",frameSlot.frameType))
        print(("collisionScheduleIndex:",frameSlot.collisionScheduleIndex))
