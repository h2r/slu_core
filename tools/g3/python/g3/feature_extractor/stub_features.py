from scipy import mod, isnan, arange
from features.linguistic_features import sfe_language_object as language_object
from spatial_features.groundings import Path, PhysicalObject, Place
from g3.annotation_to_ggg import assignPathGroundingsToGGG
import numpy as na
import spatial_features_cxx as sf
from spatial_features_cxx import vectors
import collections
from itertools import chain
from features.feature_utils import add_prefix, merge, compute_fdict, average_dicts, add_word_features


def convert_words(standoffs):
    words = [s.text.lower().replace(" ", "_") for s in standoffs]
    return words



class StubFeatures:
    """
    Really simple, really fast features for testing faster and easier.
    """

    def __init__(self):
        pass


    def factor_features(self, factor, ggg):
        """
        Computes features for a particular factor.
        """
        parent_node = factor.nodes_for_link("top")[0]
        if "OBJECT" in parent_node.type:
            return self.object_factor_features(factor, ggg)
        elif "PLACE" in parent_node.type:
            return self.object_factor_features(factor, ggg)
        elif "PATH" in parent_node.type:
            return self.path_factor_features(factor, ggg)
        elif "EVENT" in parent_node.type:
            return self.event_factor_features(factor, ggg)
        else:
            raise ValueError("unexpected type: " + `parent_node.type`)

        

    def object_factor_features(self, factor, ggg):
        if factor.has_children("r"):
            return self.relation_object_factor_features(factor, ggg)
        else:
            return self.leaf_object_factor_features(factor, ggg)

    def leaf_object_factor_features(self, factor, ggg):
        assert factor.has_children("f")
        assert not factor.has_children("r")
        assert not factor.has_children("l")
        assert not factor.has_children("l2")

        f_words = convert_words(ggg.evidence_for_node(factor.nodes_for_link("f")[0]))
        
        result_dict = {}        

        for fi, f_grounding in enumerate(ggg.evidence_for_node(factor.nodes_for_link("top")[0])):

            assert (isinstance(f_grounding, PhysicalObject) or
                    isinstance(f_grounding, Place)), (f_grounding, str(ggg.factor_to_esdc(factor)))
            fdict = add_prefix("f_%d_" % fi, self.np_features(f_words, f_grounding))
            result_dict = merge(result_dict, fdict)
                
        return result_dict
        
    def relation_object_factor_features(self, factor, ggg):
        parent_node = factor.nodes_for_link("top")[0]
        assert "OBJECT" in parent_node.type or "PLACE" in parent_node.type
        result_dict = {}        
        assert factor.has_children("r")
        r_words = convert_words(ggg.evidence_for_node(factor.nodes_for_link("r")[0])) # + ["null"]
        #r_words = [w.text.lower() for w in esdc.r]

        for fi, f_grounding in enumerate(ggg.evidence_for_node(parent_node)):

            assert (isinstance(f_grounding, PhysicalObject) or 
                    isinstance(f_grounding, Place)), f_grounding

            if factor.has_children("l"):
                l_groundings = chain(*[ggg.evidence_for_node(node) for node in factor.nodes_for_link("l")])
                # if the landmark is empty, add in the fork
            else:
                l_groundings = [ggg.context.agent]
#            else:
#                raise ValueError("L must be esdcs or empty." + str(esdc))
            
            for li, l_grounding in enumerate(l_groundings):
                if not isinstance(l_grounding, Path):
                    fdict = self.object_landmark_features(ggg.context.agent,
                                                          f_grounding.prism, r_words, l_grounding.prism)
                    fdict = add_prefix("f_%d_l_%d_" % (fi, li), fdict)
                    result_dict = merge(result_dict, fdict)
                
            if factor.has_children("l2"):
                l2_groundings = chain(*[ggg.evidence_for_node(node) for node in factor.nodes_for_link("l2")])

                for l2i, l2_grounding in enumerate(l2_groundings):
                    if not isinstance(l2_grounding, Path):
                        fdict = self.object_landmark_features(ggg.context.agent,
                                                              f_grounding.prism, r_words, l_grounding.prism)

                        fdict = add_prefix("f_%d_l2_%d_" % (fi, l2i), fdict)
                        result_dict = merge(result_dict, fdict)

        return result_dict

    def object_object_start_end(self, agent, f_grounding, r_words, l_grounding, prefix):
        result_dict = {}
        f_start = f_grounding.prismAtT(0)
        f_end = f_grounding.prismAtT(-1)
        l_start = l_grounding.prismAtT(0)
        l_end = l_grounding.prismAtT(-1)

        fdict = self.object_landmark_features(agent, f_start, r_words, l_start)
        fdict = add_prefix("start_%s" % (prefix), fdict)        
        result_dict = merge(result_dict, fdict)

        
        fdict = self.object_landmark_features(agent, f_end, r_words, l_end)
        fdict = add_prefix("end_%s" % (prefix), fdict)
        result_dict = merge(result_dict, fdict)

        return result_dict
        
            
    def event_factor_features(self, factor, ggg):
        parent_node = factor.nodes_for_link("top")[0]
        assert "EVENT" in parent_node.type

        r_words = convert_words(ggg.evidence_for_node(factor.nodes_for_link("r")[0]))
        try:
            f_grounding = ggg.evidence_for_node(parent_node)[0]
        except:
            raise
            return dict()
            
        assert isinstance(f_grounding, PhysicalObject), (f_grounding, f_grounding.__class__)
        result_dict = {}
        
        for li, (l_node, l_groundings) in enumerate((node, ggg.evidence_for_node(node))
                                                    for node in factor.nodes_for_link("l")):
            for lj, l_grounding in enumerate(l_groundings):                
                if "PATH" in l_node.type and isinstance(l_grounding, PhysicalObject):
                    l_grounding = l_grounding.path

                if hasattr(l_grounding, "prism"):
                    fdict = self.object_object_start_end(ggg.context.agent,
                                                         f_grounding, r_words, l_grounding,
                                                         "l1_%d_%d_" % (li, lj))
                    result_dict = merge(result_dict, fdict)
        if factor.has_children("l2"):
            for l2i, (l2_node, l2_groundings) in enumerate((node, ggg.evidence_for_node(node))
                                                           for node in factor.nodes_for_link("l2")):
                for l2j, l2_grounding in enumerate(l2_groundings):
                    if "PATH" in l2_node.type and isinstance(l2_grounding, PhysicalObject):
                        l2_grounding = l2_grounding.path
                    
                    if hasattr(l2_grounding, "prism"):
                        fdict = self.object_object_start_end(ggg.context.agent,
                                                             f_grounding, r_words, l2_grounding,
                                                             "l2_%d_%d_" % (l2i, l2j))
                        result_dict = merge(result_dict, fdict)                    

        for li, (l_node, l_groundings) in enumerate((node, ggg.evidence_for_node(node))
                                                    for node in factor.nodes_for_link("l")):
            
            for lj, l_grounding in enumerate(l_groundings):
                if "PATH" in l_node.type and isinstance(l_grounding, PhysicalObject):
                    l_grounding = l_grounding.path

                if not factor.has_children("l2"):
                    continue

                for l2i, (l2_node, l2_groundings) in enumerate((node, ggg.evidence_for_node(node))
                                                               for node in factor.nodes_for_link("l2")):
                    for l2j, l2_grounding in enumerate(l2_groundings):
                        if "PATH" in l2_node.type and isinstance(l2_grounding, PhysicalObject):
                            l2_grounding = l2_grounding.path

                        if (hasattr(l2_grounding, "prism") and
                            hasattr(l_grounding, "prism")):
                            fdict = self.object_object_start_end(ggg.context.agent,
                                                                 l_grounding, r_words, l2_grounding,
                                                                 "l_l2_%d_%d_%d_%d_" % (li, lj, l2i, l2j))
                            result_dict = merge(result_dict, fdict)
                        

                
        result_dict = merge(result_dict, self.path_factor_features(factor, ggg))

        return result_dict
        
    def path_factor_features(self, factor, ggg):
        parent_node = factor.nodes_for_link("top")[0]
        assert "EVENT" in parent_node.type or "PATH" in parent_node.type

        assert factor.has_children("r")
        r_words = convert_words(ggg.evidence_for_node(factor.nodes_for_link("r")[0]))
        
        result_dict = {}
        
        f_groundings = ggg.evidence_for_node(parent_node)
        if len(f_groundings) == 0:
            return {}

        #assert len(f_groundings) == 1#, (len(f_groundings), esdc, str(esdc))
        f_grounding = f_groundings[0]

        if isinstance(f_grounding, PhysicalObject):
            f_path = f_grounding.path
        else:
            f_path = f_grounding

        assert isinstance(f_path, Path), f_path
        #assert esdc.childIsEsdcs("l") or esdc.childIsEmpty("l")
        for li, (l_node, l_groundings) in enumerate((node, ggg.evidence_for_node(node))
                                                    for node in factor.nodes_for_link("l")):
            for lj, l_grounding in enumerate(l_groundings):
                if "PATH" in l_node.type and isinstance(l_grounding, PhysicalObject):
                    l_grounding = l_grounding.path

                fdict = self.path_landmark_features(f_path, r_words, l_grounding)
                fdict = add_prefix("l_%d_%d_" % (li, lj), fdict)
                result_dict = merge(result_dict, fdict)
                #print len(fdict), [x for x in fdict.values() if x == 'l_0_0_w_from_F_behind_st']
        #assert esdc.childIsEsdcs("l2") or esdc.childIsEmpty("l2")            
        if factor.has_children("l2"):
            for l2i, (l2_node, l2_groundings) in enumerate((node, ggg.evidence_for_node(node))
                                                           for node in factor.nodes_for_link("l2")):
                for l2j, l2_grounding in enumerate(l2_groundings):            
                    if "PATH" in l2_node.type and isinstance(l2_grounding, PhysicalObject):
                        l2_grounding = l2_grounding.path

                    fdict = self.path_landmark_features(f_path, r_words, l2_grounding)
                    fdict = add_prefix("l2_%d_%d_" % (l2i, l2j), fdict)
                    result_dict = merge(result_dict, fdict)                

        return result_dict
    
    def path_landmark_features(self, f_path, r_words, l_grounding):

        if sf.math2d_dist(f_path.points_pts[-1], l_grounding.centroid2d) < 4:
            fdict = {"ends_close": 1}
        else:
            fdict = {"ends_close": 0}
            
        fdict = add_word_features(fdict, r_words)
        return fdict


    def object_landmark_features(self, agent, f_prism, r_words, l_prism):
        result_dict = {"dist_f_l": sf.math2d_dist(f_prism.centroid2d(), l_prism.centroid2d())}        

        result_dict = add_word_features(result_dict, r_words)
        
        return result_dict

    def np_features(self, f_words, object_grounding):
        """
        Compute features for a noun phrase, given a grounding. 
        """
        assert not isnan(object_grounding.points_xy[0][0])


        result_dict = {}        


        if hasattr(object_grounding, "tags"):
            lo_dict = language_object(f_words,
                                      [],
                                      object_grounding.tags)
            lo_dict = dict((key, value) for key, value in lo_dict.iteritems() if "flickr" not in key and "wordnet" not in key and "whole" not in key and "overlap" not in key and "cword" not in key)
            result_dict = merge(result_dict, lo_dict)
            

        return result_dict

                
    
    def extract_features(self, state, ggg, factors=[]):
        """
        Top level feature extraction method.  Assigns path groundings,
        then computes features.  It modifies the annotation.
        """
        new_evidences = assignPathGroundingsToGGG(state, ggg)
        from g3.graph import GGG
        ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)

        groundable_list = state.getObjectsSet() + state.getPlacesSet() + [state.getAgentId()]
        groundings = chain(*[[g for g in ggg.evidence_for_node(node)
                              if g in groundable_list] 
                             for node in ggg.nodes if not node.is_phi])

        groundings = [g for g in groundings if not isinstance(g, Path) and not None]


        fdict, namesdict = self.compute_features(ggg, factors)
        return fdict, namesdict



    def compute_features(self, ggg, factors = None, state_sequence=None):
        """
        Computes features for the unmodified annotation.  If factors
        isn't specified, does all factors.
        """

        factor_to_fnames = {}
        factor_to_fvalues = {}
        
        if factors == None:
            factors = [ggg.factor_from_id(fid) 
                       for fid in ggg.factor_ids]
        for factor in factors:
            fdict = self.factor_features(factor, ggg)
            fdict = add_prefix(factor.nodes_for_link("top")[0].type.split("_")[1] + "_", fdict)
            factor_to_fnames[factor.id] = fdict.keys()
            factor_to_fvalues[factor.id] = fdict.values()
            
        return factor_to_fvalues, factor_to_fnames
