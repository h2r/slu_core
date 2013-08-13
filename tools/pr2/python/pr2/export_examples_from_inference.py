from esdcs.esdcIo import annotationIo
import spatial_features_cxx as sf
import pool_27
from multiprocessing import cpu_count
from g3.cost_functions.cost_function_crf import CostFnCrf
from g3.esdcs_to_ggg import gggs_from_esdc_group
from g3.inference import nodeSearch
from pr2.pr2_state import Pr2State
from os.path import dirname, basename


taskPlanner = None

def export_annotation_free_places(args):
    state_cls, a, desc = args
    state_cls, a, desc = args
    global taskPlanner
    print "doing", desc
    aid_count = 0
    new_corpus = []
    
    for place_esdc in [e for e in a.esdcs.flattenedEsdcs if e.type == "PLACE"]:
        new_context = a.context.withoutPaths()
        start_state = state_cls.from_context(new_context)
        if not place_esdc.childIsEsdcs("l"):
            continue
        landmark_esdc = place_esdc.children("l")[0]
        print "doing", place_esdc
        for pobj in [o for o in start_state.objects if "block" in o.tags]:

            for i in range(0, 5):
                aid = "%s_%d" % (a.id, aid_count + 1000)
                aid_count += 1
                new_annotation = annotationIo.Annotation(aid, a.esdcs, 
                                                         agent=new_context.agent,
                                                         context=new_context)

                new_annotation.fname = "%s/free_place_examples_%s" % (dirname(a.fname), basename(a.fname))
                
                #new_annotation.setGrounding(place_esdc, place)
                new_annotation.setGrounding(landmark_esdc, pobj)
                    
                new_corpus.append(new_annotation)

    return new_corpus

def export_annotation_places(args):
    state_cls, a, desc = args
    state_cls, a, desc = args
    global taskPlanner
    print "doing", desc
    aid_count = 0
    new_corpus = []
    
    for place_esdc in [e for e in a.esdcs.flattenedEsdcs if e.type == "PLACE"]:
        new_context = a.context.withoutPaths()
        start_state = state_cls.from_context(new_context)
        if not place_esdc.childIsEsdcs("l"):
            continue
        landmark_esdc = place_esdc.children("l")[0]
        print "doing", place_esdc
        for pobj in [o for o in start_state.objects if "block" in o.tags]:
            for place in start_state.places:

                
                if sf.math2d_dist(pobj.centroid2d, place.centroid2d) < 3:
                    aid = "%s_%d" % (a.id, aid_count)
                    aid_count += 1
                    new_annotation = annotationIo.Annotation(aid, a.esdcs, 
                                                             agent=new_context.agent,
                                                             context=new_context)

                    new_annotation.fname = "%s/place_examples_%s" % (dirname(a.fname), basename(a.fname))

                    new_annotation.setGrounding(place_esdc, place)
                    new_annotation.setGrounding(landmark_esdc, pobj)
                    
                    new_corpus.append(new_annotation)

    return new_corpus


def export_annotation_events(args):
    state_cls, a, desc = args
    global taskPlanner
    print "doing", desc
    aid_count = 0
    new_corpus = []
    for esdc in a.esdcs:
        start_state = state_cls.from_context(a.context.withoutPaths())
        gggs = gggs_from_esdc_group([esdc])
        plans = taskPlanner.find_plan(
            start_state,
            gggs,
            beam_width=10,
            beam_width_sequence=1,
            search_depth_event=2,
            beam_width_event=5,
            save_state_tree=True)
        plans_to_include = []
        
        longer_plans = []
        for cost, state, ggg in plans:
            state_sequence = taskPlanner.state_sequence(state)
            if len(state_sequence) == 1:
                plans_to_include.append((cost, state, ggg))
            else:
                if state_sequence[-1][0].name != "noop" and state_sequence[0][0].name != "noop":
                    longer_plans.append((cost, state, ggg))
        plans_to_include = plans_to_include[0:10]
        for cost, state, ggg in longer_plans[0:5]:
            plans_to_include.append((cost, state, ggg))

        for j, (cost, state, ggg) in enumerate(plans_to_include):
            new_context = state.to_context()
            #print cost

            aid = "%s_%d" % (a.id, aid_count)
            aid_count += 1
            new_annotation = annotationIo.Annotation(aid, a.esdcs, 
                                                     agent=new_context.agent,
                                                     context=new_context)

            for node in ggg.gamma_nodes:
                groundings = ggg.evidence_for_node(node)
                esdc = ggg.node_to_top_esdc(node)
                new_annotation.setGroundings(esdc, groundings)


            new_annotation.fname = "%s/inference_examples_%s" % (dirname(a.fname), basename(a.fname))
            new_corpus.append(new_annotation)
    return new_corpus

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--corpus-fname",dest="corpus_fnames", 
                      help="CRF Filename", metavar="FILE", action="append")
    parser.add_option("--model-filename", dest="model_fname")
    (options, args) = parser.parse_args()

    state_cls = Pr2State
    corpus = annotationIo.load_all(options.corpus_fnames)
    global taskPlanner
    taskPlanner = nodeSearch.BeamSearch(CostFnCrf.from_mallet(options.model_fname))

    args = []
    for i, annotation in enumerate(corpus):
        #if not i in (0, 1, 132,):
        #    continue
        desc = "%d of %d %s" % (i, len(corpus), annotation.entireText)
        args.append((state_cls, annotation, desc))

    pool = pool_27.Pool(processes=max(cpu_count(), 4), maxtasksperchild=1)
    #result = pool.map(export_annotation_places, args)
    result = pool.map(export_annotation_free_places, args)
    
    new_corpus = []
    for r in result:
        new_corpus.extend(r)
    
    annotationIo.save_separate_files(new_corpus)
if __name__== "__main__":
    main()

