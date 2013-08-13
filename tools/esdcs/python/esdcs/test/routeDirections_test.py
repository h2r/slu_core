import unittest
import os



class TestCase(unittest.TestCase):
    

    def testConverter(self):
        try:
            from routeDirectionCorpusReader import readSession
            import routeDirections
        except ImportError:
            print "skipping because no route directions module"
            return
        fname = (os.environ["SLU_HOME"] +
                 "/nlp/data/Direction understanding subjects Floor 1 (Final).ods")
        
        sessions = readSession(fname, "stefie10-d1-hierarchical")
        for session in sessions:
            for instructionIdx, instruction in enumerate(session.routeInstructions):
                print instruction
                sdcs = session.routeAnnotations[instructionIdx]
                esdcs = routeDirections.fromRouteDirectionSdc(sdcs)
                for esdc in esdcs:
                    print esdc


