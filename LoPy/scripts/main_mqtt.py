import machine
from machine import Pin
from machine import Timer
from mqtt import MQTTClient
from network import WLAN
import pycom
import time

from DitchController import DitchController

# enable the UART on the USB-to-serial port
uart = UART(0, baudrate=115200)
# duplicate the terminal on the UART
dupterm(uart)
print('UART initialised!')

import settings
networks = settings.PREFERRED_NETWORKS

# login to the local network
print('Initialising WLAN in station mode...', end=' ')
wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
for net in nets:
    if net.ssid in networks:
        wifikey=networks.get(net.ssid)
        print('Network {} found!'.format(net.ssid))
        wlan.connect(net.ssid, auth=(net.sec, wifikey), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        # I don't think we need this.. and it gives errors.
        #wlan.ifconfig(id=0,config='dhcp')
        break

# print
ip, mask, gateway, dns = wlan.ifconfig()
print('IP address: {ip}\nNetwork:{mask}\nGateway:{gateway}\nDNS:{dns}\n'.format(
    ip=ip, mask=mask, gateway=gateway, dns=dns))

controller = DitchController(
    ditch_pin="P13",
    sump_pin="P16",
    pump_pin="P19",
    south_pin="P20",
    north_pin="P21"
)
controller.connect()

button = Pin("P10", mode=Pin.IN, pull=Pin.PULL_UP)

def onoff(x):
    if x:
        return b"ON"
    return b"OFF"

def button_press(arg):
    print("Button Pressed")
    ctl_pump.toggle()
    ctl_south.toggle()
    ctl_north.toggle()

    controller.publish_controls()

    print("Digital pins are {},{} and {}".format(
        ctl_pump(), ctl_south(), ctl_north()
    ))

button.callback(Pin.IRQ_FALLING, handler=button_press)

def publish_timer_handler(arg):
    controller.time_to_publish()
publish_timer = Timer.Alarm(publish_timer_handler, 5, periodic=True)

pycom.heartbeat(False)
start = 0x080000
val=start
counter=12
while True:
    try:
        controller.loop()

        pycom.rgbled(val)
        time.sleep(0.25)

        val = val >> 8 or start
    except Exception as e:
        print("Bah.. got an execption:{}".format(e))
