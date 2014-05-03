#!/usr/bin/env python

from serial import Serial
import re
import random

from struct import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *

import ui_imu_display
from IMUPacket import IMUPacket

class CHR6d:
    
    def __init__(self,port,rate=115200):
    
        self.port = port
        self.rate = rate
        
        ser = Serial(self.port,self.rate,timeout = 1)
        if ser.inWaiting():
            s = ser.read(20)
            print "Read some bytes.. %s" % s
        ser.close()
    
    # returns total as checksum
    # input - string
    def checksum(self,st):
        return reduce(lambda x,y:x+y, map(ord, st))
    
    def BuildPacket(self, pt, str):
        
        N = len(str)
        if False and N == 0:
            '''
            The protocol is not specific here. but, it appears that packet types
            that do not send data, also do not send the N.. this is stupid IMNSHO..
            '''
            sdata = 'snp' + pack("=B",pt)
        else:
            sdata = 'snp' + pack("=BB",pt,N) + str
        chk = self.checksum(sdata)
        sdata = sdata + pack(">H",chk)
        
        return sdata
    
    def Send(self,p):
        ser = Serial(self.port,baudrate=self.rate,timeout = 5)
        print "Opend serial channel to %s" % self.port
        #ser = Serial("/dev/tty.usbserial-A9007KPc",baudrate=115200,timeout = 5)
        if not ser:
            print "Failed to create the serial channel"
            return
        
        N = len(p)
        try:
            print "Attempting to send %d bytes" % N
            #nSent = ser.write(p)
            #ser.flushInput()
            #ser.flushOutput()
            print "Sending.."
            nSent = 2
            ser.flushInput()
            for x in range(0,N):
                ser.write(p[x])
            #ser.flushOutput()
            #if nSent != N:
            #    print "nBbyte not equal to count in. %d != %d" % (nSent, N)
        except:
            print "Failed to send data.."
            
        ser.close()
        
    
    def setSilentMode(self):
        p = self.BuildPacket(0x83,"")
        self.Send(p)
    
    def setBroadcastMode(self,freq=20):
        if freq < 20:
            x = 0
        elif freq > 300:
            x = 255
        else:
            x = 255*(freq-20)/280
        
        p = self.BuildPacket(0x84, pack("=B",x))
        self.Send(p)
        
        
def main(port):
    chr = CHR6d(port)
    
    chr.setSilentMode()
        
        
if __name__ == "__main__":
    #main("/dev/tty.usbserial-A9007KPc")
    main("/dev/cu.usbserial-A9005ccP")
    

        

