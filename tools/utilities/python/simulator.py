from datatypes import point
from EKF2D_datatypes import *
from EKF2D_utils import *
from pylab import *
from gaussian import *
from copy import *
from scipy import *
from carmen_maptools import *
from carmen_util import get_euclidean_distance
#from pyTklib import gridmapping_simulator_ray_trace


class tklib_map:
    def __init__(self, start_pose, motion_noise_model):
        self.true_pose = deepcopy(start_pose)
        self.corrupted_pose = deepcopy(start_pose)
        self.noise_model = motion_noise_model


    def get_true_pose(self):
        return self.true_pose

    
    def get_pose(self):
        return self.corrupted_pose
    
    def simulate_motion(self, tv, rv, dt):
        dth1 = rv*(dt/2.0)
        dr = tv*dt
        dth2 = rv*(dt/2.0)
        
        ds = self.noise_model.slip_noise_model.getmean(tv, rv)

        #use dth1 since otherwise we are doubling the error
        N = self.noise_model.getvariance(dr, dth1)
        U = self.noise_model.getmean(dr, dth1)
        #print "N->", N
        dr_hat, dth_hat, dslip_hat = normal_sampleC(N, U)

        #use the motion model of parr to simulate the true motion
        #of the robot
        x_true = self.true_pose.x + (dr_hat)*cos(self.true_pose.theta + dth_hat) + dslip_hat*cos(self.true_pose.theta + dth_hat + pi/2.0)
        y_true = self.true_pose.y + (dr_hat)*sin(self.true_pose.theta + dth_hat) + dslip_hat*sin(self.true_pose.theta + dth_hat + pi/2.0)
        th_true = normalize_theta(self.true_pose.theta + 2.0*dth_hat)

        self.true_pose.x = x_true
        self.true_pose.y = y_true
        self.true_pose.theta = th_true

        #compute the corrupted odometry
        x_pr = self.corrupted_pose.x + (dr)*cos(self.corrupted_pose.theta + dth1) + ds*cos(self.corrupted_pose.theta + dth1 + pi/2.0)
        y_pr = self.corrupted_pose.y + (dr)*sin(self.corrupted_pose.theta + dth1) + ds*sin(self.corrupted_pose.theta + dth1 + pi/2.0)
        th_pr = normalize_theta(self.corrupted_pose.theta + rv*dt)

        self.corrupted_pose.x = x_pr
        self.corrupted_pose.y = y_pr
        self.corrupted_pose.theta = th_pr
        return point(x_pr, y_pr, th_pr)



#features should be 3xN dimensional
class sim_hurdle_map(tklib_map):
    def __init__(self, start_pose, features, motion_noise_model, observation_noise_model):
        #self.noise_model = motion_noise_model
        #self.start_pose = deepcopy(start_pose)
        self.observation_noise_model = observation_noise_model
        self.features = array(features)
        tklib_map.__init__(self, start_pose, motion_noise_model)

    def simulate_features(self, max_dist, min_th, max_th):
        N = self.observation_noise_model.getvariance()
        
        D, Phi = globalXY_to_r_theta(self.true_pose, self.features[0:len(self.features)-1, 0:len(self.features[0])])
        Signature = self.features[2,:]

        retD = []
        retPhi = []
        retSignature = []
        for i in range(len(D)):
            if(D[i] < max_dist and Phi[i] <= max_th and Phi[i] >= min_th):
                err_r, err_th , err_sig = normal_sampleC(N, [0,0,0])
                retD.append(D[i] + err_r)
                retPhi.append(Phi[i] + err_th)
                retSignature.append(Signature[i] + err_sig)
        
        retPhi = normalize_theta_array(retPhi)    
        return array([retD, retPhi, retSignature])
             



        
'''class sim_carmen_map(tklib_map, carmen_map):
    def __init__(self, start_pose, motion_noise_model,
                 x_size=None, y_size=None, resolution=None, filename=None):
                 
        carmen_map.__init__(self, x_size, y_size, resolution)
        
        if(not filename == None):
            self.load_carmen_map(filename)
                    
        tklib_map.__init__(self, start_pose, motion_noise_model)


    #assume that the robot has only a 180 degree
    #sensor suite
    def simulate_measurements(self, pose=None):
        if(pose == None):
            pose = self.true_pose
            
        readings = list(self.ray_trace(pose.x, pose.y, pose.theta+a) for a in arange(-pi/2.0, pi/2.0, pi/180.0))
        return readings



    #def ray_trace_array(self, startx, starty, thetas):
    #return list(self.ray_trace(startx, starty, theta) for theta in thetas)

    def ray_trace(self, startx, starty, start_theta):
        x_step = cos(start_theta)*self.resolution
        y_step = sin(start_theta)*self.resolution
        
        j=0; 
        while(1):
            ix, iy = self.xy_to_ind(startx+j*x_step, starty+j*y_step)
            
            if(ix < 0 or iy < 0):
                break

            if(ix >= self.x_size/(1.0*self.resolution) or iy >= self.y_size/(1.0*self.resolution)):
                break

            #we have hit something
            if(self.data[ix,iy] >= rand()):
                d = get_euclidean_distance([startx, starty], [startx+j*x_step, starty+j*y_step])
                return d

            j+=1
                
        
        return [[-1,-1],30]'''


def generate_circle_features(x_off, y_off, r):
    theta = arange(0,2*pi,0.3)

    X = r*cos(theta) + x_off
    Y = r*sin(theta) + y_off
    S = range(len(theta))
    
    return X, Y, S

def generate_square_features(x_off, y_off, r):
    X = [-1.0, -1.0, 1.0, 1.0]
    Y = [-1.0, 1.0, 1.0, -1.0]
    S = array([0, 1, 2, 3])
    
    X = array(X)*r+x_off
    Y = array(Y)*r+y_off
    
    return X, Y, S


def test1():
    ion()
    start_pose = point(0,0,0);
    
    #create the noise models
    tv_nm = motion_noise(1.0, 0, 0.001, 0.0)
    rv_nm = motion_noise(0, 1.0, 0.0, 0.001)
    slip_nm = motion_noise(0, 0, 0.01, 0.0)
    
    #make the papa of noise models here 
    nm =  motion_noise_model_slip(tv_nm, rv_nm, slip_nm)
    onm = observation_noise_model(0.1, 0.05, 0.1)
    
    #make the simulator
    sim = sim_hurdle_map(start_pose, [], nm, onm)
    
    #test motion simulator
    true_pos,  = plot([], [], 'go', markersize=5)
    true_ang,  = plot([], [], linewidth=3)
    meas_pos,  = plot([], [], 'ro', markersize=5)
    meas_ang,  = plot([], [], linewidth=3)
    
    for i in range(1000):
        axis([-5, 5, -5, 5])
        #sim.simulate_motion(0.5, 0.05, 0.1)
        sim.simulate_motion(0.5, 0.3, 0.1)

        #set true pose
        true_pos.set_data([sim.true_pose.x] , [sim.true_pose.y])
        true_ang.set_data([sim.true_pose.x, sim.true_pose.x + 0.2*cos(sim.true_pose.theta)] ,
                          [sim.true_pose.y, sim.true_pose.y + 0.2*sin(sim.true_pose.theta)])

        #set measured pose
        meas_pos.set_data([sim.corrupted_pose.x] , [sim.corrupted_pose.y])
        meas_ang.set_data([sim.corrupted_pose.x, sim.corrupted_pose.x + 0.2*cos(sim.corrupted_pose.theta)] ,
                          [sim.corrupted_pose.y, sim.corrupted_pose.y + 0.2*sin(sim.corrupted_pose.theta)])
        draw()
    show()


def test2():
    ion()
    start_pose = point(0,0,0);
    
    #create the noise models
    tv_nm = motion_noise(1.0, 0, 0.1, 0.0)
    rv_nm = motion_noise(0, 1.0, 0.0, 0.1)
    slip_nm = motion_noise(0, 0, 0.0001, 0.0)
    
    #make the papa of noise models here 
    nm =  motion_noise_model_slip(tv_nm, rv_nm, slip_nm)
    onm = observation_noise_model(0.01, 0.01, 0.1)

    #generate the features
    myfeat = generate_circle_features(0.0, 0.0, 1.0) 

    #make the simulator
    sim = sim_hurdle_map(start_pose, myfeat, nm, onm)
    
    #test motion simulator
    true_pos,  = plot([], [], 'go', markersize=10)
    true_ang,  = plot([], [], linewidth=3)
    meas_pos,  = plot([], [], 'ro', markersize=10)
    meas_ang,  = plot([], [], linewidth=3)

    features_plt,  = plot([], [], 'mx', markersize=5)
    
    for i in range(1000):
        sim.simulate_motion(0.5, 0.3, 0.1)
        
        
        axis([-3, 3, -3, 3])
        #set true pose
        true_pos.set_data([sim.true_pose.x] , [sim.true_pose.y])
        true_ang.set_data([sim.true_pose.x, sim.true_pose.x + 0.2*cos(sim.true_pose.theta)] ,
                          [sim.true_pose.y, sim.true_pose.y + 0.2*sin(sim.true_pose.theta)])
        
        #set measured pose
        meas_pos.set_data([sim.corrupted_pose.x] , [sim.corrupted_pose.y])
        meas_ang.set_data([sim.corrupted_pose.x, sim.corrupted_pose.x + 0.2*cos(sim.corrupted_pose.theta)] ,
                          [sim.corrupted_pose.y, sim.corrupted_pose.y + 0.2*sin(sim.corrupted_pose.theta)])

        R, Phi, Sig = sim.simulate_features(10.0, -pi/2.0, pi/2.0)
        
        X, Y = measurement_to_global(R, Phi, sim.corrupted_pose)
        features_plt.set_data(X, Y)
        draw()
    show()


def test3():
    #create the noise models
    tv_nm = motion_noise(1.0, 0, 0.1, 0.0)
    rv_nm = motion_noise(0, 1.0, 0.0, 0.1)
    slip_nm = motion_noise(0, 0, 0.0001, 0.0)
    
    #make the papa of noise models here 
    nm =  motion_noise_model_slip(tv_nm, rv_nm, slip_nm)
    
    myogm = sim_carmen_map(point(3,3,0), nm,
                           filename="/home/tkollar/installs/carmen/data/thickwean.map")
                           #filename="/home/tkollar/local/tklib/tools/trajopt/data/maps/hurdles.cmf.gz")
    
    myogm.plot()
    show()

def test4():
    #create the noise models
    tv_nm = motion_noise(0.0001, 0, 0.001, 0.0)
    rv_nm = motion_noise(0, 0.0001, 0.0, 0.001)
    slip_nm = motion_noise(0, 0, 0.0001, 0.0)
    
    #make the papa of noise models here 
    nm =  motion_noise_model_slip(tv_nm, rv_nm, slip_nm)
    ion()
    mysim = sim_carmen_map(point(3,3,0), nm,
                           filename="/home/tkollar/local/tklib/tools/trajopt/data/maps/hurdles.cmf.gz")
    mysim.plot()

    for i in range(180):
        res = mysim.simulate_measurements()
        print res
        #print res
        #raw_input()
        X, Y = rtheta_to_xy(mysim.get_pose(), res)
        
        plot(X, Y, 'bo')
        
    show()


if __name__ == "__main__":
    test3()

