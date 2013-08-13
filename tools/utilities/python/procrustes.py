from carmen_util import *
from scipy.linalg import svd, det
from scipy import *
from pylab import *
from nearest_neighbor import *
from scipy_addons import *


#Written by Thomas Kollar 6/20/06
#function procrustes_rotate_translate_scale
#
#parameters: A, B
#returns: sse, R, t, c
#
#parameters:
# A, B are an m x n matrix, where m is the dimensionality of the space
# and n is the number of data points
#
# A is the target data points and B are the source
#
#returns:
#
#  sse -- the error after the optimization
#  R -- the rotation matrix
#  t -- the translation
#  c -- the scaling factor
#
#  cRB + t is approximately minimizes B's distance to A
def procrustesSVD(measured, model):
    u_model = transpose([sum(model, 1)])/(1.0*len(model[0]))
    u_measured = transpose([sum(measured, 1)])/(1.0*len(measured[0]))
    var_measured = sum(sum((measured - u_measured)**2, 1))/(1.0*len(measured[0]))
    U, D, V = svd(dot(model-u_model, transpose(measured-u_measured))/len(measured[0]))
    det_U = det(U)
    det_V = det(V)

    S = None

    if(round(det_U*det_V) == 1.0):
        S = diag(ones(len(U[0])))
    elif(round(det_U*det_V) == -1.0):
        S = diag(ones(len(U[0])))
        S[len(S[0])-1,len(S[0])-1] = -1
    else:
        print "error in sse_procrustes"
        return None

    R = dot(dot(U, S), V)
    #c = (1.0/var_measured)*trace(dot(diag(D),S))
    t = u_model - dot(R, u_measured)

    #sse = sqrt(sum(sum((model-(dot(R, measured)+t))**2)))
    sse = sqrt(sum(sum((model-(dot(R, measured)+t))**2)))
    return sse, R, t


def icp(measured_points, model_points, tau, maxsse):
    prev_points = array(measured_points)
    model_points = model_points

    prevsse = sys.maxint
    currsse = -sys.maxint

    while(abs(prevsse - currsse) > tau and abs(currsse)>maxsse):
        nns = NNs(prev_points, model_points)
        #print "****************"
        sse, R, t = procrustesSVD(prev_points, nns)
        prev_points = dot(R, prev_points) + t

        if(currsse == -sys.maxint):
            currsse = sse
        else:
            prevsse = currsse
            currsse = sse

        #print "curr sse-->", currsse
    return prev_points, currsse



def test3():
    th1 = arange(0.0, pi, 0.1)
    th2 = arange(pi/2.0,pi+pi/2.0, 0.1)
    #th1 = arange(0,pi, 0.05)
    #th2 = arange(pi/2.0,pi+pi/2.0, 0.05)

    X1 = cos(th1)
    Y1 = sin(th1)

    X2 = cos(th2)
    Y2 = sin(th2)
    #Z = zeros(len(X2))*1.0


    measured_pts = transpose(zip(X1,Y1))
    #sse, R, t, q = procrustes3D(measured_pts, transpose(zip(X2,Y2,Z)))
    sse, R, t = procrustesSVD(measured_pts, transpose(zip(X2,Y2)))


    print "sse", sse
    print "R", R
    print "t", t

    pts = dot(R, measured_pts) + t

    plot(X2,Y2, 'rx')

    X, Y = pts
    plot(X, Y, 'g<')

    show()

def test4():
    th1 = arange(0,pi, 0.05)
    th2 = arange(pi/2.0,pi+pi/2.0, 0.05)

    X1 = cos(th1)
    Y1 = sin(th1)

    X2 = cos(th2)
    Y2 = sin(th2)
    Z = zeros(len(X2))*1.0

    pts = icp(transpose(zip(X1,Y1,Z)), transpose(zip(X2,Y2,Z)), 0.001, 0.001)
    #print len(pts), len(pts[0])
    #plot(X1, Y1, 'ro')
    plot(X2,Y2, 'rx')

    X, Y, Z = pts
    plot(X, Y, 'g<')

    show()


def test5():
    th1 = arange(0,pi, 0.05)
    th2 = arange(pi/2.0,pi+pi/2.0, 0.05)

    X1 = cos(th1)
    Y1 = sin(th1)

    X2 = cos(th2)
    Y2 = sin(th2)
    Z = zeros(len(X2))*1.0

    first = transpose(zip(X1,Y1,Z))
    second = transpose(zip(X2,Y2,Z))

    first = matrix_concatenate(first, transpose(zip(X1,Y1,Z+1.0)))
    second = matrix_concatenate(second, transpose(zip(X2,Y2,Z+1.0)))

    pts = icp(first, second, 0.001, 0.001)
    #print len(pts), len(pts[0])
    #plot(X1, Y1, 'ro')
    plot(X2,Y2, 'rx')

    X, Y, Z = pts
    plot(X, Y, 'g<')

    show()


def test8():
    t1 = arange(-1,1,0.5);
    t2 = ones(len(t1))*1.0

    Z = zeros(len(t2))*1.0
    #X_top = array([t1+0.1*rand(len(t1)),t2+0.1*rand(len(t1)),Z])
    #X_left = array([-1.0*t2+0.1*rand(len(t1)), t1+0.1*rand(len(t1)),Z])
    #X_right = array([t2+0.1*rand(len(t1)), t1+0.1*rand(len(t1)),Z])
    #X_bottom = array([t1,-1.0*t2,Z])

    X_top = array([t1,t2])
    X_left = array([-1.0*t2, t1])
    X_right = array([t2, t1])
    X_bottom = array([t1,-1.0*t2])

    X_top_pr = array([t1,t2+1.0])
    X_left_pr = array([-1.0*t2, t1])
    X_right_pr = array([t2, t1])
    X_bottom_pr = array([t1,-1.0*t2])

    first = matrix_concatenate(X_right, X_top)
    second = matrix_concatenate(X_top, X_left)

    sse, R, t = procrustesSVD(first, second)
    pts = dot(R, first) + t

    plot(second[0],second[1], 'rx')
    X, Y = pts
    plot(X, Y, 'g<')

    show()

def test9():
    t1 = arange(-1,1,0.5);

    t2 = ones(len(t1))*1.0


    Z = zeros(len(t2))*1.0#+rand(len(t2))
    X_top = array([t1+0.0001*rand(len(t1)),t2+0.0001*rand(len(t1)),Z])
    X_left = array([-1.0*t2+0.0001*rand(len(t1)), t1+0.0001*rand(len(t1)),Z])
    X_right = array([t2+0.0001*rand(len(t1)), t1+0.0001*rand(len(t1)),Z])
    X_bottom = array([t1,-1.0*t2,Z])

    #X_top = array([t1,t2,Z])
    #X_left = array([-1.0*t2, t1,Z])
    #X_right = array([t2, t1,Z])
    #X_bottom = array([t1,-1.0*t2,Z])

    first = matrix_concatenate(X_top, X_right)
    second = matrix_concatenate(matrix_concatenate(X_top, X_right), X_bottom)

    pts = icp(first,second, 0.0001, 0.1)

    #plot(X1, Y1, 'ro')

    plot(second[0],second[1], 'rx')

    X, Y, Z = pts
    plot(X, Y, 'g<')

    show()



if(__name__ == "__main__"):

    #test3()
    #test4()
    #test5()
    test8()
    #test9()


    pass
