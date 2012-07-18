#!/usr/bin/env python

import serial
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

MAC = True
try:
    from PyQt4.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False

class IMU_Display(QDialog):

    def __init__(self, parent=None):
        super(EngineThrust, self).__init__(parent)
        self.setupUi(self)


        self.connect(self.sldThrottle,SIGNAL('sliderMoved(int)'), self.ThrottleChange)

        if not MAC:
            self.findButton.setFocusPolicy(Qt.NoFocus)
            self.replaceButton.setFocusPolicy(Qt.NoFocus)
            self.replaceAllButton.setFocusPolicy(Qt.NoFocus)
            self.closeButton.setFocusPolicy(Qt.NoFocus)
            self.ser = serial.Serial('COM4:',9600,timeout = 1)
        else:
            # This works on a mac of course...
            self.ser = serial.Serial('/dev/cu.usbserial-A800ewSr',9600,timeout = 1)
        #self.updateUi()

    def ThrottleChange(self,val):
        print "Throttle changed.. to %d" % val
        self.ser.write('ES %d\n' % val)
        self.ser.flushInput()

class IMU_Display(QDialog, ui_newimagedlg.Ui_NewImageDlg):

    def __init__(self, parent=None):
        super(NewImageDlg, self).__init__(parent)
        self.setupUi(self)

        self.color = Qt.red
        for value, text in (
                (Qt.SolidPattern, "Solid"),
                (Qt.Dense1Pattern, "Dense #1"),
                (Qt.Dense2Pattern, "Dense #2"),
                (Qt.Dense3Pattern, "Dense #3"),
                (Qt.Dense4Pattern, "Dense #4"),
                (Qt.Dense5Pattern, "Dense #5"),
                (Qt.Dense6Pattern, "Dense #6"),
                (Qt.Dense7Pattern, "Dense #7"),
                (Qt.HorPattern, "Horizontal"),
                (Qt.VerPattern, "Vertical"),
                (Qt.CrossPattern, "Cross"),
                (Qt.BDiagPattern, "Backward Diagonal"),
                (Qt.FDiagPattern, "Forward Diagonal"),
                (Qt.DiagCrossPattern, "Diagonal Cross")):
            self.brushComboBox.addItem(text, value)

        self.connect(self.colorButton, SIGNAL("clicked()"),
                     self.getColor)
        self.connect(self.brushComboBox, SIGNAL("activated(int)"),
                     self.setColor)
        self.setColor()
        self.widthSpinBox.setFocus()


    def getColor(self):
        color = QColorDialog.getColor(Qt.black, self)
        if color.isValid():
            self.color = color
            self.setColor()


    def setColor(self):
        pixmap = self._makePixmap(60, 30)
        self.colorLabel.setPixmap(pixmap)


    def image(self):
        pixmap = self._makePixmap(self.widthSpinBox.value(),
                                  self.heightSpinBox.value())
        return QPixmap.toImage(pixmap)


    def _makePixmap(self, width, height):
        pixmap = QPixmap(width, height)
        style = int(self.brushComboBox.itemData(
                    self.brushComboBox.currentIndex()))
        brush = QBrush(self.color, Qt.BrushStyle(style))
        painter = QPainter(pixmap)
        painter.fillRect(pixmap.rect(), Qt.white)
        painter.fillRect(pixmap.rect(), brush)
        return pixmap


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = NewImageDlg()
    r = mw.rect()
    mw.show()
    mw.raise_()
    #mw.resize(1000,800)
    app.exec_()
