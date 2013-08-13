import matplotlib_qt
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from PyQt4.QtGui import QMainWindow
from qt_window_manager import WindowManager
from PyQt4.QtCore import SIGNAL
import nodeFeatureWeights_ui
from dcrf3.gui import featureModel
from esdcs.gui import context3d
from g3.gui import nodeModel
from g3.inference import entropy_metrics
from g3.evaluator.gui import nodeResultsModel
from g3.evaluator.gui import factorResultsModel
from g3.evaluator.evaluate_nodes import NodeResult
from g3.inference.gui import entropyMetricModel
import pylab as mpl
import math

class MainWindow(QMainWindow, nodeFeatureWeights_ui.Ui_MainWindow):

    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()
    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self):
        if self.limits != None:
            self.axes.axis(self.limits)



    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.nodeModel  = nodeModel.Model(self.nodeTable)
        self.nodeResultsModel = nodeResultsModel.Model(self.nodeResultsTable)
        self.factorResultsModel = factorResultsModel.Model(self.factorResultsTable)
        self.featureModel = featureModel.Model(self.featureTable)
        self.entropyMetricModel = entropyMetricModel.Model(self.entropyMetricTable)

        self.windowManager = WindowManager(self.windowsMenu)
        self.contextWindow = context3d.MainWindow()
        #self.context3dFrame.layout().addWidget(self.contextWindow.centralWidget())
        self.contextWindow.setWindowTitle(self.contextWindow.windowTitle() +
                                          " - Node Feature Weights")
        #self.contextWindow.show()
        self.windowManager.addWindow(self.contextWindow)

        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)
        self.limits = [-20, 30, 10, 51]
        self.restoreLimits()
        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)


        self.cf_obj = None

        self.connect(self.nodeTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectNode)
        self.connect(self.nodeResultsTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectNodeResult)

        self.connect(self.factorResultsTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectFactorResult)

    def selectNode(self):
        node = self.nodeModel.selectedNode()
        node_results = []
        for i, plan in enumerate(self.plans):
            try:
                nr = NodeResult(i, plan.ggg, node, plan.ggg)
                nr.state = plan.state
            except:
                print "couldn't get top factors for node", node
                print plan.ggg.node_to_top_esdc(node)
                raise
            node_results.append(nr)

        #self.entropyMetricModel.setData(entropy_metrics.metrics.values(), node_results)
        self.nodeResultsModel.setData(node_results)

    def selectNodeResult(self):
        r = []
        for nr in self.nodeResultsModel.selectedEntries():
            print "selected nr", nr
            r.extend([factorResultsModel.Entry(i, nr.end_ggg, factor)
                      for i, factor in enumerate(nr.node.factors)])
        self.factorResultsModel.setData(r)

        overall_cost = sum(x.cost for x in r)
        self.overallCostLabel.setText("%.3e" % overall_cost)
        self.overallProbLabel.setText("%.3e" % math.exp(-overall_cost))

        nr = self.nodeResultsModel.selectedEntry()
        print 'highlight'
        self.contextWindow.setContext(nr.state.to_context())

        self.contextWindow.highlightGroundings([nr.inferred_pobj], color="yellow")

        groundings = []
        for other_node in nr.node.factor_for_link("top").nodes:
            if other_node.is_object:
                groundings.extend(nr.ggg.evidence_for_node(other_node))

        self.contextWindow.highlightGroundings(groundings,
                                               color="green")

    def selectFactorResult(self):

        factors = self.factorResultsModel.selectedEntries()
        if len(factors) != 0:
            fr = factors[0]
            entry = fr.ggg.entry_for_factor(fr.factor)
            self.featureModel.setData(self.cf_obj.lccrf, entry.dobs)

    def load(self, cf_obj, gggs, plans, context=None):
        self.cf_obj = cf_obj
        self.ggg = gggs[0]
        self.plans = plans
        self.nodeModel.setData(self.ggg.gamma_nodes, self.ggg)
        if context != None:
            self.contextWindow.setContext(context)

        self.selectNode()
        self.selectNodeResult()
        self.nodeResultsTable.selectRow(0)
        self.selectFactorResult()

    def draw(self):
        self.axes.clear()
        self.restoreLimits()
        self.figure.canvas.draw()


