from PyQt4.QtGui import QMainWindow
import spatial_relations_gui_ui

class MainWindow(QMainWindow, spatial_relations_gui_ui.Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

if __name__=="__main__":
    import sys
    #print "test"
    #import psyco
    #psyco.full()
    main(sys.argv)


