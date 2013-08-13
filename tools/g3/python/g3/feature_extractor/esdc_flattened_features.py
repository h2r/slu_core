from features.feature_utils import merge, EsdcFeatureTypeError
from grounded_features import GGGFeatures
from itertools import combinations
from esdcs.dataStructures import ExtendedSdc
from spatial_features.groundings import assignPathGroundings, Path

class EsdcFlattenedFeatures:
    def __init__(self):
        self.sm = GGGFeatures()


    def esdc_features(self, annotation, esdc):
        all_groundings = []
        for key in esdc.fieldNames:
            for child in esdc.children(key):
                if isinstance(child, ExtendedSdc):
                    groundings = annotation.getGroundings(child)
                    all_groundings.extend(groundings)
        words = [w.lower() for w in esdc.text.split()] + ["null"]

        all_groundings = [("g%i" % i, g) for i, g in enumerate(all_groundings)]

        two_arg_feature_methods = [self.sm.object_object_start_end,
                                   self.sm.path_landmark_features,
                                   self.sm.object_landmark_features,
                                   ]
        
        result_dict = {}
        for x1, x2 in combinations(all_groundings, r=2):
            for (n1, g1), (n2, g2) in [(x1, x2), (x2, x1)]:
                for method in two_arg_feature_methods:
                    args = dict(agent=annotation.agent,
                                f_grounding=g1, l_grounding=g2, r_words=words,
                                prefix="%s_%s" % (n1, n2)
                                )
                    try:
                        fdict = method(**args)
                        result_dict = merge(result_dict, fdict)
                    except EsdcFeatureTypeError:
                        pass

        one_arg_feature_methods = []
        for g in all_groundings:
            for method in one_arg_feature_methods:
                fdict = method(g)
                result_dict = merge(result_dict, fdict)

        

        
        return result_dict
        
        
    def extract_features(self, annotation):
        """
        Top level feature extraction method.  Assigns path
        groundings, then computes features.
        It modifies the annotation.
        """
        esdc_to_fnames = {}
        esdc_to_fvalues = {}
        
        groundings = []
        for esdc in annotation.flattenedEsdcs:
            print "agent", annotation.agent
            assignPathGroundings(esdc, annotation)
            groundings.extend(annotation.getGroundings(esdc))
            esdc_to_fnames[esdc] = {}
            esdc_to_fvalues[esdc] = {}
            

        groundings = [g for g in groundings if not isinstance(g, Path)]

        for g in groundings:
            self.sm.add_landmark(g)

        
            
            
        for esdc in annotation.esdcs:
            fdict = self.esdc_features(annotation, esdc)
            esdc_to_fnames[esdc] = fdict.keys()
            esdc_to_fvalues[esdc] = fdict.values()
            
        return esdc_to_fvalues, esdc_to_fnames
