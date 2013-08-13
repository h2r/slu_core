import pickle_util

def main():
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("--dfactor", dest="dfactor", default=36)
    (options, args) = parser.parse_args()

    original_dataset_fname = args[0]
    convert_dataset_fname = args[1]
    save_fname = args[2]
    original_dataset = pickle_util.load(original_dataset_fname)
    convert_dataset = pickle_util.load(convert_dataset_fname)
    obs = convert_dataset.observations
    discrete_dataset = original_dataset.to_discrete_dataset(dataset=obs, dfactor=int(options.dfactor))
    print "saving to...", save_fname
    print "...with ", len(discrete_dataset.fnames), "features"
    pickle_util.save(save_fname, discrete_dataset)
    print "done"

if __name__=="__main__":
    main()
