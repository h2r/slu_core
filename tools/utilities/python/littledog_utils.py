from math import sin, cos, pi
from scipy import *
from carmen_util import *

try:
    import pymat
except:
    print ">> COULD NOT IMPORT PYMAT... continuing"

s=None

def motion_model_alec(feet_prev, body_prev, encoders_curr, swing_leg):
    #change the rotation matrix for roll for littledog
    #select the non-swing feet
    [x_body,R_body,valid] = kin_body_qa(encoders_curr,
                                        feet_prev,swing_leg)

    del_x = x_body-body_prev[0:3]
    
    return del_x, R_body


def motion_model(encoders_prev, encoders_curr, imu_prev, imu_curr, swing_leg):
    #compute the feet positions in t and then t+1
    fprel_prev = footpos(encoders_prev)
    fprel_curr = footpos(encoders_curr)
    
    #rotate according to the first position into the global frame
    Rb_prev = q2Rb(imu_prev.roll, imu_prev.pitch, imu_prev.yaw)
    Rb_curr = q2Rb(imu_curr.roll, imu_curr.pitch, imu_curr.yaw)

    #foot positions in the global frame
    fp_prime_prev = matrixmultiply(Rb_prev,fprel_prev)
    fp_prime_curr = matrixmultiply(Rb_curr,fprel_curr)
    
    #get the displacement
    del_x  = fp_prime_prev - fp_prime_curr

    ret_disp = []
    for i in range(4):
        #swing legs are 1-4, so add 1 to the index
        if(not i+1 == swing_leg):
            ret_disp.append(del_x[:,i])
    
    #print "del_x", array(ret_disp)
    
    return ret_disp

def rotate_x_ld(pts, theta):
    R = get_rotation_matrix_x_ld(theta)
    return transpose(matrixmultiply(R, transpose(pts)))

def get_rotation_matrix_x_ld(theta):
    return array([[1,0,0], [0, cos(theta),-sin(theta)], [0, sin(theta), cos(theta)]])


def R_cob_to_global(rot_pts, roll, pitch, yaw, t):
    #rotate out the dog's roll, pitch and yaw
    rot_pts = rotate_z(rot_pts,    yaw)
    rot_pts = rotate_y(rot_pts,    pitch)
    rot_pts = rotate_x_ld(rot_pts, roll)

    
    #add the offset
    rot_pts = rot_pts + array(t)
    #array([pose_cob.x, pose_cob.y, -pose_cob.z])

    return rot_pts

def get_laser_reading_robot_frame_littledog(reading, pose_cob, laser_angle):
    pts = []
    
    #finish get the laser scans raw
    #reading.reverse()
    for i in range(len(reading)):
        theta = i*(360.0/1024.0)*(pi/180.0) - (3*pi/4.0)

        #if(theta < pi/4.0 and theta > -pi/4.0):
        #if(reading[i] < 1.0):
        pts.append([reading[i]*math.cos(theta),reading[i]*math.sin(theta), 0])

    laser_height_over_cob=0.254
    
    #dunno if this is exactly right
    laser_y_offset = 0.0254
    rot_pts = pts
    #rotate out the pitch of the dog
    rot_pts = rotate_y(rot_pts, laser_angle)

    
    #subtract out so that we are at the center of the robot body
    rot_pts = rot_pts+array([0.0, laser_y_offset, laser_height_over_cob])

    rot_pts = R_cob_to_global(rot_pts, pose_cob.roll, pose_cob.pitch, pose_cob.yaw,
                              array([pose_cob.x, pose_cob.y, pose_cob.z]))
    
    X = rot_pts[:,0]
    Y = rot_pts[:,1]
    Z = rot_pts[:,2]
    #print Z
    
    return X,Y,Z



def init_matlab():
    global s
    if(s == None):
        s = pymat.open()
        pymat.eval(s, 'init_root_path')
        pymat.eval(s, 'ld_parameters')

def get_matlab_session():
    global s

    return s

    
#set the swing leg to None on the input
#swing leg is 1-4
def kin_body_qa(encoder_angles, x_st, swing_leg):
    global s
    init_matlab()
    
    x_st = transpose(x_st).tolist()
    x_st.pop(swing_leg-1)
    x_st = transpose(x_st)
    
    enc_ary = encoder_angles.toarray()

    pymat.put(s, 'enc_ary', array(enc_ary))
    pymat.put(s, 'x_st', array(x_st))
    pymat.put(s, 'swing_leg', [swing_leg])
    pymat.eval(s, 'swing_leg=swing_leg(1)')

    pymat.eval(s, '[x_body, R_body, valid] = kin_body_qa(enc_ary, x_st, swing_leg)')
    x_body =  pymat.get(s, 'x_body')
    R_body =  pymat.get(s, 'R_body')
    valid  =  pymat.get(s, 'valid')

    return x_body, R_body, valid


def q2Rb(r, p, y):
    global s
    init_matlab()
        
    pymat.put(s, 'R_glob', array([r,p,y]))
    pymat.eval(s, 'Rb = q2Rb(R_glob)')
    Rb = pymat.get(s, 'Rb')

    return Rb


def Rb2q(Rb):
    global s
    init_matlab()
        
    pymat.put(s, 'Rb', array(Rb))
    pymat.eval(s, 'q = Rb2q(Rb)')
    q = pymat.get(s, 'q')

    return q

def footpos(encoders):
    global s
    init_matlab()
    
    arry = encoders.toarray()
    pymat.put(s, 'encoders', arry)
    pymat.eval(s, 'encoders')
    pymat.eval(s, 'fp = footpos(encoders)')
    feet_pos_rel = pymat.get(s, 'fp')

    return feet_pos_rel

#q is the state vector for the whole dog
#xbody is the relative coordinates of the dog
def xrel2xabs(q, xbody):
    global s
    init_matlab()
    
    pymat.put(s, 'q', array(q))
    pymat.put(s, 'xbody', array(xbody))
    pymat.eval(s, 'x_curr = xrel2xabs(q, xbody)')
    x_curr = pymat.get(s, 'x_curr')

    return x_curr


