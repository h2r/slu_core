from numpy import transpose as tp
from esdcs.dataStructures import ExtendedSdc
from esdcs.esdcIo.annotationIo import Annotation
from esdcs import esdcIo
from esdcs.groundings import PhysicalObject, Prism
from g3.cost_functions.cost_function_crf import CostFnCrf
from g3.graph import GGG
from standoff import TextStandoff
from optparse import OptionParser
import cPickle
import random
from g3.annotation_to_ggg import annotation_to_ggg_map
from tokenizer import IndexedTokenizer

def make_esdc_candidate(esdc_structure, esdc_field_to_texts):
    field_map = {}
    entire_text = ""
    for field in ExtendedSdc.fieldNames:
        if not esdc_structure.childIsEmpty(field):
            text = random.choice(esdc_field_to_texts[field])
            entire_text += text + " "
            start = len(entire_text) - len(text) - 1
            end = start + len(text)
            field_map[field] = (start, end)
    field_standoffs = dict((f, [[entire_text.__getslice__(*r), r]])
                           for f, r in field_map.iteritems())
    tokenizer = IndexedTokenizer()
    for field, standoffs in field_standoffs.iteritems():
        results = []
        for text, range_tuple in standoffs:
            start = range_tuple[0]
            indexes, tokens = tokenizer.tokenize(text)


            for idx, word in zip(indexes, tokens):
                range_tuple = [start + idx , start + idx + len(word)]
                results.append([word, range_tuple])
        field_standoffs[field] = results
            
    esdc_candidate = esdcIo.fromYaml(entire_text, 
                                     {esdc_structure.type: field_standoffs})
    return esdc_candidate

def annotation_candidate(esdc_structure, esdc_field_to_texts, groundings,
                              test_grounding):
    esdc_candidate = make_esdc_candidate(esdc_structure,
                                         esdc_field_to_texts)
    annotation = Annotation("test", esdc_candidate)

    esdc_candidate = esdc_candidate[0]
    annotation.setGrounding(esdc_candidate, test_grounding)
    for field in ExtendedSdc.fieldNames:
        if not esdc_candidate.childIsEmpty(field):
            child = esdc_candidate.children(field)[0]
            while True:
                grounding = random.choice(groundings)
                if  not isinstance(grounding, PhysicalObject):
                    continue
                else:
                    break
            annotation.setGrounding(child, grounding)
    if isinstance(test_grounding, PhysicalObject):
        annotation.agent = test_grounding
    else:
        annotation.agent = PhysicalObject(Prism(tp([(0, 0), (1, 0), (1, 1), (0, 1)]), 0, 1), 
                                          tags=["agent"], path=test_grounding)

    return annotation, esdc_candidate

class Describer:
    def __init__(self, training_ds, cf):
        self.training_ds = training_ds
        self.cf = cf
        
        t = ""
        self.esdc_structures = [ExtendedSdc(esdcType="PATH", entireText=t,
                                            r=[TextStandoff(t, (0, 0))],
                                            l=[ExtendedSdc(esdcType="OBJECT", f=[TextStandoff(t, (0, 0))])]),
                                #ExtendedSdc(esdcType="EVENT", entireText=t,
                                #            r=[TextStandoff(t, (0, 0))],
                                #            l=[TextStandoff(t, (0, 0))],
                                #            l2=[TextStandoff(t, (0, 0))])
                                ]

        self.esdc_field_to_texts = {}

        groundings = set([])
        for ex in self.training_ds.observations:
            for sdc in ex.sdcs:
                for field in ExtendedSdc.fieldNames:
                    self.esdc_field_to_texts.setdefault(field, [])
                    text = sdc.childText(field)
                    if text != "":
                        self.esdc_field_to_texts[field].append(text)
            if len(groundings) < 10:
                for glist in ex.annotation.groundings:
                    groundings.update(glist)
                
        self.groundings = list(groundings)            

    def describe(self, thing_to_describe):
        results = []
        for esdc_structure in self.esdc_structures:
            for i in range(0, 500):
                annotation, esdc_candidate = annotation_candidate(esdc_structure, 
                                                                  self.esdc_field_to_texts,
                                                                  self.groundings, 
                                                                  thing_to_describe)
                state, esdc_to_ggg = annotation_to_ggg_map(annotation)
                ggg = esdc_to_ggg[esdc_candidate]
                new_evidences = ggg.evidences
                for phi in ggg.nodes_with_name("phi"):
                    new_evidences = new_evidences.set_evidence(phi.id, True)
                ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
                cost, entries = self.cf.costEntry(ggg.factors, state, ggg)
                #cost, entries = self.cf.costEntry([factor], state, ggg)
                results.append((cost, annotation))



        results.sort()
        return results


def main():
    parser = OptionParser()
    
    parser.add_option("--model",dest="model_fname", 
                      help="CRF Filename", metavar="FILE")

    parser.add_option("--training",dest="training_fname")
    parser.add_option("--testing",dest="testing_fname")

  
    (options, args) = parser.parse_args()
    cf = CostFnCrf.from_mallet(options.model_fname)
    
    training = cPickle.load(open(options.training_fname))
    testing = cPickle.load(open(options.testing_fname))


    describer = Describer(training, cf)

    for ex in testing.observations:
        if not ex.sdcs[0].type == "PATH":
            continue

        path_esdc = ex.sdcs[0]
        test_grounding = ex.annotation.getGroundings(path_esdc)[0]
        results = describer.describe(test_grounding)
        cost, annotation = results[0]
        print "initial", path_esdc
        print "description", annotation.esdcs[0]
if __name__ == "__main__":
    main()
