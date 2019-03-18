#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2019, the python-lin project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from lin.frameSlot import FrameSlot

class ScheduleTable(object):

    table_index_register = {} # ... used to track allocations for error handling, etc.

    def __init__(self, ldf_parsed=None, ldf_filename=None, schedule_name=None, transport=None, index=None, diagnostic_schedule=False):
        self.__ldf = ldf_parsed
        self.__frameSlots = []
        self.__sizes = 0
        self.__transport = transport
		self.__schedule_index = None  # ... schedule index is taken from the LDF file (based on order of schedule table in the files), OR allocated/specified when the table is 

        # Allowing for different ways of hooking the code together at this stage (can be rationalised later).
		# The caller can either pass a pre-parsed ldf object, or specify an ldf file to parse and use the details from.
        if self.__ldf is None and ldf_filename is not None:
            self.__ldf = LdfFile(ldf_filename)

        if self.__ldf is not None:
            if schedule_name is not None:
                scheduleData = self.__ldf.getScheduleDetails(schedule_name=schedule_name)  # ... could be None

                self.__frameSlots = [FrameSlot(frame_name=fn) for fn in self.__ldf.getFrameNames(schedule_name=schedule_name)]
		        self.__size = len(self.__frameSlots)

    @property
    def frameSlots(self):
        return self.__frameSlots

    @property
    def size(self):
        return self.__size

    def addFrameSlot(self, frameSlot):
        self.__frameSlots.append(frameSlot)
        self.__size = len(self.__frameSlots)
 
    """
    def registerTransport(self,transport):
        self.__transport = transport

    def start(self):
        self.transport.startSchedule(self.__schedule_index)

    def pause(self):
        self.transport.pauseSchedule(self.__schedule_index)

    def stop(self):
        self.transport.stopSchedule(self.__schedule_index)
    """



