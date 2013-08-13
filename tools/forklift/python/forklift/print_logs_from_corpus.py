from corpusMturk import readCorpus

def main():
    corpus = readCorpus.Corpus("dataCollection/data/corpusCommandsForVideoSmallFilesOnly/")
    
    filtered_annotations = [x for x in corpus.assignments
                           if (x.scenario.platform == "forklift" and
                               x.scenario.isSimulated == True)]

    assignments = set(a.scenario for a in filtered_annotations)
    for a in assignments:
        print "/".join(a.lcmlog.split("/")[-2:])

if __name__ == "__main__":
    main()
    
