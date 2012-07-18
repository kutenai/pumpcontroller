#!/usr/bin/env python

import serial
import platform
from struct import *

class IMUPacket:
    def __init__(self):
        self.pkID = 0
        self.pkType = None
        self.pkBytes = 0
        self.pkData = []
        self.WatchDog = 0
        self.pkCRC = 0

    def RawData(self):
        if self.pkType == 0xB7:
            lenPerIMU = 9
            numIMUs = len(self.pkData)/(lenPerIMU*2)
            numVals = (len(self.pkData))/2
            return self.pkData

    def Results(self):
        if self.pkType == 0xB7:
            '''
            The packet data consists of a single byte "Mask", and then N 2-byte unsigned
            values.
            The Unpack will unpack as many values as there are, since the values are all 2 bytes
            and the length of the data packet is 2*#values + 1
            '''
            lenPerIMU = 9
            Values = []
            #print ("Length of packet:%d" % len(self.pkData))
            numIMUs = len(self.pkData)/(lenPerIMU*2)
            #print ("Number of IMU's:%d" % numIMUs)
            numVals = (len(self.pkData))/2
            sUnpack = ">" + ''.join(["H8h" for x in range(0,numIMUs)])
            (Values) = unpack(sUnpack,self.pkData)
            #for x in self.pkData:
            #    print("Data:0x%x" % x)

            '''
            At this point, the Mask will tell us which values are valid
            '''

            imuData = []

            keys = ['sentinal','temp','gx','gy','gz','ax','ay','az','footer']
            numIMUs = len(Values)/lenPerIMU
            for x in range(0,numIMUs):
                imu = {}
                y = 0
                for k in keys:
                    imu[k] = Values[x*lenPerIMU+y]
                    y = y +1
                imuData.append(imu)

            return imuData
        else:
            print("Invalid packet type:%d" % self.pkType)

        '''
        Only handling one type for now..
        '''
        return None

class IMUPacketRead:

    sStart, sFndS, sFndN, sFndP, sPkType, sPkID, sPkSize, sPkData, sPkCRC, sPkDone = range(0,10)

    def __init__(self):
        self.pkLoc = 0
        self.pkState = IMUPacketRead.sStart
        self.packet = IMUPacket()
        self.isValidPacket = False
        self.verbose = False

    def isValid(self):
        return self.isValidPacket

    def getChars(self,ser):

        while not self.isValidPacket and ser.inWaiting() > 0:
        #while not self.isValidPacket:
            if self.pkState == IMUPacketRead.sStart:
                byte = ser.read(1)
                if byte == 'S':
                    self.pkState = IMUPacketRead.sFndN
                    if self.verbose:
                        print ("Found S")
            elif self.pkState == IMUPacketRead.sFndN:
                byte = ser.read(1)
                if byte == 'N':
                    self.pkState = IMUPacketRead.sFndP
                    if self.verbose:
                        print ("Found N")
                else:
                    self.pkState = IMUPacketRead.sStart
                    if self.verbose:
                        print ("Returning to Start")
            elif self.pkState ==  IMUPacketRead.sFndP:
                byte = ser.read(1)
                if byte == 'P':
                    self.pkState = IMUPacketRead.sPkType
                    if self.verbose:
                        print ("Found P")
                else:
                    self.pkState = IMUPacketRead.sStart
                    if self.verbose:
                        print ("Returning to Start")
            elif self.pkState == IMUPacketRead.sPkType:
                pkType = ser.read(1)
                self.packet.pkType = unpack('>B',pkType)[0]
                self.pkState = IMUPacketRead.sPkID
                if self.verbose:
                    print ("Found PkType:0x%x" % self.packet.pkType)
            elif self.pkState == IMUPacketRead.sPkID:
                ID = ser.read(1)
                self.packet.pkID = unpack('>B',ID)[0]
                self.pkState = IMUPacketRead.sPkSize
                if self.verbose:
                    print ("Found pkID:0x%x" % self.packet.pkID)
            elif self.pkState == IMUPacketRead.sPkSize:
                pkBytes = ser.read(1)
                self.packet.pkBytes = unpack('>B',pkBytes)[0]
                if self.verbose:
                    print("PkBytes:0x%x" % self.packet.pkBytes)
                if self.packet.pkBytes > 0:
                    '''
                    Doing a direct read here, rather than defering the read and
                    reading a seperate bytes... should be mucho faster.
                    '''
                    if self.verbose:
                        print ("Reading %d Bytes" % self.packet.pkBytes)
                    try:
                        #self.packet.pkData = []
                        #for x in range(0,self.packet.pkBytes):
                        #    b = ser.read(1)
                        #    self.packet.pkData.append(unpack('>B',b)[0])
                        d = ser.read(self.packet.pkBytes)
                        self.packet.pkData = d
                        self.pkState = IMUPacketRead.sPkCRC
                        #self.pkState = IMUPacketRead.sPkDone
                        if self.verbose:
                            print ("Going to PkDone")
                    except:
                        '''
                        What happens if I time out... want to handle this someday
                        '''
                        self.pkState = IMUPacketRead.sStart
                        print("Exception while reading packet data")
                else:
                    self.pkState = IMUPacketRead.sPkDone
                    if self.verbose:
                        print ("Packet Size == 0, Returning to Start")
            elif self.pkState == IMUPacketRead.sPkCRC:
                pkWD = ser.read(1)
                self.packet.WatchDog = unpack('>B',pkWD)[0]
                pkCRC = ser.read(2)
                self.packet.pkCRC = unpack('>H',pkCRC)[0]
                if self.verbose:
                    print("CRC Code:0x%x" % self.packet.pkCRC)
                self.pkState = IMUPacketRead.sPkDone
                if self.verbose:
                    print ("Going to PkDone")

            if self.pkState == IMUPacketRead.sPkDone:
                self.isValidPacket = True

        return self.isValidPacket

    def Clear(self):
        self.isValidPacket = False
        self.packet = IMUPacket()
        self.pkState = IMUPacketRead.sStart
