from scipy import optimize, exp, log, zeros, dot, array, isnan, isinf, mod, amax, argmax
from scipy.linalg.basic import norm
from math_util import combinations_self
from copy import deepcopy, copy
from dcrf2.datasets.linear_chain_dataset import observation
from scipy import random, shape, exp


class linear_chain_crf:
    def __init__(self, dataset, sigma=1.0):
        self.D = dataset
        
        self.sigma = sigma
        
        #self.W_obs = zeros(self.D.get_num_features_obs()*self.D.num_output)*1.0
        #self.W_trans = zeros(self.D.get_num_features_trans()*(self.D.num_output**2.0))*1.0
        
        random.seed(0)
        self.W_obs = random.random(self.D.get_num_features_obs()*self.D.num_output)*1.0
        self.W_trans = random.random(self.D.get_num_features_trans()*(self.D.num_output**2.0))*1.0
        
        self.fc_obs, self.fc_trans = self.D.get_feature_counts()
        
        #print self.fc_trans
        #name_to_num_trans = self.D.name_to_num_trans()
        #print "1:", self.fc_trans[name_to_num_trans["orient_dir_end_pp_0.0_0.0526315789474"]]
        #print "2:", self.fc_trans[name_to_num_trans["orient_dir_end_pp_0.0_0.0526315789474"]+self.D.num_trans]
        #print "3:", self.fc_trans[name_to_num_trans["orient_dir_end_pp_0.0_0.0526315789474"]+2*self.D.num_trans]
        #print "4:", self.fc_trans[name_to_num_trans["orient_dir_end_pp_0.0_0.0526315789474"]+3*self.D.num_trans]
        #raw_input()
        #self._obs_ = observation([], [], [])
        
        
    def train(self):
        print "training"
        self.theta = list(self.W_obs)
        self.theta.extend(self.W_trans)
        
        self.theta = optimize.fmin_l_bfgs_b(self.negative_data_log_likelihood, 
                                            self.theta,
                                            self.compute_log_gradient, pgtol=0.25)
        
        #self.theta = optimize.fmin_l_bfgs_b(self.negative_data_log_likelihood, 
        #                                    self.theta, approx_grad=True, pgtol=0.25)
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
            if(mod(i+1, 1000) == 0):
                print i, "of", len(self.D.observations), ":", lp

            lp += self.log_probability(d)

        rlp = -1.0*lp
        rlp += dot(theta, theta)/(2*(self.sigma**2.0))
        
        print "data likelihood", rlp
        return rlp
    
    def __compute_log_Z__(self, lalpha):
        #print "lalpha:", lalpha
        j_max = argmax(lalpha[:,-1])
        lZ = lalpha[j_max,-1] + log(1 + (sum(exp(lalpha[:,-1] - lalpha[j_max,-1]))-exp(0)))
        
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
            output.append(alp[e])
        
        return output, lalpha[path]

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
                    f_obs, f_trans = self.__get_features__([alp[j]], [d.features_obs[i]], [])
                    lalpha[j,i] = dot(self.W_obs, f_obs[0])
                    continue
                    
                for k in range(len(alp)):
                    f_obs, f_trans = self.__get_features__([alp[j], alp[k]],
                                                           [d.features_obs[i-1], 
                                                            d.features_obs[i]], 
                                                           [d.features_trans[i-1]]);

                    f_val = dot(self.W_obs, f_obs[1])+dot(self.W_trans, f_trans[0])
                    
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
        f_obs, f_trans = self.D.get_features(d)
        
        v=0
        for i in range(len(f_obs)):
            v += dot(f_obs[i], self.W_obs)
            if(i < len(f_obs)-1):
                v+=dot(f_trans[i], self.W_trans)
                
        return v

    #helper function to clean up the code around getting features
    #  uses an internal variable _obs_ that would break any parallelization
    #  attempts
    def __get_features__(self, labels, features_obs, features_trans):
        self._obs_ = observation([], [], [])
        self._obs_.labels=labels
        self._obs_.features_obs =features_obs
        self._obs_.features_trans =features_trans
        
        f_obs, f_trans = self.D.get_features(self._obs_)
        
        return f_obs, f_trans


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
                f_obs, f_trans = self.__get_features__([alp[j_max], alp[k]], 
                                                       [d.features_obs[i-1], d.features_obs[i]], 
                                                       [d.features_trans[i-1]])

                f_val = dot(self.W_obs, f_obs[1])+dot(self.W_trans, f_trans[0])
                alpha_max[k]=f_val+lalpha[j_max,i-1]
                
            #now compute the acutal values of alpha
            for j in range(len(alp)):
                if(i == 0):
                    f_obs, f_trans = self.__get_features__([alp[j]], [d.features_obs[i]], [])
                    lalpha[j,i] = dot(self.W_obs, f_obs[0])
                    continue
                    
                for k in range(len(alp)):
                    if(j == j_max):
                        continue
                    f_obs, f_trans = self.__get_features__([alp[j], alp[k]],
                                                           [d.features_obs[i-1], 
                                                            d.features_obs[i]], 
                                                           [d.features_trans[i-1]]);
                    
                    f_val = dot(self.W_obs, f_obs[1])+dot(self.W_trans, f_trans[0])
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
                    f_obs, f_trans = self.__get_features__([alp[k], alp[j_max]], 
                                                           [d.features_obs[i], 
                                                            d.features_obs[i+1]], 
                                                           [d.features_trans[i]])
                    f_val = dot(self.W_obs, f_obs[0])+dot(self.W_trans, f_trans[0])
                    beta_max[k]=f_val+lbeta[j_max,i+1]
                
            #now compute the acutal values of beta
            for j in range(len(alp)):
                if(i == len(d.features_obs)-1):
                    f_obs, f_trans = self.__get_features__([alp[j]], [d.features_obs[i]], [])
                    lbeta[j,i] = dot(self.W_obs, f_obs[0])
                    continue
                    
                for k in range(len(alp)):
                    if(j == j_max):
                        continue
                    f_obs, f_trans = self.__get_features__([alp[k], alp[j]],
                                                           [d.features_obs[i], 
                                                            d.features_obs[i+1]], 
                                                           [d.features_trans[i]]);
                    
                    f_val = dot(self.W_obs, f_obs[0])+dot(self.W_trans, f_trans[0])
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
            if(mod(i+1, 10) == 0):
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
                f_obs, f_trans = self.__get_features__([y1], [d.features_obs[i]], [])
                lprob = lalpha[ntonum_oput[y1],i]+lbeta[ntonum_oput[y1],i]-dot(self.W_obs, 
                                                                               f_obs[0])
                lprob = lprob-lZ
                
                f_exp_obs += exp(lprob)*f_obs[0]
                
                if(i == 0):
                    continue
                
                #iterate through the rest
                for y2 in alp:
                    f_obs, f_trans = self.__get_features__([y1,y2], 
                                                           [d.features_obs[i-1],
                                                            d.features_obs[i]], 
                                                           [d.features_trans[i-1]])
                    
                    lprob = dot(self.W_trans, f_trans[0])
                    lprob += lalpha[ntonum_oput[y1],i-1]+lbeta[ntonum_oput[y2],i]

                    #not sure about this
                    #lprob -= dot(self.W_obs, f_obs[1]) + dot(self.W_obs, f_obs[0])
                    lprob = lprob-lZ
                        
                    f_exp_trans += exp(lprob)*f_trans[0]

        return f_exp_obs, f_exp_trans    
