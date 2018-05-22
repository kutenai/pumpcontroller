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
                  pump_pin="P19", south_pin="P20", north_pin="P21"):

        adc = machine.ADC()
        self.adc_ditch = adc.channel(pin=ditch_pin)
        self.adc_sump = adc.channel(pin=sump_pin)
        self.ctl_pump = Pin(pump_pin, mode=Pin.OPEN_DRAIN, pull=Pin.PULL_UP)
        self.ctl_south = Pin(south_pin, mode=Pin.OPEN_DRAIN, pull=Pin.PULL_UP)
        self.ctl_north = Pin(north_pin, mode=Pin.OPEN_DRAIN, pull=Pin.PULL_UP)

        self.ctl_pump(1)
        self.ctl_south(1)
        self.ctl_north(1)

        self.enable_publish = True

        self.topic_vector = {
            b"kutenai/feeds/pump": self.pump_command_handler,
            b"kutenai/feeds/north": self.north_command_handler,
            b"kutenai/feeds/south": self.south_command_handler,
        }

    def connect(self):
        self.client = MQTTClient("ditch_client", "io.adafruit.com", port=1883,
                                 user="kutenai",
                                 password="2aea0e47611f4f36a221bccf8c23ed7d")
        self.client.set_callback(self.ditch_command_handler)
        self.client.connect()
        print("Connected to mqtt server")
        self.subscribe()
        self.publish_controls()

    def ditch_level(self):
        val = self.adc_ditch()
        val = 12.0 * val / 4095
        return val

    def sump_level(self):
        val = self.adc_sump()
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

    def subscribe(self):
        self.client.subscribe(topic="kutenai/feeds/pump")
        self.client.subscribe(topic="kutenai/feeds/north")
        self.client.subscribe(topic="kutenai/feeds/south")

    def publish_controls(self):
        self.client.publish("kutenai/feeds/pump", onoff(self.ctl_pump()))
        self.client.publish("kutenai/feeds/north", onoff(self.ctl_north()))
        self.client.publish("kutenai/feeds/south", onoff(self.ctl_south()))

    # Setup our publish Timer
    def publish_levels(self):
        print("Sending ditch and sump levels")
        self.client.publish("kutenai/feeds/ditch", "{:5.2f}".format(self.ditch_level()))
        self.client.publish("kutenai/feeds/sump", "{:5.2f}".format(self.sump_level()))

    def time_to_publish(self):
        """ Called by Alarm interrupt to indicate time to publish levels """
        self.enable_publish = True

    def loop(self):
        """ Called repeatedly in the main loop """
        try:
            self.client.check_msg()

            if self.enable_publish:
                self.publish_levels()
                self.enable_publish = False
        except OSError as e:
            """ Occurs with error in wait_msg """
            # Not sure what the proper recovery is.. so I'll disconnect and re-connection
            print("***** Warning.... Received an OSError. Resetting MQTT Client ******")
            self.client.disconnect()
            self.connect()
            print("MQTT Client Re-connected")
