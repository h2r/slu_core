try:
    from pyTklib import *
except:
    print "gaussian.py: COULD NOT IMPORT pyTklib optimized libraries"
    
try:
    from scipy.linalg import *
    from scipy import *
except:
    print "gaussian.py: COULD NOT IMPORT scipy optimized libraries"

def normal_get_ellipse(P, mean):
    P = array(P)
    U,S,V=linalg.svd(P)

    mean = transpose([mean])
    R = matrixmultiply(U, diag(S**(1.0/2.0)));
    
    return  get_ellipse(mean, R, 20);

# Fake an ellipse using an N-sided polygon
# pts is a 2xN array, R is a rotation matrix
def get_ellipse(center, R, resolution=20):
    theta = 2*pi/resolution*arange(resolution)
    circle = array([cos(theta), sin(theta)])
    
    ellipse = matrixmultiply(R, circle)
    ellipse = ellipse + center
    
    return ellipse

def normal_sampleC(cov, u):
    samp = gaussian_normal_sample(cov, u);
    return samp

def normal_sample(cov, u):
    R = linalg.decomp.cholesky(cov, lower=1)
    
    x = randn(len(u))
    myVal = matrixmultiply(R, x)+u

    return myVal

#X here is the number of dimensions by the number of points
def normal_prob(X, u, cov):
    N = len(X)
    Z = 1.0/(((2*pi)**(N/2.0))*det(cov)**(1/2.0))

    R1 = matrixmultiply(transpose(X-transpose([u])), inv(cov))
    R2 = R1*transpose(X-transpose([u]))
    V = sum(R2, 1)

    p = Z*exp((-1.0/2.0)*V)
    return p

def normal_log_prob(X, u, cov):
    N = len(X)
    Z = 1.0/(((2*pi)**(N/2.0))*det(cov)**(1/2.0))

    #print "(((((((((((((((((("
    #print "log_prob: u", u
    #print "log_prob: X", X
    #print "X-u:", transpose(X-transpose([u]))

    #print "inv(cov):", inv(cov)
    R1 = matrixmultiply(transpose(X-transpose([u])), inv(cov))
    R2 = R1*transpose(X-transpose([u]))
    V = sum(R2, 1)
    #print "R2:", R2
    #print ")))))))))))))))))))"

    l_prob = log(Z) + (-1.0/2.0)*V
    return l_prob


def test1():
    #cov = array([[0.75,1],[1,0.75]])#rand(2,2)
    cov = array([[1,0.4],[0.4,1.0]])
    cov = matrixmultiply(cov, transpose(cov))
    u = zeros(2)
    
    print normal_sample(cov, u)
    print normal_sampleC(cov, u)
        
    
    samples = [];
    samples2 = [];
    for i in range(1000):
        samples.append(normal_sampleC(cov, u))
        samples2.append(normal_sample(cov, u))
    
    samples=transpose(samples)
    samples2=transpose(samples2)
    
    X, Y = normal_get_ellipse(cov, u)
    plot(samples[:][0], samples[:][1], 'ro')
    plot(samples2[:][0], samples2[:][1], 'go')
    plot(X, Y, linewidth=3);
    axis([-8, 8, -8, 8])
    show()

def test2():
    cov = array([[0.75,1],[1,0.75]])#rand(2,2)
    #cov = matrixmultiply(cov, transpose(cov))
    u = zeros(2)+3

    X, Y = normal_get_ellipse(cov, u)
    plot(X, Y);
    show()


def test3():
    u = array([0,0,0])
    cov = diag([0.1, 0.5, 1.0])
    #x = array([0.1,0.2,0.3])

    x = array([[0.1,0.1],
               [0.2,0.3],
               [0.3,0.5]])

    print normal_log_prob(x, u, cov)


if(__name__ == "__main__"):
    from pylab import *

    #test3()
    #test2()
    test1()
