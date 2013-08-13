from standoff import TextStandoff
import numpy as na
from hash_utils import fasthash
import yaml


def all_object_arguments(esdc):
    for key in ExtendedSdc.fieldNames:
        if esdc.childIsEsdcs(key):
            for child in esdc.children(key):
                if child.type != "OBJECT":
                    return False
    return True


def contains(r1, r2):
    s1, e1 = r1
    s2, e2 = r2
    if s1 <= s2 and e2 <= e1:
        return True
    else:
        return False


def proper_contains(r1, r2):
    s1, e1 = r1
    s2, e2 = r2
    if ((s1 <= s2 and e2 < e1) or
        (s1 < s2 and e2 <= e1)):
        return True
    else:
        return False


def equal(esdc1, esdc2, visited=[]):

    if esdc1 is esdc2:
        return True

    if not isinstance(esdc1, ExtendedSdc):
        return False

    if not isinstance(esdc2, ExtendedSdc):
        return False

    if esdc1.id != esdc2.id:
        return False

    if esdc1.type != esdc2.type:
        return False

    if esdc1.range != esdc2.range:
        return False

    if esdc1.entireText != esdc2.entireText:
        return False

    for key in esdc1.fieldNames:
        if not esdc1.childIsEsdcs(key):
            if esdc1.children(key) != esdc2.children(key):
                return False

    for v in visited:
        if esdc1 is v and not esdc2 is v:
            return False

    for key in esdc1.fieldNames:
        if esdc1.childIsEsdcs(key):
            if not esdc2.childIsEsdcs(key):
                return False
            if len(esdc1.children(key)) != len(esdc2.children(key)):
                return False

            for c1, c2 in zip(esdc1.children(key), esdc2.children(key)):
                if not equal(c1, c2, visited + [esdc1, esdc2]):
                    return False

    return True

def leavesToRoot(esdcs):
    fesdcs = flattenedEsdcs(esdcs)

    return flattenedEsdcs



def null_ids(esdcs):
    def callback(esdc):
        esdc.id = None
    breadthFirstTraverse(esdcs, callback)

def flattenedEsdcs(esdcs):
    flattenedEsdcs = []
    def callback(esdc):
        flattenedEsdcs.append(esdc)
    breadthFirstTraverse(esdcs, callback)
    return flattenedEsdcs

def updateRep(esdcs):
    def callback(esdc):
        esdc.updateRep()
    breadthFirstTraverse(esdcs, callback)

def freeze(esdcs):
    def callback(esdc):
        esdc.freeze()
    updateRep(esdcs)
    breadthFirstTraverse(esdcs, callback)


def unfreeze(esdcs):
    def callback(esdc):
        esdc.unfreeze()
    breadthFirstTraverse(esdcs, callback)
    updateRep(esdcs)


def isLeafObject(esdc):
    """
    Returns true if the object is a leaf node, false otherwise.
    """
    return (esdc.type == "OBJECT" and
            all(esdc.childIsEmpty(c) for c in ["l", "l2", "r"]))


def isLeafPath(esdc):
    """
    Returns true if the path is a leaf node, false otherwise.
    """
    return (esdc.type == "PATH" and
            all(esdc.childIsEmpty(c) for c in ["l", "l2", "r"]))


def objectifyLandmarks(esdcs):
    """
    Wrap landmarks in OBJECT esdcs
    """
    def callback(esdc):
        for lkey in ["l", "l2", "f"]:

            if esdc.childIsListOfWords(lkey) and not isLeafObject(esdc):

                esdc.setChild(lkey, ExtendedSdc("OBJECT",
                                                f=esdc.children(lkey)))
    breadthFirstTraverse(esdcs, callback)



def objectifyFiguresOfEvents(esdcs):
    """
    Make sure that figures of events are always wrapped in OBJECTs
    """
    def callback(esdc):
        if esdc.type == "EVENT":
            for fkey in ["f"]:
                if esdc.childIsListOfWords(fkey):
                    esdc.setChild(fkey, ExtendedSdc("OBJECT",
                                                    f=esdc.children(fkey)))
    breadthFirstTraverse(esdcs, callback)


def addEmptyFigures(esdcs):
    """
    Make an empty OBJECT ESDC if the figure field is empty.
    """
    def callback(esdc):
        if esdc.type == "EVENT":
            if esdc.childIsEmpty("f"):
                esdc.f = ExtendedSdc("OBJECT", entireText=esdc.entireText)

    breadthFirstTraverse(esdcs, callback)


def _getEntireText(esdcs, entireText=None):
    entireTextLst = [entireText]
    def callback(esdc):
        if entireTextLst[0] == None:
            entireTextLst[0] = esdc.entireText
        else:
            assert entireTextLst[0] == esdc.entireText, entireTextLst

    breadthFirstTraverse(esdcs, callback)
    return entireTextLst[0]

def breadthFirstTraverse(esdcs, callback):
    activeSet = list(wrapValueInList(esdcs))
    visitedIds = list()
    while len(activeSet) != 0:
        esdc = activeSet.pop(0)
        if id(esdc) in visitedIds and not esdc.isEmpty():
            continue
            pass
        else:
            visitedIds.append(id(esdc))

        for fieldName in esdc.fieldNames:
            if esdc.childIsEsdcs(fieldName):
                for child in esdc.children(fieldName):
                    activeSet.append(child)
        callback(esdc)
    return


def parentsToChildren(esdcs):
    """
    Returns flattened ESDCs with the guarantee that all parents will
    appear before their children
    """
    flattened_esdcs = []
    def callback(esdc):
        flattened_esdcs.append(esdc)

    depthFirstTraverse(esdcs, callback)
    return flattened_esdcs

def depthFirstTraverse(esdcs, callback):
    activeSet = list(wrapValueInList(esdcs))
    while len(activeSet) != 0:
        esdc = activeSet.pop()
        for fieldName in ExtendedSdc.fieldNames:
            if esdc.childIsEsdcs(fieldName):
                for child in esdc.children(fieldName):
                    activeSet.append(child)
        callback(esdc)
    return





def makeProperty(key):
    def getx(self):
        return self.fields[key]
    def setx(self, x):
        self.setChild(key, x)
    return property(getx, setx)

def wrapValueInList(value):
    if isinstance(value, list):
        return value
    elif isinstance(value, tuple):
        return list(value)
    elif value == None:
        return []
    elif isinstance(value, ExtendedSdcGroup):
        return list(value)
    else:
        return [value]


class ExtendedSdcGroup(object):
    """
    Represents a group of multiple ESDCS.  If use_ids is True, it will
    set the id field of the child sdcs to the breadth-first traversal
    order.  Otherwise, the id fields of SDCs are null.

    """
    @staticmethod
    def copy(esdcs):
        return ExtendedSdcGroup([ExtendedSdc.copy(e) for e in esdcs],
                                score=esdcs.score, metadata=esdcs.metadata)




    def __init__(self, esdcs, entireText=None, score=na.nan, metadata=None,
                 use_ids=False):
        freeze(esdcs)
        self.esdcs = list(sorted(esdcs))
        self.score = score
        self.metadata = metadata

        self.entireText = _getEntireText(esdcs, entireText)


        assert self.entireText != None, (esdcs, entireText)


        self.flattenedEsdcs = []

        def callback(esdc):
            self.flattenedEsdcs.append(esdc)
        breadthFirstTraverse(self.esdcs, callback)

        if use_ids:
            for i, esdc in enumerate(self.flattenedEsdcs):
                assert esdc.id == None
                esdc.id = i


        self.start = len(self.entireText)
        self.end = 0
        for esdc in self.flattenedEsdcs:
            start, end = esdc.range
            if start == 0 and end == 0:
                continue
            if start < self.start:
                self.start = start
            if end > self.end:
                self.end = end
        self.range = self.start, self.end

        self.updateText()
        self.hash_string = "_".join(esdc.hash_string for esdc in self.esdcs)


    def hasCycle(self):
        for esdc in self:
            if esdc.hasCycle():
                return True
        return False
    def updateText(self):
        self.text = self.entireText[self.start:self.end]

    def asPrettyMap(self):
        return [esdc.asPrettyMap() for esdc in self.esdcs]

    def updateRep(self):
        def callback(esdc):
            esdc.updateRep()
        breadthFirstTraverse(self.esdcs, callback)

    def contains(self, esdc2):
        """
        If self contains esdc.
        """
        return contains(self.range, esdc2.range)

    def proper_contains(self, esdc2):
        """
        If self contains and is not equal to esdc.
        """
        return proper_contains(self.range, esdc2.range)

    def __len__(self):
        return len(self.esdcs)

    def __iter__(self):
        return self.esdcs.__iter__()

    def __getitem__(self, i):
        return self.esdcs[i]
    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(repr(self))


    def __eq__(self, other):
        if not isinstance(other, ExtendedSdcGroup):
            return False
        for key in ["entireText", "esdcs"]:
            try:
                if self.__dict__[key] != other.__dict__[key]:
                    return False
            except:
                print "self", self
                print "other", other
                print "self", self.entireText
                print "other", other.entireText
                print "self", self.score
                print "other", other.score
                raise

        return True
    #self.esdcs == other.esdcs and self.entireText == other.entireText
    def __repr__(self):
        return ("ExtendedSdcGroup(%s, %s)" % (
            repr(self.esdcs), repr(self.entireText)))

class ExtendedSdc(object):

    """ Class to hold extended SDCs. It consists of a list of children
    for the fields for figure, relation, landmark, and landmark2.  The
    contents of the children has to be either a list of TextStandoffs,
    or a list of ExtendedSdcs for the same underlying text.
    """

    fieldNames = ['f', 'r', 'l', 'l2']
    types = ["EVENT","PATH", "PLACE", "OBJECT"]
    fieldNamesToDescriptions = {'f':'figure', 'r':'relation', 'l':'landmark', 'l2':'landmark2'}

    for key in fieldNames:
        exec("%s = makeProperty(\"%s\")" % (key, key))

    @staticmethod
    def copy(esdc, id_to_copy = None):

        if id_to_copy == None:
            id_to_copy = {}
        if id(esdc) in id_to_copy:
            return id_to_copy[id(esdc)]

        fields = dict(esdc.fields)
        for key, value in fields.iteritems():
            if esdc.childIsEsdcs(key):
                fields[key] = [ExtendedSdc.copy(e, id_to_copy) for e in value]
            else:
                fields[key] = list(value)


        result = ExtendedSdc(esdcType=esdc.type,
                             entireText=esdc.entireText,
                             **fields)
        id_to_copy[id(esdc)] = result

        return result

    def __init__(self, esdcType=None, entireText=None, esdc_id=None, **args):
        """
        When constructing ESDCs, you can pass in children as either a
        list or a single class of one of the two types.  It will
        automatically wrap it in a list.
        """
        self.type = esdcType
        self.fields = dict([(key, wrapValueInList(values))
                            for key, values in args.iteritems()])
        # for field in self.fields:
        #     print "ESDC got field:", field
        #     print "with values:", self.fields[field]
        # print "\n"
        for key in self.fields.keys():
            assert key in ExtendedSdc.fieldNames, key

        self.entireText = entireText
        for key, values in self:
            for value in values:
                if self.entireText == None:
                    self.entireText == value.entireText
                else:
                    assert self.entireText == value.entireText, \
                        (key, value, self.entireText, value.entireText)



        for key in self.fieldNames:
            self.fields.setdefault(key, [])


        self.updateRep()

        self.frozen = False
        self.id = esdc_id



    def freeze(self):
        self.updateRep()
        self.frozen = True

    def unfreeze(self):
        self.updateRep()
        self.frozen = False


    def contains(self, esdc2):
        """
        If self contains esdc.
        """
        return contains(self.range, esdc2.range)

    def proper_contains(self, esdc2):
        """
        If self contains and is not equal to esdc.
        """
        return proper_contains(self.range, esdc2.range)

    def children(self, fieldName):
        return self.fields[fieldName]

    def __getitem__(self, fieldName):
        return self.children(fieldName)

#    @MemoizeInstance
    def childLowercaseWordSet(self, fieldName):
        return set(w.text.lower() for w in self.childTokens(fieldName))

    def childText(self, fieldName):
        """
        Get the string value of the field, walkign down the tree.
        """
        return " ".join(t.text for t in self.childTokens(fieldName))

    def childTokens(self, fieldName):
        """
        Get all the child tokens for the field, walking down the tree.
        """
        if self.childIsListOfWords(fieldName):
            return self.children(fieldName)
        else:
            tokens = []
            def callback(esdc):
                for key in esdc.fieldNames:
                    if esdc.childIsListOfWords(key):
                        tokens.extend(esdc.children(key))
            breadthFirstTraverse(self.children(fieldName), callback)
            return tokens




    def setChild(self, key, value):
        assert key in self.fieldNames
        assert not self.frozen, str(self)
        self.fields[key] = wrapValueInList(value)

    def isEmpty(self):
        return all(len(self[f]) == 0 for f in self.fieldNames)

    def isLeafObject(self):
        """
        Test whether this ESDC is an OBJECT esdc with only the figure
        field populated.
        """
        return (all(self.childIsEmpty(fieldName)
                    for fieldName in self.fieldNames if fieldName != "f")
                and self.type == "OBJECT")

    def isLeaf(self):
        """
        Test whether this ESDC is an OBJECT esdc with only the figure
        field populated.
        """
        return (all(self.childIsEmpty(fieldName)
                    for fieldName in self.fieldNames if fieldName != "f"))
              


    def isLeafPath(self):
        """
        Test whether this ESDC is a PATH esdc with only the figure
        field populated.
        """
        return (all(self.childIsEmpty(fieldName)
                    for fieldName in self.fieldNames if fieldName != "f")
                and self.type == "PATH")


    def childIsLeafObject(self, child):
        return (self.childIsEsdcs(child) and
                all([isLeafObject(x) for x in self.fields[child]]))
    def childIsEsdcs(self, child):
        # print "child", child
        # for x in self.fields[child]:
        #     print x
        #     print x.__class__
        #     print isinstance(x, ExtendedSdc)
        return (all([isinstance(x, ExtendedSdc)
                     for x in self.fields[child]])
                and self.fields[child] != [])


    def childIsListOfWords(self, child):
        # safe
        #return (all(isinstance(x, TextStandoff)
        #            for x in self.fields[child])
        #        and self.fields[child] != [])
        # faster
        return (self.fields[child] != [] and
                isinstance(self.fields[child][0], TextStandoff))


    def childIsEmpty(self, child):
        return self.fields[child] == []

    def checkRep(self):
        assert all([key in ExtendedSdc.fieldNames for key in self.fields.keys()]), self.fields.keys()
        assert self.type in ExtendedSdc.types or self.type == None, self.type

        for key, values in self:
            for value in values:
                assert self.entireText == value.entireText, (self.entireText,value.entireText)


    def updateRep(self):
        if not hasattr(self, "frozen"):
            self.frozen = False
        for key, values in self:
            for value in values:
                if self.entireText == None:
                    self.entireText = value.entireText
                else:
                    assert self.entireText == value.entireText, (self.entireText, value.entireText, key, str(value), [str(x) for x in values])

            self.fields[key] = sorted(values, key=lambda x: x.range[0])

        minRange = len(self.entireText)
        maxRange = 0
        for key, values in self:
            for value in values:
                minValueRange, maxValueRange = value.range
                if minValueRange < minRange:
                    minRange = minValueRange
                if maxValueRange > maxRange:
                    maxRange = maxValueRange
        self.range = minRange, maxRange
        self.startIdx = minRange;
        self.endIdx = maxRange
        self.text = self.entireText[self.startIdx:self.endIdx]
        self.flattenedEsdcs = flattenedEsdcs([self])
        self.checkRep()
        self._repr = self.recomputeRepr()
        self._hash = hash(self._repr)
        self.hash_string = fasthash(self._repr)

        self.standoff = TextStandoff(self.entireText, self.range)


    def __iter__(self):
        return self.fields.iteritems()

    def __eq__(self, obj):
        # if isinstance(obj, ExtendedSdc):
        #     return (self.type == obj.type and self.entireText == obj.entireText
        #             and all([self.fields[key] == obj.fields[key]
        #                      for key in ExtendedSdc.fieldNames]))
        # else:
        #     return False
        return equal(self, obj)

    def __ne__(self, other):
        return not self == other

    def standoffs(self):
        result = []
        for key, values in self:
            if self.childIsListOfWords(key):
                result.extend(values)
            elif self.childIsEsdcs(key):
                for child in values:
                    result.extend(child.standoffs())
            else:
                assert self.childIsEmpty(key)
        return result


    def __hash__(self):
#        if not self.frozen:
#            raise ValueError("Must freeze before hashing: " + str(self))
#        else:
            return self._hash
        #return hash(repr(self))

    def __repr__(self):
        return self._repr
        #return self.recomputeRepr()

    def recomputeRepr(self):
        result =  (self.__class__.__name__ + "(" + repr(self.type) + ", " +
                   ",".join("%s=%s" % (key, repr(value))
                            for key, value in self))
        if self.isEmpty():
            result += ', entireText=' + repr(self.entireText)
        result += ")"
        return result

    def __str__(self):
        return ", ".join(["%s=%s" % (key, " ".join([value.text
                                                    for value in self[key]]))
                          for key in self.fieldNames])

    def __cmp__(self, other):
        if self == other:
            return 0
        elif isinstance(self, ExtendedSdc):
            s1, e1 = self.range
            s2, e2 = other.range
            if s1 != s2:
                return cmp(s1, s2)
            elif e1 != e2:
                return cmp(e1, e2)
            elif repr(self) != repr(other):
                return cmp(repr(self), repr(other))
            else:
                print s1, e1
                print s2, e2
                raise ValueError("Couldn't cmp: " + str(self) + " " + str(other))


        else:
            raise ValueError("Must cmp an ExtendedSdc: "  + `other`)


    def asPrettyMap(self):
        outList = []
        for key, values in self:
            outValueList = []
            for value in values:
                if isinstance(value, TextStandoff):
                    outValueList.append(value.text)
                elif isinstance(value, ExtendedSdc):
                    outValueList.append(value.asPrettyMap())
                else:
                    raise ValueError("Unexpected type: " + `value` + " class: " + str(value.__class__))
                outList.append((key, outValueList))
        return {self.type: dict(outList)}


    def isAncestor(self, esdc):
        if esdc != self and esdc in flattenedEsdcs(self):
            return True
        else:
            return False

    def isParent(self, esdc):
        for key in ExtendedSdc.fieldNames:
            if self.childIsEsdcs(key):
                for child in self.children(key):
                    if child == esdc:
                        return True
        return False

    def hasCycle(self):
        activeSet = [self]
        visitedNodes = list()
        while len(activeSet) != 0:
            esdc = activeSet.pop(0)
            if esdc in visitedNodes and not esdc.isEmpty():
                return True
            else:
                visitedNodes.append(esdc)
            for fieldName in self.fieldNames:
                if esdc.childIsEsdcs(fieldName):
                    for child in esdc.children(fieldName):
                        activeSet.append(child)
        return False

    def is_same_constituent(self, other):
        """
        Designed for comparing ESDCs created by different parsing systems. This
        checks if two ESDCs represent the same linguistic constituent. What that
        means here is that they must have the same entireText and range values,
        but they may have different child structures.
        """
        # print "Comparing these two esdcs:"
        # print yaml.dump(self.asPrettyMap())
        # print yaml.dump(other.asPrettyMap())
        # print [x.entireText for x in [self, other]]
        # print [x.range for x in [self, other]]
        # print "Returning", self.entireText == other.entireText and self.range == other.range
        # return self.range == other.range and self.text == other.text
        # return self.entireText == other.entireText and self.range == other.range
        return self.range == other.range and self.text == other.text and (self.entireText in other.entireText or other.entireText in self.entireText)


def isTopLevel(esdc, esdcs):
    for possibleParent in esdcs:
        if possibleParent.isAncestor(esdc):
            return False
    return True


def makeConstructorFunctions():
    for esdcType in ExtendedSdc.types:
        def function(**args):
            return ExtendedSdc(esdcType, **args)

        globals()[esdcType]=function

makeConstructorFunctions()
