#from datatypes import *
#from scipy import *
from scipy.linalg import eig
from sorting import quicksort
#from kmeans import *
#from nearest_neighbor import *
#from spectral_clustering_utils import *
from scipy import nan

#def spectral_clustering_two_class(X,r,beta):
'''return labels for each data point
    
    runs spectral clustering on X and displays the resulting
    clustering, overlayed onto the neighbourhood graph used.
    
    Arguments:  X -- the data
    k -- number of resulting clusters
    r -- number of neighbors
    beta -- the weight falloff parameter
'''
def spectral_clustering_W(W, k=None,numkmeans=1,seed_number=987,max_dist=10e10,t=None):
    return spectral_clustering(None,None,t,k,W,numkmeans,seed_number=seed_number,max_dist=max_dist)
 
def spectral_clustering(X,r,t=None,k=None,W=None,numkmeans=1,seed_number=987,max_dist=10e10):
    ''' return labels for each data point
    
    runs spectral clustering on X and displays the resulting
    clustering, overlayed onto the neighbourhood graph used.
    
    Arguments:  X -- the data
    r -- number of neighbors
    k -- number of resulting clusters
    t -- the threshold for the selection of eigenvalues near 1
    '''
    print "running with", "t=",t, "k=",k, "max_dist=",max_dist
    
    #create the weight matrix and normalize it
    if(W == None):
        W = weights_perona(X,r)
        
    Dinv = diag(1/(1.0*sum(W, 1)))
    M = dot(dot(sqrt(Dinv), W), sqrt(Dinv))

    #get the eigenvectors, which are now in the columnsx
    U,E,V = svd(M)
    V=transpose(U)
    sortedE, I = quicksort(E)

    #estimate the number of clusters by looking at the eigenvalues
    if(t==None):
        #this has worked really well: t=0.195
        #t=0.01
        #t=0.17
        t=0.185
        #t=0.195
        #t=0.18
    if(k==None):
        k=0
        for i in range(len(sortedE)):
            if((1.0-sortedE[len(sortedE)-i-1])>t):
                break
            k=k+1

        if(k == 0):
            print "There are no eigenvalues of 1"
            print "The closest is:", sortedE[len(sortedE)-1]
            return
        
    #print "E:", E
    print "number of clusters", k

    #get only the relevant eigenvectors based on the number of classes
    #that we have selected 
    V_sorted =[]
    E_svals = []
    for j in range(len(I)-k,len(I)):
        V_sorted.append(V[I[j],:])
        E_svals.append(E[I[j]])

    #print len(I)
    #print range(len(I)-k,len(I))
    #print "number of ev:", len(range(len(I)-k,len(I)))
    #raw_input()
    #normalize the rows of the eigenvectors

    V = transpose(V_sorted)
    #print "V", 
    #for elt in V:
    #    print elt
    
    divisor = 1.0/(sum(sqrt(V**2),1)+(10.0**(-30)))
    V = dot(diag(divisor), V)

    #try to weight the vector values
    V = V*array([E_svals])

    #print "V_norm", V
    #for elt in V:
    #    print elt

    #use optimized methods here
    print "random seed:", seed_number

    
    mylabels = []
    for i in range(numkmeans):
        print "performing k-means on ", k, "clusters"
        means = kmeans_autoinit(transpose(V), 500, k);
        mylabels.append(kmeans_get_labels(transpose(V), means))
        
        D = array(kmeans_get_distances(transpose(V), means))
        for j, label in enumerate(mylabels[-1]):
            if(D[label][j] > max_dist):
                mylabels[-1][j] = nan
            
    return mylabels, k


def spectral_clustering_auto(X,r,k=None,kMax=None,W=None,seed_number=987):
    ''' return labels for each data point
    
    runs spectral clustering on X and displays the resulting
    clustering, overlayed onto the neighbourhood graph used.
    
    Arguments:  X -- the data
    r -- number of neighbors
    k -- number of resulting clusters
    t -- the threshold for the selection of eigenvalues near 1
    '''
    
    #create the weight matrix and normalize it
    if(W == None):
        W = weights_perona(X,r)
        
    Dinv = diag(1/(1.0*sum(W, 1)))
    M = dot(dot(sqrt(Dinv), W), sqrt(Dinv))

    #get the eigenvectors, which are now in the columnsx
    U,E,V = svd(M)
    V=transpose(U)
    sortedE, I = quicksort(E)

    #get only the relevant eigenvectors based on the number of classes
    #that we have selected 
    V_sorted =[]
    for j in range(len(I)-kMax,len(I)):
        V_sorted.append(V[I[j],:])

    #normalize the rows of the eigenvectors
    V = transpose(V_sorted)
    V_pr,k = get_number_of_clusters(V, kMax)
    
    divisor = 1.0/(sum(sqrt(V_pr**2),1)+(10.0**(-30)))
    V_pr = dot(diag(divisor), V_pr)
    
    #use optimized methods here
    print "random seed:", seed_number
    means =  kmeans_autoinit(transpose(V_pr), 100, k);
    labels = kmeans_get_labels(transpose(V_pr), means);
    
    return labels, k


def get_number_of_clusters(V, kMax):
    #create a normalized V
    g_init=None
    g_rot_fin = None

    k=2
    minC = sys.maxint
    for i in range(2, kMax+1):
        V_i = copy(V[:,len(V[0])-i:len(V[0])])
        g_rot = spectral_gradient_descent(V_i,10.0**(-2), threshold=(10.0)**(-9),
                                          iterations=10000, g_rot_init=g_init)

        currC = get_score(V_i, g_rot)
        print "i,", i, "score", currC
        if(currC < minC):
            k = i
            minC = currC
            g_rot_fin = g_rot

    
    V_ret = dot(abs(V[:,len(V[0])-k:len(V[0])]), g_rot_fin.toR())
    divisor = 1.0/(sum(sqrt(V_ret**2),1)+(10.0**(-8)))
    V_ret = dot(diag(divisor), V_ret)
    
    return V_ret, k


def get_random_circle_pt(radius):
    theta = 2*math.pi*random()
    #return [theta, radius]    
    return [radius*cos(theta), radius*sin(theta)]


def test1():
    #number_of_classes = 3
    title("rotation")
    pts = []
    
    ion()
    for i in range(200):
        pts.append(get_random_circle_pt(15))
    for i in range(100):
        pts.append(get_random_circle_pt(4))
    for i in range(100):
        pts.append(get_random_circle_pt(0.2))
    pts = array(pts)

    #for j in range(len(pts)):
    #   plot([pts[j].data[0]], [pts[j].data[1]], 'ro')
    #draw()
    #raw_input()

    #def spectral_clustering(X,r,t=None,k=None,W=None):
    classes1,k = spectral_clustering_auto(pts, 150, kMax=5, k=3)

    colors = ['g', 'b', 'y', 'r', 'm']
    types = ['o', 'x', '>', '<']
    print "classes1", classes1
    for i in range(k):
        X, Y = [],[]

        #print "length",len(classes1)
        #print "classes1", classes1
        for j in range(len(classes1)):
            if(classes1[j] == i):
                #print "YAYYYYYYYYYYY"
                #print pts[j]
                X.append(pts[j][0])
                Y.append(pts[j][1])

        plot(X,Y,colors[i]+types[i])

        show()
'''figure()
    title("no rotation")
    colors = ['g', 'b', 'y', 'r', 'm']
    types = ['o', 'x', '>', '<']
    print "classes2", classes2
    for i in range(k):
        X, Y = [],[]

        #print "length",len(classes2)
        #print "classes2", classes2
        for j in range(len(classes2)):
            if(classes2[j] == i):
                #print "YAYYYYYYYYYYY"
                #print pts[j]
                X.append(pts[j][0])
                Y.append(pts[j][1])

        plot(X,Y,colors[i]+types[i])


    show()'''
def test1_5():
    #number_of_classes = 3
    pts = []
    
    ion()
    for i in range(100):
        pts.append(get_random_circle_pt(15))
    for i in range(100):
        pts.append(get_random_circle_pt(4))
    for i in range(100):
        pts.append(get_random_circle_pt(0.2))
    pts = array(pts)

    #for j in range(len(pts)):
    #   plot([pts[j].data[0]], [pts[j].data[1]], 'ro')
    #draw()
    #raw_input()

    #def spectral_clustering(X,r,t=None,k=None,W=None):
    classes,k = spectral_clustering(pts, 150, k=3)
    print classes
    colors = ['g', 'b', 'y', 'r', 'm']
    types = ['o', 'x', '>', '<']

    for i in range(k):
        X, Y = [],[]

        #print "length",len(classes)
        #print "classes", classes
        for j in range(len(classes)):
            if(classes[j] == i):
                #print "YAYYYYYYYYYYY"
                #print pts[j]
                X.append(pts[j][0])
                Y.append(pts[j][1])

        plot(X,Y,colors[i]+types[i])


    show()

def test2():
    #number_of_classes = 3
    pts = []
    
    ion()
    for i in range(100):
        pts.append(gaussian_normal_sample([[1, 0], [0, 1]], [0,0]))
    for i in range(100):
        pts.append(gaussian_normal_sample([[1, 0], [0, 1]], [10,10]))
    for i in range(100):
        pts.append(gaussian_normal_sample([[1, 0], [0, 1]], [-10,-10]))
    for i in range(100):
        pts.append(gaussian_normal_sample([[1, 0], [0, 1]], [-10,10]))
    for i in range(100):
        pts.append(gaussian_normal_sample([[1, 0], [0, 1]], [10,-10]))        
    pts = array(pts)

    #for j in range(len(pts)):
    #   plot([pts[j].data[0]], [pts[j].data[1]], 'ro')
    #draw()
    #raw_input()

    #def spectral_clustering(X,r,t=None,k=None,W=None):
    classes,k = spectral_clustering_auto(pts, 200, kMax=5)
    
    print classes
    colors = ['g', 'b', 'y', 'r', 'm', 'k']
    types = ['o', 'x', '>', '<','^']

    for i in range(k):
        X, Y = [],[]

        #print "length",len(classes)
        #print "classes", classes
        for j in range(len(classes)):
            if(classes[j] == i):
                #print "YAYYYYYYYYYYY"
                #print pts[j]
                X.append(pts[j][0])
                Y.append(pts[j][1])

        plot(X,Y,colors[i]+types[i])


    show()
        
    
