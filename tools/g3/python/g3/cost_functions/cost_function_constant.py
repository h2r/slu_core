import random
from cost_function_crf import CostEntry
from g3.feature_extractor.grounded_features import GGGFeatures
from dcrf3.dataset import ContinuousObservation
import math
class CostFunction:
    
    def __init__(self, dataset, feature_extractor_cls=GGGFeatures,
                 guiMode=True):
        self.feature_extractor_cls = feature_extractor_cls
        self.example_id = 0
        self.dataset = dataset
    def initialize_state(self, state):
        self.feature_extractor = self.feature_extractor_cls()

    def cost(self, esdcs, assignments):
        return random.random()

    def compute_factor_cost_entry(self, factor, ggg, state_sequence,
                                  verbose=False):
        features  = self.feature_extractor.compute_features(ggg, [factor],
                                                            state_sequence);
        f_OBS, f_OBS_names = features 
        self.example_id += 1
        cobs = ContinuousObservation("cost_function_constant" + 
                                     str(self.example_id),
                                     True, True,
                                     dict(zip(f_OBS_names[factor.id],
                                              f_OBS[factor.id])))

        dobs = self.dataset.convert_observation(cobs)  
        cost = -math.log(0.5)
        return CostEntry(factor, ggg, state_sequence,
                         cobs, dobs, cost)

    def compute_costs(self, input_factors, ggg, state_sequence, verbose=False):
        entries = []
        cost = 0
        for factor in input_factors:
            ce = self.compute_factor_cost_entry(factor, ggg, state_sequence)
            entries.append(ce)
            cost += ce.cost
            ggg.set_cost_for_factor(factor, ce.cost, ce) 
        return ce.cost, entries
