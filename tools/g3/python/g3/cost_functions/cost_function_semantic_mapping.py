from cost_function_crf import CostFnCrf
from g3.feature_extractor.sr_features import SrFeatures
from mallet.learners.crf_mallet import CRFMallet
from stopwords import stopwords
import spatial_features_cxx as sf
import math

class CostFnSemanticMapping(CostFnCrf):
    @staticmethod
    def from_mallet(model_fname, feature_extractor_cls=SrFeatures, guiMode=True):
        print "loading crf at:", model_fname
        model = CRFMallet.load(model_fname)
        return CostFnSemanticMapping(model, feature_extractor_cls, guiMode)


    def __init__(self, *args, **margs):
        CostFnCrf.__init__(self, *args, **margs)
        self.nodes = []

    def node_for_pobj(self, input_pobj):
        for node, pobj in self.nodes:
            if pobj.hash_string == input_pobj.hash_string:
                return node
        raise ValueError("Couldn't find node.")
    def compute_factor_cost_entry(self, factor, ggg, state_sequence, 
                                  verbose=False):
        print "sm, computing factor cost entry", factor.type
        entry = CostFnCrf.compute_factor_cost_entry(self, factor, ggg, 
                                                    state_sequence, verbose)


        if "OBJECT" in factor.type and len(factor.gamma_nodes) == 1:
            assert len(factor.gamma_nodes) == 1
            object_node = factor.nodes_for_link("top")[0]

            print "link", factor.link_names
            lambda_node = factor.nodes_for_link("f")[0]
            standoffs = ggg.evidence_for_node(lambda_node)
            words = [s.text for s in standoffs if not s.text in stopwords]
            print "*****"
            print "words", words
            object_grounding = ggg.evidence_for_node(object_node)[0]
            assert len(words) == 1
            
            object_map_node = self.node_for_pobj(object_grounding)

            prob = object_map_node.label_dist.getprobability(words[0])

            print "prob", prob
            print "label dist", object_map_node.label_dist.getdictionary()
            print "pobjs", object_grounding.tags
            groundings = ggg.groundings_for_factor(factor)

            print "groundings", ", ".join([str(g) for g in groundings])

            entry.probability = prob

            entry.cost = -math.log(entry.probability)

        return entry
            




    def compute_cost_away_from(self, factor, ggg):
        figure_node = factor.nodes_for_link("top")[0]
        landmark_node = factor.nodes_for_link("l")[0]
        figure_value = ggg.evidence_for_node(figure_node)[0]
        landmark_value = ggg.evidence_for_node(landmark_node)[0]
        dist = sf.math2d_dist(figure_value.centroid2d, landmark_value.centroid2d)
        area = sf.math2d_area(landmark_value.prism.points_xy)
        t = dist / area
        prob = 1.0 / (1 + math.exp(-t * 1))
        print "prob", prob
        return -math.log(prob)
        

    def compute_cost_near(self, factor, ggg):
        figure_node = factor.nodes_for_link("top")[0]
        landmark_node = factor.nodes_for_link("l")[0]
        figure_value = ggg.evidence_for_node(figure_node)[0]
        landmark_value = ggg.evidence_for_node(landmark_node)[0]
        dist = sf.math2d_dist(figure_value.centroid2d, landmark_value.centroid2d)
        area = sf.math2d_area(landmark_value.prism.points_xy)
        t = 1 - dist / area
        t = -dist/30
        prob = 1.0 / (1 + math.exp(-t))
        print "prob", prob
        return -math.log(prob)

    def compute_factor_cost(self, factor, ggg, state_sequence=None, verbose=False):
        print "sm.compute_factor_cost"
        lambda_node = factor.lambda_node
        lambda_value = ggg.evidence_for_node(lambda_node)
        print "lambda", [s.text for s in lambda_value]
        cost, cobs, dobs = CostFnCrf.compute_factor_cost(self, factor, ggg, [])

        if ("near" in [s.text for s in lambda_value] or
            "behind" in [s.text for s in lambda_value]  or
            "next to" in [s.text for s in lambda_value] or
            "besides" in [s.text for s in lambda_value]):
            print "*************** near special"
            return self.compute_cost_near(factor, ggg), cobs, dobs
        elif "away" in [s.text for s in lambda_value]:
            return self.compute_cost_away_from(factor, ggg), cobs, dobs
        else:
            return cost, cobs, dobs
        
