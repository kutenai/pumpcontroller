import machine
from machine import Pin, Timer, SD
from mqtt import MQTTClient
from network import WLAN
import pycom
import time
import uos
import os

from DitchController import DitchController

# enable the UART on the USB-to-serial port
uart = UART(0, baudrate=115200)
# duplicate the terminal on the UART
uos.dupterm(uart)
print('UART initialised!')

import settings
networks = settings.PREFERRED_NETWORKS

# Setup the SD Card, if found
print("Mount SD")
sd = SD()
print("OS MOunt")
try:
    os.mount(sd, '/sd')
except Exception as e:
    print("Exception {}".format(e))
print("MOunted")

print('Here')
controller = DitchController(
    ditch_pin="P13",
    sump_pin="P16",
    pump_pin="P19",
    south_pin="P20",
    north_pin="P21"
)
#controller.connect()
print('there')

button = Pin("P10", mode=Pin.IN, pull=Pin.PULL_UP)


pycom.heartbeat(False)
start = 0x080000
val=start
counter=12

while True:
    try:
        #controller.loop()
        #ditch = controller.ditch_level()
        val = controller.adc_sump()
        sump = controller.sump_level(show=False)
        #print("Ditch level is {}".format(ditch))
        print("Sump adc: {} level is {}".format(val, sump))

        pycom.rgbled(val)
        time.sleep(0.25)

        val = val >> 8 or start
    except Exception as e:
        print("Received an Exception:{}".format(e))
