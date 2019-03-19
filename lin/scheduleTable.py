#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from Utilities.LdfParser import LdfFile
from frameSlot import FrameSlot

class ScheduleTable(object):

    table_index_register = {} # ... used to track allocations for error handling, etc.

    def __init__(self, ldf_parsed=None, ldf_filename=None, schedule_name=None, transport=None, index=None, diagnostic_schedule=False):
        self.__ldf = ldf_parsed
        self.__scheduleName = None
        self.__frameSchedule = []
        self.__frameSlots = []
        self.__size = 0
        self.__transport = transport
        self.__scheduleIndex = None  # ... schedule index is taken from the LDF file (based on order of schedule table in the files), OR allocated/specified when the table is 

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
            self.__scheduleIndex = scheduleData[1]
            self.__frameSchedule = scheduleData[2] # ... list of frames as specified in the schedule - not sure if this is what's wanted!!!

            if self.__scheduleName is not None:
                self.__frameSlots = [FrameSlot(ldf=self.__ldf,frame_name=fn) for fn in self.__ldf.getFrameNames(schedule_name=self.__scheduleName)]   # ... unique frame object per frame type - not sure if this is what's wanted!!!
                self.__size = len(self.__frameSlots)

        if self.__scheduleName is None and schedule_name is not None:
            self.__scheduleName = schedule_name
        if self.__scheduleIndex is None and index is not None:
            self.__scheduleIndex = index

    @property
    def scheduleName(self):
        return self.__scheduleName

    @property
    def scheduleIndex(self):
        return self.__scheduleIndex

    @property
    def frameSchedule(self):
        return self.__frameSchedule

    @property
    def frameSlots(self):
        return self.__frameSlots

    @property
    def size(self):
        return self.__size

    def addFrameSlot(self, frameSlot):
        self.__frameSlots.append(frameSlot)
        self.__size = len(self.__frameSlots)
 

    def registerTransport(self,transport):
        self.__transport = transport

    def start(self):
        self.transport.startSchedule(self.__scheduleIndex)

    def pause(self):
        self.transport.pauseSchedule(self.__scheduleIndex)

    def stop(self):
        self.transport.stopSchedule(self.__scheduleIndex)



if __name__ == "__main__":
        #table = ScheduleTable()
        #table = ScheduleTable(ldf_filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../../SecurityLIN_P22_3.5.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../../SecurityLIN_P22_3.5.5.ldf",diagnostic_schedule=False)
        #table = ScheduleTable(ldf_filename="../../../SecurityLIN_P22_3.5.5.ldf",diagnostic_schedule=True)

        #table = ScheduleTable(ldf_filename="../../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(schedule_name='SecurityLINNormal',ldf_filename="../../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../../McLaren_P14_SecurityLIN_3.5.ldf")
        #table = ScheduleTable(index=1,ldf_filename="../../../McLaren_P14_SecurityLIN_3.5.ldf",diagnostic_schedule=False)
        table = ScheduleTable(ldf_filename="../../../McLaren_P14_SecurityLIN_3.5.ldf",diagnostic_schedule=True)
		
        print(("scheduleName:",table.scheduleName))
        print("")
        print(("scheduleIndex:",table.scheduleIndex))
        print("")
        print(("frameSchedule:",table.frameSchedule))
        print("")
        print(("size:",table.size))
        print("")
        for entry in table.frameSlots:
            print(("frameName:",entry.frameName,"frameId:",entry.frameId,"delay:",entry.delay,"checktype:",entry.checksumType))



