#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from lin import LinBus
#from lin import LinBusVector
from lin import LinBusTest

##
# @brief class for creating Tp objects
class LinBusFactory(object):

    configType = ''
    configParameters = []

    config = None

    ##
    # @brief method to create the different connection types
    @staticmethod
    def __call__(linBusType=None, baudrate=None, **kwargs):
        if(linBusType == "Peak"):
            return LinBus(baudrate=baudrate, **kwargs) # ... TODO: rename to LinBusPeak
        elif(linBusType == "Vector"):
            raise NotImplementedError("DoIP transport not currently supported")
            #return LinBusVector(configPath=configPath, **kwargs)
        elif(linBusType == "TEST"):
            return LinBusTest(**kwargs)
        else:
            raise Exception("Unknown transport type selected")


if __name__ == "__main__":

    pass
