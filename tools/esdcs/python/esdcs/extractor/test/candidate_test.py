import unittest
from esdcs import candidates as esdcCandidates
from esdcs.dataStructures import ExtendedSdcGroup, TextStandoff, ExtendedSdc

class TestCase(unittest.TestCase):

    def testCandidate(self):
        cmd = "turn and move to the truck on the right"
        esdcg = ExtendedSdcGroup([ExtendedSdc('EVENT', r=[TextStandoff(cmd, (0, 4))],l2=[],l=[ExtendedSdc('PATH', r=[TextStandoff(cmd, (14, 16))],l2=[],l=[ExtendedSdc('OBJECT', r=[TextStandoff(cmd, (27, 29))],l2=[],l=[TextStandoff(cmd, (30, 33)), TextStandoff(cmd, (34, 39))],f=[TextStandoff(cmd, (17, 20)), TextStandoff(cmd, (21, 26))])],f=[])],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[], entireText=cmd)]), ExtendedSdc('EVENT', r=[TextStandoff(cmd, (9, 13))],l2=[],l=[],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[], entireText=cmd)])], cmd)
        

        candidates = esdcCandidates.makeCandidatesForEsdcGroup(esdcg)
        self.assertEqual(len(candidates), 5)
        
        
