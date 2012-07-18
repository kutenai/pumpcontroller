#!/usr/bin/env python

import serial
import re
import random
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from PyQt4.Qwt5.anynumpy import *
from threading import Thread,Lock
import numpy as np

import ui_imu_display
from IMUPacket import IMUPacket
from GloveAPI import GloveAPI
#from IMU import IMU
from IMUManager import IMUManager

class DataWorker(Thread):
    '''
    Worker thread for retrieving results from the IMU.
    This thread runs a loop that captures data from the IMU and
    processes it into packets. it then takes the important IMU
    results and passes it to a function on the data object. This
    function uses a lock object to protect access from multiple
    threads, and serves as the data transfer point between this thread
    and the display thread.

    An enhancement would be to have this tread JUST capture the data
    and then have another thread or more handle the processing of the
    data, even the basic conversion and extraction of the data. Normally
    this might not be a good idea, but since I have an 8 Core machine
    at home, this makes a ton of sense...
    '''

    def __init__(self,api,dataObj,step):
        super(DataWorker,self).__init__()

        self.api = api
        self.dataObj = dataObj
        self.stopme = False
        self.rate = int(1/step)

    def run(self):
        '''
        Do the hard work..
        '''
        print("worker started..")
        self.api.debug(False)
        self.api.rate(self.rate)
        self.api.configimu()
        self.api.stream(10)
        while True:
            t = time.time()

            if self.stopme:
                self.api.stream(1)
                print("Worker asked to quit")
                return

            self.api.stream(10)
            packet = self.api.getIMUPacket()
            if packet:
                imudata = packet.Results()
                v = imudata[self.dataObj.IMUIndex]
                #print("Pushing data..")
                if self.dataObj.intDataSelect == 0:
                    self.dataObj.AddData((v['gx'],v['gy'],v['gz']))
                else:
                    self.dataObj.AddData((v['ax'],v['ay'],v['az']))
            else:
                print("Empty data returned")

            tdiff = time.time() - t



class IMU_Display(QMainWindow,
                       ui_imu_display.Ui_IMU_Display):
    def __init__(self,parent=None):
        super(IMU_Display, self).__init__(parent)

        self._running = False
        self.ser = None
        self.tval = 0

        self.setupUi(self)
        self.api = GloveAPI()
        self.api.initHardware()
        self.imumgr = IMUManager(self.api)
        self.imumgr.Configure()

        self.pbStartStop.setText("Start")

        self.connect(self.pbStartStop, SIGNAL("clicked()"),
                     self.StartStop)

        self.comboIMU.addItem('Hand')
        self.comboIMU.addItem('Pinkie')
        self.comboIMU.addItem('Ring')
        self.comboIMU.addItem('Middle')
        self.comboIMU.addItem('Index')
        self.comboIMU.addItem('Thumb')

        self.connect(self.comboIMU,SIGNAL("currentIndexChanged(int)"), self.IMUChanged)
        self.IMUIndex = self.comboIMU.currentIndex()

        self.intDataSelect = 0 # 0 = Gyros, 1 = Accelerometers
        self.connect(self.btnSelect,SIGNAL("clicked()"), self.DataSelect)
        self.btnSelect.setText('Gyro')

        self.size = 1000
        self.step = 0.020 # 5ms.
        #self.t = arange(0.0,self.size*self.step,self.step)
        #self.x = zeros(self.size,Float)
        #self.y = zeros(self.size,Float)
        #self.z = zeros(self.size,Float)
        self.t = np.arange(0,self.size*self.step,self.step)
        self.x = np.zeros(self.size)
        self.y = np.zeros(self.size)
        self.z = np.zeros(self.size)

        self.nPos = 0

        self.pxAccel = Qwt.QwtPlot()
        self.vertPlots.addWidget(self.pxAccel)
        self.pyAccel = Qwt.QwtPlot()
        self.vertPlots.addWidget(self.pyAccel)
        self.pzAccel = Qwt.QwtPlot()
        self.vertPlots.addWidget(self.pzAccel)
        self.pxAccel.setTitle("X Gyroscope")
        self.pyAccel.setTitle("Y Gyroscope")
        self.pzAccel.setTitle("Z Gyroscope")

        self.curveX = Qwt.QwtPlotCurve("X Accel")
        #self.curveX.setStyle(Qwt.QwtPlotCurve.Sticks)
        self.curveX.attach(self.pxAccel)
        self.curveY = Qwt.QwtPlotCurve("Y Accel")
        self.curveY.attach(self.pyAccel)
        self.curveZ = Qwt.QwtPlotCurve("Z Accel")
        self.curveZ.attach(self.pzAccel)

        self.curveX.setPen(Qt.QPen(Qt.Qt.red))
        self.curveY.setPen(Qt.QPen(Qt.Qt.blue))
        self.curveZ.setPen(Qt.QPen(Qt.Qt.green))

        self.lock = None
        self.data = []
        self.worker = None


    def IMUChanged(self,int):
        self.IMUIndex = self.comboIMU.currentIndex()

    def DataSelect(self):
        if self.intDataSelect == 0:
            self.intDataSelect = 1
            self.btnSelect.setText("Acc")
            self.pxAccel.setTitle("X Accelerometer")
            self.pyAccel.setTitle("Y Accelerometer")
            self.pzAccel.setTitle("Z Accelerometer")
        else:
            self.intDataSelect = 0
            self.btnSelect.setText("Gyro")
            self.pxAccel.setTitle("X Gyroscope")
            self.pyAccel.setTitle("Y Gyroscope")
            self.pzAccel.setTitle("Z Gyroscope")

    def UpdateData(self,vals):

        if self.nPos < self.size:
            '''
            Insert more data.. the initial data is all zeros
            '''
            self.x[self.nPos] = vals[0]
            self.y[self.nPos] = vals[1]
            self.z[self.nPos] = vals[2]
            self.nPos = self.nPos + 1

        else:
            ''' Shift the data down '''
            #self.t = np.concatenate((self.t[1:],[self.t[-1]+self.step]))
            self.x = np.concatenate((self.x[1:],[vals[0]]))
            self.y = np.concatenate((self.y[1:],[vals[1]]))
            self.z = np.concatenate((self.z[1:],[vals[2]]))

        self.curveX.setData(self.t, self.x)
        self.curveY.setData(self.t, self.y)
        self.curveZ.setData(self.t, self.z)

        self.pxAccel.replot()
        self.pyAccel.replot()
        self.pzAccel.replot()

    def AddData(self,v=[]):
        self.lock.acquire()
        self.data.append(v)
        self.lock.release()

    def timerEvent(self, e):
        if self._running == False:
            return

        self.lock.acquire()
        ldata = self.data
        self.data = []
        self.lock.release()
        #print("Updating with %d values" % len(ldata))
        if len(ldata) > 0:
            #self.StartStop()
            try:
                for v in ldata:
                    self.UpdateData(np.array(v))

            except:
                print ("Error...")
                #self.StartStop()

    def StartStop(self):
        if self._running:
            #self.api.streamOn(False)
            self.pbStartStop.setText("Start")
            self._running = False
            ''' Signal the worker thread to stop, then wait for it '''

            print("Telling worker to stop..")
            self.worker.stopme = True
            self.worker.join()
            print("Worker done")
            self.worker = None
            self.killTimer(self.timerid)

        else:
            self._running = True
            self.pbStartStop.setText("Stop")
            #self.api.streamOn(True)
            self.lock = Lock()
            '''
            The speed here is not critical, since we can process multiple
            values for each timer even. The timer locks the data, grabs all
            of the values present, then unlocks it.. running this loop faster
            would probably only serve to increase the overhead. It might make
            the viewer smoother, but I doubt it, since a 25ms update rate is
            faster than we can really discern anyway, assume we can discern a
            30Hz update rate...
            '''
            self.timerid = self.startTimer(25)
            self.worker = DataWorker(self.api,self,self.step)
            self.worker.start()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = IMU_Display()
    mw.show()
    mw.raise_()
    app.exec_()
