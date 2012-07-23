import serial
import platform
import glob
import time
import re

class IrrigationAPI(object):

    def __init__(self):
        super(IrrigationAPI,self).__init__()
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

        retval = ""

        tstart = time.time()

        while (1):
            t = time.time()
            retval = self.ser.readline()

            try:
                tdiff = time.time() - t
                if tdiff > self.ser.timeout:
                    #print("Timeout probably occurred:%f" % tdiff)
                    self.ser.write(packet)
                    continue

                retval = retval.decode()
                m = re.search("(\d+),(.*);",retval,re.IGNORECASE)
                if m:
                    #print("{0} Result:{1}".format(packet.decode(),retval))
                    return retval
            except:
                # Invalid format, cannot decode it..
                continue

        return retval

    def initHardware(self):
        '''
        The first time we write to the hardware it appears that the FTDI chip resets
        it.. this has been problematic. It requires about 3 seconds for the hardware
        to come up, so I do a write, then a read with a long timeout, and see what happens.
        This should insure we are ready to run....
        '''
        self.ser.timeout = 1

        self.sendPacket(b'7;\n')

        self.ser.timeout = 0.1

    def getSystemStatus(self,retries=10):

        # Expected response example:
        # D:530 S:529 PC:1 P:1 NC:0 N:0 SC0: S:0 ST:0 STen:0;
        while retries:
            retval = self.sendPacket(b'7;\n')
            if retval:
                m = re.search("1,\s*(.*)\s*;\s*",retval)
                if m:
                    status = m.group(1)
                    pairs = re.split("\s+",status)
                    data = {}
                    for pair in pairs:
                        key,val = re.split(":",pair)
                        data[key] = val

                    return data
            retries -= 1

        return None
    def getSensorData(self,retries=10):

        while retries:
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
            retries -= 1

    def pumpEnable(self,bEnable):

        if bEnable:
            self.sendPacket('4,on;\n')
        else:
            self.sendPacket('4,off;\n')

    def northZoneEnable(self,bEnable):

        if bEnable:
            self.sendPacket('6,on;\n')
        else:
            self.sendPacket('6,off;\n')

    def southZoneEnable(self,bEnable):

        if bEnable:
            self.sendPacket('5,on;\n')
        else:
            self.sendPacket('5,off;\n')

    def getPorts(self):
        if platform.system() == 'Darwin':
            """scan for available ports. return a list of device names."""
            ports = glob.glob('/dev/tty.usbserial-A600*')
            return ports[0]
        elif platform.system() == 'Windows':
            return "COM10" # No super good way to determine this..
