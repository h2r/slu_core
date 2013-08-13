from scipy import *
from pylab import *
import sys
import math
from datatypes import point
from carmen_util import *

#FINISH HERE TOMORROW
class ActionsPoseToPoint:
    def __init__(self, start_pose, end_pt, numActions, th_inc):
        self.start_pose = start_pose
        self.end_pt = end_pt
        self.numActions = numActions
        self.th_inc = th_inc
        self.theta_dest = arange(0, 2*pi, th_inc);

        if(len(self.theta_dest) > self.numActions):
            print "************************"
            print "ActionsPoseToPoint: resolution of theta is too small for given number of actions"
            sys.exit(0);

    def getAction(self, a):
        if(a >= self.numActions or a < 0):
            print "ActionsPoseToPoint: action out of range ->", a
            sys.exit(0)

        numsubactions = ceil(self.numActions/(1.0*len(self.theta_dest)))
        sub_action = mod(a, numsubactions)
        super_action = (a - mod(a, numsubactions))/(numsubactions*1.0)

        end_pose = point(self.end_pt[0], self.end_pt[1],
                         self.theta_dest[int(super_action)] + self.start_pose.theta)
        myactions = ActionsPoseToPose(self.start_pose, end_pose, numsubactions)
        return myactions.getAction(int(sub_action))



#HERE WE ASSUME THAT ACTIONS ARE IN THE RANGE 0 TO (NUMACTIONS-1)
class ActionsPoseToPose:
    def __init__(self, start_pose, end_pose, numActions):
        self.start_pose = start_pose
        self.end_pose = end_pose
        self.numActions = numActions
        self.distance = self.start_pose.distance(self.end_pose)

        #internal variable
        self.scaling_factor = 10.0
        
    def getAction(self, a):
        if(a<0 or a>self.numActions-1):
            print "ActionsPoseToPose.py: No such action available"
            sys.exit(0);


        st_mag, end_mag = self.getActionParameters(a)
        return Spline(self.start_pose, self.end_pose, st_mag, end_mag)
    
    #this will range from 1 to d
    #where d is the distance from the current location
    def getActionParameters(self, a):
        #assuming that actions are in the range 0 to a-1
        #here we convert to 1 to a
        a = a+1
        inc = (self.distance/self.numActions)*self.scaling_factor
        start_magnitude = a*(inc)
        end_magnitude = a*(inc)
        
        return start_magnitude, end_magnitude


class Spline:
    def __init__(self, start_pose, end_pose, start_magnitude, end_magnitude):
        self.x0 = start_pose.x
        self.y0 = start_pose.y
        
        self.x1 = end_pose.x
        self.y1 = end_pose.y

        self.start_theta = start_pose.theta
        self.end_theta = end_pose.theta

        self.Dx0, self.Dy0 = self.getDerivativeNormalized(self.start_theta)
        self.Dx0, self.Dy0 = [start_magnitude*self.Dx0, start_magnitude*self.Dy0]
        
        self.Dx1, self.Dy1 = self.getDerivativeNormalized(self.end_theta)
        self.Dx1, self.Dy1 = [end_magnitude*self.Dx1, end_magnitude*self.Dy1]
        
        self.al = 0
        self.start_magnitude = start_magnitude
        self.end_magnitude = end_magnitude
        self.setArcLength()

    def curvature(self):
        curv = 0;
        X, Y = self.getVals(arange(0.0,1.0, 0.05))
        v1 = [Y[1]-Y[0], X[1]-X[0]]
        for i in range(2, len(X)):
            v2 = [Y[i]-Y[i-1], X[i]-X[i-1]]
            v1_len = sqrt(dot(v1, v1))
            v2_len = sqrt(dot(v2, v2))
            
            myarg = dot(v1, v2)/(v1_len*v2_len)
            if(myarg > 1.0):
                myarg=1.0;
            th_i = math.acos(myarg)
            curv += abs(th_i)
            v1 = v2

        return curv

    def get_start_pose(self):
        return point(self.x0, self.y0, self.start_theta);

    def get_end_pose(self):
        return point(self.x1, self.y1, self.end_theta);


    def toCtype(self):
        retspl = SplineC([self.x0, self.y0, self.start_theta],
                         [self.x1, self.y1, self.end_theta],
                         self.start_magnitude, self.end_magnitude);
        
        return retspl;


    def getDerivativeNormalized(self, theta):
        return [cos(theta), sin(theta)]

    def getY(self, y0, y1, Dy0, Dy1, t):
        a0 = y0
        b0 = Dy0
        c0 = 3*(y1 - y0) - 2*Dy0 - Dy1
        d0 = 2*(y0 - y1) + Dy0 + Dy1

        return a0 + b0*t + c0*(t**2) + d0*(t**3)

    def getVals(self, t):
        X = self.getY(self.x0, self.x1, self.Dx0, self.Dx1, t)
        Y = self.getY(self.y0, self.y1, self.Dy0, self.Dy1, t)
        return [X, Y]

    #this velocity is in distance per 1 time unit
    def getTimeIncrement(self, velocity):
        al,accuracy = self.getArcLength()
        return 0.3 / (al / (velocity*1.0))

    def derivative(self, t):
        ax, bx, cx, dx = self.getCoefX();
        ay, by, cy, dy = self.getCoefY();
        x = (3*ax*(t**2) + 2*bx*t + cx)
        y = (3*ay*(t**2) + 2*by*t + cy)
        theta = math.atan2(y,x)
        return [theta,x,y]

    #gets the arc length of the spline
    def setArcLength(self):
        self.al = integrate.quad(self.cPr, 0, 1)
        
    def getArcLength(self):
        return self.al

    def cPr(self, t):
        ax, bx, cx, dx = self.getCoefX();
        ay, by, cy, dy = self.getCoefY();
        return ((3*ax*(t**2) + 2*bx*t + cx)**2 + (3*ay*t**2 + 2*by*t + cy)**2)**(0.5)


    #This is specific to a polynomial of degree 3
    def getPerpendicularDistances(self, rX, rY):
        ax, bx, cx, dx = self.getCoefX();
        ay, by, cy, dy = self.getCoefY();

        a = -cx*dx -cy*dy + cx*rX + cy*rY
        b = -cx**2 - cy**2 - 2*bx*dx - 2*by*dy + 2*bx*rX + 2*by*rY
        c = -3*bx*cx - 3*by*cy - 3*ax*dx - 3*ay*dy + 3*ax*rX + 3*ay*rY
        d = -2*(bx**2) - 2*(by**2)  - 4*ax*cx - 4*ay*cy;
        e = -5*ax*bx - 5*ay*by
        f = -3*(ax**2) - 3*(ay**2)

        myroots = roots([f,e,d,c,b,a])
        
        return myroots

    #This is specific to a polynomial of degree 3
    def getClosestPerpDistance(self, rX, rY, Dx1, Dy1, t):
        myroots, myvals = self.getPerpendicularDistances(rX, rY, Dx1, Dy1)

        minDist = sys.maxint
        minindex = None
        for i in range(len(myvals[0])):
            a = complex(myvals[0][i])
            b = complex(myvals[1][i])
            
            dist = self.euclidDistanceComp(a, b, complex(rX), complex(rY))
            if((dist < minDist) and (complex(myroots[i]).real <= 1) and (complex(myroots[i]).real >= 0)):
                minDist = dist
                minindex = i

        if(minindex == None):
            print "Error, no valid closest distance\n"
            return [None, None] #[1, [self.x1, self.y1]]
        
        return [myroots[minindex], [myvals[0][minindex], myvals[1][minindex]]]

    def euclidDistanceComp(self, x1, y1, x2, y2):
        return sqrt((x1.real - x2.real)**2 + (y1.real - y2.real)**2)

    def getCoefX(self):
        return self.getCoef(self.x0, self.x1, self.Dx0, self.Dx1)

    def getCoefY(self):
        return self.getCoef(self.y0, self.y1, self.Dy0, self.Dy1)
    
    def getCoef(self, y0, y1, Dy0, Dy1):
        a0 = y0
        b0 = Dy0
        c0 = 3*(y1 - y0) - 2*Dy0 - Dy1
        d0 = 2*(y0 - y1) + Dy0 + Dy1
        
        return [d0, c0, b0, a0]
    
    def atDestination(self, curr_pose, epsilon):
        dist = curr_pose.distance(point(self.x1, self.y1))
        if(dist < epsilon):
            return True
        return False

def test1():
    mystart = point(0, 0, 0);
    myend = point(10, 10, pi/4.0);
    myrange = arange(0,1,0.01);

    ion()
    for i in range(100):
        myspline = Spline(mystart, myend, i, i);
        X, Y = myspline.getVals(myrange);
        plot(X, Y);
        draw();

    show()

def test2():
    mystart = point(0, 0, 0);
    myend = point(100, 100, pi/2.0);
    myrange = arange(0,1,0.01);

    ion()
    myacts = ActionsPoseToPose(mystart, myend, 10);
    for i in range(10):
        myspline = myacts.getAction(i);
        X, Y = myspline.getVals(myrange);
        plot(X, Y);
        draw()

    show()
ion()
def test3():
    mystart = point(0, 0, 0);
    myend = point(100, 100, pi/2.0);
    myrange = arange(0,1.01,0.01);

    myacts = ActionsPoseToPoint(mystart, [2, 0], 100, 2*pi/4.0);
    #myacts = ActionsPoseToPoint(mystart, [1,1], 50, pi/4.0)
    plot([mystart.x], [mystart.y], 'go', markersize=15);
    plot([mystart.x, 0.07*cos(mystart.theta)],
         [mystart.y, 0.07*sin(mystart.theta)], 'r', linewidth=3);

    X1, Y1 = [], []
    plt, = plot([], []);

    for i in range(100):

        myspline = myacts.getAction(i);
        X, Y = myspline.getVals(myrange);
        #X1.append(X); Y1.append(Y);
        plot(X,Y)
        #plt.set_data(X1,Y1)
        axis([-0.3, 2.1, -1.2, 1.2])
        draw()
        #print "saving -> video/splines"+num_as_str(i)+".png"
        #savefig("video/splines"+num_as_str(i)+".png")

    title("Action Space")
    #savefig("data/action_space.eps")
    show()



ion()
def test4():
    mystart = point(0, 0, 0);
    myend = point(100, 100, pi/2.0);
    myrange = arange(0,1.01,0.01);

    myacts = ActionsPoseToPoint(mystart, [2, 0], 100, 2*pi/4.0);
    #myacts = ActionsPoseToPoint(mystart, [1,1], 50, pi/4.0)
    plot([mystart.x], [mystart.y], 'go', markersize=15);
    plot([mystart.x, 0.07*cos(mystart.theta)],
         [mystart.y, 0.07*sin(mystart.theta)], 'r', linewidth=3);

    X1, Y1 = [], []
    plt, = plot([], []);

    for i in range(100):

        myspline = myacts.getAction(i);
        X, Y = myspline.getVals(myrange);
        print "curvature", myspline.curvature()
        #X1.append(X); Y1.append(Y);
        plot(X,Y)
        #plt.set_data(X1,Y1)
        axis([-0.3, 2.1, -1.2, 1.2])
        draw()
        raw_input()
        #print "saving -> video/splines"+num_as_str(i)+".png"
        #savefig("video/splines"+num_as_str(i)+".png")

    title("Action Space")
    #savefig("data/action_space.eps")
    show()


if __name__ == "__main__":
    test4()
    
