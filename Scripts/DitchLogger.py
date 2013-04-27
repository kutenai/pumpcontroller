__author__ = 'kutenai'


import json
import httplib, urllib
from IrrigationAPIAT import IrrigationAPI

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

    def __init__(self):
        self.hi = True

        self.apikey = "d8ytNTiS45sNRIVqsluvbDTlW2eSAKxJVUNVamJLUmtJZz0g"


    def logStream(self,feedid,id,val):
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
            print ("Logged To Feedid %d Stream %s => %s" % (feedid,id,val))
        else:
            print response.status, response.reason
            data = response.read()
            print('Response:' + data)

        conn.close()


    def logResults(self,ditch,sump):
        feedid = 121835
        self.logStream(feedid,'ditch_level',ditch)
        self.logStream(feedid,'sump_level', sump)


    def logResults2(self,ditch):
        feedid = 127898
        self.logStream(feedid,'ditch_level',ditch)

def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    api = IrrigationAPI()
    vals = api.getSensors()

    if vals:
        dl = DitchLogger()
        dl.logResults(vals['ditch'],vals['sump'])
        dl.logResults2(vals['ditch'])


if __name__ == "__main__":
    main()
