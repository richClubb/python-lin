#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from lin.Utilities.LdfParser import LdfFile
from lin.linTypes import ChecksumTypes, FrameTypes

class FrameSlot(object):

    def __init__(self, frame=None, delay=None, schedule_index=None):
        self.__frame = frame
        self.__delay = frame.delay['selected']  # ... initialise slot delay from basic frame data
        if schedule_index is not None:
            self.__delay = frame.delay['by_schedule'][schedule_index]
        if delay is not None:
            self.__delay = delay                # ... but allow override where details are provided directly
        """
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
        else:
            # Set up a few extra bits if possible, where manual entry has taken place ...
            # NOTE: at present we do not include and parse out any details here for anything other than type - see LDF parser for how the parser extracts details for the diff commands (TODO) !!!!!!!!!!
            command_lower = frame_name.lower()
            if 'masterreq' in command_lower:
                self.__frameType = 'MasterReq'
            elif 'slaveresp' in command_lower:
                self.__frameType = 'SlaveResp'
            elif 'assignnad' in command_lower:
                self.__frameType = 'AssignNAD'                      
            elif 'conditionalchangenad' in command_lower:                    
                self.__frameType = 'ConditionalChangeNAD'                      
            elif 'datadump' in command_lower:                    
                self.__frameType = 'DataDump'
            elif 'saveconfiguration ' in command_lower:                  
                self.__frameType = 'SaveConfiguration'                   
            elif 'assignframeidrange ' in command_lower:
                self.__frameType = 'AssignFrameIdRange'
            elif 'freeformat ' in command_lower:
                self.__frameType = 'FreeFormat'
            elif 'assignframeid ' in command_lower:                    
                self.__frameType = 'AssignFrameId'
            else:
                self.__frameType = 'frame_name'   

        # Check if delay has been overridden ...
        if frame_id is not None:
            self.__frameId = frame_id

        # Check if delay has been overridden ...
        if delay is not None:
            if self.__delay is None:
                self.__delay = {'selected': None,'unique': [],'by_schedule':{}}
            self.__delay['selected'] = delay

        # Check if checksumType has been overridden ...
        if checksumType is not None:
            self.__checksumType = checksumType
        """
			

    @property
    def frame(self):
        return self.__frame

    @property
    def frameName(self):
        return self.__frame.frameName

    @property
    def frameId(self):
        return self.__frame.frameId

    @property
    def delay(self):
        return self.__frame.delay

    @property
    def checksumType(self):
        return self.__frame.checksumType

    @property
    def frameType(self):
        return self.__frame.frameType

    @property
    def collisionScheduleIndex(self):
        return self.__frame.collisionScheduleIndex

    @property
    def direction(self):
        return self.__frame.direction

    @property
    def initialData(self):
        return self.__frame.initialData

    @property
    def length(self):
        return self.__frame.length

    @property
    def flags(self):
        return self.__frame.flags


if __name__ == "__main__":
        #frameSlot = FrameSlot()

        #frameSlot = FrameSlot(filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #frameSlot = FrameSlot(frame_name='DoorLCommand',filename="../../SecurityLIN_P22_3.5.5.ldf")
        #frameSlot = FrameSlot(frame_name='DoorLCommand',filename="../../SecurityLIN_P22_3.5.5.ldf",delay=20)

        #frameSlot = FrameSlot(filename="../../../McLaren_P14_SecurityLIN_3.5.ldf")
        frameSlot = FrameSlot(frame_name='DoorLCommand',filename="../../McLaren_P14_SecurityLIN_3.5.ldf")
        #frameSlot = FrameSlot(frame_name='DoorLCommand',filename="../../McLaren_P14_SecurityLIN_3.5.ldf",delay=20)

        print(("frameName:",frameSlot.frameName))
        print(("frameId:",frameSlot.frameId))
        print(("delay:",frameSlot.delay))
        print(("checksumType:",frameSlot.checksumType))
        print(("frameType:",frameSlot.frameType))
        print(("collisionScheduleIndex:",frameSlot.collisionScheduleIndex))
