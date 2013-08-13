from datatypes import *
from scipy import *
from scipy.linalg import eig
from sorting import quicksort
from copy import deepcopy
from gaussian import normal_sample
from kmeans import *
from nearest_neighbor import *
from random import randint
from givens_matrix import *
from carmen_util import get_euclidean_distance
from pyTklib import *

def spectral_gradient_descent(X, alpha, threshold=0.1, iterations=10000000, g_rot_init=None):
    done = False

    g_rot = None
    if(g_rot_init != None):
        
        init_thetas = g_rot_init.toThetaArry().tolist()
        init_thetas.append(0.0);
    
        #get the initial givens rotation
        g_rot = GivensRotation(len(X[0]), init_thetas)
    else:
        g_rot = GivensRotation(len(X[0]))

    #initialize the current and previous thetas
    prev_thetas = g_rot.toThetaArry()

    i = 0
    #print "***************************"
    #print "gettting number of clusters"
    while(1):
        #convert to an array
        curr_thetas = g_rot.toThetaArry()
        prev_thetas = curr_thetas

        #update the current thetas
        #print "jacobian", get_jacobian(X, g_rot)
        #print "curr_thetas", curr_thetas
        #print "thetas", curr_thetas
        J = get_jacobian(X, g_rot)
        #print "jacobian", J
        curr_thetas = curr_thetas - alpha*J
        
        #print "new_thetas", curr_thetas
        #plug it back into the given rotation
        g_rot.fromThetaArry(curr_thetas)
        

        #see if we are at our finishing condition
        #print "diff", (curr_thetas-prev_thetas)**2
        
        d = get_euclidean_distance(curr_thetas, prev_thetas)
        #print "d:", d

        if(d < threshold):
            print "threadhold broken, exiting"
            break
        
        if(i > iterations):
            print "spectral_gradient_descent did not converge"
            break

        i+=1

    return g_rot

def get_score(X, g_rot):
    #if(len(X[0])==1 or g_rot==None):
    #    X_max = amax(X, 1)
    #    return sum((X_max*X_max)*sum(X*X, 1))
    #divisor = 1.0/(sum(sqrt(X**2),1)+(10.0**(-30)))
    #X_pr = matrixmultiply(diag(divisor), X)
    
    R = g_rot.toR()
    Z = dot(X, R)
    Z_max = amax(Z, 1)

    #return (1.0/len(X[0]))*(sum((Z_max*Z_max)*sum(Z*Z, 1)))
    return sum((1.0/(Z_max*Z_max))*sum(Z*Z, 1))


def get_jacobian(X, g_rot):
    #get the A matrices
    #X = abs(X)
    As = g_rot.get_derivatives()

    #convert to a rotation matrix
    R = g_rot.toR();

    #get the current Z
    Z = dot(X, R)

    #get the maximum over Z
    Z_max = amax(Z, 1)
    I = argmax(Z, 1)
    
    #now iterate through the A[i] and get the respective
    #    theta updates
    J = []
    
    for i in range(len(As)):

        A_curr = dot(X, As[i])

        #get the first term
        #check the order in which these get applied
        T1 = sum((1.0/(Z_max*Z_max))*sum(A_curr*Z, 1))

        #pick out the maximum values given the index set
        A_max = array(list(A_curr[k,I[k]] for k in range(len(A_curr))))

        #get the second term
        T2 = sum((1.0/(Z_max*Z_max*Z_max))*A_max*sum(Z*Z, 1))

        J.append(2*(T1-T2))
        #raw_input("T2 press a key")
        
    return array(J)

        

def get_median_matrix(dist_matrix):
    median_dists = []
    for row in dist_matrix:
        stripped = get_valid_dists_array(row)
        if(len(stripped) > 0):
            median_dists.append(median(stripped))
        else:
            median_dists.append(1000)
            
    return median_dists

def get_valid_dists_array(dist_array):
    valid_dists = []
    for val in dist_array:
        if(val > 0):
            valid_dists.append(val)

    return valid_dists

#need to test this
def dists2weights_perona(Dist, alpha=1.0):
    sigma = get_median_matrix(Dist)
    W = zeros([len(Dist),len(Dist)])*1.0
    
    for i in range(len(Dist)):
        #print indices
        for j in range(len(Dist[0])):
            #distance here

            if(i == j):
                W[i,j] = 1.0
                W[j,i] = 1.0
            if(Dist[i,j] >= 0):
                val = exp(-(1.0/(1.0*sigma[j]*sigma[i]))*alpha*Dist[i,j])
                W[i,j] = val
                W[j,i] = val

    return W
    

def save_matrix(filename, mymatrix):
    print "writing matrix to -> ", filename

    myfile = open(filename, 'w')

    for row in range(len(mymatrix)):
        for column in range(len(mymatrix[row])):
            myfile.write(str(mymatrix[row][column])+" , ")
        myfile.write("\n")

    myfile.close()

    

def get_initial_clusters(num_clusters, X):
    clusters = []
    clusters.append(X[randint(0,len(X)-1)])

    for i in range(len(X)):
        guess = randint(0,len(X)-1)
        
        pt_is_okay = True
        for init_pt in clusters:
            if(sqrt(dot(X[guess]-init_pt, X[guess]-init_pt)) < 0.1):
                pt_is_okay = False
                break

        if(len(clusters)>= num_clusters):
            return clusters
        
        if(pt_is_okay):
            clusters.append(X[guess])
        

    return clusters



def weights(X,r,beta):
    W = zeros([len(X),len(X)])*1.0

    i = 0
    for pt in X:
        nearest_pts,indices,dists = kNN_g0(pt,X,r)
        for j in indices:
            #distance here
            val = exp(-beta*sqrt(dot(X[j]-pt, X[j]-pt)))
            W[i,j] = val
            W[j,i] = val
        i += 1

    return W

def weights_perona(X,r):
    sigma = get_scaling_parameters(X)
    
    W = zeros([len(X),len(X)])*1.0 
    
    i = 0
    for pt in X:
        nearest_pts, indices, dists = kNN_g0(pt,X,r)
        #print indices
        
        for j in indices:
            #distance here
            val = exp(-(1.0/(1.0*sigma[j]*sigma[i]))*dot(X[j]-pt, X[j]-pt))
            W[i,j] = val
            W[j,i] = val
        i += 1

    return W

def get_scaling_parameters(X):
    sigs = []

    i = 0
    for pt in X:
        nearest_pts, indices, dists = kNN_g0(pt,X,5)
        sigs.append(median(dists))
        i += 1
        
    return sigs

                

def get_indices(my_dists, r):

    dists = deepcopy(my_dists)
    dists.sort()
    indices = []

    for i in range(min(r, len(my_dists))):
        my_i = my_dists.index(dists[i])
        indices.append(my_i)

    return indices


def test1():
    mysum = sum(range(10))
    print mysum
    print (10*(10-1))/2.0

def test2():
    thetas = array([pi/4.0, pi/4.0, pi/4.0,pi/4.0, pi/4.0, pi/4.0])
    mygivens = thetas_to_Givens(thetas, 3)
    print mygivens

def test4():
    print "***************TEST4*******************"
    #def __init__(self, theta, i, j, n):
    g1 = GivensRotation(3, [pi/4.0, pi/4.0, pi/4.0])
    
    X1 = array([[1,0, 0],[0,1.0, 0], [0, 0, 1.0]])
    X = dot(X1, g1.toR())
    print "initial rotation"
    print g1.toR()

    print "****************"
    print "initial X"
    print X1
    print "rotated X"
    print X
    g_rot = spectral_gradient_descent(X, 10.0**-3, 10**-8, 10000)

    print "unrotated X"
    print dot(X, g_rot.toR())
    print "****************"

    print "unrotation applied"
    R = g_rot.toR()
    print R

    print "score"
    print get_score(X, g_rot)

    print "vector lengths"
    D1 = sqrt(sum(X1*X1, 1))
    D2 = sqrt(sum(X*X, 1))
    Z = dot(X, g_rot.toR())
    D3 = sqrt(sum(Z*Z, 1))
    print "initial", D1
    print "test", D2
    print "unrotated", D3
    print "***************************************"
    
def test3():
    print "***************TEST3*******************"
    #def __init__(self, theta, i, j, n):
    initR = givens_matrix(pi/4.0, 0, 1, 2);
    print initR.tostring()
    
    X1 = array([[1,0],[0,1.0], [0, 0.001]])
    X = initR.rmultiply(X1)


    print "****************"
    print "initial X"
    print X1
    print "rotated X"
    print X
    g_rot = spectral_gradient_descent(X, 10.0**-3, 10**-6, 1000)

    print "unrotated X"
    print dot(X, g_rot.toR())
    print "****************"

    print "unrotation applied"
    R = g_rot.toR()
    print R

    print "score"
    print get_score(X, g_rot)
    print "**************************************"


def test5():
    print "***************TEST4*******************"
    thetas = ones(10)*pi/4.0
    g1 = GivensRotation(5, thetas)
    X1 = array([[1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1]])*1.0
    X = dot(X1, g1.toR())
    
    print "initial rotation"
    print g1.toR()

    print "****************"
    print "initial X"
    print X1
    print "rotated X"
    print X
    g_rot = spectral_gradient_descent(X, 10.0**-2, 10**-8, 10000)

    print "unrotated X"
    print dot(X, g_rot.toR())
    print "****************"

    print "unrotation applied"
    R = g_rot.toR()
    print R

    print "score"
    print get_score(X, g_rot)

    print "vector lengths"
    D1 = sqrt(sum(X1*X1, 1))
    D2 = sqrt(sum(X*X, 1))
    Z = dot(X, g_rot.toR())
    D3 = sqrt(sum(Z*Z, 1))
    print "initial", D1
    print "test", D2
    print "unrotated", D3
    print "***************************************"

if __name__ == "__main__":
    from pylab import *

    #test3()
    #test4()
    test5()
