#!/usr/bin/env python

__author__ = 'kutenai'

from DitchRedisHandler import DitchRedisHandler

class DitchController(DitchRedisHandler):
    """
    Ditch Logger runs one time, reads the sensor levels, and logs
    them to the COSM site.



    The Monitor performs the following checks
    - Log the ditch and sump levels.
    - turn off the pump, and both valves if the water level is too low.
    - apply any rules to turn ON the values..

    The Monitor will report issues via e-mail. A follow-up e-mail
    is sent every 15 minutes. If the error list changes, a new
    e-mail is sent.

    """

    def __init__(self):
        super(DitchController, self).__init__('localhost', 6388, 0)
        self.hi = True
        self.redisConnect()

    def setRequest(self,key,val):

        req = key + 'request'
        if val:
            self.redis.set(req,1)
            print ("Set %s to 1" % req)
        else:
            self.redis.set(req,0)
            print ("Set %s to 0" % req)

    def allOff(self):
        print("Setting all controls to off.")
        self.setRequest('pump',False)
        self.setRequest('north',False)
        self.setRequest('south',False)

    def runNorth(self):
        print("Turning on North Zone.")
        self.setRequest('pump',True)
        self.setRequest('north',True)
        self.setRequest('south',False)


    def runSouth(self):
        print("Turning on South Zone.")
        self.setRequest('pump',True)
        self.setRequest('north',False)
        self.setRequest('south',True)


    def southEnable(self, bOn):
        if bOn:
            self.setRequest('south', True)
        else:
            self.setRequest('south', False)


    def pumpEnable(self, bOn):
        if bOn:
            self.setRequest('pump', True)
        else:
            self.setRequest('pump', False)


    def northEnable(self, bOn):
        if bOn:
            self.setRequest('north', True)
        else:
            self.setRequest('north', False)


    def southEnable(self, bOn):
        if bOn:
            self.setRequest('south', True)
        else:
            self.setRequest('south', False)


    def isPumpOn(self):
        return self.redis.get('pumpon') != '0'


    def isNorthOn(self):
        return self.redis.get('northon') != '0'


    def isSouthOn(self):
        return self.redis.get('southon') != '0'


    def showLevels(self):
        d = self.redis.get('ditch')
        s = self.redis.get('sump')
        di = self.redis.get('ditch_inches')
        si = self.redis.get('sump_inches')

        print("Ditch is %s\" (%d)" % (di, int(d)))
        print("Sump is %s\" (%d)" % (si, int(s)))


    def getSystemValue(self, key, default):
        val = self.redis.get(key)
        if val == None:
            val = default
            self.lprint("Setting %s to default value of %s" % (key,default))
            self.redis.set(key, val)

        return val


    def getSystemStatus(self):
        stat = {
            'ditch': self.getSystemValue('ditch', 0),
            'sump': self.getSystemValue('sump', 0),
            'ditch_in': self.getSystemValue('ditch_inches', 0.0),
            'sump_in': self.getSystemValue('sump_inches', 0.0),
            'pumpcall': self.getSystemValue('pumpcall', 0),
            'northcall': self.getSystemValue('northcall', 0),
            'southcall': self.getSystemValue('southcall', 0),
            'pumpon': self.getSystemValue('pumpon', 0),
            'northon': self.getSystemValue('northon', 0),
            'southon': self.getSystemValue('southon', 0)
        }
        return stat


    def showSystemStatus(self):
        print("Showing System Status:")
        stat = self.getSystemStatus()

        print("Pump: Call:%s On:%s" % (stat['pumpcall'], stat['pumpon']))
        print("North: Call:%s On:%s" % (stat['northcall'], stat['northon']))
        print("South: Call:%s On:%s" % (stat['southcall'], stat['southon']))
        print("Ditch: %s\" (%d)" % (stat['ditch_in'], int(stat['ditch'])))
        print("Sump: %s\" (%d)" % (stat['sump_in'], int(stat['sump'])))


    def lprint(self, string):
        print(string)
