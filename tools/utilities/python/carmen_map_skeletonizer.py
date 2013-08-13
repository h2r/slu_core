from carmen_util import get_euclidean_distance
#from pyTklib import *
from scipy import array, transpose, zeros
from carmen_gridmap import tklib_log_gridmap
from shortest_path import shortestPath
from spatial_features_cxx import kNN_index
#from tklib_image_utils import *
from copy import deepcopy
import cPickle
from collections import deque
from scipy import mod


def load(skel_fn, map_fn):
    skeleton = cPickle.load(open(skel_fn, 'r'))
    skeleton.map_filename = map_fn
    return skeleton


class carmen_map_skeletonizer:
    def __init__(self, map_filename, mfilter_width, num_iterations):
        self.map_filename = map_filename
        self.num_iterations = num_iterations
        self.mfilter_width = mfilter_width
        
        self.gridmap  = tklib_log_gridmap()
        self.gridmap.load_carmen_map(map_filename);
        
        #make a binary map from a gridmap
        self.b_map = self.to_binary_map(self.gridmap)
        self.b_map = median_filter(self.b_map, mfilter_width)
        self.skeleton = None
        self.skeleton_prestaircase = None

        self.skeleton_indicies = None
        self.G = None; self.I = None
        
    def get_skeleton(self):
        if(not self.skeleton == None):
            return self.skeleton

        skeleton = skeletonize(self.b_map, self.num_iterations)
        self.skeleton_prestaircase = skeleton

        print "removing staircases"
        skeleton_nosc = self.remove_staircases(skeleton)
        
        self.skeleton = skeleton_nosc
        return skeleton_nosc

    def get_skeleton_indices(self):
        if(self.skeleton == None):
            return None

        #this try-except block is deprecated in order
        #  to deal with already-generated skeletons
        try:
            if(not self.skeleton_indicies == None):
                return self.skeleton_indicies
        except:
            pass

        I, J = [], []
        for i in range(len(self.skeleton)):
            for j in range(len(self.skeleton[0])):
                if(self.skeleton[i,j] > 0.5):
                    I.append(i);
                    J.append(j);

        self.skeleton_indicies = [I,J]
        return self.skeleton_indicies

    def get_skeleton_indices_index(self):
        if(self.skeleton == None):
            return None

        myindex = {}
        I, J = [], []
        ind = 0
        for i in range(len(self.skeleton)):
            for j in range(len(self.skeleton[0])):
                if(self.skeleton[i,j] > 0.5):
                    myindex[str([i,j])] = ind
                    ind+=1

        return myindex

    #get the interest points in a map
    def get_interest_points(self):
        curr_map = self.get_skeleton()
        gm = self.get_map()
        
        
        #get the junctions and ends
        junction_map, Ij  = self.find_junction_points(curr_map)
        end_map, Ie  = self.find_end_points(curr_map)
    
        #get the XY locations for the dest pts
        XY = self.ind_to_xy(Ij*1.0).tolist()
        XY_tmp = self.ind_to_xy(Ie*1.0)
        XY[0].extend(XY_tmp[0]); XY[1].extend(XY_tmp[1])
    
        return XY
    
    def get_junction_points(self):
        curr_map = self.get_skeleton()
        #gm = self.get_map()
        
        #get the junctions and ends
        junction_map, Ij  = self.find_junction_points(curr_map)
        XY = self.ind_to_xy(Ij*1.0).tolist()
    
        return XY

    def get_end_points(self):
        curr_map = self.get_skeleton()
        #gm = self.get_map()
        
        #get the junctions and ends
        end_map, Ie  = self.find_end_points(curr_map)


        #get the XY locations for the dest pts
        XY = self.ind_to_xy(Ie*1.0).tolist()
        

        return XY

    def get_map(self):
        if(self.gridmap==None):
            self.gridmap  = tklib_log_gridmap()
            self.gridmap.load_carmen_map(self.map_filename);
        
        return self.gridmap

    def to_binary_map(self, gm):
        binary_map = 1.0*zeros([gm.get_map_height(), gm.get_map_width()])
        I = array(gm.get_free_inds())

        for m in range(len(I[0])):
            i, j = I[:,m]
            binary_map[j][i] = 1.0

        return binary_map

    def remove_staircases(self, b_map):
        #curr_map = deepcopy(b_map)
        tmp_map = deepcopy(b_map)

        for k in range(1, 5):
            #print "i=", k
            myfilter = self.get_filter(k)
            height = len(myfilter)
            width  = len(myfilter[0])

            for i in range(1,len(tmp_map)-height-1):
                for j in range(1, len(tmp_map[0])-width-1):
                    neigh = tmp_map[i:i+height,j:j+width]

                    if(sum(neigh*myfilter) == 3):
                        if(k == 1):
                            ic, jc = i+1, j
                        elif(k == 2):
                            ic, jc = i+1, j+1
                        elif(k == 3):
                            ic, jc = i, j+1
                        elif(k == 4):
                            ic, jc = i, j

                        #check this neighborhood for connectivity
                        neigh = deepcopy(tmp_map[ic-1:ic+2,jc-1:jc+2])
                        neigh[1, 1] = 0.0
                        iscon = self.is_connected(neigh)

                        if(iscon):
                            tmp_map[ic,jc] = 0.0
        return tmp_map

    def get_filter(self, style):
        myfilter = None

        if(style == 1):
            myfilter = array([[1.0, 0.0],
                              [1.0, 1.0]])
        elif(style == 2):
            myfilter = array([[0.0, 1.0],
                              [1.0, 1.0]])
        elif(style == 3):
            myfilter = array([[1.0, 1.0],
                              [0.0, 1.0]])
        elif(style == 4):
            myfilter = array([[1.0, 1.0],
                              [1.0, 0.0]])
        return myfilter


    def is_connected(self, neigh):
        unreached = self.get_open_locations(neigh)
        reached = [unreached.pop()]

        while(len(reached) > 0):

            ind = reached.pop()
            tmp_unreached = deepcopy(unreached)
            for i in range(len(unreached)):
                if(sqrt(sum((ind-array(unreached[i]))**2.0)) <= sqrt(2.0)):
                    reached.append(unreached[i])
                    tmp_unreached.remove(unreached[i])
            unreached = tmp_unreached

        if(len(unreached) > 0.0):
            return False

        return True

    def get_open_locations(self, neigh):
        I = []
        for i in range(len(neigh)):
            for j in range(len(neigh)):
                if(neigh[i][j] == 1.0):
                    I.append([i, j])
        return I


    def find_junction_points(self, b_map):
        new_map = deepcopy(b_map)

        I = []
        filter_size = 1
        for i in range(filter_size, len(b_map)-filter_size):
            for j in range(filter_size, len(b_map[0])-filter_size):

                if(new_map[i,j] == 0):
                    continue

                neigh = b_map[i-filter_size:i+filter_size+1,j-filter_size:j+filter_size+1]
                s = sum(neigh)

                i1, i2 = not [i, j-1] in I, not [i-1, j-1] in I
                i3, i4 = not [i-1, j] in I, not [i+1, j-1] in I
                i5, i6 = not [i, j+1] in I, not [i+1, j+1] in I
                i7, i8 = not [i+1, j] in I, not [i-1, j+1] in I
                if(s >= 4 and i1 and i2 and i3 and i4 and i5 and i6 and i7 and i8):
                    I.append([i,j])
                else:
                    new_map[i,j]=0.0

        return new_map, transpose(I)


    def get_neighbors(self, i, j):
        I = []
        for k in range(-1, 2):
            for l in range(-1, 2):
                if(k == 0 and l == 0):
                    continue
                if(self.skeleton[i+k, j+l] > 0.75):
                    I.append([i+k,j+l])
        return transpose(I)


    def find_end_points(self, b_map):
        new_map = deepcopy(b_map)

        I = []
        filter_size = 1
        for i in range(filter_size, len(b_map)-filter_size):
            for j in range(filter_size, len(b_map[0])-filter_size):

                if(new_map[i,j] == 0):
                    continue

                neigh = b_map[i-filter_size:i+filter_size+1,j-filter_size:j+filter_size+1]
                s = sum(neigh)

                if(s == 2):
                    I.append([i,j])
                else:
                    new_map[i,j]=0.0

        return new_map, transpose(I)

    def i_to_ind(self, indexes):
        I = array(self.get_skeleton_indices())
        return  [array([I[1, idx], I[0, idx]]) * 1.0 for idx in indexes]


    def i_to_xy(self, indexes):
        gridmap = self.get_map()
        X = []
        Y = []
        
        for ind in self.i_to_ind(indexes):
            x, y = gridmap.to_xy(ind)
            X.append(x)
            Y.append(y)
        return X, Y

    def ind_to_xy(self, I):
        XY = []
        I = array(I)

        gm = self.get_map()
        for i in range(len(I[0])):
            ind = array([I[1,i], I[0,i]])*1.0
            x, y = gm.to_xy(ind)
            XY.append([x, y])

        return transpose(XY)


    def xy_to_ind(self, XY):
        XY = array(XY)
        I = []
        gm = self.get_map()
        for i in range(len(XY[0])):
            xy = XY[:,i] #XY[0,i], XY[1,i]
            ix, iy = gm.to_index(xy)
            I.append([iy, ix])

        return transpose(I)

    def nearest_spline_location(self, loc):
        """
        return a tuple of the point closest to loc on the spline, and
        the index of that point in the skeleton.
        """
        I = self.get_skeleton_indices()
        XY = self.ind_to_xy(I)
        i, = kNN_index(loc, XY, 1)
        
        #print "loc:", 
        #print "nearest loc:", XY[:,i]
        #raw_input()
        return XY[:,i], int(i)
    
    

#    @memoize
    def get_graph(self):
        """
        Returns a dictionary, and an array of indices.  Keys are
        indices in get_skeleton_indices.  Values are a map whose keys
        are connected indices, and values are the distance between the
        two indices.  The graph contains a node for every point in the
        skeleton, as a grid map.  Use get_junction_points to get the
        junctions.
        """
        
        G = {}
        I = array(self.get_skeleton_indices())
        index_to_num_hash = self.get_skeleton_indices_index()

        for i in range(len(I[0])):
            G[i] = {}
            neighs = self.get_neighbors(I[0,i], I[1,i])

            if(len(neighs) == 0):
                continue
            
            for j in range(len(neighs[0])):
                myi, myj = neighs[:,j]

                G[i][index_to_num_hash[str([myi,myj])]] = get_euclidean_distance(I[:,i], 
                                                                                [myi,myj]);

        return G, I

    def compute_path(self, loc_st, loc_end):
        #get the nearest points on the spline
        loc_st_spl, loc_st_i = self.nearest_spline_location(loc_st)
        loc_end_spl, loc_end_i = self.nearest_spline_location(loc_end)
        

        #convert this to indices
        XY = transpose([loc_st_spl, loc_end_spl])
        Ind = self.xy_to_ind(XY)

        #print "len(XY)", len(XY)
        #print "len(XY[0])", len(XY[0])
        
        myst = Ind[:,0]
        myend = Ind[:,1]
        
        
        if(self.G == None):
            #now get this as a graph
            self.G, self.I = self.get_graph()
        
        #if(len(G[loc_st_i].keys()) == 0 or len(G[loc_end_i].keys()) == 0):
        #    return []
        
        sp = shortestPath(self.G,int(loc_st_i), int(loc_end_i))
        
        I = self.get_skeleton_indices()
        XY = self.ind_to_xy(I)
        return XY.take(sp, axis=1)


    def interest_graph_all_pairs_shortest_path(self):
        G_graph_I, G_locs_XY = self.get_interest_graph()
        
        G_paths_XY = {}
        for iteration, i in enumerate(G_graph_I.keys()):
            if(mod(iteration, 5) == 0):
                print iteration, "of", len(G_graph_I)
            
            G_paths_XY[i] = {}
            for j in G_graph_I[i]:
                if(not G_paths_XY.has_key(j)):
                    G_paths_XY[j] = {}

                path1 = self.compute_path(G_locs_XY[:,i], G_locs_XY[:,j])
                path2 = array([list(reversed(path1[0])), list(reversed(path1[1]))])
                
                G_paths_XY[i][j] = path1
                G_paths_XY[j][i] = path2
              
        return G_graph_I, G_paths_XY, G_locs_XY


    def get_interest_graph(self):
        #get the graph
        G, I = self.get_graph()

        #get the indices of the interest points in all pts
        interest_XY = array(self.get_interest_points())
        allpts_XY =  self.ind_to_xy(I)
        interest_I = self.get_indices(interest_XY, allpts_XY)

        #create the graph
        G_interest = {}
        for ind in interest_I:
            G_interest[ind] = []

            Gdone = []
            myq = deque(G[ind])
            while(len(myq) > 0):
                e = myq.popleft()

                if(e in interest_I):
                    #print "in G-interest", ind, e
                    if(e not in G_interest[ind]):
                        G_interest[ind].append(e)
                else:
                    Gdone.append(e)
                    #add the connections of G
                    for conn in G[e]:
                        if(not conn in Gdone):
                            myq.append(conn)

        return G_interest, allpts_XY


    def get_indices(self, query_XY, model_XY):
        #get the locations of the interest points
        interest_I = []
        for i in range(len(query_XY[0])):
            xy_int = query_XY[:,i]
            for j in range(len(model_XY[0])):
                xy_elt = model_XY[:,j]
                if((xy_int == xy_elt).all()):
                    interest_I.append(j)
                    break

        #print "ind_interest", interest_I
        if(len(interest_I) != len(query_XY[0])):
            print "tmap error"
            exit(0)

        return interest_I



