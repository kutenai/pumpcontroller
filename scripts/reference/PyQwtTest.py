#!/usr/bin/env python

import numpy as np

import sys
from PyQt4.Qt import Qt
from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *

def aSlot(aQPointF):
    print 'aSlot gets:', aQPointF

    # aSlot()
def make():
    demo = Qwt.QwtPlot()
    picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                Qwt.QwtPlot.yLeft,
                Qwt.QwtPicker.PointSelection,
                Qwt.QwtPlotPicker.CrossRubberBand,
                Qwt.QwtPicker.AlwaysOn,
                demo.canvas())
    picker.connect(
        picker, Qt.SIGNAL('selected(const QwtDoublePoint&)'), aSlot)
    return demo

def test1():
    app = QApplication([])
    x = np.arange(-2*np.pi, 2*np.pi, 0.01)
    p = Plot(
        Curve(x, np.cos(x), Pen(Magenta, 2), "cos(x)"),
        Curve(x, np.exp(x), Pen(Red), "exp(x)", Y2),
        Axis(Y2, Log),
        "PyQst using Qwt-%s -- http://qst.sf.net" % QWT_VERSION_STR)
    QPixmap.grabWidget(p).save('cli-plot-1.png', 'PNG')
    x = x[0:-1:10]
    p.plot(
        Curve(x, np.cos(x-np.pi/4), Symbol(Circle, Yellow), "circle"),
        Curve(x, np.cos(x+np.pi/4), Pen(Blue), Symbol(Square, Cyan), "square"))
    QPixmap.grabWidget(p).save('cli-plot-2.png', 'PNG')


# make()
def main(args):
    app = Qt.QApplication(args)
    demo = make()
    demo.show()
    sys.exit(app.exec_())

# main()
if __name__ == '__main__':
    #main(sys.argv)
    test1()

# Local Variables: ***
# mode: python ***
# End: ***