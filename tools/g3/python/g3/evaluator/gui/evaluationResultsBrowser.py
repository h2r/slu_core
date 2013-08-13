import matplotlib_qt
import sys
import pickle_util
import random
from environ_vars import SLU_HOME
import yaml
import signal
from g3.evaluator.plot_entropy import plot_entropy_curves
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL
import pylab as mpl
from qt_window_manager import WindowManager
import basewindow
import evaluationResultsBrowser_ui
from g3.cost_functions.gui import nodeFeatureWeights
from g3.evaluator.gui import resultsModel
from g3.evaluator.gui import nodeResultsModel
from g3.inference.gui import costFunctionBrowser
from optparse import OptionParser
from esdcs.gui import context3d
from esdcs.gui.esdc_utils import highlightTextLabel
from g3.gui import gggBrowser
from g3.evaluator.evaluateCorpus import ResultsFile
from g3.evaluator.evaluate_nodes import compute_node_results

from g3.inference import nodeSearch
from g3.cost_functions import cost_function_crf as cf
import os


'''Allows for viewing of the evaluation results from generate_plans. Displays a cost function browser as well as lists of feature weights, and allows the cost function browser to display the actual path for the annotation alongside the inferred path.'''

class MainWindow(QMainWindow, evaluationResultsBrowser_ui.Ui_MainWindow):
    def cleanup(self):
        sys.exit(1)

    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()

    def __init__(self, model):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.windowManager = WindowManager(self.windowsMenu)

        self.taskPlanner = nodeSearch.BeamSearch(cf.CostFnCrf.from_mallet(model))

        self.cfBrowser = costFunctionBrowser.MainWindow(limits=[10, 40, 10, 40],
                                                        taskPlanner = self.taskPlanner,
                                                        initialState=False)
        self.cfBrowser.setWindowTitle(str(self.cfBrowser.windowTitle()) +
                                      " (Evaluation Results Browser)")
        self.windowManager.addWindow(self.cfBrowser)


        self.nodeFeatureWeights = nodeFeatureWeights.MainWindow()

        self.gggBrowser = gggBrowser.MainWindow()
        self.gggBrowser.setWindowTitle(self.gggBrowser.windowTitle() + " (Evaluation Results Browser)")
        self.windowManager.addWindow(self.gggBrowser)


        self.contextWindow = context3d.MainWindow()
        self.contextWindow.setWindowTitle(self.contextWindow.windowTitle() +
                                          " - Annotation")
        self.windowManager.addWindow(self.contextWindow)

        self.contextWindowInferred = context3d.MainWindow()
        self.contextWindowInferred.setWindowTitle(self.contextWindow.windowTitle() +
                                          " - Inferred")
        self.windowManager.addWindow(self.contextWindowInferred)


        self.original_commands_fname = None

        self.figure = mpl.figure()
        self.axes = self.figure.gca()

        self.limits = [10, 40, 10, 40]
        self.restoreLimits()
        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)

        self.resultsModel = resultsModel.Model(self.resultsTable)
        self.resultListModel = resultsModel.Model(self.resultListTable)
        self.nodeResultsModel = nodeResultsModel.Model(self.nodeResultsTable)


        self.model = None
        self.dataset = None

        self.connect(self.resultsTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectResult)

        self.connect(self.nodeResultsTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectNodeResult)

        self.connect(self.sendToCfbButton,
                     SIGNAL("clicked()"),
                     self.sendToCfb)

        self.connect(self.recomputeEntropyButton,
                     SIGNAL("clicked()"),
                     self.recomputeEntropy)
        self.connect(self.saveNodeResultsButton,
                     SIGNAL("clicked()"),
                     self.saveNodeResults)

        self.connect(self.plotEntropyButton,
                     SIGNAL("clicked()"),
                     self.plotEntropy)

        self.connect(self.sendToCfbNodeButton,
                     SIGNAL("clicked()"),
                     self.sendToCfbNode)

        self.connect(self.esdcFilter,
                     SIGNAL("editingFinished()"),
                     self.filterEsdcs)

        self.connect(self.nodeFilter,
                     SIGNAL("editingFinished()"),
                     self.filterNodes)


        print "adding export button"
        self.connect(self.exportResultsButton,
                     SIGNAL("clicked()"),
                     self.sendToClipboard)

        print "adding export button"
        self.connect(self.exportNodeResultsButton,
                     SIGNAL("clicked()"),
                     self.sendToClipboardNodeResults)

        self.filterEsdcs()
        self.filterNodes()
        self.resultsTable.selectRow(0)

        signal.signal (signal.SIGINT, lambda *s: self.cleanup())

    def sendToClipboard(self):
        self.resultsModel.sendToClipboard()

    def sendToClipboardNodeResults(self):
        self.nodeResultsModel.sendToClipboard()

    def sendToCfbNode(self):
        result = self.nodeResultsModel.selectedEntry().best_result
        self.sendResultToCfb(result)


    def sendResultToCfb(self, result):
        self.cfBrowser.updateEsdcs(result.esdcs, result.start_gggs)
        self.cfBrowser.currAnnotation = result.annotation
        self.cfBrowser.setState(result.start_state)


    def sendToCfb(self):
        '''send a command to the cost function browser'''

        selectedResults = self.resultListModel.selectedData()
        selectedResult = selectedResults[0]

        self.sendResultToCfb(selectedResult)



    def filterNodes(self):
        expr = self.nodeFilter.text()
        print expr
        try:
            filterFunction = eval(str(expr))
        except:
            raise
        self.nodeResultsModel.setFilter(filterFunction)
        self.updateNodeLabels()

    def filterEsdcs(self):
        expr = self.esdcFilter.text()
        print expr
        try:
            filterFunction = eval(str(expr))
        except:
            raise
        self.resultsModel.setFilter(filterFunction)
    def plotEntropy(self):
        print "making figure"
        entries = self.nodeResultsModel.selectedEntries()
        plot_entropy_curves(entries, "%d entries " % len(entries))
        mpl.show()

    def saveNodeResults(self):
        entries = self.nodeResultsModel.entries
        for e in entries:
            e.ggg = None
            e.annotation = None
            #e.results = [e.results[0]] + random.sample(e.results[1:], 50)
            for r in e.results:
                r.end_ggg.remove_cost_entries()



        fname = "node_results.pck"
        print "saving", fname, "..."
        pickle_util.save("node_results.pck", entries)
        print "done"

    def recomputeEntropy(self):
        print "making figure"
        fname = "%s/tools/g3/python/g3/evaluator/test_metric.py" % SLU_HOME

        locals_dict = {}
        execfile(fname, globals(), locals_dict)
        metric = locals_dict["metric"]

        entries = self.nodeResultsModel.entries
        for entry in entries:
            entry.entropy = metric(entry.results, entry.node)

        self.nodeResultsModel.reset()
        plot_entropy_curves(entries, "%d entries " % len(entries))
        mpl.show()

    def selectNodeResult(self, newSelection, oldSelection):
        result = self.nodeResultsModel.selectedEntry()
        self.contextWindowInferred.setContext(result.annotation.context.withoutPaths())
        self.contextWindowInferred.highlightGroundings([result.labeled_pobj],
                                                       color="green")
        if result.inferred_pobj != None:
            self.contextWindowInferred.highlightGroundings([result.inferred_pobj],
                                                           color="red")

        highlightTextLabel(self.entireEsdcTextNode, result.node_esdc)


        self.updateNodeLabels()
        self.gggBrowser.load(result.ggg)

    def updateNodeLabels(self):
        self.updateAccuracyLabel(self.nodeResultsModel.selectedEntries(),
                                 self.selectedNodeAccuracyLabel)
        self.updateAccuracyLabel(self.nodeResultsModel.allData(),
                                 self.overallNodeAccuracyLabel)
    def updateAccuracyLabel(self, data, label):
        if len(data) == 0:
            accuracy = 0
            num = 0
            denom = 0
        else:
            num = float(len([r for r in data if r.correct]))
            denom = len(data)
            accuracy = num / denom
        label.setText("%.3f (%d of %d)" % (accuracy, num, denom))




    def selectResult(self, newSelection, oldSelection):
        selectedResults = self.resultsModel.selectedData()
        result = selectedResults[0]
        self.contextWindow.setContext(result.annotation.context)
        self.contextWindowInferred.setContext(result.annotation.context.withoutPaths())
        self.contextWindowInferred.highlightGroundings(result.end_ggg.groundings,
                                                       color="cyan")

        highlightTextLabel(self.entireEsdcText, result.esdcs)

        self.resultListModel.loadResults(result)
        self.resultListTable.selectRow(0)
        self.nodeResultsModel.setData(compute_node_results(selectedResults, self.original_commands_fname))
        self.updateNodeLabels()

    def load(self, dataset_fname, results_dir, original_commands_fname):
        self.resultsFile = ResultsFile(results_dir)
        self.original_commands_fname = original_commands_fname
        with open("%s/parameters.yaml" % results_dir, "r") as f:
            self.parameters = yaml.load(f)
            self.cfBrowser.beamWidthBox.setValue(self.parameters['beam_width'])
            self.cfBrowser.seqBeamWidthBox.setValue(self.parameters['beam_width_sequence'])
            self.cfBrowser.searchDepthBox.setValue(self.parameters['search_depth_event'])
            self.cfBrowser.beamWidthEventBox.setValue(self.parameters['beam_width_event'])




        self.agileRunSummaryLog = "%s/agile_run_summary_log.txt" % results_dir
        if (os.path.exists(self.agileRunSummaryLog) == False):
            f = open (self.agileRunSummaryLog, 'w')
            f.write('# ' + results_dir + '\n')
            f.write('# EvaluationTimeSec LCMCommandLog\n')
            f.close()
        self.setWindowTitle("Evaluation Results Browser: " + results_dir)
        self.resultsModel.loadResultsFile(self.resultsFile)


    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self):
        if self.limits != None:
            self.axes.axis(self.limits)


def main(argv):
    app = basewindow.makeApp()

    parser = OptionParser()

    parser.add_option("--model-filename", dest="model_fname",
                      help="CRF Filename", metavar="FILE")

    parser.add_option("--original-commands", dest="original_commands_fname",
                      metavar="FILE")

    (options, args) = parser.parse_args()

    print "loading model at:", options.model_fname

    from sys import argv

    wnd = MainWindow(options.model_fname)
    print "loading"
    wnd.load(argv[1], argv[2], options.original_commands_fname)
    print "showing"
    wnd.show()

    app.exec_()

if __name__=="__main__":
    main(sys.argv)


