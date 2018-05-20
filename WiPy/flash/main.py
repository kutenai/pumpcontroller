# main.py -- put your code here!
import untplib
from machine import ADC

# get time from NTP server
c=untplib.NTPClient()
resp=c.request('0.uk.pool.ntp.org', version=3, port=123)
print("Offset is ", resp.offset)

# adjust WiPy time
from machine import RTC
import time

rtc = RTC()
print("Adjusting clock by ", resp.offset, "seconds")
rtc.init(time.localtime(time.time() + resp.offset+3600)) #+3600 for BST
print(rtc.now())
wipy_time = str(time.localtime())
print("Current time", wipy_time)

# send e-mail

print("Sending e-mail...")
import smtplib

# Please replace with your e-mail credentials:
to = 'ed@sharpertool.com'
gmail_user = 'henderson.ed@gmail.com'
gmail_pwd = 'waken-playpen-acanthus'

smtpserver = smtplib.SMTP("smtp.gmail.com", 465)
smtpserver.helo()
smtpserver.login(gmail_user, gmail_pwd)
header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: WiPy Time \n'
msg = header + '\n Hi, \n\n WiPy time is '+ wipy_time +' ;-) \n\n Cheers, \n The WiPy'
smtpserver.sendmail(gmail_user, to, msg)
smtpserver.close()

print("e-mail sent!")

# the end.