import pylab as mpl
from histograms import Histogram, graphStacked
from stopwords import stopwords
from esdcs.dataStructures import ExtendedSdc
from esdcs.esdcIo import annotationIo

def main():

    corpus = annotationIo.load("dataAnnotation/data/forkliftMturkEsdcs.stefie10.groundings.yaml")
    
    wordHist = Histogram()
    fieldToHist = {}
    
    count = 0
    for annotation in corpus:
        for token in annotation.entireText.split():
            if not token in stopwords:
                wordHist.add(token.lower())
        esdcs = annotation.esdcs
        for esdc in esdcs:
            for fieldName in esdc.fieldNames:
                fieldToHist.setdefault(fieldName, Histogram())
                for word in esdc.childTokens(fieldName):
                    text = word.text
                    if not text in stopwords:
                        fieldToHist[fieldName].add(text.lower())
        count += 1
        if count >= 10:
            #break
            pass

    graphStacked({"words":wordHist}, "histogram", "Words",
                 maxCols=10)

    for key in ExtendedSdc.fieldNames:
        if len(fieldToHist[key].bins) != 0:
            graphStacked({key:fieldToHist[key]}, "histogram",
                         ExtendedSdc.fieldNamesToDescriptions[key].capitalize(),
                         maxCols=10)    
                 
    
    mpl.show()

if __name__ == "__main__":
    main()
