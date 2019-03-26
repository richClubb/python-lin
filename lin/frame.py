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
from ctypes import *

class Frame(object):

    def __init__(self, ldf=None, filename=None, frame_name=None, delay=None, frame_id=None, checksumType=None, direction=None, initial_data=None, flags=None):
        self.__ldf = ldf
        self.__frameName = None
        self.__frameId = None
        self.__delay = None
        self.__checksumType = None
        self.__frameType = None # event, sporadic, masterRequest, slaveResponse, unconditional
        self.__collisionScheduleIndex = None # only applies to event
        self.__direction = None # ... from params, and possibly from ldf or context, so set to an indeterminate None at this point
        self.__initialData = None # ... possibly set from ldf or params, so initialise to an indeterminate None at this point
        self.__length = c_ubyte(8) # ... initilaise length for the basic 8 byte frame
        self.__flags = flags  # ... we don't look as though we can derive these, so 

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

        """ The LinBus code used to set up request and response frames - these will now need to be set up via data from here
		so make sure it is all available as frame properties - LinBus should then get the details from here ...
        """			

        # Check if there's a direction that cna be established (publisher or subscriber) ...
        if direction is not None:
            if direction not in ['publisher','subscriber']:
                raise Exception("Direction must be 'publisher' or 'subscriber'")
            self.__direction = direction
        else:
            pass # ... can we self-determine? if so, then we can add it here (TODO)

        # Is there any initial data? If not, we initial the frame to 0's ...
        if self.__initialData is None:
            self.__initialData = [c_ubyte(0) for i in range(0, 8)]  # ... set to 0's at least
        if initial_data is not None:
            self.__initialData = [c_ubyte(0) for i in range(0, 8)]  # ... the caller wants to override whatever has already been set up as a default, so clear and replace
            data_length = len(initial_data)
            if data_length > 8:
                raise Exception("Currently not configured to accept more than 8 bytes of data in the frame")
            for i in range(0, data_length):
                self.__initialData[i] = c_ubyte(initial_data[i]) 
		
	
			

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

    @property
    def direction(self):
        return self.__direction

    @property
    def initialData(self):
        return self.__initialData

    @property
    def length(self):
        return self.__length

    @property
    def flags(self):
        return self.__flags


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
        print(("direction:",frame.direction))
        print(("initialData:",frame.initialData))
        print(("length:",frame.length))
        print(("flags:",frame.flags))
