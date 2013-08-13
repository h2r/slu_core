from dcrf3.feature_cache import FeatureCache
from optparse import OptionParser

import pickle_util

def main():
    parser = OptionParser()

    parser.add_option("--training_filename",dest="training_fname", 
                      help="Training Filename", metavar="FILE")
    parser.add_option("--save_filename", dest="save_fname",
                      help="Save Filename", metavar="FILE")

    (options, args) = parser.parse_args()

    print "opening positive dataset"
    dataset_all = pickle_util.load(options.training_fname)
    print "dataset", dataset_all

    feature_cache = FeatureCache(dataset_all)
    feature_cache.cache_feature_counts()
    print "saving to...", options.save_fname
    print "...with ", len(feature_cache), "features"
    FeatureCache.save(feature_cache, options.save_fname)
    print "done"

if __name__ == "__main__":
    main()
