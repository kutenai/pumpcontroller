#!/usr/bin/env python

import serial
import platform
import glob
import time
import re
import numpy
import scipy
from GloveAPI import GloveAPI
from IMU3000 import IMU3000
from LIS331 import Accelerometer

class IMU(object):
    def __init__(self,api,port,imuID, accID):
        super(IMU,self).__init__()

        self.api = api
        self.acc = Accelerometer(api,port,accID)
        self.imu = IMU3000(api,port,imuID,accID)

    def Configure(self):
        self.imu.Passthrough(True)
        self.acc.Configure()
        self.imu.Configure()
        self.imu.Passthrough(False)

    def Read(self):
        return self.imu.Read()

if __name__ == "__main__":
    api = GloveAPI()
    api.initHardware()

    imu1 = IMU(api,1,0xD0,0x32)
    #imu2 = IMU(api,2,0xD2,0x30)

    imu1.Configure()
    #imu2.Configure()

    #x = imu1.imu.Status()

    while (1):
        try:
            v = imu1.Read()
            if len(v) > 5:
                print ("Temp:{0}".format(v[0]))
                print ("GX,Y,Z:{0} {1} {2}".format(v[1],v[2],v[3]))
                print ("AX,Y,Z:{0} {1} {2}".format(v[4],v[5],v[6]))
        except:
            print("Excepton")


    print ("Done")
