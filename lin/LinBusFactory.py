#!/usr/bin/env python

__author__ = "Richard Clubb"
__copyrights__ = "Copyright 2018, the python-uds project"
__credits__ = ["Richard Clubb"]

__license__ = "MIT"
__maintainer__ = "Richard Clubb"
__email__ = "richard.clubb@embeduk.com"
__status__ = "Development"

from lin.interfaces.peak.LinBus import LinBus as LinBus_Peak
#from interfaces.vector.LinBus import LinBus as LinBus_Vector
#from lin import LinBusTest as LinBus_TEST

##
# @brief class for creating Tp objects
class LinBusFactory(object):

    configType = ''
    configParameters = []

    config = None

    ##
    # @brief method to create the different connection types
    @staticmethod
    def __call__(linBusType=None, baudrate=None, callback=None, **kwargs):
        if(linBusType == "Peak"):
            return LinBus_Peak(baudrate=baudrate, callback=callback, **kwargs) # ... TODO: rename to LinBusPeak
        elif(linBusType == "Vector"):
            raise NotImplementedError("Vector transport/API not currently supported")
            #return LinBusVector(configPath=configPath, **kwargs)
        elif(linBusType == "TEST"):
            raise NotImplementedError("Test transport/API not currently supported")
            #return LinBus_test(**kwargs)
        else:
            raise Exception("Unknown transport type selected")


if __name__ == "__main__":

    pass
