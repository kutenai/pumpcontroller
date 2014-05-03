#!/usr/bin/env python

import serial
import platform
import glob
import time
import re
from GloveAPI import GloveAPI

class Accelerometer(object):

    def __init__(self,api,port,ID):
        super(Accelerometer,self).__init__()
        self.api = api
        self.port = port
        self.ID = ID

    def Configure(self):

        ''' Configure the CFG regs '''
        self.Wr(0x20, 0x37)
        self.Wr(0x21, 0x0)
        self.Wr(0x22, 0x0)
        self.Wr(0x23, 0x80 | 0x40)
        self.Wr(0x24, 0x00)

    def Read(self):
        vals = []
        rdvals = self.Rd(0x28,6)
        if length(rdvals) == 6:
            for x in range(0,3):
                val = int(rdvals[x*2+1],16) << 8 + int(rdvals[x*2],16)
                vals.append(val)
            return vals
        else:
            return None

    def Rd(self,addr,n=1):
        rdvals = self.api.i2crd(self.port,self.ID,addr,n)
        return rdvals

    def Wr(self,addr,data):
        self.api.i2cwr(self.port,self.ID,addr,data)

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
