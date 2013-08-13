from corpusMturk import readCorpus
import collections
import numpy as na
from esdc_chunker import pos_tagger
from pos_histograms import pos_histograms
def main():
    corpus = readCorpus.Corpus("../mturk_data_collector/data/corpusCommandsForVideoSmallFilesOnly/")

    annotators = set()
    scenarios = set()
    commands = []
    words = []

    commands_per_scenario = collections.defaultdict(lambda : 0)
    discourses = []
    current_scenario = None
    for annotation in corpus.assignments:
        scenario = annotation.scenario

        if current_scenario != scenario:
            current_scenario = scenario
            print "scenario", scenario.name

        if scenario.platform == "forklift" and scenario.isSimulated and len(annotation.command) <= 150:
            scenarios.add(scenario)
            annotators.add(annotation.workerId)
            words.extend(annotation.command.split())
            discourses.append(annotation.command)
            #print "*", annotation.command, scenario.youtubeUrl
            commands.append(annotation.command)
            print annotation.command
            commands_per_scenario[scenario.name] += 1
        
    print len(annotators), "annotators"
    print len(scenarios), "videos"
    print len(commands), "commands"
    print len(words), "words"
    print len(set(words)), "unique words"
    posTagger = pos_tagger.makeTagger()
    pos_histograms(discourses, posTagger)
    for scenario in sorted(scenarios):
        print scenario, commands_per_scenario[scenario.name]

    for word in ["put", "take", "bring", "go", "move", "to", "on", "across", "the", "cymbal"]:
        print word + ":",
        print len([w for w in words if w.lower() == word])


    mean_commands_per_scenario = na.mean(commands_per_scenario.values())
    print "mean commands", mean_commands_per_scenario
              
if __name__ == "__main__":
    main()
