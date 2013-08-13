import unittest
from esdcs.esdcIo import annotationIo
from esdcs.groundings import PhysicalObject, Prism, Place, Path
from esdcs.dataStructures import null_ids
from numpy import transpose as tp
import numpy as na

#SOURCE_FILE = "../forklift/dataCollection/data/dialog/parsed_dialog_edited.yaml"
SOURCE_FILE = "data/forkliftMturkEsdcs.yaml"

def xyToXyth(fig_xy):
    fig_xy = na.array(fig_xy)
    Xst, Yst = fig_xy[:,:-1]
    Xend, Yend = fig_xy[:,1:]
   
    Theta = na.arctan2(Yend-Yst, Xend-Xst);
    Theta = list(Theta)
    Theta.append(Theta[-1])
    return na.array([fig_xy[0], fig_xy[1], Theta])



def pts_to_xyzTheta(points_pts):
    X, Y, Theta = xyToXyth(na.transpose(points_pts))
    Z = na.zeros(len(X))
    return na.array([X, Y, Z, Theta])


class TestCase(unittest.TestCase):
    def testReader(self): 

        corpus = annotationIo.load(SOURCE_FILE)

        assignmentIds = set()
        for annotation in corpus:
            assignmentIds.add(annotation.assignmentId)

        self.assertEqual(len(assignmentIds), len(corpus))
        
        
        yamlCorpus = annotationIo.toYaml(corpus)
        newCorpus = annotationIo.fromYaml(yamlCorpus)

        esdc1 = corpus[0].esdcs[-1]
        esdc2 = newCorpus[0].esdcs[-1]

        null_ids(esdc1)
        null_ids(esdc2)
        
        self.assertEqual(esdc1, esdc2)

        
        self.assertEqual(corpus[0].esdcToGroundings[esdc1],
                         newCorpus[0].esdcToGroundings[esdc2])

        self.assertEqual(corpus[0], newCorpus[0])
        for a1, a2 in zip(corpus, newCorpus):
            print "***********"
            print "a1"
            print [str(e) for e in a1.esdcs]
            print "a2"
            print [str(e) for e in a2.esdcs]
            
            for esdc1, esdc2 in zip(a1.flattenedEsdcs, a2.flattenedEsdcs):
                self.assertEqual(esdc1.text, esdc2.text)
                groundings1 = a1.getGroundings(esdc1)
                groundings2 = a2.getGroundings(esdc2)
                self.assertEqual(len(groundings1), len(groundings2))
                for g1, g2 in zip(groundings1, groundings2):
                    self.assertEqual(g1, g2)

    def testGroundings(self):
        corpus = annotationIo.load(SOURCE_FILE)
        annotation = corpus[0]

        esdc = annotation.flattenedEsdcs[0]

        annotation.addGrounding(esdc, PhysicalObject(Prism.from_points_xy(tp([(0, 0), (1, 0),
                                                               (1, 1), (0, 1)]),
                                                           3, 4),
                                                     ["tire", "pallet"]))

        annotation.addGrounding(esdc, Place(Prism.from_points_xy(tp([(0, 0), (1, 0),
                                                      (1, 1), (0, 1)]), 3, 4)))
        
        annotation.addGrounding(esdc,
                                Path.from_xyztheta(timestamps=[0, 1],
                                     points_xyztheta=pts_to_xyzTheta([(0, 0),
                                                                      (1, 1)])))

        
                                

        yamlCorpus = annotationIo.toYaml(corpus)

        print "yaml", yamlCorpus
        newCorpus = annotationIo.fromYaml(yamlCorpus)


        esdc1 = corpus[0].flattenedEsdcs[0]
        esdc2 = newCorpus[0].flattenedEsdcs[0]
        null_ids(esdc1)
        null_ids(esdc2)
        self.assertEqual(esdc1, esdc2)

    def testDuplicateEsdcs(self):
        corpus = annotationIo.load(SOURCE_FILE)
        annotation = corpus[-1]
        self.assertEqual(len(annotation.esdcs), 3)
        for i, esdc in enumerate(annotation.esdcs):
            groundings = annotation.getGroundings(esdc)
            self.assertEqual(len(groundings), 1)
            grounding = groundings[0]
            print "id", esdc.id
            self.assertEqual(grounding.tags, ("trailer%d" % (i + 1),))
            



        
    def testLoadSave(self):
        corpus1 = annotationIo.load("data/corpusWithPathsSmall.v0.yaml")
        annotationIo.save(corpus1, "data/corpusWithPathsSmall.v1.yaml")
        corpus2 = annotationIo.load("data/corpusWithPathsSmall.v1.yaml")

        self.assertEqual(len(corpus1), len(corpus2))

        

    def testSource(self):
        corpus1 = annotationIo.load("data/corpusWithPathsSmall.v0.yaml")
        annotation1 = corpus1[0]
        esdc1 = annotation1.esdcs[0]
        annotation1.setSource(esdc1, "person 1")
        self.assertEqual(annotation1.getSource(esdc1), "person 1")


        annotationIo.save(corpus1, "data/corpusWithPathsSmall.v1.yaml")

        corpus2 = annotationIo.load("data/corpusWithPathsSmall.v1.yaml")
        annotation2 = corpus2[0]
        esdc2 = annotation2.esdcs[0]
        self.assertEqual(annotation1.getSource(esdc1),
                         annotation2.getSource(esdc2))

