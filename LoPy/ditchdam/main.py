import machine
from machine import Pin, Timer, SD
from mqtt import MQTTClient
from network import WLAN
import pycom
import time
import uos

from DitchMonitor import DitchMonitor

# enable the UART on the USB-to-serial port
uart = UART(0, baudrate=115200)
# duplicate the terminal on the UART
uos.dupterm(uart)
print('UART initialised!')

import settings
networks = settings.PREFERRED_NETWORKS

# login to the local network
print('Initialising WLAN in station mode...')
wlan = WLAN(mode=WLAN.STA)

while True:
    nets = wlan.scan()
    print("Nets found:{}".format(",".join([n.ssid for n in nets])))
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

    if ip == '0.0.0.0':
        print("Did not get a valid IP. Will re-try")
        time.sleep(1)
    else:
        break

# Setup the SD Card, if found
sd = SD()
os.mount(sd, '/sd')

controller = DitchController(
    ditch_pin="P13",
    intake_pin="P16",
)
controller.connect()

button = Pin("P10", mode=Pin.IN, pull=Pin.PULL_UP)

def onoff(x):
    if x:
        return b"ON"
    return b"OFF"

def button_press(arg):
    print("Button Pressed, toggling all controls")
    controller.toggle_pump()
    controller.toggle_south()
    controller.toggle_north()

    controller.publish_controls()

button.callback(Pin.IRQ_FALLING, handler=button_press)

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
        print("Received an Exception:{}".format(e))
