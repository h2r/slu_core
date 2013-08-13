from esdcs.esdcIo import annotationIo
from optparse import OptionParser
import collections

def main():
    parser = OptionParser()
    parser.add_option("--corpus-fname", dest="corpus_fname", action="append")
    (options, args) = parser.parse_args()

    corpus = annotationIo.load_all(options.corpus_fname, check=False)

    id_to_annotations = collections.defaultdict(lambda: list())

    for annotation in corpus:
        id_to_annotations[annotation.id].append(annotation)

    for annotation_id, annotations in id_to_annotations.iteritems():
        for i, annotation in enumerate(annotations):
            annotation.id = annotation.id + "_%d" % i
            annotation.assignmentId = annotation.id
    annotationIo.save_separate_files(corpus)
        

if __name__=="__main__":
    main()
