from scipy import mod, isnan, arange
from features.linguistic_features import sfe_language_object as language_object
from spatial_features.groundings import Path, PhysicalObject, Place
from g3.annotation_to_ggg import assignPathGroundingsToGGG
from assert_utils import array_equal
import numpy as na
from math import degrees
import math
import spatial_features_cxx as sf
from spatial_features_cxx import vectors
import collections
from itertools import chain
from features.feature_utils import add_prefix, merge, add_word_features, compute_fdict, average_dicts, convert_words

class GGGFeatures:
    def __init__(self):

        self.landmarks = []

        #cache landmark context
        self.landmark_context = collections.defaultdict(lambda : set())
        for i in range(len(self.landmarks)):
            if(mod(i, 50) == 0):
                print i, "of", len(self.landmarks)
            self._get_landmark_context(i)

    def add_landmark(self, lmark):
        assert lmark != None, lmark
        for i, other_lmark in enumerate(self.landmarks):

            if other_lmark == lmark:
                return i

        self.landmarks.append(lmark)
        self._get_landmark_context(len(self.landmarks)-1)
        self._update_landmark_context(lmark)

        return len(self.landmarks)-1

    def _update_landmark_context(self, new_lmark):
        for i, lmark in enumerate(self.landmarks):
            if lmark == new_lmark:
                continue
            if sf.math2d_dist(lmark.centroid2d, new_lmark.centroid2d) < 10.0:
                for t in new_lmark.tags:
                    self.landmark_context[i].add(t)

    def _get_landmark_context(self, i):
        return set()
        if(not self.landmark_context.has_key(i)):
            known_objects = set()
            landmark = self.landmarks[i]

            for other_lmark in self.landmarks:
                #curr_visible = self.get_visible_tags(landmark[:,j], max_dist=10.0)[0]
                if (hasattr(landmark, "centroid2d") and
                    sf.math2d_dist(landmark.centroid2d, other_lmark.centroid2d) < 10.0):
                    for t in other_lmark.tags:
                        known_objects.add(t)

            self.landmark_context[i] = known_objects

        return self.landmark_context[i]

    def factor_features(self, factor, ggg):
        """
        Computes features for a particular factor.
        """
        parent_nodes = [node for node in factor.nodes_for_link('top') if 'BOUND' not in node.type]
        try:
            assert len(parent_nodes) == 1, "There should only be one (non-bound) top node"
        except:
            import pdb; pdb.set_trace()
        parent_node = parent_nodes[0]
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

    def object_object_averages(self, agent, f_grounding, r_words, l_grounding):
        """
        Compute features along the entire path of the figure and landmark.
        """
        start_t = min(f_grounding.start_t, l_grounding.start_t)
        end_t = max(f_grounding.end_t, l_grounding.end_t)

        step_size = (end_t - start_t) / 5.0

        fdicts = []
        if step_size == 0:
            step_size = 1

        # iterate at least once
        if start_t == end_t:
            end_t = end_t + step_size
        for t in arange(start_t, end_t + step_size, step_size):
            f_prism = f_grounding.prismAtT(t)
            l_prism = l_grounding.prismAtT(t)
            #print "f_prism = ", f_prism
            #print "l_prism = ", l_prism

            fdict = self.object_landmark_features(agent, f_prism, r_words,
                                                  l_prism)
            #print "landmark supports figure", [(key, value) for key, value in fdict.iteritems()
             #                                  if "F_3dSupportsLandmarkFigure" in key]
            #print "landmark supports figure", [(key, value) for key, value in fdict.iteritems()
             #                                  if "F_3dSupportsFigureLandmark" in key]

            fdicts.append(fdict)


        merged = average_dicts(fdicts)
        max_dict = {}
        for key, value in merged.iteritems():
            farray = [fdict[key] for fdict in fdicts]
            max_dict["max_%s" % key] = max(farray)

        #merged = merge(merged, max_dict)
        #averaged_dict = add_prefix("avg_", merged)
        averaged_dict = max_dict
        #print "avg landmark supports figure", [(key, value) for key, value in averaged_dict.iteritems()
         #                                      if "F_3dSupportsLandmarkFigure" in key]
        #print "avg landmark supports figure", [(key, value) for key, value in averaged_dict.iteritems()
         #                                      if "F_3dSupportsFigureLandmark" in key]


        result_dict = add_word_features(averaged_dict, r_words)
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

        fdict = self.object_object_averages(agent, f_grounding, r_words, l_grounding)
        fdict = add_prefix("avg_%s" % (prefix), fdict)
        result_dict = merge(result_dict, fdict)
        for r_word in r_words:
            if l_grounding.path.max_dist_from_start() > 0.1:
                result_dict["%s_w_%s_l_moving" % (prefix, r_word)] = 1
            else:
                result_dict["%s_w_%s_l_still" % (prefix, r_word)] = 1

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
        fdict = compute_fdict(sf.sfe_f_path_l_polygon_names(),
                              sf.sfe_extract_f_path_l_polygon(f_path.points_xytheta,
                                                              l_grounding.points_xy,
                                                              normalize=True))

        fdict = add_word_features(fdict, r_words)
        return fdict


    def object_landmark_features(self, agent, f_prism, r_words, l_prism):
        result_dict = {}

        assert not isnan(l_prism.points_xy[0][0])
        assert not isnan(f_prism.points_xy[0][0])

        prism_dict = compute_fdict(sf.sfe_f_prism_l_prism_names(),
                                   sf.sfe_f_prism_l_prism(f_prism, l_prism, normalize=True))
        result_dict = merge(result_dict, prism_dict)

        ax, ay, agent_theta = agent.path.points_xytheta


        for name, theta in [("avs_theta_start", agent_theta[0]), ("avs_theta_end", agent_theta[-1]),
                            ("avs_theta_avg", na.mean(agent_theta))]:
            avs_dict = compute_fdict(sf.spatial_features_names_avs_polygon_polygon(),
                                     sf.spatial_features_avs_polygon_polygon(f_prism.points_xy,
                                                                             l_prism.points_xy,
                                                                             theta))

            result_dict = merge(result_dict, add_prefix(name, avs_dict))            
        #print "******************"
        #theta = agent_theta[0]
        theta = agent_theta[0]
        #print "agent theta", degrees(theta)
        #print "f_centroid", f_prism.centroid2d()
        #print "l_centroid", l_prism.centroid2d()
        if not array_equal(f_prism.centroid2d(), l_prism.centroid2d()):
            angle_btwn_points = sf.math2d_angle(na.array(f_prism.centroid2d()) - na.array(l_prism.centroid2d()))
            #print "angle between points", degrees(angle_btwn_points)
            angle = theta - angle_btwn_points - math.pi/4
            #print "angle", degrees(angle)
            quadrant = sf.math2d_angle_to_quadrant(angle)
            octant = sf.math2d_angle_to_octant(angle + math.pi/8)
            #print "quadrant", quadrant
            #print "******************"
        else:
            quadrant = -1
            octant = -1

            #result_dict["f_in_l_quadrant_%d" % quadrant] = 1
        result_dict["f_in_l_quadrant"] = quadrant
        for i in range(-1, 8):
            result_dict["f_in_l_octant_%d" % i] = 0
        result_dict["f_in_l_octant_%d" % octant] = 1


        result_dict = dict((f, v) for f, v in result_dict.iteritems() if (("avsg" not in f) and
                                                                          ("avsHeightExp" not in f) and
                                                                          ("avsResult" not in f)))


        result_dict = add_word_features(result_dict, r_words)


        return result_dict

    def np_features(self, f_words, object_grounding):
        """
        Compute features for a noun phrase, given a grounding.
        """
        assert not isnan(object_grounding.points_xy[0][0])


        result_dict = {}
        polygon_dict = compute_fdict(sf.flu_polygon_names(vectors(f_words)),
                                     sf.flu_polygon(vectors(f_words), object_grounding.points_xy, True))

        figure_i = self.add_landmark(object_grounding)
        result_dict = merge(result_dict, polygon_dict)


        if hasattr(object_grounding, "tags"):
            visible_objects = self._get_landmark_context(figure_i)
            lo_dict = language_object(f_words,
                                      visible_objects,
                                      object_grounding.tags)

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
            #fdict = dict((key, value) for key, value in fdict.iteritems()
            #             if "flickr" not in key and "wordnet" not in key and "_avs_" not in key and "_avg_" not in key)
            fdict["prior"] = 1.0
            factor_to_fnames[factor.id] = fdict.keys()
            factor_to_fvalues[factor.id] = fdict.values()

        return factor_to_fvalues, factor_to_fnames
