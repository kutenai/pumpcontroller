import machine
from machine import Pin
import pycom
import time

adc = machine.ADC()
adc_ditch = adc.channel(pin="P13")
adc_sump = adc.channel(pin="P16")
ctl_pump = Pin("P19", mode=Pin.OUT)
ctl_south = Pin("P20", mode=Pin.OUT)
ctl_north = Pin("P21", mode=Pin.OUT)
ctl_pump2 = Pin("P22", mode=Pin.OUT)

button = Pin("P10", mode=Pin.IN, pull=Pin.PULL_UP)

def button_press(arg):
    print("Button Pressed")
    ctl_pump.toggle()
    ctl_pump2.toggle()
    ctl_south.toggle()
    ctl_north.toggle()

    print("Digital pins are {},{},{} and {}".format(
        ctl_pump(), ctl_pump2, ctl_south(), ctl_north()
    ))

button.callback(Pin.IRQ_FALLING, handler=button_press)

pycom.heartbeat(False)
start = 0x080000
val=start
counter=12
while True:

    pycom.rgbled(val)
    time.sleep(0.25)

    val = val >> 8 or start
    counter -= 1

    if counter <= 0:
        counter = 12
        print("ADC Values Ditch:{ditch} and Sump:{sump}".format(
            ditch=adc_ditch(), sump=adc_sump()
        ))
