from g3.state import State, Action
from actionMap import ActionMap, tmapFromObjects, tmapFromObjectsAndPlaces
from spatial_features.groundings import PhysicalObject, Prism, Place, Path
from esdcs.context import Context
from numpy import transpose, arctan2, zeros, ones, arange
import spatial_features_cxx as sf
from assert_utils import array_equal




def prism_from_point(x,y,z1,z2):
     return Prism.from_points_xy([(x-1, x+1, x+1, x-1), (y-1, y-1, y+1, y+1)], z1, z2)

class ForkState(State):
     @staticmethod
     def copy(other_state):
          state = ForkState()
          state.currentNode = other_state.currentNode
          state.orientation = other_state.orientation
          state.pallet_ids = list(other_state.pallet_ids)
          state.object_ids = list(other_state.object_ids)
          state.place_ids = list(other_state.place_ids)
          state.has_pallet = other_state.has_pallet
          state.action_sequence = list(other_state.action_sequence)
          
          state.has_pallet_id = other_state.has_pallet_id
          
          # needs to be deep copied to preserve immutability
          state.groundableDict = dict(other_state.groundableDict)
          
          # should be immutable on its own
          state.actionMap = other_state.actionMap
          state.useRrt = other_state.useRrt

          return state

     def __init__(self, all_active_ids=False):
          self.all_active_ids = all_active_ids
          self.reset()
          
     @property
     def active_ids(self):
          if self.all_active_ids:
               return self.object_ids
          else:
               if self.has_pallet_id == None:
                    return []
               else:
                    return [self.has_pallet_id]
     @staticmethod
     def from_lcm(agent, orientation, pallets, has_pallet, objects, actionMap):
        from load_from_lcm import getLabel, physicalObject
        new_state = ForkState()
        new_state.currentNode = agent
        new_state.orientation = orientation
        new_state.pallet_ids = [p.id for p in pallets]
        new_state.object_ids = [o.id for o in objects if not 'wheel' in getLabel(o)]
        if has_pallet:
            new_state.has_pallet_id = has_pallet.id
        else:
             new_state.has_pallet_id = None

        new_state.actionMap = actionMap

        for obj in pallets+objects:
            new_state.groundableDict[obj.id] = physicalObject(obj)
 
        obj_places = [new_state.getGroundableById(oid).centroid3d for oid in new_state.object_ids]
        loc_places = [(l[0], l[1], 0) for l in new_state.actionMap.list_locations()]

        id_counter = max([0]+new_state.getObjectsSet()) + 1
        new_state.place_ids = []
        for x,y,z in obj_places+loc_places:            
            new_state.place_ids.append(id_counter)
            new_state.groundableDict[id_counter] = Place(prism_from_point(x,y,
                                                                          z+.2, 
                                                                          z+.5))
            id_counter += 1

        ax, ay = new_state.getPosition()
        new_state.groundableDict[State.AGENT_ID] = \
            PhysicalObject(prism_from_point(ax, ay, 0, 1),
                           path=Path.from_xyztheta([1], [[ax],[ay],[0],[new_state.orientation]]),
                           lcmId = State.AGENT_ID, tags=['forklift'])

        #Legacy fields, should not be used other than in repr
        new_state.has_pallet = has_pallet
       
        return new_state

     @staticmethod
     def from_context(context, moves_to_places=False, all_active_ids=False):
          """
          Creates a state initialized with the objects and agent in
          the context class.
          """
          context = context.withoutPaths()

          new_state = ForkState(all_active_ids=all_active_ids)
          
          new_state.orientation = context.agent.path.locationAtT(0)[-1]


          pallets = [o for o in context.objects if "pallet" in o.tags]
          objects = [o for o in context.objects if not "pallet" in o.tags]
          
          new_state.pallet_ids = [p.id for p in pallets]
          new_state.object_ids = [o.id for o in objects]

          if moves_to_places:
               tmap, tmap_locs = tmapFromObjects(loc_xy=None, objects=context.places)
          else:
               #tmap, tmap_locs = tmapFromObjects(loc_xy=None, objects=context.objects)
               tmap, tmap_locs = tmapFromObjectsAndPlaces(loc_xy=None, objects=context.objects, 
                                                          places=context.places)
          new_state.actionMap = ActionMap(tmap=tmap, tmap_locs=tmap_locs)          
          new_state.currentNode = new_state.actionMap.nearest_index(context.agent.centroid2d)

          new_state.groundableDict = {}          
          for obj in context.groundings:
               new_state.groundableDict[obj.id] = obj
          
          new_state.place_ids = [p.id for p in context.places]
          new_state.groundableDict[State.AGENT_ID] = context.agent



          held_pallets = [o for o in pallets
                          if (o != new_state.agent and
                              sf.math3d_intersect_prisms(o.prismAtT(0), 
                                                         new_state.agent.prismAtT(0)))]
          if len(held_pallets) == 0:
               new_state.has_pallet_id = None
               new_state.has_pallet = False
          elif len(held_pallets) == 1:
               new_state.has_pallet_id = held_pallets[0].id
               new_state.has_pallet = True
          else:
               raise ValueError("more than one held pallet.")
          
          
          return new_state


     @staticmethod
     def init_state():
          """
          Creates a state from the Waverly parking lot.  An initial
          state for debugging.
          """
          from load_from_lcm import waverly_state_truck
          state, am = waverly_state_truck()
          import yaml
          yaml.dump(state.toContext().toYaml(), open("waverly_state_truck.yaml", "w"))
          return state


     def reset(self):
          self.currentNode = 0
          self.orientation = 0
          self.pallet_ids = []
          self.has_pallet_id = None
          self.object_ids = []
          self.actionMap = None
          self.action_sequence = []
          self.groundableDict = dict()
          self.useRrt = False

     @property
     def topological_locations(self):
          '''Returns the coordinates of the locations of the topological
          nodes for this state's topological map.'''
          locations = []
          for i in self.actionMap.list_indicies():
               for n in self.actionMap.neighbors_by_index(i):
                    xy1 = self.actionMap.index_to_location(i)
                    locations.append(xy1)
          return locations


     def getAgentId(self):
          return State.AGENT_ID



     def getPosition(self):
          return self.actionMap.index_to_location(self.currentNode)


     def get_label(self, obj):
          from arlcm.pallet_t import pallet_t as p_t
          from arlcm.object_t import object_t as o_t
          if isinstance(obj, p_t) :
               return ForkState.pallet_types[obj.label]
          if isinstance(obj, o_t):
               return ForkState.object_types[obj.object_type.value]
          return None

     @property
     def objects(self):
          return [self.getGroundableById(oid) for oid in self.getObjectsSet()]

     @property
     def places(self):
          return [self.getGroundableById(pid) for pid in self.getPlacesSet()]

     def getObjectsSet(self):
          return self.pallet_ids + self.object_ids

     def getPlacesSet(self):
          return self.place_ids

     def toContext(self):
          return Context.from_groundings(self.groundableDict.values())
     
     @property
     def held_pallet(self):
         if self.has_pallet_id:
              return self.getGroundableById(self.has_pallet_id)
         else:
              return None

     def getGroundableById(self, gid):
          return self.groundableDict[gid]

     def getSuccessors(self, groundings=[]):
          states = []
          
          obstacles_2d = [self.getGroundableById(obj).prismAtT(-1) for obj in self.getObjectsSet()]
          # null action
          a = None
          s = ForkState.copy(self)
          s.action_sequence.append((self, None))
          states.append((s, a, [s.agent]))
          # motions
          here = self.actionMap.index_to_location(self.currentNode)
          for loc in self.actionMap.neighbors_by_index(self.currentNode):

               x,y = self.actionMap.index_to_location(loc)
               if not array_equal((x, y), here):
                    if not any(sf.math2d_is_interior_point((x, y), o.points_xy)
                               for o in obstacles_2d):
                         a = Move(here, (x,y))
                         s, mg = a.execute(self)
                         states.append((s, a, mg))

          # manipulations
          if self.has_pallet_id:
               places = sorted(self.getPlacesSet())
               for p in places:
                    x,y,z = self.getGroundableById(p).prismAtT(-1).centroid3d()
                    a = PutDown((x,y,z+1), self.has_pallet_id)
                    s, mg = a.execute(self)                
                    states.append((s, a, mg))
          else:
               for pid in sorted(self.pallet_ids):
                    # check if pallet has grounding
                    #if not pid in [g.id for g in groundings]:
                    #     continue
                    a = PickUp(pid)
                    s, mg = a.execute(self)
                    states.append((s, a, mg))         
          return states

     def getSequence(self):
          return self.action_sequence

class Move(Action):

    def __init__(self, from_location, to_location):
        self.from_location = from_location 
        self.to_location = to_location
        self.name = "move"
        self.args = (from_location, to_location)

    def execute(self, in_state, tstep=1):
         next_state = ForkState.copy(in_state)
         next_state.currentNode = next_state.actionMap.nearest_index(self.to_location)
         next_state.has_pallet_id = in_state.has_pallet_id

         modified_groundings = []
         # propogate trajectories using rrt
         agent = next_state.agent
         sx,sy,sz,stheta = transpose(agent.path.points_xyztheta)[-1]
         start_t = agent.path.timestamps[-1]+tstep

         fx, fy = self.to_location
         ftheta = arctan2(fy - sy, fx - sx)
         path = [[fx, fy, ftheta]]

         pX, pY, pTheta = transpose(path)
         end_t = tstep*len(pX)+start_t
         pTime = arange(start_t, end_t, tstep)

         apath = Path.from_xyztheta(pTime, [pX, pY, zeros(len(pX)), pTheta])
         new_agent = next_state.agent.withExtendedPath(apath)
         next_state.groundableDict[new_agent.id] = new_agent
         modified_groundings.append(new_agent)
         
         if next_state.has_pallet_id:
              ppath = Path.from_xyztheta(pTime, [pX, pY, ones(len(pX)), pTheta])
              new_pallet = next_state.getGroundableById(next_state.has_pallet_id).withExtendedPath(ppath)
              next_state.groundableDict[new_pallet.id] = new_pallet
              modified_groundings.append(new_pallet)
         next_state.action_sequence.append((in_state, self))
         return next_state, modified_groundings

    def __str__(self):
        return '(Move to '+str(self.to_location)+')'

class PickUp(Action):
     def __init__(self, pallet_id):
          self.pallet_id = pallet_id
          self.name = "pickup"
          self.args = (pallet_id,)
          
     def execute(self, in_state, tstep=1):

          next_state = ForkState.copy(in_state)
          next_state.has_pallet_id = self.pallet_id
          modified_groundings = []

          agent = next_state.agent
          sx,sy,sz,stheta = transpose(agent.path.points_xyztheta)[-1]
          start_t = agent.path.timestamps[-1]+tstep
          
          fx,fy,z,th = transpose(next_state.getGroundableById(self.pallet_id).path.points_xyztheta)[-1]
          ftheta = arctan2(fy - sy, fx - sx)
          path = [[fx, fy, ftheta]]

          pX, pY, pTheta = transpose(path)
          end_t = tstep*len(pX)+start_t
          pTime = arange(start_t, end_t, tstep)

          apath = Path.from_xyztheta(pTime, [pX, pY, zeros(len(pX)), pTheta])
          new_agent = next_state.agent.withExtendedPath(apath)
          next_state.groundableDict[new_agent.id] = new_agent
          modified_groundings.append(new_agent)
         
          ppath = Path.from_xyztheta([end_t], [[fx],[fy],[1],[0]])
          new_pallet = next_state.getGroundableById(self.pallet_id).withExtendedPath(ppath)
          next_state.groundableDict[new_pallet.id] = new_pallet
          modified_groundings.append(new_pallet)
         
          next_state.currentNode = next_state.actionMap.nearest_index((fx,fy,z))
          next_state.action_sequence.append((in_state, self))
          return next_state, modified_groundings

     def __str__(self):
          return 'Pick up pallet '+str(self.pallet_id)

class PutDown(Action):

    def __init__(self, location, pallet_id):
        #location to place pallet
        self.location = location
        self.pallet_id = pallet_id
        self.name = "putdown"
        self.args = (location, pallet_id)

    def execute(self, in_state, tstep=1):
         modified_groundings = []
         next_state = ForkState.copy(in_state)
         next_state.currentNode = next_state.actionMap.nearest_index(self.location)
         placed_pallet_id = in_state.has_pallet_id
         next_state.has_pallet_id = None
         
        #propogate trajectories using rrt
         agent = next_state.agent
         sx,sy,sz,stheta = transpose(agent.path.points_xyztheta)[-1]
         start_t = agent.path.timestamps[-1]+tstep
         
         fx,fy,z = self.location
         ftheta = arctan2(fy - sy, fx - sx)
         path = [[fx, fy, ftheta]]

         pX, pY, pTheta = transpose(path)
         end_t = tstep*len(pX)+start_t
         pTime = arange(start_t, end_t, tstep)

         apath = Path.from_xyztheta(pTime, [pX, pY, zeros(len(pX)), pTheta])
         new_agent = next_state.agent.withExtendedPath(apath)
         next_state.groundableDict[new_agent.id] = new_agent
         modified_groundings.append(new_agent)
         cx,cy,cz = self.location
         ppath = Path.from_xyztheta([end_t], [[cx],[cy],[cz],[0]])
         new_pallet = next_state.getGroundableById(placed_pallet_id).withExtendedPath(ppath)
         next_state.groundableDict[new_pallet.id] = new_pallet
         modified_groundings.append(new_pallet)
         next_state.action_sequence.append((in_state, self))
         return next_state, modified_groundings

    def __str__(self):
        return 'Put Down pallet at '+str(self.location)



