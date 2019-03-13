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

    def __init__(self, ldf=None, filename=None, schedule_name=None, transport=None):
        self.__ldf = ldf
        self.__frameSlots = []
        self.__sizes = 0
        self.__transport = transport
        #self.__<??schedule index??>)   # ... what in consitutes the index? The ldf doesn't clearly specify anything as an index?
        # ... anything to do with service index? Only other ref to index I can find is to frame index?
        # ... the peak interface this was based on support 255 slots with straight 
		#     indexing - index number is just where loaded, so whatever we choose? (see page 147 in PLIN API doc)

        # Allowing for different ways of hooking the code together at this stage (can be rationalised later).
		# The caller can either pass a pre-parsed ldf object, or specify an ldf file to parse and use the details from.
        if ldf is none and filename is not None:
            self.__ldf = LdfFile(filename)

		# Schedule_name could be None, in which case it will return an empty list ...
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
        self.transport.startSchedule(self.__<??schedule index??>)   # ... what in consitutes the index? The ldf doesn't clearly specify anything as an index?

    def pause(self):
        self.transport.pauseSchedule(self.__<??schedule index??>)

    def start(self):
        self.transport.stopSchedule(self.__<??schedule index??>)
    """



