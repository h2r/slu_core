import matplotlib
matplotlib.use("Qt4Agg")
import numpy as na
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import capturers
import pylab as mpl
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL
import spatial_relations_gui_ui
import argparse
from g3.inference import nodeSearch
import basewindow
from g3.cost_functions.cost_function_crf import CostFnCrf

class MainWindow(QMainWindow, spatial_relations_gui_ui.Ui_MainWindow):
    def initializeMatplotlib(self):
        self.figure = mpl.figure()
        self.axes = mpl.gca()
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.canvasFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)


    def __init__(self, task_planner):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.task_planner = task_planner
        self.initializeMatplotlib()

        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)
        self.capturePolygon = capturers.PolygonCapturer()
        self.capturePoint = capturers.PointCapturer()
        

        self.connect(self.capturePolygon, SIGNAL("completedPolygon"),
                     self.completedPolygon)

        self.connect(self.capturePoint, SIGNAL("completedPoint"),
                     self.completedPoint)        
        self.capturers = [self.capturePoint,
                          self.capturePolygon,
                          ]
        for c in self.capturers:
            self.capturerList.addItem(c.name)

        self.connect(self.capturerList.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.changeCapturer)


    def updateLimits(self, event):
        self.limits = self.axes.axis()
    def completedPolygon(self, polygon):
        print "completed polygon", na.transpose(polygon)
    def completedPoint(self, point):
        print "got", point

    def changeCapturer(self):
        self.capturer = self.capturers[self.capturerList.currentIndex().row()]

        for c in self.capturers:
            c.deactivate()

        self.capturer.activate(self.figure)

def main(args):
    app = basewindow.makeApp()
    parser = argparse.ArgumentParser()

    parser.add_argument("--model-filename",dest="model_fname", 
                        help="Model Filename", metavar="FILE")

    args = parser.parse_args()
    cost_function = CostFnCrf.from_mallet(args.model_fname)

    task_planner = nodeSearch.BeamSearch(cost_function)
    wnd = MainWindow(task_planner)
    wnd.show()
    app.exec_()

if __name__=="__main__":
    import sys
    #print "test"
    #import psyco
    #psyco.full()
    main(sys.argv)


