#!/usr/bin/env python
__author__ = 'kutenai'


import json
import time
import httplib, urllib
from IrrigationAPIAT import IrrigationAPI
from DBConnection import DBConnection
from DBDitch import DBDitch

import plotly

"""
Feed id: 127898

POST /v2/feeds
First let's create an empty feed template. We'll just give it a 'title' and 'version' for now and specify the rest later.

{"title":"My feed", "version":"1.0.0"}

An example using curl is:

curl --request POST \
--data '{"title":"My feed", "version":"1.0.0"}' \
--header "X-ApiKey: YOUR_API_KEY_HERE" \
--verbose \
http://api.cosm.com/v2/feeds

Update your feed
PUT /v2/feeds/YOUR_FEED_ID
Now let's update your feed and its datastreams. We'll set up three datastreams with unique datastream ids.

{
"version":"1.0.0",
"datastreams":[
{"id":"0", "current_value":"100"},
{"id":"two", "current_value":"500"},
{"id":"3.0", "current_value":"300"}
]
}
Let's save this to a file called cosm.json.

We can get the id of your feed (referred to as YOUR_FEED_ID below) from your 'my feeds' page in Cosm or in the response header from curl above.

To update the feed using curl is:

curl --request PUT \
--data-binary @cosm.json \
--header "X-ApiKey: YOUR_API_KEY_HERE" \
--verbose \
http://api.cosm.com/v2/feeds/YOUR_FEED_ID

We can now update the values and repeat this request whenever required.

URL: http://api.cosm.com/v2/feeds/127898
API_KEY: TMEpzWw_F5H38h2qhRc0ZJPbsi-SAKxaYUtja2pqM1RFQT0g
"""


class DitchLogger(object):
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

    def __init__(self,api = None):
        self.hi = True

        if not api:
            self.api = IrrigationAPI()
        else:
            self.api = api

        self.conn = None
        self.dbTable = None

        self.printer = None

        self.apikey = "d8ytNTiS45sNRIVqsluvbDTlW2eSAKxJVUNVamJLUmtJZz0g"

        self.feedid = 121835

        self.feedHist = {

        }

        self.py = plotly.plotly(username_or_email='kutenai',key='xhhbxk2swl')

    def setPrintObj(self,pobj):

        self.printer = pobj

    def lprint(self,txt):

        if self.printer:
            self.printer.lprint(txt)
        else:
            print(txt)

    def InitializeDB(self):
        """
        Initialize the DB Connection for logging
        """

        self.conn = DBConnection()
        self.dbTable = DBDitch(self.conn)


    def ditchInches(self,reading):

        m = 0.011974658
        intercept = 17.5
        return intercept - m*int(reading)

    def sumpInches(self,reading):

        m = 0.037290516
        inches = m* int(reading)
        return inches

    def _logStream(self,feedid,id,val):
        """
        Low-level log, no history
        """

        data = {
            'id' : id,
            "current_value" : val
        }

        jsons = json.dumps(data)
        headers = {"Content-type": "application/json",'X-ApiKey': self.apikey }
        conn = httplib.HTTPConnection("api.cosm.com")
        conn.request("PUT", "/v2/feeds/%d/datastreams/%s" % (feedid,id), jsons, headers)
        response = conn.getresponse()

        if response.status == 200:
            self.lprint ("Logged To Feedid %d Stream %s => %s" % (feedid,id,val))
            return True
        else:
            self.lprint(response.status, response.reason)
            data = response.read()
            self.lprint('Response:' + data)

            conn.close()

        return False


    def logStream(self, feedid, id, val):
        """
        Log the stream to the given feedid and id.

        Use a history mechanism to keep from re-logging identical values, however,
        if you don't log a value for a while and the previous value has changed.. then
        log the previous value again, and the new value.
        """

        if self.feedHist.has_key(id):
            fh = self.feedHist[id]
            if fh['val'] == val: # No change
                return
            lastUpdateDuration = time.time() - fh['lastupdate']
        else:
            self.feedHist[id] = {
                'val' : None,
                'lastupdate' : None
            }
            lastUpdateDuration = 0

        fh = self.feedHist[id]

        if lastUpdateDuration > 60:
            # Log the previous value to update the time.
            self._logStream(feedid, id, fh['val'])

        if self._logStream(feedid, id, val):
            fh['val'] = val
            fh['lastupdate'] = time.time()


    def logBoolStream(self,feedid,id,bIn):
        """
        Convert a boolean value to a 1 or a 0 and log the stream
        """
        bval = 0
        if bIn:
            bval = 1

        self.logStream(feedid,id,bval)


    def logResultsCosm(self,ditch,sump):
        feedid = self.feedid
        self.logStream(feedid,'ditch_level',self.ditchInches(ditch))
        self.logStream(feedid,'sump_level', self.sumpInches(sump))

    def logSystemStatus(self,pumpOn, northOn, southOn):
        feedid = self.feedid
        self.logBoolStream(feedid, 'pump_on', pumpOn)
        self.logBoolStream(feedid, 'north_on', northOn)
        self.logBoolStream(feedid, 'south_on', southOn)

    def logResultsDB(self,ditch,sump, pump,north,south):
        """
        Dump all information to the database.
        """

        if not self.conn:
            self.InitializeDB()

        if self.conn and self.dbTable:
            self.dbTable.insertLogEntry(
                int(ditch), int(sump),
                self.ditchInches(ditch),
                self.sumpInches(sump),
                int(pump), int(north), int(south)
            )

            self.lprint("Logged to Database.")


    def logLevels(self):
        vals = self.api.getSensors()

        if vals:
            self.logResults(vals['ditch'],vals['sump'])


    def logSome(self,interval,count):
        """
        Script is called once a minute.. so, log every 10 seconds
        5 times.
        """

        self.api.Initialize()

        while count:
            try:
                self.api.open()
                self.logLevels()
                self.api.close()
                time.sleep(interval)
                count -= 1
            except KeyboardInterrupt:
                break

        self.api.close()


def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    lgr = DitchLogger()


    lgr.logSome(10,5)


if __name__ == "__main__":
    main()
