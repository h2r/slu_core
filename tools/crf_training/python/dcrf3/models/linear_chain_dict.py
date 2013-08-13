from scipy import optimize, exp, log, zeros, dot, array, isnan, isinf, mod, amax, argmax
from scipy.linalg import norm
from math_util import combinations_self
from copy import deepcopy, copy
from dcrf3.dataset import DiscreteObservation
from scipy import random, shape, exp, nan
import cPickle

class linear_chain_crf:
    def __init__(self, dataset, sigma=1.0):
        
        #print "linear chain dict"
        #raw_input()
        self.D = dataset
        self.sigma = sigma
        
        random.seed(0)
        self.W_obs = random.random(self.D.get_num_features_obs()*self.D.num_output)*1.0
        self.W_trans = random.random(self.D.get_num_features_trans()*(self.D.num_output**2.0))*1.0
        
        self.fc_obs, self.fc_trans = self.D.get_feature_counts()
    
    def save(self, filename):
        cPickle.dump(self, open(filename, 'wb'))

    def unload(self):
        pass
    
    def set_observations(self, obs):
        self.D.observations = obs
        self.fc_obs, self.fc_trans = self.D.get_feature_counts()

        
    def train(self):
        print "training"
        self.theta = list(self.W_obs)
        self.theta.extend(self.W_trans)
        
        self.theta = optimize.fmin_l_bfgs_b(self.negative_data_log_likelihood, 
                                            self.theta,
                                            self.compute_log_gradient, pgtol=0.25)
        
        self.theta = self.theta[0]
        self.W_obs = self.theta[0:len(self.W_obs)]
        self.W_trans = self.theta[len(self.W_obs):]
        
        #print "theta:", self.theta
        print "likelihood:", self.negative_data_log_likelihood(self.theta)
        
        
    def negative_data_log_likelihood(self, theta):
        self.W_obs = theta[0:len(self.W_obs)]
        self.W_trans = theta[len(self.W_obs):]
        
        lp = 0
        for i, d in enumerate(self.D.observations):
            if(mod(i+1, 200) == 0):
                print i, "of", len(self.D.observations), ":", -1.0*lp
            
            assert self.log_probability > 0
            lp += self.log_probability(d)

        rlp = -1.0*lp
        rlp += dot(theta, theta)/(2*(self.sigma**2.0))
        
        print "data likelihood", rlp
        return rlp
    
    def __compute_log_Z__(self, lalpha):
        j_max = argmax(lalpha[:,-1])
        lZ = lalpha[j_max,-1] + log(1 + (sum(exp(lalpha[:,-1] - lalpha[j_max,-1]))-exp(0)))
        
        #lalpha[k,i] = log(1+lalpha[k,i])+alpha_max[k]
        return lZ

    def __compute_log_Z_beta__(self, lbeta):
        j_max = argmax(lbeta[:,0])
        lZ = lbeta[j_max,0] + log(1 + (sum(exp(lbeta[:,0] - lbeta[j_max,0]))-exp(0)))
        
        return lZ

    def predict(self, d):
        lalpha, parents = self.__log_forward_backward_alpha_predict__(d)

        alp = self.D.get_output_alphabet()
        path = [argmax(lalpha[:,-1])]

        for i in reversed(range(len(parents[0]))):
            path.append(parents[path[-1],i])
        
        output = []
        for e in path:
            output.append(alp[int(e)])
        
        return list(reversed(output)), lalpha[path[-1],-1]

    def __log_forward_backward_alpha_predict__(self, d):
        alp = self.D.get_output_alphabet()
        
        #initialize the relevant variables
        lalpha = zeros([len(alp), len(d.features_obs)])*1.0
        parents = zeros([len(alp), len(d.features_obs)-1])*1.0
        alpha_max = zeros(len(alp))
        
        for i in range(len(d.features_obs)):
            #pre-compute the maximum value alpha transitions for the current time
            #  see CRF-OPT paper for more details
            #now compute the acutal values of alpha
            for j in range(len(alp)):
                if(i == 0):
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[j]], [d.features_obs[i]], [])
                    lalpha[j,i] = sum(self.W_obs.take(f_obs_I[0]))
                    continue
                    
                for k in range(len(alp)):
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[j], alp[k]],
                                                                 [d.features_obs[i-1], 
                                                                  d.features_obs[i]], 
                                                                 [d.features_trans[i-1]]);

                    f_val = sum(self.W_obs.take(f_obs_I[1]))+sum(self.W_trans.take(f_trans_I[0]))
                    
                    if(f_val+lalpha[j,i-1] > lalpha[k,i]):
                        lalpha[k,i] = f_val + lalpha[j,i-1]
                        parents[k,i-1] = j
        
        return lalpha, parents

    
    def log_probability(self, d):
        lalpha, lbeta = self.log_forward_backward(d)
        
        lp = self.log_probability_compute_numerator(d)
        lZ = self.__compute_log_Z__(lalpha)
        
        return lp-lZ

    def log_probability_compute_numerator(self, d):
        f_obs_I, f_trans_I = self.D.get_features_I(d)
        
        v=0
        for i in range(len(f_obs_I)):
            v += sum(self.W_obs.take(f_obs_I[i]))
            if(i < len(f_obs_I)-1):
                v+=sum(self.W_trans.take(f_trans_I[i]))
                
        return v

    def export_weights(self):
        alp = self.D.get_output_alphabet()
        
        obs_hash = {}; trans_hash={}
        for a in alp:
            trans_hash[a] = {}
            for b in alp:
                d = DiscreteObservation([a,b], 
                                         [self.D.get_obs_alphabet(),
                                          self.D.get_obs_alphabet()],
                                         [self.D.get_trans_alphabet()])
            
                W_obs, W_trans = self.get_weights(d)
                obs_hash[a] = dict(zip(self.D.get_obs_alphabet(), W_obs[0]))
                trans_hash[a][b] = dict(zip(self.D.get_trans_alphabet(), W_trans[0]))
        return obs_hash, trans_hash

    def import_weights(self, obs_hash, trans_hash):
        alp = self.D.get_output_alphabet()
        
        for a in alp:
            f_obs_names = obs_hash[a].keys()
            for b in alp:
                f_trans_names = trans_hash[a][b].keys()
                
                d = DiscreteObservation([a,b], 
                                         [f_obs_names, f_obs_names], [f_trans_names])
                
                f_obs_I, f_trans_I = self.D.get_features_I(d, use_nan=True)
                
                for i, f_i in enumerate(f_obs_I[0]):
                    if(not isnan(obs_hash[a][f_obs_names[i]]) 
                       and not isnan(f_i)):
                        self.W_obs[f_i] = obs_hash[a][f_obs_names[i]]

                for i, f_i in enumerate(f_trans_I[0]):
                    if(not isnan(trans_hash[a][b][f_trans_names[i]]) 
                       and not isnan(f_i)):
                        self.W_trans[f_i] = trans_hash[a][b][f_trans_names[i]]

    def get_weights(self, obs):
        f_obs_I, f_trans_I = self.D.get_features_I(obs, use_nan=True)
        
        W_obs = []
        for j, f_obs_i in enumerate(f_obs_I):
            wo = []
            for i, f_j in enumerate(f_obs_i):
                if(not isnan(f_j)): 
                    wo.append(self.W_obs[f_j])
                else:
                    #print "weights null:", f_j, obs.features_obs[j][i]
                    wo.append(-10e100)
            W_obs.append(wo)
            
        W_trans = []
        for f_trans_i in f_trans_I:
            wt = []
            for f_j in f_trans_i:
                if(not isnan(f_j)):
                    wt.append(self.W_trans[f_j])
                else:
                    wt.append(-10e100)
            W_trans.append(wt)
        
        return W_obs, W_trans
        

    #helper function to clean up the code around getting features
    #  uses an internal variable _obs_ that would break any parallelization
    #  attempts
    def __get_features_I__(self, labels, features_obs, features_trans):
        self._obs_ = DiscreteObservation([], [], [])
        self._obs_.labels=labels
        self._obs_.features_obs =features_obs
        self._obs_.features_trans =features_trans
        
        f_obs_I, f_trans_I = self.D.get_features_I(self._obs_)
        
        return f_obs_I, f_trans_I


    def __compute_log_alpha__(self, d):
        alp = self.D.get_output_alphabet()
        
        #initialize the relevant variables
        lalpha = zeros([len(alp), len(d.features_obs)])*1.0
        alpha_max = zeros(len(alp))
        
        for i in range(len(d.features_obs)):
            #pre-compute the maximum value alpha transitions for the current time
            #  see CRF-OPT paper for more details
            j_max = None
            if(i != 0):
                j_max = argmax(lalpha[:,i-1])
            for k in range(len(alp)):
                if(i == 0):
                    break
                f_obs_I, f_trans_I = self.__get_features_I__([alp[j_max], alp[k]], 
                                                             [d.features_obs[i-1], 
                                                              d.features_obs[i]], 
                                                             [d.features_trans[i-1]])
                
                #f_val = dot(self.W_obs, f_obs[1])+dot(self.W_trans, f_trans[0])
                f_val = sum(self.W_obs.take(f_obs_I[1]))+sum(self.W_trans.take(f_trans_I[0]))
                alpha_max[k]=f_val+lalpha[j_max,i-1]
                
            #now compute the acutal values of alpha
            for j in range(len(alp)):
                if(i == 0):
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[j]], [d.features_obs[i]], [])
                    lalpha[j,i] = sum(self.W_obs.take(f_obs_I[0]))
                    continue
                    
                for k in range(len(alp)):
                    if(j == j_max):
                        continue
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[j], alp[k]],
                                                                 [d.features_obs[i-1], 
                                                                  d.features_obs[i]], 
                                                                 [d.features_trans[i-1]]);
                    
                    f_val = sum(self.W_obs.take(f_obs_I[1]))+sum(self.W_trans.take(f_trans_I[0]))
                    lalpha[k,i] += exp(lalpha[j,i-1]+f_val-alpha_max[k])
            
            if(i == 0):
                continue

            #add back in the beta_max
            for k in range(len(alp)):
                lalpha[k,i] = log(1+lalpha[k,i])+alpha_max[k]

        return lalpha
    
    def __compute_log_beta__(self, d):
        alp = self.D.get_output_alphabet()
        
        #initialize the relevant variables
        lbeta = zeros([len(alp), len(d.features_obs)])*1.0
        
        for i in reversed(range(len(d.features_obs))):
            #pre-compute the maximum value beta transitions for the current time
            #  see CRF-OPT paper for more details
            j_max = None
            beta_max = zeros(len(alp))
            
            if(i < len(d.features_obs)-1):
                j_max = argmax(lbeta[:,i+1])
                
                for k in range(len(alp)):
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[k], alp[j_max]], 
                                                                 [d.features_obs[i], 
                                                                  d.features_obs[i+1]], 
                                                                 [d.features_trans[i]])
                    f_val = sum(self.W_obs.take(f_obs_I[0]))+sum(self.W_trans.take(f_trans_I[0]))
                    beta_max[k]=f_val+lbeta[j_max,i+1]
                
            #now compute the acutal values of beta
            for j in range(len(alp)):
                if(i == len(d.features_obs)-1):
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[j]], [d.features_obs[i]], [])
                    lbeta[j,i] = sum(self.W_obs.take(f_obs_I[0]))
                    continue
                    
                for k in range(len(alp)):
                    if(j == j_max):
                        continue
                    f_obs_I, f_trans_I = self.__get_features_I__([alp[k], alp[j]],
                                                                 [d.features_obs[i], 
                                                                  d.features_obs[i+1]], 
                                                                 [d.features_trans[i]]);
                    
                    f_val = sum(self.W_obs.take(f_obs_I[0]))+sum(self.W_trans.take(f_trans_I[0]))
                    lbeta[k,i] += exp(lbeta[j,i+1]+f_val-beta_max[k])

            if(i == len(d.features_obs)-1):
                continue
            
            #add back in the beta_max
            for k in range(len(alp)):
                lbeta[k,i] = log(1+lbeta[k,i])+beta_max[k]

        return lbeta

    def log_forward_backward(self, d):
        lalpha = self.__compute_log_alpha__(d)
        lbeta = self.__compute_log_beta__(d)
        return lalpha, lbeta

    def compute_log_gradient(self, theta):
        self.W_obs = theta[0:len(self.W_obs)]
        self.W_trans = theta[len(self.W_obs):]
        
        f_obs_exp = zeros(len(self.W_obs))
        f_trans_exp = zeros(len(self.W_trans))
        
        for i, d in enumerate(self.D.observations):
            if(mod(i+1, 200) == 0):
                print i, "grad. of", len(self.D.observations)
            
            f_obs_e, f_trans_e = self.compute_expected_feature_count(d)
            f_obs_exp+=f_obs_e
            f_trans_exp+=f_trans_e

        obs_grad = self.fc_obs - f_obs_exp
        trans_grad = self.fc_trans - f_trans_exp

        ret_val = []
        ret_val.extend(obs_grad)
        ret_val.extend(trans_grad)
        ret_val = array(ret_val)
        
        #because we're minimizing the negative log likelihood
        ret_val*=-1.0
        ret_val+=theta/(self.sigma**2.0)
        print "max", amax(ret_val)
        
        i = argmax(obs_grad)
        print "diff:", obs_grad[i], " features:", self.fc_obs[i], " expectation:", f_obs_exp[i]
        
        return ret_val

    
    def compute_expected_feature_count(self, d):
        #initialize the arrays
        f_exp_obs = zeros(len(self.W_obs))
        f_exp_trans = zeros(len(self.W_trans))

        #perform forward backward
        lalpha, lbeta = self.log_forward_backward(d)
        lZ = self.__compute_log_Z__(lalpha)
        #Z = sum(alpha[:,-1])
        
        #get the output alphabet
        alp = self.D.get_output_alphabet()
        ntonum_oput = self.D.name_to_num_output()
        
        #o = observation([],[],[])
        #iterate through
        for i in range(len(d.features_obs)):
            for y1 in alp:
                #do the base case
                f_obs_I, f_trans_I = self.__get_features_I__([y1], [d.features_obs[i]], [])
                lprob = lalpha[ntonum_oput[y1],i]+lbeta[ntonum_oput[y1],i]-sum(self.W_obs.take(f_obs_I[0]))
                lprob = lprob-lZ
                
                f_exp_obs[f_obs_I[0]] += exp(lprob)
                
                if(i == 0):
                    continue
                
                #iterate through the rest
                for y2 in alp:
                    f_obs_I, f_trans_I = self.__get_features_I__([y1,y2], 
                                                                 [d.features_obs[i-1],
                                                                  d.features_obs[i]], 
                                                                 [d.features_trans[i-1]])
                    
                    lprob = sum(self.W_trans.take(f_trans_I[0]))
                    lprob += lalpha[ntonum_oput[y1],i-1]+lbeta[ntonum_oput[y2],i]

                    #not sure about this
                    #lprob -= dot(self.W_obs, f_obs[1]) + dot(self.W_obs, f_obs[0])
                    lprob = lprob-lZ
                        
                    f_exp_trans[f_trans_I[0]] += exp(lprob)

        return f_exp_obs, f_exp_trans
