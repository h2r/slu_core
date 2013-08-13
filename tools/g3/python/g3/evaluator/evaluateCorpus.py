import cPickle
import yaml
import collections
import math
import os
import shelve
import sys

from environ_vars import SLU_HOME
from esdcs.dataStructures import ExtendedSdcGroup
from esdcs.esdcIo import annotationIo
from esdcs.extractor import extractor_utils
from g3.cost_functions.cost_function_utils import make_cost_function_class
from g3.esdcs_to_ggg import gggs_from_esdc_group, ggg_from_esdc
from g3.evaluator import evaluationResult
from g3.inference import nodeSearch 
from g3.state import state_type_from_name
from heapq import nsmallest
from os.path import dirname

class ResultsFile:
    def __init__(self, results_dir):
        results_fname = "%s/evaluationResults.shelf" % results_dir
        if not os.path.isfile(results_fname):
            raise ValueError("Must exist and be a file: " + `results_fname`)

        result_shelf = shelve.open(results_fname, protocol=2, flag='r')

        self.esdcs_to_results = collections.defaultdict(lambda : list())
 
        self.results = []
        for annotationId, (results, annotation) in result_shelf.iteritems():
            for ggg, result_list in results:
                self.results.append((ggg, result_list))
                 
        print "loaded", len(self.results)
    def __len__(self):
        return len(self.results)

def evaluateDataSet(model, corpus,  dataset, esdc_extractor_func, state_cls,
                    useRrt = True, runId=-1, 
                    runMultiEsdcCommands=False, use_merging=False):
    
    if runId == -1:
        runId = 1
        while True:
            if os.path.isdir('dataEvaluation/data/evaluation-run-%d' % runId):
                runId += 1
            else:
                break

    print runId

    dirToUse = 'dataEvaluation/data/evaluation-run-%d' % runId
    if not os.path.exists(dirToUse):
        os.makedirs(dirToUse)

    ce = CorpusEvaluator(model, dirToUse, esdc_extractor_func, useRrt, use_merging)

    if dataset != None:
        testIds = set()
        for cobs in dataset.observations:
            testIds.add(cobs.annotation.assignmentId)
    else:
        testIds = None

    print "testIds is", testIds

    resultsFname = '%s/evaluationResults.shelf' % dirToUse
    modelFname = '%s/model.pck' % dirToUse
    print "loading", resultsFname
    resultsDir = dirname(resultsFname)
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)
    results = shelve.open(resultsFname, protocol=2, flag='c')
    print "num assignments", len(corpus)

    try:
        cnt = 0
        done_cnt = 0
        for i, annotation in enumerate(corpus):
            print "doing annotation", i
            path = dirToUse + '/' + annotation.assignmentId + '/'
#            path = dirToUse + '/' + assignmentId + '/'
            print "path is", path
            if os.path.exists(path):
                cnt += 1
                continue

            if testIds != None and not annotation.assignmentId in testIds:
                continue


            cnt += 1


            result = (ce.evaluateAnnotation(annotation,
                                            state_cls,
                                            dirToUse,
                                            numToReturn=20, 
                                            runMultiEsdcCommands=runMultiEsdcCommands), 
                      annotation)

            print "result is:", result
            print "results are:",  [x.__class__ for x in result[0]]
#            tempfile = open(resultsFname, 'w')
#            pickle.dump(result, tempfile)
#            tempfile.close()

            results[annotation.assignmentId]= result
#            results[assignmentId]= result

            done_cnt += 1
            
            print "saving", resultsFname, modelFname
            results.sync()
#            if i > 3:
#                break
            if done_cnt > 5:
                raise ValueError("Exit preemptively because of memory leak.")

    except Exception as e:
        import traceback
        traceback.print_tb( sys.exc_info()[2])
        print e
        print "cnt", cnt
        print "command", annotation.entireText
        raise
    finally:
        print "saving", resultsFname, modelFname
        results.close()

def countNumTestInCorpus(corpus, dataset):
    testIds = set()
    for cobs in dataset.observations:
         testIds.add(cobs.annotation.assignmentId)

    count = 0
    for i, annotation in enumerate(corpus):
        if annotation.assignmentId in testIds:
            count += 1

    print count


class CorpusEvaluator:

    def __init__(self, model, directory, esdc_extractor_func, useRrt=True,
                 use_merging=False):

        self.esdc_extractor_func = esdc_extractor_func
        
        self.directory = directory

        self.model = model

        self.taskPlanner = nodeSearch.BeamSearch(self.model, useRrt)
#        self.taskPlanner = esdcSearch.BeamSearch(self.model, useRrt)

        #parameters
        parameter_fname = "%s/parameters.yaml" % self.directory
        if os.path.exists(parameter_fname):
            with open(parameter_fname, "r") as f:
                parameter_map = yaml.load(f)
        else:
            parameter_map = {
                "beam_width":10,
                "beam_width_sequence":20,
                "search_depth_event":4,
                "beam_width_event":2,
                }
            with open(parameter_fname, "w") as f:
                yaml.dump(parameter_map, f)


        self.beam_width = parameter_map["beam_width"]
        self.beam_width_sequence = parameter_map["beam_width_sequence"]
        self.search_depth_event = parameter_map["search_depth_event"]  
        self.beam_width_event = parameter_map["beam_width_event"]

        self.depth = parameter_map["search_depth_event"]

        self.use_merging = use_merging

    def evaluateAnnotation(self, annotation, state_cls, dirToUse, numToReturn=None, 
                           runMultiEsdcCommands=False):
        print 'annotation has', len(annotation.esdcs), 'esdcs'
        esdcs = self.esdc_extractor_func(annotation)
        entries = []
        if runMultiEsdcCommands:
            print "multiesdcs"
            print 'finding plan for', (' ').join([esdc.text for esdc in esdcs])
            if self.use_merging:
                from coreference.merge_coreferences import merge_coreferences
                from coreference.bag_of_words_resolver import BagOfWordsResolver
#                resolver = BagOfWordsResolver("%s/tools/coreference/models/coref_1.5.pck" % SLU_HOME)
                from coreference.oracle_resolver import OracleResolver
#                resolver = OracleResolver("%s/tools/forklift/dataAnnotation/data/forklift_ambiguous_revised_context_with_answers.prthaker.yaml" % SLU_HOME)
                resolver = OracleResolver("%s/tools/forklift/dataAnnotation/data/forklift_ambiguous_larger_corpus_with_answers.yaml" % SLU_HOME)
                gggs = merge_coreferences(esdcs, resolver)
            else:
                gggs = gggs_from_esdc_group(esdcs)
            start_state, plans = self.getSearchResults(annotation, state_cls,  gggs, 
                                                       numToReturn=numToReturn)
            esdcNum = 0
            entries.append((gggs, self.writeResults(dirToUse, annotation, esdcs, esdcNum, 
                                             start_state, gggs, plans)))
        else:
            print "not multiesdcs"
            if self.use_merging:
#                from coreference.bag_of_words_resolver import BagOfWordsResolver
                from coreference.merge_coreferences import merge_coreferences
                from coreference.oracle_resolver import OracleResolver
#                resolver = OracleResolver("%s/tools/forklift/dataAnnotation/data/forklift_ambiguous_revised_context_with_answers.prthaker.yaml" % SLU_HOME)
                resolver = OracleResolver("%s/tools/forklift/dataAnnotation/data/forklift_ambiguous_larger_corpus_with_answers.yaml" % SLU_HOME)
#                resolver = BagOfWordsResolver("%s/tools/coreference/models/coref_1.5.pck" % SLU_HOME)
                gggs = merge_coreferences(esdcs, resolver)
            else:
                gggs = []
                for esdc in esdcs:
                    gggs.append(ggg_from_esdc(esdc))
            for esdcNum, ggg in enumerate(gggs):
                esdcGroup = ExtendedSdcGroup([esdcs[esdcNum]])
                gggs = [ggg]
                start_state, plans = self.getSearchResults(annotation, state_cls, [ggg], 
                                                           numToReturn)
                entries.append((gggs, self.writeResults(dirToUse, annotation, esdcGroup, esdcNum, 
                                                       start_state, gggs, plans)))
        
        return entries

    def getSearchResults(self, annotation, state_cls,  gggs, numToReturn=None):
#        from forklift.forkState import ForkState
#        startState = ForkState.init_state()
        startState = state_cls.from_context(annotation.context)
        plans = self.taskPlanner.find_plan(startState, gggs,
                                           beam_width=self.beam_width,
                                           beam_width_sequence=self.beam_width_sequence,
                                           search_depth_event=self.search_depth_event,
                                           beam_width_event=self.beam_width_event)
        if numToReturn != None:
            plans = nsmallest(numToReturn, plans)
        for plan in plans:
            print plan
        return startState, plans
      
    def writeResults(self, dirToUse, annotation, esdcs, esdcNum, start_state, start_gggs, plans): 
        aId = annotation.assignmentId
#        aId = annotation.assignmentId.split('_')[0]
        path = dirToUse #should be coming from evaluateDataSet and should match the directories for modelFname and resultsFname
        path = path + '/' + aId + '/'   #create directory for annotation id
        if not os.path.exists(path):
            os.makedirs(path)
        
        entries = []
        assert len(plans), plans
        
        passed = 10 #predicted endpoint can be 10m away from actual endpoint in annotation
        numPassed = 0
        
        for i, planTuple in enumerate(plans):
            (cost, active_set_i), end_state, end_ggg = planTuple
            
            actualEnd = annotation.agent.path.locationAtT(-1)
            resultEnd = end_state.getPosition()

            dist = math.hypot((actualEnd[0]-resultEnd[0]), (actualEnd[1]-resultEnd[1]))
            if dist <= passed:
                numPassed += 1

            yamlFname = path + 'summary_%s_%d_%d.yaml' % (aId, esdcNum, i)
            yamlData = {}
            yamlData['platform'] = 'navigation'
            yamlData['command'] = (' ').join([esdc.text for esdc in esdcs])
            yamlData['entireText'] = annotation.entireText
            yamlData['objectsFname'] = ''
            yamlData['assignmentId'] = aId
            yamlData['planCost'] = float(cost)
            yamlData['endDist'] = float(dist)

            try:
                print "saving", yamlFname
                yaml.dump(yamlData, open(yamlFname, 'w'))
                print "done"
                
            except Exception as e:
                import traceback
                traceback.print_tb( sys.exc_info()[2])
                print e
                print 'error saving',yamlFname
                
            print "number of plans with endpoint within", passed, "away from actual endpoint:", numPassed

            er = evaluationResult.EvaluationResult(annotation, esdcs, esdcNum, start_state, start_gggs, 
                                                   end_state, end_ggg, cost, float(dist))

            entries.append(er)
        return entries

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--cost-function-class", dest="cost_function_class")
    parser.add_option("--model", dest="model_fname")
    parser.add_option("--dataset", dest="dataset_fname", default=None)
    parser.add_option("--corpus-fname", dest="corpus_fnames")
    parser.add_option("--runid", dest="run_id", type="int", default=-1)
    parser.add_option("--userrt", dest="use_rrt", action="store_true", default=False)
    parser.add_option("--esdcmulti", dest="esdc_multi", type="string", default="False")
    parser.add_option("--state-type",dest="state_type",
                      help="State or Agent Type", metavar="FILE")


    parser.add_option("--esdc-extractor", type="string", dest="esdc_extractor")
    parser.add_option("--esdc-extractor-model", type="string",
                      dest="esdc_extractor_model")
    parser.add_option("-m", "--merging", dest="use_merging",
                      help="Use merging?", metavar="FILE")

    (options, args) = parser.parse_args()

    cost_function_cls = make_cost_function_class(options.cost_function_class)
    model = cost_function_cls(options.model_fname)
    if options.dataset_fname != None:
        dataset = cPickle.load(open(options.dataset_fname))
    else:
        dataset = None

    runId = options.run_id
    multiEsdcs = eval(options.esdc_multi)
    use_merging = eval(options.use_merging)
    
    #########semantic map for d8##########
#    smap = CarmenSemanticMap("%s/data/directions/direction_floor_8_full/direction_floor_8_full.cmf.gz" % SLU_HOME,
#                             "%s/data/directions/direction_floor_8_full/tags/df8_full_tags.tag" % SLU_HOME,
#                             "%s/data/directions/direction_floor_8_full/partitions/d8_full_part.pck" % SLU_HOME)
    #state_cls = state_type_from_name("forklift")
    state_cls = state_type_from_name(options.state_type)

    corpus = annotationIo.load(options.corpus_fnames)
    print "corpus is", corpus

    extractor_func = extractor_utils.make_extractor_func(options.esdc_extractor,
                                                         options.esdc_extractor_model)
    print "func", extractor_func
    print "multi", multiEsdcs
    evaluateDataSet(model, corpus, dataset, extractor_func, state_cls,
                    useRrt=options.use_rrt, runId=runId, 
                    runMultiEsdcCommands=multiEsdcs, use_merging=use_merging)


if __name__=="__main__":
    main()

 








