import cPickle
from heapq import *
from pyTklib import kNN_index, tklib_euclidean_distance
from copy import deepcopy
from optimizer_util import *
from dcrf3.dataset import *
from srch.beam_search import beam_search
from cost_util import *

class optimizer:
    def __init__(self,  model_filename, semantic_map_filename, 
                 map_filename, landmarks_filename, 
                 resolution, alignment_steps, num_nearest_landmarks, beam_width=10):
        print "creating semantic map"
        self.map_sem = semantic_map(semantic_map_filename, map_filename, 
                                    landmarks_filename=landmarks_filename)
        
        print "creating optimizer engine"
        self.oe = optimizer_engine(self.map_sem, resolution, 
                                   alignment_steps, num_nearest_landmarks)
        
        self.model =  cPickle.load(open(model_filename, 'r'))
        
        self.beam_width = beam_width

    def initial_configurations(self, start_pose):
        return self.oe.get_initial_configurations(start_pose)

    def next(self, conf_seq):
        next_confs = self.oe.next_configuration_sequences(conf_seq[-1])
        return next_confs

    def to_discrete_observation(self, sdcs, conf_seq):
        cobs = self.oe.configuration_sequence_to_continuous_observation(sdcs, conf_seq)
        dobs = self.model.D.to_discrete_observation(cobs)
        
        return dobs

    def optimize(self, sdcs, start_pose):
        cf = crf_cost(start_pose, sdcs, self.model, self.oe)
        
        #perform the search
        bs = beam_search(cf, self.beam_width)
        
        for i in range(len(sdcs)-1):
            print "i:", i, " of", len(sdcs)-1
            bs.step()
        
        #return the actual paths
        obs = []; probs = []; conf_seqs = []
        for i in range(len(bs.heap)):
            p, conf_seq = heappop(bs.heap)

            dobs = cf.configuration_sequence_to_discrete_observation(sdcs, conf_seq);
            obs.append(dobs); probs.append(p); conf_seqs.append(conf_seq);
        
        return probs, obs, conf_seqs


