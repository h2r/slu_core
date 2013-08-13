import unittest
from esdcs.extractor.stanfordParserExtractor import Extractor
#from maximumEntropyRerankingExtractor import Extractor
from esdcs.esdcIo import toYaml

class TestCase(unittest.TestCase):
    def ain(self, esdc_groups, correct_yaml):
        current_metadata = None
        parse_i = 0
        lst = [toYaml(esdcs)[1] for esdcs in esdc_groups]
        

        for i, l in enumerate(lst):
            esdc = esdc_groups[i]
            if esdc.metadata != current_metadata:
                print "****************************** dependency", parse_i, 

                current_metadata = esdc.metadata
                print current_metadata[0]
                parse_i += 1

            if correct_yaml == l:
                print "correct"
            else:
                print "incorrect"

            print l
        if not correct_yaml in lst:
            self.fail("Correct esdc not in results.")
    



    def __init__(self, *args, **margs):
        unittest.TestCase.__init__(self, *args, **margs)
        self.aeq = self.assertEqual

    @classmethod
    def setUpClass(cls):
        cls.extractor = Extractor()
        
    def testPickUp(self):
        
        esdcs = self.extractor.extractEsdcs("Pick up the tire pallet.")

        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f':[{'OBJECT':{}}],
                            'r':['Pick', 'up'],
                            'l':[{'OBJECT':{'f':['the', 'tire', 'pallet']}}]}}])


        
    def testPickUpAndPut(self):
        
        esdcs = self.extractor.extractEsdcs("Pick up the tire pallet and " + 
                                            "take it to the truck.")
        print esdcs[0]
        print esdcs[1]
        print cmp(esdcs[0], esdcs[1])
        print cmp(esdcs[1], esdcs[0])
        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'r': ['Pick', 'up'], 
                             'l': [{'OBJECT': 
                                    {'f': ['the', 'tire', 'pallet']}}], 
                             'f': [{'OBJECT': {}}]}},
                 {'EVENT': {'r': ['take'], 
                            'l2': [{'PATH': 
                                    {'r': ['to'], 
                                     'l': [{'OBJECT': 
                                            {'f': ['the', 'truck']}}]}}], 
                            'l': [{'OBJECT': {'f': ['it']}}], 
                            'f': [{'OBJECT': {}}]}}])



    def testPlace(self):
        
        esdcs = self.extractor.extractEsdcs("Place the tire pallet on the truck.")

        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT':
                   {'r': ['Place'],
                    'l2': [{'PLACE': {'r': ['on'],
                                      'l': [{'OBJECT':
                                             {'f': ['the', 'truck']}}]}}],
                    'l': [{'OBJECT': {'f': ['the', 'tire', 'pallet']}}],
                    'f': [{'OBJECT': {}}]}}])


        

        esdcs = self.extractor.extractEsdcs("place the tire pallet on the truck.")

        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT':
                   {'r': ['place'],
                    'l2': [{'PLACE': {'r': ['on'],
                                      'l': [{'OBJECT':
                                             {'f': ['the', 'truck']}}]}}],
                    'l': [{'OBJECT': {'f': ['the', 'tire', 'pallet']}}],
                    'f': [{'OBJECT': {}}]}}])


        

        



        
    def testLift(self):
        
        esdcGroups = self.extractor.extractTopNEsdcs("Lift the tire pallet.", 10)

        for esdcGroup in esdcGroups:
            print "*********", esdcGroup.score
            for esdc in esdcGroup:
                print esdc
            
        

    def testIndexError(self):
        esdcs = self.extractor.extractEsdcsFromSentence("""Move the package pallet to the row to the right.""")

        self.assertTrue(esdcs != None)




    def testDivideByZero(self):

        esdcs = self.extractor.extractEsdcsFromSentence("""lower forklift. 
        Bring pallet of tires forward. Slide over forks. Lift pallet.""")

        self.assertTrue(esdcs != None)

        
    def testPickUpCokeCan(self):

        esdcs = self.extractor.extractEsdcsFromSentence("""Pick up the Coke can""")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'Pick up',
                             'l': 'the Coke can'}}])
        



        


    def testOrdering(self):

        esdcs = self.extractor.extractEsdcs("""Come out of the parking lot and turn left. You''ll come to Titus Avenue. Take
    a right, and then a quick left onto Hudson. Wegmans will be on the right.""")
        print esdcs.__class__
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'Come', 
                             'l': {'PATH': {'r': 'out of', 
                                            'l': 'the parking lot'}}}}, 
                  {'EVENT': {'r': 'turn left'}}, 
                  {'EVENT': {'r': [['You', [43, 46]], 
                                   ['come', [51, 55]]], 
                             'l': {'PATH': {'r': [['to', [56, 58]]], 
                                            'l': 'Titus Avenue'}}, 
                             'f': [['ll', [48, 50]]]}}, 
                  {'EVENT': {'r': 'Take', 
                             'l2': {'PATH': {'r': 'onto', 'l': 'Hudson'}}, 
                             'l': [['a', [78, 79]], ['right', [80, 85]], 
                                   ['then', [91, 95]]]}}, 
                  {'EVENT': {'r': [['a', [78, 79]], ['right', [80, 85]], 
                                   ['then', [91, 95]]]}}, 
                  {'EVENT': {'r': 'a quick left'}}, 
                  {'EVENT': {'r': 'will be', 
                             'l': {'PLACE': {'r': [['on', [138, 140]]], 
                                             'l': 'the right'}}, 
                             'f': 'Wegmans'}}])


    def testCrash(self):

        esdcs = self.extractor.extractEsdcs("""The trailer is to your right, and in at the end of the row of pallets.""")
        
        self.aeq(toYaml(esdcs)[1], 
                 [{'EVENT': {'r': 'is', 
                             'l2': {'PLACE': {'r': 'in', 'l': 'your right'}}, 
                             'l': {'PATH': {'r': 'to', 'l': 'your right'}}, 
                             'f': 'The trailer'}}, 
                  {'PLACE': {'r': 'at', 
                             'l': {'OBJECT': {'r': [['of', [48, 50]]], 
                                              'l2': 'pallets', 
                                              'l': 'the row', 
                                              'f': 'the end'}}}}])
        
 
    def testGoLeft(self):

        command = "go left"
        
        esdc_group = self.extractor.extractEsdcs(command)
        self.aeq(toYaml(esdc_group)[1],
                 [{'EVENT': {'r': 'go left'}}])


