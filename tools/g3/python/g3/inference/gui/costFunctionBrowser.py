import matplotlib_qt
from environ_vars import SLU_HOME
from qt_window_manager import WindowManager
from esdcs import esdcIo
import numpy as na
import math
import pickle_util
from esdcs.context import Context
import yaml
from esdcs.dataStructures import breadthFirstTraverse, ExtendedSdcGroup
from esdcs.extractor import extractor_utils
from spatial_features.groundings import PhysicalObject, Path, Place
from esdcs.gui.drawUtils import drawObject, drawPath, drawRobot
from esdcs.gui import context3d, esdcTreeModel

from g3.cost_functions.cost_function_crf import CostFnCrf
from g3.cost_functions import cost_function_constant
from g3.cost_functions.gui import crfFeatureWeights
from g3.cost_functions.gui import nodeFeatureWeights
from g3.evaluator import evaluateCorpus
from g3.feature_extractor.gui import esdcFeatureBrowser 
from g3.gui import gggBrowser
from g3.inference import nodeSearch
from g3.inference.gui import plansModel
from g3.state import state_type_from_name
from g3.esdcs_to_ggg import gggs_from_esdc_group
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from os.path import dirname
from optparse import OptionParser
from PyQt4.QtGui import QMainWindow, QFileDialog
from PyQt4.QtCore import SIGNAL

import basewindow
import cProfile
import g3.inference.gui.costFunctionBrowser_ui as costFunctionBrowser_ui
import pylab as mpl
import time

class MainWindow(QMainWindow, costFunctionBrowser_ui.Ui_MainWindow):
    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()
    def __init__(self, 
                 limits,
                 taskPlanner=None, initialState = True,
                 show_gui=True,  merging_mode="merge_none",
                 start_command=None):

        QMainWindow.__init__(self)
        self.setupUi(self)

        self.windowManager = WindowManager(self.windowsMenu)
        self.artists = []
        self.extractor = None
        self.taskPlanner = taskPlanner
        self.plansDict = None
        self.currAnnotation = None
        self.save_state_tree = True
        self.allow_null_action = False

        self.command = ""
        if start_command:
            self.command = start_command
            self.commandEdit.setPlainText(start_command)


        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)

        self.limits = limits

        self.restoreLimits()
        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)

        self.esdcFeatureBrowser = esdcFeatureBrowser.MainWindow()
        self.esdcFeatureBrowser.setWindowTitle(str(self.esdcFeatureBrowser.windowTitle()) +
                                               " (ESDC Feature Browser)")

        self.contextWindow = context3d.MainWindow()
        self.contextWindow.setWindowTitle(self.contextWindow.windowTitle() + 
                                          " - Cost Function Browser")

        self.windowManager.addWindow(self.contextWindow)

        self.gggWindow = gggBrowser.MainWindow()
        self.gggWindow.setWindowTitle(self.gggWindow.windowTitle() + "(GGG Visualizer)")
        self.windowManager.addWindow(self.gggWindow)


        self.crfFeatureWeights = crfFeatureWeights.MainWindow()
        self.crfFeatureWeights.setWindowTitle(str(self.crfFeatureWeights.windowTitle()) +
                                              " (CFB)")
        self.windowManager.addWindow(self.crfFeatureWeights)


        self.nodeFeatureWeights = nodeFeatureWeights.MainWindow()
        self.nodeFeatureWeights.setWindowTitle(str(self.nodeFeatureWeights.windowTitle()) +
                                              " (CFB)")
        self.windowManager.addWindow(self.nodeFeatureWeights)

        self.esdcModel = esdcTreeModel.Model(self.esdcView)
        self.plansModel = plansModel.Model(self.plansView)
        
        self.connect(self.submitButton,
                     SIGNAL("clicked()"),
                     self.followCommandSelf)
  
        self.connect(self.esdcView.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectEsdc)        


        self.connect(self.plansView.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectPlan)
                     

        self.connect(self.esdcParserComboBox,
                     SIGNAL("currentIndexChanged( QString)"),
                     self.selectEsdcExtractor)


        self.connect(self.rrtCacheButton,
                     SIGNAL("clicked()"),
                     self.saveRrtCache)

        self.connect(self.esdcParserModelButton,
                     SIGNAL("clicked()"),
                     self.askForEsdcParserModel)


        self.connect(self.saveCommandLogButton,
                     SIGNAL("clicked()"),
                     self.planToLcmLog)


        self.connect(self.actionLoadContext,
                     SIGNAL("triggered()"),
                     self.loadContext) 
        self.connect(self.actionSaveState,
                     SIGNAL("triggered()"),
                     self.saveState) 
        self.connect(self.actionLoadState,
                     SIGNAL("triggered()"),
                     self.loadState) 

        self.connect(self.actionGroundingProbabilityGraph,
                     SIGNAL("triggered()"),
                     self.groundingProbabilityGraph) 

        self.esdcParserModelButton.setText("%s/data/directions/direction_training/annotation/models/crf_discrete_esdcs_1.5.pck" % SLU_HOME)
        
        self.esdcs = []
        self.factors_to_esdcs = None
        self.gggs = None

        #self.selectEsdcExtractor()

        self.merging_mode = merging_mode

    def loadContext(self):
        fname = QFileDialog.getOpenFileName(self)
        context = Context.fromYaml(yaml.load(open(fname)))


    def saveState(self):
        fname = QFileDialog.getSaveFileName(self)
        pickle_util.save(fname, self.state)

    def loadState(self):
        fname = QFileDialog.getOpenFileName(self)
        state = pickle_util.load(fname)
        self.setState(state)
        

    def showGui(self):
        self.esdcFeatureBrowser.show()
        self.crfFeatureWeights.show()
        self.nodeFeatureWeights.show()

    def show(self):
        self.contextWindow.show()
        QMainWindow.show(self)

    def askForEsdcParserModel(self):
        existingFname = str(self.esdcParserModelButton.text())
        fname = str(QFileDialog.getOpenFileName(self, directory=dirname(existingFname)))
        print "fname", fname, fname.__class__
        if fname != "":
            self.esdcParserModelButton.setText(fname)
        

    def selectEsdcExtractor(self):

        esdc_extractor = str(self.esdcParserComboBox.currentText())
        esdc_extractor_model = str(self.esdcParserModelButton.text())
        self.extractor = extractor_utils.make_extractor_func(esdc_extractor,
                                                        esdc_extractor_model)

        
        
    def updateEsdcs(self, esdcs, gggs=None):
        self.esdcs = esdcs
        self.esdcModel.setData(self.esdcs)
        self.updateCommand(self.esdcs.text)
        self.gggs = gggs

    def setState(self, state):  
        self.state = state
        self.contextWindow.setContext(state.to_context())
        self.drawStateOnly()

    def setContext(self, context):
        state = self.state.from_context(context)
        self.setState(state)


    def updateCommand(self, command):
        self.command = command 
        self.commandEdit.setPlainText(command)                          
     
    def followCommandSelf(self):
        command = str(self.commandEdit.toPlainText())
        state = self.state
        esdcs = None

        self.followCommand(command, state, esdcs)

    def followCommand(self, command=None, state=None, esdcs=None,
                 first_esdc_only=False, verbose=True, input_gggs=None):
        if command != None:
            self.updateCommand(command)

        if state != None:
            self.state = state

        command = str(self.commandEdit.toPlainText())

        if input_gggs != None:
            self.esdcs = input_gggs[0].esdcs
        elif esdcs != None and command == self.command:
            self.esdcs = esdcs
        else:
            class AnnotationStub:
                def __init__(self, command):
                    self.entireText = command

            self.esdcs = self.extractor(AnnotationStub(command))

            if len(self.esdcs) == 0:
                return [], []
            if first_esdc_only:
                self.esdcs = ExtendedSdcGroup([self.esdcs[0]])
                self.flattenedEsdcs = self.esdcs.flattenedEsdcs
        print "esdcs", esdcIo.toYaml(self.esdcs)
                #print "flattened esdcs", self.flattenedEsdcs
       
        self.esdcModel.setData(self.esdcs)

        #convert to a list of plans
        if input_gggs != None:
            gggs = input_gggs
        elif self.gggs != None:
            gggs = self.gggs
        else:
            if self.merging_mode == "merge_coreferences":
                from coreference.bag_of_words_resolver import BagOfWordsResolver
                from coreference.merge_coreferences import merge_coreferences
                resolver = BagOfWordsResolver("%s/tools/coreference/models/coref_1.5.pck" % SLU_HOME)
                gggs = merge_coreferences(self.esdcs, resolver)
                if len(gggs) > 1:
                    gggs = [gggs[0]]
            elif self.merging_mode == "merge_events":
                from coreference.event_resolver import EventResolver
                from coreference.merge_coreferences import merge_coreferences
                resolver = EventResolver()
                gggs = merge_coreferences(self.esdcs, resolver)
                gggs = gggs[0:1]
                for i, ggg in enumerate(gggs):
                    #ggg.to_latex("ggg_%d.pdf" % i)
                    pass

                # export parses, when saving ground truth parses from asr evaluation run
                # -- stefie10 7/19/2012
                #from esdcs.esdcIo import toYaml
                #import yaml
                #import os
                #with open("esdcs_%d.txt" % os.getpid(), "a") as f:
                #    f.write(yaml.dump([toYaml(self.esdcs)]))
                    
                if len(self.esdcs) != 1:
                    raise ValueError("ESDCs didn't parse right: " + `self.esdcs`)
                # print "merging events", self.esdcs.entireText
                # from coreference.merge_coreferences import merge_toplevel_events
                # #resolver = EventResolver()
                # #gggs = merge_coreferences(self.esdcs, resolver, 
                # #                          verbose=False)
                # gggs = gggs_from_esdc_group(self.esdcs)
                # gggs = [merge_toplevel_events(gggs)]
                
                assert len(gggs) == 1, (len(gggs), self.esdcs.text)
            elif self.merging_mode == "merge_none":
                gggs = gggs_from_esdc_group(self.esdcs)
            else:
                raise ValueError("Bad merging mode: " + `self.merging_mode`)

            if gggs[0].context == None:
                gggs[0].context = self.state.to_context()
            assert gggs[0].context.agent != None
        def run():
            try:
                assert gggs[0].context.agent != None
                self.plansList = self.taskPlanner.find_plan(
                    self.state,
                    gggs,
                    beam_width=self.beamWidthBox.value(),
                    beam_width_sequence=self.seqBeamWidthBox.value(),
                    search_depth_event=self.searchDepthBox.value(),
                    beam_width_event=self.beamWidthEventBox.value(),
                    save_state_tree=self.save_state_tree,
                    allow_null_action=self.allow_null_action)
            except:
                print "excption on gggs"
                #for i, ggg in enumerate(gggs):
                #    ggg.to_latex("ggg_%d.pdf" % i)                
                raise


        start = time.time()
        cProfile.runctx("run()", globals(), locals(), "out.prof")
        end = time.time()

        if verbose:
            print "Cost Function Browser took", (end - start), "seconds."
        
        plansList = self.plansList
        if len(plansList) == 0:
            return [], []
        else:


            self.plans = plansModel.Plan.from_inference_result(self.taskPlanner, plansList)
            self.plansModel.setData(self.plans)
            self.nodeFeatureWeights.load(self.taskPlanner.cf_obj, gggs, self.plans,
                                         context=self.state.to_context())
            self.plansView.selectRow(0)
            self.gggWindow.load(plansList[0][2], groundingSpace=state.objects)
            return self.esdcs, plans



    def drawState(self):
        artists = []

        #index of manipulated object, e.g. pallet for forklift
#        index = self.browserTools.manipulated_object_index(self.state)
        # TODO remove browser tools
        index = -1

        if self.state != None:
            objects = self.state.getObjectsSet()
#            print "list of objects: ", objects
            for i, ob in enumerate(objects):
                obj = self.state.getGroundableById(ob)
                oldTags = obj.tags
                #newTags = tuple([t for t in oldTags if len(t) > 4][0:1])
                #obj.tags = newTags
                if i == index:  #plot the manipulated object in red
                    self.artists.extend(drawObject(self.axes, obj,
                                                   plotArgs = dict(color="red")))
                else:           #plot everything else in blue
                    self.artists.extend(drawObject(self.axes, obj,
                                                   plotArgs = dict(color="blue")))
                obj.tags = oldTags
            
        return artists


    def drawStateOnly(self):
        self.axes.clear()
            
        self.artists = []
        self.artists.extend(self.drawState())
        self.artists.extend(self.drawTopologicalMap())
        
        x,y = self.state.getPosition()
        theta = self.state.orientation
        self.artists.extend(drawRobot(self.axes, x, y, theta,
                                      facecolor="red"))

        self.restoreLimits()
        self.figure.canvas.draw()   
    
    def draw(self):
        self.axes.clear()

            
        self.artists = []
        self.artists.extend(self.drawTopologicalMap())
        self.artists.extend(self.drawAgentPath())
        self.artists.extend(self.drawState())
        self.artists.extend(self.drawBoundObjects())
        self.artists.extend(self.drawActualPath())

        x,y = self.state.getPosition()
        theta = self.state.orientation
        self.artists.extend(drawRobot(self.axes, x, y, theta,
                                      facecolor="red"))



        self.restoreLimits()
        self.figure.canvas.draw()
        

    def drawBoundObjects(self):
         

        ggg = self.plansModel.selectedData().ggg

        artists = []
        selectedEsdc = self.esdcModel.selectedEsdc()

        def callback(esdc):
            if selectedEsdc == esdc:
                selected = True
            else:
                selected = False

            artists.extend(self.drawGroundingsForEsdc(esdc, ggg, selected))

        breadthFirstTraverse(self.esdcs, callback)
        
        return artists


    def drawGroundingsForEsdc(self, esdc, ggg, selected=False):
        artists = []


        factor = ggg.esdc_to_factor(esdc)
        if factor ==  None:
            return []
        #print "***** groundings"
        #print "esdc is:", esdc

        groundings = ggg.evidences[factor.nodes_for_link("top")[0].id]
        #print repr(groundings)
        #print "-----lambdas"
        #print ggg.evidences[factor.nodes_with_type("lambda")[0].id]
        if len(groundings) == 0:
            print 'no groundings', esdc
            return artists

        value = groundings[0]
        #print "value", value, value.__class__
        if isinstance(value, PhysicalObject) or isinstance(value, Place):
            #print "drawing obj", value
            if selected:
                plotArgs=dict(color="yellow", linewidth=3)
            else:
                plotArgs=dict(color="black")
                
            artists.extend(drawObject(self.axes, value, plotArgs))
        elif isinstance(value, Path):
            X,Y = value.points_xy
            args = dict(color="green", linewidth=1)            
            artists.extend(self.axes.plot(X, Y, "ro-", markersize=1,
                                              **args))
        elif isinstance(value, list): #then value is a sequence of actions  
            raise ValueError("no longer supported")

        self.mpl_draw()
        return artists
    
    def drawTopologicalMap(self):
        args = dict(linewidth=1, color="red")
        artists = []
        nodeLocs = []

        nodeLocs = self.state.topological_locations
        
        for loc in nodeLocs:
            x, y = loc
            artists.extend(self.axes.plot([x],[y],"ro-",markersize=3, **args))

        return artists
    
    def drawAgentPath(self):
        plan = self.plansModel.selectedData()

        artists = []
        if plan != None:
            state = plan.state
            agent = state.getGroundableById(state.getAgentId())
            artists.extend(drawObject(self.axes, agent, 
                                      shouldDrawStartAndEnd=True))
        return artists

    def drawActualPath(self):
        artists = []
        if(self.currAnnotation):
            path = self.currAnnotation.agent.path

            plotArgs = dict(color="red", linewidth = 3)
            artists.extend(drawPath(self.axes, path, plotArgs))

        return artists
    
    def selectEsdc(self):
#        if self.esdcModel.selectedEsdc() in self.plansDict:
#            self.plansModel.setData(self.plansDict[self.esdcModel.selectedEsdc()])
#            self.esdcFeatureBrowser.selectEsdc(self.esdcModel.selectedEsdc())
        self.draw()
        esdc = self.esdcModel.selectedEsdc()
        plan = self.plansModel.selectedData()
        ggg = plan.ggg
        factor = ggg.esdc_to_factor(esdc)
        print "factor", factor, esdc
        if factor != None:
            print "loading crf feature weights"
            self.crfFeatureWeights.load(ggg.context, self.taskPlanner.cf_obj, factor)
        
    def selectPlan(self):
        #selectedAnnotation = self.plansModel.selectedPlan()
        #print selectedAnnotation.toYaml()
        #self.esdcFeatureBrowser.loadAnnotations([selectedAnnotation])

        state, ggg = self.plansModel.selectedPlan()
        self.contextWindow.setContext(state.to_context())
        self.contextWindow.highlightGroundings(ggg.groundings)

        print self.plansModel.selectedData().plan_string

               
        self.draw()

        
    def saveRrtCache(self):
        if self.taskPlanner.useRrt:
            self.taskPlanner.rrt.saveCache()

    def clearRrtCache(self):
        if self.taskPlanner.useRrt:
            self.taskPlanner.rrt.clearCache()

    def planToLcmLog(self):
        plan = self.plansModel.selectedData().annotation
        fname = 'testlog.lcm'
        
        if plan != None:
            evaluateCorpus.planToLcmLog(plan, fname, actionMap=self.state.actionMap)
        
    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self):
        if self.limits != None:
            self.axes.axis(self.limits)

    def groundingProbabilityGraph(self):
        print "graph"
        mpl.figure()
        selectedEsdc = self.esdcModel.selectedEsdc()
        if selectedEsdc == None:
            return
        values_to_prob = {}
        values_to_groundings = {}
        for plan in self.plansModel._data:
            factor = plan.ggg.esdc_to_factor(selectedEsdc)
            assert len(factor.gamma_nodes) == 1
            node = factor.gamma_nodes[0]
            node_value = plan.ggg.evidence_for_node(node)[0].withoutPath()
            
            node_value_hash = tuple(node_value.hash_string)
            cost = plan.ggg.cost_for_factor(factor)
            prob = math.exp(-cost)
            if node_value_hash in values_to_prob:
                assert values_to_prob[node_value_hash] == prob
            else:
                values_to_prob[node_value_hash] = prob
            values_to_groundings[node_value_hash] = node_value

        X = []
        heights = []
        labels = []
        for i, (key, prob) in enumerate(values_to_prob.iteritems()):
            grounding = values_to_groundings[key]

            X.append(i)
            heights.append(prob)
            labels.append(grounding.tags)
        mpl.bar(X, heights)
        mpl.xticks(na.array(X) + 0.4, labels)
        mpl.ylabel("Probability")
        mpl.ylim(0, 1)
        mpl.show()
     
def main(argv):
    app = basewindow.makeApp()
    
    parser = OptionParser()

    parser.add_option("--model-filename",dest="model_fname", 
                      help="CRF Filename", metavar="FILE")

    parser.add_option("--use-rrt",dest="use_rrt", 
                      help="Use RRT?")

    parser.add_option("--limits", dest="limits",
                      help="Browser axis limits", metavar="FILE")

    parser.add_option("--state-type",dest="state_type",
                      help="State or Agent Type", metavar="FILE")

    parser.add_option("--merging-mode", dest="merging_mode",
                      default="merge_none")

    parser.add_option("--start-command", dest="start_command", 
                      help="Initial Command", default=None)

    parser.add_option("--start-state-file", dest="start_state_fname", 
                      help="Initial state file", default=None)
    parser.add_option("--start-context-file", dest="start_context_fname", 
                      help="Initial context file", default=None)

    parser.add_option("--search-depth", dest="search_depth", type="int",
                      default=1)

    parser.add_option("--beam-width", dest="beam_width", type="int",
                      default=2)


    parser.add_option("--beam-width-event", dest="beam_width_event", type="int",
                      default=2)
    



    (options, args) = parser.parse_args()
    
    useRrt = False

    cf = CostFnCrf.from_mallet(options.model_fname)
    #cf_constant = cost_function_constant.CostFunction(cf.lccrf.dataset)
    taskPlanner = nodeSearch.BeamSearch(cf, useRrt=useRrt)
    

    limits = [float(x) for x in options.limits.split(",")]
    

    wnd = MainWindow(taskPlanner=taskPlanner, limits=limits,
                     merging_mode=options.merging_mode, 
                     start_command=options.start_command)
    wnd.searchDepthBox.setValue(options.search_depth)
    wnd.beamWidthBox.setValue(options.beam_width)
    wnd.beamWidthEventBox.setValue(options.beam_width_event)

    state_type = state_type_from_name(options.state_type)

    if options.start_state_fname != None:
        start_state = pickle_util.load(options.start_state_fname)
    elif options.start_context_fname:
        start_context = Context.fromYaml(yaml.load(open(options.start_context_fname)))
        start_state = state_type.from_context(start_context)
    else:
        start_state = state_type.init_state()
    wnd.setState(start_state)

    wnd.show()
    wnd.followCommand()
    app.exec_()

if __name__=="__main__":
    import sys
    #print "test"
    #import psyco
    #psyco.full()
    main(sys.argv)


