from esdcs.esdcIo import annotationIo
from optparse import OptionParser
from environ_vars import SLU_HOME
from os.path import basename
import pickle_util
import random
from scipy import ceil

from dcrf3.dataset import ContinuousObservation, ContinuousDataset
from corpusMturk import readCorpus
from g3.annotation_to_ggg import annotation_to_ggg_map, assignPathGroundingsToGGG
from g3.graph import GGG
from counter import Counter

random.seed(0)

def ggg_to_observation(ggg, state, fe, esdc, id_base, counter, annotation,
                       true_class_value=None):
    factor = ggg.esdc_to_factor(esdc)
    phi_node = factor.nodes_with_type("phi")[0]
    labeled_class_value = ggg.evidence_for_node(phi_node)

    if ggg.context.agent == None:
        return None


    fdict, namesdict = fe.extract_features(state, ggg, [factor])

    if not len(fdict):
        return None

    factor = ggg.esdc_to_factor(esdc)
    if len(fdict[factor.id]) == 0:
        return None


    example_id = id_base + "_" + str(counter.cnt)
    counter.pp()
    obs = ContinuousObservation(example_id,
                                labeled_class_value,
                                true_class_value,
                                dict(zip(namesdict[factor.id],
                                         fdict[factor.id])),
                                [esdc], ggg, factor, annotation=annotation)
    return obs


def annotation_to_observations(annotation, fe, force_default_class_value,
                               default_class_value, counter, id_base):
    observations = []
    try:
        a_state, esdc_to_ggg = annotation_to_ggg_map(annotation)

        for g_index, (esdc, ggg) in enumerate(esdc_to_ggg.iteritems()):
            new_evidences = assignPathGroundingsToGGG(a_state, ggg)
            ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
            true_class_value = annotation.isGroundingCorrect(esdc)
            if true_class_value == None and default_class_value == None:
                continue
            elif true_class_value == None:
                true_class_value = default_class_value

            if force_default_class_value:
                labeled_class_value = default_class_value
            else:
                labeled_class_value =  true_class_value

            factor = ggg.esdc_to_factor(esdc)
            if factor != None:
                phi_node = factor.nodes_with_type("phi")[0]
                ggg.set_evidence_for_node(phi_node, labeled_class_value)

                obs = ggg_to_observation(ggg, a_state, fe, esdc,
                                         id_base, counter, annotation,
                                         true_class_value)

                if obs != None:
                    observations.append(obs)
    except:
        print "problem with", annotation.entireText
        #print annotation
        raise

    return observations
def generate_examples(id_base, corpus, feature_extractor, default_class_value,
                      force_default_class_value=False):

    print "extracting features"
    observations = []
    fe = feature_extractor
    counter = Counter()

    for i, annotation in enumerate(corpus):

        print i + 1, "of", len(corpus)
        cobs = annotation_to_observations(annotation,
                                          fe,
                                          force_default_class_value,
                                          default_class_value,
                                          counter, id_base)
        observations.extend(cobs)
        

    return observations

def main():

    parser = OptionParser()

    parser.add_option("--outfile_training",dest="training_fname",
                      help="Training Output Filename")
    parser.add_option("--outfile_test", dest="testing_fname",
                      help="Test Output Filename")
    parser.add_option("--infile_positive", dest="positive_fnames",
                      action="append", default=[],
                      help="Positive Filename; default to True if isGroundingCorrect is None")
    parser.add_option("--infile_negative", dest="negative_fnames",
                      action="append", default=[],
                      help="Negative Filename; default to False if isGroundingCorrect is None")
    parser.add_option("--infile_labeled", dest="labeled_fnames",
                      action="append", default=[],
                      help="Labeled examples; skip if isGroundingCorrect is None")

    parser.add_option("--infile_unlabeled", dest="unlabeled_fnames",
                      action="append", default=[],
                      help="unlabeld fnames")


    parser.add_option("--feature_extractor", dest="feature_extractor",
                      help="Feature Extractor Class")

    parser.add_option("--split", dest="split", type="string",
                      help="'random' to split randomly; 'scenario' to split " +
                      "by scenario.")

    parser.add_option("--training_examples", dest="training_examples",
                      action="append",
                      help="Examples that are in the training set; others go in the test set.  Can be passed more than once. ")


    (options, args) = parser.parse_args()



    try:
        from  g3.feature_extractor.esdc_features import EsdcFeatures
        from  g3.feature_extractor.esdc_flattened_features import EsdcFlattenedFeatures
        from  g3.feature_extractor.grounded_features import GGGFeatures
        from  g3.feature_extractor.rl_features import RLFeatures
        from  g3.feature_extractor.bolt_features import BoltFeatures
        from  g3.feature_extractor.ikea_features import IkeaFeatures
        from  g3.feature_extractor.sr_features import SrFeatures
        #feature_extractor = semantic_map.esdc_semantic_map2.esdc_semantic_map()
        feature_extractor_cls = eval(options.feature_extractor)
        feature_extractor = feature_extractor_cls()
    except:
        print "error doing", options.feature_extractor
        raise

    observations = list()

    for positive_fname in options.positive_fnames:
        corpus = annotationIo.load(positive_fname)
        new_examples = generate_examples(basename(positive_fname), corpus, feature_extractor,
                                         default_class_value=True)
        if len(new_examples) == 0:
            raise ValueError("No examples from" + `positive_fname`)
        observations.extend(new_examples)

    for negative_fname in options.negative_fnames:
        corpus = annotationIo.load(negative_fname)
        new_examples = generate_examples(basename(negative_fname), corpus, feature_extractor,
                                         default_class_value=False)
        if len(new_examples) == 0:
            raise ValueError("No examples from" + `negative_fname`)

        observations.extend(new_examples)

    for labeled_fname in options.labeled_fnames:
        corpus = annotationIo.load(labeled_fname, check=False)
        new_examples = generate_examples(basename(labeled_fname), corpus, feature_extractor,
                                         default_class_value=None)
        if len(new_examples) == 0:
            raise ValueError("No examples from" + `labeled_fname`)
        observations.extend(new_examples)


    for unlabeled_fname in options.unlabeled_fnames:
        corpus = annotationIo.load(unlabeled_fname)
        new_examples = generate_examples(basename(unlabeled_fname), corpus, feature_extractor,
                                         default_class_value=None, force_default_class_value=True)
        if len(new_examples) == 0:
            raise ValueError("No examples from" + `unlabeled_fname`)
        observations.extend(new_examples)


    if options.split == "scenario":
        mturkCorpus = readCorpus.Corpus("%s/data/corpusCommandsForVideoSmallFilesOnly/" % SLU_HOME)
        scenario_names = list(set(mturkCorpus.assignmentForId(obs.annotation.assignmentId.split("_")[0]).scenario.name for obs in observations))
        random.shuffle(scenario_names)

        n_training_scenarios = int(ceil(len(scenario_names) * 0.7))

        training_scenarios = scenario_names[:n_training_scenarios]
        testing_scenarios = scenario_names[n_training_scenarios:]

        training = [o for o in observations if
                    mturkCorpus.assignmentForId(o.annotation.assignmentId.split("_")[0]).scenario.name
                    in training_scenarios]

        testing = [o for o in observations if
                   mturkCorpus.assignmentForId(o.annotation.assignmentId.split("_")[0]).scenario.name
                   in testing_scenarios]
    elif options.split == "annotation":
        '''
        Splits the examples, grouped by annotation.
        If the spatial relations corpus is included,
        that data will be in the training set only.
        '''
        training = []
        testing = []
        sr_ids = []
        ids = []

        for o in observations:
            aid = o.annotation.id
            if ((aid not in ids) and ("sr_" not in aid)):
                ids.append(aid)
            elif "sr_" in aid:
                sr_ids.append(aid)

        random.shuffle(ids)
        n_training_ids = int(ceil(len(ids) * 0.7))

        training_ids = ids[:n_training_ids]
        testing_ids = ids[n_training_ids:]

        training = [o for o in observations if o.annotation.id in
                    training_ids or o.annotation.assignmentId in sr_ids]
        testing = [o for o in observations if o.annotation.id in
                    testing_ids]
    elif options.split == "random":
        random.shuffle(observations)
        n_training = int(ceil(len(observations) * 0.7))
        training = observations[0:n_training]
        testing = observations[n_training:]
    elif options.split == "labeled_annotation":
        training_ids = set()
        training = []
        testing = []
        for training_fname in options.training_examples:
            ds = pickle_util.load(training_fname)
            for ex in ds.observations:

                training_ids.add(ex.annotation.id)
                training_ids.add(ex.annotation.id.split("_")[0])
        print "training", training_ids
        for example in observations:
            if example.annotation.id in training_ids:
                training.append(example)
            else:
                aid = example.annotation.id.split("_")[0]
                if aid in training_ids:
                    training.append(example)
                else:
                    print "skipping", example.annotation.id, aid
                    testing.append(example)
        print "labeled training", len(training)
        print "labeled testing", len(testing)
    elif options.split == "labeled_file":
        training = []
        testing = []
        for example in observations:
            if "training" in example.annotation.fname:
                training.append(example)
            elif "testing" in example.annotation.fname:
                testing.append(example)
            else:
                training.append(example)


    elif options.split == "labeled":
        training_ids = set()
        training = []
        testing = []
        for training_fname in options.training_examples:
            ds = pickle_util.load(training_fname)
            for ex in ds.observations:
                print "id", ex.id
                training_ids.add(ex.id)

        for example in observations:
            print "example", example.id
            if example.id in training_ids:

                training.append(example)
            else:
                testing.append(example)

    else:
        raise ValueError("Unexpected split type: " + `options.split`)



    training_dataset = ContinuousDataset(training, feature_extractor_cls)
    testing_dataset = ContinuousDataset(testing, feature_extractor_cls)

    print "saving ", len(training), " examples to:", options.training_fname
    pickle_util.save(options.training_fname, training_dataset)

    print "saving ",len(testing), " examples to:", options.testing_fname
    pickle_util.save(options.testing_fname, testing_dataset)

if __name__ == "__main__":
    main()
