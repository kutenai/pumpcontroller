import platform
import glob
import time
import re
from xbee import ZigBee
import serial

class ZBCommand(object):

    def __init__(self,cmd,param):

        self.cmd = cmd
        self.param = param

class IrrigationAPI(object):

    devices = {
        "coord": '\x00\x13\xa2\x00\x40\x9e\x0e\x94',
        "ditch": '\x00\x13\xa2\x00\x40\x9e\x0e\xa4'
    }

    def __init__(self, async = False):
        super(IrrigationAPI,self).__init__()
        self.ser = None
        self.xbee = None
        self.frameid = 1
        self.isAsync = async

        self.dataBuffer = []

    def __delete__(self):

        self.halt()

    def nextFrameid(self):
        """
        Increment the frame id, but keep the frame to
        just a single byte.

        """

        self.frameid = (self.frameid + 1) % 255
        return "%d" % self.frameid

    def Initialize(self):
        """
        Initialize and open the serial port. Needs to be done one time.
        """
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

    def writeDitchCmd(self,cmd,param):

        self.xbee.remote_at(dest_addr_long=devices['ditch'],command=cmd,parameter=param)

    def writeDitchCmds(self,cmds):

        for cmd in cmds:
            self.writeDitchCmd(cmd.cmd,cmd.param)

    def setupConnection(self):
        """
        The Zigbee modules require a connection setup.
        If I name the nodes, then it is easier.

        For not the Ditch node is named 'DITCH', so I can issue the following
        command to set the coordinator to talk to the ditch node:

        +++
        ATDN DITCH
        ATCN

        That puts the coordinator into command mode, sets the destination node to 'DITCH',
        and then exits command mode.
        """



        self.xbee.send('at', command="NI")
        data = self.xbee.wait_read_frame()

        print ("Results are here:" + data['parameter'])

        #self.atCommands(['ATDN DITCH'])

    def getNodeIdentifier(self):
        self.xbee.send('at', command="NI",
                        frame_id=self.nextFrameid())
        data = self.xbee.wait_read_frame()

        return data['parameter']

    def getDestNodeIdentifier(self):
        self.xbee.remote_at(dest_addr_long=IrrigationAPI.devices['ditch'],
                            command="NI",
                            frame_id=self.nextFrameid())
        data = self.xbee.wait_read_frame()

        return data['parameter']

    def getDitchStatus(self):
        self.xbee.tx(dest_addr_long=IrrigationAPI.devices['ditch'],
                     dest_addr='\xFF\xFF',
                            data=b'7;\n',
                            frame_id=self.nextFrameid())
        #resp = self.xbee.wait_read_frame()
        #data = self.xbee.wait_read_frame()

        #print("Did it work")
        #return data['parameter']

    def readData(self):

        data = self.xbee._wait_for_frame()
        return data

    def sendData(self):

        self.xbee.tx(dest_addr_long=IrrigationAPI.devices['ditch'],
                     dest_addr='\xFF\xFF',
                     data=b'7;\n',
                     frame_id=self.nextFrameid())


    def networkDiscovery(self):
        self.xbee.send('at',command="ND",
                            frame_id=self.nextFrameid())
        #data1 = self.xbee.wait_read_frame()
        #data2 = self.xbee.wait_read_frame()

        #return data1['parameter']
        return None

    def halt(self):

        self.xbee.halt()
        self.ser.close()

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
            ports = glob.glob('/dev/tty.usbserial-A600dS*')
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

    api = IrrigationAPI(True)
    #d = api.getSensorData()

    doDiscovery = False
    if doDiscovery:
        api.networkDiscovery()
        waitkey()
        api.halt()
        return

    #api.getDitchStatus()
    #waitkey()
    while True:
        try:
            #data = api.readData()
            api.sendData()
            print("Send data")
            time.sleep(1)
        except:
            print ("No data..")
    time.sleep(3)
    api.halt()
    return


    ni = api.getNodeIdentifier()

    print ("Node identifier:%s" % ni)

    nid = api.getDestNodeIdentifier()
    print ("Dest Node identifier:%s" % nid)
    return


if __name__ == '__main__':
    main()
