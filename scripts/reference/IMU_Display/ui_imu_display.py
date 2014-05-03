# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_IMU_Display.ui'
#
# Created: Wed Feb 16 21:32:29 2011
#      by: PyQt4 UI code generator 4.7.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_IMU_Display(object):
    def setupUi(self, IMU_Display):
        IMU_Display.setObjectName(_fromUtf8("IMU_Display"))
        IMU_Display.resize(853, 742)
        self.centralwidget = QtGui.QWidget(IMU_Display)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.vertPlots = QtGui.QVBoxLayout()
        self.vertPlots.setSpacing(3)
        self.vertPlots.setContentsMargins(12, -1, -1, -1)
        self.vertPlots.setObjectName(_fromUtf8("vertPlots"))
        self.verticalLayout_2.addLayout(self.vertPlots)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 2, 1, 1)
        self.txtSerialPort = QtGui.QLineEdit(self.centralwidget)
        self.txtSerialPort.setObjectName(_fromUtf8("txtSerialPort"))
        self.gridLayout.addWidget(self.txtSerialPort, 1, 3, 1, 1)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 2, 1, 1)
        self.txtPeriod = QtGui.QLineEdit(self.centralwidget)
        self.txtPeriod.setObjectName(_fromUtf8("txtPeriod"))
        self.gridLayout.addWidget(self.txtPeriod, 2, 3, 1, 1)
        self.comboIMU = QtGui.QComboBox(self.centralwidget)
        self.comboIMU.setObjectName(_fromUtf8("comboIMU"))
        self.gridLayout.addWidget(self.comboIMU, 0, 3, 1, 1)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.btnSelect = QtGui.QPushButton(self.centralwidget)
        self.btnSelect.setObjectName(_fromUtf8("btnSelect"))
        self.gridLayout.addWidget(self.btnSelect, 1, 1, 1, 1)
        self.btnExit = QtGui.QPushButton(self.centralwidget)
        self.btnExit.setObjectName(_fromUtf8("btnExit"))
        self.gridLayout.addWidget(self.btnExit, 3, 1, 1, 1)
        self.pbClear = QtGui.QPushButton(self.centralwidget)
        self.pbClear.setObjectName(_fromUtf8("pbClear"))
        self.gridLayout.addWidget(self.pbClear, 2, 1, 1, 1)
        self.pbStartStop = QtGui.QPushButton(self.centralwidget)
        self.pbStartStop.setObjectName(_fromUtf8("pbStartStop"))
        self.gridLayout.addWidget(self.pbStartStop, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        IMU_Display.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(IMU_Display)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 853, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuExit = QtGui.QMenu(self.menubar)
        self.menuExit.setObjectName(_fromUtf8("menuExit"))
        IMU_Display.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(IMU_Display)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        IMU_Display.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuExit.menuAction())

        self.retranslateUi(IMU_Display)
        QtCore.QObject.connect(self.btnExit, QtCore.SIGNAL(_fromUtf8("clicked()")), IMU_Display.close)
        QtCore.QMetaObject.connectSlotsByName(IMU_Display)

    def retranslateUi(self, IMU_Display):
        IMU_Display.setWindowTitle(QtGui.QApplication.translate("IMU_Display", "IMU Window", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("IMU_Display", "Serial Port", None, QtGui.QApplication.UnicodeUTF8))
        self.txtSerialPort.setText(QtGui.QApplication.translate("IMU_Display", "/dev/cu.usbserial-A9007KPc", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("IMU_Display", "Period (ms)", None, QtGui.QApplication.UnicodeUTF8))
        self.txtPeriod.setText(QtGui.QApplication.translate("IMU_Display", "100", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("IMU_Display", "IMU", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelect.setText(QtGui.QApplication.translate("IMU_Display", "Gyros", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExit.setText(QtGui.QApplication.translate("IMU_Display", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.pbClear.setText(QtGui.QApplication.translate("IMU_Display", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.pbStartStop.setText(QtGui.QApplication.translate("IMU_Display", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.menuExit.setTitle(QtGui.QApplication.translate("IMU_Display", "Exit", None, QtGui.QApplication.UnicodeUTF8))

