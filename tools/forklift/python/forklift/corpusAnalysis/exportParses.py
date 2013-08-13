from corpusMturk import readCorpus
from esdcs.extractor.stanfordParserExtractor import Extractor
from esdcs.esdcIo import toYaml, annotationIo
from esdcs.esdcIo.annotationIo import Annotation, Corpus, load, save
from optparse import OptionParser
import yaml
import os

def main():
    parser = OptionParser()
    parser.add_option("--source_corpus", dest="source_corpus",
                      help="The file or directory to read from")
    parser.add_option("--dest_corpus", dest="dest_corpus",
                      help="The yaml file to which data will be written")
    (options, args) = parser.parse_args()

    corpus = readCorpus.Corpus(options.source_corpus)
    extractor = Extractor()
    #oldCorpus = annotationIo.load("%s/dataAnnotation/data/forkliftMturkEsdcs.stefie10.groundings.withPaths.yaml" % os.environ['FORKLIFT_HOME'])
    #oldAssignmentIds = set(a.assignmentId for a in oldCorpus)
    #print len(oldAssignmentIds), "old ids"
    yamlData =[]
    print len(corpus.assignments), "assignments"
    filteredAnnotations = [x for x in corpus.assignments
                           if (x.scenario.platform == "forklift" and
                               x.scenario.isSimulated == True)]
    print len(filteredAnnotations), "filtered annotations"
    output_annotations = []
    for i, a in enumerate(filteredAnnotations):
        esdcs = extractor.extractEsdcs(a.command)
        assignmentId = a.assignmentId
        agent = a.agent
        context = a.context
        esdcSource = [assignmentId for esdc in esdcs.flattenedEsdcs]
        output_annotations.append(Annotation(assignmentId = assignmentId,
                                    esdcs = esdcs,
                                    objectGroundings = None,
                                    groundingIsCorrect = None,
                                    agent = agent,
                                    context = context,
                                    esdcSource = esdcSource))
        esdcYaml = toYaml(esdcs)
        print "******"
        print a, esdcYaml
        print esdcs
        
        yamlData.append({"command":esdcYaml,
                         "assignmentId":a.assignmentId})

    print "dumped", i, "commands."
    yaml.dump(yamlData, open(options.dest_corpus, "w"))
    

if __name__ == "__main__":
    main()
