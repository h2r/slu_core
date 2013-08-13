from esdcs.esdcIo import annotationIo
import collections
def main():
    corpus = annotationIo.load("dataAnnotation/data/spatialRelations.stefie10.yaml")
    sr_to_num_positive = collections.defaultdict(lambda: 0)
    sr_to_num_negative = collections.defaultdict(lambda: 0)
    srs = set()
    total = 0
    for annotation in corpus:
        path_esdc = annotation.esdcs[0]
        sr = path_esdc.r[0].text
        srs.add(sr)
        if annotation.isGroundingCorrect(path_esdc):
            sr_to_num_positive[sr] += 1
        else:
            sr_to_num_negative[sr] += 1
        total += 1

    for sr in sorted(srs):
        print sr, sr_to_num_positive[sr], sr_to_num_negative[sr]
    print "total", total

if __name__ == "__main__":
    main()
