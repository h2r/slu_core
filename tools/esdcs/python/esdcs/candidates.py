from dataStructures import ExtendedSdc, ExtendedSdcGroup, isLeafObject, \
     objectifyLandmarks, addEmptyFigures, objectifyFiguresOfEvents
import itertools



def makeDirectCandidatesForEsdc(esdc):
    if esdc.hasCycle():
        return [esdc]
    esdc = ExtendedSdc.copy(esdc)
    candidates = [esdc]
    if (esdc.childIsEsdcs("l") 
        and len(esdc.l) == 1 and not isLeafObject(esdc.l[0])):

        # "for on the right of X"
        landmark = esdc.l[0]
        new_relations = []
        new_relations.extend(esdc.r)
        if landmark.childIsEsdcs("f"):
            for e in landmark.f:
                new_relations.extend(e.standoffs())
        else:
            new_relations.extend(landmark.f)
        new_relations.extend(landmark.r)

        newEsdc = ExtendedSdc(esdcType=esdc.type,
                              entireText=esdc.entireText,
                              f=esdc.f,
                              r=new_relations,
                              l=landmark.l)

        candidates.append(newEsdc)

    l_words = " ".join([w.text.lower() for w in esdc.l])
    if (esdc.type == "OBJECT" and esdc.childIsLeafObject("l") and
        ("right" in l_words or "left" in l_words)):
        new_relations = esdc.r + esdc.l[0].f
        newEsdc = ExtendedSdc(esdcType=esdc.type,
                              entireText=esdc.entireText,
                              f=esdc.f,
                              r=new_relations,
                              l=[])
        candidates.append(newEsdc)        

    objectifyLandmarks(candidates)
    objectifyFiguresOfEvents(candidates)
    addEmptyFigures(candidates)
    return candidates
def makeChildCandidates(esdc):

    if esdc.hasCycle():
        return []
    candidates_for_keys = []
    for key in esdc.fieldNames:
        child_candidates = []
        if esdc.childIsEsdcs(key):
            candidates = []
            for child in esdc.children(key):
                lst = []
                lst.extend(makeCandidatesForEsdc(child))
                candidates.append(lst)

            child_candidates.extend(itertools.product(*candidates))
        else:
            child_candidates.append(esdc.children(key))
        candidates_for_keys.append(child_candidates)
        
    candidate_esdcs = []
    for candidates in itertools.product(*candidates_for_keys):
        assert len(candidates) == len(esdc.fieldNames)
        args = dict(zip(esdc.fieldNames, candidates))
        candidate_esdcs.append(ExtendedSdc(esdcType=esdc.type,
                                           entireText=esdc.entireText,
                                           **args))
    assert len(candidates_for_keys) == len(esdc.fieldNames)
    return candidate_esdcs
def makeCandidatesForEsdc(esdc):
    direct_candidates = makeDirectCandidatesForEsdc(esdc)
    candidates = []
    for candidate in direct_candidates:
        candidates.extend(makeChildCandidates(candidate))

    return candidates


def makeCandidatesForEsdcGroup(esdc_group):
    candidates_for_esdc = [makeCandidatesForEsdc(esdc) for esdc in esdc_group]
    groups = []

    for candidates in itertools.product(*candidates_for_esdc):
        groups.append(ExtendedSdcGroup(candidates,
                                       entireText=esdc_group.entireText,
                                       score=esdc_group.score,
                                       metadata=esdc_group.metadata))

    if len(groups) == 0:
        return [esdc_group]
    else:
        return groups
                   
                               
