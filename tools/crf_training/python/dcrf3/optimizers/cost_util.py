from srch.search_util import *

class crf_configuration:
    def __init__(self, d_st_i, d_end_i, 
                 a_st_i, a_end_i, lmark_i):
        self.d_st_i = d_st_i 
        self.d_end_i = d_end_i 
        self.a_st = a_st_i
        self.a_end = a_end_i
        self.lmark_i = lmark_i

    def __repr__(self):
        return "st:"+str(self.d_st_i)+" end:"+str(self.d_end_i)+" a_st:"+str(self.a_st)+" a_end:"+str(self.a_end)+" lmark_i:"+str(self.lmark_i)

    def __str__(self):
        return "st:"+str(self.d_st_i)+" end:"+str(self.d_end_i)+" a_st:"+str(self.a_st)+" a_end:"+str(self.a_end)+" lmark_i:"+str(self.lmark_i)


class crf_cost(cost_function):
    def __init__(self, start_pose, sdcs, model, oe):
        self.model = model
        self.oe = oe
        self.sdcs = sdcs
        self.start_pose = start_pose

    def initialize(self):
        oe_confs = self.oe.get_initial_configurations(self.start_pose)
        
        return oe_confs
    
    def next(self, conf):
        confs_new = self.oe.next_configuration_sequences(conf)
        
        return confs_new

    def value(self, conf_seq):
        assert len(conf_seq) <= len(self.sdcs)
        
        dobs = self.configuration_sequence_to_discrete_observation(self.sdcs[:len(conf_seq)], 
                                                                   conf_seq)
        p = self.model.log_probability(dobs)
        
        return -1*p

    def configuration_sequence_to_discrete_observation(self, sdcs, conf_seq):
        cobs = self.oe.configuration_sequence_to_continuous_observation(sdcs, conf_seq)
        dobs = self.model.D.to_discrete_observation(cobs)
        
        return dobs

