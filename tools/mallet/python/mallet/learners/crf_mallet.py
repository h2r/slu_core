from time import time
import pickle_util
import numpy as na


def fnames_from_root(fname):
    python_fname = fname
    java_fname = fname + ".mallet"        
    return python_fname, java_fname
class CRFMallet(object):
    @staticmethod
    def load(fname):
        python_fname, java_fname = fnames_from_root(fname)
        m = pickle_util.load(python_fname)
        return m
    @staticmethod
    def save(model, fname):
        python_fname, model.java_fname = fnames_from_root(fname)

        model.java_crf.saveModel(model.java_fname)
        tmp = model.java_crf
        model.loadWeights()
        print 'loading', len(model.featureNames), 'features'

        model.java_crf = None
        pickle_util.save(python_fname, model)
        model.java_crf = tmp
        
    def __init__(self, dataset, sigma=1.0, train_iterations=500):
        self.dataset = dataset
        assert self.dataset != None
        self.sigma = sigma
        self.training_fname = '/tmp/mallet_tmp_dataset_'+str(time())+'.txt'
        self.java_crf = None
        self.featureWeights = None
        self.train_iterations = train_iterations

 
    def save_dataset(self, fname):
        assert self.dataset != None

        D_str = self.dataset.to_mallet_dataset()
        print "saving to", fname
        with open(fname, 'w') as tmp_file:

            tmp_file.write(D_str)
            

    def train(self):
        import jvm
        import jpype
        
        p_classifier = jpype.JPackage("edu.mit.csail.spatial.learner")

        p_logging = jpype.JPackage("java.util.logging")
        lm = p_logging.LogManager.getLogManager()

        print "saving dataset"
        self.save_dataset(self.training_fname)
        print "done saving dataset, making classifier"
        self.java_crf = p_classifier.CRFMallet2(self.training_fname, self.sigma)
        #self.java_crf.setClassifier("CRFTrainerByLabelLikelihood")
        print "set classifier"
        self.java_crf.setClassifier("CRFTrainerByL1LabelLikelihood")
        print "set logging"
        lm.getLogger("").setLevel(p_logging.Level.WARNING)
        print "now training"
        self.java_crf.setTrainingIterations( self.train_iterations)
        self.java_crf.train()
        self.update_rep()

    def update_rep(self):
        self.true_idx = self.java_crf.getCrf().getOutputAlphabet().lookupIndex("True")
        self.false_idx = self.java_crf.getCrf().getOutputAlphabet().lookupIndex("False")
        print "true offset t1", self.java_crf.getCrf().getParameters().defaultWeights[self.true_idx]
        print "true offset t2", self.java_crf.getCrf().getState(self.true_idx).getFinalWeight()

        print "false offset t1", self.java_crf.getCrf().getParameters().defaultWeights[self.false_idx]
        print "false offset t2", self.java_crf.getCrf().getState(self.false_idx).getFinalWeight()


        self.true_offset = self.java_crf.getCrf().getParameters().defaultWeights[self.true_idx]  + self.java_crf.getCrf().getState(self.true_idx).getFinalWeight()
        self.false_offset = self.java_crf.getCrf().getParameters().defaultWeights[self.false_idx]  + self.java_crf.getCrf().getState(self.false_idx).getFinalWeight()


    def log_probability(self, d, phi_value):
        #lm.getLogger("").setLevel(p_logging.Level.FINE)
        #print "****** lattice"
       # lp = self.log_probability_java(d, phi_value)
        #print "****** done lattice"
        lp = self.log_probability_na(d, phi_value)
        #from assert_utils import assert_sorta_eq
        #assert_sorta_eq(lp_java, lp)
        return lp
        
        
        
    def log_probability_na(self, d, phi_value=True):
        """
        Compute log probability directly from python.  This verifies
        we get the weights out properly and is also faster than
        mallet.
        """
        summed_weight = self.summed_weight(d)
        assert not na.isnan(summed_weight)
        true_sum = summed_weight + self.true_offset
        
        false_sum = -summed_weight + self.false_offset
        Z = na.exp(true_sum) + na.exp(false_sum)
        z = na.log(Z)
        assert not na.isnan(z)
        if phi_value == True:
            return true_sum - z
        elif phi_value == False:
            return false_sum - z
        else:
            raise ValueError("Bad phi value: " + `phi_value`)
               
    
        
    def log_probability_java(self, d, phi_value):
        r = self.java_crf.log_probability([str(phi_value)], 
                                          d.features_obs.keys(),
                                          self.convert_values(d.features_obs))
        return r

    def convert_values(self, features):
        fvalues = [float(f) for f in features.values()]
        fvalues = [0.0 if na.isnan(f) or na.isinf(f) else f for f in fvalues]
        return fvalues


    def predict(self, d):
        fvalues = self.convert_values(d.features_obs)
        values = self.java_crf.predict(d.features_obs.keys(), fvalues)
        lp = self.java_crf.log_probability(values, d.features_obs.keys(), 
                                           fvalues)
        value = values[0]
        try:
            return eval(value), lp
        except:
            pass
        
        return value, lp


    def unload(self):
        self.java_crf = None
        
    
    def loadModel(self, fname):
        import jvm
        import jpype

        p_classifier = jpype.JPackage("edu.mit.csail.spatial.learner")
        self.java_crf = p_classifier.CRFMallet2()
        self.java_crf.loadModel(fname)
        self.update_rep()

    def loadWeights(self):
        # getting out the weights with a slice causes Jpype to do
        # the converstion from Java to Python in C, which is way
        # faster than calling the list constructor.
        featureNames = self.java_crf.featureNames()
        self.featureNames = [str(x) for x in featureNames[0:len(featureNames)]]
        featureWeights = self.java_crf.featureWeights()
        featureWeights = featureWeights[0:len(featureWeights)]
        self.feature_name_to_weight = dict(zip(featureNames,
                                               featureWeights))


        self.feature_name_to_idx = {}
        self.feature_weight_array = na.zeros(len(self.featureNames))
        for i, fname in enumerate(self.featureNames):
            weight = self.feature_name_to_weight.get(fname, 0)
            self.feature_weight_array[i] = weight
            self.feature_name_to_idx[fname] = i

        

    def summed_weight(self, obs):
        r = 0
        #print "**** summing weight"
        for name, value in obs.features_obs.iteritems():
            weight = self.feature_name_to_weight.get(name, 0)
            #print name, weight, value
            assert not na.isnan(value), (name, value)
            r += weight * value
        #print "**** end summing weight"
        return r
                                       
    def get_weights(self, obs):
        names = obs.features_obs
        return dict((n, self.feature_name_to_weight.get(n, 0)) for n in names)

