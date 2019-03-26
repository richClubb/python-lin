#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from lin.Utilities.LdfParser import LdfFile
from lin.frame import Frame
from lin.frameSlot import FrameSlot

class ScheduleTable(object):

    table_index_register = {} # ... used to track allocations for error handling, etc.

    def __init__(self, ldf_parsed=None, ldf_filename=None, schedule_name=None, transport=None, index=None, diagnostic_schedule=False):
        self.__ldf = ldf_parsed
        self.__scheduleName = None
        self.__frames = {}
        self.__frameSlots = []
        self.__size = 0   # ... number of frameslots
        self.__transport = transport
        self.__scheduleIndex = None  # ... schedule index is taken from the LDF file (based on order of schedule table in the files), OR allocated/specified when the table is 
        self.__scheduledAdded = False

        # Allowing for different ways of hooking the code together at this stage (can be rationalised later).
		# The caller can either pass a pre-parsed ldf object, or specify an ldf file to parse and use the details from.
        if self.__ldf is None and ldf_filename is not None:
            self.__ldf = LdfFile(ldf_filename)

        if self.__ldf is not None:
            scheduleData = None
            if schedule_name is not None:
                scheduleData = self.__ldf.getScheduleDetails(schedule_name=schedule_name)
            elif index is not None:
                scheduleData = self.__ldf.getScheduleDetails(schedule_index=index)
            elif diagnostic_schedule:
                scheduleData = self.__ldf.getScheduleDetails(diagnostic_schedule=True)

            self.__scheduleName  = scheduleData[0]
            if self.__scheduleName is not None:
                # If we can derive any flags (or meta instructions for flag generation at the bus level) to pass down to the LinBus, then we need to add this here when we auto create the frames (TODO)
                pass

                # Can we establish direction at this point, as it's needed by the frame to pass to LinBus? (TODO)
                pass
                # ... frame details (via frame name) provide publisher
                # ... note: can do this here at this level and pass to frame, or do it in the frame constructor, but may need info passed down.
                # ... the transport has the node address supplied, and the NodeAttributes in the ldf have configured_NAD and initial_NAD available - I presume we can match configured_NAD? - this would tell us our node_name in the ldf
                # ... node_address is not mandatory though
 
                self.__frames = dict([(fn,Frame(ldf=self.__ldf,frame_name=fn)) for fn in self.__ldf.getFrameNames(schedule_name=self.__scheduleName)])   # ... unique frame object per frame type - not sure if this is what's wanted!!!
 			
            self.__scheduleIndex = scheduleData[1]
            self.__frameSlots = [FrameSlot(frame=self.__frames[fn],schedule_index=self.__scheduleIndex) for fn in scheduleData[2]]   # ... unique frame object per frame type - not sure if this is what's wanted!!!
            self.__size = len(self.__frameSlots)


        if self.__scheduleName is None and schedule_name is not None:
            self.__scheduleName = schedule_name
        if self.__scheduleIndex is None and index is not None:
            self.__scheduleIndex = index

        #!!!!!!!!!!!!!!!!! We need an add schedule() operation here !!!!!!!!!!!!!! (certainly for the manually added schedules?) (TODO)

    @property
    def scheduleName(self):
        return self.__scheduleName

    @property
    def scheduleIndex(self):
        return self.__scheduleIndex

    @property
    def frames(self):
        return self.__frames

    @property
    def frameSlots(self):
        return self.__frameSlots

    @property
    def size(self):
        return self.__size

    ##
    # @brief this function ...
    def addFrameSlot(self, frameSlot=None, frame=None):
        if frameSlot is None and frame is not None:
            frameSlot = FrameSlot(frame=frame,schedule_index=self.__scheduleIndex)
        if frameSlot is not None:
            self.__frameSlots.append(frameSlot)
            self.__size = len(self.__frameSlots)
            # Keep additional records in synch ...
            if frameSlot.frameName not in self.__frames:
                self.__frames[frameSlot.frameName] = frameSlot.frame
        self.__transport.addFrame(frameSlot.frame)  # ... this calls the code to initialise the frame entry in the LinBus code (which in turn accesses the frame object for the frame properties held at this level).
 

    ##
    # @brief this function ...
    def registerTransport(self,transport):
        # Do we need to add something like the following? (assuming we can even change the transport rather than just registering one for the first time) ...
        """
        if self.__transport is not None and self.__transport != transport:
            self.__scheduledAdded = False
        """
        self.__transport = transport

    ##
    # @brief this function ...
    def add(self):
        if not self.__scheduledAdded:    # ... curerntly assuming we only need to add a schedule once - is this correct? Can it be lost and require re-adding? - check with Richard (TODO)
            self.__transport.addSchedule(self, self.__scheduleIndex)
            self.__scheduledAdded = True

    ##
    # @brief this function ...
    def start(self):
        if not self.__scheduledAdded:
            self.add()
        self.__transport.startSchedule(self.__scheduleIndex)

    ##
    # @brief this function ...
    def pause(self):
        if self.__scheduledAdded:
            self.__transport.pauseSchedule(self.__scheduleIndex)

    ##
    # @brief this function ...
    def stop(self):
        if self.__scheduledAdded:
            self.__transport.stopSchedule(self.__scheduleIndex)



if __name__ == "__main__":
        #table = ScheduleTable()
        #table = ScheduleTable(ldf_filename="../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../SecurityLIN_P22_3.5.5.ldf",diagnostic_schedule=False)
        #table = ScheduleTable(ldf_filename="../../SecurityLIN_P22_3.5.5.ldf",diagnostic_schedule=True)

        #table = ScheduleTable(ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf")
        table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf",diagnostic_schedule=False)
        #table = ScheduleTable(ldf_filename="../../McLaren_P14_SecurityLIN_3.5.ldf",diagnostic_schedule=True)
		
        print(("scheduleName:",table.scheduleName))
        print("")
        print(("scheduleIndex:",table.scheduleIndex))
        print("")
        print(("frames:",table.frames))
        print("")
        print(("size:",table.size))
        print("")
        print("frameslots")
        for entry in table.frameSlots:
            print(("frameName:",entry.frameName,"frameId:",entry.frameId,"delay:",entry.delay,"checktype:",entry.checksumType))



