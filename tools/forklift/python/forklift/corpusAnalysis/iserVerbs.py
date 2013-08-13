from corpusMturk import readCorpus

def main():
    corpus = readCorpus.Corpus("dataCollection/data/corpusCommandsForVideoSmallFilesOnly/")

    iserVerbs = ["meet", "bring", "avoid", "follow"]
    for annotation in corpus.annotations:
        scenario = annotation.scenario
        for verb in iserVerbs:
            if verb in annotation.command:
                print verb, scenario.youtubeId, scenario.name,
                print annotation.command
                
if __name__ == "__main__":
    main()
