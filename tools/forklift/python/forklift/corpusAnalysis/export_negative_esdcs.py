from esdcs.extractor.stanfordParserExtractor import Extractor
from esdcs.esdcIo import toYaml, annotationIo
from esdcs.dataStructures import ExtendedSdcGroup
import yaml
import os

def main():

    extractor = Extractor()
    oldCorpus = annotationIo.load("%s/dataAnnotation/data/forkliftMturkEsdcs.stefie10.groundings.withPaths.yaml" % os.environ['FORKLIFT_HOME'])
    annotations = []
    for i, a in enumerate(oldCorpus):
#        if i != 140:
#            continue
        print "doing", i, a.entireText
        automatic_esdcs_groups = extractor.extractTopNEsdcs(a.entireText, n=10)

        
        for automatic_esdc_group in automatic_esdcs_groups:
            annotation = annotationIo.Annotation(a.assignmentId,
                                                 automatic_esdc_group)
            
            for automatic_esdc in automatic_esdc_group.flattenedEsdcs:
                if automatic_esdc in a.flattenedEsdcs:
                    annotation.setGroundingIsCorrect(automatic_esdc, True)
                else:
                    annotation.setGroundingIsCorrect(automatic_esdc, False)

            annotations.append(annotation)
    annotationIo.save(annotationIo.Corpus(annotations), "negativeEsdcs.yaml")
    
if __name__ == "__main__":
    main()
