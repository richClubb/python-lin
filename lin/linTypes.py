from enum import Enum


class FrameType(Enum):

    UNCONDITIONAL = 1
    EVENT = 2
    SPORADIC = 3
    MASTER_REQUEST = 4
    SLAVE_RESPONSE = 5


class ChecksumType(Enum):

    CLASSIC = 1
    ENHANCED = 2


