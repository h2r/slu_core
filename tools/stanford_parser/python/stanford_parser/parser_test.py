import unittest

from stanford_parser.parser import Parser, startJvm
startJvm()
parser = Parser()


class TestCase(unittest.TestCase):

    def testParseTopN(self):
        
        d1, d2 = parser.parseToTopNStanfordDependencies("Pick up the tire pallet.", 2)

        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in d1.dependencies]
        self.assertEqual(tupleResult, [
                ('root', '.', 'Pick'),
                ('prt', 'Pick', 'up'),
                ('det', 'pallet', 'the'),
                ('nn', 'pallet', 'tire'),
                ('dobj', 'Pick', 'pallet')])

        self.assertEqual(d1.tagForTokenStandoff(gov), "VB")
        self.assertEqual(d1.tagForTokenStandoff(dep), "NN")


        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in d2.dependencies]
        print tupleResult
        self.assertEqual(tupleResult,
                         [('root', '.', 'Pick'), 
                          ('prt', 'Pick', 'up'),
                          ('det', 'pallet', 'the'), 
                          ('nn', 'pallet', 'tire'), 
                          ('dobj', 'Pick', 'pallet')])


        self.assertEqual(d2.tagForTokenStandoff(gov), "VB")
        self.assertEqual(d2.tagForTokenStandoff(dep), "NN")

        self.assertTrue(d1.score < 0)
        self.assertTrue(d2.score < 0)
    
        
    def testParse(self):
        
        dependencies = parser.parseToStanfordDependencies("Pick up the tire pallet.")

        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in dependencies.dependencies]
        self.assertEqual(tupleResult, [('root', '.', 'Pick'),
                                       ('prt', 'Pick', 'up'),
                                       ('det', 'pallet', 'the'),
                                       ('nn', 'pallet', 'tire'),
                                       ('dobj', 'Pick', 'pallet')])

        self.assertEqual(dependencies.tagForTokenStandoff(gov), "VB")
        self.assertEqual(dependencies.tagForTokenStandoff(dep), "NN") 

    def testParseRefexpNextTo(self):        
        dependencies = parser.parseToStanfordDependencies("Pick up the tire pallet next to the truck.")
        
        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in dependencies.dependencies]

        
        self.assertEqual(tupleResult,
                         [
                ('root', '.', 'Pick'),
                ('prt', 'Pick', 'up'),
                ('det', 'pallet', 'the'),
                ('nn', 'pallet', 'tire'),
                ('dobj', 'Pick', 'pallet'),
                ('det', 'truck', 'the'),
                ('prep_next_to', 'pallet', 'truck')])


    def testParseRefexpNear(self):                
        dependencies =parser.parseToStanfordDependencies("Pick up the tire pallet near the truck.")
        
        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in dependencies.dependencies]
        self.assertEqual(tupleResult,
                         [
                ('root', '.', 'Pick'),
                ('prt', 'Pick', 'up'),
                ('det', 'pallet', 'the'),
                ('nn', 'pallet', 'tire'),
                ('dobj', 'Pick', 'pallet'),
                ('det', 'truck', 'the'),
                ('prep_near', 'pallet', 'truck')])

        

    def testParseLong(self):                

        # this sentence has a self dependency that the python code filters out.
        # between drop and drop.
        dependencies = parser.parseToStanfordDependencies("Grab the skid of tires right in front of you " +
                                                               "and drop it off just in front and to the " +
                                                               "right of the far skid of tires.")
    
        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in dependencies.dependencies]
        self.assertEqual(tupleResult,
                         [
                ('root', '.', 'Grab'),
                ('det', 'skid', 'the'),
                ('dobj', 'Grab', 'skid'),
                ('prep_of', 'skid', 'tires'),
                ('advmod', 'Grab', 'right'),
                ('prep_in', 'Grab', 'front'),
                ('prep_of', 'front', 'you'),
                ('conj_and', 'Grab', 'drop'),
                ('dobj', 'drop', 'it'),
                ('prt', 'drop', 'off'),
                ('advmod', 'drop', 'just'),
                ('prep_in', 'drop', 'front'),
                ('det', 'right', 'the'),
                ('prep_to', 'drop', 'right'),
                ('det', 'skid', 'the'),
                ('amod', 'skid', 'far'),
                ('prep_of', 'right', 'skid'),
                ('prep_of', 'skid', 'tires')])

                         
       
    
    def testAllCaps(self):
        dependencies = parser.parseToStanfordDependencies("GO TO THE TIRE PALLET NEXT TO THE TRUCK.")
        tupleResult = [(rel, gov.text, dep.text) for rel, gov, dep in dependencies.dependencies]
        print "tuple", tupleResult
        self.assertEqual(tupleResult,
                         [('nn', 'PALLET', 'GO'), 
                          ('nn', 'PALLET', 'TO'), 
                          ('nn', 'PALLET', 'THE'), 
                          ('nn', 'PALLET', 'TIRE'), 
                          ('nsubj', 'NEXT', 'PALLET'), 
                          ('root', '.', 'NEXT'), 
                          ('dep', 'NEXT', 'TO'),
                          ('det', 'TRUCK', 'THE'), 
                          ('dobj', 'TO', 'TRUCK')])

        

        
    def testNBest(self):
        dependencies = parser.parseToTopNStanfordDependencies("  pick up the pallet of of tires that is directly to the right of the pallet of boxes.",
                                                              10)

        self.assertEqual(len(dependencies), 10)
