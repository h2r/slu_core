import unittest
from esdcs.esdcIo import yamlReader, yamlWriter
class TestCase(unittest.TestCase):
    def __init__(self, *args, **margs):
        unittest.TestCase.__init__(self, *args, **margs)
        
        self.aeq = self.assertEqual


        
    def testAnnotationsFile(self):

        
        annotations = yamlReader.load("data/forklift_open_ended.yaml")

        self.aeq(annotations[0].esdcs[0].asPrettyMap(),
                 {"EVENT": {'r': ['stop'],
                            'f': [{'OBJECT': {'f':['Forklift']}}]}})

        self.aeq(annotations[1].esdcs[0].asPrettyMap(),
                 {"PATH": {'r': ['to'],
                           'l': [{'OBJECT':{'f':['the',  'truck']}}]}})

        self.aeq(annotations[3].esdcs[0].asPrettyMap(),
                 {'EVENT': {'r': ['Go'],
                            'l': [{'PATH':
                                   {'r': ['past'],
                                    'l': [{'OBJECT': {'r': ['by'],
                                                      'l': [{'OBJECT': {'f': ['the', 'stairs']}}],
                                                      'f': [{'OBJECT': {'f': ['the', 'truck']}}]}}]}}],
                            'f': [{'OBJECT': {}}]}})

        
        self.aeq(annotations[4].esdcs[0].asPrettyMap(),
                 {'EVENT':
                  {'f': [{'OBJECT': {}}],
                   'r': ['Pick', 'up'],
                   'l': [{'OBJECT': {'f': ['the', 'tire', 'pallet']}}]}})
                 

        self.aeq(annotations[4].esdcs[1].asPrettyMap(),
                 {'EVENT':
                  {'f': [{'OBJECT': {}}],
                   'r': ['put'],
                   'l2': [{'PLACE':
                           {'r': ['on'],
                            'l': [{'OBJECT': {'f': ['the', 'truck']}}]}}],
                   'l': [{'OBJECT': {'f': ['it']}}]}})

        
        self.aeq(annotations[5].esdcs[0].asPrettyMap(),
                 {'EVENT': {'r': ['Go'],
                            'l': [{'PATH': {'r': ['past'],
                                            'l': [{'OBJECT': {'r': ['past'],
                                                              'l': [{'OBJECT': {'f': ['the', 'stairs']}}],
                                                              'f': [{'OBJECT': {'f': ['the', 'truck']}}]}}]}}],
                            'f': [{'OBJECT': {}}]}})
        

        self.aeq(annotations[8].esdcs.entireText, "Go left.")
        self.aeq(annotations[8].esdcs.esdcs, [])

        self.assertTrue(annotations[9].esdcs.entireText.startswith("Orient yourself"))
        self.aeq(annotations[9].esdcs.esdcs[6].text, "turn  left")
        
        entireText, yamlData = yamlWriter.toYaml(annotations[9].esdcs)
        esdcGroup = yamlReader.fromYaml(entireText, yamlData)
        
        self.aeq(esdcGroup.esdcs[6].text, "turn  left")
        
        self.aeq(esdcGroup.esdcs[6].text, "turn  left")


        self.aeq(annotations[10].esdcs.entireText, "Pick the tire pallet up.")
        self.aeq(len(annotations[10].esdcs), 3)
        
