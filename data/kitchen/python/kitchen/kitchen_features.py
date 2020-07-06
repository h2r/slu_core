import tokenizer
from features.feature_utils import remove_stopwords
from kitchen.planningLanguage import decompile

class GGGFeatures:
    def __init__(self):
        self.tokenizer = tokenizer.IndexedTokenizer()
    
    def features(self, ggg, factor, state_sequence):
        """
        Computes features for a factor, given a ggg with evidence, the
        factor, and a state sequence.  Returns a dictionary, key is
        feature name, value is float feature values.
        """
        words_string = ggg.evidence_for_node(factor.nodes_for_link("r")[0])[0].text
        words = remove_stopwords([w.text.lower() 
                                  for w in self.tokenizer.tokenize(words_string)])
        words = [w for w in words if ("," not in w and "." not in w and "!" not in w
                                      and "(" not in w and ")" not in w and
                                      w not in ["and", "in"])]

        feature_map = {}

        action_strings = [decompile([(a, s)]) for a, s in state_sequence] 
        #if len(action_strings) != len(set(action_strings)):
        #    feature_map["duplicate_actions"] = 1.0
        #else:
        #    feature_map["no_duplicate_actions"] = 1.0


        word_to_arg_equals_word = {}
        for word in words:
            word_to_arg_equals_word[word] = False
            for i, (action, state) in enumerate(state_sequence):
                for arg in action.args:
                    if hasattr(arg, "name"):
                        arg_name = "a_" + arg.name
                    else:
                        arg_name = "s_" + str(arg)
                    arg_name = arg_name.replace(" ", "_")
                    fname = "w_%s_%s_%s" % (word, action.name, arg_name)
                    feature_map[fname] = 1.0
                    if arg_name[2:] == word:
                        feature_map.setdefault("arg_equals_word", 0)
                        feature_map["arg_equals_word"] += 1.0
                        feature_map.setdefault("a_%s_equals_word" % (arg_name), 0)
                        
                        feature_map["a_%s_equals_word" % (arg_name)] = 1.0
                        word_to_arg_equals_word[word] = True
                    #feature_map["w_%s_a_%s_%d" % (word, action.name, i)] = 1.0
                    #feature_map["w_%s_a_%s_first" % (word, state_sequence[0][0].name)] = 1.0
                    #feature_map["w_%s_a_%s_last" % (word, state_sequence[-1][0].name)] = 1.0
            fname = "w_%s_%s" % (word, action.name)
            feature_map[fname] = 1.0
        for word, value in word_to_arg_equals_word.iteritems():
            if not value:
                feature_map["w_%s_has_no_arg" % word] = 1.0
        return feature_map

    def compute_features(self, ggg, factors, state_sequence):
        assert len(factors) == 1
        factor = factors[0]
        features = self.features(ggg, factor, state_sequence)
        return {factor.id: features.values()}, {factor.id:features.keys()}

    def add_landmark(self, *args, **markgs):
        pass
        
