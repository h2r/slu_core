from arlcm.gps_to_local_t import gps_to_local_t
from arlcm.pallet_list_t import pallet_list_t
from arlcm.object_list_t import object_list_t
from botlcm.pose_t import pose_t
from forkState import ForkState,  physicalObject
from spatial_features.groundings import Prism
from affineMatrix import AffineMatrix
from actionMap import ActionMap, tmapFromRndf, tmapFromObjects
from lcm import EventLog
import lcm
import math
import select
import rndf_util as ru
import threading
from numpy import transpose as tp
import spatial_features_cxx as sf
from lcm_log_parse import LcmParse
from spatial_features.groundings import PhysicalObject, Path
import collections
from memoized import memoized


def play_start_of_lcm_log(state_app, log_fname, callback=lambda : True):
    state_app.reset()
    from subprocess import Popen
    import time
    cmd = ["lcm-logplayer", "--speed=4", "%s" % log_fname]
    print "cmd", cmd
    process = Popen(cmd)
    try:
        for i in range(0, 5):
            time.sleep(0.01)
            callback()
    finally:
        process.terminate()
        process.wait()

# must be synced with c code in renderer_object_anntoator in ar viewer.
FORKLIFT_ID = -100 

class App(threading.Thread):
    def __init__(self, rndf_fname=None):
        threading.Thread.__init__(self)
        self.lc = lcm.LCM()

        #load the model
        if rndf_fname != None:
            self.set_rndf(rndf_fname)
        else:
            self.rndf = None

        self.trans_xyz = (0, 0, 0)
        
        self.trans_theta = 0

        self.curr_location = None
        self.curr_orientation = None

        self.lc.subscribe("PALLET_LIST", self.on_pallet_msg)
        self.lc.subscribe("POSE", self.on_pose_msg)
        self.lc.subscribe("GPS_TO_LOCAL", self.on_transform_msg)
        self.lc.subscribe("OBJECT_LIST", self.on_objects_msg)

        self.reset()
        self.lock = threading.Lock()

    def set_rndf(self, rndf_fname):
        self.rndf = ru.rndf(rndf_fname, True)
        self.trans_latlon = self.rndf.origin


    def reset(self):
        self.curr_state = None
        self.curr_pallets = dict()
        self.curr_objects = dict()
        self.curr_prism = None
        self.curr_location = None
        self.curr_orientation = None
        self.trans_xyz = (0, 0, 0)        
        self.trans_theta = 0
    
    def socketActivated(self):
        self.lc.handle()
        
    def on_transform_msg(self, channel, data):
        #print 'got trans'
        msg = gps_to_local_t.decode(data)
        self.trans_xyz = msg.local
        self.trans_latlon = (msg.lat_lon_el_theta[0], msg.lat_lon_el_theta[1])
        self.trans_theta = msg.lat_lon_el_theta[3]

    def pos_to_location(self, pos):
        return ru.robot_pose_to_rndf(pos,
                                     self.trans_xyz, self.trans_theta,
                                     self.trans_latlon, self.rndf)
    
    def on_pose_msg(self, channel, data):
        msg = pose_t.decode(data)
        x, y, z = msg.pos[0:3]

        self.curr_location = self.pos_to_location(msg.pos[0:3])
        #p = self.curr_location
        #print p[0], p[1] ,self.closest_map_location(self.curr_location)
        
        #compute orientation in rndf frame
        o_vec = self.bot_quat_rotate(msg.orientation, (1,0,0))
        robot_orientation = math.atan2(o_vec[1], o_vec[0])
        self.curr_orientation = robot_orientation - self.trans_theta

        x, y, z = self.curr_location
        bounding_polygon = [(x - 0.75, y - 0.75),
                            (x + 0.75, y - 0.75),
                            (x + 0.75, y + 0.75),
                            (x - 0.75, y + 0.75)]
        cx, cy = sf.math2d_centroid(tp(bounding_polygon))
        af = AffineMatrix()
        af.translate(cx, cy)
        af.rotate(self.curr_orientation)
        af.translate(-cx, -cy)
        self.curr_prism = Prism(tp([af.transformPt(p)
                                    for p in bounding_polygon]),
                                0, 2)

    def on_pallet_msg(self, channel, data):
        msg = pallet_list_t.decode(data)
        
        for p in msg.pallets:
            self.convert_lcm(p)
            self.curr_pallets[p.id] = p

    def convert_lcm(self, objectOrPallet):
        # it appears we can just ignore relative_to_id for this;
        # the positions look correct. - stefie10
        objectOrPallet.pos = self.pos_to_location(objectOrPallet.pos)
        
    def on_objects_msg(self, channel, data):
        msg = object_list_t.decode(data)

        for o in msg.objects:
            self.convert_lcm(o)
            self.curr_objects[o.id] = o
        
    '''
    Generates the first state of a state sequence
    Should only be called after a pose, an obstacle and a pallet
    message are recieved
    '''
    def initialize_state(self, useRndf = True):

        held_pallet = self.holding_pallet()

        objects = self.curr_objects.values()
        pallets = self.curr_pallets.values()
        orientation = self.curr_orientation
        
        if self.rndf and useRndf:
            tmap, tmap_locs = tmapFromRndf(self.curr_location[0:2], self.rndf)
        else:
            tmap, tmap_locs = tmapFromObjects(self.curr_location[0:2], [physicalObject(o) for o in objects+pallets])
        am = ActionMap(tmap=tmap, tmap_locs=tmap_locs)

        self.curr_state = ForkState.from_lcm(am.nearest_index(self.curr_location), 
                                             orientation,
                                             pallets,
                                             held_pallet,
                                             objects,
                                             am)
                                                       
    def holding_pallet(self):
        for p in self.curr_pallets.values():
            if p.relative_to_id == 1:
                return p
        return None
    
    def closest_map_location(self, pose):

        cloc = None
        min_dist = float('inf')
        for loc in self.tmap_locs:
            position = self.tmap_locs[loc]
            if position == None:
                raise ValueError("No position for " + `loc`)
            dist = math.hypot(position[0] - pose[0], position[1] - pose[1])
            if dist < min_dist:
                min_dist = dist
                cloc = loc

        return cloc

    def bot_quat_rotate(self, rot, v):
        ab  =  rot[0]*rot[1]
        ac  =  rot[0]*rot[2]
        ad  =  rot[0]*rot[3]

        nbb = -rot[1]*rot[1]
        bc  =  rot[1]*rot[2]
        bd  =  rot[1]*rot[3]

        ncc = -rot[2]*rot[2]
        cd  =  rot[2]*rot[3]
        ndd = -rot[3]*rot[3]

        result = (
        2*( (ncc + ndd)*v[0] + (bc -  ad)*v[1] + (ac + bd)*v[2] ) + v[0],
        2*( (ad +  bc)*v[0] + (nbb + ndd)*v[1] + (cd - ab)*v[2] ) + v[1],
        2*( (bd -  ac)*v[0] + (ab +  cd)*v[1] + (nbb + ncc)*v[2] ) + v[2])

        return result

    def run(self):
        print "Waiting for command"
        
        loop = True
        while True:
            if loop:
                print 'go....................'
                loop = False
            if len(select.select([self.lc],[],[],0.01)[0]):
                self.lock.acquire()
                self.lc.handle()
                self.lock.release()

    def get_current_state(self):
        if self.curr_location == None:
            # haven't received enough packets.
            return None
            
        
        self.initialize_state()
        return self.curr_state, self.curr_state.actionMap 
            
    def get_current_state_no_rndf(self):
        if self.curr_location == None:
            # haven't received enough packets.
            return None
            
        
        self.initialize_state(useRndf=False)
        return self.curr_state, self.curr_state.actionMap 

def getInitialStateFromLogApp(log_file, rndf_file=None):
    app = App(rndf_fname=rndf_file)

    return getInitialStateFromLog(log_file, app)

def getInitialStateFromLog(log_file, app):
    app.reset()

    log = EventLog(log_file, "r")
    for i, e in enumerate(log):
        if e.channel == "POSE":
            app.on_pose_msg(e.channel, e.data)
        elif e.channel == "PALLET_LIST":
            app.on_pallet_msg(e.channel, e.data)
        elif e.channel == "GPS_TO_LOCAL":
            app.on_transform_msg(e.channel, e.data)
        elif e.channel == "OBJECT_LIST":
            app.on_objects_msg(e.channel, e.data)
        
        if i > 5000:
            break
    
    return app.get_current_state()

@memoized
def parse_log(rndf_fname, log_fname, wait_until_teleport=False):
    app = App(rndf_fname)
    try:
        log = EventLog(log_fname, "r")
    except:
        print "can't read", log_fname
        raise

    pallets = dict()
    for e in log:
        if e.channel == "PALLET_LIST":
            msg = pallet_list_t.decode(e.data)
            for p in msg.pallets:
                if not p.id in pallets:
                    pallets[p.id] = p
                if p.relative_to_id == 0:
                    p.pos = ru.robot_pose_to_rndf(p.pos, app.trans_xyz, app.trans_theta, app.trans_latlon, app.rndf)
        if e.channel == "GPS_TO_LOCAL":
            app.on_transform_msg(e.channel, e.data)
            
    #should have all pallets in the first position they were seen
    app.curr_pallets = pallets
    
    #now that pallets are initialized, restart
    log = EventLog(log_fname, "r")
    agent_path = []
    object_paths = collections.defaultdict(lambda : list())
    obj_id_to_pobj = {}
    agent_prism = None
    sample_frequency_hz = 1
    last_sample_micros = None
    timestamps = []
    teleport_ts = None
    for e in log:
        if e.channel == "SIM_TELEPORT":
            teleport_ts = e.timestamp
        if (teleport_ts == None or 
            e.timestamp - teleport_ts < (1 * 1000 * 1000)):
            if wait_until_teleport:
                continue

        if e.channel == "POSE":
            app.on_pose_msg(e.channel, e.data)


        elif e.channel == "PALLET_LIST":
            app.on_pallet_msg(e.channel, e.data)
        elif e.channel == "GPS_TO_LOCAL":
            app.on_transform_msg(e.channel, e.data)
        elif e.channel == "OBJECT_LIST":
            app.on_objects_msg(e.channel, e.data)

        if last_sample_micros == None:
            last_sample_micros = e.timestamp

        if (e.timestamp - last_sample_micros >=
            (1.0/sample_frequency_hz) * 1000 * 1000):
            state, new_am = app.get_current_state()
            x,y,z = app.curr_location
            if agent_prism == None:
                agent_prism = app.curr_prism

            agent_path.append((x, y, z, app.curr_orientation))
            if state != None:
                last_sample_micros = e.timestamp
                timestamps.append(e.timestamp)
                for pobj_id in state.getObjectsSet():
                    if pobj_id in app.curr_objects:
                        lcm_obj = app.curr_objects[pobj_id]
                    elif pobj_id in app.curr_pallets:
                        lcm_obj = app.curr_pallets[pobj_id]
                    else:
                        raise ValueError()
                    o_vec = app.bot_quat_rotate(lcm_obj.orientation, (1,0,0))
                    orientation = math.atan2(o_vec[1], o_vec[0])

                    pobj = state.getGroundableById(pobj_id)
                    object_paths[pobj.lcmId].append(pobj.centroid3d + 
                                                    (orientation,))
                    if not pobj.lcmId in obj_id_to_pobj:
                        obj_id_to_pobj[pobj.lcmId] = pobj
            

    lcm_parse = LcmParse()
    lcm_parse.agent_obj = PhysicalObject(agent_prism, tags=["forklift"],
                                         path=Path(timestamps,
                                                   points_xyztheta=tp(agent_path)),
                                         lcmId=FORKLIFT_ID)
    for obj_id, path in object_paths.iteritems():
        if obj_id == FORKLIFT_ID:
            continue # forklift weirdly appears here, but we deal with it separately.
        pobj = obj_id_to_pobj[obj_id]

        path = Path(timestamps, points_xyztheta=tp(object_paths[pobj.lcmId]))
        pobj.path = path
        pobj.updateRep()
        lcm_parse.pobjs.append(pobj)
        lcm_parse.object_id_to_path[pobj.lcmId] = path

    lcm_parse.places = []
    for place_id in app.curr_state.getPlacesSet():
        lcm_parse.places.append(app.curr_state.getGroundableById(place_id))
        

    lcm_parse.object_id_to_path[FORKLIFT_ID] = lcm_parse.agent_obj.path

    return lcm_parse


