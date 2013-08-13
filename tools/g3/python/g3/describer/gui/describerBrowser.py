import matplotlib_qt
import basewindow
from optparse import OptionParser
from PyQt4.QtGui import QMainWindow
import describerBrowser_ui 
from g3.describer.describe import Describer
from esdcs.gui.drawUtils import drawGrounding
from g3.cost_functions.cost_function_crf import CostFnCrf
import cPickle
import pylab as mpl
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from g3.cost_functions.gui import crfFeatureWeights

class MainWindow(QMainWindow, describerBrowser_ui.Ui_MainWindow):
    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()
    def __init__(self, describer):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.describer = describer
        self.cf = self.describer.cf

        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)

        self.crfFeatureWeights = crfFeatureWeights.MainWindow()
        self.crfFeatureWeights.setWindowTitle("CRF Feature Weights"  + 
                                              " created by " + 
                                              str(self.crfFeatureWeights.windowTitle()))
        self.crfFeatureWeights.show()

        self.draw()
        
    def draw(self):
        self.axes.clear()
        for g in self.describer.groundings:
            drawGrounding(self.axes, g)

    def describe(self, thing):
        drawGrounding(self.axes, thing, plotArgs={"color":"red"})
        self.describer.describe(thing)
        
        factor_to_cost = []
        for c in self.describer.cf.factor_to_cost.values():
            factor_to_cost.extend(c)
        
        self.crfFeatureWeights.load(self.describer.cf.lccrf, factor_to_cost)
                                    
def main(argv):
    app = basewindow.makeApp()

    parser = OptionParser()
    
    parser.add_option("--model",dest="model_fname", 
                      help="CRF Filename", metavar="FILE")

    parser.add_option("--training",dest="training_fname")
    parser.add_option("--testing",dest="testing_fname")

  
    (options, args) = parser.parse_args()
    cf = CostFnCrf(options.model_fname)
    
    training = cPickle.load(open(options.training_fname))
    testing = cPickle.load(open(options.testing_fname))

    describer = Describer(training, cf)

    wnd = MainWindow(describer)

    wnd.show()

    testing_examples = [ex for ex in testing.observations 
                        if ex.sdcs[0].type == "PATH"]
    ex = testing_examples[1]
    path_esdc = ex.sdcs[0]
    test_grounding = ex.annotation.getGroundings(path_esdc)[0]
    wnd.describe(test_grounding)

    app.exec_()

if __name__=="__main__":
    import sys
    #print "test"
    #import psyco
    #psyco.full()
    main(sys.argv)


