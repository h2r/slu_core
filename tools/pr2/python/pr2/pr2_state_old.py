from g3.state import State, Action
import spatial_features_cxx as sfe

from esdcs.groundings import PhysicalObject, Prism, Path, Place
from esdcs.context import Context
from numpy import arange
from numpy import transpose as tp
import numpy as na

def find_closest_object(objects, point):
    sorted_objects = list(sorted(objects, key=lambda o: sfe.math2d_dist(o.centroid2d, point)))
    return sorted_objects[0]

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
               raise ValueError("No blocks")
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
          raise ValueError("Implement me.")

     @staticmethod
     def init_state():
          """
          Creates an initial default state.
          """

          rightee = PhysicalObject(Prism(tp([(1, 1.1), (0.9, 1.1), 
                                             (0.9, 1.2), (1, 1.2)]),
                                         1, 1.3),
                                   tags=("robot", "right", "hand"), 
                                   lcmId=Pr2State.AGENT_ID)


          leftee = PhysicalObject(Prism(tp([(0, 1.1), (-0.1, 1.1), 
                                            (-0.1, 1.2), (0, 1.2)]),
                                        1, 1.3),
                                  tags=("robot", "left", "hand"), 
                                  lcmId=Pr2State.AGENT_ID + 1)
          body = PhysicalObject(Prism(tp([(0, 0), (1, 0), (1, 1), (0, 1)]),
                                      0, 2),
                                tags=("robot", "body"), 
                                  lcmId=Pr2State.AGENT_ID + 2)
          
          table = PhysicalObject(Prism(tp([(-1, 1.1), (2, 1.1), (2, 3),
                                           (-1, 3)]),
                                       1, 1.25), tags=("table",), lcmId=3)

          blocks = [PhysicalObject(Prism(tp([(0.5, 1.5), (0.75, 1.5), 
                                             (0.75, 1.75), (0.5, 1.75)]),
                                         1.25, 1.3), tags=("red","block"), 
                                   lcmId=4), 
                    PhysicalObject(Prism(tp([(1, 2), (1.25, 2), 
                                             (1.25, 2.25), (1, 2.25)]),
                                         1.25, 1.3), tags=("blue","block"), 
                                   lcmId=5)]
          
          places = []
          for x in [0.5]: # arange(-0.5, 1.5, 0.5):
               for y in arange(-.35, 0.1, 0.2):
                    places.append(Place(Prism(tp([(x, y), (x + 0.25, y), 
                                                  (x + 0.25, y + 0.25), (x, y + 0.25)]),
                                              1.25, 1.5)))
                    
                                               


          initial_state = Pr2State.from_pobj(body, rightee, leftee, table,
                                             blocks, places)

          
          return initial_state
     @property
     def active_ids(self):
         return [e.held_pobj.id for e in self.effectors if e.has_object]

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

          print "\n\n\n******** get successors"
          # manipulations
          for ee in [self.rightee]: #self.end_effectors:
               if ee.has_object:
                    print "has object"
                    for place_id in sorted(self.getPlacesSet()):
                        place = self.getGroundableById(place_id)
                        closest_object = find_closest_object([o for o in self.objects if not self.is_object_held(o) and "block" in o.tags], place.centroid2d)
                        if sfe.math2d_dist(closest_object.centroid2d,
                                           place.centroid2d) > 0.1:
                            a = PutDown(ee, place)
                            s, mg = a.execute(self)                
                            states.append((s, a, mg))
               else:
                    print "picking up actions", self.blocks
                    for block in sorted(self.blocks):
                         if not self.is_object_held(block):
                              print "block", block
                              a = PickUp(ee, block)
                              s, mg = a.execute(self)
                              states.append((s, a, mg))
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


          new_t1 = self.block.path.end_t + Path.ONE_SECOND_IN_MICROS




          new_t2 = new_t1 + Path.ONE_SECOND_IN_MICROS
          new_block = self.block.withExtendedPath(Path([new_t1, new_t2], tp([
                          self.block.path.locationAtT(-1),
                          self.end_effector.home_xyztheta])))
          new_blocks.append(new_block)


          new_effectors = [e for e in in_state.effectors if e.id != self.end_effector.id]
          assert len(new_effectors) == len(in_state.effectors) - 1
          new_effector_obj = self.end_effector.pobj.withExtendedPath(Path([new_t1, new_t2], 
                                                                          tp([self.block.centroid3d + (0,),
                                                                              self.end_effector.home_xyztheta])))
          new_effector = EndEffector(self.end_effector.home_xyztheta, new_effector_obj, new_block)



          new_effectors.append(new_effector)

          next_state = Pr2State(in_state.body, new_effectors, in_state.table, 
                                new_blocks, in_state.places)
          modified_groundings = [new_block, new_effector.pobj]
          return next_state, modified_groundings

     def __str__(self):
         return 'Pick up ' + str(self.block.id)

class PutDown(Action):
     def __init__(self, end_effector, place):
          self.end_effector = end_effector
          assert self.end_effector.has_object
          self.place = place
          self.name = "putdown"
          self.args = [str(self.end_effector.held_pobj.id), str(self.place.centroid2d)]

     def execute(self, in_state):
          
          modified_groundings = [self.end_effector.pobj] #, self.end_effector.held_pobj]
          
          new_blocks = [b for b in in_state.blocks if b.id != self.block.id]
          assert len(new_blocks) == len(in_state.blocks) - 1
          new_t = self.block.path.end_t + Path.ONE_SECOND_IN_MICROS
          new_block = self.block.withExtendedPath(Path([new_t], 
tp([self.place.centroid3d + (0, )])))
          new_blocks.append(new_block)
          

          new_effectors = [e for e in in_state.effectors if e.id != self.end_effector.id]
          assert len(new_effectors) == len(in_state.effectors) - 1
          new_effector_obj = self.end_effector.pobj.withExtendedPath(Path([new_t], 
                                                                          tp([self.place.centroid3d + (0, )])))
          
          new_t1 = new_t + Path.ONE_SECOND_IN_MICROS
          new_effector_obj = self.end_effector.pobj.withExtendedPath(Path([new_t1], 
                                                                          tp([self.end_effector.home_xyztheta])))

          new_effector = EndEffector(self.end_effector.home_xyztheta, new_effector_obj)
          new_effectors.append(new_effector)


          next_state = Pr2State(in_state.body, new_effectors, in_state.table, new_blocks, in_state.places)
          
          return next_state, modified_groundings
     
     @property
     def block(self):
         return self.end_effector.held_pobj

     def __str__(self):
          return ('Put Down ' + str(self.block.id) + ", " + 
                  str(self.place.centroid3d))

