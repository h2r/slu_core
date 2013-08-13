from glob import glob
import yaml
from os.path import basename
import os.path
from itertools import chain

def readProperties(corpus_directory):
    """
    Read all the properties.yaml files from the corpus and yield them.
    Adds in the directory name to the properties files.
    """
        
    for properties_fname in glob("%s/*/properties.yaml" % corpus_directory):
        properties = yaml.load(open(properties_fname))
        properties["directory"] = corpus_directory
        yield properties


class Assignment:
    def __init__(self, scenario, **assignmentMap):
        self.__dict__.update(assignmentMap)
        self.scenario = scenario

        assert "assignmentId" in self.__dict__
        assert "command" in self.__dict__
        assert "hitId" in self.__dict__
        assert "youtubeId" in self.__dict__
        assert "workerId" in self.__dict__

        assert self.scenario.youtubeId == self.youtubeId


class Evaluation:
    def __init__(self, scenario, **evaluationMap):
        self.__dict__.update(evaluationMap)
        self.scenario = scenario

        assert "assignmentId" in self.__dict__
        assert "hitId" in self.__dict__
        assert "workerId" in self.__dict__
        assert "commandYoutubeId" in self.__dict__
        assert "displayedYoutubeId" in self.__dict__
        assert "command" in self.__dict__
        assert "similarityScore" in self.__dict__

        assert self.scenario.youtubeId == self.commandYoutubeId 
        
        
class Scenario:
    """
    One scenario from the corpus.
    """
    def __init__(self, directory):
        properties = yaml.load(open("%s/properties.yaml" % directory))
        try:
            self.directory = directory
            self.objects_fname = "%s/objects.xml" % directory
            self.platform = properties['platform']
            self.youtubeId = properties['youtubeId']

            self.youtubeUrl = "http://www.youtube.com/watch?v=%s" % self.youtubeId
            self.isSimulated = properties['isSimulated']
            self.lcmlog = "%s/lcmlog" % directory
            

            
            self.name = basename(directory)
            self.assignmentFname = "%s/assignments.yaml" % directory
            self.evaluationFname = "%s/evaluations.yaml" % directory

            self.loadAssignments()
            self.loadEvaluations()
        except:
            print directory
            raise
    def loadAssignments(self):
        self.assignments = []
        if not os.path.exists(self.assignmentFname):
            return


        assignmentsYaml = yaml.load(open(self.assignmentFname))
        for assignmentMap in assignmentsYaml:
            self.assignments.append(Assignment(self, **assignmentMap))
    def loadEvaluations(self):
        self.evaluations = []
        if not os.path.exists(self.evaluationFname):
            return

        if os.path.getsize(self.evaluationFname) == 0:
            return

        evaluationsYaml = yaml.load(open(self.evaluationFname))
        for evaluationMap in evaluationsYaml:
            self.evaluations.append(Evaluation(self, **evaluationMap))
                
        
            
                        
class Corpus:
    def __init__(self, directory):
        self.directory = directory
        if not os.path.exists(directory):
            raise ValueError("Directory doesn't exist: " + str(directory))
        self.readScenarios()
        
    def readScenarios(self):
        scenarios = []
        assignments = []
        evaluations = []
        youtubeIdToScenario = {}
        assignment_ids = set()
        for scenarioDir in chain(glob("%s/*" % self.directory),
                                 glob("%s/*/*" % self.directory)):
            if basename(scenarioDir) != "in_progress":
                if os.path.exists("%s/properties.yaml" % scenarioDir):
                    scenario = Scenario(scenarioDir)
                    scenarios.append(scenario)
                    assert scenario.youtubeId not in youtubeIdToScenario
                    youtubeIdToScenario[scenario.youtubeId] = scenario
                    assignments.extend(scenario.assignments)
                    evaluations.extend(scenario.evaluations)
                    for a in scenario.assignments:
                        if a.assignmentId in assignment_ids:
                            print "a", a.assignmentId
                            print "command", a.command
                            print scenario.youtubeId
                            print scenario.directory
                            print "****** already saw it!"
                            raise ValueError("Already saw this annotation")
                        else:
                            assignment_ids.add(a.assignmentId)
        self.scenarios = sorted(scenarios, key=lambda s: s.name)

        self.assignments = sorted(assignments, key=lambda a: a.scenario.name)
 #       print self.assignments
        self.assignmentIdToAssignment = dict([(a.assignmentId, a)
                                              for a in self.assignments])
        
        assert len(self.assignmentIdToAssignment) == len(self.assignments)

        self.evaluations = sorted(evaluations, key=lambda e: e.scenario.name)
        self.assignmentIdToEvaluation = dict([(e.assignmentId, e)
                                              for e in self.evaluations])
        assert len(self.assignmentIdToEvaluation) == len(self.evaluations)

        self.youtubeIdToScenario = youtubeIdToScenario

    def assignmentForId(self, assignmentId):
        return self.assignmentIdToAssignment[assignmentId]

    def scenarioForYoutubeId(self, youtubeId):
        return self.youtubeIdToScenario[youtubeId]

    def evaluationForAssignmentId(self, assignmentId):
        return self.assignmentIdToEvaluation[assignmentId]
