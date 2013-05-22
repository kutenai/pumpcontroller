#!/usr/bin/env python
__author__ = 'kutenai'


import smtplib
from email.MIMEText import MIMEText
from time import time,sleep,strftime

class DitchMessenger(object):
    """
    Ditch Messenger sends information and alert messages via e-mail, and maybe SMS

    """

    def __init__(self):
        self.printer = None

        # Information for e-mail messages
        self.username = "sharpertoolgardening@gmail.com"
        self.password = "nu0tyba0ghuc"
        self.smtpserver = "smtp.gmail.com:587"
        self.reportDests = {
            'test' : ['kutenai@me.com', 'ed@eeweb.com'],
            'info' : ['kutenai@me.com', 'viquee@me.com'],
            'warn' : ['kutenai@me.com', 'viquee@me.com','joel@me.com'],
            'alarm': ['joelhurlburt@me.com', 'viquee@me.com', 'kutenai@me.com']
        }

    def setPrintObj(self,pobj):

        self.printer = pobj

    def lprint(self,txt):

        if self.printer:
            self.printer.lprint(txt)
        else:
            print(txt)

    def sendMessage(self,severity,subject, txt):
        """
        Send a message, based on the severity and such..
        """


        #subject = "%s Errors (resent on %s)" \
        #          % ("TESTING",strftime("%m-%d-%Y at %H:%M",localtime()))

        if self.reportDests.has_key(severity):
            dests = self.reportDests[severity]
        else:
            dests = self.reportDests['warn']

        self.sendEmail(dests,subject,txt)

        pass

    def sendEmail(self,dests,subject,message):
        """
        Send an e-mail message to the given recipient(s)
        """

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = ','.join(dests)

        server = smtplib.SMTP(self.smtpserver)
        server.starttls()
        server.login(self.username,self.password)
        server.sendmail(self.username, dests, msg.as_string())
        server.quit()


def main():
    """
    Parse command line arguments.
    If the server is looping, or running for a continuous time, then
    enter a loop and keep calling the check function.

    """

    m = DitchMessenger()


    m.sendMessage('test',"Test System", "This is a test of the Ditch Broadcast System")


if __name__ == "__main__":
    main()
