import unittest
from standoff import TextStandoff
from esdcs.dataStructures import ExtendedSdc, _getEntireText, ExtendedSdcGroup, all_object_arguments
from esdcs import dataStructures
from esdcs.esdcIo import fromYaml
import yaml
class TestCase(unittest.TestCase):
    def setUp(self):

        

        self.sentence = "Pick up the tire pallet."
        self.esdc1 = ExtendedSdc("EVENT", r=TextStandoff(self.sentence, (0, 7)),
                                 l=TextStandoff(self.sentence, (8, 23)))
        
        self.esdc2 = ExtendedSdc("EVENT", r=TextStandoff(self.sentence, (0, 7)),
                                 l=TextStandoff(self.sentence, (8, 23)))
        
        self.esdc3 = ExtendedSdc("EVENT", r=TextStandoff(self.sentence, (0, 7)),
                                l=TextStandoff(self.sentence, (8, 22)))


        self.sentence2 = "Pick up the tire pallet near the truck."
        self.childEsdc = ExtendedSdc("OBJECT",
                                     f=TextStandoff(self.sentence2, (8, 23)),
                                     r=TextStandoff(self.sentence2, (24, 28)),
                                     l=TextStandoff(self.sentence2, (29, 38)))
        self.parentEsdc = ExtendedSdc("EVENT",
                                      r=TextStandoff(self.sentence2, (0, 7)),
                                      l=self.childEsdc)
        
    def testEqual(self):
            
        self.assertEqual(self.esdc1, self.esdc1)        
        self.assertEqual(self.esdc1, self.esdc2)
        self.assertNotEqual(self.esdc1, self.esdc3)

    def testSetter(self):
        newL = [TextStandoff(self.sentence, (0, 4))]
        self.esdc1.l = newL

        self.assertEqual(self.esdc1.fields['l'], newL)
        self.assertNotEqual(self.esdc1, self.esdc2)

    def testFlatBreadthFirstTraverse(self):
        esdcs = []
        def callback(esdc):
            esdcs.append(esdc)
                                                              
        dataStructures.breadthFirstTraverse(self.esdc1, callback)
        self.assertEqual(esdcs, [self.esdc1])


    def testAccessingFields(self):        
        self.assertEqual(" ".join([x.text for x in self.childEsdc.f]), "the tire pallet")

        self.assertEqual(" ".join([x.text for x in self.childEsdc.r]), "near")
        self.assertEqual(" ".join([x.text for x in self.childEsdc.l]), "the truck")        

    def testBreadthFirstTraverse(self):
        esdcs = []
        def callback(esdc):
            esdcs.append(esdc)
                                                              
        dataStructures.breadthFirstTraverse(self.parentEsdc, callback)
        self.assertEqual(esdcs, [self.parentEsdc, self.childEsdc])


    def testEntireText(self):
        self.assertEqual(_getEntireText(self.parentEsdc),
                         self.parentEsdc.entireText)
        
                                   
    def testChildTypeChecking(self):
        self.assertEqual(self.parentEsdc.childIsEsdcs("l"), True)
        self.assertEqual(self.parentEsdc.childIsListOfWords("l"), False)
        self.assertEqual(self.parentEsdc.childIsEmpty("l"), False)


        self.assertEqual(self.parentEsdc.childIsEsdcs("f"), False)
        self.assertEqual(self.parentEsdc.childIsListOfWords("f"), False)
        self.assertEqual(self.parentEsdc.childIsEmpty("f"), True)
        
                         
    def testIsEmptyObjectEsdc(self):
        from esdcs import esdcIo
        esdcs = esdcIo.fromYaml("to the truck", {"PATH":{"r":"to", "l":"the truck"}})

        self.assertEqual(esdcs[0].l[0].isLeafObject(), True)
        self.assertEqual(esdcs[0].isLeafObject(), False)

        
    def testRep(self):
        esdc = ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[], entireText="Robots are awesome.")
        self.assertEqual(eval(repr(esdc)), esdc)
        
        esdcGroup = ExtendedSdcGroup([esdc], esdc.entireText)
        print repr(esdcGroup)



    def testEqual1(self):
        e1 = ExtendedSdc('EVENT', r=[TextStandoff("Load the forklift onto the trailer.", (0, 4))],l2=[ExtendedSdc('PATH', r=[TextStandoff("Load the forklift onto the trailer.", (18, 22))],l2=[],l=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Load the forklift onto the trailer.", (23, 26)), TextStandoff("Load the forklift onto the trailer.", (27, 34))])],f=[])],l=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Load the forklift onto the trailer.", (5, 8)), TextStandoff("Load the forklift onto the trailer.", (9, 17))])],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[], entireText='Load the forklift onto the trailer.')])
        e2 = ExtendedSdc('EVENT', r=[TextStandoff("Load the forklift onto the trailer.", (0, 4))],l2=[ExtendedSdc('PATH', r=[TextStandoff("Load the forklift onto the trailer.", (18, 22))],l2=[],l=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Load the forklift onto the trailer.", (23, 26)), TextStandoff("Load the forklift onto the trailer.", (27, 34))])],f=[])],l=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[TextStandoff("Load the forklift onto the trailer.", (5, 8)), TextStandoff("Load the forklift onto the trailer.", (9, 17))])],f=[ExtendedSdc('OBJECT', r=[],l2=[],l=[],f=[], entireText='Load the forklift onto the trailer.')])  
        self.assertEqual(e1, e2)

        self.assertFalse(e1 != e2)

        self.assertTrue(e1 in [e2])
        self.assertTrue(e2 in [e1])
        
        

        
    def testBreadthFirstTraverseLoop(self):
        cmd = "Move in front of the pallet of boxes in the center and wait."        
        esdc = ExtendedSdc('EVENT',
                           r=[TextStandoff(cmd, (0, 4)),
                              TextStandoff(cmd, (5, 7))],
                           l2=[],
                           f=[TextStandoff(cmd, (8, 13))])
        esdc.l = [esdc]
        def callback(esdcFromParent):
            print "callback"
                
        dataStructures.breadthFirstTraverse(esdc, callback)
        
    def testParentsToChildren(self):
                                                              


        esdcs = dataStructures.parentsToChildren(self.parentEsdc)
        print [str(e) for e in esdcs]
        self.assertEqual(esdcs, [self.parentEsdc, self.childEsdc])
        
    def testAllObjectArguments(self):
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
        
        self.assertEqual(all_object_arguments(esdc), True)
        self.assertEqual(all_object_arguments(esdc.f[0]), True)
        self.assertEqual(all_object_arguments(esdc.l[0]), True)


        esdcGroup = fromYaml("Pick up the pallet",
                             yaml.load("""
        - EVENT:
            r: Pick up
            l: the pallet
        """))
        esdc = esdcGroup[0]
        
        self.assertEqual(all_object_arguments(esdc), True)
        self.assertEqual(all_object_arguments(esdc.l[0]), True)


        esdcGroup = fromYaml("Go to the pallet",
                             yaml.load("""
        - EVENT:
            r: Go 
            l: 
              PATH:
                r:  to
                l:  the pallet
        """))
        esdc = esdcGroup[0]
        
        self.assertEqual(all_object_arguments(esdc), False)
        self.assertEqual(all_object_arguments(esdc.l[0]), True)
