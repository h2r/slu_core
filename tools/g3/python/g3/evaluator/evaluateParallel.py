import cPickle
import time
import pool_27
import os
import shelve
import sys
import traceback
import math
import logging
from logging import warn, debug, info, error

from dialog.dialog_manager import DialogManager
from environ_vars import SLU_HOME
from esdcs.esdcIo import annotationIo
from esdcs.extractor import extractor_utils
from g3.cost_functions.cost_function_utils import make_cost_function_class
# from g3.cost_functions.cost_function_crf import CostFnCrf
from g3.feature_extractor.grounded_features import GGGFeatures
from g3.state import state_type_from_name
from multiprocessing import cpu_count
from os.path import dirname


dm = None
EVAL_BASE_PATH = 'dataEvaluation/data/evaluation-run-'
LOG_FOLDER = 'evaluation_logs'


def create_evaluation_logger(directory, annotation_id):
    logger = logging.getLogger(annotation_id)
    logger.setLevel(logging.DEBUG)

    ch = logging.FileHandler(filename=os.path.join(directory, annotation_id + '.log'), mode='w')
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def create_root_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
create_root_logger()


def run_evaluation(desc, annotation, state_cls, esdc_extractor_func, entropy_metric, num_questions, num_answers, question_type):
    global dm
    assert entropy_metric != None
    log = logging.getLogger(annotation.id)
    log.debug("running %s %s" % (desc, entropy_metric))
    try:
        if num_questions >= 0:
            log.info("Running num questions evaluation")
            num_asked, entries = dm.num_questions_evaluation(
                                   annotation,
                                   state_cls,
                                   esdc_extractor_func,
                                   entropy_metric=entropy_metric,
                                   numToReturn=100,
                                   num_questions=num_questions,
                                   num_answers=num_answers,
                                   question_type=question_type
                                   )
        elif num_questions == -1:
            log.info("Running all questions evaluation")
            num_asked, entries = dm.all_questions_evaluation(annotation,
                                   state_cls,
                                   esdc_extractor_func,
                                   numToReturn=100,
                                   num_answers=num_answers
                                   )
        elif num_questions == -2:
            log.info("Running decision based evaluation")
            num_asked, entries = dm.decision_based_evaluation(
                                              annotation,
                                              state_cls,
                                              esdc_extractor_func,
                                              entropy_metric,
                                              numToReturn=100)

        else:
            raise ValueError("Invalid num_questions parameter received. Must be -1, -2, 0, or positive integer.")
        log.debug("got %d" % len(entries))

        return (desc,
                entries,
                annotation,
                num_asked)
    except:
        log.error("exception on %s %s %s" % (desc, annotation.id, annotation.entireText))
        error(traceback.format_exc())
        raise

def evaluateDataSet(model, corpus, test_set, esdc_extractor_func,
                    state_cls,
                    entropy_metric,
                    useRrt = True, runId=-1,
                    multi_esdcs=False, use_merging=False,
                    resolver = None, qa_corpora = [],
                    num_questions=0,
                    num_answers=1,
                    force_sync=False,
                    question_type='targeted',
                    random_seed=10):
    if runId == -1:
        runId = 1
        while True:
            if os.path.isdir(EVAL_BASE_PATH + '%d' % runId):
                runId += 1
            else:
                break

    dirToUse = EVAL_BASE_PATH + '%d' % runId
    if not os.path.exists(dirToUse):
        os.makedirs(dirToUse)
    global dm
    dm = DialogManager(model, dirToUse, useRrt,
                       use_merging, multi_esdcs, resolver, corpus, qa_corpora,
                       random_seed=random_seed)

    if test_set != None:
        testIds = set()
        for cobs in test_set.observations:
            testIds.add(cobs.annotation.assignmentId)
    else:
        testIds = None

    resultsFname = '%s/evaluationResults.shelf' % dirToUse
    modelFname = '%s/model.pck' % dirToUse
    resultsDir = dirname(resultsFname)
    logsDir = os.path.join(resultsDir, LOG_FOLDER)
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)
    if not os.path.exists(logsDir):
        os.makedirs(logsDir)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(filename=os.path.join(resultsDir, 'evaluateParallel.log'), mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root_log = logging.getLogger()
    root_log.addHandler(fh)
    try:
        args = []
        annotations = [a for a in corpus if testIds == None or a.assignmentId in testIds]
        # annotations = [a for a in corpus if a.assignmentId == '1N0XWCDO610E6C35ZFK4KVSUV50TI4']
        for i, annotation in enumerate(annotations):
#            if i + 1 != 8:
#                 continue
            desc ="annotation %d of %d" % (i + 1, len(annotations))
            log = create_evaluation_logger(logsDir, annotation.id)
            args.append((desc, annotation, state_cls, esdc_extractor_func, entropy_metric, num_questions, num_answers, question_type))

        pool = pool_27.Pool(processes=min(cpu_count(), 4), maxtasksperchild=1)

        results = shelve.open(resultsFname, protocol=2, flag='c')
        totalExamples = len(args)
        startTime = time.time()

        callback_state = dict(processed_examples=0,
                              num_questions_asked=0)


        def callback(result):
            desc, result, annotation, num_questions_asked = result
            info("done with %s" % desc)
            results[annotation.assignmentId] = (result, annotation)
            results.sync()
            callback_state["processed_examples"] += 1
            callback_state["num_questions_asked"] += num_questions_asked
            progress = float(callback_state["processed_examples"])/totalExamples
            now = time.time()
            elapsedMinutes = (now - startTime) / 60.0
            estimatedTotal = elapsedMinutes / progress
            info("progress: %.2f%%" % (progress * 100.0))
            print "progress: %.2f%%. Going for %.2f minutes, about %.2f minutes remaining." % (progress * 100.0, elapsedMinutes, estimatedTotal - elapsedMinutes)
            info("(Going for %.2f minutes," % elapsedMinutes)
            info("about %.2f minutes remaining)" % (estimatedTotal - elapsedMinutes))
        #args = args[2:3]
        for arg in args:
            if force_sync:
                pool.apply_sync(run_evaluation, arg, callback=callback)
            else:
                pool.apply_async(run_evaluation, arg, callback=callback)



        while callback_state["processed_examples"] != len(args):
            time.sleep(1)

        debug("asked %d questions." % callback_state["num_questions_asked"])
        debug("processed %d annotations" % callback_state["processed_examples"])
        pool.close()
        pool.join()
        # while len(args) != 0:
        #     run_args = args.pop(0)
        #     result, annotation = run_evaluation(*run_args)
        #     results[annotation.assignmentId]= (result, annotation)
        #     results.sync()

    except Exception as e:
        error(traceback.format_tb( sys.exc_info()[2]))
        error(e)
        error("command %s" % annotation.entireText)
        raise
    finally:
        info("saving %s %s" % (resultsFname, modelFname))
        results.close()

def countNumTestInCorpus(corpus, test_set):
    testIds = set()
    for cobs in test_set.observations:
         testIds.add(cobs.annotation.assignmentId)

    count = 0
    for i, annotation in enumerate(corpus):
        if annotation.assignmentId in testIds:
            count += 1

    debug(count)

def generate_evaluation_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--cost-function-class", dest="cost_function_class")
    parser.add_option("--model", dest="model_fname")
    parser.add_option("--test_set", dest="test_set_fname", default=None)
    parser.add_option("--corpus-fname", dest="corpus_fname", action="append")
    parser.add_option("--qa_corpus_1", dest="qa_corpus_fname_1", default=None)
    parser.add_option("--qa_corpus_2", dest="qa_corpus_fname_2", default=None)
    parser.add_option("--runid", dest="run_id", type="int", default=-1)
    parser.add_option("--userrt", dest="use_rrt", action="store_true", default=False)
    parser.add_option("--esdcmulti", dest="esdc_multi", type="string", default="False")
    parser.add_option("--state-type",dest="state_type",
                      help="State or Agent Type", metavar="FILE")


    parser.add_option("--esdc-extractor", type="string", dest="esdc_extractor")
    parser.add_option("--esdc-extractor-model", type="string",
                      dest="esdc_extractor_model")
    parser.add_option("-m", "--merging", dest="use_merging")

    parser.add_option("--resolver-type", dest="resolver_type", help="Coreference resolver type")

    parser.add_option("--entropy-metric", dest="entropy_metric", help="Name for entropy metric")
    parser.add_option("--num-questions", dest="num_questions", type="int",
            help="number of questions to ask. -1 will ask all available questions, -2 will choose number dynamically", default=0)
    parser.add_option("--num-answers", dest="num_answers", type="int",
                      help="number of answers per question to use", default=0)
    parser.add_option("--force_sync", dest="force_sync", default="False", help="Force synchronous (not parallel) evaluation")
    parser.add_option("--question_type", dest="question_type", default="targeted", help="Type of question to ask. Can be 'targeted' or 'yn'")
    parser.add_option("--random_seed", dest="random_seed", default=10, type="int")
    return parser

def main():
    parser = generate_evaluation_parser()

    (options, args) = parser.parse_args()
    evaluateParallel(options)

def evaluateParallel(options):
    cost_function_cls = make_cost_function_class(options.cost_function_class)
    model = cost_function_cls.from_mallet(options.model_fname, feature_extractor_cls=GGGFeatures, guiMode=False)
    if options.test_set_fname != None:
        test_set = cPickle.load(open(options.test_set_fname))
    else:
        test_set = None

    runId = options.run_id
    multi_esdcs = eval(options.esdc_multi)
    use_merging = eval(options.use_merging)
    debug("use_merging: %s" % use_merging)
    force_sync = eval(options.force_sync)
    resolver_type = options.resolver_type


    # qa_corpus_fname_1 = "%s/tools/forklift/dataAnnotation/data/dialog_ambiguous_RSS_12/forklift_ambiguous_larger_corpus_all_questions.yaml" % SLU_HOME
    qa_corpus_fname_1 = options.qa_corpus_fname_1
    qa_corpus_fname_2 = options.qa_corpus_fname_2
    qa_corpora = []
    if qa_corpus_fname_1:
        qa_corpora.append(annotationIo.load(qa_corpus_fname_1))


    # qa_corpus_fname_2 = "%s/tools/forklift/dataAnnotation/data/dialog_ambiguous_RSS_12/forklift_ambiguous_larger_corpus_all_questions_set000.yaml" % SLU_HOME
    if qa_corpus_fname_2:
        qa_corpus_2 = annotationIo.load(qa_corpus_fname_2)
        qa_corpora.append(qa_corpus_2)


    if resolver_type == "bag_of_words":
        from coreference.bag_of_words_resolver import BagOfWordsResolver
        resolver = BagOfWordsResolver("%s/tools/coreference/models/coref_1.5.pck" % SLU_HOME)
    elif resolver_type == "oracle":
        from coreference.oracle_resolver import OracleResolver
        resolver = OracleResolver(options.corpus_fname)
    else:
        resolver = None

    state_cls = state_type_from_name(options.state_type)
    corpus = annotationIo.load_all(options.corpus_fname)
    ########### UGLY HACK ##############
    # The corpus file is always a command set, so we set its ESDC sources to be
    # "command" in every case. This is necessary, because our commands_AAAI_11
    # datasets don't have their sources set at all.
    for annotation in corpus:
        for esdc in annotation.flattenedEsdcs:
            annotation.setSource(esdc, 'command')
    extractor_func = extractor_utils.make_extractor_func(options.esdc_extractor,
                                                         options.esdc_extractor_model)
    info("num questions: %d" % options.num_questions)
    info("num answers: %d" % options.num_answers)
    evaluateDataSet(model, corpus, test_set, extractor_func,
                    state_cls, options.entropy_metric,
                    useRrt=options.use_rrt, runId=runId,
                    multi_esdcs=multi_esdcs, use_merging=use_merging,
                    resolver=resolver, qa_corpora = qa_corpora,
                    num_questions=options.num_questions,
                    num_answers=options.num_answers,
                    force_sync=force_sync,
                    question_type=options.question_type,
                    random_seed=options.random_seed)


if __name__=="__main__":
    main()

