#File: nearest_neighbor_ctree.py
#Author: Thomas Kollar
#Date: 05/04/07
#All Rights Reserved. Copyright Thomas Kollar 2007
#
#
#
#  This is a class for the cover tree nearest
#  neighbor algorithm.  For more information
#  please refer to the technical report entitled
#  "Fast Nearest Neighbors" by Thomas Kollar
#  or to "Cover Trees for Nearest Neighbor" by
#  John Langford, Sham Kakade and Alina Beygelzimer

from cover_tree_core import *
from scipy import *
import sys

class cover_tree:
    def __init__(self, model_pts, top_level=15, bottom_level=-15):
        self.ct = self.build_cover_tree(model_pts, top_level, bottom_level)
        
    #
    #Overview: insert a vector into the cover tree
    #
    #input:   takes a vector
    #output:  None
    #
    def insert(self, pt):
        self.ct.insert(Node(pt))


    #
    #Overview: find if an element is in the cover tree
    #
    #input:   takes a vector
    #output:  returns the point and the level at which it was found
    # or None if it was not found
    #
    def find(self, pt):
        return self.ct.find(Node(pt))

    #
    #Overview: get the nearest neighbor
    #
    #input:   takes a vector
    #output:  returns the nearest point
    #
    def nearest_neighbor(self, pt):
        return self.ct.nearest_neighbor(Node(pt))

    #
    #Overview: get the nearest neighbor for a number of points
    #
    #input:   takes an MxN matrix whose columns are the vectors of length M
    #           and N query points
    #output:  returns a matrix of size MxN with vectors of length M and N
    #            return points, one for each query point
    #
    def nearest_neighbors(self, pts):
        results = zeros([len(pts), len(pts[0])])*1.0;
        for i in range(len(pts[0])):
            resNode = self.nearest_neighbor(pts[:,i])
            results[:,i] = resNode.toarray()
        return results

    #
    #Overview: build the core cover tree
    #
    #input:   takes an MxN matrix whose columns are the vectors of length M
    #           and N query points
    #output:  returns a matrix of size MxN with vectors of length M and N
    #            return points, one for each query point
    #
    def build_cover_tree(self, pts, top_level, bottom_level):
        ctree = cover_tree_core(Node(pts[:,0]), top_level, bottom_level)
        for i in range(1,len(pts[0])):
            ctree.insert(Node(pts[:,i]))
    
        return ctree


    #
    #Overview: Compute the optimal minimum level
    #
    #input:   takes a list of Nodes and a maximum level
    #output:  the minimum level
    #
    def compute_optimal_level(self, node_list, maxlevel):
        minDist = sys.maxint
        for p in node_list:
            for q in node_list:
                if(p.d(q)<minDist and not p==q):
                    minDist = p.d(q)

        brange = range(-1000, maxlevel)
        brange.reverse()

        max_minlevel = 0
        for i in brange:
            if(2**i < minDist):
                max_minlevel = i
                print "The setting of I", self.minlevel
                break

        return max_minlevel

    #
    #Overview: Prints the covertree to a dotty graph
    #
    #input:   
    #output:  
    #
    def printTree(self):
        self.ct.printDotty()


