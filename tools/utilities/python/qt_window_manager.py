from PyQt4.QtCore import SIGNAL, QString
from PyQt4.QtGui import QAction

class WindowManager:
    def __init__(self, menu):
        self.menu = menu
        self.windows = []
        self.actions = []


    def addWindow(self, window):
        action = QAction(QString(window.windowTitle()), self.menu)
        action.setCheckable(True)
        action.setChecked(window.isVisible())
        self.menu.addAction(action)
        self.windows.append(window)
        self.actions.append(action)

        self.menu.connect(action,
                          SIGNAL("toggled(bool)"),
                          self.makeActionSignal(action, window))

    def makeActionSignal(self, action, window):
        def actionSignal(self):
            if action.isChecked():
                print "show"
                window.show()
            else:
                print" hide"
                window.hide()
        return actionSignal

    def addWindows(self, windows):
        for w in windows:
            self.addWindow(w)
            
