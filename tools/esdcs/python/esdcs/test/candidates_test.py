import unittest
from esdcs.extractor.stanfordParserExtractor import Extractor
from esdcs.esdcIo import fromYaml
#from maximumEntropyRerankingExtractor import Extractor
import yaml
from esdcs import candidates
class TestCase(unittest.TestCase):

    def testCandidates(self):
        esdcGroup = fromYaml("the pallets on the right of you",
                             yaml.load("""
        - OBJECT:
            f: the pallets
            r: 'on'
            l:
              OBJECT:
                f: the right
                r: of
                l: you
        """))
        esdc = esdcGroup[0]
        candidate_esdcs = candidates.makeCandidatesForEsdc(esdc)

        print "candidates"
        for cesdc in candidate_esdcs:
            print cesdc
            
        self.assertTrue(esdc in candidate_esdcs)
        self.assertEqual(len(candidate_esdcs), 2)
        


    def testCandidateGroup(self):
        esdcGroup = fromYaml("the pallets on the right of you",
                             yaml.load("""
        - OBJECT:
            f: the pallets
            r: 'on'
            l:
              OBJECT:
                f: the right
                r: of
                l: you
        """))

        candidate_esdc_groups = candidates.makeCandidatesForEsdcGroup(esdcGroup)
        for esdc_group in candidate_esdc_groups:
            self.assertEqual(len(esdc_group), 1)

        self.assertEqual(len(candidate_esdc_groups), 2)
        
