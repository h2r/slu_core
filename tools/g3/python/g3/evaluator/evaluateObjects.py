from esdcs.esdcIo import annotationIo
from g3.cost_functions.cost_function_utils import make_cost_function_class
import time
from multiprocessing import cpu_count
import pool_27
from g3.esdcs_to_ggg import ggg_from_esdc
from g3.state import state_type_from_name
from g3.inference.entropy_metrics import make_node_to_object_ids
from confusion_matrix import ConfusionMatrix
from dcrf3 import dataset

import math
import random
import numpy as na
import pickle_util
evaluator = None

def evaluate(*args, **margs):
    global evaluator
    print "********** calling", args
    result = evaluator.evaluate(*args, **margs)
    print "********** finished", args
    return result

def evaluate_ggg(ggg, grounding, start_state, taskPlanner):
    assert len(ggg.esdcs) == 1
    esdc = ggg.esdcs[0]
    query_node = ggg.node_for_esdc(esdc)
    ggg.set_evidence_for_node(query_node, [grounding])  
    plans = taskPlanner.find_plan(start_state, [ggg],
                                  beam_width=50)
    
    end_gggs = [end_ggg for cost, start_state, end_ggg in plans]
    probabilities = [math.exp(-cost) for (cost, idx), start_state, end_ggg in plans]
    #print
    #print "esdc", str(esdc), grounding.tags
    for (cost, idx), start_state, end_ggg in plans:
        #print "plan: prob", math.exp(-cost)
        for f in end_ggg.factors:
            esdc = end_ggg.factor_to_esdc(f)
            #print str(esdc), math.exp(-end_ggg.cost_for_factor(f))
        #print
    node_to_object_ids = make_node_to_object_ids(end_gggs)
    candidates = []
    for node in ggg.gamma_nodes:
        if node != query_node:
            candidates.append(len(node_to_object_ids[node]))
    K = 1.0 / na.prod(candidates)
    K = K / (math.pow(0.5, len(probabilities) - 1))
    sum_of_candidates = na.sum(probabilities)
    prob = K * sum_of_candidates
    #print "result", str(esdc), grounding.tags, prob, sum_of_candidates, K
    return prob


def evaluate_objects(model, corpus_fname, state_type):
    corpus = annotationIo.load(corpus_fname)
    state_cls = state_type_from_name(state_type)
    from g3.inference import nodeSearch 
    taskPlanner = nodeSearch.BeamSearch(model)
    predictions = []
    done = False
    phrases = set()
    for i, annotation in enumerate(corpus):
        start_state = state_cls.from_context(annotation.context)

        for esdc in annotation.esdcs:
            #if esdc.text != "the pallet of boxes":
            #    continue
            #if esdc.text in phrases:
            #    continue
            isCorrect = annotation.isGroundingCorrect(esdc)
            if isCorrect != None:
                ggg = ggg_from_esdc(esdc)
                groundings = annotation.getGroundings(esdc)
                assert len(groundings) == 1
                grounding = groundings[0]
                #if "generator" not in grounding.tags:
                #    continue
                prob = evaluate_ggg(ggg, grounding, start_state, taskPlanner)
                if prob > 0.7:
                    predicted_class = True
                else:
                    predicted_class = False
                predictions.append((predicted_class, isCorrect))
                #print "Query: Is object", " ".join(grounding.tags),
                #print "'" + esdc.text + "'?"
                #print "System: ", 
                #if predicted_class:
                #    print "Yes."
                #else:
                #    print "No."
                #done = True
                phrases.add(esdc.text)
            if done:
                break
        if done:
            break

    
    tp = len([(p, l) for  p, l in predictions if p and p == l])
    fp = len([(p, l) for  p, l in predictions if p and p != l])
    tn = len([(p, l) for  p, l in predictions if not p and p == l])
    fn = len([(p, l) for  p, l in predictions if not p and p != l])
    cm = ConfusionMatrix(tp, fp, tn, fn)
    #cm.print_all()

    #if len(phrases) > 20:
    #    phrases = random.sample(phrases, 20)
    #for phrase in sorted(phrases):
    #    print phrase
    return cm

class Evaluator:
    def __init__(self, old_model_fname, cost_function_class_name, training_set, 
                 corpus_fname, state_type, num_samples=2):
        self.cost_function_class_name = cost_function_class_name
        self.training_set = training_set
        self.old_model_fname = old_model_fname
        self.corpus_fname = corpus_fname
        self.state_type = state_type
        self.num_samples = num_samples
        
    def evaluate(self, fraction):
        cms = []
        from dcrf3.train_lccrf import train_lccrf
        cost_function_cls = make_cost_function_class(self.cost_function_class_name)
        old_model = cost_function_cls(self.old_model_fname, guiMode=False)
        num_examples = int(fraction * len(self.training_set.observations))
        for sample in range(self.num_samples):
            newds = dataset.DiscreteDataset(random.sample(self.training_set.observations, 
                                                          num_examples),
                                            self.training_set.discretization_factor,
                                            f_min_max = self.training_set.f_min_max)
            
            new_fname = train_lccrf(newds, 
                                    "crf_discrete_forklift_subsampled_%d.pck" % num_examples, 
                                    sigma=old_model.lccrf.sigma)
            newcf = cost_function_cls(new_fname, guiMode=False)
            cm = evaluate_objects(newcf, self.corpus_fname, self.state_type)
            print "training fraction: ", fraction, "sample", sample, "of", 
            print self.num_samples
            cm.print_all()
            cms.append(cm)
        return num_examples, cms

def main():
    """
    Evaluates object groundings for the NIST/BOLT evaluation.  Takes a
    special input file annotated with correctness for noun phrases in
    the test corpus.
    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--cost-function-class", dest="cost_function_class")
    parser.add_option("--model", dest="model_fname")
    parser.add_option("--training_fname", dest="training_fname")
    parser.add_option("--corpus-fname", dest="corpus_fname")
    parser.add_option("--state-type",dest="state_type")

    (options, args) = parser.parse_args()
    print "training", options.training_fname
    training_set = pickle_util.load(options.training_fname)

    print "Training on", len(training_set.observations), "examples"


    global evaluator
    evaluator = Evaluator(options.model_fname, options.cost_function_class, 
                          training_set,
                          options.corpus_fname, options.state_type)
    results = []

    args = []
    for i in range(1, 100, 10):
        fraction = float(i)/100
        args.append((fraction, ))

    pool = pool_27.Pool(processes=2, maxtasksperchild=1)

    def callback(result):
        num_examples, cms = result
        print "***** finished results", num_examples
        results.append((num_examples, cms))

    #args = args[2:3]
    for arg in args:
        print "apply"
        pool.apply_async(evaluate, arg, callback=callback)    
        #pool.apply_sync(evaluate, arg, callback=callback)    

    while len(results) <  len(args):
        time.sleep(1)

    print "closing"
    pool.close()
    print "joining"
    pool.join()            

    fname = "confusion_matrices.pck"            
    print "saving", fname
    pickle_util.save(fname, results)

if __name__=="__main__":
    main()
