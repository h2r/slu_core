from pyTklib import kNN_index, math2d_line_length, math2d_centroid, tklib_normalize_theta
from scipy import transpose, ones, nan, ceil, linspace, arange, array, mean
from copy import deepcopy
from semantic_map.carmen import *
from scipy import transpose, ones, nan, pi, fabs
from dcrf3.dataset import *
from cost_util import *

class optimizer_engine:
    def __init__(self, sem_map, resolution_dist, num_next_alignments, num_landmarks):
        
        #store the parameters of the partitions
        self.resolution_dist = resolution_dist
        self.num_next_alignments = num_next_alignments
        self.num_landmarks = num_landmarks
        
        #load the semantic map
        self.map_sem = sem_map
        
        print "getting destination poses"
        #store the start and destination poses
        self.start_poses = self.map_sem.get_regions_poses()
        self.dest_poses = deepcopy(self.start_poses)
        
        #initialize partitions
        self.partitions = self.initialize_partitions(self.start_poses, self.dest_poses)
        
    def initialize_paths(self, start_poses, dest_poses):
        paths = []
        for i, pst in enumerate(start_poses):
            print "initializing", i, "of", len(start_poses)
            d, paths_p_st = self.map_sem.map_rrg.get_path_xyth_interpolate(pst, transpose(dest_poses))
            paths.append(paths_p_st)
            
        return paths
    
    
    def initialize_partitions(self, start_poses, dest_poses):
        partitions = []

        print "initialize paths"
        paths = self.initialize_paths(start_poses, dest_poses)
        
        #compute the paths between all destinations and the partition according to the 
        #  result
        print "initialize partitions"
        for i, pst in enumerate(start_poses):
            print "destination:", i, "of", len(start_poses)

            tmp_partitions = []
            for j, pdst in enumerate(dest_poses):
                path_xyth = paths[i][j]
                
                #create a partitioning of the path
                tmp_partitions.append(path_partition(path_xyth, 
                                                     self.map_sem.landmarks, 
                                                     self.resolution_dist, 
                                                     self.num_next_alignments, 
                                                     self.num_landmarks))
            partitions.append(tmp_partitions)
                
        return partitions

    
    def get_initial_configurations(self, pose_st):
        ret_configurations = []
        
        #propose all the destinations and the first alignments
        # for each of the first elements
        s_I = kNN_index(pose_st[0:2], transpose(self.start_poses)[0:2], 10);
        
        s_i = None
        for i in s_I:
            if(fabs(tklib_normalize_theta(self.start_poses[int(i)][2]-pose_st[2])) < pi/4.0):
                s_i = int(i)
                break;
        
        if(s_i == None):
            print "couldn't fine a candidate start location"
            return []

        for d_i, dst in enumerate(self.dest_poses):
            #print "starting d_i=", d_i, 'of', len(self.dest_poses)
            
            if(tklib_euclidean_distance(dst[0:2], pose_st[0:2]) < 10e-5):
                continue
            
            start_confs = self.partitions[s_i][d_i].init_alignments(s_i, d_i)
            ret_configurations.extend(start_confs)
            
        return ret_configurations


    def next_configuration_sequences(self, conf_end):
        #get the alignments from starting at the end configuration
        new_alignment = self.partitions[conf_end.d_st_i][conf_end.d_end_i].next_alignments(conf_end)
        
        return new_alignment

    def configuration_sequence_to_continuous_observation(self, sdcs, conf_seq):
        assert len(sdcs) == len(conf_seq);

        ppaths = []; lmarks = [];

        for conf in conf_seq:
            partition = self.partitions[conf.d_st_i][conf.d_end_i]
            ppaths.append(partition.get_path_segment(conf.a_st, conf.a_end))
            lmarks.append(self.map_sem.landmarks[conf.lmark_i])
        
        f_OBS, f_OBS_names, f_TRANS, f_TRANS_names = self.map_sem.get_features(sdcs, ppaths, lmarks)
        
        
        #extract the landmarks
        #lmarks = [self.map_sem.landmarks[j] for j in lmarks_I]
        
        #print "full path", partition.path
        #print "part_I:", partition.part_I
        
        #create a continuous observation
        co = continuous_observation(ones(len(sdcs), dtype='bool'), 
                                    f_OBS, f_OBS_names, f_TRANS, f_TRANS_names, 
                                    sdcs=sdcs, figures_xyth=ppaths, 
                                    grounds_xy=lmarks);

        '''mypath = []
        for i in range(len(ppaths)):
            mypath.append([ppaths[i][0][-1],ppaths[i][1][-1]])
        print mypath'''
        
        #raw_input()
        return co



class path_partition:
    def __init__(self, path, landmarks, resolution_dist,
                 num_next_alignments, num_landmarks):
        self.path = array(path)
        self.landmarks = landmarks
        
        self.resolution_dist = resolution_dist
        self.num_next_alignments = num_next_alignments
        self.num_landmarks = num_landmarks
        
        #print "path:", path
        
        #part_I[j] returns the index into the path corresponding
        #   to the start of the jth segment
        self.part_I = self.get_path_partitions_I()
        #print "part_I", self.part_I
        #print "number of elements:", len(self.part_I)
        
        #landmarks_I[i,j] returns the landmarks associated with
        #  the a_i, a_j alignment
        self.landmarks_I = self.get_landmarks_I()
        
    
    def init_alignments(self, st_i, end_i):
        num_aligns = len(self.part_I)
        
        alignments = []
        a1_new = 0;
        for j in range(self.num_next_alignments):
            a2_new = j;
            
            if(a2_new > num_aligns-1):
                continue
            
            for l in self.landmarks_I[(a1_new, a2_new)]:
                alignments.append(crf_configuration(st_i, end_i,
                                                    a1_new, a2_new, int(l)))

        return alignments;
        
    def next_alignments(self, conf):
        num_aligns = len(self.part_I)
        
        #set up the alignments
        alignments = []
        
        for i in range(-1,2):
            a1_new = conf.a_end + i
            for j in range(self.num_next_alignments):
                a2_new = a1_new + j
                
                if(a1_new < 0 or a1_new > num_aligns-1 or
                   a2_new < 0 or a2_new > num_aligns-1):
                    continue
                
                for l in self.landmarks_I[(a1_new, a2_new)]:
                    alignments.append(crf_configuration(conf.d_st_i, conf.d_end_i,
                                                        a1_new, a2_new, int(l)))
        return alignments


    def get_path_segment(self, a_st, a_end):
        i_st = int(self.part_I[a_st])
        i_end = int(self.part_I[a_end])
        
        if(i_st == len(self.path[0])):
            path_seg = self.path[:,max(0, i_st-1):i_end]
        elif(i_st == i_end):
            path_seg = self.path[:,i_st:min(len(self.path[0]), i_end+1)]
        else:
            path_seg = self.path[:,i_st:i_end+1]
            
        return path_seg

    def get_path_partitions_I(self):
        #d = spatial_features_integrate_path(self.path);
        #d = math2d_line_length(self.path)
        #num_steps = max(2, ceil(d/self.resolution_dist))
        #I = ceil(linspace(0, len(self.path[0]), min(num_steps, len(self.path[0])+1)))
        #if(num_steps > len(self.path[0])-1):
        #     pass
            
        I = [0]
        curr_index = 0;
        while(curr_index+1 < len(self.path[0])):
            curr_d = 0;
            while(curr_index+1 < len(self.path[0])):
                curr_index+=1;
                curr_d += tklib_euclidean_distance(self.path[:2,curr_index-1], self.path[:2,curr_index])
                if(curr_d > self.resolution_dist):
                    #print "curr_d:", curr_d
                    #print self.path[:,curr_index]
                    break;
            
            #if(curr_index < len(self.path[0])-1):
            #    curr_index+=1
            I.append(curr_index)

        #add the last element if it hasn't already been added
        if(I[-1] != len(self.path[0])-1):
            I.append(len(self.path[0])-1)
        
        return I

    def get_landmarks_I(self):
        landmarks = {}
        lmark_centroids_xy = self.get_landmark_centroids()

        for k in range(len(self.part_I)):
            for l in arange(self.num_next_alignments)+k:
                if(l > len(self.part_I)-1):
                    continue
                
                ppath = self.get_path_segment(k, l)
                path_com_xy = mean(ppath, axis=1)
                landmarks[(k,l)] = kNN_index(path_com_xy, lmark_centroids_xy, 
                                             min(self.num_landmarks, len(self.landmarks)));
                                                 
        
        return landmarks


    def get_landmark_centroids(self):
        #cache landmark means
        
        lmarks_xy = []
        for lmark in self.landmarks:
            if(len(lmark.XY) > 0):
                lmarks_xy.append(math2d_centroid(lmark.XY));
            else:
                lmarks_xy.append([nan, nan]);

        lmarks_xy = transpose(lmarks_xy)
        return lmarks_xy



