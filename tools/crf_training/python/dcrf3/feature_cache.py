import math
import pickle_util

'''
Cache feature counts in a dataset for use in the Naive
Bayes implementation of the cost function.
'''

class FeatureCache:
    @staticmethod
    def load(fname):
        m = pickle_util.load(fname)
        return m

    @staticmethod
    def save(model, fname):
        pickle_util.save(fname, model)

    def __init__(self, dataset):
        self.dataset = dataset
        self.feature_counts = None
        
    def cache_feature_counts(self):
        feature_counts = dict()
        for dobs in self.dataset.observations:
            factor = dobs.factor
            if factor != None:
                phi_node = factor.nodes_with_type("phi")[0]
                truth_value = dobs.ggg.evidence_for_node(phi_node)
                if not truth_value:
                    continue
            features = dobs.features_obs
            for (key, value) in features.iteritems():
                feature_counts.setdefault(key, 0)
                feature_counts[key] += value
        for key, value in feature_counts.iteritems():
            feature_counts[key] = math.log(value/len(feature_counts))
        print min(feature_counts.values())
        print max(feature_counts.values())
        self.feature_counts = feature_counts

    def log_probability(self, dobs, phi_value=True):
        dobs_features = dobs.features_obs
        return sum([value for key, value in self.feature_counts.iteritems() if key in dobs_features.keys()])

    def __len__(self):
        if self.feature_counts != None:
            return len(self.feature_counts)
        else:
            return None
