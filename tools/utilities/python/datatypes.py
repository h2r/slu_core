import math
import sys
from random import random
from numpy import *
import carmen_util


class littledog_encoders:
    def __init__(self, lf_hip_x, lf_hip_y, lf_knee_y, rf_hip_x, rf_hip_y, rf_knee_y,
                 lr_hip_x, lr_hip_y, lr_knee_y, rr_hip_x, rr_hip_y, rr_knee_y, stepleg):
        self.lf_hip_x, self.lf_hip_y, self.lf_knee_y =  lf_hip_x, lf_hip_y, lf_knee_y 
        self.rf_hip_x, self.rf_hip_y, self.rf_knee_y =  rf_hip_x, rf_hip_y, rf_knee_y
        self.lr_hip_x, self.lr_hip_y, self.lr_knee_y =  lr_hip_x, lr_hip_y, lr_knee_y
        self.rr_hip_x, self.rr_hip_y, self.rr_knee_y =  rr_hip_x, rr_hip_y, rr_knee_y
        self.stepleg = stepleg
    
    def fromarray(self, data):
        [self.lf_hip_x, self.lf_hip_y, self.lf_knee_y, 
         self.rf_hip_x, self.rf_hip_y, self.rf_knee_y,
         self.lr_hip_x, self.lr_hip_y, self.lr_knee_y,
         self.rr_hip_x, self.rr_hip_y, self.rr_knee_y, self.stepleg] = data
    
    def toarray(self):
        arry=[self.lf_hip_x, self.lf_hip_y, self.lf_knee_y, 
              self.rf_hip_x, self.rf_hip_y, self.rf_knee_y,
              self.lr_hip_x, self.lr_hip_y, self.lr_knee_y,
              self.rr_hip_x, self.rr_hip_y, self.rr_knee_y]
        return arry
    
    def __str__(self):
        return str(self.toarray())
    
    def __repr__(self):
        return str(self.toarray())

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0


class foot_sensors:
    def __init__(self, fl, fr, rl, rr, dog_ts, ts):
        self.fl = fl
        self.fr = fr
        self.rl = rl
        self.rr = rr
        self.dog_ts = dog_ts
        self.ts = ts

    def toarray(self):
        return [self.fl, self.fr, self.rl, self.rr]

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0


class plane:
    def __init__(self,n,d,extents=None):
        #this is assumed to be a polygon
        #   encasing the plane
        self.extents = extents
        #Z = sqrt(sum(array(n)**2))
        self.n = n
        self.d = d

    def value(self, x, y):
        return (self.d - self.n[0]*x -self.n[1]*y)/(1.0*self.n[2])

    def valueyz(self, y, z):
        return (self.d - self.n[2]*z -self.n[1]*y)/(1.0*self.n[0])

    def valuexz(self, x, z):
        return (self.d - self.n[0]*x -self.n[2]*z)/(1.0*self.n[1])
    
    def __str__ (self):
        return "[n:"+ str(self.n)+ " d:" +str(self.d)+"]"
    def __repr__ (self):
        return "[n:"+ str(self.n)+ " d:" + str(self.d)+"]"


class body_pose:
    def __init__(self, x, y, z, roll, pitch, yaw, timestamp=None, dog_ts=None):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.dog_ts = dog_ts
        self.timestamp = timestamp

    def fromdata(self, data, dog_ts, ts):
        self.x = data[0]
        self.y = data[1]
        self.z = data[2]
        self.yaw = data[3]
        self.pitch = data[4]
        self.roll = data[5]
        self.dog_ts = dog_ts
        self.timestamp = ts


    def getpose_xyz(self):
        return array([self.x, self.y, self.z])

    def getdata(self):
        return [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]

    def toarray(self):
        return [self.x, self.y, self.z, self.roll, self.pitch, self.yaw]
    


    def __str__(self):
        return "x:" + str(self.x) + " y:"+str(self.y) + " z:"+str(self.z) + " yaw:"+str(self.yaw) +" pitch:"+str(self.pitch) + " roll:"+str(self.roll)


    def __repr__(self):
        return "x:" + str(self.x) + " y:"+str(self.y) + " z:"+str(self.z) + " yaw:"+str(self.yaw) +" pitch:"+str(self.pitch) + " roll:"+str(self.roll)

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0




class velocity_reading:
    def __init__(self, vx, vy, vz, vyaw, vpitch, vroll, timestamp=None, dog_ts=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.vyaw = vyaw
        self.vpitch = vpitch
        self.vroll = vroll
        self.dog_ts = dog_ts
        self.timestamp = timestamp

    def toarray(self):
        return [self.vx, self.vy, self.vz, self.vyaw, self.vpitch, self.vroll]
 
    def get_rates_xyz(self):
        return [self.vx, self.vy, self.vz]

    def get_rates_orient(self):
        return [self.vyaw, self.vpitch, self.vroll]
    
    def __str__(self):
        return "vx:" + str(self.vx) + " vy:"+str(self.vy) + " vz:"+str(self.vz) + " vyaw:"+str(self.vyaw) +" vpitch:"+str(self.vpitch) + " vroll:"+str(self.vroll)

    def __repr__(self):
        return "vx:" + str(self.vx) + " vy:"+str(self.vy) + " vz:"+str(self.vz) + " vyaw:"+str(self.vyaw) +" vpitch:"+str(self.vpitch) + " vroll:"+str(self.vroll)

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0


class imu_reading:
    def __init__(self, roll, pitch, yaw, vx, vy, vz, ax, ay, az, timestamp=None, dog_ts=None):
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.ax = ax
        self.ay = ay
        self.az = az
        self.dog_ts = dog_ts
        self.timestamp = timestamp

    def get_ypr(self):
        return [self.yaw, self.pitch, self.roll]

    def get_rates_xyz(self):
        return [self.vx, self.vy, self.vz]

    def get_acc_xyz(self):
        return [self.ax, self.ay, self.az]
    
    def __str__(self):
        return "x:" + str(self.x) + " y:"+str(self.y) + " z:"+str(self.z) + " yaw:"+str(self.yaw) +" pitch:"+str(self.pitch) + " roll:"+str(self.roll)

    def __repr__(self):
        return "x:" + str(self.x) + " y:"+str(self.y) + " z:"+str(self.z) + " yaw:"+str(self.yaw) +" pitch:"+str(self.pitch) + " roll:"+str(self.roll)

    def fromdata(self, data, dog_ts, ts):
        self.yaw = data[0]
        self.pitch = data[1]
        self.roll = data[2]
        self.vx = data[3]
        self.vy = data[4]
        self.vz = data[5]
        self.ax = data[6]
        self.ay = data[7]
        self.az = data[8]
        self.dog_ts = dog_ts
        self.timestamp = ts

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0


class tree_elt:
    def __init__(self, key, data):
        self.key = key
        self.data = data

    def __str__ (self):
        return str(self.data)
    def __repr__ (self):
        return str(self.data)

class line:
    def __init__(self, m, b):
        self.m = m
        self.b = b

    def perpendicular_distance_arry(self, pt):
        if(self.m == 0):
            m2 = sys.maxint
        else:
            m2 = -1 * (1/(self.m * 1.0))

        b2 = pt[1] - (m2 * pt[0])
        x = (b2 - self.b)/(1.0*self.m - m2)
        y = self.m * x + self.b
        
        return carmen_util.get_euclidean_distance([x,y], pt)

    def perpendicular_distance(self, toPoint):
        if(self.m == 0):
            m2 = sys.maxint
        else:
            m2 = -1 * (1/(self.m * 1.0))
        
        b2 = toPoint.y - (m2 * toPoint.x)
        x = (b2 - self.b)/(1.0*self.m - m2)
        y = self.m * x + self.b

        return toPoint.distance(point(x, y, None)), point(toPoint.x,toPoint.y,None)

    def furthest_point_from_line(self, points):
        mymax = -1
        maxpt = None
        max_index = None
        pt_index = 0
        sum_dists = 0
        
        for pt in points:
            #print "points:", pt.x, pt.y
            dist,the_pt = self.perpendicular_distance(pt)

            #set the maximums
            if(dist > mymax):
                mymax = dist
                maxpt = pt
                max_index = pt_index

            #if we have a second maximum, set it to the maximum randomly
            elif(dist == mymax):
                myrand = random()
                if(myrand > 0.5):
                    mymax = dist
                    maxpt = pt
                    max_index = pt_index

            pt_index = pt_index + 1
            sum_dists = sum_dists + dist

        if(sum_dists == 0):
            sum_dists = sys.maxint
            
        mystd = sum_dists/len(points)
        return maxpt,mymax,max_index,mystd

    def closest_point_to_line(self, points):
        mymin = sys.maxint
        minpt = None
        min_index = None
        pt_index = 0
        
        for pt in points:
            #print "points:", pt.x, pt.y
            dist,the_pt = self.perpendicular_distance(pt)

            #set the minimums
            if(dist < mymin):
                mymin = dist
                minpt = pt
                min_index = pt_index

            #if we have a second minimum, set it to the minimum randomly
            elif(dist == mymin):
                myrand = random()
                if(myrand > 0.5):
                    mymin = dist
                    minpt = pt
                    min_index = pt_index

            pt_index = pt_index + 1
        return minpt,mymin,min_index

    def same_line(self, line, epsilon_m, epsilon_b):
        if(abs(line.m-self.m) > epsilon_m):
            return False
        if(abs(line.b-self.b) > epsilon_b):
            return False

        return True
        
    def get_val(self, x):
        return self.m * x + self.b


    def get_line_segment(self, start_x, end_x):
        start_y = self.get_val(start_x)
        end_y = self.get_val(end_x)

        X = [start_x, end_x]
        Y = [start_y, end_y]

        return X,Y

    def get_line_from_points(self,start_pt, end_pt):
        if(start_pt.distance(end_pt)==0):
            return None
        m = (end_pt.y-start_pt.y)/(end_pt.x - start_pt.x)
        b = start_pt.y - m*start_pt.x

        return line(m,b)

    def get_intercept(self, l2):

        x = (self.b - l2.b)/(1.0*(self.m - l2.m))

        y = self.m*x+self.b

        return [x,y]

    def above(self, pt):
        myB = pt.y - self.m * pt.x 

        if myB > self.b:
            return True
        else:
            return False

class vector:
    def __init__(self, data):
        self.data = array(data)

    def distance(self, other_vec):
        if(not len(self.data) == len(other_vec.data)):
            print "vectors of different size... exiting"
            #throwing an exception is probably better
            sys.exit(0)

        return float(abs((sqrt(sum(power((self.data-other_vec.data), 2))))))
    def __str__ (self):
        return str(self.data)
    def __repr__ (self):
        return str(self.data)

class point:
    def __init__(self, x=0, y=0, theta=0):
        self.x = x
        self.y = y
        self.theta = theta

    def set(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

    def distance(self, pt):
        return math.sqrt((self.x-pt.x)**2 + (self.y-pt.y)**2)
    
    def manhattan_distance(self, pt):
        return abs(self.x-pt.x) + abs(self.y-pt.y)

    def toarray(self):
        return [self.x, self.y, self.theta]

    def fromarray(self, arry):
        self.x = arry[0];
        self.y = arry[1]
        self.theta = arry[2]

        return point(self.x, self.y, self.theta)

    def tomatrix(self):
        return array([[self.x], [self.y], [self.theta]])
    
    def __str__ (self):
        return "X:"+ str(self.x) + " Y:" + str(self.y)+ " Theta:" + str(self.theta)

    def __repr__ (self):
        return "X:"+ str(self.x) + " Y:" +str(self.y)+ " Theta:" + str(self.theta)


class point_timestamp(point):
    def __init__(self, x=0, y=0, theta=0, timestamp=0):
        self.x = x
        self.y = y
        self.theta = theta
        self.timestamp = timestamp

class odometry_message:
    def __init__(self, timestamp, data):
        self.timestamp = timestamp
        self.location = point(data[0], data[1], data[2])

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0

class laser_message:
    def __init__(self, timestamp, data, laser_number=1):
        self.laser_number = 1
        self.timestamp = timestamp
        self.data = data
        self.odometry = None

    def set_odometry(self, odometry):
        self.odometry = odometry

    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0
    def __str__(self):
        return str(self.timestamp)
    def __repr__(self):
        return str(self.timestamp)


class robot_laser_message(odometry_message, laser_message):
    def __init__(self, timestamp, odometry, data, laser_number=1):
        odometry_message.__init__(self, timestamp, odometry)
        laser_message.__init__(self, timestamp, data, laser_number)
    def __str__(self):
        return str(self.timestamp)
    def __repr__(self):
        return str(self.timestamp)
    def __cmp__(self, other):
        if(self.timestamp < other.timestamp):
            return -1
        if(self.timestamp > other.timestamp):
            return 1

        return 0

    def carmen_str(self):

        # ROBOTLASER1 laser_type start_angle field_of_view angular_resolution maximum_range accuracy remission_mode num_readings [range_readings] num_remissions [remission values] laser_pose_x laser_pose_y laser_pose_theta robot_pose_x robot_pose_y robot_pose_theta laser_tv laser_rv forward_safety_dist side_safty_dist turn_axis

        mystr = "ROBOTLASER1 99 -1.570750 3.1415 0.0174 15.0 0.1 0 "
        mystr += str(len(self.data)) + " "
        for val in self.data:
            mystr+= str(val) + " "
        mystr += " 0 " + str(self.location.x) + " " + str(self.location.y) + " " + str(self.location.theta) + " "
        mystr += str(self.location.x) + " " + str(self.location.y) + " " + str(self.location.theta)
        mystr += " 0 0 0.435 0.505 100000.0 " + str(self.timestamp) + " none " + str(self.timestamp)

        return mystr

    
        
