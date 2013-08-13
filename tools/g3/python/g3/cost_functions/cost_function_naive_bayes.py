from cost_function_crf import CostEntry
from dcrf3.feature_cache import FeatureCache
from dcrf3.dataset import ContinuousObservation
from g3.feature_extractor.grounded_features import GGGFeatures
from g3.graph import Factor
#import persistent_memoize
from hash_utils import fasthash

import math

'''
Naive Bayes implementation of the cost function,
which is the same as the CRF implementation with the
minor change of using the Naive Bayes feature counts
model for probabilities instead of using lccrf.
'''

class CostFnNaiveBayes:
    def __init__(self, model_fname, feature_extractor_cls=GGGFeatures, 
                 guiMode=True):
        print "loading feature probabilities at:", model_fname
        self.feature_cache = FeatureCache.load(model_fname)
        # save the last key computed, for debugging
        self.last_bigkey = None
        self.guiMode = guiMode
        self.feature_extractor_cls = feature_extractor_cls
        self.initialize()
        self.example_id = 0

    def initialize(self):
        self.feature_extractor = self.feature_extractor_cls()
        self.factor_to_cost = {}

    def initialize_state(self, state):
        self.initialize()
        objects = [state.getGroundableById(oid) 
                   for oid in state.getObjectsSet()]
        for obj in objects:
            self.feature_extractor.add_landmark(obj)

    def do_compute_features(self, factor, ggg, state_sequence):
        features  = self.feature_extractor.compute_features(ggg, [factor],
                                                            state_sequence);

        f_OBS, f_OBS_names = features 
        self.example_id += 1
        cobs = ContinuousObservation("cost_function_" + 
                                     str(self.example_id),
                                     True, True,
                                     dict(zip(f_OBS_names[factor.id],
                                              f_OBS[factor.id])))

        dobs = self.feature_cache.dataset.convert_observation(cobs)  

        return cobs, dobs
    
    def factor_cost_key(self, factor, ggg):
        words = ggg.evidence_for_node(factor.lambda_node)
        txt = " ".join(w.text for w in words)
        groundings = {}
        for ln in Factor.link_names:
            gnodes = [n for n in factor.nodes_for_link(ln) if n.is_gamma]
            if len(gnodes) != 0:
                groundings[ln] = sorted([[e.hash_string for e in ggg.evidence_for_node(n)] for n in gnodes])
                
        
        key = " ".join([factor.hash_string,
                        ggg.context.hash_string,
                        repr(groundings)
                        ])
        key += txt
        key = key.replace(" ", "")
        self.last_bigkey = key
        return "cf_" + fasthash(key)

    def close(self):
        #self.cache.close()
        pass

    def compute_features(self, factor, ggg, state_sequence=[]):
        #return self.cache.cache(factor, ggg)
        return self.do_compute_features(factor, ggg, state_sequence)
        

    def compute_factor_cost(self, factor, ggg, state_sequence, verbose=False):
        
        cobs, dobs = self.compute_features(factor, ggg, state_sequence)

        phi_value = ggg.evidence_for_node(factor.phi_node)

        factor_cost = self.feature_cache.log_probability(dobs, phi_value) * -1

        if verbose:
            print "context", ggg.context.hash_string
            print "agent", ggg.context.agent, ggg.context.agent.hash_string
            print "phi", phi_value
            print "cost", factor_cost
            for key in sorted(cobs.features_obs.keys()):
                print key, cobs.features_obs[key]
            

        return factor_cost, cobs, dobs

    def compute_factor_cost_entry(self, factor, ggg, state_sequence,
                                  verbose=False):
        factor_cost, cobs, dobs = self.compute_factor_cost(factor, ggg, 
                                                           state_sequence,
                                                           verbose=verbose)
        entry = CostEntry(factor, ggg, state_sequence, cobs, dobs, factor_cost)
        return entry

    def compute_costs(self, input_factor, ggg, state_sequence, verbose=False):
        
        if isinstance(input_factor, list):
            factors = input_factor
        else:
            factors = [input_factor]
        
        cost = 0
        entries = []

        for factor in factors:
            entry = self.compute_factor_cost_entry(factor, ggg, state_sequence,
                                                   verbose=verbose)
            entries.append(entry)
            cost += entry.esdc_cost

        for e in entries:
            e.overall_cost = cost
            e.overall_prob = math.exp(-e.overall_cost)
            
            if self.guiMode:
                self.factor_to_cost.setdefault(e.factor, [])
                self.factor_to_cost[e.factor].append(e) # save for the gui. 

        if not isinstance(input_factor, list):
            assert len(entries) == 1
            entries = entries[0]

        return cost, entries

    def cost(self, factors, ggg):
        if not isinstance(factors, list):
            factors = [factors]
        cost, entries = self.compute_costs(factors, ggg)
        return cost
