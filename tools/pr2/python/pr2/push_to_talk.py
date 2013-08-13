from Tkinter import *
import tkFont
import rosbridge
import time
import traceback

class PushToTalkGui:
    inProcess = False
    
    def __init__(self, master):
        # Set up the gui
        frame = Frame(master)
        frame.pack()

        font = tkFont.Font(family="Helvetica",size=40)
        self.button = Button(frame, text="Push To Talk", bg="green", font=font,
                             padx=75, pady=50, activebackground="green",
                             command=self.buttonCallback)
        self.button.pack()

        # Connect to rosbridge
        try:
          #self.rosbridge = rosbridge.Rosbridge("localhost", 9091)
          self.rosbridge = rosbridge.Rosbridge("pr2mm1.csail.mit.edu",9091)
          self.rosbridge.subscribe("/blocknlp/slu_command_parser_status", "std_msgs/Empty", self.SLUCommandParserStatusCallback)
          self.rosbridge.subscribe("/blocknlp/pr2_commander_exception", "std_msgs/String", self.pr2CommanderExceptionCallback)

        except: 
          traceback.print_exc()

    # Listen for a single speech recognition message and relay the message to pr2_commander      
    def buttonCallback(self):
        self.button.config(bg="red")
        self.button.config(state=DISABLED)
        self.button.update_idletasks()
	print "Listening for speech and executing..."

        # Make the robot look up, listen to a command, and attempt to execute the command (controlled by head_manager and BuildManager)
        self.rosbridge.check()
        self.inProcess = True
        self.rosbridge.publish("/blocknlp/speech_localization", "geometry_msgs/Point", {"x":1,"y":0,"z":1.2})
        self.waitForResponse()
        
        self.button.config(bg="green",state=NORMAL)
	print "\nReady for next message"
    
    # Spin method that waits for block_builder (BuildManager.py) to finish executing a command before proceeding
    def waitForResponse(self):
        while(self.inProcess):
          self.rosbridge.check()
          time.sleep(0.1)

    # Receives a message from block_builder (BuildManager.py) whenever block_builder finishs executing an SLUCommand
    def SLUCommandParserStatusCallback(self, msg):
        if self.inProcess:
            self.inProcess = False
            print "Command execution complete"

    # Handles an exception from pr2CommanderGui.py if the evaluation of a NL command fails in the commandReceived function
    def pr2CommanderExceptionCallback(self, msg):
        if self.inProcess:
            print "ERROR: Could not process nl_input command in pr2_commander:\n"
            print msg["data"]
            self.inProcess = False

if __name__ == '__main__':
    root = Tk()
    root.wm_title("Speech Recognition GUI")
    p2t = PushToTalkGui(root)
    root.mainloop()
