from grounded_features import GGGFeatures

class BoltFeatures:
    def __init__(self):
        self.ggg_features = GGGFeatures()
        
    def add_landmark(self, lmark):
        self.ggg_features.add_landmark(lmark)
    def filter(self, names, values):
        filtered_names = []
        filtered_values = []
        for name, value in zip(names, values):
            if "EVENT" in name and ("_avs_" in name or "_avg_" in name
                                    or "right_end" in name or "behind_end" in name
                                    or "left_end" in name or "front_end" in name
                                    or "front_st" in name or "right_st" in name 
                                    or "left_st" in name or "behind_st" in name
                                    or "orientDir" in name or "dist" in name or "Dist" in name
                                    or "quadrant" in name or "Axes" in name or "axes" in name
                                    or "ratio" in name or "orient" in name
                                    or "landmarkArea" in name or "angle" in name
                                    ):

                continue

            if "Perimeter" in name:
                continue
            #print "using", name
            filtered_names.append(name)
            filtered_values.append(value)
        
        return filtered_names, filtered_values
    def extract_features(self, *args, **margs):
        factor_to_fvalues, factor_to_fnames = self.ggg_features.extract_features(*args, **margs)

        filtered_factor_to_fnames = {}
        filtered_factor_to_fvalues = {}

        for factor in factor_to_fvalues.keys():
            names = factor_to_fnames[factor]
            values = factor_to_fvalues[factor]
            filtered_names, filtered_values = self.filter(names, values)
            filtered_factor_to_fnames[factor] = filtered_names
            filtered_factor_to_fvalues[factor] = filtered_values
        return filtered_factor_to_fvalues, filtered_factor_to_fnames
        
    def compute_features(self, *args, **margs):
        factor_to_fvalues, factor_to_fnames = self.ggg_features.compute_features(*args, **margs)

        filtered_factor_to_fnames = {}
        filtered_factor_to_fvalues = {}

        for factor in factor_to_fvalues.keys():
            names = factor_to_fnames[factor]
            values = factor_to_fvalues[factor]
            filtered_names, filtered_values = self.filter(names, values)
            filtered_factor_to_fnames[factor] = filtered_names
            filtered_factor_to_fvalues[factor] = filtered_values
        return filtered_factor_to_fvalues, filtered_factor_to_fnames
