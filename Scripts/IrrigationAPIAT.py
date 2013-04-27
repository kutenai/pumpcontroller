import serial
import platform
import glob
import time
import re

class IrrigationAPI(object):

    def __init__(self):
        super(IrrigationAPI,self).__init__()
        self.ser = None
        self.lastResult = None
        try:
            self.setupSerial(False)
        except:
            raise "Could not open serial port!"

    def setupSerial(self,bFast = False):

        if bFast:
            self.baudrate = 115200
        else:
            self.baudrate = 9600

        #print("Baud Rate set to %d" % self.baudrate)

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

    def setLastResult(self,res):
        self.lastResult = res

    def getLastResult(self):
        return self.lastResult

    def sendPacket(self,packet):


        if packet[-1] != '\n':
            packet = packet + '\n'

        self.ser.write(packet)

        self.setLastResult(None)

        tstart = time.time()

        while True:
            t = time.time()
            retval = self.ser.readline()

            try:
                tdiff = time.time() - t
                if tdiff > self.ser.timeout:
                    self.ser.write(packet)
                    continue

                retval = retval.decode()
                m = re.search("(Ok|Fail):?(.*)", retval, re.IGNORECASE)
                if m:
                    #print("{0} Result:{1}".format(packet.decode(),retval))
                    pf = m.group(1)
                    res = m.group(2)
                    self.setLastResult(res)
                    return pf == 'Ok'
            except:
                # Invalid format, cannot decode it..
                continue

        return False

    def getSystemStatus(self,retries=10):
        """
        Request the status of the system. Returns a string with
        information about each item
        Ditch:%d Sump:%d PC:%d P:%d NC:%d N:%d SC:%d S:%d ST:%d STen

        Ditch = ditch level in analog value
        Sump = sump level value
        PC = pump call
        P = pump actual
        NC = North Call, N = North Actual
        SC = South Call, S = South actual
        ST = Sump trigger level
        STen = Sump trigger enable
        """

        while retries:
            if self.sendPacket(b'status'):
                result = self.getLastResult()
                data = dict(item.split(":") for item in re.split('\s',result))
                return data
            retries -= 1

        return None

    def getSensors(self,retries=10):
        """
        Request the status of the sensors.

        Returns space seperated values:
         ditch sump
        """

        while retries:
            if self.sendPacket(b'levels'):
                result = re.split("\s",self.getLastResult())
                data = {
                    'ditch' : result[0],
                    'sump' : result[1]
                }
                return data
            retries -= 1

        return None

    def sendBool(self,cmd,bOn):

        if bOn:
            self.sendPacket('%s 1' % cmd)
        else:
            self.sendPacket('%s 0' % cmd)

    def pumpEnable(self,bEnable):
        self.sendBool('pump',bEnable)

    def getStatus(self,cmd):
        data = {
            'call' : -1,
            'actual' : -1
        }
        if self.sendPacket(b'pump?'):
            result = re.split("\s",self.getLastResult())
            data['call'] = result[0]
            data['actual']= result[1]

        return data


    def isPumpOn(self):
        return self.getStatus('pump?')

    def isNorthOn(self):
        return self.getStatus('north?')

    def isSouthOn(self):
        return self.getStatus('south?')

    def northEnable(self,bEnable):
        self.sendBool('north',bEnable)

    def southEnable(self,bEnable):
        self.sendBool('south',bEnable)

    def sumpTriggerEnable(self,bEnable):
        self.sendBool('sump_trig_en',bEnable)

    def sumpTriggerLevel(self,lvl):
        self.sendPacket('sump_trigger %d' % lvl)

    def getPorts(self):
        if platform.system() == 'Darwin':
            """scan for available ports. return a list of device names."""
            ports = glob.glob('/dev/tty.usbserial-A600*')
            return ports[0]
        elif platform.system() == 'Windows':
            return "COM10" # No super good way to determine this..


def main():

    api = IrrigationAPI()

    stat = api.getSystemStatus()
    if stat:
        print ("System Status:")
        for key,val in stat.iteritems():
            print ("%s => %s" % (key,val))

    sensors = api.getSensors()
    if sensors:
        print ("Sensor Levels:")
        for key,val in sensors.iteritems():
            print ("%s => %s" % (key,val))
    else:
        print("No Sensor levels returned")


    print("Pump Call:" + api.isPumpOn()['call'])
    api.pumpEnable(True)
    print("Pump Call:" + api.isPumpOn()['call'])
    api.pumpEnable(False)
    print("Pump Call:" + api.isPumpOn()['call'])

    print("North Call:" + api.isNorthOn()['call'])
    api.northEnable(True)
    print("North Call:" + api.isNorthOn()['call'])
    api.northEnable(False)
    print("North Call:" + api.isNorthOn()['call'])

    print("South Call:" + api.isSouthOn()['call'])
    api.southEnable(True)
    print("South Call:" + api.isSouthOn()['call'])
    api.southEnable(False)
    print("South Call:" + api.isSouthOn()['call'])

if __name__ == '__main__':
    main()
