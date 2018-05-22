import machine
import pycom
from machine import Pin
from machine import Timer
from network import WLAN
from mqtt import MQTTClient
import machine
import time

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

adc = machine.ADC()
adc_ditch = adc.channel(pin="P13")
adc_sump = adc.channel(pin="P16")
ctl_pump = Pin("P19", mode=Pin.OUT)
ctl_south = Pin("P20", mode=Pin.OUT)
ctl_north = Pin("P21", mode=Pin.OUT)

def ditch_level():
    val = adc_ditch()
    val = 12.0*val/4095
    return val

def sump_level():
    val = adc_sump()
    val = 26*val/4095
    return val

button = Pin("P10", mode=Pin.IN, pull=Pin.PULL_UP)


def pump_command_handler(arg):
    print("Pump commanded to: {}".format(arg))

def north_command_handler(arg):
    print("North commanded to: {}".format(arg))

def south_command_handler(arg):
    print("South commanded to: {}".format(arg))

topic_vector = {
    b"kutenai/feeds/pump": pump_command_handler,
    b"kutenai/feeds/north": north_command_handler,
    b"kutenai/feeds/south": south_command_handler,
}

def ditch_command_handler(topic, msg):
    print("Received a command topic:{} msg:{}".format(topic, msg))
    if topic in topic_vector:
        topic_vector.get(topic)(msg)

client = MQTTClient("ditch_client", "io.adafruit.com", port=1883,
    user="kutenai", password="2aea0e47611f4f36a221bccf8c23ed7d")
client.set_callback(ditch_command_handler)
client.connect()
print("Connected to mqtt server")

def onoff(x):
    if x:
        return b"ON"
    return b"OFF"

def button_press(arg):
    print("Button Pressed")
    ctl_pump.toggle()
    ctl_south.toggle()
    ctl_north.toggle()


    client.publish("kutenai/feeds/pump", onoff(ctl_pump()))
    client.publish("kutenai/feeds/north", onoff(ctl_north()))
    client.publish("kutenai/feeds/south", onoff(ctl_south()))

    print("Digital pins are {},{} and {}".format(
        ctl_pump(), ctl_south(), ctl_north()
    ))

button.callback(Pin.IRQ_FALLING, handler=button_press)

#client.subscribe(topic="kutenai/feeds/ditch")
#client.subscribe(topic="kutenai/feeds/sump")
client.subscribe(topic="kutenai/feeds/pump")
client.subscribe(topic="kutenai/feeds/north")
client.subscribe(topic="kutenai/feeds/south")

client.publish("kutenai/feeds/pump", onoff(ctl_pump()))
client.publish("kutenai/feeds/north", onoff(ctl_north()))
client.publish("kutenai/feeds/south", onoff(ctl_south()))

# Setup our publish Timer
def publish_levels(arg):
    print("Sending ditch and sump levels")
    client.publish("kutenai/feeds/ditch", "{:5.2f}".format(ditch_level()))
    client.publish("kutenai/feeds/sump", "{:5.2f}".format(sump_level()))

publish_timer = Timer.Alarm(publish_levels, 5, periodic=True)

pycom.heartbeat(False)
start = 0x080000
val=start
counter=12
while True:
    client.check_msg()

    pycom.rgbled(val)
    time.sleep(0.25)

    val = val >> 8 or start
