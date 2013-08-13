import cPickle
import datatypes
import math
from math import cos, sin, atan2, tan, pi, sqrt, asin
from scipy import array, zeros, transpose, dot, arange, squeeze
from gsl_utilities import tklib_normalize_theta
#from pyTklib import *

#from datatypes import *


import gzip

def carmen_util_load_pck_gzip(inputfilename):
    myfile = gzip.open(inputfilename, 'rb')
    obj = cPickle.load(myfile)
    
    return obj

def carmen_util_load_pck(inputfilename):
    myfile = open(inputfilename, 'rb')
    obj = cPickle.load(myfile)
    
    return obj

def carmen_util_save_pck(outputfilename, data):
    myfile = open(outputfilename, 'wb')
    cPickle.dump(data, myfile)
    myfile.close()

def carmen_util_save_pck_gzip(outputfilename, data):
    myfile = gzip.open(outputfilename, 'wb')
    cPickle.dump(data, myfile)
    myfile.close()

def normalize_theta(theta):
    return tklib_normalize_theta(theta)

def normalize_theta_array(theta_array):
    ret_arry = []
    for theta in theta_array:
        ret_arry.append(normalize_theta(theta))
    return ret_arry

def quat2rot(q):
    R = zeros([3,3])*1.0

    R[0][0] = q[0]*q[0] + q[1]*q[1] - q[2]*q[2] - q[3]*q[3]
    R[0][1] = 2*(q[1]*q[2] - q[0]*q[3])
    R[0][2] = 2*(q[1]*q[3] + q[0]*q[2])


    R[1][0] = 2*(q[1]*q[2] + q[0]*q[3])
    R[1][1] = q[0]*q[0] + q[2]*q[2] - q[1]*q[1] - q[3]*q[3]
    R[1][2] = 2*(q[2]*q[3] - q[0]*q[1])

    R[2][0] = 2*(q[1]*q[3] - q[0]*q[2])
    R[2][1] = 2*(q[2]*q[3] + q[0]*q[1])
    R[2][2] = q[0]*q[0] + q[3]*q[3] - q[1]*q[1] - q[2]*q[2]

    return R

def quat2ypr(q):
    r = atan2(2*q[2]*q[3] + 2*q[0]*q[1], q[3]*q[3] - q[2]*q[2] - q[1]*q[1] + q[0]*q[0])
    p = -asin(2*q[1]*q[3] - 2*q[0]*q[2])
    y = atan2(2*q[1]*q[2] + 2*q[0]*q[3], q[1]*q[1] + q[0]*q[0] - q[3]*q[3] -q[2]*q[2])

    return [y, p, r]

def quat2rpy(q):
    y = -atan2(2*q[1]*q[2] - 2*q[0]*q[3], q[1]*q[1] + q[0]*q[0] - q[3]*q[3] -q[2]*q[2])
    p = asin(2*q[1]*q[3] + 2*q[0]*q[2])
    r = -atan2(2*q[2]*q[3] - 2*q[0]*q[1], q[3]*q[3] - q[2]*q[2] - q[1]*q[1] + q[0]*q[0])

    return [r, p, y]

def get_rotation_matrix2D(theta):
    return array([[cos(theta), -1.0*sin(theta)], [sin(theta), cos(theta)]])


#rotate around X
def rotate_x(pts, theta):
    R = get_rotation_matrix_x(theta)
    return transpose(matrixmultiply(R, transpose(pts)))

def get_rotation_matrix_x(theta):
    return array([[1,0,0], [0, cos(theta), sin(theta)], [0, -sin(theta), cos(theta)]])    

#rotate around Y
def rotate_y(pts, theta):
    R = get_rotation_matrix_y(theta)
    return transpose(matrixmultiply(R, transpose(pts)))

def get_rotation_matrix_y(theta):
    return array([[cos(theta),0,-sin(theta)],[0, 1, 0],[sin(theta),0,cos(theta)]])

#rotate around Z
def rotate_z(pts, theta):
    R = get_rotation_matrix_z(theta)
    return transpose(matrixmultiply(R, transpose(pts)));

def get_rotation_matrix_z(theta):
    return array([[cos(theta),sin(theta),0],[-sin(theta),cos(theta),0],[0,0,1]])

#other utilities
def num_as_str(i, buff=6):
    mylen = len(str(i))
    mysavefile = ""
    for j in range(buff-mylen):
        mysavefile = mysavefile + "0"

    mysavefile+=str(i)
    
    return mysavefile

def get_euclidean_distance(pt1, pt2):
    #print "in euclid dist"
    pt1 = array(pt1)
    pt2 = array(pt2)
    dist = sqrt(dot(pt1-pt2, pt1-pt2))
    
    return dist


def get_line_intercepts_r_theta(l_1, l_2):
    r_seg,phi_seg = l_1
    r_i,phi_i = l_2
    
    x_int = (((sin(phi_i)/sin(phi_seg))*r_seg) - r_i) / ((sin(phi_i)*cos(phi_seg)/sin(phi_seg))-cos(phi_i))
    y_int = (r_i - (x_int*cos(phi_i)))/sin(phi_i)

    return [x_int, y_int]

def get_line_intercepts_r_theta2(l_1, l_2):
    r_seg,phi_seg = l_1
    r_i,phi_i = l_2
    
    x_int = (((r_i*tan(phi_seg))/cos(phi_i)) - ((r_seg*tan(phi_i))/cos(phi_seg)))/(tan(phi_seg)-tan(phi_i))
    y_int = (r_i - (x_int*cos(phi_i)))/sin(phi_i)

    return [x_int,y_int]

def get_parametric_line_at_time(t, theta, a_x, a_y):
    x = t*cos(theta)+a_x
    y = t*sin(theta)+a_y
    return [x,y]

def get_perpendicular_line_intercept(pt, m1, b1):
    m2 = -1/(1.0*m1)
    b2 = pt[1] - m2*pt[0]

    x_intercept = (b2 - b1)/(1.0*(m1-m2))
    y_intercept = m1*x_intercept + b1

    return [x_intercept, y_intercept]

def get_line_parameters_r_theta(pt1, pt2):
    theta = atan2(pt1[0] - pt2[0], pt2[1] - pt1[1])
    r = pt1[0]*cos(theta) + pt1[1]*sin(theta)

    return r, theta

def get_line_parameters_m_pt(m, pt):
    b = (-m*pt[0]) + pt[1]
    return m, b

def get_line_parameters_m_b(pt1, pt2):
    if(pt1[0] - pt2[0] == 0):
        print pt1, pt2
    m = (pt1[1]-pt2[1])/((1.0)*pt1[0]-pt2[0])
    b = pt1[1] - pt1[0]*m
    
    return m, b

def get_smallest_and_largest_x(pts):
    minpt = pts[0]
    maxpt = pts[0]
    
    for pt in pts:
        if(pt.x < minpt.x):
            minpt = pt
        if(pt.x > maxpt.x):
            maxpt = pt

    return minpt, maxpt

def points_to_x_y(points):
    x = []
    y = []
    
    for pt in points:
        x.append(pt.x)
        y.append(pt.y)
    return x,y

def x_y_to_points(x,y):
    ptList = []
    
    for i in range(len(x)):
        ptList.append(datatypes.point(x[i],y[i],0))

    return ptList


def rtheta_to_xy(pose, reading):
    reading = array(reading)
    theta = arange(-pi/2.0, pi/2.0+0.001, pi/180.0)

    X = reading*cos(pose.theta + theta)+pose.x
    Y = reading*sin(pose.theta + theta)+pose.y
    
    return squeeze([X, Y])


def get_laser_reading_robot_frame(pose, reading):
    X=[]
    Y=[]
    #print "theta", odometry.location.theta
    for i in range(len(reading.data)):
        theta = i*math.pi/180.0
        if(reading.data[i] < 51):
            X.append(reading.data[i]*math.cos(theta+pose.theta-(math.pi/2.0)) + pose.x)
            Y.append(reading.data[i]*math.sin(theta+pose.theta-(math.pi/2.0)) + pose.y)

    return X,Y

def load_littledog_logfile(filename):
    myfile = open(filename) 
    laser_readings = []
    odometry_readings = []
    cob_readings = []
    imu_readings = []
    foot_readings = []
    mocap_encoder_readings = []
    body_encoder_readings = []
    #pose readings from mocap for the right,
    #left upper and lower legs

    front_left_upper_leg = []
    front_left_lower_leg = []
    front_right_upper_leg = []
    front_right_lower_leg = []

    rear_left_upper_leg = []
    rear_left_lower_leg = []
    rear_right_upper_leg = []
    rear_right_lower_leg = []

    for line in myfile:
        split_line = line.split()

        #take care of front laser readings
        if(split_line[0] == 'ROBOTLASER1'):
            num_readings = int(split_line[8])
            reading = []
            for i in range(num_readings):
                reading.append(float(split_line[i+9]))
            pose = split_line[len(split_line)-14:len(split_line)-11]
            
            #create them as floats
            for i in range(len(pose)):
                pose[i] = float(pose[i])

            
            timestamp = float(split_line[len(split_line)-3])
            my_msg = datatypes.robot_laser_message(timestamp, pose, reading, 1)

            laser_readings.append(my_msg)

        if(split_line[0] == 'ROBOTLASER2'):
            num_readings = int(split_line[8])
            reading = []
            for i in range(num_readings):
                reading.append(float(split_line[i+9]))

            timestamp = float(split_line[len(split_line)-3])
            my_msg = datatypes.laser_message(timestamp, reading, 2)
            laser_readings.append(my_msg)

        if(split_line[0] == 'RAWLASER5'):
            num_readings = int(split_line[8])
            reading = []
            for i in range(num_readings):
                reading.append(float(split_line[i+9]))

            ts = float(split_line[len(split_line)-3])
            my_msg = datatypes.laser_message(ts, reading)
            laser_readings.append(my_msg)

        if(split_line[0] == 'FOOT_SENSORS'):
            fl = float(split_line[2])
            fr = float(split_line[4])
            rl = float(split_line[6][0:len(split_line[6])-2])
            rr = float(split_line[8])
            dog_ts = float(split_line[10])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.foot_sensors(fl, fr, rl, rr, dog_ts, ts)
            foot_readings.append(my_msg)

        if(split_line[0] == 'MOCAP_ENCODERS'):
            fl_hip_rx = float(split_line[2])
            fl_hip_ry = float(split_line[4])
            fl_knee_ry = float(split_line[6])
            fr_hip_rx = float(split_line[8])
            fr_hip_ry = float(split_line[10])
            fr_knee_ry = float(split_line[12])

            rl_hip_rx = float(split_line[14])
            rl_hip_ry = float(split_line[16])
            rl_knee_ry = float(split_line[18])
            rr_hip_rx = float(split_line[20])
            rr_hip_ry = float(split_line[22])
            rr_knee_ry = float(split_line[24])

            step_leg = float(split_line[26])

            dog_ts = float(split_line[28])
            ts = float(split_line[len(split_line) -1])
            
            my_msg=datatypes.littledog_encoders(fl_hip_rx, fl_hip_ry, fl_knee_ry, fr_hip_rx,
                                                fr_hip_ry, fr_knee_ry, rl_hip_rx, rl_hip_ry,
                                                rl_knee_ry, rr_hip_rx, rr_hip_ry, rr_knee_ry, step_leg)
            mocap_encoder_readings.append(my_msg)

        if(split_line[0] == 'BODY_ENCODERS'):
            fl_hip_rx = float(split_line[2])
            fl_hip_ry = float(split_line[4])
            fl_knee_ry = float(split_line[6])
            fr_hip_rx = float(split_line[8])
            fr_hip_ry = float(split_line[10])
            fr_knee_ry = float(split_line[12])

            rl_hip_rx = float(split_line[14])
            rl_hip_ry = float(split_line[16])
            rl_knee_ry = float(split_line[18])
            rr_hip_rx = float(split_line[20])
            rr_hip_ry = float(split_line[22])
            rr_knee_ry = float(split_line[24])

            step_leg = float(split_line[26])
            
            dog_ts = float(split_line[28])
            ts = float(split_line[len(split_line) -1])

            my_msg=datatypes.littledog_encoders(fl_hip_rx, fl_hip_ry, fl_knee_ry, fr_hip_rx,
                                                fr_hip_ry, fr_knee_ry, rl_hip_rx, rl_hip_ry,
                                                rl_knee_ry, rr_hip_rx, rr_hip_ry, rr_knee_ry, step_leg)
            body_encoder_readings.append(my_msg)


        if(split_line[0] == 'IMU_BODY'):
            r = float(split_line[2])
            p = float(split_line[4])
            y = float(split_line[6][0:len(split_line[6])-2])
            vx = float(split_line[8])
            vy = float(split_line[10])
            vz = float(split_line[12])
            ax = float(split_line[14])
            ay = float(split_line[16])
            az = float(split_line[18])
            dog_ts = float(split_line[20])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.imu_reading(r,p,y,vx,vy,vz,ax,ay,az,ts,dog_ts);
            imu_readings.append(my_msg)

        if(split_line[0] == 'MOCAP_BODY'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            dog_ts = float(split_line[14])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts,dog_ts);
            cob_readings.append(my_msg)

        if(split_line[0] == 'MOCAP_FRONT_LEFT_UPPER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            front_left_upper_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_FRONT_LEFT_LOWER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            front_left_lower_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_FRONT_RIGHT_UPPER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            front_right_upper_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_FRONT_RIGHT_LOWER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            front_right_lower_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_REAR_LEFT_UPPER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            rear_left_upper_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_REAR_LEFT_LOWER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            rear_left_lower_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_REAR_RIGHT_UPPER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            rear_right_upper_leg.append(my_msg)

        if(split_line[0] == 'MOCAP_REAR_RIGHT_LOWER_LEG'):
            x = float(split_line[2])
            y = float(split_line[4])
            z = float(split_line[6][0:len(split_line[6])-2])
            r = float(split_line[8])
            p = float(split_line[10])
            yaw = float(split_line[12])
            ts = float(split_line[len(split_line) -1])
            my_msg = datatypes.body_pose(x,y,z,r,p,yaw,ts);
            rear_right_lower_leg.append(my_msg)

    retvec = [laser_readings, cob_readings, front_left_upper_leg,
              front_left_lower_leg, front_right_upper_leg, front_right_lower_leg,
              rear_left_upper_leg, rear_left_lower_leg, rear_right_upper_leg,
              rear_right_lower_leg, imu_readings, foot_readings, mocap_encoder_readings,
              body_encoder_readings]
    
    return retvec


def load_logfile(filename):
    myfile = open(filename) 
    laser_readings = []
    odometry_readings = []
    
    for line in myfile:
        split_line = line.split()


        if(split_line == []):
            continue


        #take care of front laser readings
        if(split_line[0] == 'FLASER'):
            num_readings = int(split_line[1])

            reading = []
            for i in range(num_readings):
                reading.append(float(split_line[i+2]))

            my_msg = datatypes.laser_message(float(split_line[len(split_line)-1]), reading)

            laser_readings.append(my_msg)

        #take care of robot odometry here
        if(split_line[0] == 'ODOM'):
            odometry = [float(split_line[1]), float(split_line[2]),
                        normalize_theta(float(split_line[3]))]
            my_odometry = datatypes.odometry_message(float(split_line[len(split_line)-1]), odometry)
            odometry_readings.append(my_odometry)


    return [odometry_readings, laser_readings]

def load_carmen_logfile(filename):
    myfile = open(filename) 
    front_readings = []
    rear_readings = []
    true_pos = []
    global_pos = []
    odometry_readings = []
    i=0

    thefile = myfile.readlines()
    for line in thefile:
        if(i >= len(thefile)-1):
            continue
        split_line = line.split()
        
        if(split_line == []):
            continue 
        #take care of front laser readings
        if(split_line[0] == 'ROBOTLASER1' or split_line[0]=='ROBOTLASER'):
            if(len(split_line) <= 15):
                continue

            num_readings = int(split_line[8])
            reading = []
            for i in range(num_readings):
                reading.append(float(split_line[i+9]))
            pose = split_line[len(split_line)-14:len(split_line)-11]
            
            #create them as floats
            for i in range(len(pose)):
                pose[i] = float(pose[i])

                
            timestamp = float(split_line[len(split_line)-3])
            #timestamp = float(split_line[len(split_line)-1])
            my_msg = datatypes.robot_laser_message(timestamp, pose, reading, 1)
            
            front_readings.append(my_msg)
            #take care of front laser readings
            
        if(split_line[0] == 'ROBOTLASER2'):
            print len(split_line)
            if(len(split_line) <= 180):
                continue
            
            num_readings = int(split_line[8])
            reading = []
            for i in range(num_readings):
                reading.append(float(split_line[i+9]))
            #reading.reverse()
            pose = split_line[len(split_line)-14:len(split_line)-11]
            
            #create them as floats
            for i in range(len(pose)):
                pose[i] = float(pose[i])

            
            timestamp = float(split_line[len(split_line)-3])
            my_msg = datatypes.robot_laser_message(timestamp, pose, reading, 1)
            
            rear_readings.append(my_msg)
                #take care of front laser readings
                
        if(split_line[0] == 'TRUEPOS'):

            if(len(split_line) <= 4):
                continue
            
            x = float(split_line[1])
            y = float(split_line[2])
            theta = float(split_line[3])
            timestamp = float(split_line[len(split_line)-3])
            pt = point_timestamp(x, y, theta, timestamp)
            true_pos.append(pt)
            
        if(split_line[0] == 'GLOBALPOS'):
            if(len(split_line) <= 4):
                continue
            
            x = float(split_line[1])
            y = float(split_line[2])
            theta = float(split_line[3])
            timestamp = float(split_line[len(split_line)-3])
            pt = point_timestamp(x, y, theta, timestamp)
            global_pos.append(pt)

        #take care of robot odometry here
        if(split_line[0] == 'ODOM'):
            odometry = [float(split_line[1]), float(split_line[2]),
                        normalize_theta(float(split_line[3]))]
            my_odometry = datatypes.odometry_message(float(split_line[7]), odometry)
            odometry_readings.append(my_odometry)
        
        i+=1
    
    if(len(true_pos) > 0):
        return front_readings, rear_readings, true_pos, odometry_readings
    else:
        return front_readings, rear_readings, global_pos, odometry_readings

def tklib_rotate_poses_match_pose(model_pose, measured_pose, measured_poses):
    Pts = tklib_rotate_pts_match_pose(model_pose, measured_pose, measured_poses[0:2,:])
    thetas = tklib_rotate_thetas_match_pose(model_pose, measured_pose, measured_poses[2,:])

    ret_pts = zeros([3, len(Pts[0])])*1.0
    ret_pts[0:2,:] = Pts
    ret_pts[2,:] = thetas

    return ret_pts
    

def tklib_rotate_pts_match_pose(model_pose, measured_pose, measured_pts):
    th_diff = tklib_normalize_theta(model_pose.theta - measured_pose.theta)
    R = array([[cos(th_diff), -sin(th_diff)], [sin(th_diff), cos(th_diff)]])
    new_pts = dot(R, measured_pts-array([[measured_pose.x],[measured_pose.y]]))
    new_pts += array([[model_pose.x],[model_pose.y]])
    
    return new_pts

def tklib_rotate_thetas_match_pose(model_pose, measured_pose, thetas):
    th_diff  = thetas - measured_pose.theta
    return tklib_normalize_theta_array(model_pose.theta + th_diff)
    

def test1():
    measured_pose = point(-10, -10, pi/2.0)

    R_measured = zeros(180)+1.0
    theta_measured = arange(0, pi, pi/180.0)

    X1 = R_measured*cos(theta_measured)+measured_pose.x
    Y1 = R_measured*sin(theta_measured)+measured_pose.y

    #model
    model_pose = point(10, 0, 0);
    R_model = zeros(180)+1.0
    theta_model = arange(-pi/2.0, pi/2.0, pi/180.0)

    X2 = R_model*cos(theta_model)+model_pose.x
    Y2 = R_model*sin(theta_model)+model_pose.y
    
    #rectification
    X3, Y3 = tklib_rotate_pts_match_pose(model_pose, array([X2, Y2]), measured_pose, array([X1, Y1]))
    
    plot(X1, Y1, 'r>')
    plot(X2, Y2, 'r^')
    plot(X3, Y3, 'gx')

    show()

def test2():
    measured_pose = point(-10, -10, pi/2.0)
    
    R_measured = zeros(180)+1.0
    theta_measured = arange(0, pi, pi/180.0)

    X1 = R_measured*cos(theta_measured)+measured_pose.x
    Y1 = R_measured*sin(theta_measured)+measured_pose.y

    #model
    model_pose = point(10, 0, 0);
    R_model = zeros(180)+1.0
    theta_model = arange(-pi/2.0, pi/2.0, pi/180.0)

    X2 = R_model*cos(theta_model)+model_pose.x
    Y2 = R_model*sin(theta_model)+model_pose.y
    
    #rectification
    X3, Y3 = tklib_rotate_pts_match_pose(measured_pose, array([X1, Y1]), model_pose, array([X2, Y2]))
    
    plot(X1, Y1, 'r>')
    plot(X2, Y2, 'r^')
    plot(X3, Y3, 'gx')

    show()

if __name__=="__main__":
    from pylab import plot, show
    #measured
    test1()
    #test2()
