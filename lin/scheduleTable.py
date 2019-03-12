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

    def __init__(self, ldf=None, filename=None, schedule_name=None):
        self.__ldf = ldf
        self.__frameSlots = []
        self.__sizes = 0

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



