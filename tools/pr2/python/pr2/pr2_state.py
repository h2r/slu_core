from g3.state import State, Action
import spatial_features_cxx as sfe

from esdcs.groundings import PhysicalObject, Prism, Path, Place, find_closest_object
from esdcs.context import Context
from numpy import arange
from numpy import transpose as tp
import numpy as na

def compute_places(table, body):
    """
    Compute places on the table, within reach of the robot.  The
    body_min and body_max are assuming the robot is at roughly zero
    zero.  We're ignoring the body centroid for now, but maybe we
    should check that it's zero...?
    """
    X, Y = table.points_xy
    table_xmin = min(X)
    table_xmax = max(X)
    table_ymin = min(Y)
    table_ymax = max(Y)

    body_x, body_y = body.centroid2d

    # red block start.
    # x: 0.638734,  y: 0.030862
    # red block end.
    # x: 0.7,  y: 0.03
    # x: 0.5,  y: 0.03
    # x: 0.4,  y: 0.03


    # x: 0.5,  y: 0.1
    # x: 0.5,  y: 0.3
    # x: 0.5,  y: -0.1 
    # x: 0.5,  y: -0.2
    # -0.3 and higher - kinect calibration

    # corners (left/right relative to pr2, back is close to pr2)
    # corners are more conservative than the initial numbers, but
    # I tested pickup and put down for all.
    # x: 0.7, y: -0.2 (front right)
    # x: 0.4, y: -0.2 (back right)
    # x: 0.7, y:  0.0 (front left)
    # x: 0.4, y:  0.0 (back left)

    #print "body", body_x, body_y
    body_xmin = 0.4
    body_xmax = 0.7
    body_ymin = -0.2
    body_ymax = 0.0

    #print "table min", table_xmin, table_ymin
    #print "table max", table_xmax, table_ymax

    xmin = max(body_xmin, table_xmin)
    xmax = min(body_xmax, table_xmax)
    ymin = max(body_ymin, table_ymin)
    ymax = min(body_ymax, table_ymax)


    size = max([xmax - xmin, ymax - ymin]) / 3
    places = []
    #        for x in [0.3, 0.5, 0.7]: # arange(-0.5, 1.5, 0.5):
    #            for y in arange(-0.35, 0.101, 0.1):

    pr = 0.03
    for x in arange(xmin, xmax + 0.01, size):
        for y in arange(ymin, ymax + 0.01, size):
            place = Place(Prism.from_points_xy(tp([(x - pr, y - pr), (x + pr, y - pr),
                                    (x + pr, y + pr), (x - pr, y + pr)]),
                                table.prism.zEnd, table.prism.zEnd + 0.1))
            if sfe.math2d_is_interior_point(place.centroid2d, table.prism.points_xy):
                places.append(place)

    return places




def enum(**enums):
    return type('Enum', (), enums)

Colors = enum(RED=1, GREEN=2, BLUE=3)

class EndEffector:
     """
     Represents the end effector for the robot, as well as an object
     it is holding.
     """
     @staticmethod
     def copy(ee):
          return EndEffector(ee.home_xyztheta, ee.pobj, ee.held_pobj)
     
     def __init__(self, home_xyztheta, pobj, held_pobj=None):
         assert isinstance(pobj, PhysicalObject)
         self.home_xyztheta = na.array(home_xyztheta)
         self.pobj = pobj
         self.held_pobj = held_pobj

     @property
     def id(self):
          return self.pobj.id

     @property
     def tags(self):
          return self.pobj.tags

     
          
     @property
     def has_object(self):
          return self.held_pobj != None

class Pr2State(State):
     @staticmethod
     def from_pobj(body, rightee, leftee, table, blocks, places):
          """
          Construct, passing in everything as physical objects
          """
          
          return Pr2State(body, [EndEffector(rightee.centroid3d + (0,), rightee), 
                                 EndEffector(leftee.centroid3d + (0,), leftee)], 
                          table, blocks, places)

     def __init__(self, body, effectors, table, blocks, places):
          self.body = body
          self.effectors = effectors
          assert len(self.effectors) == 2
          self.rightee = [e for e in self.effectors if 'right' in e.tags][0]
          self.leftee = [e for e in self.effectors if 'left' in e.tags][0]
          
          self.blocks = list(blocks)
          if len(self.blocks) == 0:
              print "warning: no blocks."
          self.table = table
          self.places = places


          self.groundings = list()
          self.groundings.append(self.body)
          self.groundings.append(self.table)
          self.groundings.append(self.rightee.pobj)
          self.groundings.append(self.leftee.pobj)
          self.groundings.extend(self.places)
          self.groundings.extend(self.blocks)
          
          self.groundableDict = dict((g.id, g) for g in self.groundings)
          assert self.AGENT_ID in self.groundableDict
          assert len(self.groundings) == len(self.groundableDict), "duplicate ids"
          self.orientation = self.agent.path.locationAtT(0)[-1]
          self.used_noop = False
          self.is_initial_state = True


     def to_context(self):
         return Context.from_groundings(self.groundings)
          
     @staticmethod
     def copy(state):
          state = Pr2State(state.body, 
                           [EndEffector.copy(e) for e in state.effectors],
                           state.table, state.blocks, state.places)

          return state

     @staticmethod
     def from_context(context):
          """
          Creates a state initialized with the objects and agent in
          the context class.
          """
          body = [o for o in context.objects if 'base' in o.tags][0]
          rightee = [o for o in context.objects if 'right' in o.tags][0]
          leftee = [o for o in context.objects if 'left' in o.tags][0]
          table = [o for o in context.objects if 'table' in o.tags][0]
          blocks = [o for o in context.objects if 'block' in o.tags]

          places = compute_places(table, body)

          return Pr2State.from_pobj(body, rightee, leftee, table, blocks, 
                                    places)

     @staticmethod
     def init_state_blocks_on_table():
          """
          Creates an initial default state with blocks on the table
          """

          rightee = PhysicalObject(Prism.from_points_xy(tp([(1, 1.1), (0.9, 1.1), 
                                             (0.9, 1.2), (1, 1.2)]),
                                         1, 1.3),
                                   tags=("robot", "right", "hand"), 
                                   lcmId=Pr2State.AGENT_ID)


          leftee = PhysicalObject(Prism.from_points_xy(tp([(0, 1.1), (-0.1, 1.1), 
                                            (-0.1, 1.2), (0, 1.2)]),
                                        1, 1.3),
                                  tags=("robot", "left", "hand"), 
                                  lcmId=Pr2State.AGENT_ID + 1)
          body = PhysicalObject(Prism.from_points_xy(tp([(0, 0), (1, 0), (1, 1), (0, 1)]),
                                      0, 2),
                                tags=("robot", "body"), 
                                  lcmId=Pr2State.AGENT_ID + 2)
          
          table = PhysicalObject(Prism.from_points_xy(tp([(-1, 1.1), (2, 1.1), (2, 3),
                                           (-1, 3)]),
                                       1, 1.25), tags=("table",), lcmId=3)

          blocks = [PhysicalObject(Prism.from_points_xy(tp([(0.5, 1.5), (0.75, 1.5), 
                                             (0.75, 1.75), (0.5, 1.75)]),
                                         1.25, 1.3), tags=("red","block"), 
                                   lcmId=4), 
                    PhysicalObject(Prism.from_points_xy(tp([(1, 2), (1.25, 2), 
                                             (1.25, 2.25), (1, 2.25)]),
                                         1.25, 1.3), tags=("blue","block"), 
                                   lcmId=5)]
          
          places = compute_places(table, body)

          initial_state = Pr2State.from_pobj(body, rightee, leftee, table,
                                             blocks, places)

          
          return initial_state


     @staticmethod
     def init_state_block_in_hand():
          """
          Creates an initial default state with a block in the hand.
          """

          state = Pr2State.init_state_blocks_on_table()
          for s, a, mg in state.getSuccessors():
              if isinstance(a, PickUp):
                  pobjs = []
                  new_rightee_pobj = None
                  new_leftee_pobj = None
                  if s.rightee.held_pobj != None:
                      new_rightee_pobj = s.rightee.held_pobj.withoutHistory()
                      pobjs.append(new_rightee_pobj)
                  if s.leftee.held_pobj != None:
                      new_leftee_pobj = s.leftee.held_pobj.withoutHistory()
                      pobjs.append(new_leftee_pobj)
                  new_blocks = [b for b in s.blocks if not b.id in [p.id for p in pobjs]]
                  new_blocks.extend(pobjs)
                  return Pr2State(s.body, [EndEffector(s.rightee.home_xyztheta, s.rightee.pobj.withoutHistory(),
                                                       new_rightee_pobj),
                                           EndEffector(s.leftee.home_xyztheta, s.leftee.pobj.withoutHistory(),
                                                       new_leftee_pobj),],
                                  s.table.withoutPath(),
                                  new_blocks, s.places)
          raise ValueError("No pickup action.")
     @staticmethod
     def init_state():
         return Pr2State.init_state_block_in_hand()
         #return Pr2State.init_state_blocks_on_table()


     @property
     def active_ids(self):
         return (#[e.held_pobj.id for e in self.effectors if e.has_object] + 
                 [self.leftee.pobj.id, self.rightee.pobj.id])
     

     def is_object_id_held(self, pobj_id):
         return pobj_id in self.active_ids

     def is_object_held(self, pobj):
         return self.is_object_id_held(pobj.id)

     @property
     def place_ids(self):
         return [p.id for p in self.places]
          
     @property
     def end_effectors(self):
          return [self.leftee, self.rightee]




     @property
     def topological_locations(self):
          return []


     def getAgentId(self):
          return State.AGENT_ID



     def getPosition(self):
          return (0, 0)

     @property
     def objects(self):
          return [self.getGroundableById(oid) for oid in self.getObjectsSet()]

     @property
     def places(self):
          return [self.getGroundableById(pid) for pid in self.getPlacesSet()]

     def getObjectsSet(self):
          return [g.id for g in self.groundings if isinstance(g, PhysicalObject)]

     def getPlacesSet(self):
          return self.place_ids
     

     def getGroundableById(self, gid):
          return self.groundableDict[gid]

     def getSuccessors(self, groundings=[]):
          states = []
          
          s = Pr2State.copy(self)
          states.append((s, None, [s.agent]))

          # manipulations
          for ee in [self.rightee]: #self.end_effectors:
               if ee.has_object:
                    for place_id in sorted(self.getPlacesSet()):
                        place = self.getGroundableById(place_id)
                        manipulable_objects = [o for o in self.objects 
                                               if not self.is_object_held(o) 
                                               and "block" in o.tags]
                        closest_object = find_closest_object(manipulable_objects, place.centroid2d)
                        
                        if (closest_object != None and
                            sfe.math2d_dist(closest_object.centroid2d,
                                            place.centroid2d) > 0.05):
                            a = PutDown(ee, place)
                            s, mg = a.execute(self)                
                            states.append((s, a, mg))
		    # Add Drop Action to List of Successor States
		    # a = Drop(ee)
		    # s, mg = a.execute(self)
		    # states.append((s, a, mg))
               else:
                    for block in sorted(self.blocks):
                         if not self.is_object_held(block):
                              a = PickUp(ee, block)
                              s, mg = a.execute(self)
                              states.append((s, a, mg))

          if not hasattr(self, "is_initial_state") or self.is_initial_state:
              noop_action = Noop()
              new_state, mg = noop_action.execute(self)
              states.append((new_state, noop_action, mg))
          return states


class PickUp(Action):
     def __init__(self, end_effector, block):
          self.end_effector = end_effector
          self.block = block
          self.name = "pickup"
          self.args = [str(self.block.id)]

          
     def execute(self, in_state):

          new_blocks = [b for b in in_state.blocks if b.id != self.block.id]
          assert len(new_blocks) == len(in_state.blocks) - 1

          start_t = max(self.block.path.end_t, self.end_effector.pobj.path.end_t) + 1

          new_t1 = start_t + Path.ONE_SECOND_IN_MICROS
          new_t2 = start_t + 2 * Path.ONE_SECOND_IN_MICROS

          new_block = self.block.withExtendedPath(Path.from_xyztheta([start_t, new_t1, new_t2], tp([
                          self.block.path.locationAtT(-1) + 0.01,
                          self.block.path.locationAtT(-1) - 0.01,
                          self.end_effector.home_xyztheta])))
          new_blocks.append(new_block)


          new_effectors = [e for e in in_state.effectors if e.id != self.end_effector.id]
          assert len(new_effectors) == len(in_state.effectors) - 1
          new_effector_obj = self.end_effector.pobj.withExtendedPath(Path.from_xyztheta([new_t1, new_t2], 
                                                                          tp([self.block.path.locationAtT(-1),
                                                                              self.end_effector.home_xyztheta
                                                                              ])))
          new_effector = EndEffector(self.end_effector.home_xyztheta, new_effector_obj, new_block)



          new_effectors.append(new_effector)

          next_state = Pr2State(in_state.body, new_effectors, in_state.table, 
                                new_blocks, in_state.places)
          next_state.is_initial_state = False
          modified_groundings = [new_block, new_effector.pobj]
          return next_state, modified_groundings

     def __str__(self):
         return 'Pick up ' + str(self.block.id)

class Noop(Action):
    def __init__(self):
        self.name = "noop"
        self.args = []

    def execute(self, in_state):
          next_state = Pr2State.copy(in_state)
          next_state.used_noop = True
          next_state.is_initial_state = False
          return next_state, []
        

class PutDown(Action):
     def __init__(self, end_effector, place):
          self.end_effector = end_effector
          assert self.end_effector.has_object
          self.place = place
          self.name = "putdown"
          self.args = [str(self.end_effector.held_pobj.id), str(self.place.centroid2d)]

     def execute(self, in_state):
          

          
          new_blocks = [b for b in in_state.blocks if b.id != self.block.id]
          assert len(new_blocks) == len(in_state.blocks) - 1

          t0 = max(self.block.path.end_t, self.end_effector.pobj.path.end_t) + 1
          t1 =  t0 + Path.ONE_SECOND_IN_MICROS
          t2 = t1 + Path.ONE_SECOND_IN_MICROS
          #print "put down"
          #print self.block.path.locationAtT(-1)
          #print self.block.centroid3d
          #print "length", self.block.path.length_seconds
          #print "length", self.block.path.length_meters
          #print "place", self.place.centroid3d

          new_block = self.block.withExtendedPath(Path.from_xyztheta([t0, t1], 
                                               tp([
                          na.array(self.block.centroid3d + (0, )) + 0.01,
                          na.array(self.place.centroid3d + (0, )) + 0.01,
                          ])))
          new_blocks.append(new_block)
          

          new_effectors = [e for e in in_state.effectors if e.id != self.end_effector.id]
          assert len(new_effectors) == len(in_state.effectors) - 1

          new_effector_obj = self.end_effector.pobj.withExtendedPath(Path.from_xyztheta([t1, t2], 
                                                                          tp([self.place.centroid3d + (0, ),
                                                                              self.end_effector.home_xyztheta
                                                                              ])))
          
          #print "effector", new_effector_obj.centroid3d, new_effector_obj.path.toYaml()
          #print "block", self.block.centroid3d, self.block.path.toYaml()
          new_effector = EndEffector(self.end_effector.home_xyztheta, new_effector_obj)
          new_effectors.append(new_effector)


          next_state = Pr2State(in_state.body, new_effectors, in_state.table, new_blocks, in_state.places)
          next_state.is_initial_state = False
          modified_groundings = [new_effector.pobj, new_block]
          return next_state, modified_groundings
     
     @property
     def block(self):
         return self.end_effector.held_pobj

     def __str__(self):
          return ('Put Down ' + str(self.block.id) + ", " + 
                  str(self.place.centroid3d))

class Drop(Action):
     def __init__(self, end_effector):
          self.end_effector = end_effector
          assert self.end_effector.has_object
          self.name = "dropblock"
          self.args = ['']

     def execute(self, in_state):
          
          modified_groundings = [self.end_effector.pobj] #, self.end_effector.held_pobj]
          
          new_blocks = [b for b in in_state.blocks if b.id != self.block.id]
          assert len(new_blocks) == len(in_state.blocks) - 1
          new_t = self.block.path.end_t + Path.ONE_SECOND_IN_MICROS
	  new_block = self.block.withExtendedPath(Path.from_xyztheta([new_t],
tp([tuple(self.end_effector.pobj.centroid2d) + (1.275,0)])))
          new_blocks.append(new_block)

	  new_effectors = [e for e in in_state.effectors if e.id != self.end_effector.id]
          assert len(new_effectors) == len(in_state.effectors) - 1
          new_t1 = new_t + Path.ONE_SECOND_IN_MICROS
          new_effector_obj = self.end_effector.pobj.withExtendedPath(Path.from_xyztheta([new_t1], 
                                                                          tp([self.end_effector.home_xyztheta])))

	  new_effector = EndEffector(self.end_effector.home_xyztheta, new_effector_obj)
          new_effectors.append(new_effector)

          next_state = Pr2State(in_state.body, new_effectors, in_state.table, new_blocks, in_state.places)
          next_state.is_initial_state = False
          return next_state, modified_groundings
     
     @property
     def block(self):
         return self.end_effector.held_pobj

     def __str__(self):
          return ('Drop ' + str(self.block.id))

