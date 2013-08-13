import unittest

from esdcs.extractor.extractorBase import correctStandoffs, correctStandoffsImmutable
from standoff import TextStandoff
from esdcs.esdcIo import yamlReader
from esdcs.dataStructures import ExtendedSdcGroup

class TestCase(unittest.TestCase):
    def testCorrectStandoffs(self):
        annotations = yamlReader.load("data/forklift_open_ended.yaml")
        esdc1 = annotations[0].esdcs[0]
        esdc2 = annotations[1].esdcs[0]

        new_entire_text = esdc1.entireText + " " + esdc2.entireText
        
        sentence_standoff = TextStandoff(new_entire_text, esdc1.range)
        
        correctStandoffs(sentence_standoff, esdc1)
        self.assertEqual(esdc1.entireText, new_entire_text)
        
    def testCorrectStandoffsImmutable(self):
        annotations = yamlReader.load("data/forklift_open_ended.yaml")
        esdc1 = annotations[0].esdcs[0]
        esdc2 = annotations[1].esdcs[0]
        old_entire_text = esdc1.entireText
        new_entire_text = esdc1.entireText + " " + esdc2.entireText
        
        sentence_standoff = TextStandoff(new_entire_text, esdc1.range)
        
        correctedEsdc1 = correctStandoffsImmutable(sentence_standoff, 
                                                   ExtendedSdcGroup([esdc1]))
        self.assertEqual(esdc1.entireText, old_entire_text)
        self.assertEqual(correctedEsdc1.entireText, new_entire_text)
        

        print str(correctedEsdc1[0])
        self.assertEqual(" ".join(x.text for x in correctedEsdc1[0]["f"]), 
                         "Forklift")

