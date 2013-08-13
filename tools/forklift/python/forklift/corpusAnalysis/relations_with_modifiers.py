from esdcs.esdcIo import annotationIo
def main():

    corpus = annotationIo.load("dataAnnotation/data/forkliftMturkEsdcs.stefie10.groundings.yaml")
    for annotation in corpus:
        esdcs = annotation.esdcs
        for esdc in esdcs.flattenedEsdcs:
            if (not esdc.childIsEmpty("r") and esdc.type == "OBJECT" or 
                esdc.type == "PLACE"):
                rwords = [str(e.text) for e in esdc.r]
                if (len(rwords) > 1 and not "right" in rwords and not "left" in rwords and not "front" in rwords and not "next" in rwords):
                    print esdc.text
    

if __name__ == "__main__":
    main()
