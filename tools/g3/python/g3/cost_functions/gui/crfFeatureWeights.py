import matplotlib_qt
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from PyQt4.QtGui import QMainWindow
from qt_window_manager import WindowManager
from PyQt4.QtCore import SIGNAL
import crfFeatureWeights_ui
from esdcs.gui import context3d
from esdcs.context import Context
from dcrf3.gui import featureModel
import candidateModel
from esdcs.gui import groundingsModel
from g3.graph import GGG
import pylab as mpl
import qt_utils
from esdcs.gui.drawUtils import drawGrounding, drawRobot, drawObject

class MainWindow(QMainWindow, crfFeatureWeights_ui.Ui_MainWindow):

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



    def __init__(self, taskPlanner=None, initialState=True):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.featureModel = featureModel.Model(self.featureTable)
        self.candidateModel = candidateModel.Model(self.factorCandidateTable)
        self.groundingsModel = groundingsModel.Model(self.groundingTable)
        self.windowManager = WindowManager(self.windowsMenu)
        self.contextWindow = context3d.MainWindow()
        self.contextWindow.setWindowTitle(self.contextWindow.windowTitle() + 
                                          " - CRF Feature Weights")
        self.windowManager.addWindow(self.contextWindow)


        self.connect(self.factorCandidateTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectCandidate)        

        self.connect(self.groundingTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.draw)        
        self.connect(self.shouldDrawTextCheckBox, SIGNAL("stateChanged(int)"),
                     self.draw)
        self.connect(self.shouldDrawIconsCheckBox, SIGNAL("stateChanged(int)"),
                     self.draw)
        self.connect(self.shouldDrawAgentCheckBox, SIGNAL("stateChanged(int)"),
                     self.draw)
        self.connect(self.shouldDrawObjectGeomCheckBox, SIGNAL("stateChanged(int)"),
                     self.draw)


        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)
        self.limits = [-20, 30, 10, 51]
        #self.limits = [10, 40, 10, 40]
        self.restoreLimits()
        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)
        self.figure.canvas.mpl_connect('button_press_event', self.mapClick)
        self.costImage = None

    def load(self, context, cf_obj, factor):
        self.cf_obj = cf_obj
        self.candidateModel.setData(cf_obj.factor_to_cost[factor], cf_obj)
        self.factorCandidateTable.selectRow(0)
        if context == None:
            context = Context.empty_context()
        self.contextWindow.setContext(context)

        
    def selectCandidate(self):
        entry = self.candidateModel.selectedEntry()
        if entry != None:
            self.featureModel.setData(self.cf_obj.lccrf, entry.candidate.dobs)
            self.featureTable.sortByColumn(featureModel.COL_WEIGHT_ABS)
            self.groundingsModel.setData(list(entry.groundings))
            self.groundingTable.selectAll()
            import math
            for phi in [True, False]:
                ev = entry.ggg.evidences.add(entry.factor.phi_node.id, phi)
                ggg = GGG.from_ggg_and_evidence(entry.ggg, ev)
                cost, cobs, dobs = self.cf_obj.compute_factor_cost(entry.factor, 
                                                                   ggg, entry.states)
                
                prob = math.exp(-cost)
                print phi, prob
            entry.ggg.set_evidence_for_node(entry.factor.phi_node, phi)            
            print "highlighting", entry.groundings
            self.contextWindow.highlightGroundings(entry.all_groundings)
        self.draw()

    def draw(self):
        self.axes.clear()
        #self.axes.set_xticks([])
        #self.axes.set_yticks([])
        
        if self.costImage:
            self.axes.imshow(self.costImage.costs, origin="lower",
                             extent=(self.costImage.xmin, self.costImage.xmax, 
                                     self.costImage.ymin, self.costImage.ymax),
#                             cmap=mpl.cm.gray)
                             cmap=mpl.cm.jet)
                              #norm=matplotlib.colors.Normalize(vmin=0.0, vmax=1.0))

        for grounding in self.groundingsModel.selectedGroundings():
            drawGrounding(self.axes, grounding, 
                          shouldDrawIcon=self.shouldDrawIcons,
                          shouldDrawText=self.shouldDrawText,
                          plotArgs=dict(color="black", lw=4))

        if self.shouldDrawAgent:
            for candidate in self.candidateModel.selectedEntries():
                if candidate.ggg.context != None:
                    agent = candidate.ggg.context.agent
                    if agent != None:
                        ax, ay, az, ath = agent.path.locationAtT(0)
                        drawRobot(self.axes, ax, ay, ath)
                        drawObject(self.axes, agent, shouldDrawPath=True)
        self.restoreLimits()
        self.figure.canvas.draw()

    def mapClick(self, mouseevent):
        if not self.costImage or mouseevent.key != 'shift':
            return
        x = mouseevent.xdata
        y = mouseevent.ydata

        for (xe,ye), entries in self.costImage.costEntries:
            if x > xe:
                continue
            if y > ye:
                continue
            break
        for i in range(self.candidateModel.rowCount(None)):
            if self.candidateModel.get(i).candidate in entries:
                self.factorCandidateTable.selectRow(i)
                break

    def setCostImage(self, costs, xmin, xmax, ymin, ymax):
        self.costImage = CostImage(costs, xmin, xmax, ymin, ymax)
        self.limits = [xmin, xmax, ymin, ymax]

    @property
    def shouldDrawIcons(self):
        return qt_utils.isChecked(self.shouldDrawIconsCheckBox)

    @property
    def shouldDrawAgent(self):
        return qt_utils.isChecked(self.shouldDrawAgentCheckBox)

    @property
    def shouldDrawObjectGeom(self):
        return qt_utils.isChecked(self.shouldDrawObjectGeomCheckBox)
    
    @property
    def shouldDrawText(self):
        return qt_utils.isChecked(self.shouldDrawIconsCheckBox)


class CostImage:
    def __init__(self, costs, xmin, xmax, ymin, ymax):
        self.costs = costs
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
