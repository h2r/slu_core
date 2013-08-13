from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL, QSocketNotifier
from g3.cost_functions.cost_function_crf import CostFnCrf
from pr2.gui import pr2CommanderGui_ui
import basewindow
import yaml
from esdcs import esdcIo
import time
from g3.inference import nodeSearch
from g3.inference.gui import costFunctionBrowser
from optparse import OptionParser
from pr2.pr2_state import Pr2State
import rosbridge
from pr2.world_state_from_ros import WorldStateFromRos
import traceback
from esdcs.gui import context3d

class MainWindow(QMainWindow, pr2CommanderGui_ui.Ui_MainWindow):
    def __init__(self, model_fname):
        QMainWindow.__init__(self)
        self.setupUi(self)        
        self.connect(self.updateStateButton,
                     SIGNAL("clicked()"),
                     self.updateState)
        self.connect(self.inferActionButton,
                     SIGNAL("clicked()"),
                     self.inferAction)
        self.connect(self.sendToRosButton,
                     SIGNAL("clicked()"),
                     self.sendToRos)

        self.taskPlanner = nodeSearch.BeamSearch(CostFnCrf.from_mallet(model_fname))
        self.cfBrowser = costFunctionBrowser.MainWindow([0, 10, 0, 10],
                                                        self.taskPlanner, 
                                                        initialState=False)
        self.cfBrowser.save_state_tree = True
        self.cfBrowser.beamWidthBox.setValue(10)
        self.cfBrowser.beamWidthEventBox.setValue(10)
        self.cfBrowser.searchDepthBox.setValue(2)

        self.contextWindow = context3d.MainWindow()
        self.contextWindow.setWindowTitle(self.contextWindow.windowTitle() + 
                                          " - PR2 Commander")
        self.contextWindow.show()

        

        try:
            #self.rosbridge = rosbridge.Rosbridge("10.68.0.118", 9090) # jihoon's machine
            #self.rosbridge = rosbridge.Rosbridge("192.168.0.149 ", 9090) # jihoon's machine
            #self.rosbridge = rosbridge.Rosbridge("128.30.31.152", 9090)
            #self.rosbridge = rosbridge.Rosbridge("localhost", 9091)
            self.rosbridge = rosbridge.Rosbridge("pr2mm1.csail.mit.edu",9091)

            print "subscribing"
            self.rosbridge.subscribe("/blocknlp/nl_input", "std_msgs/String", self.commandReceived)
            self.world_state = WorldStateFromRos.create_and_subscribe(self.rosbridge)
            

            
            self.socket = QSocketNotifier(self.rosbridge.fileno,
                                          QSocketNotifier.Read)


            
            self.connect(self.socket,
                         SIGNAL("activated(int)"),
                         self.checkSocket)



        except:
            traceback.print_exc()

    def checkSocket(self):
        self.rosbridge.check()  
    def commandReceived(self, command):
        sent_to_ros = False
        try:
            if command["data"].strip() != "":
                print "in command received"
                self.commandEdit.document().setPlainText(command["data"])
                print "resetting command edit"
                self.inferredCommandEdit.setPlainText("")
                print "--Updating State"
                self.updateState()

                print "--Inferring Action"
                self.inferAction()
                    
                print "--Sending to ROS"
                self.sendToRos()
                sent_to_ros = True
        except:
            print "ERROR: Could not process nl_input command"
            traceback.print_exc()
            exception_msg = traceback.format_exc()
            self.rosbridge.publish("/blocknlp/pr2_commander_status","std_msgs/String",
                                   {"data": str({"status":exception_msg, "is_successful":False})})
        else:
            self.rosbridge.publish("/blocknlp/pr2_commander_status","std_msgs/String",
                                   {"data": str({"status":command, "is_successful":True})})

        if not sent_to_ros:
            self.rosbridge.publish("/blocknlp/nl_output", "block_build_msgs/SLUCommand", 
                                   {"command":"(noop(),)", "do_reset":True})

    def show(self):
        self.cfBrowser.show()
        QMainWindow.show(self)

    def updateState(self):
        pr2_state = Pr2State.init_state()
        self.cfBrowser.setState(pr2_state)
        pr2_state = self.world_state.current_state()

        if pr2_state != None:
            self.cfBrowser.setState(pr2_state)
            self.contextWindow.setContext(pr2_state.to_context())
        else:
            print "No data received from ROS."

    
    def inferAction(self):
        print "infer action"
        esdcs, self.plans = self.cfBrowser.followCommand(self.commandEdit.toPlainText())

        result = self.computeResult()
        self.inferredCommandEdit.setPlainText(result)

    def computeResult(self):
        print "computing result, preparing to send to ros"
        plan = self.cfBrowser.plansModel.selectedData()
        state_sequence = self.cfBrowser.taskPlanner.state_sequence(plan.state)
        entries = []
        for action, next_state in state_sequence:
            print "name", action.name, ", ".join(action.args)
            entries.append("%s(%s)" % (action.name, ", ".join(action.args)))
        result = "(%s,)" % ", ".join(entries)
        return result
        
    def sendToRos(self):
        #result = self.computeResult()
        result = str(self.inferredCommandEdit.toPlainText())
	print "sending", result
        self.rosbridge.publish("/blocknlp/nl_output", "block_build_msgs/SLUCommand", 
                               {"command":result, "do_reset":True})
        
        #self.rosbridge.publish("/blocknlp/parser_output", "std_msgs/String", yaml.dump(esdcIo.toYaml(self.esdcs)))

def main():
    app = basewindow.makeApp()

    parser = OptionParser()
    parser.add_option("--model-filename",dest="model_fname", 
                      help="CRF Filename", metavar="FILE")
    (options, args) = parser.parse_args()


    wnd = MainWindow(options.model_fname)
    wnd.show()
    app.exec_()


if __name__=="__main__":
    main()


