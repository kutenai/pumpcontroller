#!/usr/bin/env python

from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import View, Item
from enthought.chaco.api import HPlotContainer,Plot, ArrayPlotData
from enthought.enable.component_editor import ComponentEditor
from numpy import linspace, sin

from GloveAPI import *

class IMUGloveDisplay(HasTraits):
    plot = Instance(HPlotContainer)
    traits_view = View(
        Item('plot',editor=ComponentEditor(), show_label=False),
        width=1000, height=600, resizable=True, title="IMU Glove Display")

    def __init__(self):
        super(IMUGloveDisplay, self).__init__()
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x=x, y=y)
        scatter = Plot(plotdata)
        scatter.plot(("x","y"), type="scatter", color="blue")
        line = Plot(plotdata)
        line.plot(("x", "y"), type="line", color="blue")
        container = HPlotContainer(scatter,line)
        #scatter.title = "sin(x) * x^3"
        #line.title = 'line plot'
        self.plot = container
        self.InitGlove()

    def InitGlove(self):
        self.api = GloveAPI()
        self.api.initHardware()
        self.api.debug(False)
        self.api.configimu()

    def ReadData(self,numToRead):
        ''' Start streaming data '''
        self.api.stream(numToRead)

        self.api.clearIMUPacketEngine()
        keys = ['sentinal','footer','temp','gx','gy','gz','ax','ay','az','sentinal']
        #keys = ['gx','gy','gz','ax','ay','az']
        packets = []
        t = time.time()
        for x in range(0,numToRead):
            p = self.api.getIMUPacket()
            if p:
                ''' Update the data in the plot.. '''
                showPacket(p,keys)
            else:
                self.api.configimu()
                self.api.stream(numToRead-x)

        tdiff = time.time() - t
        print("Total time:%6.6f Time per Packet:%6.6f" % (tdiff,tdiff/x))


if __name__ == "__main__":
    gd = IMUGloveDisplay()
    gd.configure_traits()
    gd.ReadData(100)


