import sys
import rosbridge
import traceback
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, QSocketNotifier

class PushToTalkGui(QtGui.QWidget):
    
    def __init__(self):
        super(PushToTalkGui, self).__init__()
        self.connect2rosbridge()
        self.initUI()
        self.mode = "Command"
        self.inProcess = False
        print "--------------------"
        print "Command Mode\n"

    def initUI(self):
        self.p2tButton = QtGui.QPushButton("Push To Talk")
        self.p2tButton.setMinimumSize(400,100)
        self.cButton = QtGui.QPushButton("Command")
        self.cButton.setMinimumSize(200,50)
        self.cButton.setEnabled(False) # Start off gui in command mode
        self.wlButton = QtGui.QPushButton("Word Learning")
        self.wlButton.setMinimumSize(200,50)

        largeFont = QtGui.QFont()
        largeFont.setPixelSize(30)
        self.p2tButton.setFont(largeFont)

        self.p2tButton.clicked.connect(self.p2tButtonCallback)            
        self.cButton.clicked.connect(self.changeState)
        self.wlButton.clicked.connect(self.changeState)

        upper_box = QtGui.QHBoxLayout()
        upper_box.addWidget(self.p2tButton)
        lower_box = QtGui.QHBoxLayout()
        lower_box.addWidget(self.cButton)
        lower_box.addWidget(self.wlButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(upper_box)
        vbox.addLayout(lower_box)
        
        self.setLayout(vbox)    
        
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Speech Recognition GUI')    
        self.show()

    def connect2rosbridge(self):
        try:
          #self.rosbridge = rosbridge.Rosbridge("localhost", 9091)
          self.rosbridge = rosbridge.Rosbridge("pr2mm1.csail.mit.edu",9091)
          
          self.rosbridge.subscribe("/blocknlp/slu_command_parser_status", "std_msgs/Empty", self.SLUCommandParserStatusCallback)
          self.rosbridge.subscribe("/blocknlp/pr2_commander_exception", "std_msgs/String", self.pr2CommanderExceptionCallback)
          self.socket = QSocketNotifier(self.rosbridge.fileno, QSocketNotifier.Read)
          self.connect(self.socket, SIGNAL("activated(int)"), self.checkSocket)
        except: 
          traceback.print_exc()
          
    def checkSocket(self):
        self.rosbridge.check()
  
    def p2tButtonCallback(self, pressed):
        # Listen for a single speech recognition message and relay the message to pr2_commander    
        if self.mode == 'Command':
            self.p2tButton.setEnabled(False)
            self.p2tButton.setText("Waiting for Robot...")
            print "Listening for speech and executing..."

            # Make the robot look up, listen to a command, and attempt to execute the command (controlled by head_manager and BuildManager)
            self.inProcess = True
            self.rosbridge.publish("/speech/localization", "geometry_msgs/Point", {"x":1,"y":0,"z":1.2})

        # Send start and stop messages to speech recognition software
        elif self.mode == "Word Learning":
            if pressed: self.rosbridge.publish("/speech/change_mode", "std_msgs/String", {"data": "Start"})
            else: self.rosbridge.publish("/speech/change_mode", "std_msgs/String", {"data": "Stop"})

    # Receives a message from block_builder (BuildManager.py) whenever block_builder finishs executing an SLUCommand
    def SLUCommandParserStatusCallback(self, msg):
        if self.inProcess:
            print "Command execution complete\n"
            self.p2tButton.setEnabled(True)
            self.p2tButton.setText("Push To Talk")
            print "Ready for next message"

    # Handles an exception from pr2CommanderGui.py if the evaluation of a NL command fails in the commandReceived function
    def pr2CommanderExceptionCallback(self, msg):
        if self.inProcess:
            print "ERROR: Could not process nl_input command in pr2_commander:\n"
            print msg["data"]
            self.p2tButton.setEnabled(True)
            self.p2tButton.setText("Push To Talk")
            print "\nReady for next message"

    def changeState(self):
        source = self.sender()
        if source.text() == "Command":
            print "--------------------"
            print "Command Mode\n"
            self.mode = "Command"
            self.rosbridge.publish("/speech/change_mode", "std_msgs/String", {"data": "Command"})
            self.cButton.setEnabled(False)
            self.wlButton.setEnabled(True)
            self.p2tButton.setCheckable(False)
            self.p2tButton.setText("Push To Talk")
            
        elif source.text() == "Word Learning":
            print "--------------------"
            print "Word Learning Mode\n"
            self.mode = "Word Learning"
            self.rosbridge.publish("/speech/change_mode", "std_msgs/String", {"data": "Word Learning"})
            self.cButton.setEnabled(True)
            self.wlButton.setEnabled(False)
            self.rosbridge.publish("/mit/head_command", "std_msgs/String", {"data": "lookAt(1,0,1.2)"})
            self.p2tButton.setCheckable(True)
            self.p2tButton.setEnabled(True)
            self.p2tButton.setText("Push To Talk")
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    g = PushToTalkGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
