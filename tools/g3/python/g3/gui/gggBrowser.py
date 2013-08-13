import matplotlib_qt
from esdcs.gui import esdcTreeModel
from esdcs.gui.esdc_utils import highlightTextLabel
import basewindow
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL
import gggBrowser_ui
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import pylab as mpl
from esdcs.esdcIo import annotationIo
from g3.annotation_to_ggg import annotation_to_ggg_map
import factorModel
import nodeForFactorModel
from esdcs.gui import groundingsModel
from esdcs.gui.drawUtils import drawGrounding

class MainWindow(QMainWindow, gggBrowser_ui.Ui_MainWindow):
    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)
        self.limits = None
        #self.figure.canvas.mpl_connect('draw_event', self.updateLimits)

        self.esdcModel = esdcTreeModel.Model(self.esdcTreeView)
        self.factorModel = factorModel.Model(self.factorTable)
        self.nodeForFactorModel = nodeForFactorModel.Model(self.nodeTable)
        self.gsModel = groundingsModel.Model(self.groundingSpaceTable)
        self.groundingSpace = None

        self.connect(self.groundingSpaceTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectGrounding)


        self.connect(self.esdcTreeView.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectEsdc)

        self.connect(self.factorTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectFactor)


        self.connect(self.nodeTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectNode)

        self.connect(self.pdfButton,
                     SIGNAL("clicked()"),
                     self.saveToPdf)
        
        self.connect(self.latexButton,
                     SIGNAL("clicked()"),
                     self.saveToLatex)

        self.baseWindowTitle = "GGG Browser"
    def selectNode(self):
        selectedNode = self.nodeForFactorModel.selectedNode()

        if selectedNode.is_gamma:
            gs = self.groundingSpace.grounding_space(selectedNode, 
                                                     self.ggg.context)
        else:
            gs = []
            
        self.gsModel.setData(gs)
        self.draw()
        
    def selectEsdc(self):
        print "selecting esdc"

    def selectGrounding(self):
        self.draw()

    def selectFactor(self):
        factor = self.factorModel.selectedFactor()
        esdc = self.ggg.factor_to_esdc(factor)
        if esdc != None:
            self.esdcModel.setData(esdc)
        self.nodeForFactorModel.setData([(self.ggg, factor, n) for n in factor.nodes])

    def saveToPdf(self):
        fname = str(self.gggFilename.text())
        if fname:
            self.ggg.to_file(fname)

    def saveToLatex(self):
        fname = str(self.gggFilename.text())
        if fname:
            self.ggg.to_latex(fname)

    def draw(self):
        self.axes.clear()
        
        for grounding in self.gsModel.selectedGroundings():
            drawGrounding(self.axes, grounding,
                          plotArgs=dict(color="purple", lw=4))

        for grounding in self.ggg.context.groundings:
            drawGrounding(self.axes, grounding,
                          plotArgs=dict(color="green"))



        selected_nodes = self.nodeForFactorModel.selectedNodes()
        for e in self.nodeForFactorModel.entries:
            
            if e.node.is_gamma and e.ggg.is_grounded(e.node):
                evidences = self.ggg.evidence_for_node(e.node)
                for g in evidences:
                    if e.node in selected_nodes:
                        plotArgs = dict(color="yellow", lw="4")
                    else:
                        plotArgs = dict(color="black")
                    drawGrounding(self.axes, g, plotArgs=plotArgs)

        

        self.restoreLimits()
        self.figure.canvas.draw()

    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self, limits=None):
        if limits != None:
            self.limits = limits
        if self.limits != None:
            self.axes.axis(self.limits)
        else:
            self.saveLimits()

    def load(self, ggg, groundingSpace=None, node=None):
        self.ggg = ggg
        highlightTextLabel(self.commandText, self.ggg.esdcs)
        if groundingSpace != None:
            self.groundingSpace = groundingSpace

        self.factorModel.setData(self.ggg.factors, self.ggg)
        self.setWindowTitle(self.baseWindowTitle + ": " + 
                            self.ggg.esdcs.text[0:100])
        if node != None:
            for f in node.factors:
                self.factorModel.selectFactor(f)
                break
            self.nodeForFactorModel.selectNode(node)
        self.limits = None
        self.draw()
def main(argv):
    app = basewindow.makeApp()

    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("--training_filename",dest="training_fname", 
                      help="Training Filename", metavar="FILE")
    (options, args) = parser.parse_args()
    
    annotations = annotationIo.load(options.training_fname)
    annotation = annotations[0]
    state, esdc_to_ggg = annotation_to_ggg_map(annotation)
    ggg = esdc_to_ggg[annotation.esdcs[0]]


    wnd= MainWindow()
    wnd.show()
    
    wnd.load(ggg)
    app.exec_()


if __name__=="__main__":
    import sys
    main(sys.argv)


