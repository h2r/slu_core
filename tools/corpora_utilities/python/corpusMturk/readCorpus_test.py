import os.path

import unittest
import readCorpus

class TestCase(unittest.TestCase):
    def setUp(self):
        self.corpus = readCorpus.Corpus("data/corpusCommandsForVideo")
    def testForklift(self):
        forkliftScenarios = [s for s in self.corpus.scenarios
                             if s.platform == "forklift"]
        self.assertEqual(forkliftScenarios[0].name, "go_to_receiving")
        for s in forkliftScenarios:
            print s.name
            self.assertEqual(s.rndfFname,
                             os.environ["FORKLIFT_HOME"] + "/" +
                             "dataCollection/etc/agile/Lee_RNDF_demo.txt")
            self.assertTrue(os.path.exists(s.rndfFname))
            
    def testLoad(self):


        self.assertEqual(self.corpus.scenarios[0].name, "follow_around_room")

        for scenario in self.corpus.scenarios:
            if scenario.platform != "wheelchair":
                self.assertTrue(os.path.exists(scenario.lcmlog),
                                scenario.lcmlog)
            if scenario.name.startswith("real"):
                self.assertFalse(scenario.isSimulated)
            for annotation in scenario.assignments:
                annotation.command


    def testAssignmentForId(self):
        assignment = self.corpus.assignmentForId("1K49UT2XYPYGLAE65THO4GNIQB6M44")
        self.assertEqual(assignment.command,
                         'Load the forklift onto the trailer.')
        
        assignment = self.corpus.assignmentForId("1DGUDLED3GI2QXAGT6BO8L92BJ410U")
        self.assertEqual(assignment.command,
                         "go left")
        assignment = self.corpus.assignmentForId("1IBH2UV96D1T6PIUZKAEPREV8CNUIQ")
        self.assertEqual(assignment.command,
                         "Move to the right side of the trailer of the " +
                         "trailer on the right and wait.")

        assignment = self.corpus.assignmentForId("1DGUDLED3GI2QXAGT6BO8L92BJ410U")
        self.assertEqual(assignment.command,
                         "go left")
