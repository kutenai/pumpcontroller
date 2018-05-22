# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal
import machine
from machine import UART
from network import WLAN
from os import dupterm
from time import sleep_ms

from machine import UART
import machine
import os

uart = UART(0, baudrate=115200)
os.dupterm(uart)

machine.main('main_mqtt.py')
# # enable the UART on the USB-to-serial port
# uart = UART(0, baudrate=115200)
# # duplicate the terminal on the UART
# dupterm(uart)
# print('UART initialised!')
#
# import settings
# networks = settings.PREFERRED_NETWORKS
#
# # login to the local network
# print('Initialising WLAN in station mode...', end=' ')
# wlan = WLAN(mode=WLAN.STA)
#
# nets = wlan.scan()
# for net in nets:
#     if net.ssid in networks:
#         wifikey=networks.get(net.ssid)
#         print('Network {} found!'.format(net.ssid))
#         wlan.connect(net.ssid, auth=(net.sec, wifikey), timeout=5000)
#         while not wlan.isconnected():
#             machine.idle() # save power while waiting
#         print('WLAN connection succeeded!')
#         # I don't think we need this.. and it gives errors.
#         #wlan.ifconfig(id=0,config='dhcp')
#         break
#
# # print
# ip, mask, gateway, dns = wlan.ifconfig()
# print('IP address: {ip}\nNetwork:{mask}\nGateway:{gateway}\nDNS:{dns}\n'.format(
#     ip=ip, mask=mask, gateway=gateway, dns=dns))
#
# sleep_ms(1000)
