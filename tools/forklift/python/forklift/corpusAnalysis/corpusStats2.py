from esdcs.esdcIo import annotationIo

def main():
    #annotations = annotationIo.load_all(["../nlu_navigation/data/d8_full_all_path_annotations.yaml", "../nlu_navigation/data/d1_full_all_path_annotations.yaml", ])
    annotations = annotationIo.load_all(["dataAnnotation/data/commands_AAAI_11/forkliftMturkEsdcs.stefie10.groundings.withPaths.yaml"])
    
    words = []
    phrases = []
    with open("commands.txt", "w") as f:
        for annotation in annotations:
            f.write(annotation.entireText + "\n")
            words.extend(annotation.entireText.split())
            phrases.extend(annotation.esdcs)
        
    print len(words), "words"
    print len(phrases), "phrases"

    num_towards = len([w for w in words if "toward" in w])
    num_to = len([w for w in words if "to" == w])
    print "toward[s]?", num_towards
    print "to", num_to
    print "%.1f" % (float(num_to)/num_towards)
if __name__ == "__main__":
    main()
