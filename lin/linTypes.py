from enum import Enum


class FrameTypes(Enum):
    UNCONDITIONAL = 1
    EVENT = 2
    SPORADIC = 3
    MASTER_REQUEST = 4
    SLAVE_RESPONSE = 5


class ChecksumTypes(Enum):
    CLASSIC = 1
    ENHANCED = 2


class ScheduleTypes(Enum):
    NORMAL = 1
    DIAGNOSTIC = 2
    DIAGNOSTIC_INTERLEAVED = 3
    COLLISION_RESOLUTION = 4


class DeviceTypes(Enum):
    MASTER = 1
    SLAVE = 2
