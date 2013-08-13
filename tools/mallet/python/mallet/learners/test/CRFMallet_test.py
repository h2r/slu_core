import unittest
import cPickle
from environ_vars import SLU_HOME
from mallet.learners.CRFMallet import *

class CRFMalletTest(unittest.TestCase):
    
    '''def test_crf(self):
        D = cPickle.load(open(SLU_HOME+'/data/directions/direction_training/annotation/datasets/training_discrete_d8_full.pck', 'r'))
        
        cm = CRFMallet(D, sigma=1.0)
        cm.train()'''


    def test_crf2(self):
        D = cPickle.load(open(SLU_HOME+'/data/directions/direction_training/annotation/datasets/training_discrete_d8_full.pck', 'r'))
        
        cm = CRFMallet(D, sigma=1.0)
        cm.train()
        v = cm.predict(D.observations[0])
        print "example:", v
        print "len(v)", len(v)
        print "label:", D.observations[0].labels
        
        prob = cm.log_probability(D.observations[0])
        print "probability", prob
        
        cm.save()
        cm.loadModel()
        
        
        

