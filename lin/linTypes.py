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

# The following have been moved down here from Python-UDS LinTPTypes.py (for the time being at least) 
# ... I've basically been moving anything LIN related but not UDS related down to here.

##
# used for controlling single/multi-frame messages - possibly incomplete
class LinTpState(Enum):
    IDLE = 0
    SEND_SINGLE_FRAME = 1
    SEND_FIRST_FRAME = 2
    SEND_CONSECUTIVE_FRAME = 3
    RECEIVING_CONSECUTIVE_FRAME = 4


class LinTpMessageType(IntEnum):
    SINGLE_FRAME = 0
    FIRST_FRAME = 1
    CONSECUTIVE_FRAME = 2

# Needs checking!!!
LINTP_MAX_PAYLOAD_LENGTH = 4095
N_PCI_INDEX = 0
SINGLE_FRAME_DL_INDEX = 0
SINGLE_FRAME_DATA_START_INDEX = 1
FIRST_FRAME_DL_INDEX_HIGH = 0
FIRST_FRAME_DL_INDEX_LOW = 1
FIRST_FRAME_DATA_START_INDEX = 2
CONSECUTIVE_FRAME_SEQUENCE_NUMBER_INDEX = 0
CONSECUTIVE_FRAME_SEQUENCE_DATA_START_INDEX = 1
