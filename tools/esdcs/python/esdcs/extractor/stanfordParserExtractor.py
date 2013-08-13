from esdcs.dataStructures import ExtendedSdc, objectifyLandmarks, \
     addEmptyFigures, breadthFirstTraverse, ExtendedSdcGroup, flattenedEsdcs, \
     isTopLevel, objectifyFiguresOfEvents, freeze, unfreeze
from standoff import TextStandoff
import extractorBase
from esdcs import candidates as esdcCandidates

def baseFigureStandoff(esdc):
    if len(esdc.f) == 1 and esdc.childIsEsdcs('f'):
        return baseFigureStandoff(esdc.f[0])
    else:
        return esdc.f

def baseLandmarkStandoff(esdc):
    if esdc.childIsListOfWords("l"):
        return esdc.l
    elif esdc.childIsEsdcs("l"):
        return baseFigureStandoff(esdc.l[0])
    else:
        return []
        

def pp(obj):
    if isinstance(obj, list) or isinstance(obj, tuple):
        return ", ".join([pp(x) for x in obj])
    else:
        return str(obj)
    
def mergeAll(esdcs):
    mergedSet = list()
    newEsdcs = []
    fesdcs = flattenedEsdcs(esdcs)
    for esdc1 in fesdcs:
        for esdc2 in fesdcs:
            if (esdc1 not in mergedSet and esdc2 not in mergedSet
                and esdc1 != esdc2):

                newEsdc = merge(esdc1, esdc2)
                

                if newEsdc != None and not newEsdc.hasCycle():
                    newEsdc.updateRep()
                    mergedSet.append(esdc1)
                    mergedSet.append(esdc2)

                    def callback(esdc):
                        for key in esdc.fieldNames:
                            if esdc.childIsEsdcs(key):
                                esdc.setChild(key,
                                              [e if e not in [esdc1, esdc2] else newEsdc for e in esdc.children(key)])
                    for e in flattenedEsdcs(esdcs + newEsdcs):
                        callback(e)
                    newEsdcs.append(newEsdc)

    for esdc in esdcs:
        if esdc not in mergedSet:
            newEsdcs.append(esdc)


    topLevelEsdcs = [esdc for esdc in newEsdcs
                     if isTopLevel(esdc, newEsdcs)]
    return topLevelEsdcs
                    
                    
                    

    

def firstAndSecond(esdc1, esdc2):    
    esdc1Range = esdc1.l[0].range[0] if esdc1.l != [] else -1
    esdc2Range = esdc2.l[0].range[0] if esdc2.l != [] else -1
    if esdc1Range < esdc2Range:
        firstEsdc = esdc1
        secondEsdc = esdc2
    else:
        firstEsdc = esdc2
        secondEsdc = esdc1
    return firstEsdc, secondEsdc


def merge(esdc1, esdc2, verbose=False):
    # event with more than one landmark
    if esdc1 == esdc2:
        return esdc1
    esdc1.updateRep()
    esdc2.updateRep()

    if esdc1.hasCycle() or esdc2.hasCycle():
        return None

    if verbose:
        print "*****************************"
        print esdc1
        print esdc2

    #if (esdc1.r == esdc2.r):
    if (all(r in esdc2.r for r in esdc1.r) or
        all(r in esdc1.r for r in esdc2.r)):
        firstEsdc, secondEsdc = firstAndSecond(esdc1, esdc2)
        newEsdc = ExtendedSdc.copy(firstEsdc)
        if verbose:
            print "merge 1"
        
        if len(firstEsdc.r)  < len(secondEsdc.r):
            newEsdc.r = secondEsdc.r

        
        if firstEsdc.childIsEmpty("l"):
            newEsdc.l = secondEsdc.l
        elif firstEsdc.childIsEmpty("l2"):
            newEsdc.l2 = secondEsdc.l

        if newEsdc.childIsEmpty("l2"):
            newEsdc.l2 = secondEsdc.l2

        if firstEsdc.childIsEmpty("f"):
            newEsdc.f = secondEsdc.f
        else:
            newEsdc.f = firstEsdc.f

        if verbose:
            print newEsdc
        return newEsdc

        
    
    elif (esdc1.f == esdc2.f and esdc1.type == "OBJECT"
          and esdc2.type == "OBJECT"):
        if verbose:
            print "merge 2"
        firstEsdc, secondEsdc = firstAndSecond(esdc1, esdc2)

        newEsdc = ExtendedSdc.copy(secondEsdc)
        newEsdc.f = [firstEsdc]
        if verbose:
            print newEsdc        
        return newEsdc
    elif (esdc1.type == "OBJECT" and
          baseFigureStandoff(esdc1) == baseLandmarkStandoff(esdc2)
          and not esdc1 in esdc2.l
          ):
        if verbose:
            print "merge 3"
        
        newEsdc = ExtendedSdc.copy(esdc2)
        newEsdc.l = [esdc1]
        if verbose:
            print newEsdc        
        return newEsdc
    else:
        return None
    
    

def standoffForString(relation, sentence):

    try:
        if relation.startswith("prep"):
            preposition = relation[relation.index("_") + 1:].replace("_", " ")
            
            index = sentence.lower().find(preposition + " ")
            if index == -1:
                index = sentence.lower().find(preposition )
                
            string = sentence[index:index + len(preposition)]
            standoffs = []
            offset = index
            for token in string.split(" "):
                standoffs.append(TextStandoff(sentence, (offset, offset + len(token))))
                offset += len(token) + 1


            return (standoffs, preposition)
        else:
            raise ValueError("Invalid relation: " + `relation` + " in " + `sentence`)
    except:
        print "relation", relation
        print "sentence", sentence
        raise





class Extractor(extractorBase.Extractor):
    def __init__(self):
        extractorBase.Extractor.__init__(self)
        from stanford_parser.parser import getParser
        from stanford_parser import dependencies
        
        self.parser = getParser()
        self.sdh = dependencies.StanfordDependencyHierarchy()


        
    def esdcGroupFromDependencies(self, sentence, dependencies):
        if len(dependencies.dependencies) == 0:
            return ExtendedSdcGroup([ExtendedSdc("EVENT",
                                                 r=dependencies.tokens[0])],
                                    entireText=sentence,
                                    score=dependencies.score,
                                    metadata=dependencies
                                    )
        else:
            esdcList = self.extractEsdcList(sentence, dependencies)
            hierarchicalEsdcs = self.extractHierarchy(dependencies, esdcList)
            objectifyLandmarks(hierarchicalEsdcs)
            objectifyFiguresOfEvents(hierarchicalEsdcs)
            addEmptyFigures(hierarchicalEsdcs)
            
            hierarchicalEsdcs.sort(key=lambda e: e.startIdx)
            return ExtendedSdcGroup(hierarchicalEsdcs, entireText=sentence,
                                    score=dependencies.score,
                                    metadata=dependencies)
                


        

        
        
    def extractTopNEsdcsFromSentence(self, sentence, n):
        if sentence.strip() == "":
            return [ExtendedSdcGroup([], entireText=sentence)]
        
        topNDependencies = self.parser.parseToTopNStanfordDependencies(sentence, n)


        result = list()
        idx = 0
        for i, dependencies in enumerate(topNDependencies):
            esdc_group = self.esdcGroupFromDependencies(sentence, dependencies)
            assert esdc_group.entireText == sentence
            candidates = esdcCandidates.makeCandidatesForEsdcGroup(esdc_group)
            for c in candidates:
                c.idx = idx
                idx += 1

            result.extend(candidates)

        candidateSet = set()
        newResult = []
        for r in result:
            if not r in candidateSet:
                newResult.append(r)
                candidateSet.add(r)


        #result = list(sorted(result, key=lambda x: x.idx))
        return newResult
                

    def extractHierarchy(self, dependencies, esdcList):
        """
        Extracts the hierarchy given a flat list of esdcs.
        The token 'the tire pallet' appears as a landmark of one esdc and a figure of another one, and
        we have to connect them.
        """
        def findParent(esdcs, child):
            for potentialParent in esdcs:
                if (potentialParent == child or
                    child.isAncestor(potentialParent)):
                    continue

                potentialEsdcs = []

                def callback(esdcFromParent):
                    if esdcFromParent.l == child.f and child.f != []:
                        potentialEsdcs.append(esdcFromParent)


                breadthFirstTraverse(potentialParent, callback)
                if len(potentialEsdcs) >= 1:
                    assert len(potentialEsdcs) == 1
                    return potentialEsdcs[0]
            return None
        
        newList = []
        for esdc in esdcList:
            parent = findParent(esdcList, esdc)
            if parent == None:
                newList.append(esdc)
                esdc.updateRep()                
            else:
                parent.l = [esdc]
                

        return newList

    def extractEsdcList(self, sentence, dependencies):
        """
        Returns a list of ESDCs, without hierarchy.
        """

        esdcs = []

        child_esdcs = []

        leftover_deps = []

        for relation, gov, dep in dependencies.dependencies:
            #print "Relation:", relation
            if relation == "root":
                continue
            if relation == "prep":
                
                esdc = ExtendedSdc("EVENT", r=gov, l=ExtendedSdc("EVENT", r=dep))
            elif relation.startswith("prep"):
                prepStandoff, prep = standoffForString(relation, sentence)
                govTag = dependencies.tagForTokenStandoff(gov)
                if prep in ["on", "in", "at","near","next to", "in front of", "behind", "away from", "close to", "closer to"]:
                    esdcType = "PLACE"
                else:
                    esdcType ="PATH"
                #if relation.startswith("prepc"):
                if not govTag in ["NN", "NNS", "NNP"]:
                    esdc = ExtendedSdc("EVENT", r=gov,
                                       l=ExtendedSdc(esdcType,
                                                     r=prepStandoff,
                                                     l=dep))
                    child_esdcs.extend(esdc.l)
                    esdcs.append(esdc)                    
                else:

                    if govTag in ["NN", "NNS", "NNP"]:
                        esdc = ExtendedSdc("OBJECT", f=gov, r=prepStandoff,
                                           l=dep)
                    else:
                        esdc = ExtendedSdc("EVENT",r=gov,
                                           l=[ExtendedSdc(esdcType,
                                                          r=prepStandoff,
                                                          l=dep)])
                        child_esdcs.extend(esdc.l)                        
                    esdcs.append(esdc)
            elif relation == "conj_and":
                esdcs.append(ExtendedSdc("EVENT", r=[gov]))
                esdcs.append(ExtendedSdc("EVENT", r=[dep]))
            elif self.sdh.isa(relation, "arg"):
                esdc = ExtendedSdc("EVENT", r=gov, l=dep)
                esdcs.append(esdc)

            elif self.sdh.isa(relation, "subj"):
                esdc = ExtendedSdc("EVENT", f=dep, r=gov)
                esdcs.append(esdc)
            elif relation == "conj_and":
                pass
            elif relation == "dep":
                esdc = ExtendedSdc("EVENT", r=[dep, gov])
                esdcs.append(esdc)
            else:
                leftover_deps.append((relation, gov, dep))


        for relation, gov, dep in leftover_deps:
            for esdc in flattenedEsdcs(esdcs): #chain(esdcs, child_esdcs): 
                for key, valueList in esdc:
                    if gov in valueList:
                        valueList.append(dep)


        freeze(esdcs)
        esdcs = list(sorted(set(esdcs)))
        unfreeze(esdcs)
        
        esdcs = mergeAll(esdcs)
        esdcs = mergeAll(esdcs)
        #esdcs = mergeAll(esdcs)
                        
        #for esdc in flattenedEsdcs(esdcs):
        #    esdc.updateRep()

        for esdc in flattenedEsdcs(esdcs):
            esdc.updateRep()        

        if len(esdcs) == 0:
            print "sentence", sentence, sentence.__class__
            sentence_standoff = TextStandoff(sentence, (0, len(sentence)))
            return [ExtendedSdc("EVENT", r=sentence_standoff)]
        return esdcs
            

        
