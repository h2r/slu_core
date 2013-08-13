import unittest

from esdcs.extractor import malletTrainer

class TestCase(unittest.TestCase):
    def testOverlaps(self):
        trainer = malletTrainer.Trainer()
        self.assertTrue(trainer != None)
        
