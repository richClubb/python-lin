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

class Frame(object):

    def __init__(self, ldf=None, filename=None, frame_name=None, delay=None, frame_id=None, checksumType=None):
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
            frameData = self.__ldf.getFrameDetails(frame_name=frame_name)  # ... could be None, in which case it will return an empty table
            self.__frameName              = frameData[0]
            self.__frameId                = frameData[1]
            self.__delay                  = frameData[2]   # from sched table delay - this is dependent of schedule table index - i.e. not the same for all schedules! (see real-world ldf examples)
            self.__checksumType           = frameData[3]
            self.__frameType              = frameData[4]
            self.__collisionScheduleIndex = frameData[5]
            self.__initialData            = frameData[6]
            self.__length                 = frameData[7] 
        else:
            # Set up a few extra bits if possible, where manual entry has taken place ...
            # NOTE: at present we do not include and parse out any details here for anything other than type - see LDF parser for how the parser extracts details for the diff commands (TODO) !!!!!!!!!!
            command_lower = frame_name.lower()
            if 'masterreq' in command_lower:
                self.__frameType = 'MasterReq'   # ... we should most likey be using enums for a lot of these strings - needs adding and using throughout (TODO) - seom already exist in linTypes.py
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
        #frame = Frame()

        #frame = Frame(filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #frame = Frame(frame_name='DoorLCommand',filename="../../SecurityLIN_P22_3.5.5.ldf")
        #frame = Frame(frame_name='DoorLCommand',filename="../../SecurityLIN_P22_3.5.5.ldf",delay=20)

        #frame = Frame(filename="../../../McLaren_P14_SecurityLIN_3.5.ldf")
        frame = Frame(frame_name='DoorLCommand',filename="../../McLaren_P14_SecurityLIN_3.5.ldf")
        #frame = Frame(frame_name='DoorLCommand',filename="../../McLaren_P14_SecurityLIN_3.5.ldf",delay=20)

        print(("frameName:",frame.frameName))
        print(("frameId:",frame.frameId))
        print(("delay:",frame.delay))
        print(("checksumType:",frame.checksumType))
        print(("frameType:",frame.frameType))
        print(("collisionScheduleIndex:",frame.collisionScheduleIndex))
