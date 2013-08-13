from carmen_util import *
from pyTklib import *
import networkx as nx
from sys import argv, maxint
from random import randint
from carmen_maptools import plot_map



class carmen_path_planner:
    def __init__(self, filename, num_samples=100, max_d_to_next_pt=maxint, seed=1):
        tklib_init_rng(seed)
        
        self.map = tklib_log_gridmap();        
        self.map.load_carmen_map(filename)
        
        #the minimum distance two points have to be apart for a loop
        #    to exist
        self.locations = array(self.map.get_random_open_locations(num_samples, 0.2))
        
        #build a graph
        self.max_d = max_d_to_next_pt
        self.G = self.build_graph(self.locations, max_d_to_next_pt)

    def __del__(self):
        del self.locations, self.max_d, self.G
        
        
    def build_graph(self, pts, max_dist=maxint):
        G = nx.XGraph()
        
        for i in range(len(pts[0])):
            for j in range(len(pts[0])):
                if(self.map.is_visible(pts[:,i], pts[:,j])):
                    d_euclid = get_euclidean_distance(pts[:,i], pts[:,j])
                    if(d_euclid < max_dist):
                        G.add_edge((i,j,d_euclid))
        return G

    def shortest_path(self, pt1_label, pt2_label):
        return nx.bidirectional_dijkstra(self.G, pt1_label, pt2_label)

    
    def is_visible_path(self, i, path):
        if(i in path):
            return True
        
        for j in range(len(path)):
            if(self.map.is_visible(self.locations[:,i], self.locations[:,path[j]])):
                return True
        
        return False


    def find_sentinel(self, path):
        for i in range(len(self.locations[0])):
            if(not self.is_visible_path(i, path)):
                return i

        return None

    def get_nearest_visible_point(self, pt):
        #otherwise, compute using the sampling-based approach
        I1 = kNN_index(pt, self.locations, len(self.locations[0]));


        #compute the nearest visible point
        i1 = None
        for i in I1:
            if(self.map.is_visible(pt, self.locations[:,i])):
                i1 = i
                break
    
        return i1
    
    def get_path(self, pt1, pt2):
        #if we can see one point from another, then 
        #   simply compute the straight line distance
        if(self.map.is_visible(pt1, pt2)):
            d =  tklib_euclidean_distance(pt1, pt2)
            mypath = self.get_straight_path(pt1, pt2) # transpose([pt1, pt2])
            
            return mypath, d

        i1 = self.get_nearest_visible_point(pt1)
        i2 = self.get_nearest_visible_point(pt2)
        
        if(i1 == None or i2 == None):
            #print "no nearest point"
            return None

        sp = self.shortest_path(int(i1), int(i2))

        if(sp == False):
            #print "no shorteset path"
            return None
        
        d, path = sp
        
        mypath = self.locations.take(path, axis=1)
        
        #compute the final path including the start and end points
        finpath = concatenate((transpose([pt1]), mypath, transpose([pt2])), 1)
        
        #include the distance to the closest point
        d = d + tklib_euclidean_distance(pt1, mypath[:,0]) + tklib_euclidean_distance(mypath[:,-1], pt2)
        del sp, mypath, i1, i2, pt1, pt2
        
        return finpath, d

    def get_straight_path(self, pt1, pt2):

        dy = pt2[1] - pt1[1]
        dx = pt2[0] - pt1[0]
        theta = atan2(dy, dx)

        dx_p = self.max_d * cos(theta)
        dy_p = self.max_d * sin(theta)

        i=0;

        Pts = []; curr_pt = pt1

        while(get_euclidean_distance(curr_pt, pt2) >= self.max_d):
            x = i*dx_p + pt1[0]
            y = i*dy_p + pt1[1]

            curr_pt = [x, y]
            Pts.append(curr_pt)
            i+=1
            #raw_input()

        Pts.append(pt2)

        return transpose(Pts)

    

def test1(argv):
    filename = argv[1]
    num_samples = int(argv[2])
    
    path_planner = carmen_path_planner(filename, num_samples)
    
    #plot(path_planner.locations[0], path_planner.locations[1], 'ro')
    #mymap = path_planner.map.to_probability_map_carmen()
    #plot_map(mymap, path_planner.map.get_y_size(),path_planner.map.get_x_size())
    
    #show()
    pts = path_planner.get_loop_pts()
    
    if(pts != None):
        plot(pts[0], pts[1], 'r-');
        mymap = path_planner.map.to_probability_map_carmen()
        plot_map(mymap, path_planner.map.get_y_size(),path_planner.map.get_x_size())
        
        plot([path_planner.locations[0,path_planner.s_ind]],
             [path_planner.locations[1,path_planner.s_ind]], 'ro')
        plot([path_planner.locations[0,path_planner.e_ind]],
            [path_planner.locations[1,path_planner.e_ind]], 'rx')
        
        for i in range(len(path_planner.sentinels)):
            plot([path_planner.locations[0,path_planner.sentinels[i]]],
                 [path_planner.locations[1,path_planner.sentinels[i]]], 'r^')
        show()

def test2(argv):
    filename = argv[1]
    num_samples = int(argv[2])
    
    path_planner = carmen_path_planner(filename, num_samples)
    pts = path_planner.get_path([45, 25], [45, 45])
    
    if(pts != None):
        mymap = path_planner.map.to_probability_map_carmen()
        plot_map(mymap, path_planner.map.get_y_size(),path_planner.map.get_x_size())
        plot(pts[0], pts[1], 'r-');
        show()


if __name__=="__main__":
    
    if(len(argv) == 4):
        #test1(argv)
        test2(argv)
    else:
        print "usage: \n\t\t>>python carmen_path_planner.py filename d_loop numsamples"
