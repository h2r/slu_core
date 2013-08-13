import matplotlib_qt

from forkliftBrowserTools import ForkliftBrowserTools
from dataEvaluation.evaluateCorpus import planToLcmLog
import os
import signal
from optparse import OptionParser
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL, QSocketNotifier
import agileGui_ui
import basewindow
from g3.cost_functions.cost_function_crf import CostFnCrf
import costFunctionBrowser
from forklift import state_extractor, action_executor
from rndf_util import rndf
from forklift.esdcSearch import BeamSearch
from dataEvaluation import agile_videos
from features.linguistic_features import load_maps

class MainWindow(QMainWindow, agileGui_ui.Ui_MainWindow):
    def __init__(self, rndfFname, skelFname, modelFname):
        QMainWindow.__init__(self)
        self.setupUi(self)        

        self.skelFname = skelFname
        self.rndfFname = rndfFname
        

        self.rndf = rndf(self.rndfFname)
        assert rndf !=  None

        self.taskPlanner = BeamSearch(CostFnCrf.from_mallet(modelFname), 
                                      useRrt=False)

        self.stateApp = state_extractor.App(self.rndfFname)
        
        self.actionApp = action_executor.App(rndf_file=self.rndfFname)
        
        self.agileRun = agile_videos.AgileRun(self.stateApp.lc,
                                              startSheriff=False)

        self.socket = QSocketNotifier(self.stateApp.lc.fileno(),
                                      QSocketNotifier.Read)
        self.stateApp.lc.subscribe("SPEECH", self.onSpeech)
        
        self.connect(self.socket,
                     SIGNAL("activated(int)"),
                     self.socketActivated)


        self.cfBrowser = costFunctionBrowser.MainWindow(ForkliftBrowserTools(),
                                                        self.taskPlanner, 
                                                        initialState=False)
        self.cfBrowser.show()
        self.connect(self.submitButton,
                     SIGNAL("clicked()"),
                     self.followCommand)

        self.connect(self.sendActionButton,
                     SIGNAL("clicked()"),
                     self.sendAction)

        self.connect(self.viewStateButton,
                     SIGNAL("clicked()"),
                     self.updateState)

        signal.signal (signal.SIGINT, lambda *s: self.cleanup())
        load_maps()

    def cleanup(self):
        self.agileRun.cleanup()
        sys.exit(1)

    def onSpeech(self, channel, command):
        self.commandEdit.setPlainText(command)
                
    def updateState(self):
        curr_state, new_am = self.stateApp.get_current_state_no_rndf()
        self.cfBrowser.updateState(curr_state, new_am)
        self.am = new_am
        return curr_state
    
    def followCommand(self):
        #interchange these two lines to use or not use RNDF nodes
        #curr_state, new_am = self.updateState()
        curr_state, new_am = self.stateApp.get_current_state_no_rndf()
        self.cfBrowser.updateState(curr_state, new_am)

        self.am = new_am
        print [ curr_state.getGroundableById(x).tags for x in curr_state.getObjectsSet() ]
        cmd = str(self.commandEdit.toPlainText())
        self.esdcs, self.plans = self.cfBrowser.followCommand(cmd, curr_state)
        
    def sendAction(self):
        self.actionApp.set_transform(self.stateApp.trans_xyz, self.stateApp.trans_latlon, self.stateApp.trans_theta)

        plan = self.cfBrowser.plansModel.selectedData()
        lcmFname = "/tmp/lcmcommands_%d.lcm" % os.getpid()
        planToLcmLog(plan.annotation, lcmFname,
                     rndf=self.rndf, actionMap=self.am, app=self.actionApp, realForklift=True)
        #self.agileRun.sendCommands(lcmFname)        
        agile_videos.sendCommands(lcmFname)
    def socketActivated(self, arg):
        self.stateApp.lc.handle()
        
def main(argv):
    parser = OptionParser()
    parser.add_option("--model-filename",dest="model_fname", 
                      help="CRF Filename", metavar="FILE")
    parser.add_option("--rndf-filename",dest="rndf_fname", 
                      help="RNDF Filename", metavar="FILE")
    parser.add_option("--skeleton-filename",dest="skel_fname", 
                      help="Skeleton Filename", metavar="FILE")    
    parser.add_option("--use-rrt",dest="use_rrt", 
                      help="Use RRT?", metavar="FILE")    

    (options, args) = parser.parse_args()    
    print "loading model at:", options.model_fname


    app = basewindow.makeApp()

    wnd = MainWindow(options.rndf_fname, options.skel_fname, options.model_fname)
    wnd.show()
    
    app.exec_()

if __name__=="__main__":
    import sys
    main(sys.argv)

    
