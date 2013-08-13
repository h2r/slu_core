import re
from esdcs.dataStructures import breadthFirstTraverse, ExtendedSdcGroup
from esdcs.sentenceTokenizer import SentenceTokenizer
import numpy as na
from itertools import chain
from standoff import correctStandoff, correctStandoffImmutable, correctStandoffOffset

def correctStandoffsOffset(esdcs, new_entire_text, offset):
    modified_esdcs = ExtendedSdcGroup.copy(esdcs)
    update_rep_esdcs = []
    def callback(esdc):
        esdc.entireText = new_entire_text
        update_rep_esdcs.append(esdc)
        for fieldName in esdc.fieldNames:
            if esdc.childIsListOfWords(fieldName):
                new_standoffs = [correctStandoffOffset(s, new_entire_text, offset)
                                 for s in esdc[fieldName]]
                esdc.fields[fieldName] = new_standoffs
                    

    breadthFirstTraverse(modified_esdcs, callback)
    for e in reversed(update_rep_esdcs):
        e.updateRep()
    return ExtendedSdcGroup(modified_esdcs)

    
def correctStandoffsImmutable(sentenceStandoff, esdcs):
    """Corrects the standoffs in the esdcs
    to be relative to a larger standoff object.  Returns the new ESDC
    """
    
    modified_esdcs = ExtendedSdcGroup.copy(esdcs)
    def callback(esdc):
        for fieldName in esdc.fieldNames:
            if esdc.childIsListOfWords(fieldName):
                new_standoffs = [correctStandoffImmutable(sentenceStandoff, s)
                                 for s in esdc[fieldName]]
                esdc.fields[fieldName] = new_standoffs
                    
        esdc.entireText = sentenceStandoff.entireText
    breadthFirstTraverse(modified_esdcs, callback)
    for e in modified_esdcs:
        e.updateRep()
    return ExtendedSdcGroup(modified_esdcs)
    
def correctStandoffs(sentenceStandoff, esdcs):
    """
    Corrects the standoffs in the esdcs to be relative to a larger
    standoff object.  For example, if you have a multi-sentence
    command like "Pick up the tire pallet.  Put it on the truck."  The
    parser outputs standoffs for each sentence separately (e.g., just
    "Put it on the truck.")  But the standoffs for the entire command
    should refer to the larger string.  

    This method takes as input the standoff for "Put it on the truck"
    in the context of the larger string, as well as SDCs for just "Put
    it on the truck" and rewrites them to refer to the larger string.

    It MUTATES the ESDCs, unlike most ESDC methods.  It CHANGES the
    hash code.
    """
    modified_esdcs = []
    def callback(esdc):
        modified_esdcs.append(esdc)
        for fieldName in esdc.fieldNames:
            if esdc.childIsListOfWords(fieldName):
                for standoff in esdc[fieldName]:
                    correctStandoff(sentenceStandoff, standoff)
        esdc.entireText = sentenceStandoff.entireText
    breadthFirstTraverse(esdcs, callback)
    esdcs.entireText = sentenceStandoff.entireText
    for esdc in reversed(modified_esdcs):
        esdc.updateRep()




def normalizeWhitespace(command):
    """
    Get rid of newlines, etc.  All whitespace strings are
    converted to exactly one space.
    """
    return re.sub(r"\s+", " ", command)


class Extractor(object):
    def __init__(self):
        self.sentenceTokenizer = SentenceTokenizer()

    def extractEsdcs(self, command):
        command = normalizeWhitespace(command)
        esdcList = []
        score = 0.0
        for sentenceStandoff in self.sentenceTokenizer.tokenize(command):
            esdcs = self.extractEsdcsFromSentence(sentenceStandoff.text)
            assert sentenceStandoff.entireText == command
            correctStandoffs(sentenceStandoff, esdcs)
            esdcList.extend(esdcs)
            score += esdcs.score

        return ExtendedSdcGroup(esdcList, command, score=score)

    def extractTopNEsdcs(self, command, n):
        command = normalizeWhitespace(command)
        esdcList = []
        for sentenceStandoff in self.sentenceTokenizer.tokenize(command):
            esdcs = self.extractTopNEsdcsFromSentence(sentenceStandoff.text, n + 10)
            for esdc in esdcs:
                correctStandoffs(sentenceStandoff, esdc)
            esdcList.append(esdcs)

            
        esdcList = [e for e in esdcList if len(e) != 0]
        indices = [0 for esdcGroups in esdcList]

        results = []
        for iteration in range(0, n):
            lst = [esdcGroups[i] for i, esdcGroups in zip(indices, esdcList)]
            metadata = [e.metadata for e in lst]
            score = sum(e.score for e in lst)
            results.append(ExtendedSdcGroup(list(chain(*lst)), command,
                                            score=score, metadata=metadata))
            next_indices = [min(index + 1, len(esdcList[i]) - 1)
                            for i, index in enumerate(indices)]
            best_idx = na.argmax([esdcGroups[min(i, len(esdcGroups) - 1)].score for i, esdcGroups in zip(next_indices, esdcList)])
            indices[best_idx] = next_indices[best_idx]
            
        return results

    def extractEsdcsFromSentence(self, sentence):
        esdcs = self.extractTopNEsdcsFromSentence(sentence, n=1)
        if len(esdcs) == 0:
            raise ValueError("No results returned for " + `sentence`)
        return esdcs[0] 


    
    
    
    
