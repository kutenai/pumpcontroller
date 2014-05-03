#!/usr/bin/env python


import wx
import wx.media

#Importing math constants and functions
from threading import Thread,Lock
import socket

# Define Events to be used
EVT_POS_ID      = wx.NewId()
EVT_CONTROL_ID  = wx.NewId()
EVT_LOAD_ID     = wx.NewId()

def EVT_RESULT(win,func):
    '''Define Result Event.'''
    win.Connect(-1,-1,EVT_RESULT_ID, func)

'''
Helper Classes
These generate an event class that is then pushed onto the event queue.
The class contains the event ID and then the data as needed by the class
type..

'''
class PositionEvent(wx.PyEvent):
    """Update the position of the video"""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_POS_ID)
        self.data = data

class LoadEvent(wx.PyEvent):
    """Update the position of the video"""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_LOAD_ID)
        self.data = data

class ControlEvent(wx.PyEvent):
    """Play, Pause or Stop the video"""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_CONTROL_ID)
        self.data = data

# Thread class that executes processing
class SocketListener(Thread):
    """Worker Thread Class."""
    def __init__(self, destClass):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.destClass = destClass
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("", 5000))
        server_socket.listen(5)

        print ("Client Socket Setup")

        while 1:
            client_socket, address = server_socket.accept()
            print "I got a connection from ", address
            data = client_socket.recv(512)
            while data:
                cmdFound = False
                m = re.search("pos (\d+)",data,re.IGNORECASE)
                if m:
                    pos = int(m.group(1))
                    #wx.PostEvent(self._notify_window,PositionEvent(pos) )
                    #print ("Updated Position to %d" % pos)
                    destClass.notifyPos(pos)
                    cmdFound = True
                m = re.search("load \"(.*)\"", data, re.IGNORECASE)
                if m:
                    # Re-load a new file
                    #wx.PostEvent(self._notify_window,LoadEvent(m.group(1)))
                    cmdFound = True

                if re.search("play",data,re.IGNORECASE):
                    #wx.PostEvent(self._notify_window,ControlEvent(2) )
                    print("Play Video")
                    cmdFound = True
                elif re.search("pause",data,re.IGNORECASE):
                    #wx.PostEvent(self._notify_window,ControlEvent(1) )
                    print("Pause Video")
                    cmdFound = True
                elif re.search("stop",data,re.IGNORECASE):
                    #wx.PostEvent(self._notify_window,ControlEvent(0) )
                    print("Stop Video")
                    cmdFound = True

                if not cmdFound:
                    print("Unknown Command:%s" % data)

                data = client_socket.recv(512)
