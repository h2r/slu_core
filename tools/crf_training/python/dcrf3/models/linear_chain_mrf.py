from scipy import optimize, exp, log, zeros, dot, array, isnan, isinf, mod, amax, argmax
from scipy.linalg.basic import norm
from math_util import combinations_self
from copy import deepcopy, copy
from dcrf2.datasets.linear_chain_dataset import observation
from scipy import random, shape, exp, log, transpose, tile, sum

class linear_chain_mrf:
    
    def __init__(self, dataset):
        self.D = dataset
        
        self.P_obs, self.P_trans, self.P_prior = self.D.get_feature_counts_mrf()

        #print "denominator:", sum(self.P_obs, axis=1)
        #raw_input()

        #print "denominator:", transpose(tile(sum(self.P_obs, axis=1), 
        #                                     (len(self.P_obs[0]), 1)))
        #print "normalization:", transpose(tile(sum(self.P_obs, axis=0), 
        #print "len(summation()", len(sum(self.P_obs, axis=0))
        #Z = sum(self.P_obs, axis=0)

        self.f_obs_cnt = self.D.observations_count()
        self.P_obs = log(self.P_obs+1) - log(self.f_obs_cnt+2)

        print "obs:", self.P_obs
        #print "log(P_obs):", self.P_obs
        #print "P_obs:", exp(self.P_obs)

        #print "counts:", self.P_trans
        #print "probs:", (1.0*tile(sum(self.P_trans, axis=1), 
        #                          (len(self.P_trans[0]), 1)))

        self.f_trans_cnt = self.D.transitions_count()
        print "f_trans_cnt", self.f_trans_cnt
        self.P_prior = log(self.P_prior+1) - log(sum(self.P_prior, axis=1)+len(self.P_prior[0]));
        
        print "prior:", self.P_prior
        print sum(exp(self.P_prior), axis=1)
        
        #print "len:", shape(self.P_prior[0])
        
        
        #print "total", exp(sum(self.P_prior[1]))
        '''denom = (1.0*tile(sum(self.P_trans, axis=1), 
                          (len(self.P_trans[0]), 1)))
        print shape(denom)
        print shape(self.P_trans)
        self.P_trans = log(self.P_trans/denom)'''
                                                  

        
    def log_probability(self, d):
        #print "------------------------"
        #print "new data point"
        f_obs = d.to_array_obs(self.D.name_to_num_obs(), self.D.num_obs)
        f_trans = d.to_array_trans(self.D.name_to_num_trans(), self.D.num_trans)
        f_output = d.to_array_output(self.D.name_to_num_output(), self.D.num_output)
        
        #print "labels:", d.labels
        ohash = self.D.name_to_num_output()

        #print "ohash", ohash
        lp = 0
        for i in range(len(f_obs)):
            #print "ohash:", ohash
            #print "d.labels:", d.labels[i]
            #print "probs:", len(self.P_obs[ohash[d.labels[i]]])
            #print "f_obs[i]", sum(f_obs[i]), 
            #print "prob=", exp(sum(self.P_obs[ohash[d.labels[i]]]*f_obs[i]))
            
            lp += sum(self.P_obs[ohash[d.labels[i]]]*f_obs[i])
            lp += sum((log(1-exp(self.P_obs[ohash[d.labels[i]]])))*(1-f_obs[i]))
            
        #print "obs prob:", lp, exp(lp)
        pri_tmp = 0
        for i in range(1,len(d.labels)):
            lp +=self.P_prior[ohash[d.labels[i-1]]][ohash[d.labels[i]]]
            pri_tmp += self.P_prior[ohash[d.labels[i-1]]][ohash[d.labels[i]]]

        return lp


        
