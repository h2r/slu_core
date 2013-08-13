from esdcs.dataStructures import breadthFirstTraverse, ExtendedSdc
import re
from yamlReader import isWordList

import yaml


def keyFunction():
    # Prioritizes certain keys when sorting.
    keyDict = dict((key, i) for i, key in enumerate(ExtendedSdc.fieldNames))

    def function((key, value)):
        return keyDict.get(key, 99)
    return function


def representDict(self, data):
    items = data.items()
    items.sort(key=keyFunction())
    return self.represent_mapping(u'tag:yaml.org,2002:map', items)

# make keys output in field name order instead of alphabetical.
yaml.add_representer(dict, representDict)


def toYaml(esdcs):
    """
    Converts the ESDCs to y
    and converts
    them to python classes that can be dumped to yaml with yaml.dump
    """

    entireText = esdcs.entireText

    unlinkedMap = buildUnlinkedMap(esdcs)

    def callback(esdc):

        esdcMap = unlinkedMap[esdc]

        if isinstance(esdcMap, str):
            return
        fieldMap = esdcMap[esdc.type]
        for fieldName in esdc.fieldNames:
            if esdc.childIsEsdcs(fieldName):

                if len(esdc[fieldName]) == 1 and esdc[fieldName][0].isLeafObject():
                    fieldMap[fieldName] = makeFieldString(esdc.entireText, esdc[fieldName][0].f)
                else:
                    fieldMap[fieldName] = [unlinkedMap[child]
                                            for child in esdc[fieldName]]
                if len(fieldMap[fieldName]) == 1 and not isWordList(fieldMap[fieldName]):
                    fieldMap[fieldName] = fieldMap[fieldName][0]

                if fieldMap[fieldName] == "":
                    del fieldMap[fieldName]
    breadthFirstTraverse(esdcs, callback)
    # now unlinked map is linked
    esdcList = [unlinkedMap[esdc] for esdc in esdcs]

    return [entireText, esdcList]


def makeFieldString(entireText, listOfStandoffs):
    fieldSubstring = " ".join(w.text for w in listOfStandoffs)

    try:
        matches = list(re.finditer(re.escape(fieldSubstring), entireText))
    except:
        print "field", fieldSubstring
        print "entire text", entireText
        raise

    if fieldSubstring == "" or (len(matches) == 1 and matches[0].start() == listOfStandoffs[0].start and matches[0].end() == listOfStandoffs[-1].end):
        return fieldSubstring
    else:
        return [[w.text, list(w.range)] for w in listOfStandoffs]


def buildUnlinkedMap(esdcs):
    resultMap = {}

    def callback(esdc):
        esdcMap = {}
        for fieldName in esdc.fieldNames:
            if esdc.childIsListOfWords(fieldName):
                fieldSubstring = makeFieldString(esdc.entireText,
                                                 esdc[fieldName])
                esdcMap[fieldName] = fieldSubstring

        resultMap[esdc] = {esdc.type: esdcMap}
        if esdc.id != None:
            resultMap[esdc]["id"] = esdc.id

    breadthFirstTraverse(esdcs, callback)
    return resultMap
