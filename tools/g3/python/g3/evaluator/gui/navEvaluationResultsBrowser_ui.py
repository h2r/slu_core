# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'navEvaluationResultsBrowser.ui'
#
# Created: Tue Jun 14 13:04:09 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(803, 522)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.sendToCostFunctionBrowserButton = QtGui.QPushButton(self.centralwidget)
        self.sendToCostFunctionBrowserButton.setGeometry(QtCore.QRect(20, 430, 221, 28))
        self.sendToCostFunctionBrowserButton.setObjectName(_fromUtf8("sendToCostFunctionBrowserButton"))
        self.exportButton = QtGui.QPushButton(self.centralwidget)
        self.exportButton.setGeometry(QtCore.QRect(250, 430, 86, 28))
        self.exportButton.setObjectName(_fromUtf8("exportButton"))
        self.resultsTable = QtGui.QTableView(self.centralwidget)
        self.resultsTable.setGeometry(QtCore.QRect(20, 240, 771, 181))
        self.resultsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.resultsTable.setSortingEnabled(True)
        self.resultsTable.setObjectName(_fromUtf8("resultsTable"))
        self.esdcFilter = QtGui.QLineEdit(self.centralwidget)
        self.esdcFilter.setGeometry(QtCore.QRect(20, 200, 541, 31))
        self.esdcFilter.setObjectName(_fromUtf8("esdcFilter"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 170, 371, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.commandText = QtGui.QLabel(self.centralwidget)
        self.commandText.setGeometry(QtCore.QRect(20, 10, 761, 81))
        self.commandText.setText(_fromUtf8(""))
        self.commandText.setObjectName(_fromUtf8("commandText"))
        self.entireEsdcText = QtGui.QLabel(self.centralwidget)
        self.entireEsdcText.setGeometry(QtCore.QRect(20, 100, 771, 71))
        self.entireEsdcText.setText(_fromUtf8(""))
        self.entireEsdcText.setObjectName(_fromUtf8("entireEsdcText"))
        self.distance = QtGui.QLabel(self.centralwidget)
        self.distance.setGeometry(QtCore.QRect(510, 430, 281, 31))
        self.distance.setText(_fromUtf8(""))
        self.distance.setObjectName(_fromUtf8("distance"))
        self.distancelabel = QtGui.QLabel(self.centralwidget)
        self.distancelabel.setGeometry(QtCore.QRect(370, 430, 151, 31))
        self.distancelabel.setObjectName(_fromUtf8("distancelabel"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 803, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.sendToCostFunctionBrowserButton.setText(QtGui.QApplication.translate("MainWindow", "Send to Cost Function Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.exportButton.setText(QtGui.QApplication.translate("MainWindow", "Export", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "ESDC filter: python lambda expression that takes a table entry", None, QtGui.QApplication.UnicodeUTF8))
        self.distancelabel.setText(QtGui.QApplication.translate("MainWindow", "Dist to Actual Endpoint:", None, QtGui.QApplication.UnicodeUTF8))

