from arlcm.task_destination_checkpoint_t import task_destination_checkpoint_t
from arlcm.task_destination_pose_t import task_destination_pose_t
from arlcm.task_pose_trajectory_t import task_pose_trajectory_t
from arlcm.waypoint_list_t import waypoint_list_t
from arlcm.waypoint_t import waypoint_t
from arlcm.gps_to_local_t import gps_to_local_t
from arlcm.task_planner_status_t import task_planner_status_t
from arlcm.task_planner_state_enum_t import task_planner_state_enum_t
from arlcm.pallet_manipulation_command_list_t import pallet_manipulation_command_list_t
from arlcm.pallet_manipulation_command_t import pallet_manipulation_command_t
from botlcm.pose_t import pose_t
from arlcm.pointlist2d_t import pointlist2d_t

import lcm
import time
import random
import select
import rndf_util as ru

class App:

    def __init__(self, rndf_file=None):
        self.lc = lcm.LCM()
        self.event_num = 0

        if rndf_file == None:
            self.rndf = None
            self.tmap = None
            self.tmap_locs = None
            return
        print 'subscribing'
        self.lc.subscribe("GPS_TO_LOCAL", self.on_transform_msg)

        if isinstance(rndf_file, ru.rndf):
            self.rndf = rndf_file
            self.tmap = None
            self.tmap_locs = None
            return
        else:
            self.rndf = ru.rndf(rndf_file, True)

        self.trans_xyz = (0, 0, 0)
        self.trans_latlon = self.rndf.origin
        self.trans_theta = 0

        self.tp_status = task_planner_state_enum_t.TP_IDLE
        self.lc.subscribe("TASK_PLANNER_STATUS", self.on_task_planner_status_msg)

    def send_checkpoint(self, chk_pt, returnEvent=False):
        msg = task_destination_checkpoint_t()
        msg.utime = self.bot_time_now()
        msg.clear = 0
        msg.checkpoint = chk_pt
        msg.task_id = self.get_unique_task_id()

        if returnEvent:
            self.event_num += 1
            return lcm.Event(self.event_num, msg.utime, "TASK_DESTINATION_CHECKPOINT", msg.encode())
        else:
            self.lc.publish("TASK_DESTINATION_CHECKPOINT", msg.encode())


    def send_xy(self, xy, returnEvent=False):
        if self.rndf == None:
            raise Error("Can't call send xy without supplying an RNDF")

        x,y,z = ru.rndf_pose_to_robot((xy[0], xy[1], 0), self.trans_xyz, self.trans_theta, self.trans_latlon, self.rndf)
        print x,y
        msg = task_destination_pose_t()
        msg.utime = self.bot_time_now()
        msg.pos = [x, y]
        #TODO fix me
        #msg.heading = 1.79+3.14/2-1
        #msg.heading_matters = True
        msg.task_id = self.get_unique_task_id()
        if returnEvent:
            self.event_num += 1
            return lcm.Event(self.event_num, msg.utime, "TASK_DESTINATION_POSE", msg.encode())
        else:
            self.lc.publish("TASK_DESTINATION_POSE", msg.encode())


    def send_latlon(self, lat, lon, returnEvent=False):
        msg = task_destination_pose_t()
        msg.utime = self.bot_time_now()
        msg.pos = [lat, lon]
        #TODO fix me
        #msg.heading = 1.79+3.14/2-1
        #msg.heading_matters = True
        msg.task_id = self.get_unique_task_id()
        if returnEvent:
            self.event_num += 1
            return lcm.Event(self.event_num, msg.utime, "TASK_DESTINATION_POSE_GPS", msg.encode())
        else:
            self.lc.publish("TASK_DESTINATION_POSE_GPS", msg.encode())

    def send_trajectory(self, xys):
        if self.rndf == None:
            raise Error("Can't call send trajectory without supplying an RNDF")

        msg = task_pose_trajectory_t()
        msg.utime = self.bot_time_now()
        msg.task_id = self.get_unique_task_id()
        wps = waypoint_list_t()
        wps.utime = msg.utime
        wps.numWaypoints = len(xys)

        for k in range(len(xys)):
            xy = xys[k]

            wp = waypoint_t()
            wp.utime = msg.utime
            wp.id = k
            robot_xy = ru.rndf_pose_to_robot((xy[0], xy[1], 0), self.trans_xyz, self.trans_theta, self.trans_latlon, self.rndf)
            wp.x = robot_xy[0]
            wp.y = robot_xy[1]

            wps.waypoints.append(wp)
        
        msg.waypoints = wps
        self.lc.publish("TASK_POSE_TRAJECTORY", msg.encode())

    def send_pickup_pallet_msg(self, lcmId, returnEvent=False):

        msg_l = pallet_manipulation_command_list_t()
        msg_l.num_commands = 1
        msg_l.utime = self.bot_time_now()

        msg = pallet_manipulation_command_t()
        msg.task_id = self.get_unique_task_id()
        msg.utime = msg_l.utime
        msg.pickup = True
        msg.pallet_id = lcmId
        msg.destination_id = -1
        msg.roi = pointlist2d_t() 
        msg.pose = pose_t()
        msg.pose.pos = (0,0,0)
        msg.pose.vel = [0,0,0]
        msg.pose.orientation = [0,0,0,0]
        msg.pose.rotation_rate = [0,0,0]
        msg.pose.accel = [0,0,0]

        msg_l.commands = [msg]
        if returnEvent:
            self.event_num += 1 
            return lcm.Event(self.event_num, msg_l.utime, "PALLET_MANIPULATION_COMMAND_LIST", msg_l.encode())
        else:
            self.lc.publish("PALLET_MANIPULATION_COMMAND_LIST", msg_l.encode())

    def send_place_pallet_msg(self, x,y,z, returnEvent=False):

        msg_l = pallet_manipulation_command_list_t()
        msg_l.num_commands = 1
        msg_l.utime = self.bot_time_now()

        msg = pallet_manipulation_command_t()
        msg.task_id = self.get_unique_task_id()
        msg.utime = msg_l.utime
        msg.pickup = False
        msg.pallet_id = -1
        msg.destination_id = -1
        
        msg.roi = pointlist2d_t() 
        msg.pose = pose_t()
        msg.pose.pos = (x, y, z)
        msg.pose.vel = [0,0,0]
        msg.pose.orientation = [0,0,0,0]
        msg.pose.rotation_rate = [0,0,0]
        msg.pose.accel = [0,0,0]

        msg_l.commands = [msg]
        if returnEvent:
            self.event_num += 1 
            return lcm.Event(self.event_num, msg_l.utime, "PALLET_MANIPULATION_COMMAND_LIST", msg_l.encode())
        else:
            self.lc.publish("PALLET_MANIPULATION_COMMAND_LIST", msg_l.encode())

    def send_transport_msg(self, lat, lon, orientation, returnEvent=False):
        msg = pose_t()
        msg.utime = self.bot_time_now()
        msg.pos = (lat, lon, orientation)
        msg.vel = (0, 0, 0)
        msg.orientation = (orientation, 0, 0, 0)
        msg.rotation_rate = (0, 0, 0)
        msg.accel = (0, 0, 0)
        
        if returnEvent:
           self.event_num += 1  
           return lcm.Event(self.event_num, msg.utime, "SIM_TELEPORT_GLOBAL_FRAME", msg.encode())
        else:
            self.lc.publish("SIM_TELEPORT_GLOBAL_FRAME", msg.encode())

    def set_transform(self, trans_xyz, trans_latlon, trans_theta):
        self.trans_xyz = trans_xyz
        self.trans_latlon = trans_latlon
        self.trans_theta = trans_theta
            
    def on_transform_msg(self, channel, data):
        print 'got trans'
        msg = gps_to_local_t.decode(data)
        self.trans_xyz = msg.local
        self.trans_latlon = (msg.lat_lon_el_theta[0], msg.lat_lon_el_theta[1])
        self.trans_theta = msg.lat_lon_el_theta[3]

    def on_task_planner_status_msg(self, channel, data):
        msg = task_planner_status_t.decode(data)
        self.tp_status = msg.task_planner_state;
        
    def get_unique_task_id(self):
        return (int('0xefffffffffffffff',16)&(self.bot_time_now()<<8)) + random.randint(0,255);

    def bot_time_now(self):
        return int(time.time()*1000000)
        
    def run(self):
        print "Waiting for command"
        start = time.time()
        curr = time.time()
        while True:
            curr = time.time()
            if len(select.select([self.lc],[],[],0.01)[0]):
                self.lc.handle()
            #actions_left = self.process_actions()
            #if not actions_left:
            #    break

    
                
if __name__=="__main__":
    app = App([], '../../data/directions/forklift/partitions/forklift_full_part.pck','../../data/directions/forklift/Lee_RNDF_demo.txt')
    #app.run()
    print 'commanding'
    #app.send_checkpoint(35)
    app.send_xy((3,25))
    app.send_xy((5,40))
    #app.send_checkpoint(35, True)
    #app.send_place_pallet_msg(0,0,0)
    #app.send_pickup_pallet_msg(1)
    #app.send_trajectory([(5,5), (10,10), (20,0)])
