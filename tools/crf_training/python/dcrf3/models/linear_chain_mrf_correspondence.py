import cPickle
from sys import argv
import orange
import orngSVM, orngBayes, orngTree, orngEnsemble

class linear_chain_mrf_correspondence:
    def __init__(self, dataset, learner="svm"):
        self.classifier_obs = None
        self.classifier_trans = None
        self.dataset = dataset
        self.learner = learner
    
    def train(self):
        F_train_obs = []; F_train_trans = [];
        print "--------------creating tables-------------------"
        for i, obs in enumerate(self.dataset.observations):
            print i, "of", len(self.dataset.observations)
            
            f_obs, f_trans = self.dataset.to_orange_entries(obs)
            
            for i, fs in enumerate(f_obs):
                print i, f_obs[0]
                F_train_obs.append(fs)
            
            for fs in f_trans:
                F_train_trans.append(fs)
                
        
        if(len(F_train_obs) == 0):
            return None
        

        print ">> adding elements to tables"
        #create the attributes and domain
        #define the rest of the table by addign elements to it
        table_obs = orange.ExampleTable(self.get_domain_obs())
        
        for i in range(len(F_train_obs)):
            table_obs.append(F_train_obs[i])
            
        table_trans = orange.ExampleTable(self.get_domain_trans())
        for i in range(len(F_train_trans)):
            table_trans.append(F_train_trans[i])
        
        #perform the learning
        print "training"
        if(self.learner == "bayes"):
            print "training bayes obs"
            self.classifier_obs = orngBayes.BayesLearner(table_obs)
            print "training bayes trans"
            self.classifier_trans = orngBayes.BayesLearner(table_trans)
        elif(self.learner == "tree"):
            print "running tree"
            self.classifier_obs = orngTree.TreeLearner(table_obs)
            self.classifier_trans = orngTree.TreeLearner(table_trans)
        elif(self.learner == "svm"):
            #can't load the svmlearner
            print "trianing observation svm"
            self.classifier_obs = orngSVM.SVMLearner(table_obs, 
                                                     svm_type=orange.SVMLearner.Nu_SVC, 
                                                     nu=0.3, probability=True)

            print "trianing transition svm"
            self.classifier_trans = orngSVM.SVMLearner(table_trans, 
                                                       svm_type=orange.SVMLearner.Nu_SVC, 
                                                       nu=0.3, probability=True)
        elif(self.learner == "boosting"):
            #problem here too
            #this is meant to be adaboost
            self.classifier_obs = orngTree.BoostedLearner(table_obs)
            self.classifier_trans = orngTree.BoostedLearner(table_trans)
        elif(self.learner == "randomforest"):
            #problem here too 
            self.classifier_obs = orngEnsemble.RandomForestLearner(table_obs, 
                                                                   trees=50, name="forest")
            self.classifier_trans = orngEnsemble.RandomForestLearner(table_trans, 
                                                                     trees=50, name="forest")
        else:
            print "unknown learner"
            raise
        
        return self.classifier_obs, self.classifier_trans
    

    def get_domain_obs(self):
        #if(self.domain != None):
        #    return self.domain
        
        attributes = [orange.FloatVariable(name) for name in self.dataset.obs_alphabet]
        
        alp = [str(s) for s in self.dataset.label_alphabet]
        classattr = orange.EnumVariable("classname", values = alp);
        domain = orange.Domain(attributes + [classattr])
        
        return domain

    def get_domain_trans(self):
        #if(self.domain != None):
        #    return self.domain
        
        attributes = [orange.FloatVariable(name) for name in self.dataset.trans_alphabet]
        
        alp = [str(i) for i in range(len(self.dataset.label_alphabet)**2)]
        classattr = orange.EnumVariable("classname", values = alp);
        domain = orange.Domain(attributes + [classattr])
        
        return domain


    def predict(self, obs):
        print "to orange entries"
        f_obs, f_trans = self.dataset.to_orange_entries(obs)
        #orngBayes.printModel(self.classifiers[query_word])
        
        prob = 1; labels = [];
        for i in range(len(f_obs)):
            ex_obs = orange.Example(self.get_domain_obs(), f_obs[i])
            print "classifying", f_obs[i]
            results = self.classifier_obs(ex_obs, orange.GetBoth)
            labels.append(bool(results[0]))
            #print "bool", bool(results[0])
            label_i = self.dataset.label_alphabet_dict[bool(results[0])]

        #ex_trans = orange.Example(self.get_domain_trans(), f_trans)        
        return labels, results[1][label_i]
    
