import json
import math
import machine
from machine import Pin
from machine import Timer
from mqtt import MQTTClient
from network import WLAN
import pycom
import time


def onoff(x):
    """ Translate pin value to message string """
    if x == 0:
        return b"ON"
    return b"OFF"


class DitchController:
    """ Control the Ditch at my house """

    def __init__(self, ditch_pin="P13", sump_pin="P16",
                  pump_pin="P19", south_pin="P20", north_pin="P21",
                  cals='/sd/calibration/cal.json'):

        adc = machine.ADC()
        self.adc_ditch = adc.channel(pin=ditch_pin)
        self.adc_sump = adc.channel(pin=sump_pin)
        self.ctl_pump = Pin(pump_pin, mode=Pin.OPEN_DRAIN)
        self.ctl_south = Pin(south_pin, mode=Pin.OPEN_DRAIN)
        self.ctl_north = Pin(north_pin, mode=Pin.OPEN_DRAIN)

        self.ctl_pump(1)
        self.ctl_south(1)
        self.ctl_north(1)

        self._ditch_level = self.ditch_level()
        self._sump_level = self.sump_level()
        self._diff_trigger = 0.05
        self._last_published = time.time()

        self.enable_publish = True
        self.publish_timer = None
        self._publish_maxtime = 60

        self.topic_vector = {
            b"kutenai/feeds/pump": self.pump_command_handler,
            b"kutenai/feeds/north": self.north_command_handler,
            b"kutenai/feeds/south": self.south_command_handler,
        }

        self.read_calibrations(cals)

    def connect(self):
        self.client = MQTTClient("ditch_client", "io.adafruit.com", port=1883,
                                 user="kutenai",
                                 password="2aea0e47611f4f36a221bccf8c23ed7d")
        self.client.set_callback(self.ditch_command_handler)
        self.client.connect()
        print("Connected to mqtt server")
        self.subscribe()
        self.publish_controls(get=True)

        if self.publish_timer:
            self.publish_timer.cancel()

        self.setup_publish_timer()

    def read_calibrations(self, file):
        """ Read the calibration values from the file """

        with open(file, 'r') as fp:
            data = json.load(fp)

    def write_calibration_pair(self, file, type='ditch', x=None,  y=None):
        """ Write a calibration pair to the file """

        with open(file, 'r') as fp:
            data = json.load(fp)

        d = data.get(type, [])
        d.append([x, y])

        if type not in data:
            data[type] = d

        with open(file, 'w') as fp:
            fp.write(json.dumps(data))

    def publish_timer_handler(self, arg):
        """ Called by Alarm interrupt to indicate time to publish levels """
        self.enable_publish = True

    def setup_publish_timer(self):
        """ Setup a timer to enable publishing every N seconds """
        self.publish_timer = Timer.Alarm(self.publish_timer_handler, 10, periodic=True)

    def ditch_level(self):
        val = self.adc_ditch()
        print("ADC Ditch {:4.2}".format(val))
        val = 12.0 * val / 4095
        return val

    def sump_level(self, show=True):
        val = self.adc_sump()
        if show:
            print("ADC Sump {:4.2}".format(val))
        val = 26 * val / 4095
        return val

    def ditch_command_handler(self, topic, msg):
        print("Topic:{} Msg:{}".format(topic, msg))
        if topic in self.topic_vector:
            bOn = msg == b"ON"
            self.topic_vector[topic](bOn)

    def pump_command_handler(self, on=False):
        self.ctl_pump(0 if on else 1)

    def north_command_handler(self, on=False):
        self.ctl_north(0 if on else 1)

    def south_command_handler(self, on=False):
        self.ctl_south(0 if on else 1)

    def toggle_pump(self):
        self.ctl_pump.toggle()

    def toggle_north(self):
        self.ctl_north.toggle()

    def toggle_south(self):
        self.ctl_south.toggle()

    def subscribe(self):
        self.client.subscribe(topic="kutenai/feeds/pump")
        self.client.subscribe(topic="kutenai/feeds/north")
        self.client.subscribe(topic="kutenai/feeds/south")

    def publish_controls(self, get=True):
        if get:
            self.client.publish(topic="kutenai/feeds/pump/get", msg='\0')
            self.client.publish(topic="kutenai/feeds/north/get", msg='\0')
            self.client.publish(topic="kutenai/feeds/south/get", msg='\0')
        else:
            self.client.publish(topic="kutenai/feeds/pump", msg=onoff(self.ctl_pump()))
            self.client.publish(topic="kutenai/feeds/north", msg=onoff(self.ctl_north()))
            self.client.publish(topic="kutenai/feeds/south", msg=onoff(self.ctl_south()))

    # Setup our publish Timer
    def update_levels(self):
        """ Query current levels. Publish them if they have changed, or our publish timeout occurs """
        ditch = self.ditch_level()
        sump = self.sump_level()
        publish = abs(self._ditch_level-ditch) > self._diff_trigger
        publish = publish or abs(self._sump_level-sump) > self._diff_trigger
        if publish:
            print("Publish flag set, so ditch levels must be different")
            print("Ditch Levels: {} {}".format(self._ditch_level, ditch))
            print("Sump Levels: {} {}".format(self._sump_level, sump))
        if (time.time() - self._last_published) > self._publish_maxtime:
            print("It's been a while since we publisehd, so publishing again")

        if publish or (time.time() - self._last_published) > self._publish_maxtime:
            self.publish_levels()

    def publish_levels(self):
        print("Sending ditch and sump levels")
        self._ditch_level = self.ditch_level()
        self._sump_level = self.sump_level()
        self.client.publish("kutenai/feeds/ditch", "{:5.2f}".format(self._ditch_level))
        self.client.publish("kutenai/feeds/sump", "{:5.2f}".format(self._sump_level))
        self._last_published = time.time()

    def loop(self):
        """
        Called repeatedly in the main loop
        Enable publish is set by a timer
        """
        try:
            self.client.check_msg()

            if self.enable_publish:
                self.update_levels()
                self.enable_publish = False
        except OSError as e:
            """ Occurs with error in wait_msg """
            # Not sure what the proper recovery is.. so I'll disconnect and re-connection
            print("***** Warning.... Received an OSError. Resetting MQTT Client ******")
            self.client.disconnect()
            self.connect()
            print("MQTT Client Re-connected")
