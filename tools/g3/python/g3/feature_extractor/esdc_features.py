from features.feature_utils import add_prefix, merge, add_word_features
from features.linguistic_features import depluralize

class EsdcFeatures:
    """
    Features involving esdcs only and not groundings.  Used to train
    the ESDC reranker.
    """
    def factor_features(self, factor, state, ggg):
        f_dict = {}
        esdc = ggg.factor_to_esdc(factor)
        if esdc.isLeafObject():
            f_dict["is_leaf_object"] = True
        else:
            for word_standoff in esdc.r:
                r_word = word_standoff.text

                for lfield in ["l", "l2"]:
                    for cesdc in esdc.children(lfield):
                        for l_word in cesdc.text.split():
                            f_dict["join_r_%s_%s_%s" % 
                                   (r_word, lfield, l_word)] = True
                        


        f_dict["type_%s" % esdc.type] = True

            

        for key in esdc.fieldNames:
            if esdc.childIsEsdcs(key):

                f_dict["%s_is_esdcs" % key] = True
                child_types = set()
                for child in esdc.children(key):
                    child_types.add(child.type)
                    
                
                for esdc_type in child_types:
                    f_dict["child_type_%s_%s" % (key, esdc_type)] = True
                    

            elif esdc.childIsListOfWords(key):
                f_dict["%s_is_list_of_words" % key] = True

                for i, standoff in enumerate(esdc.children(key)):
                    word = depluralize(standoff.text.lower())
                    f_dict["%s_%s" % (key, word)] = True
                    f_dict["%s_%s_%d" % (key, word, i)] = True

                for i, standoff1 in enumerate(esdc.children(key)):
                    word1 = depluralize(standoff1.text.lower())
                    for j, standoff2 in enumerate(esdc.children(key)):
                        word2 = depluralize(standoff2.text.lower())
                        if (i == j):
                            continue
                        f_dict["pairs_%s_%s_%s" % (key, word1, word2)] = True
                
            elif esdc.childIsEmpty(key):
                f_dict["%s_is_empty" % key] = True
            else:
                raise ValueError("Strange type for key: "+ `key` +
                                 " esdc: " + `esdc`)

        return f_dict
        

    def compute_features(self, state, ggg, factors):
        """
        Computes features for the unmodified annotation.
        """

        factor_to_fnames = {}
        factor_to_fvalues = {}

        if factors == None:
            factors = [ggg.graph.get_factor_with_id(fid) 
                       for fid in ggg.graph.get_factor_id_list()]
        
        for factor in factors:
            esdc = ggg.factor_to_esdc(factor)
            r_words = [w.text.lower() for w in esdc.r] + ["null"]
            words = [w.lower() for w in esdc.text.split()] + ["null"]

            fdict = self.factor_features(factor, state, ggg)
            base_features = merge(fdict, add_prefix(esdc.type + "_", fdict))
                          
            fdict = merge(base_features, add_prefix("r_", 
                                                    add_word_features(base_features, 
                                                                      r_words)))
            fdict = merge(fdict, add_word_features(base_features, 
                                                   words))

            factor_to_fnames[factor.id] = fdict.keys()
            factor_to_fvalues[factor.id] = fdict.values()
            
        return factor_to_fvalues, factor_to_fnames

    def extract_features(self, a_state, ggg, factors=None):
        """
        Top level feature extraction method.  Assigns path groundings,
        then computes features.  It modifies the annotation.
        """

        try:
            fdict, namesdict = self.compute_features(a_state, ggg, factors)
        except:
            print "exception on", a_state, ggg
            raise
        return fdict, namesdict
