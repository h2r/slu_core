from esdcs.esdcIo import annotationIo
from corpusMturk import readCorpus

def main():
    import sys
    fname = sys.argv[1]
    assignments = readCorpus.Corpus("dataCollection/data/corpusCommandsForVideoSmallFilesOnly/")
    corpus = annotationIo.load(fname)

    word_cnt = 0
    workers = set()
    scenarios = set()
    
    for annotation in corpus:

        assignment = assignments.assignmentForId(annotation.assignmentId)
        word_cnt += len(annotation.entireText.split())
        workers.add(assignment.workerId)
        scenarios.add(assignment.scenario)
        if assignment.scenario.name == "put_tire_pallet_on_loaded_truck":
            print "command", assignment.scenario.name, annotation.entireText

    print len(scenarios), "scenarios"
    print len(workers), "annotators"
    print word_cnt, "words"
    print len(corpus), "commands"
        


if __name__ == "__main__":
    main()
