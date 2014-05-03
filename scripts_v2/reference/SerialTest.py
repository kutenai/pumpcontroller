#!/usr/bin/env python

import serial
import platform
import glob
import time
import re

class PumpAPI(object):

    def __init__(self):
        super(PumpAPI,self).__init__()
        self.ser = None
        try:
            self.setupSerial(False)
        except:
            raise "Could not open serial port!"

    def setupSerial(self,bFast = False):

        if bFast:
            self.baudrate = 115200
        else:
            self.baudrate = 9600

        print("Baud Rate set to %d" % self.baudrate)

        port = self.getPorts()
        if self.ser:
            ''' Reset to new baud rate '''
            print("Closed existing port.")
            self.ser.close()
            self.ser = None
            self.ser = serial.Serial(port,self.baudrate,timeout = 1)
            print ("Re-opened port at different baud rate")
            self.initHardware()
        else:
            self.ser = serial.Serial(port,self.baudrate, timeout = 1)
            self.ser.open()
            print("Opened port %s" % port)

    def sendPacket(self,packet):
        self.ser.write(packet)

        while (1):
            t = time.time()
            retval = self.ser.readline()

            try:
                tdiff = time.time() - t
                if tdiff > 1.0:
                    print("Timeout probably occurred:%f" % tdiff)
                    return None

                retval = retval.decode()
                m = re.search("(\d+),(.*);",retval,re.IGNORECASE)
                if m:
                    #print("{0} Result:{1}".format(packet.decode(),retval))
                    break
                else:
                    #print("{0}".format(retval))
                    pass
            except:
                # Invalid format, cannot decode it..
                break


        return retval

    def initHardware(self):
        '''
        The first time we write to the hardware it appears that the FTDI chip resets
        it.. this has been problematic. It requires about 3 seconds for the hardware
        to come up, so I do a write, then a read with a long timeout, and see what happens.
        This should insure we are ready to run....
        '''
        self.ser.timeout = 3

        self.sendPacket(b'7;\n')

        self.ser.timeout = 1

    def getSensorData(self):

        retval = self.sendPacket(b'7;\n')
        if retval:
            m = re.search("(\d+),(\d+),(\d+);",retval)
            if m:
                dt = m.group(1)
                sensor1 = int(m.group(2))
                sensor2 = int(m.group(3))

                data = {
                    "response": dt,
                    "sensor1": sensor1,
                    "sensor2": sensor2
                }

                return data
            else:
                return None
        else:
            return None

    def getPorts(self):
        if platform.system() == 'Darwin':
            """scan for available ports. return a list of device names."""
            ports = glob.glob('/dev/tty.usbserial-A600*')
            return ports[0]
        elif platform.system() == 'Windows':
            return "COM10" # No super good way to determine this..

def main():
    api = PumpAPI()
    api.initHardware()
    s = api.getSensorData()
    if s:
        print ("Sensor Data returned %s" % s)
    else:
        print( "Nothing returned.")

def rangeTest():
    api = PumpAPI()
    api.initHardware()

    numOk = 0
    numBad = 0
    s1 = 0
    s2 = 0
    while True:
        s = api.getSensorData()
        if s:
            numOk += 1
            s1 = s['sensor1']
            s2 = s['sensor2']
        else:
            numBad += 1

        #print ("Sensor1: %d Sensor2: %d Good: %d Bad:%d" % (s1,s2,numOk,numBad))
        print ("Ditch Sensor: %d Sump Sensor: %d" % (s1, s2))
        time.sleep(0.5)

        """
        Sump Sensor Readings:
        Nominal, full ditch: 756
        Absolute bottom - 50
        Absolute top - 930

        Ditch Sensor:
        1/4" below dam slot - 473

        Sensor Match:
        Ditch   Sump
        482     777



        """


if __name__ == "__main__":
    #main()
    rangeTest()
