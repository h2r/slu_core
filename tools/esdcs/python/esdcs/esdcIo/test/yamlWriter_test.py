import unittest
from esdcs.esdcIo import yamlReader
import esdcs.esdcIo as esdcIo

class TestCase(unittest.TestCase):
    def __init__(self, *args, **margs):
        unittest.TestCase.__init__(self, *args, **margs)
        self.aeq = self.assertEqual


        
    def testAnnotationsWriter(self):

        
        annotations = yamlReader.load("data/forklift_open_ended.yaml")
        print annotations
        print annotations[0]
        entireText, yamlData = esdcIo.toYaml(annotations[0].esdcs)
        self.assertEqual(entireText, "Forklift stop.")
        self.assertEqual(yamlData, [{'EVENT': {'r': 'stop', 'f': 'Forklift'}}])

        entireText, yamlData = esdcIo.toYaml(annotations[1].esdcs)
        self.assertEqual(entireText, "to the truck")
        self.assertEqual(yamlData, [{'PATH': {'r': 'to', 'l': 'the truck'}}])

        entireText, yamlData = esdcIo.toYaml(annotations[2].esdcs)
        self.assertEqual(entireText, "Go between the truck and the pallet.")
        self.assertEqual(yamlData, [{'EVENT': {'r': 'Go',
                                              'l': {'PATH':{'r':'between',
                                                            'l': [{'OBJECT':{'f':'the truck'}},
                                                                  {'OBJECT':{'f':'the pallet'}}]}}}}])
        
        
        for annotatedSentence in annotations:
            entireText, yamlData = esdcIo.toYaml(annotatedSentence.esdcs)
            try:
                rereadAnnotations = esdcIo.fromYaml(entireText, yamlData)
                self.assertEqual(rereadAnnotations, annotatedSentence.esdcs)
            except:
                print "starting esdcs", [e.asPrettyMap() for e in annotatedSentence.esdcs]
                print "text", entireText
                print "data", yamlData
                raise

    def testNestedRepeatedStrings(self):
        from esdcs.dataStructures import ExtendedSdc, ExtendedSdcGroup
        from standoff import TextStandoff
        txt = "Move to the right side of the trailer of the trailer on the right and wait."

        esdcs = [ExtendedSdc('EVENT', r=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (0, 4))],l2=[],l=[ExtendedSdc('PATH', r=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (5, 7))],l2=[],l=[ExtendedSdc('OBJECT', r=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (23, 25))],l2=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (41, 44)), TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (45, 52))])],l=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (26, 29)), TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (30, 37))])],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (8, 11)), TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (12, 17)), TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (18, 22))])])],f=[])],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[], entireText='Move to the right side of the trailer of the trailer on the right and wait.')]), ExtendedSdc('OBJECT', r=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (53, 55))],l2=[],l=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (56, 59)), TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (60, 65))])],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (41, 44)), TextStandoff("Move to the right side of the trailer of the trailer on the right and wait.", (45, 52))])])]

        entireText, yamlData = esdcIo.toYaml(ExtendedSdcGroup(esdcs))
        rereadAnnotations = esdcIo.fromYaml(entireText, yamlData)
        try:
            self.assertEqual(list(rereadAnnotations), esdcs)
        except:
            print "start with", [e.asPrettyMap() for e in esdcs]
            print "ended with", [e.asPrettyMap() for e in rereadAnnotations]
            raise
        
