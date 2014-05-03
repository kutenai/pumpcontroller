import platform
import glob
import time
import re
from xbee import ZigBee,python2to3
import serial

class ZBCommand(object):

    def __init__(self,cmd,param):

        self.cmd = cmd
        self.param = param

class DitchDummy(object):

    devices = {
        "coord": '\x00\x13\xa2\x00\x40\x9e\x0e\x94',
        "ditch": '\x00\x13\xa2\x00\x40\x9e\x0e\xa4'
    }

    def __init__(self, async = False):
        super(DitchDummy,self).__init__()
        self.ser = None
        self.xbee = None
        self.frameid = 1
        self.isAsync = async

        self.dataBuffer = []
        try:
            self.setupSerial(False)
        except:
            raise "Could not open serial port!"

        #self.setupConnection()

    def __delete__(self):

        self.halt()

    def nextFrameid(self):

        self.frameid = (self.frameid + 1) % 255
        #return python2to3.intToByte(self.frameid)
        return '3'

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
            self.ser = serial.Serial(port, self.baudrate,timeout = 1)
            print ("Re-opened port at different baud rate")
            self.initHardware()
        else:
            self.ser = serial.Serial(port, self.baudrate, timeout = 1)
            self.ser.open()
            print("Opened port %s" % port)

            if self.isAsync:
                self.xbee = ZigBee(self.ser, callback=self.onData)
            else:
                self.xbee = ZigBee(self.ser)


    def onData(self,data):

        print ("Got some data:")
        self.dataBuffer.append(data)

    def sendDitchStatus(self):
        self.xbee.tx(dest_addr_long=DitchDummy.devices['coord'],
                     dest_addr='\xFF\xFF',
                            data="ThisIsATest",
                            frame_id=self.nextFrameid())

    def readData(self):

        data = self.xbee._wait_for_frame()
        return data

    def getPorts(self):
        if platform.system() == 'Darwin':
            """scan for available ports. return a list of device names."""
            ports = glob.glob('/dev/tty.usbserial-A6007W*')
            return ports[0]
        elif platform.system() == 'Windows':
            return "COM10" # No super good way to determine this..

def waitkey():
    while True:
        try:
            time.sleep(0.001)
        except KeyboardInterrupt:
            break



def main():

    api = DitchDummy(True)
    api.sendDitchStatus()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
        api.sendDitchStatus()

if __name__ == '__main__':
    main()
