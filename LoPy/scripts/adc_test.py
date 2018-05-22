import machine
import time

adc = machine.ADC()


adc_ditch = adc.channel(pin="P13")
adc_sump = adc.channel(pin="P16")
ctl_pump = machine.Pin("P19", mode=machine.Pin.OUT)
ctl_south = machine.Pin("P20", mode=machine.Pin.OUT)
ctl_north = machine.Pin("P21", mode=machine.Pin.OUT)

while True:
    print("ADC Values {one} and {two}".format(
        one=adc1(), two=adc2()
    ))
    time.sleep(1)

    ctl_pump.toggle()
    ctl_south.toggle()
    ctl_north.toggle()

    print("Digital pins are {},{} and {}".format(
        ctl_pump(), ctl_south(), ctl_north()
    ))
