from grounded_features import GGGFeatures

class RLFeatures:
    def __init__(self):
        self.ggg_features = GGGFeatures()
        

    def filter(self, names, values):
        filtered_names = []
        filtered_values = []
        for name, value in zip(names, values):
            if "quadrant" in name:
                continue
            if "octant" in name:
                continue
            if "avs" in name:
                continue
            if "_whole_" in name:
                continue
#            if "3d" in name:
#                continue
            if "avg" in name:
                continue
            if "axes" in name:
                continue
            if "Axes" in name:
                continue
            if "angleBtwn" in name:
                continue
            if "eigen" in name:
                continue
            if "orient" in name:
                continue
            if "left" in name:
                continue
            if "right" in name:
                continue
            if "behind" in name:
                continue
            if "front" in name:
                continue
            if "_angle_" in name:
                continue
            if "Perimeter" in name:
                continue
            if "landmarkArea" in name:
                continue
            if "landmarkArea" in name:
                continue
            if "angleBtwnLinearzied" in name:
                continue
            if "distFigureCenterOfMass" in name:
                continue
            if "distBtwnCentroids" in name:
                continue
            if "figureStartToEnd" in name:
                continue
            if "figureCenterOfMass" in name:
                continue
            if "moving" in name or "still" in name:
                continue
            if "ratioDistStartEnd" in name:
                 continue
            if "averageDistStartEndLandmark" in name:
                 continue

            if "flickr" in name:
                continue
            if "wordnet" in name:
                continue
            if "overlap" in name:
                continue
            

#            if "Axes" in name:
#                continue
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
