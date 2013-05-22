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
        self.port = None
        self.printer = None


    def setPrintObj(self,pobj):

        self.printer = pobj

    def lprint(self,txt):

        if self.printer:
            self.printer.lprint(txt)
        else:
            print(txt)

    def Initialize(self):
        """
        Initialzie the serial port.
        """

        try:
            self.setupSerial(False)
        except:
            raise "Could not open serial port!"


    def setupSerial(self,bFast = False):
        """
        Determine the serial port, then open that port with the default
        buad rate.
        """

        if bFast:
            self.baudrate = 115200
        else:
            self.baudrate = 9600

        self.port = self.getPorts()

        if self.ser:
            ''' Reset to new baud rate '''
            self.lprint("Closed existing port.")
            self.ser.close()
            self.ser = None
            self.ser = serial.Serial(self.port,self.baudrate,timeout = 1)
            self.ser.open()
            self.lprint ("Re-opened port at different baud rate")

        else:
            self.ser = serial.Serial(self.port,self.baudrate, timeout = 1)
            self.open()
            self.lprint("Opened port %s" % self.port)

    def close(self):
        """
        Close the serial connection
        """
        self.ser.close()


    def open(self):
        """
        Open the serial connection
        """

        self.ser.open()


    def setLastResult(self,res):
        self.lastResult = res

    def getLastResult(self):
        return self.lastResult

    def sendPacket(self,packet):
        """
        Send a packet of data.
        Append a newline if not already present.


        """


        if packet[-1] != '\n':
            packet = packet + '\n'

        self.ser.write(packet)

        self.setLastResult(None)

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
                try:
                    data = dict(item.split(":") for item in re.split('\s', result))
                except:
                    continue
                return data
            retries -= 1
            #print("Retries..")

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
        """
        Re-usable function that sends a boolean value as a 1 or a 0.

        """

        if bOn:
            self.sendPacket('%s 1' % cmd)
            self.lprint("Set %s to on" % cmd)
        else:
            self.sendPacket('%s 0' % cmd)
            self.lprint("Set %s to on" % cmd)

    def pumpEnable(self,bEnable):
        """
        Send the pump enable signal. Can be true or false to enable or disable the pump.

        """
        self.sendBool('pump',bEnable)

    def getStatus(self,cmd):
        """
        Return the status of the specified command.
        Valid commands are pump, north or south.
        """

        data = {
            'call' : -1,
            'actual' : -1
        }

        if cmd in ['pump','north','south']:
            if self.sendPacket(b'%s?' % cmd):
                result = re.split("\s",self.getLastResult())
                data['call'] = result[0]
                data['actual']= result[1]

        return data


    def isPumpOn(self):
        return self.getStatus('pump')['actual'] == '1'

    def isNorthOn(self):
        return self.getStatus('north')['actual'] == '1'

    def isSouthOn(self):
        return self.getStatus('south')['actual'] == '1'

    def getPumpStatus(self):
        return self.getStatus('pump')

    def getNorthStatus(self):
        return self.getStatus('north')

    def getSouthStatus(self):
        return self.getStatus('south')

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


    print("Pump Call:" + api.getPumpStatus()['call'])
    api.pumpEnable(True)
    print("Pump Call:" + api.getPumpStatus()['call'])
    api.pumpEnable(False)
    print("Pump Call:" + api.getPumpStatus()['call'])

    print("North Call:" + api.getNorthStatus()['call'])
    api.northEnable(True)
    print("North Call:" + api.getNorthStatus()['call'])
    api.northEnable(False)
    print("North Call:" + api.getNorthStatus()['call'])

    print("South Call:" + api.getSouthStatus()['call'])
    api.southEnable(True)
    print("South Call:" + api.getSouthStatus()['call'])
    api.southEnable(False)
    print("South Call:" + api.getSouthStatus()['call'])

if __name__ == '__main__':
    main()
