

class ScheduleTable(object):

    def __init__(self):
        self.__frameSlots = []
        self.__sizes = 0

    @property
    def frameSlots(self):
        return self.__frameSlots

    @property
    def size(self):
        return self.__size

    def addFrameSlot(self, frameSlot):
        self.__frameSlots.append(frameSlot)
        self.__size = len(self.__frameSlots)



