import yaml
from esdcs import esdcIo
import collections
from esdcs import groundings
from itertools import chain
import os
import traceback
import pickle_util
from esdcs.context import Context
from getpass import getuser

def fromYaml(corpusYaml, check=True):
    return Corpus([Annotation.fromYaml(entryMap) for entryMap in corpusYaml], check=check)

def toYaml(corpus):
    """
    Takes as list of annotations and writes it to yaml
    """
    return [annotation.toYaml() for annotation in corpus]


def pickleMemoize(loadFunction):
    def resultFunction(fname, check=True):
        if fname.endswith(".pck"):
            return pickle_util.load(fname)
        else:
            pickleFname = "/tmp/%s_%s.pck" % (getuser(),
                                              fname.replace("/", "_"))
                                              #os.path.basename(fname))

            if (os.path.exists(pickleFname) and
                os.path.getmtime(pickleFname) > os.path.getmtime(fname)):
                try:
                    print "loading", pickleFname, "...",
                    obj = pickle_util.load(pickleFname)
                    print "done"
                    return obj
                except:
                    print "ignoring, and reloading from yaml"
                    traceback.print_exc()
            print "loading", fname, "then will dump", pickleFname, "..."
            annotations = loadFunction(fname, check=check)
            pickle_util.save(pickleFname, annotations)
            print 'done'
            return annotations
    return resultFunction


def loadRaw(annotationFname, check=True):
    docIter = yaml.load_all(open(annotationFname), Loader=yaml.CLoader)
    corpus = fromYaml(docIter.next(), check=check)
    for annotation in corpus:
        annotation.fname = annotationFname
    return corpus

load = pickleMemoize(loadRaw)

def load_all(annotation_fnames, check=True):
    """
    Takes a list of filenames (strings) and loads them, returning a
    Corpus object.
    """
    annotations = []
    for corpus_fname in annotation_fnames:
        corpus = load(corpus_fname, check=check)
        annotations.extend(corpus)
    return Corpus(annotations, check=check)

def save_separate_files(corpus):
    fname_to_annotations = collections.defaultdict(lambda: list())
    for annotation in corpus:
        fname_to_annotations[annotation.fname].append(annotation)

    for fname, annotations in fname_to_annotations.iteritems():
        save(annotations, fname)


def save(corpus, annotationFname):
    """
    Saves a corpus (which is a list of annotations) to annotationFname
    """
    print "saving", annotationFname, "..."
    yaml.dump(toYaml(corpus), open(annotationFname, "w"),
              Dumper=yaml.CDumper)
    #pickleFname = "/tmp/%s.pck" % os.path.basename(annotationFname)
    #cPickle.dump(corpus, open(pickleFname, "wb"), protocol=2)
    print "done"

class Corpus:
    """
    Corpus of commands paired with ESDCs and groundings.
    """
    def __init__(self, annotations, check=True):
        self.annotations = list(annotations)

        self._id_to_annotation = dict((a.id, a) for a in self.annotations)
        self.esdcs = list(chain(annotation.esdcs
                                for annotation in self.annotations))
        self.flattenedEsdcs = list(chain(*[annotation.esdcs.flattenedEsdcs
                                         for annotation in self.annotations]))

        if len(self._id_to_annotation) != len(self.annotations) and check:
            ids = dict()
            for a in self.annotations:
                if a.id in ids:
                    old_annotation = ids[a.id]
                    raise ValueError("Annotation in set twice: " + a.id + " text: " + a.entireText +
                                     " old text: " + old_annotation.entireText)
                ids[a.id] = a
            raise ValueError("Should never get here")
    def text_to_annotations(self, text):
        """
        Return all annotations whose entireText field exactly equals text.
        """
        results = []
        for annotation in self.annotations:
            if text == annotation.entireText:
                results.append(annotation)
        return results

    def id_to_annotation(self, annotation_id):
        return self._id_to_annotation[annotation_id]

    def __iter__(self):
        return iter(self.annotations)

    def __len__(self):
        return len(self.annotations)
    def __getitem__(self, i):
        return self.annotations[i]

    def __eq__(self, obj):
        return (isinstance(obj,Corpus) and
                obj.annotations == self.annotations and
                obj.esdcs == self.esdcs)
    def __ne__(self, obj):
        return not (obj == self)

class Annotation:
    """
    A natural language command, paired with ESDCs and groundings.
    Each ESDC in the command has an associated grounding in the
    external world.  The context object contains all other relevant
    objects in the external world.
    """
    @staticmethod
    def copy(annotation):
        return Annotation.fromYaml(annotation.toYaml())

    def __init__(self, assignmentId, esdcs, objectGroundings=None,
                 groundingIsCorrect=None, agent=None, context=None,
                 esdcSource=None
                 ):
        """
        The ith grounding is mapped to the ith ESDC in breadth first
        traverse order.
        """
        self.assignmentId = assignmentId
        self.id = assignmentId


        self.entireText = esdcs.entireText
        self.esdcs = esdcs

        self.flattenedEsdcs = self.esdcs.flattenedEsdcs
        if objectGroundings == None:
            objectGroundings = [[] for esdc in self.flattenedEsdcs]
##### hack part 1 of 3: add in extra fields if esdcs have been modified after annotating
        # for i in range(len(self.flattenedEsdcs) - len(objectGroundings)):
        #     objectGroundings.append([])
        # if len(self.flattenedEsdcs) < len(objectGroundings):
        #     objectGroundings = objectGroundings[:len(self.flattenedEsdcs)]
##### end hack part 1
        if not len(objectGroundings) == len(self.flattenedEsdcs):
            print "len groundings", len(objectGroundings)
            print "len esdcs     ", len(self.flattenedEsdcs)
            print "esdcs"
            for e in self.flattenedEsdcs:
                print e
            print "text", self.entireText
            print "esdcs", self.esdcs
            raise ValueError("Object groundings must be same size as esdc list.")

        for o in objectGroundings:
            assert isinstance(o, list)
        self.esdcToGroundings = dict(zip(self.flattenedEsdcs, objectGroundings))


        if groundingIsCorrect == None:
            groundingIsCorrect = [None for esdc in self.flattenedEsdcs]
##### hack part 2 of 3: add in extra fields if esdcs have been modified after annotating
        # for i in range(len(self.flattenedEsdcs) - len(groundingIsCorrect)):
        #    groundingIsCorrect.append(None)
        # if len(self.flattenedEsdcs) < len(groundingIsCorrect):
        #     groundingIsCorrect = groundingIsCorrect[:len(self.flattenedEsdcs)]
##### end hack part 2
        assert len(groundingIsCorrect) == len(self.flattenedEsdcs), \
               (len(groundingIsCorrect), len(self.flattenedEsdcs))

        self.esdcToGroundingIsCorrect = dict(zip(self.flattenedEsdcs,
                                                 groundingIsCorrect))


##### hack part 3 of 3: add in extra fields if esdcs have been modified after annotating
        # for i in range(len(self.flattenedEsdcs) - len(esdcSource)):
        #     esdcSource.append(None)
        # if len(self.flattenedEsdcs) < len(esdcSource):
        #     esdcSource = esdcSource[:len(self.flattenedEsdcs)]
##### end hack part 3
        if esdcSource == None or esdcSource == [] or all([e == None for e in esdcSource]):
            esdcSource = [None for esdc in self.flattenedEsdcs]
            
        assert len(esdcSource) == len(self.flattenedEsdcs), \
            (len(esdcSource), len(self.flattenedEsdcs))
        self.esdcToSource = dict(zip(self.flattenedEsdcs,
                                     esdcSource))


        self.agent = agent
        self.priorAnnotation = None #if this is an annotation for a sequential ESDC, stores previous annotation
        if context == None:
            self.context = Context.from_groundings(chain(*objectGroundings))
        else:
            self.context = context

        if self.context.agent == None:
            self.context.agent = self.agent
        elif self.agent == None:
            self.agent = self.context.agent
        else:
            #assert self.context.agent == self.agent, (self.context.agent, self.agent)
            pass

        self.fname = None
        self.checkRep()
    def setContext(self, context):
        self.context = context

    def setAgent(self, agent):
        self.agent = agent

    @property
    def sources(self):
        return set(self.esdcToSource.values())

    def esdcsForSource(self, queried_source):
        esdcs = []
        for esdc, source in self.esdcToSource.iteritems():
            if queried_source == source:
                esdcs.append(esdc)
        return esdcs

    @property
    def groundings(self):
        return list(sorted(set(chain(*self.esdcToGroundings.values()))))

    def getGroundings(self, esdc):
        """
        Return the groundings associated with this ESDC.
        """
        return self.esdcToGroundings[esdc]

    def addGrounding(self, esdc, grounding):
        return self.esdcToGroundings[esdc].append(grounding)

    def setGrounding(self, esdc, grounding):
        if grounding != None:
            self.esdcToGroundings[esdc] = [grounding]

    def hasGroundings(self, esdc):
        return len(self.esdcToGroundings[esdc]) != 0


    def setGroundings(self, esdc, groundings):
        assert all(g != None for g in groundings)
        self.esdcToGroundings[esdc] = groundings


    def isGroundingCorrect(self, esdc):
        """
        Whether the grounding associated with this esdc is known to be
        correct or incorrect. (e.g., is it a positive or negative
        example?)
        """
        return self.esdcToGroundingIsCorrect[esdc]

    def setGroundingIsCorrect(self, esdc, value):
        assert value in [True, False, None], value
        self.esdcToGroundingIsCorrect[esdc] = value


    def getSource(self, esdc):
        """
        Returns a string denoting the source of the ESDC.  e.g.,
        "human 1" or "human 2"
        """
        return self.esdcToSource[esdc]


    def setSource(self, esdc, source):
        """
        Returns a string denoting the source of the ESDC.  e.g.,
        "human 1" or "human 2"
        """
        self.esdcToSource[esdc] = source


    def removeAllGroundings(self, esdc):
        self.esdcToGroundings[esdc] = []

    def emptyGroundings(self):
        for esdc, value in self.esdcToGroundings.iteritems():
            if value != []:
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, Annotation):
            return False
        for key in ["assignmentId", "entireText", "esdcs", "esdcToGroundings"]:
            if self.__dict__[key] != other.__dict__[key]:
                return False
        return True
    def __repr__(self):
        return "Annotation(%s)" % repr(self.toYaml())

    def toYaml(self):
        self.checkRep()
        yamlData = {}

        yamlData['assignmentId'] = self.assignmentId
        yamlData['command'] = esdcIo.toYaml(self.esdcs)
        if self.agent != None:
            yamlData['agent'] = self.agent.toYaml()

        if self.context != None:
            yamlData['context'] = self.context.toYaml()

        try:
            g = [groundings.toYaml(self.esdcToGroundings[esdc])
                 for esdc in self.flattenedEsdcs]
        except KeyError:
            print esdc
            raise


        if any(len(x) != 0 for x in g):
            yamlData['objectGroundings'] = g
            yamlData['groundingIsCorrect'] = [self.isGroundingCorrect(e)
                                              for e in self.flattenedEsdcs]
        yamlData['source'] = [self.getSource(e)
                              for e in self.flattenedEsdcs]


        return yamlData

    @staticmethod
    def fromYaml(yamlData):
        entireText, esdcsYaml = yamlData['command']
        try:
            yamlGroundings = yamlData.get('objectGroundings')
            if yamlGroundings != None:
                g = [groundings.fromYaml(grounding)
                     for grounding in yamlGroundings]
            else:
                g = None

            groundingIsCorrect = yamlData.get('groundingIsCorrect')
            source = yamlData.get("source")

            if 'context' in yamlData:
                context = Context.fromYaml(yamlData['context'])
            else:
                context = None
            return Annotation(yamlData['assignmentId'],
                              esdcIo.fromYaml(entireText, esdcsYaml, use_ids=True),
                              g,
                              groundingIsCorrect,
                              groundings.PhysicalObject.fromYaml(yamlData.get('agent')),
                              context, source
                              )


        except:
            print "couldn't make esdcs", entireText
            raise

    def checkRep(self):
        assert all([esdc.entireText == self.entireText for esdc in self.esdcs])

        for esdc in self.flattenedEsdcs:
            assert esdc in self.esdcToGroundings, (str(esdc))

