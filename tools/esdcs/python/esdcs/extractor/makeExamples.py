from itertools import chain
import jvm
from esdcs.dataStructures import ExtendedSdc
import jpype
import nltk
import numpy as na
p_mallet = jpype.JPackage("cc.mallet")
mt = p_mallet.types

def makeDataAlphabet(corpus):
    """
    Make alphabet of features using all words that appear more than once.
    """
    words = wordFeatures(corpus)
    alphabet = []


    for word in words:
        for fieldName in ExtendedSdc.fieldNames:
            alphabet.append("wordAppearsInField(%s, %s)" % (repr(word), repr(fieldName)))

            for esdcType in ExtendedSdc.types:
                alphabet.append("wordAppearsInFieldWithEsdcType(%s, %s, %s)"
                                % (repr(word), repr(fieldName), repr(esdcType)))

    return mt.Alphabet(alphabet)

        

def wordFeatures(corpus):
    """
    Return a list of all the feature names, using all words in the
    corpus that appear more than once.
    """

    wordHist = nltk.probability.FreqDist()
    for annotation in corpus.annotations:
        tokens = annotation.entireText.split()
        for token in tokens:
            wordHist.inc(token.lower())

    print wordHist.N(), "words."
    print wordHist.B(), "unique words."

    wordsThatOccurOnce = wordHist.hapaxes()
    featureWords = [w for w in wordHist.keys() if not w in wordsThatOccurOnce]
    print len(featureWords), "words used in features"
    return featureWords


class ExampleMaker:

    @staticmethod
    def fromCorpus(goldStandardCorpus):
        dataAlphabet = makeDataAlphabet(goldStandardCorpus)

        targetAlphabet = mt.LabelAlphabet()
        return ExampleMaker(dataAlphabet, targetAlphabet)
    
    """
    Makes examples from the top N of the parser, on the fly.
    """
    def __init__(self, dataAlphabet, targetAlphabet=None):
        self.dataAlphabet = dataAlphabet
        self.featureNameToIdx = dict([(self.dataAlphabet.lookupObject(i), i)
                                      for i in range(self.dataAlphabet.size())])

        if targetAlphabet == None:
            targetAlphabet = mt.LabelAlphabet()
        self.targetAlphabet = targetAlphabet
        self.trueLabel = self.targetAlphabet.lookupLabel("True",
                                                         addIfNotPresent=True)
        self.falseLabel = self.targetAlphabet.lookupLabel("False",
                                                          addIfNotPresent=True)

        self.unkLabel = self.targetAlphabet.lookupLabel("Unknown",
                                                        addIfNotPresent=True)
        
        self.rankedTargetAlphabet = mt.LabelAlphabet()
        self.zeroLabel = self.rankedTargetAlphabet.lookupLabel("0",
                                                    addIfNotPresent=True)

    def corpusToInstanceList(self, corpus):
        labeledExamples = self.makeExamples(corpus)
        return self.makeInstances(labeledExamples)




        
    def makeRankedInstanceList(self, goldStandardCorpus):
        from stanfordParserExtractor import Extractor
        extractor = Extractor()

        instances = mt.InstanceList(self.dataAlphabet, self.rankedTargetAlphabet)
        
        for annotation in goldStandardCorpus.annotations:
            instance, esdcGroups = self.makeRankedInstance(annotation.entireText,
                                                           extractor, 10,
                                                           annotation.esdcs)
            instances.add(instance)
        return instances

    def makeRankedInstance(self, command, extractor, n, correctEsdcGroup=None):
        automaticEsdcGroups = [e for e in extractor.extractTopNEsdcsFromSentence(command, n=n) if len(e) != 0]
        fvecs = []
        if correctEsdcGroup != None:
            esdcGroups = [correctEsdcGroup] + automaticEsdcGroups
        else:
            esdcGroups = automaticEsdcGroups
                
        for esdcGroup in esdcGroups:
            fvec = self.esdcGroupToFeatures(esdcGroup)
            vector = mt.FeatureVector(self.dataAlphabet, fvec)
            fvecs.append(vector)
        fvecSequence = mt.FeatureVectorSequence(fvecs)            
        return mt.Instance(fvecSequence, self.zeroLabel,
                           command[0:10],
                           command), esdcGroups

        
        
    def makeExamples(self, goldStandardCorpus):
        from stanfordParserExtractor import Extractor
        extractor = Extractor()

        negativeExamples = []
        positiveExamples = list(chain(*[a.esdcs
                                        for a in goldStandardCorpus.annotations]))

        for annotation in goldStandardCorpus.annotations:
            esdcGroups = extractor.extractTopNEsdcsFromSentence(annotation.entireText, n=10)
            for esdcGroup in esdcGroups:
                for esdc in esdcGroup:
                    if not esdc in annotation.esdcs:
                        negativeExamples.append(esdc)
        print len(positiveExamples), "positive examples."
        print len(negativeExamples), "negative examples."
        return ([(e, self.trueLabel) for e in positiveExamples] +
                [(e, self.falseLabel) for e in negativeExamples])
        
        

        
    def makeInstance(self, esdc, target=None):
        if target is None:
            target = self.unkLabel
        fvec = self.esdcToFeatures(esdc)
        vector = mt.FeatureVector(self.dataAlphabet, fvec)
        return mt.Instance(vector,
                           target,
                           esdc.entireText[0:10],
                           esdc.entireText)

    

    def makeInstances(self, labeledExamples):
        instances = mt.InstanceList(self.dataAlphabet, 
                                    self.targetAlphabet)
        for i, (esdc, label) in enumerate(labeledExamples):
            instances.add(self.makeInstance(esdc, label))
            if i % 100 == 0 and i != 0:
                print i, "of", len(labeledExamples)
                #break
        return instances



        
        
    def esdcGroupToFeatures(self, esdcGroup):
        fvec = na.zeros(len(self.featureNameToIdx))
        for esdc in esdcGroup:
            fvec += self.esdcToFeatures(esdc)
        return fvec
    
    def esdcToFeatures(self, esdc):

        values = na.zeros(len(self.featureNameToIdx))

        for fieldName in esdc.fieldNames:
            for childToken in esdc.childTokens(fieldName):
                word = childToken.text
                featureName = "wordAppearsInField(%s, %s)" % (repr(word), repr(fieldName))
                if featureName in self.featureNameToIdx:
                    values[self.featureNameToIdx[featureName]] = 1
                featureName = "wordAppearsInFieldWithEsdcType(%s, %s, %s)" % (repr(word), repr(fieldName), repr(esdc.type))
                if featureName in self.featureNameToIdx:
                    values[self.featureNameToIdx[featureName]] = 1
        return values


                
    def trainClassifier(self, corpus):
        labeledExamples = self.makeExamples(corpus)
        instances = [None]
        def training():
            instances[0] = self.makeInstances(labeledExamples)

        import cProfile
        cProfile.runctx("training()", globals(), locals(), "profile.out")
        instances = instances[0]
        
        trainer = p_mallet.classify.MaxEntL1Trainer()
        return trainer.train(instances)
