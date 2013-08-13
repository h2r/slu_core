import dataStructures as ds
import crfEntityExtractor
from esdcs.dataStructures import objectifyLandmarks
from esdcs.dataStructures import ExtendedSdc

"""
Module to convert from route directions.
"""

def computeEsdcType(routeDirectionSdc):
    if routeDirectionSdc.verb.text != "":
        return "EVENT"
    elif routeDirectionSdc.figure.text != "":
        return "OBJECT"
    elif routeDirectionSdc.spatialRelation.text != "":
        # could be a place too, check this.
        return "PATH"
    else:
        return "OBJECT"

def toEsdcFields(field_to_child):
    outMap = {}
    if field_to_child["verb"] != None:
        outMap["r"] = field_to_child["verb"]
        if field_to_child["spatialRelation"] != None:
            if field_to_child["spatialRelation"] in ["at", "on", "in"]:
                esdcType = "PLACE"
            else:
                esdcType = "PATH"
            

            outMap["l"] = [ExtendedSdc(esdcType=esdcType,
                                       r=field_to_child["spatialRelation"],
                                       l=field_to_child["landmark"],
                                       l2=field_to_child["landmark2"])]
    elif field_to_child["spatialRelation"] != None:
        outMap["r"] = field_to_child["spatialRelation"]

    outMap["f"] = field_to_child["figure"]
    if not "l" in outMap:
        outMap["l"] = field_to_child["landmark"]

    outMap["l2"] = field_to_child["landmark2"]
    return outMap


def fieldToChild(rd_sdc, children, sdc_to_esdc):
    from routeDirectionCorpusReader import Annotation        
    field_to_child = dict([(key, [rd_sdc.annotationMap[key]])
                           for key in Annotation.keys])

    for key, value in field_to_child.iteritems():
        if value == "":
            field_to_child[key] = []

        field_to_child[key] = [s.ensureString() for s in value]
        field_to_child[key] = [x for x in field_to_child[key] 
                               if not (x.start == x.end)]
    for child in children:
        field = rd_sdc.fieldForChild(child)
        field_to_child[field] = [sdc_to_esdc[child]]

    for key, value in field_to_child.iteritems():
        if len(value) == 0:
            field_to_child[key] = None
    return field_to_child

class FlatEsdcExtractor:
    def __init__(self):
        self.extractor = crfEntityExtractor.SdcExtractor()

    def extractEsdcs(self, command):
        sdcs = self.extractor.chunk(command)
        return fromRouteDirectionSdc(sdcs)


def fromRouteDirectionSdc(sdcs):
    from routeDirectionCorpusReader import childrenMap, ancestorMap
    sdc_to_children = childrenMap(sdcs)
    sdc_to_esdc = {}

    i = 0

    while len(sdc_to_esdc) < len(sdcs):
        for parent, children in sdc_to_children.iteritems():
            if not parent in sdc_to_esdc:
                if all([child in sdc_to_esdc for child in children]):

                    esdcType = computeEsdcType(parent)                        
                    field_to_child = fieldToChild(parent, children,
                                                  sdc_to_esdc)
                    esdcFields = toEsdcFields(field_to_child)
                    sdc_to_esdc[parent] = ExtendedSdc(esdcType=esdcType,
                                                      **esdcFields)
        i += 1


    sdc_to_ancestors = ancestorMap(sdcs)

    esdcList = []
    for sdc in sdcs:
        if len(sdc_to_ancestors[sdc]) == 0:
            esdc = sdc_to_esdc[sdc]
            esdcList.append(esdc)

            #print sdc
            #print esdc
            #print
    objectifyLandmarks(esdcList)
    return ds.ExtendedSdcGroup(esdcList), sdc_to_esdc

        
