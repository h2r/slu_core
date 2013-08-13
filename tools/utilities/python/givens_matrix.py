import sys
from scipy import dot, cos, sin, zeros, array, pi, diag
from scipy import ones
from copy import *
from pyTklib import *

class GivensRotation:
    def __init__(self, k, thetas=None):
        self.k = k
        self.thetas = zeros([k,k])*1.0

        if(not thetas == None):
            thetas = tklib_normalize_theta_array(thetas);
            self.fromThetaArry(thetas);

    def toThetaArry(self):
        retarry = zeros(self.num_givens())
        n = 0
        
        for i in range(len(self.thetas)):
            for j in range(i+1,len(self.thetas)):
                retarry[n]=self.thetas[i,j]
                n+=1
        return retarry
    
    def fromThetaArry(self, thetas):
        if(not len(thetas) == self.num_givens()):
            raise IllegalArgumentError(thetas, "k is not the right size");

        n=0
        thetas = tklib_normalize_theta_array(thetas);
        for i in range(len(self.thetas)):
            for j in range(i+1, len(self.thetas)):
                self.thetas[i,j] = thetas[n]
                n+=1

    def get_value(self, i, j):
        return self.thetas[i,j]

    def set_value(self, val):
        val = tklib_normalize_theta(val)
        self.thetas[i,j] = val

    def num_givens(self):
        return (self.k*(self.k-1.0))/2.0
    
    
    def toR(self):
        givens = self.toGivens()

        if(len(givens) <= 0):
            return None
        
        R = diag(ones(self.k)*1.0)

        for i in range(len(givens)):
            R = givens[i].rmultiply(R)
        
        return R

    def get_derivatives(self):
        g_rots = self.toGivens();
        return list(self.get_derivative(i, g_rots) for i in range(int(self.num_givens())));
    
    def get_derivative(self, i, g_rots=None):
        if(g_rots == None):
            g_rots = self.toGivens();
            
        #initialize As
        Ai = diag(ones(self.k))
            
        #calculate As(k)
        for k in range(len(g_rots)):
            if(i==k):
                Ai = g_rots[k].rmultiply_derivative(Ai)
            else:
                Ai = g_rots[k].rmultiply(Ai)

        return Ai


    def toGivens(self):
        givens_matrices = []
        #get the givens matrices
        
        for i in range(len(self.thetas)):
            for j in range(i+1,len(self.thetas)):
                gij = givens_matrix(self.thetas[i,j], i, j, self.k)
                givens_matrices.append(gij)

        return givens_matrices



class givens_matrix:
    def __init__(self, theta, i, j, n):
        self.theta = tklib_normalize_theta(theta)
        self.i = i
        self.j = j
        self.n = n

        if(j<i):
            print "error: givens_matrix i>j"
            sys.exit(0)

    def lmultiply_derivative(self, myMatrix):
        retmat = zeros([self.n, self.n])*1.0

        rowi = zeros(self.n)*1.0
        rowj = zeros(self.n)*1.0

        rowi[self.i]=-sin(self.theta);
        rowi[self.j]=cos(self.theta);
        rowj[self.i]=-cos(self.theta);
        rowj[self.j]=-sin(self.theta);

        rowi_new = dot(rowi, myMatrix)
        rowj_new = dot(rowj, myMatrix)

        retmat[self.i,:]=rowi_new
        retmat[self.j,:]=rowj_new
        return retmat


    def rmultiply_derivative(self, myMatrix):
        retmat = zeros([self.n, self.n])*1.0

        coli = zeros(self.n)*1.0
        colj = zeros(self.n)*1.0

        coli[self.i]=-sin(self.theta);
        coli[self.j]=-cos(self.theta);
        colj[self.i]=cos(self.theta);
        colj[self.j]=-sin(self.theta);

        coli_new = dot(myMatrix, coli)
        colj_new = dot(myMatrix, colj)

        retmat[:,self.i]=coli_new
        retmat[:,self.j]=colj_new
        return retmat

    def lmultiply(self, myMatrix):
        rowi = zeros(self.n)*1.0
        rowj = zeros(self.n)*1.0
        
        rowi[self.i]=cos(self.theta);
        rowi[self.j]=sin(self.theta);
        rowj[self.i]=-sin(self.theta);
        rowj[self.j]=cos(self.theta);

        rowi_new = dot(rowi, myMatrix)
        rowj_new = dot(rowj, myMatrix)

        myMatrix[self.i,:]=rowi_new
        myMatrix[self.j,:]=rowj_new
        return myMatrix

    def rmultiply(self, myMatrix):
        coli = zeros(self.n)*1.0
        colj = zeros(self.n)*1.0

        coli[self.i]=cos(self.theta);
        coli[self.j]=-sin(self.theta);
        colj[self.i]=sin(self.theta);
        colj[self.j]=cos(self.theta);

        coli_new = dot(myMatrix, coli)
        colj_new = dot(myMatrix, colj)

        myMatrix[:,self.i]=coli_new
        myMatrix[:,self.j]=colj_new
        return myMatrix
    
    def __repr__(self):
        return self.tostring();

    def __str__(self):
        return self.tostring();
    
    def tostring(self):
        mystr = "\ngivens_matrix\n"
        val = diag(ones(self.n)*1.0)
        val[self.i, self.i]=cos(self.theta);
        val[self.i, self.j]=sin(self.theta);
        val[self.j, self.i]=-sin(self.theta);
        val[self.j, self.j]=cos(self.theta);
        mystr += str(val)
        return mystr
        

class IllegalArgumentError(Error):
    """Raised when an operation attempts to pass an argument that
    is not acceptable

    Attributes:
        argument -- argument that was bad
        message -- explanation of why the argument was bad
    """
    def __init__(self, argument, message):
        self.argument = argument
        self.message = message
        



def test1():
    testArry = array([[1,0],[0,1.0]])
    #def __init__(self, theta, i, j, n):
    gm = givens_matrix(0.0,0,1,2)
    print "lmultiply"
    print gm.lmultiply(copy(testArry))
    
    print "rmultiply"
    print gm.rmultiply(copy(testArry))

    print "lmultiply_derivative"
    print gm.lmultiply_derivative(testArry)
    
    print "rmultiply_derivative"
    print gm.rmultiply_derivative(testArry)

def test2():
    g_rot = GivensRotation(3, thetas=[pi/4.0, pi/4.0, pi/4.0])
    R = g_rot.toR()
    print R
    


if __name__ == "__main__":
    #test1();
    test2();
    
    

