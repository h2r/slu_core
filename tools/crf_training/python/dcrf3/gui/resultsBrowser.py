import matplotlib_qt

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL
import pylab as mpl
import basewindow
import resultsBrowser_ui
import pickle_util
import resultsModel
import featureModel
from mallet.learners.crf_mallet import CRFMallet
from esdcs.gui import context3d
from esdcs.gui.esdc_utils import highlightTextLabelESDCs
from esdcs.context import Context

class MainWindow(QMainWindow, resultsBrowser_ui.Ui_MainWindow):

    """
    Browser to look at the results when predicting the correspodence
    variable.
    """
    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        
        self.limits = [10, 40, 10, 40]
        self.restoreLimits()
        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)

        self.resultsModel = resultsModel.Model(self.resultsTable)
        self.featureModel = featureModel.Model(self.featureTable)
        
        self.model = None
        self.dataset = None

        self.contextWindow = context3d.MainWindow()
        self.contextWindow.setWindowTitle(self.contextWindow.windowTitle() + 
                                          " - CRF Results Browser")
        self.contextWindow.show()


        self.connect(self.resultsTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectResult)


        self.connect(self.esdcFilter,
                     SIGNAL("editingFinished()"),
                     self.filterEsdcs)


        self.resultsTable.selectRow(0)
        self.baseWindowTitle = self.windowTitle()


    def filterEsdcs(self):
        expr = self.esdcFilter.text()
        print expr
        try:
            filterFunction = eval(str(expr))
        except:
            raise
        
        self.resultsModel.setFilter(filterFunction)

        

    def selectResult(self):
        print "selecting result"
        result = self.resultsModel.selectedEntry()
        self.commandText.setText(result.esdc.text)
        highlightTextLabelESDCs(self.commandText, result.obs.sdcs)
        self.featureModel.setData(result.crf, result.obs)


        if result.obs.annotation != None:
            context = Context.from_groundings(result.obs.annotation.groundings)
            self.contextWindow.setContext(context)


        if result.obs.factor != None:
            groundings = []
            for n in result.obs.factor.nodes:
                if n.is_gamma:
                    groundings.extend(result.obs.ggg.evidence_for_node(n))

            self.contextWindow.highlightGroundings(groundings)


        cm = self.resultsModel.confusionMatrix()        


        self.accuracyLabel.setText(cm.accuracy_string())
        self.precisionLabel.setText(cm.precision_string())
        self.recallLabel.setText(cm.recall_string())
        
    def load(self, model, dataset, title=""):
        self.model = model
        self.dataset = dataset
        self.resultsModel.setData(model, dataset.observations)
        self.setWindowTitle(self.baseWindowTitle + ": %s" % title)
        
    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self):
        if self.limits != None:
            self.axes.axis(self.limits)

        
def main(argv):
    app = basewindow.makeApp()
    
    from sys import argv
    model_fname = argv[1]
    dataset_fname = argv[2]
   
    
    crf = CRFMallet.load(model_fname)
    dataset = pickle_util.load(dataset_fname)
    
    wnd = MainWindow()

    wnd.load(crf, dataset, title=dataset_fname)
    
    wnd.show()

    app.exec_()

if __name__=="__main__":
    print "starting"
    import sys
    main(sys.argv)

 
