from scipy import optimize, exp, log, zeros, dot, array, isnan, isinf, mod, amax, argmax
from scipy.linalg.basic import norm
from math_util import combinations_self
from copy import deepcopy, copy
from scipy import random, shape
from pyTklib import forward_backward_alpha,forward_backward_beta

class dataset_crf:
    def __init__(self, observations):
        self.observations = observations
        self.alphabet = None
        self.cache_features()
        
    def get_output_alphabet(self):
        if(self.alphabet != None):
            return self.alphabet
        
        self.alphabet = set([])
        for o in self.observations:
            for l in o.labels:
                if(not l in self.alphabet):
                    self.alphabet.add(l)

        self.alphabet = list(self.alphabet)
        return self.alphabet

    def cache_features(self):
        for d in self.observations:
            #print "alphabet", self.get_output_alphabet()
            #raw_input()
            d.create_features_cache(self.get_output_alphabet())
        #print self.observations[0].features_obs
        #raw_input()

class observation:
    def __init__(self, labels, observations, alp=None):
        self.labels = labels
        self.observations = observations
        self.features_obs = {}
        self.features_trans = {}
        self.alp=alp
        self.is_print = False
        
        if(alp !=None):
            self.create_features_cache(alp)
        
    def create_features_cache(self, alphabet):
        self.alp = alphabet
        
        self.features_obs = {}
        for a in alphabet:
            self.features_obs[a] = [None for i in range(len(self.labels))]
        
        self.features_trans = {}
        for a in alphabet:
            self.features_trans[a] = {}
            for b in alphabet:
                self.features_trans[a][b] = [None for i in range(len(self.labels))]

    def num_features_obs(self):
        return len(self.features_obs[self.alp[0]][0])

    def num_features_trans(self):
        return len(self.features_trans[self.alp[0]][self.alp[0]][0])
    
    def get_features_array(self):
        features_obs_a = zeros([len(self.alp), len(self.labels), self.num_features_obs()])
        features_trans_a = zeros([len(self.alp), len(self.alp), len(self.labels), self.num_features_trans()])
        
        for t in range(len(self.labels)):
            for i,a in enumerate(self.alp):
                #print self.features_obs[a]
                features_obs_a[i,:] = self.features_obs[a]
                
                for j,b in enumerate(self.alp):
                    features_trans_a[i,j,:] = self.features_trans[a][b]

        return self.alp, features_obs_a, features_trans_a
        

    def __str__(self):
        return "labels:"+str(self.labels)+"\nobservations:"+str(self.observations)

    def __repr__(self):
        return "labels:"+str(self.labels)+"\nobservations:"+str(self.observations)


class crf:
    def __init__(self, dataset):
        self.D = dataset

    def log_probability_brute_force(self, d):
        lp=self.log_probability_compute_numerator(d)
        lZ=self.log_partition_brute_force(d)
        
        return lp-lZ

    def log_partition_brute_force(self, d):
        alp = self.D.get_output_alphabet()
        combos = list(combinations_self(alp, len(d.observations)))
        
        Z = 0.0
        o = copy(d)
        for combo in list(combos):
            o.labels = combo
            Z += exp(self.log_probability_compute_numerator(o))
        return log(Z)

    def log_probability_compute_numerator(self, d):
        pass
    

class linear_chain_crf(crf):
    def __init__(self, dataset, sigma=1.0):
        crf.__init__(self, dataset)
        
        self.sigma = sigma
        self.W_obs = zeros(self.get_num_features_obs())*1.0
        self.W_trans = zeros(self.get_num_features_trans())*1.0
        
        
        #self.W_obs = random.rand(self.get_num_features_obs())*1.0
        #self.W_trans = random.rand(self.get_num_features_trans())*1.0
        
        self.fc_all = {}
        combos = list(combinations_self(self.D.get_output_alphabet(), 
                                        len(self.D.observations[0].labels)))
        for c in combos:
            self.fc_all["".join(c)] = [[] for i in range(len(dataset.observations))]
        
        for d in self.D.observations:
            #print self.D.get_output_alphabet()
            d.create_features_cache(self.D.get_output_alphabet())
        
        self.compute_emperical_feature_counts() 

        
    def train(self):
        print "training"
        self.theta = list(self.W_obs)
        self.theta.extend(self.W_trans)
        
        self.theta = optimize.fmin_l_bfgs_b(self.negative_data_log_likelihood, 
                                            self.theta,
                                            self.compute_log_gradient, pgtol=0.25)[0]
        self.W_obs = self.theta[0:len(self.W_obs)]
        self.W_trans = self.theta[len(self.W_obs):]
        
        
        #print self.theta
        #self.theta = optimize.fmin_l_bfgs_b(self.negative_data_log_likelihood, 
        #                                    self.theta, approx_grad=True, epsilon=1)
    
    def negative_data_log_likelihood(self, theta):
        #print "computing likelihood for", theta
        self.W_obs = theta[0:len(self.W_obs)]
        self.W_trans = theta[len(self.W_obs):]
        
        lp = 0
        for d in self.D.observations:
            lp += self.log_probability_forward_backward(d)
            
        rlp = -1.0*lp
        rlp += dot(theta, theta)/(2*(self.sigma**2.0))
        
        #print "len(parameters)", len(theta)
        print "data likelihood", rlp
        #print "theta", self.theta
        return rlp


    def compute_log_gradient(self, theta):
        #print "grad"
        self.W_obs = theta[0:len(self.W_obs)]
        self.W_trans = theta[len(self.W_obs):]
        
        f_obs_exp, f_trans_exp = self.compute_expected_feature_counts_brute_force()

        #print "expected features", f_obs_exp
        #print "true features:", self.fc_obs
        
        #for e in f_obs_exp:
        #    if(isnan(e)):
        #        raw_input()
        
        obs_grad = self.fc_obs - f_obs_exp
        trans_grad = self.fc_trans - f_trans_exp

        ret_val = []
        ret_val.extend(obs_grad)
        ret_val.extend(trans_grad)
        ret_val = array(ret_val)
        
        #print "orig ret_val", ret_val
        #because we're minimizing the negative log likelihood

        ret_val*=-1.0
        ret_val+=theta/(self.sigma**2.0)
        
        print "max", amax(ret_val)

        i = argmax(obs_grad)
        print "diff:", obs_grad[i], " features:", self.fc_obs[i], " expectation:", f_obs_exp[i]
        
        return ret_val
    
    def compute_expected_feature_counts_brute_force(self):
        f_obs_exp = zeros(len(self.W_obs))*1.0
        f_trans_exp = zeros(len(self.W_trans))*1.0
        
        #get the combinations
        alp = self.D.get_output_alphabet()
        combos = list(combinations_self(alp, len(self.D.observations[0].labels)))
        
        #iterate over the data
        for k, d in enumerate(self.D.observations):
            #iterate over the combinations
            o = copy(d)
            for y in combos:
                o.labels = y

                #fc_obs_exp, fc_trans_exp = self.compute_feature_counts(o)
                fc_obs_exp = zeros(len(self.W_obs))*1.0
                fc_trans_exp = zeros(len(self.W_trans))*1.0
                
                #print "y", y
                for i in range(len(y)):
                    fc_obs_exp += o.features_obs[y[i]][i]

                    if(i > 0):
                        fc_trans_exp += o.features_trans[y[i-1]][y[i]][i-1]
                
                #compute the feature counts correctly here
                f_obs_exp+=exp(self.log_probability_forward_backward(o))*fc_obs_exp
                f_trans_exp+=exp(self.log_probability_forward_backward(o))*fc_trans_exp
                
        return f_obs_exp, f_trans_exp


    def compute_emperical_feature_counts(self):
        self.fc_obs = zeros(self.get_num_features_obs())
        self.fc_trans = zeros(self.get_num_features_trans())
        #self.fc_obs_all = zeros([len(self.D.observations), self.get_num_features_obs()])
        #self.fc_trans_all = zeros([len(self.D.observations), self.get_num_features_trans()])

        for k, d in enumerate(self.D.observations):
            if(mod(k, 10000) == 0):
                print k, 'of', len(self.D.observations)
                
            for i in range(len(d.observations)):
                #print "starting"
                for a in self.D.get_output_alphabet():
                    if(d.features_obs.has_key(a) and d.features_obs[a][i] == None):
                        d.features_obs[a][i] = self.f_obs(a, d.observations[i])
                        #print "caching:", a, i, self.f_obs(a, d.observations[i]), d.observations[i]

                    #cache the transition probabilities as well
                    for b in self.D.get_output_alphabet():
                        if(d.features_trans.has_key(a) 
                           and d.features_trans[a].has_key(b) 
                           and d.features_trans[a][b][i] == None):
                            d.features_trans[a][b][i] = self.f_trans(a, b, d.observations[i])


                features_obs = d.features_obs[d.labels[i]][i]
                
                self.fc_obs += features_obs
                #self.fc_obs_all[k] += features_obs
                
                if(i != 0):
                    features_trans = self.f_trans(d.labels[i-1], d.labels[i], d.observations[i])
                    self.fc_trans += features_trans
                    #self.fc_trans_all[k] += features_trans


    def compute_feature_counts(self, d):
        fc_obs = zeros(self.get_num_features_obs())
        fc_trans = zeros(self.get_num_features_trans())

        for i in range(len(d.observations)):
            #if(d.features_obs[i] == None):
            #    d.features_obs[i] = self.f_obs(d.labels[i], d.observations[i])

            #fc_obs += d.features_obs[i]

            fc_obs += self.f_obs(d.labels[i], d.observations[i])
                
            if(i != 0):
                features_trans = self.f_trans(d.labels[i-1], d.labels[i], d.observations[i])
                fc_trans += features_trans

        return fc_obs, fc_trans

    def log_probability_compute_numerator(self, d):
        labels = d.labels

        v=0
        for i, label in enumerate(d.labels):
            if(i == 0):
                v+= self.log_probability_compute_local_potential(None, d.labels[i], d.observations[i], d.features_obs[d.labels[i]][i])
            else:
                v+= self.log_probability_compute_local_potential(d.labels[i-1], d.labels[i], d.observations[i], 
                                                                 d.features_obs[d.labels[i]][i], d.features_trans[d.labels[i-1]][d.labels[i]][i-1])
        
        return v
        
    def log_probability_compute_local_potential(self, label_i1, label_i, observation, features_obs=None, features_trans=None):
        if(features_obs == None):
            v=dot(self.f_obs(label_i, observation), self.W_obs)
        else:
            v=dot(features_obs, self.W_obs)
            
        if(label_i1 != None):

            if(features_trans == None):
                v+=dot(self.f_trans(label_i1, label_i, observation), self.W_trans)
            else:
                v+=dot(features_trans, self.W_trans)

        return v
    
    def predict_brute_force(self, observations):
        #need to do max-product here
        combos = list(combinations_self(self.D.get_output_alphabet(), len(observations)))
        
        probs = [];
        o=observation(combos[0], observations, self.D.get_output_alphabet())
        for combo in combos:
            o.labels = combo
            probs.append(self.log_probability_forward_backward(o))
        
        i = argmax(probs)
        
        return combos[i], exp(probs[i])


    def log_probability_forward_backward(self, d):
        alpha, beta = self.forward_backward(d)
        #print "alpha_old", alpha
        #print "beta_old", beta


        #print "done getting features_array", shape(list(features_obs)), shape(list(features_trans))        
        #print "mylist:", features_obs.tolist()
        #print "len(W_obs), len(W_trans)", len(self.W_obs), len(self.W_trans)
        
        alp, features_obs, features_trans = d.get_features_array()
        #alpha = array(forward_backward_alpha(range(len(alp)), features_obs.tolist(), features_trans.tolist(), 
        #                                     list(self.W_obs), list(self.W_trans), len(d.observations)));


        #beta =  array(forward_backward_beta(range(len(alp)), features_obs.tolist(), features_trans.tolist(), 
        #                                    list(self.W_obs), list(self.W_trans), len(d.observations)));
        #print "alpha_new", array(alpha_new)
        #print "beta_new", array(beta_new)
        
        #raw_input("press me");
        #forward_backward_alpha()
        
        lp = self.log_probability_compute_numerator(d)
        lZ = log(sum(alpha[:,-1]))
        
        return lp-lZ
    
    
    def forward_backward(self, d):
        alp = self.D.get_output_alphabet()
        
        alpha = zeros([len(alp), len(d.observations)])*1.0
        for i in range(len(d.observations)):
            for j in range(len(alp)):
                if(i == 0):
                    lprob = exp(self.log_probability_compute_local_potential(None, alp[j], 
                                                                             d.observations[i], 
                                                                             d.features_obs[alp[j]][i]))
                    alpha[j,i] = lprob
                    continue
                    
                for k in range(len(alp)):
                    lprob = exp(self.log_probability_compute_local_potential(alp[j], alp[k], 
                                                                             d.observations[i], 
                                                                             d.features_obs[alp[k]][i], 
                                                                             d.features_trans[alp[j]][alp[k]][i-1]))
                    alpha[k,i] += alpha[j,i-1]*lprob
        
        beta = zeros([len(alp), len(d.observations)])*1.0
        for i in reversed(range(len(d.observations))):
            for j in range(len(alp)):
                if(i == len(d.observations)-1):
                    lprob = exp(self.log_probability_compute_local_potential(None, alp[j], 
                                                                             d.observations[i], 
                                                                             d.features_obs[alp[j]][i]))
                    beta[j,i] += lprob
                    continue
                
                for k in range(len(alp)):
                    lprob = exp(self.log_probability_compute_local_potential(alp[j], alp[k], 
                                                                             d.observations[i], 
                                                                             d.features_obs[alp[k]][i], 
                                                                             d.features_trans[alp[k]][alp[j]][i+1]))
                    #print "orig:", i+1
                    beta[k,i] += beta[j,i+1]*lprob
        
        #print "alpha sum:", sum(alpha[:,-1])
        #print "beta sum:", sum(beta[:,0])
        
        #if(d.is_print == True):
        #    print alpha, beta
        return alpha, beta






    
    
    

    
