import sys
from esdcs.context import Context
def _functionId(obj, framesUp):
    fr = sys._getframe(framesUp+1)
    co = fr.f_code
    return "%s:%s" % (obj.__class__, co.co_name)

def abstractMethod(obj=None):
    raise Exception("Unimplemented Method: %s" % _functionId(obj,1))

class State:
    AGENT_ID = -100
    """Defines a class that esdcSearch can function over.
       Contains information on a specific instationation of
       a robot's current state and information on the space
       of states that robot may occupy.
    """

    
    def to_context(self):
        objects = [self.getGroundableById(gid) for gid in self.getObjectsSet()] + [self.agent]
        places = [self.getGroundableById(gid) for gid in self.getPlacesSet()]
        return Context(objects, places)

    @property
    def agent(self):
        return self.groundableDict[self.AGENT_ID]


    def getSuccessors(self):
        """Returns a list of (State, Action) pairs where states
           are the reachable set of states from the current state
           and actions are the actions required to transform the current
           state into the posterior state.
        """
        abstractMethod(self)

    def getObjectsSet(self):
        """Returns a list of object ids specific to the State object.
           These ids should be the refer to the set of PhysicalObjects
           appropriate for grounding to OBJECT ESDCs.  Additionally
           these ids should be consistent over the state space
           (i.e. should be consistent for any States generated through
           getSuccessors.)
        """
        abstractMethod(self)

    def getPlacesSet(self):
        """Returns a list of place ids specific to the State object.
           These ids should refer to the set of Places appropriate for
           grounding to PLACE ESDCs. Additionally these ids should be
           consistent over the state space (i.e. should be consistent
           for any States generated through getSuccessors.)
        """
        abstractMethod(self)

    def getGroundableById(self, id):
        """Return the grounding (as defined in groundings.py) referred
           to by ID.
        """
        abstractMethod(self)

    def getAgentId(self):
        """Return the ID refering to the agent"""
        abstractMethod(self)

    def getSequence(self):
        """Return list of actions that is the history of actions executed
           by the agent up till this state"""
        abstractMethod(self)
        
    """ 
    The rest of the methods are in order to help with the visualisations.
    They replace most BrowserTools functionality
    """
    
    def manipulatedObjectsIds(self):
        """ Returns the list of object IDs that the robot 
        is currently manipulating """
        abstractMethod(self)
        
    def topologicalMapNodes(self):
        """ Returns a dictionary of topological nodes to toplogical locations"""
        abstractMethod(self)             
        

class Action:
    def execute(self, in_state, tstep=1):
        """Return a state that is the results of executing action
           self on in_state.
        """
        abstractMethod(self)

    def __str__(self):
        return "%s(%s)" % (self.name, ", ".join([str(s) for s in self.args]))

def state_type_from_name(name):

    if name == "forklift":
        from forklift.forkState import ForkState
        return ForkState
    elif name=="d8":
        from nlu_navigation.navState import NavState
        return NavState
    elif name=="pr2":
        from pr2.pr2_state import Pr2State
        return Pr2State
    elif name=="ikea":
        from ikea.ikea_state import IkeaState
        return IkeaState
    elif name=="ikea_human":
        from ikea.ikea_human_state import IkeaHumanState
        return IkeaHumanState
    elif name == "gis":
        from nlu_navigation.navState import GisState
        return GisState
    elif name == "kitchen":
        from kitchen.kitchenState import KitchenState
        return KitchenState
    else:
        raise ValueError("Not a valid state type: " + `name`)
