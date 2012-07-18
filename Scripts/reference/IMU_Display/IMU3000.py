#!/usr/bin/env python

import serial
import platform
import glob
import time
import re
from GloveAPI import GloveAPI

class IMU3000(object):

    def __init__(self,api,port, ID, accID):
        super(IMU3000,self).__init__()

        self.api = api
        self.port = port
        self.ID = ID
        self.accID = accID

        # Settings
        self.DLPF = 0x1
        self.FullScale = 0x1
        self.ClkSel = 0x1 # Select X Gyro clock

    def Configure(self):
        ''' Set all offsets to zero '''
        for x in range(0x12,0x18):
            self.Wr(x,0x00)

        self.Wr(0x12,0xff)          # Enable all outputs to to the fifo
        self.Wr(0x13,0x00)
        self.Wr(0x14,self.accID >> 1) # Set slave address of ACC
        self.Wr(0x15,4) # Set sample rate to 200Hz
        self.Wr(0x16,self.DLPF | self.FullScale << 3)
        self.Wr(0x18,0x80 | 0x28) # Set burst address for Accelerometer, enable auto addr increment.
        self.Wr(0x3E,self.ClkSel)

    def Passthrough(self,bOn):
        if bOn:
            self.Wr(0x3D,0x8)
        else:
            self.Wr(0x3D,0x28)

    def Status(self):
        v = self.Rd(0x1a)
        if isinstance(v,(list,tuple)):
            val = v[0]
        else:
            val = v

        rdrdy = False
        dmpdone = False
        imurdy = False
        i2cErr = False
        fifoFull = False

        if val & 0x1:
            rdrdy = True
        if val & 0x2:
            dmpdone = True
        if val & 0x4:
            imurdy = True
        if val & 0x8:
            i2cErr = True
        if val & 0x80:
            fifoFull = True

        return [rdrdy,dmpdone,imurdy,i2cErr,fifoFull]

    def Read(self):
        v = self.Rd(0x1b,14)
        vout = []
        if len(v) > 13:
            for x in range(0,len(v),2):
                val = v[x] << 8 | v[x+1]
                vout.append(val)

            return vout
        return None

    def ReadD(self):
        vout = self.Read()
        dout = {
            "Temp"  : vout[0],
            'GyroX' : vout[1],
            'Gyroy' : vout[2],
            'GyroZ' : vout[3],
            'AccX'  : vout[4],
            'AccY'  : vout[5],
            'AccZ'  : vout[6],
        }

    def FifoSetup(self):
        self.Wr(0x3d,0x40 | 0x20 | 0x40 | 0x20)

    def FifoRead(self):
        fout = self.Rd(0x32,16)
        vout = []
        for x in range(0,15,2):
            val = v[x] << 8 | v[x+1]
            vout.append(val)

        return vout

    def FifoReadD(self):
        vout = self.FifoRead()
        dout = {
            'Temp'  : vout[0],
            'GyroX' : vout[1],
            'Gyroy' : vout[2],
            'GyroZ' : vout[3],
            'AccX'  : vout[4],
            'AccY'  : vout[5],
            'AccZ'  : vout[6],
        }

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
