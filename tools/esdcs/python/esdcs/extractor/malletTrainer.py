import pylab as mpl
import sys
import os
import jpype
import numpy as na
from esdcs.esdcIo import annotationIo
import makeExamples
p_classify = jpype.JPackage("cc.mallet.classify")
p_mallet = jpype.JPackage("cc.mallet")
java = jpype.JPackage("java")

def saveObject(obj, outputFname):
    oos = java.io.ObjectOutputStream(java.io.FileOutputStream(outputFname))
    oos.writeObject(obj)
    oos.close()

def loadClassifier(inputFname):
    """
    Load the classifier.  Jpype is sad with deserializing from python
    directly.  It works for simple types, but not for the classifier.
    I think it has something to do with the classloader.  Calling it
    from a class which has the Classifier stuff imported directly
    seems to fix it.
    """
    #print 'classpath', java.lang.System.getProperty("java.class.path")
    pkg = jpype.JPackage("edu.mit.csail.spatial")
    return pkg.esdcs.LoadClassifier.load(inputFname)

    

class Trainer:

    def trainAndPlotReranker(self, corpus):
        training = annotationIo.Corpus(corpus[0:75])
        testing = annotationIo.Corpus(corpus[75:])
        exampleMaker = makeExamples.ExampleMaker.fromCorpus(training)

        trainingInstances = exampleMaker.makeRankedInstanceList(training)
        testingInstances = exampleMaker.makeRankedInstanceList(testing)

        trainer = p_mallet.classify.RankMaxEntTrainer()

        try:
            classifier = trainer.train(trainingInstances)
        except:
            cls, obj, tb =  sys.exc_info()
            print obj
            print obj.__dict__
            obj.__javaobject__.printStackTrace()
            raise
            

        trial = p_mallet.classify.Trial(classifier, testingInstances)
        
        print "accuracy", trial.getAccuracy()
        saveObject(classifier, "data/classifierReranker.ser")
        
    def trainAndPlot(self, corpus):
        training = annotationIo.Corpus(corpus[0:75])
        testing = annotationIo.Corpus(corpus[75:])
        exampleMaker = makeExamples.ExampleMaker.fromCorpus(training)
        classifier = exampleMaker.trainClassifier(training)
    

        trueLabel = exampleMaker.trueLabel
        falseLabel = exampleMaker.falseLabel

        testingInstances = exampleMaker.corpusToInstanceList(testing)

        trial = p_mallet.classify.Trial(classifier, testingInstances)
        print "accuracy", trial.getAccuracy()
        print "precision", trial.getPrecision(trueLabel.getIndex())
        print "recall", trial.getRecall(trueLabel.getIndex())
        print "f1", trial.getF1(trueLabel.getIndex())
        trueI = trueLabel.getIndex()
        falseI = falseLabel.getIndex()
        print "i", trueI, falseI
        
        labels = [trueLabel, falseLabel]
        X = []
        Y = []
        for threshold in na.arange(0, 1, 0.1):
            cm = na.zeros((len(labels), len(labels))) + 0.0
            for classification in trial:

                trueScore = classification.getLabelVector().value(trueLabel)

                cls = trueLabel if trueScore > threshold else falseLabel
                #print "trueScore", trueScore, cls                

                correctLabel = classification.getInstance().getTarget()
                cm[correctLabel.getIndex(), cls.getIndex()] += 1

            #precision = cm[trueI, trueI] / na.sum(cm[:, trueI])
            recall = cm[trueI, trueI] / na.sum(cm[trueI, :])
            fpr = cm[falseI, trueI] / na.sum(cm[falseI, :])
            X.append(fpr)
            Y.append(recall)


        mpl.plot(X, Y)
        mpl.xlabel("FP", fontsize=25)
        mpl.ylabel("TP", fontsize=25)
        mpl.xlim(0,1.1)
        mpl.ylim(0,1.1)
        mpl.title("Classifying Correct vs Incorrect ESDC Parses")
        saveObject(classifier, "data/classifier.ser")
        mpl.show()
            
            
        

def main():
    trainer = Trainer()
    #dirName = "%s/tools/forklift/dataAnnotation/data"  % os.environ["SLU_HOME"]
    #positiveFname = dirName + "/forkliftMturkEsdcs.stefie10.yaml"

    fname = "%s/tools/forklift/dataAnnotation/data/forkliftMturkEsdcs.stefie10.groundings.yaml" % os.environ["SLU_HOME"]
    
    corpus = annotationIo.load(fname)
    trainer.trainAndPlot(corpus)
    #trainer.trainAndPlotReranker(corpus)
    
    
        
if __name__ == "__main__":
    main()
