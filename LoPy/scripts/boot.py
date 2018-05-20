# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal
from machine import UART
from network import WLAN
from os import dupterm
from time import sleep_ms

# enable the UART on the USB-to-serial port
uart = UART(0, baudrate=115200)
# duplicate the terminal on the UART
dupterm(uart)
print('UART initialised!')

import settings

# login to the local network
print('Initialising WLAN in station mode...', end=' ')
wlan = WLAN(mode=WLAN.STA)
wlan.ifconfig(config='dhcp')

nets = wlan.scan()
for net in nets:
    if net.ssid == settings.SSID:
        print('Network {} found!'.format(settings.SSID))
        wlan.connect(net.ssid, auth=(net.sec, settings.wifiKey), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

# print
ip, mask, gateway, dns = wlan.ifconfig()
print('IP address: {ip}\nNetwork:{mask}\nGateway:{gateway}\nDNS:{dns}\n'.format(
    ip=ip, mask=mask, gateway=gateway, dns=dns))

sleep_ms(1000)
