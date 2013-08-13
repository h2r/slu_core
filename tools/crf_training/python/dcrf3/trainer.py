from counter import Counter
from dcrf3.generate_examples import ggg_to_observation
import dcrf3
from train_lccrf import train_lccrf
from g3.cost_functions.cost_function_crf import CostFnCrf
class Trainer:
    """
    Top-level class that does training end-to-end instead of splitting
    it into separate scripts.
    """

    def __init__(self, feature_extractor, sigma, crf_fname="crf.pck"):
        self.feature_extractor = feature_extractor
        self.sigma = sigma
        self.crf_fname = crf_fname
        self.cost_function = None

    def train(self, gggs):
        id_base = "rl"
        counter = Counter()
        observations = []
        for ggg in gggs:
            state = ggg.context
            for esdc in ggg.flattened_esdcs:
                obs = ggg_to_observation(ggg, state, self.feature_extractor,
                                         esdc, id_base, counter)
                if obs != None:
                    observations.append(obs)



        cds = dcrf3.dataset.ContinuousDataset(observations, 
                                              self.feature_extractor.__class__)
        new_outfname = train_lccrf(cds.to_discrete_dataset(), 
                                   self.crf_fname, self.sigma)
        self.cost_function = CostFnCrf.from_mallet(new_outfname)
        
        

        
