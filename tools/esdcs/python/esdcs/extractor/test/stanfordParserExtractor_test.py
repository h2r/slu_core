import unittest
from esdcs.extractor.stanfordParserExtractor import Extractor
from esdcs.esdcIo import toYaml

class TestCase(unittest.TestCase):
    def ain(self, esdc_groups, correct_yaml):
        current_metadata = None
        parse_i = 0
        lst = [toYaml(esdcs)[1] for esdcs in esdc_groups]
        
        if not correct_yaml in lst:
            for i, l in enumerate(lst):
                esdc = esdc_groups[i]
                if esdc.metadata != current_metadata:
                    print "****************************** dependency", parse_i
                    
                    current_metadata = esdc.metadata
                    print current_metadata[0]
                    parse_i += 1
                    print l
                    
            self.fail("Correct esdc not in results.")
    

    def __init__(self, *args, **margs):
        unittest.TestCase.__init__(self, *args, **margs)
        self.aeq = self.assertEqual

    @classmethod
    def setUpClass(cls):
        cls.extractor = Extractor()
        cls.extractor.parser.verbose = True
        
    def testPickUp(self):
        
        esdcs = self.extractor.extractEsdcs("Pick up the tire pallet.")

        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f':[{'OBJECT':{}}],
                            'r':['Pick', 'up'],
                            'l':[{'OBJECT':{'f':['the', 'tire', 'pallet']}}]}}])

    def testPickUpNearTruck(self):       
    
        esdcs = self.extractor.extractEsdcs("Pick up the tire pallet near the truck.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'Pick up',
                             'l': {'OBJECT': {'r': 'near',
                                              'l': 'the truck',
                                              'f': 'the tire pallet'}}}}])
                 

    def testGoToReceiving(self):               

        esdcs = self.extractor.extractEsdcs("Go to receiving.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f':[{'OBJECT':{}}],
                            'r':['Go'],
                            'l':[{"PATH":
                                  {'r':['to'],
                                   'l':[{'OBJECT':{'f':['receiving']}}]}}]}}])


    def testGoPast(self):               
        esdcs = self.extractor.extractEsdcs("Go past the tire pallet.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":
                   {'f':[{'OBJECT':{}}],
                    'r':['Go'],
                    'l':[{"PATH":{'r':['past'],
                                  'l':[{'OBJECT':
                                        {'f':['the', 'tire', 'pallet']}}]}}]}}])


    def testGoTowards(self):               
        esdcs = self.extractor.extractEsdcs("Go towards the tire pallet.")
        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT':
                   {'f':[{'OBJECT':{}}],
                    'r':['Go'],
                    'l':[{'PATH':
                          {'r':['towards'],
                           'l':[{'OBJECT':{'f':['the', 'tire', 'pallet']}}]}}]
                    }}])

    def testGoToward(self):               
        esdcs = self.extractor.extractEsdcs("Go toward the tire pallet.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":
                   {'f':[{'OBJECT':{}}],
                    'r':['Go'],
                    'l':[{'PATH':
                          {'r':['toward'],
                           'l':[{'OBJECT':
                                 {'f':['the', 'tire', 'pallet']}}]}}]}}])
        

    def testWalkToward(self):               
        esdcs = self.extractor.extractEsdcs("Walk toward the tire pallet.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{
                     'f':[{'OBJECT':{}}],
                     'r':['Walk'],
                     'l':[{"PATH":{'r':['toward'],
                                   'l':[{"OBJECT": {'f':['the', 'tire', 'pallet']}}]}}]}}])
        
        

    def testPut(self):               
        esdcs = self.extractor.extractEsdcs("Put the tire pallet on the truck.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":
                   {'f':[{'OBJECT':{}}],
                    'r':['Put'],
                    'l':[{'OBJECT':{'f':['the', 'tire', 'pallet']}}],
                    'l2':[{"PLACE":
                           {'r':['on'],
                            'l':[{'OBJECT':{'f':['the', 'truck']}}]}}]}}])
        
        

        
    def testForkliftPut(self):
        esdcs = self.extractor.extractEsdcs("Forklift, put the tire pallet on the truck.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'put',
                             'l2': {'PLACE': {'r': 'on', 'l': 'the truck'}},
                             'l': 'the tire pallet',
                             'f': 'Forklift'}}])            

        
    def testRobotPut(self):
        esdcs = self.extractor.extractEsdcs("Robot, put the tire pallet on the truck.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'put',
                             'l2': {'PLACE': {'r': 'on', 'l': 'the truck'}},
                             'l': 'the tire pallet',
                             'f': 'Robot'}}])            


    def testBotPut(self):
        esdcs = self.extractor.extractEsdcs("'Bot, put the tire pallet on the truck.")
        # should have bot, but parser is misanalyzing "Bot" as partmod.
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'put',
                             'l2': {'PLACE': {'r': 'on', 'l': 'the truck'}},
                             'l': 'the tire pallet', 'f': 'Bot'}}])

    def testMoveTo(self):               
        esdcs = self.extractor.extractEsdcs("Move the battery pallet to receiving.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f':[{'OBJECT':{}}],
                            'r':['Move'],
                            'l':[{'OBJECT':{'f':['the', 'battery', 'pallet']}}],
                            'l2':[{"PATH":
                                   {'r':['to'],
                                    'l':[{'OBJECT':{'f':['receiving']}}]}}]}}])
        
        

        
        

    def testMoveInto(self):               
        esdcs = self.extractor.extractEsdcs("Move the battary pallet into receiving.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f':[{'OBJECT':{}}],
                            'r':['Move'],
                            'l':[{'OBJECT':{'f':['the', 'battary', 'pallet']}}],
                            'l2':[{"PATH":
                                   {'r':['into'],
                                    'l':[{'OBJECT':{'f':['receiving']}}]}}]}}])
        
        

        
        

    def testPickupNextToTruck(self):               
        esdcs = self.extractor.extractEsdcs("Pick up the tire pallet next to the truck.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'Pick up',
                             'l': {'OBJECT': {'f': 'the tire pallet',
                                              'r': 'next to',
                                              'l': 'the truck'}}}}])
    
        
    def testGetTirePallet(self):               
        esdcs = self.extractor.extractEsdcs("Get the tire pallet.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f':[{'OBJECT':{}}],
                            'r':['Get'],
                            'l':[{'OBJECT':{'f':['the', 'tire', 'pallet']}}]}}])

        
        

    def testPickTirePalletUp(self):
        # parsed wrong
        esdcs = self.extractor.extractTopNEsdcs("Pick the tire pallet up.",
                                                n=20)
        self.ain(esdcs,
                 [{'EVENT': {'r': [['Pick', [0, 4]], ['up', [21, 23]]],
                             'l': 'the tire pallet'}}])



    def testStop(self):
        esdcs = self.extractor.extractEsdcs("Forklift, stop.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'stop', 'f': 'Forklift'}}])



    def testStop1(self):
        esdcs = self.extractor.extractEsdcs("Stop.")
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":{'f': [{'OBJECT': {}}], 'r':['Stop.']}}])
        
        



        
    def testDown(self):
        esdcs = self.extractor.extractTopNEsdcs("Drive down the hall.",
                                                n=5)
        self.ain(esdcs,
                 [{'EVENT': {'r': 'Drive',
                             'l': {'PATH': {'r': 'down', 'l': 'the hall'}}}}])



    def testAcross(self):
        esdcs = self.extractor.extractEsdcs("Drive across the kitchen.")
        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'r': ['Drive'],
                             'l': [{'PATH': {'r': ['across'],
                                             'l': [{'OBJECT': {'f': ['the', 'kitchen']}}]}}], 'f': [{'OBJECT': {}}]}}])

        

    def destDownToKitchen(self):
        esdcs = self.extractor.extractEsdcs("Drive down the hall to the kitchen.")
        self.aeq(toYaml(esdcs)[1],
                 [{'r':['Drive'], 'l':[{'r':['down'], 'l':['the', 'hall']}]}])
        

    def destRouteInstruction2(self):
        esdcs = self.extractor.extractEsdcs("Drive past the kitchen to the elevators.")
        self.aeq(toYaml(esdcs)[1],
                 [{"EVENT":
                   {'f':[{'OBJECT':{}}],
                    'r':['Drive'],
                    'l':[{"PATH":{'r':['past'],
                                  'l':[{"OBJECT":{'f':['the', 'kitchen']}}]}}],
                    'l2':[{"PATH":
                           {'r':['to'],
                            'l':[{"OBJECT":{'f':['the', 'elevators']}}]}}]}}])

    def destRouteInstruction3(self):
        """
        Not quite right, but usable.
        """
        esdcs = self.extractor.extractEsdcs("Drive all the way to the end of the hall.")
        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'f': [{'OBJECT': {}}],
                             'r': ['Drive'],
                             'l': [{'OBJECT': {'f': ['all', 'the', 'way']}}],
                             'l2': [{'PATH': {'r': ['to'],
                                            'l': [{'OBJECT': {'r': ['of'],
                                                              'l': [{'OBJECT': {'f': ['the', 'hall']}}],
                                                              'f': ['the', 'end']}}]}}],
                             }}])

    def destRouteInstruction4(self):
        esdcs = self.extractor.extractEsdcs("Walk around the hall to the elevators.")

        
        self.aeq(esdcs.asPrettyMap(),
                 [{"EVENT":
                   {'f':[{'OBJECT':{}}],
                    'r':['Walk'],
                    'l':[{"PATH":
                          {'r':['around'],
                           'l':[{"OBJECT":{"f":['the', 'hall']}}]}}],
                    'l2':[{"PATH":
                           {'r':['to'],
                            'l':[{"OBJECT":{"f":['the', 'elevators']}}]}}]}}])



    def testRouteInstruction5(self):
        esdcs = self.extractor.extractEsdcs("Forklift, stop.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT': {'r': 'stop', 'f': 'Forklift'}}])



    def testRouteInstruction6(self):
        esdcs = self.extractor.extractEsdcs("Forklift, go to receiving.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT':
                   {'f': 'Forklift',
                    'r': 'go',
                    'l': {'PATH': {'r': 'to', 'l': 'receiving'}},
                    }}])

    def testPickUpInReceiving(self):
        esdcs = self.extractor.extractTopNEsdcs("Pick up the tire pallet in " +
                                                "receiving", n=5)

        self.ain(esdcs, 
                 [{'EVENT': {'r': 'Pick up',
                             'l': {'OBJECT': {'f': 'the tire pallet',
                                              'r': [['in', [24, 26]]],
                                              'l': 'receiving',
                                              }}}}])
    def testPickUpAndPut(self):
        esdcs = self.extractor.extractTopNEsdcs("Pick up the tire pallet in " +
                                                "receiving and put it on the truck.", n=2)
        self.aeq(toYaml(esdcs[1])[1],
                 [{'EVENT': {'r': 'Pick up',
                             'l': {'OBJECT': {'f': 'the tire pallet',
                                              'r': [['in', [24, 26]]],
                                              'l': 'receiving',}}}},
                  {'EVENT': {'r': 'put',
                             'l': 'it',
                             'l2': {'PLACE': {'r': 'on', 'l': 'the truck'}},
                             }}])


    def destCorpusString1(self):
        
        esdcs = self.extractor.extractEsdcs("Back up, spin around and " +
                                            "face the box pallet on the ground in between the tire pallets.")

        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'f': [{'OBJECT': {}}],
                             'r': ['face'],
                             'l': [{'OBJECT': {'f': ['the', 'box', 'pallet'],
                                               'r': ['on'],
                                               'l': [{'OBJECT': {'f': ['the', 'ground']}}],
                                               }}],
                             }},
                  {'EVENT': {'r': ['between'],
                             'l': [{'OBJECT': {'f': ['the', 'tire', 'pallets']}}], 'f': [{'OBJECT': {}}]}}])  

    def destCorpusString2(self):
        esdcs = self.extractor.extractEsdcs("Grab the skid of tires right in front of you and " +
                                            "drop it off just in front and to the right of the far skid of tires.")

        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'r': ['Grab', 'right'],
                             'l2': [{'PLACE': {'r': ['in'], 'l': [{'OBJECT': {'f': ['front']}}]}}],
                             'l': [{'OBJECT': {'r': ['of'], 'l2': [{'OBJECT': {'f': ['you']}}],
                                               'l': [{'OBJECT': {'f': ['tires']}}],
                                               'f': ['the', 'skid']}}],
                             'f': [{'OBJECT': {}}]}},
                  {'EVENT': {'r': ['drop', 'off', 'just'],
                             'l2': [{'OBJECT': {'f': ['it']}}],
                             'l': [{'PLACE': {'r': ['in'], 'l': [{'OBJECT': {'f': ['front']}}]}}],
                             'f': [{'OBJECT': {}}]}},
                  {'EVENT': {'r': ['drop', 'off', 'just'], 
                             'l': [{'PATH': {'r': ['to'],
                                             'l': [{'OBJECT': {'r': ['of'],
                                                               'l2': [{'OBJECT': {'f': ['tires']}}],
                                                               'l': [{'OBJECT': {'f': ['the', 'far', 'skid']}}],
                                                               'f': ['the', 'right']}}]}}], 'f': [{'OBJECT': {}}]}}])
        
                 

    def testEmpty(self):
        esdcs = self.extractor.extractEsdcs("")
        self.aeq(esdcs.asPrettyMap(), [])


    def testNextTo(self):
        esdcs = self.extractor.extractEsdcs("Go to the tire pallet next to the truck.")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT':
                   {'r': 'Go',
                    'l': {'PATH': {'r': [['to', [3, 5]]],
                                   'l': {'OBJECT':
                                         {'f': 'the tire pallet',
                                          'r': 'next to',
                                          'l': 'the truck'}}}}}}])




    def destSentences(self):

        command = """ With your back to the glass entryways, walk toward the
        question mark sign.  You will continue roughly in this
        direction as far as you can go, passing: two large white
        columns, two smaller grey pillars, under two skylights, until
        you reach a hanging concrete staircase.  Continue under this
        staircase, then turn right at the doors and continue forward
        until you see elevators.  Stop here."""
        
        esdcs = self.extractor.extractEsdcs(command)
        self.assertEqual(esdcs[0].entireText, command)
        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'r': ['walk'],
                             'l2': [{'PATH': {'r': ['toward'],
                                              'l': [{'OBJECT': {'f': ['the', '\n', 'question', 'mark', 'sign']}}]}}],
                             'l': [{'PATH': {'r': ['With'], 'l': [{'OBJECT': {'r': ['to'],
                                                                              'l': [{'OBJECT': {'f': ['the', 'glass', 'entryways']}}],
                                                                              'f': ['your', 'back']}}]}}],
                             'f': [{'OBJECT': {}}]}},
                  {'EVENT': {'r': ['will', 'continue', 'roughly', 'far', 'li', 'ts, unt', 'he door', 'ard\n   '],
                             'l': [{'PLACE': {'r': ['in'],
                                              'l': [{'OBJECT': {'f': ['this', '\n', 'direction']}}]}}], 'f': ['You']}}, {'EVENT': {'r': ['as', 'can', 'li', 'ts, unt', 'he door', 'ard\n   '], 'l': [{'PATH': {'r': ['until'], 'l': [{'OBJECT': {'f': ['\n', ' righ']}}]}}], 'f': ['you']}}, {'EVENT': {'r': [' righ'], 'l': [{'OBJECT': {'f': ['a', 'hanging', 'concrete', 'staircase']}}], 'f': ['you']}}, {'OBJECT': {'r': ['under'], 'l': [{'OBJECT': {'f': ['two', 'skylights']}}], 'f': ['two', 'large', 'white', '\n', 'he door', 'ard\n   ']}}, {'EVENT': {'r': ['until', 'see'], 'l': [{'OBJECT': {'f': ['elevators']}}], 'f': ['you']}}, {'EVENT': {'r': ['Continue'], 'l': [{'PATH': {'r': ['under'], 'l': [{'OBJECT': {'f': ['this', '\n', 'staircase']}}]}}], 'f': [{'OBJECT': {}}]}}, {'EVENT': {'r': ['then', 'turn', 'right'], 'l': [{'PLACE': {'r': ['at'], 'l': [{'OBJECT': {'f': ['the', 'doors']}}]}}], 'f': [{'OBJECT': {}}]}}])




#(ROOT (S [24.723] (NP [14.111] (NNP [11.454] Go)) (VP [9.470] (VBD [5.845] left)) (. [0.003] .)))
#(ROOT (S [18.169] (VP [17.764] (VB [4.559] go) (VP [7.760] (VBN [5.409] left)))))

    def destBackUp(self):
        esdcs = self.extractor.extractEsdcs("""Back up forklift and turn around forklift. Then line up
        forklift with the pallet before lowering the mechanical fork.""")

        self.aeq(esdcs.asPrettyMap(),
                 [{'EVENT': {'r': ['turn'], 'l': [{'PATH': {'r': ['around'],
                                                            'l': [{'OBJECT': {'f': ['forklift']}}]}}],
                             'f': [{'OBJECT': {}}]}},
                  {'EVENT': {'r': ['Then', 'line', 'up'],
                             'l2': [{'PATH': {'r': ['with'],
                                              'l': [{'OBJECT': {'f': ['the', 'pallet']}}]}}],
                             'l': [{'OBJECT': {'f': ['forklift']}}],
                             'f': [{'OBJECT': {}}]}},
                  {'EVENT': {'r': ['Then', 'line', 'up'],
                             'l': [{'PATH': {'r': ['before'],
                                             'l': [{'OBJECT': {'f': ['lowering']}}]}}],
                             'f': [{'OBJECT': {}}]}},
                  {'EVENT': {'r': ['lowering'], 'l': [{'OBJECT': {'f': ['the', 'mechanical', 'fork']}}], 'f': [{'OBJECT': {}}]}}])
        


    def destPark(self):
        esdcs = self.extractor.extractEsdcs("park in front of the pallet of boxes that is between the pallets of tires.")
        self.aeq(toYaml(esdcs)[1],
                 None)

    def testYourLeft(self):
        esdc_groups = self.extractor.extractTopNEsdcs("Back up and head over " +
                                                      "to the trailer on " +
                                                      "your left.",
                                                      n=3)
        self.ain(esdc_groups,
                 [{'EVENT': {'r': 'Back up'}},
                  {'EVENT':
                   {'r': 'head over',
                    'l': {'PATH': {'r': 'to',
                                   'l': {'OBJECT': {'r': 'on your left',
                                                    'f': 'the trailer'}}}}}}])

    def destYouSee(self):
        esdc_groups = self.extractor.extractTopNEsdcs("Back up a bit and proceed leftward to the first wheeled platform you see.", n=20)
        self.ain(esdc_groups,
                 "")

    def testDrive(self):
        esdc_groups = self.extractor.extractTopNEsdcs('Drive over to the trailer>\r\n', n=20)
        self.ain(esdc_groups,
                 [{'EVENT': {'r': 'Drive over',
                             'l': {'PATH': {'r': 'to', 
                                            'l': [['the', [14, 17]], ['trailer', [18, 25]], ['>', [25, 26]]]}}}}])

    def testGoLeft(self):

        command = "go left"
        
        esdc_group = self.extractor.extractEsdcs(command)
        self.aeq(toYaml(esdc_group)[1],
                 [{'EVENT': {'r': 'go left'}}])



    def testPalletOfBoxes(self):
        esdcs = self.extractor.extractEsdcs("move to the pallet of boxes")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT':
                   {'r': 'move',
                    'l': {'PATH': {'r': 'to',
                                   'l': {'OBJECT':
                                         {'f': 'the pallet',
                                          'r': 'of', 'l': 'boxes', }}}}}}])

        
    def testPalletOfBoxesNearTruck(self):
        esdc_groups = self.extractor.extractTopNEsdcs("move to the pallet of " +
                                                      "boxes near the truck",
                                                      n=20)

        self.ain(esdc_groups,
                 [{'EVENT':
                   {'r': 'move',
                    'l': {'PATH':
                          {'r': 'to',
                           'l': {'OBJECT':
                                 {'f': {'OBJECT':
                                        {'f': 'the pallet',
                                         'r': 'of',
                                    'l': 'boxes'}},
                                  'r': 'near',
                                  'l': 'the truck'}}}}}}])
        
        
    def testOnTheRight(self):
        esdcs = self.extractor.extractTopNEsdcs("move to the truck on the right",
                                                n=50)

        self.ain(esdcs,
                 [{'EVENT':
                   {'r': 'move',
                    'l': {'PATH': {'r': 'to',
                                   'l': {'OBJECT': {'f': 'the truck',
                                                    'r': 'on the right',
                                                    }}}}}}])
        
        


    def testOnTheRightOf(self):
        esdcs = self.extractor.extractTopNEsdcs("move to the truck on " +
                                                "the right of you",
                                                n=20)
        self.ain(esdcs, 
                 [{'EVENT':
                   {'r': 'move',
                    'l': {'PATH':
                          {'r': 'to',
                           'l': {'OBJECT': {'f': 'the truck',
                                            'r': 'on the right of',
                                            'l': 'you'}}}}}}])


    def testInFrontOf(self):
        esdcs = self.extractor.extractEsdcs("move to the truck in front of you")
        self.aeq(toYaml(esdcs)[1],
                 [{'EVENT':
                   {'r': 'move',
                    'l': {'PATH': {'r': 'to',
                                   'l': {'OBJECT':
                                         { 'f': 'the truck',
                                           'r': 'in front of',
                                           'l': 'you',}}}}}}])
        
        
    def testTurnAndMove(self):
        esdcs = self.extractor.extractTopNEsdcs("turn and move to the truck on the right", n=5)
        self.ain(esdcs, 
                 [{'EVENT': {'r': 'turn'}},
                  {'EVENT': {'r': 'move',
                             'l': {'PATH':
                                   {'r': 'to',
                                    'l': {'OBJECT': {'f': 'the truck',
                                                     'r': 'on the right',
                                                     }}}}}}])


        
        
    def testBring(self):
        esdcs = self.extractor.extractTopNEsdcs("Bring the drink bottle " +
                                                "to the right of the computer.",
                                                n=10)

        self.ain(esdcs,
                 [{'EVENT': {'r': 'Bring',
                             'l': {'OBJECT': {'r': 'to the right of',
                                              'l': 'the computer',
                                              'f': 'the drink bottle'}}}}])
                 
    def destMove(self):
        
        esdcs = self.extractor.extractEsdcs("Move to the right side of the " +
                                            "trailer of the trailer on the " +
                                            "right and wait.")


        self.aeq(toYaml(esdcs)[1],
                 "")
        


    def testPossibleInfiniteLoop(self):
        esdcs = self.extractor.extractTopNEsdcs("Move in front of the pallet of boxes in the center and wait.", n=20)

        return
        self.ain(esdcs,
                 [{'EVENT':
                   {'r': 'Move',
                    'l': {'PLACE': {'r': 'in front of',
                                    'l': {'OBJECT':
                                          {'r': [['in', [5, 7]]],
                                           'l': 'the center',
                                           'f': {'OBJECT':
                                                 {'r': [['of', [14, 16]]],
                                                  'l': 'boxes',
                                                  'f': 'the pallet'}}}}}}}},
                  {'EVENT': {'r': 'wait'}}])
    def testPossibleInfiniteLoop2(self):
        #esdcs = self.extractor.extractTopNEsdcs("""Pick up the pallet of tires on
        #the far right, located in front of the
        #forklift. Then back up and drive to the right, then swerve back to the
        #left and deposit the pallet of tires on the ground about midway
        #between the wheeled platform on the left and the rest of the pallets.""",
        #n=50)

        esdcs = self.extractor.extractTopNEsdcs("""Then back up and
        drive to the right, then swerve back to the left and deposit
        the pallet of tires on the ground about midway between the
        wheeled platform on the left and the rest of the pallets.""",
                                                n=50)




        self.assertTrue(esdcs != None)

    def testInfiniteLoop3(self):

        esdcs = self.extractor.extractTopNEsdcs("""Place the pallet of tires
        on the left of the last pallet of tires on the right.""", n=50)

        self.assertTrue(esdcs != None)
        

    def testMultipleSentences(self):
        esdcs = self.extractor.extractTopNEsdcs("""Pick up the pallet of boxes
        directly in front of the forklift and move
        that pallet to the area in between the two pallets of tires to
        your right. Set the pallet down there.""", n=50)

        self.assertTrue(esdcs != None)




    def testIndexError(self):
        esdcs = self.extractor.extractTopNEsdcs("""Move the package pallet to the row to the right.""", n=50)

        self.assertTrue(esdcs != None)




    def testIn(self):
        
        esdcs = self.extractor.extractEsdcsFromSentence("""BUSINESS_CATEGORY in europe""")
        
        self.aeq(toYaml(esdcs)[1],
                 [{'OBJECT': {'f': 'BUSINESS_CATEGORY',
                              'r': 'in',
                              'l': 'europe'}}])
        
