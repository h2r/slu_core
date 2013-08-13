from esdcs.extractor import stanfordParserExtractor
from esdcs.extractor import lccrfRerankingExtractor
#from esdcs import routeDirections
import numpy as na
import  esdcs.evaluation as esdc_eval
import pylab as mpl
from optparse import OptionParser
import collections

def evaluateCorpus(corpus, extractors):

    extractorToScores = collections.defaultdict(list)

    for i, (command, goldEsdcs) in enumerate(corpus):
        print command
        for extractor in extractors:
            esdcs = extractor.extractTopNEsdcs(command,  n=20)
            #esdcs = self.extractor.extractTopNEsdcs("turn and move to the truck on the right", n=5)            
            #score = esdc_eval.editDistance(esdcs, goldEsdcs)
            scores = [esdc_eval.fractionOfMatches(e, goldEsdcs) for e in esdcs]
            #score = max(scores)
            score = scores[0]
            print extractor, "score", score, "best possible", max(scores)

            extractorToScores[extractor].append(score)

            extractorToScores[(extractor, "best")].append(max(scores))

        
    return extractorToScores
def graphScores(extractors, corpus):
    extractorToScores = evaluateCorpus(corpus, [e for l, e in extractors])
    loc = 1
    xticks = [0.5]
    xlabels = [""]
    for name, extractor in extractors:
        score = na.mean(extractorToScores[extractor])

        mpl.bar(loc, score, 0.4)
        xticks.append(loc)
        xlabels.append(name)
        loc += 1
        print name, score,
        best = na.mean(extractorToScores[(extractor, "best")])
        print "(best", best, ")"
    mpl.xticks(na.array(xticks) + 0.25, xlabels)
    mpl.yticks(na.arange(0, 1.1, 0.1))


def evaluateForkliftCorpus(esdc_model_fname, corpus_fname):
    import cPickle
    #from esdcs.esdcIo import annotationIo
    #annotations = annotationIo.load("dataAnnotation/data/forkliftMturkEsdcs.stefie10.groundings.yaml")
    dataset = cPickle.load(open(corpus_fname))
    annotations = [o.annotation for o in dataset.observations]

    used_assignment_ids = set()
    unique_annotations = []
    for a in annotations:
        if not a.assignmentId in used_assignment_ids:
            unique_annotations.append(a)
            used_assignment_ids.add(a.assignmentId)
    annotations = unique_annotations
    annotations = annotations[0:10]
    
    
    
    corpus = [(annotation.entireText, annotation.esdcs)
              for annotation in annotations]

    extractors = [#("SDCs", routeDirections.FlatEsdcExtractor()),
                  ("ESDCs", stanfordParserExtractor.Extractor()),
                  ("LCCRF", lccrfRerankingExtractor.Extractor(esdc_model_fname)),
#                  ("Reranking Classifier", maximumEntropyRerankingExtractor.ClassifierExtractor()),
#                  ("Reranking", maximumEntropyRerankingExtractor.RerankingExtractor()),
                  ]
    
    graphScores(extractors, corpus)
    mpl.title("ESDC Extractor vs. SDC Extractor \n" +
              "for commands from the Forklift Mechanical Turk Corpus")
    mpl.savefig("esdcs.forkliftCommands.png")


        

def evaluateRouteInstructionCorpus(annotationName, title):
    from routeDirectionCorpusReader import readSession

    from environ_vars import SLU_HOME
    fname = "%s/nlp/data/Direction understanding subjects Floor 1 (Final).ods" %  SLU_HOME
    
    sessions = readSession(fname, annotationName)


    i = 0
    corpus = []
    for session in sessions:
        for instructionIdx, instruction in enumerate(session.routeInstructions):
            sdcs = session.routeAnnotations[instructionIdx]
            annotatedEsdcs = routeDirections.fromRouteDirectionSdc(sdcs)
            corpus.append((instruction, annotatedEsdcs))
            i += 1


    extractors = [("SDCs", routeDirections.FlatEsdcExtractor()),
                  ("ESDCs", stanfordParserExtractor.Extractor())]

    graphScores(extractors, corpus)
    mpl.title(title)
    mpl.savefig("esdcs.routeInstructions.%s.png" % annotationName)

    
    
def main():

    # mpl.figure()
    # evaluateRouteInstructionCorpus('stefie10-d1-hierarchical',
    #                                "ESDC Extractor vs. SDC Extractor \n" +
    #                                "for commands from the Route Instruction " +
    #                                "Corpus, Hierarchical Annotations")

    # mpl.figure()
    # evaluateRouteInstructionCorpus('stefie10',
    #                                "ESDC Extractor vs. SDC Extractor \n" +
    #                                "for commands from the Route Instruction " +
    #                                "Corpus, Flat Annotations")

    parser = OptionParser()

    parser.add_option("-m","--model-filename",dest="model_fname", 
                      help="ESDC Model Filename", metavar="FILE")
    parser.add_option("-c","--corpus-filename",dest="corpus_fname", 
                      help="ESDC Model Filename", metavar="FILE")    
    (options, args) = parser.parse_args()    
    mpl.figure()
    evaluateForkliftCorpus(options.model_fname, options.corpus_fname)    
    #mpl.show()

    
if __name__ == "__main__":
    main()
