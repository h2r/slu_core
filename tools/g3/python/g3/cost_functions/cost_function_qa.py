from cost_function_crf import CostFnCrf
from g3.feature_extractor.grounded_features import GGGFeatures
from mallet.learners.crf_mallet import CRFMallet
import numpy as np
import sys


class CostFnQa(CostFnCrf):
    @staticmethod
    def from_mallet(model_fname, feature_extractor_cls=GGGFeatures, guiMode=True):
        print "loading crf at:", model_fname
        model = CRFMallet.load(model_fname)
        return CostFnQa(model, feature_extractor_cls, guiMode)

    def compute_factor_cost(self, factor, ggg, state_sequence, verbose=False):
        cobs, dobs = self.compute_features(factor, ggg, state_sequence)
        phi_value = ggg.evidence_for_node(factor.phi_node)

        if 'BOUND_OBJECT' in factor.type:
            """
            If the factor is of the special yes/no type, then set the cost to 0 or infinity depending on whether the factor represents a yes or a no and whether the gamma nodes have matching bindings.
            """
            assert len(factor.gamma_nodes) == 2, "YNFactor expects exactly two gamma nodes during inference"
            g0 = factor.gamma_nodes[0]
            g1 = factor.gamma_nodes[1]
            if 'yes_BOUND' in factor.type:
                if [o.id for o in ggg.evidence_for_node(g0)] == [o.id for o in ggg.evidence_for_node(g1)]:
                    # factor_cost = 1e-100
                    factor_cost = 0
                else:
                    # factor_cost = sys.float_info.max
                    # factor_cost = 1e100
                    factor_cost = np.inf
            elif 'no_BOUND' in factor.type:
                if [o.id for o in ggg.evidence_for_node(g0)] != [o.id for o in ggg.evidence_for_node(g1)]:
                    # factor_cost = 1e-100
                    factor_cost = 0
                else:
                    # factor_cost = sys.float_info.max
                    # factor_cost = 1e100
                    factor_cost = np.inf
            else:
                raise ValueError("Couldn't classify yes/no factor as 'yes' or 'no'. Factor type: %s" % factor.type)

        else:
            factor_cost = self.lccrf.log_probability(dobs, phi_value) * -1

        if verbose:
            print "context", ggg.context.hash_string
            print "agent", ggg.context.agent, ggg.context.agent.hash_string
            print "phi", phi_value
            print "cost", factor_cost
            for key in sorted(cobs.features_obs.keys()):
                print key, cobs.features_obs[key]


        return factor_cost, cobs, dobs
