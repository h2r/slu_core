from gaussian import *
from datatypes import *
from random import randint
from probability import sample_discrete


#assume here that X is |X|xN , where N is the number
#of datapoints, similarly for S
def kmeans(X, iterations, num_clusters, S=None):
    labels = zeros(len(X[0]))*1.0 - 1.0

    if(not S == None):
        num_clusters = len(S[0])
        curr_means = S
    else:
        curr_means = get_initial_clusters(X, num_clusters)

    for i in range(iterations):
        distances = get_distances(X, curr_means)
        labels = argmin(distances, 0)
        curr_means = compute_mean(X, labels)

    distances = get_distances(X, curr_means)
    labels = argmin(distances, 0)
        
    return labels, curr_means

#this returns the likelihood of each cluster
#may not exactly be a likelihood, oh well
def kmeans_get_neg_log_likelihood(X, u, labels, std):
    #print "***********************************"
    probs = zeros([len(u[0]), len(X[0])])*1.0
    probs_with_assignments = zeros(len(u[0]))*1.0
    
    #norm = zeros(len(u[0]))*1.0
    for i in range(len(u[0])):
        #not sure if this is right, I think so
        #print "u[:,i]", u[:,i]
        probs[i,:] = normal_log_prob(X, u[:,i], diag(ones(len(u))*1.0*std**2))
        #print "probs[", i, ",:]", probs[i,:]

    for i in range(len(labels)):
        #norm[labels[i]] += 1.0
        probs_with_assignments[int(labels[i])] += probs[int(labels[i]),i]

    #print "probs: ", probs
    #print "pwa", probs_with_assignments
    return probs_with_assignments #+ log(norm)


def get_initial_clusters(X, num_clusters):
    init_means = []

    index = randint(0, len(X[0])-1)
    init_means.append(X[:,index])

    for i in range(1, num_clusters):
        index = select_initial_cluster(X, transpose(init_means))
        init_means.append(X[:,index])

    return transpose(init_means)

def select_initial_cluster(X, init_clusters):
    probs = []

    dists = get_distances(X, init_clusters)
    probs = min(dists)
    Z = sum(probs)
    probs = probs/(1.0*Z)
    
    i, = sample_discrete(probs, 1)
    return i

def get_distances(X, pts):
    distances = zeros([len(pts[0]), len(X[0])])*1.0

    for i in range(len(pts[0])):
        curr_mean = transpose([pts[:,i]])
        dist_i = sqrt(sum((X-transpose([pts[:,i]]))**2))

        distances[i,:] = dist_i

    return distances
    

def compute_mean(X, labels):
    means = zeros([len(X), max(labels)+1])*1.0
    count_mean_members = zeros(len(labels))*1.0

    #initialize the means
    #compute the new means in one pass
    for i in range(len(labels)):
        means[:,labels[i]] = means[:,labels[i]]+ X[:,i]
        count_mean_members[labels[i]] += 1

    for i in range(len(means)):
        means[:,i] = means[:,i]/count_mean_members[i]

    return means


def test1():

    #test me here
    pts = []
    for i in range(100):
        pts.append(normal_sample([[10, 0], [0,10]], [0,0]))
    for i in range(100):
        pts.append(normal_sample([[3, 0], [0,3]], [10,-10]))
    pts = transpose(pts)
    
    
    labels, means = kmeans(pts, 10, 2)#array([[-1.0, 0.1],
                                       #[-1.0, 0.1]]), 10)
    

    print "log likelihood", kmeans_get_log_likelihood(pts, means, labels, 1)
    
    colors = ['r', 'g', 'b', 'y', 'm']
    types = ['o', 'x', '>', '<']

    
    
    for j in range(len(means)):
        X, Y = [],[]
        for i in range(len(labels)):
            if(labels[i]==j):
                X.append(pts[0][i])
                Y.append(pts[1][i])

        plot(X,Y,colors[j]+types[j])


    show()

def test2():
    pts = array([[  3.18214879e-16,  1.83927886e-01,  2.77727555e-01,
                    3.72952220e-01, 4.69575968e-01,  5.72302848e-01], 
                 [ -5.19701500e+00, -5.26700553e+00, -5.29935745e+00,
                   -5.33346522e+00, -5.36727787e+00, -5.44509788e+00]])

    labels, means = kmeans(pts, 10, 2)#array([[-1.0, 0.1],
                                       #[-1.0, 0.1]]), 10)
    
    print "log likelihood", kmeans_get_log_likelihood(pts, means, labels, 1)
    
    colors = ['r', 'g', 'b', 'y', 'm']
    types = ['o', 'x', '>', '<']
    plot([means[:,0][0]], [means[:,0][1]],'r>')
    plot([means[:,1][0]],[means[:,1][1]],'g>')
    for j in range(len(means)):
        X, Y = [],[]
        for i in range(len(labels)):
            if(labels[i]==j):
                X.append(pts[0][i])
                Y.append(pts[1][i])

        plot(X,Y,colors[j]+types[j])

    show()


def test3():
    X = arange(0, 1, 0.2)
    Y = arange(0, 1, 0.2)*0.0

    labels, means = kmeans(array([X, Y]), 10, 2)
    print "log likelihood", kmeans_get_neg_log_likelihood(array([X, Y]), means, labels, 0.01)

    X2 = []
    Y2 = []
    tmp_means = [array([0,0]), array([1, 1])]
    j = 0
    for i in range(len(X)):
        cov = array([[0.01**2, 0.0], [0.0, 0.01**2]])

        if(i > len(X)/2):
            j = 1
        
        u = tmp_means[j]
        samp = normal_sample(cov, u)
        X2.append(samp[0])
        Y2.append(samp[1])
        
    labels, means2 = kmeans(array([X2, Y2]), 10, 2)
    print "log likelihood", kmeans_get_neg_log_likelihood(array([X2, Y2]), means2, labels, 0.01)

    plot(X, Y, 'ro')
    plot(X2, Y2, 'bx')
    plot(means[0], means[1], 'k^')
    plot(means2[0], means2[1], 'k+')
    show()


if(__name__=="__main__"):
    #test1()
    #test2()
    test3()
