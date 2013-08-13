import rosbridge
from esdcs.esdcIo import annotationIo
import time
import base64
import uuid

# get a UUID - URL safe, Base64
def make_uid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return str(r_uuid.replace('=', ''))


class SluEvaluator:
  """
  Loads in a list of annotation files and for each annotation sets up the
  initial block configuration, executes the corresponding natural language
  command, and resets the blocks in the toolbox
  """

  def sendBuildManagerCommand(self, command, reset=True):
    uid = make_uid()
    print "publishing", uid, command
    self.rosbridge.publish("/blocknlp/nl_output", "block_build_msgs/SLUCommand", {"command":command,
                                                                                  "id":uid,
                                                                                  "reset":reset})
    
    self.waitForBuildManagerResponse(uid, command)

  def waitForBuildManagerResponse(self, guid, desc=""):
    print "waiting for build manager response for", guid, desc
    while self.build_manager_response == None:
      self.rosbridge.check()
      self.waitCallback()
      time.sleep(0.1)
    print "received build manager response '%s'" % self.build_manager_response, "for guid", guid
    if guid != None and self.build_manager_response != guid:
      raise ValueError("Guid not equal")

    self.build_manager_response = None



  def waitForPr2CommanderResponse(self):
    while self.pr2_commander_response == None:
      self.rosbridge.check()
      self.waitCallback()
      time.sleep(0.1)
    self.pr2_commander_response = None




  def __init__(self, fnames):
    self.fnames = list(fnames)
    self.toolboxBlocks = {}
    self.corpus = annotationIo.load_all(fnames)
    print "doing", len(self.corpus), "annotations"
    self.annotations = self.corpus.annotations
    self.status = ""
    self.command = ""
    self.waitCallback = lambda: True
    self.build_manager_response = None
    self.pr2_commander_response = None
    self.rosbridge = rosbridge.Rosbridge("pr2mm1.csail.mit.edu",9091)
    print "subscribing"
    self.rosbridge.subscribe("/mit/object_list_all", "object_manager/ObjectList", self.processObjectListResponse)
    self.rosbridge.subscribe("/blocknlp/slu_command_parser_status", "std_msgs/String", self.SLUCommandParserStatusCallback)
    self.rosbridge.subscribe("/blocknlp/pr2_commander_status", "std_msgs/String", self.pr2CommanderExceptionCallback)

  def setStatus(self, status):
    self.status = status
    self.rosbridge.publish("/blocknlp/slu_evaluator_status", "std_msgs/String", {"data":status})
    print "Status:", status

  # Outputs an natural language command to SLU (via pr2CommanderGui.py) for processing
  def sendNlCommand(self,nl_command):
    self.setStatus("Following natural language command: %s." % nl_command)
    self.inProcess = True
    self.rosbridge.publish("/blocknlp/nl_input", "std_msgs/String", {"data":nl_command})
    #self.waitForPr2CommanderResponse()
    self.waitForBuildManagerResponse(guid=None, desc="sendNlCommand")
    
  # Tells block_builder (BuildManager.py) to reset all blocks in the active area back to their toolbox locations
  def resetToolbox(self):
    self.setStatus("Resetting.")
    self.inProcess = True
    self.sendBuildManagerCommand("resetToolbox()")
    self.initialize_robot()
    self.setStatus("")

  # Sends a pick and place command to block_builder (BuildManager.py)
  def pick_place(self,id,x,y):
    self.inProcess = True
    print "Moving block " + str(id) + " to location " + str((x,y))
    command = "(pickup(" + str(id) + "), putdown(0,[" + str(x) + "," + str(y) +"]),)"

    self.sendBuildManagerCommand(command, reset=False)

  # Tells block_builder (BuildManager.py) to reset the robot's pose back to its original position
  def initialize_robot(self):
    print "Returning to initial robot configuration"
    self.inProcess = True
    self.sendBuildManagerCommand("initializeRobot()")

  # Spin method that waits for block_builder (BuildManager.py) to finish executing a command before proceeding
  def waitForResponse(self):
    while(self.inProcess):
      self.rosbridge.check()
      self.waitCallback()
      time.sleep(0.1)

  
  # Receives a message from block_builder (BuildManager.py) whenever block_builder finishs executing an SLUCommand
  def SLUCommandParserStatusCallback(self, msg):
    self.inProcess = False
    self.build_manager_response = msg["data"]

  # Handles an exception from pr2CommanderGui.py if the evaluation of a NL command fails in the commandReceived function
  def pr2CommanderExceptionCallback(self, msg):
    self.pr2_commander_response = eval(msg["data"])
    if not self.pr2_commander_response["is_successful"]:
      print "ERROR: Could not process nl_input command in pr2_commander:\n"
      print self.pr2_commander_response["status"]
    else:
      print "pr2_commander processed nl_input"
                       
    self.inProcess = False

  # Spin method that waits for object_manager (ObjectManager.cpp) to publish an ObjectList
  def waitForObjectListToolbox(self):
    print "Waiting for Object List Message: "
    self.toolboxBlocks = {}
    while not self.toolboxBlocks:
      self.rosbridge.check()
      self.waitCallback()
      time.sleep(0.1)

  def setWaitCallback(self, callback):
    self.waitCallback = callback

  # Processes an ObjectList message as stores its contents as a dictionary of block colors
  def processObjectListResponse(self,obj_list):
      self.toolboxBlocks = {}
      for obj in obj_list["object_list"]:
        if obj["atHome"]:
          if(obj["label"] not in self.toolboxBlocks): self.toolboxBlocks[obj["label"]] = [obj["id"]]
          else: self.toolboxBlocks[obj["label"]].append(obj["id"])


  # Extracts the initial configuration of an context from a list of its objects
  def extractInitialConfiguration(self, objects):
    init_config = []
    for obj in objects:
      if "block" in obj.tags:
        x_start = obj.path.points_xyztheta[0][0]
        y_start = obj.path.points_xyztheta[1][0]
        color = [s for s in obj.tags if s in ['red','orange','yellow','green','blue','purple']][0]
        init_config.append([color,(x_start,y_start)])
    return init_config

  # Sets up the initial configuration of a context from a list of its objects
  def setupInitialConfiguration(self, objects):
    self.setStatus("Setting up initial block configuration.")
    print "Setting up initial block configuration: ", self.extractInitialConfiguration(objects)
    self.waitForObjectListToolbox()
    print "Blocks in Toolbox: ", self.toolboxBlocks
    for block in self.extractInitialConfiguration(objects):
      color = block[0]
      if color in self.toolboxBlocks:
        id = self.toolboxBlocks[color].pop()
        if not self.toolboxBlocks[color]: del self.toolboxBlocks[color]
        x = block[1][0]
        y = block[1][1]
        self.pick_place(id,x,y)
      else:
        print "ERROR: Could not locate " + color + " block in toolbox"
        print "Aborting Initial Block Configuration"
        return False
    print "Finished Setting up block configuration"
    self.initialize_robot()
    return True
  def playback_annotation(self, annotation):
    nl_command = annotation.entireText
    context_objects = annotation.context.objects
    self.command = nl_command
    print "Natural Language Command: ", nl_command
    if self.setupInitialConfiguration(context_objects):
      self.sendNlCommand(nl_command)
    self.resetToolbox()

  # Loads all annotations one by one and attempts to execute the corresponding natural language command
  def playback_all(self):
    #for i in range(len(self.annotations)):
    #for i in [0,5]:
    for i, annotation in enumerate(self.annotations):
      print "=========================================================="
      print "Annotation ", i
      self.playback_annotation(annotation)
      break
    print "=========================================================="
    print("done with test")

def main():
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--corpus-filename",dest="corpus_filenames", 
                    help="Corpus  Filename", metavar="FILE", action="append")
  (options, args) = parser.parse_args()
  
  yp = SluEvaluator(options.corpus_filenames)
  yp.playback_all()

if __name__ == '__main__':
  main()
