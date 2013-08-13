import cPickle
from heapq import *
from copy import deepcopy
from optimizer_util import *
from dcrf3.dataset import *
from srch.beam_search import beam_search
from cost_util import *
from srch.search_util import *
from copy import deepcopy

class crf_configuration_topological:
    def __init__(self, topological_nodes_I, lmark_i, num_historical_nodes=0, initial_pose=None):
        self.topo_nodes_I = topological_nodes_I
        self.lmark_i = lmark_i
        self.num_historical_nodes = num_historical_nodes
        self.value = None
        self.initial_pose = initial_pose
        
    def __repr__(self):
        return "path="+str(self.topo_nodes_I)+" landmark:"+str(self.lmark_i)+" val:"+str(self.value)

    def __str__(self):
        return "path="+str(self.topo_nodes_I)+" landmark:"+str(self.lmark_i)+" val:"+str(self.value)


class beam_search_topological:
    def __init__(self, cost_function, conf_beam_width=10, path_beam_width=100, path_max_depth=6):
        self.cf = cost_function
        
        init_confs = self.cf.initialize()

        self.heap = []
        for c in init_confs:
            c.value = self.cf.value([c])
            heappush(self.heap, (c.value, [c]))

        self.conf_beam_width=conf_beam_width        
        self.path_beam_width=path_beam_width        
        self.path_max_depth=path_max_depth        
        
    def step_conf(self):
        new_heap = []
        j = 0
        for i in range(min(self.conf_beam_width, len(self.heap))):
            c, conf_path = heappop(self.heap)
            next_confs = self.cf.next_conf(conf_path)

            print "evaluating configuration", i, "of", self.conf_beam_width, "for", len(next_confs), "elements", conf_path
            for conf_end in next_confs:
                curr_path = deepcopy(conf_path)
                curr_path.append(conf_end)
                
                if(conf_end.value == None):
                    conf_end.value = self.cf.value(curr_path)
                
                heappush(new_heap, (conf_end.value, curr_path))
                j+= 1
            
            #heappush(new_heap, (c, conf_path))
        
        c, conf_path = heappop(new_heap)
        print j, " evaluations", "cost=", c, 'path=', conf_path, "heap_size=", len(new_heap)
        heappush(new_heap, (c, conf_path))
        
        self.heap = new_heap


    def step_path(self, curr_depth):
        new_heap = []
        j = 0
        for i in range(min(self.path_beam_width, len(self.heap))):
            c, conf_path = heappop(self.heap)
            
            if(len(conf_path[-1].topo_nodes_I)-conf_path[-1].num_historical_nodes < curr_depth):
                heappush(new_heap, (c, conf_path))
                continue
            
            next_confs = self.cf.next_path(conf_path)
            for conf_end in next_confs:
                curr_path = deepcopy(conf_path[:-1])
                curr_path.append(conf_end)
                
                if(conf_end.value == None):
                    conf_end.value = self.cf.value(curr_path)
                    j+=1
                
                heappush(new_heap, (conf_end.value, curr_path))
                
        c, conf_path = heappop(new_heap)
        print "--------------------------------------------"
        print j, " evaluations", "cost=", c, "path=", conf_path, "heap_size=", len(new_heap)
        heappush(new_heap, (c, conf_path))
        
        #for e in new_heap:
        #    print e[1]
        #raw_input()

        self.heap = new_heap
        

    def minimum(self):
        min_conf = heappop(self.heap)
        heappush(self.heap, min_conf)
        return min_conf


class crf_cost_topological(cost_function):
    def __init__(self, start_pose, sdcs, model, opt):
        self.model = model
        self.sdcs = sdcs
        self.start_pose = start_pose
        self.opt = opt

    def initialize(self):
        oe_confs = self.opt.initial_configurations(self.start_pose)
        
        return oe_confs
    
    def next_conf(self, conf):
        confs_new = self.opt.next_configuration_sequences(conf)
        
        return confs_new

    def next_path(self, conf):
        confs_new = self.opt.next_path_sequences(conf)
        
        return confs_new

    def value(self, conf_seq):
        assert len(conf_seq) <= len(self.sdcs)
        
        #print self.sdcs[:len(conf_seq)]
        #print conf_seq
        dobs = self.opt.to_discrete_observation(self.sdcs[:len(conf_seq)], 
                                                conf_seq)

        p = self.model.log_probability(dobs)
        
        return -1*p


class optimizer:
    def __init__(self,  model_filename, semantic_map_filename, map_filename,
                 landmarks_filename, topological_map_filename):

        
        self.topological_map = cPickle.load(open(topological_map_filename, 'r'))        
        
        print "creating semantic map"
        self.map_sem = semantic_map(semantic_map_filename, map_filename, 
                                    landmarks_filename=landmarks_filename, create_rrg=False)

        print "loading model"
        self.model =  cPickle.load(open(model_filename, 'r'))
        
        
    def optimize(self, sdcs, start_pose, 
                 conf_beam_width=20, path_beam_width=400, path_max_depth=7):
        
        cf = crf_cost_topological(start_pose, sdcs, self.model, self)
        
        #initialize the search
        bs = beam_search_topological(cf, conf_beam_width, path_beam_width, path_max_depth)
        for j in range(bs.path_max_depth):
            print "step path:", j
            bs.step_path(j+1)


        #step to new SDCs
        for i in range(len(sdcs)-1):
            bs.step_conf()
            print "------------------------"
            print "i:", i, " of", len(sdcs)-1
            for j in range(bs.path_max_depth):
                print "step path:", j
                bs.step_path(j+1)
            

        
        #return the actual paths
        obs = []; probs = []; conf_seqs = []
        for i in range(len(bs.heap)):
            p, conf_seq = heappop(bs.heap)
            
            dobs = self.to_discrete_observation(sdcs, conf_seq);
            obs.append(dobs); probs.append(p); conf_seqs.append(conf_seq);
        
        return probs, obs, conf_seqs


    def initial_configurations(self, pose_st):
        ret_configurations = []
        
        tnode = self.topological_map.closest_node(pose_st[0:2])
        
        for lmark_i in range(len(self.map_sem.landmarks)):
            ret_configurations.append(crf_configuration_topological([tnode.index], lmark_i, initial_pose=pose_st))
        
        return ret_configurations

    def next_configuration_sequences(self, conf_seq):
        ret_configurations = []

        conf_end = conf_seq[-1]
        next_nodes = self.topological_map.next_nodes(conf_end.topo_nodes_I)
        
        for lmark_i in range(len(self.map_sem.landmarks)):        
            #if there is only one element in the previous path, add it and continue
            if(len(conf_end.topo_nodes_I)==1):
                ret_configurations.append(crf_configuration_topological(conf_end.topo_nodes_I, lmark_i))
                continue
            
            #add the alignments if the path is of length greater than 1
            #for i in range(max(-4,-len(conf_end.topo_nodes_I)),-1):
            #    ret_configurations.append(crf_configuration_topological(list(conf_end.topo_nodes_I[i:]), lmark_i, 
            #                                                            num_historical_nodes=len(conf_end.topo_nodes_I[i:])-1))

            for i in range(max(-4,-len(conf_end.topo_nodes_I)),-1):
                if(i+2 == 0):
                    ret_configurations.append(crf_configuration_topological(list(conf_end.topo_nodes_I[i:]), lmark_i, 
                                                                            num_historical_nodes=1))
                else:
                    ret_configurations.append(crf_configuration_topological(list(conf_end.topo_nodes_I[i:i+2]), lmark_i, 
                                                                            num_historical_nodes=1))
                
        return ret_configurations

    def next_path_sequences(self, conf_seq):
        ret_configurations = []
        conf_end = conf_seq[-1]
        
        next_nodes = self.topological_map.next_nodes(conf_end.topo_nodes_I)

        #add the node's connections here
        for node in next_nodes:
            #copy the last configuration and reset the value
            conf_new = deepcopy(conf_end)
            conf_end.value = None
            
            #keep going
            conf_new.topo_nodes_I.append(node.index)
            ret_configurations.append(conf_new)

        ret_configurations.append(conf_end)
        return ret_configurations

        
    def to_discrete_observation(self, sdcs, conf_seq):
        cobs = self.to_continuous_observation(sdcs, conf_seq)
        dobs = self.model.D.to_discrete_observation(cobs)
        return dobs

    
    def to_continuous_observation(self, sdcs, conf_seq):
        assert len(sdcs) == len(conf_seq);
        ppaths = []; lmarks = [];
        
        for i, conf in enumerate(conf_seq):
            #if there is an initial pose, then we should use it
            curr_path = None
            if(i == 0 and conf.initial_pose != None):
                X, Y, Th = self.topological_map.get_path(conf.topo_nodes_I)
                curr_path = [[X[0]],
                             [Y[0]],
                             [conf.initial_pose[2]]]
                curr_path[0].extend(X)
                curr_path[1].extend(Y)
                curr_path[2].extend(Th)
            else:
                curr_path = self.topological_map.get_path(conf.topo_nodes_I)
            
            ppaths.append(array(curr_path))
            #ppaths.append(self.topological_map.get_path(conf.topo_nodes_I))
            lmarks.append(self.map_sem.landmarks[conf.lmark_i])
        
        f_OBS, f_OBS_names, f_TRANS, f_TRANS_names = self.map_sem.get_features(sdcs, ppaths, lmarks)
        
        #create a continuous observation
        co = continuous_observation(ones(len(sdcs), dtype='bool'), 
                                    f_OBS, f_OBS_names, f_TRANS, f_TRANS_names, 
                                    sdcs=sdcs, figures_xyth=ppaths, 
                                    grounds_xy=lmarks);
        return co
