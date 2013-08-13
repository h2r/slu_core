import collections
from esdcs.esdcIo import annotationIo
from environ_vars import SLU_HOME

def main():

    corpus = annotationIo.load("%s/tools/forklift/dataAnnotation/data/negativeEsdcs.yaml" % SLU_HOME)
    
    assignment_id_to_count = collections.defaultdict(lambda: 0)

    new_corpus = []
    for a in corpus:
        assignment_id_to_count[a.id] += 1
        if assignment_id_to_count[a.id] <= 2:
            new_corpus.append(a)
    annotationIo.save(annotationIo.Corpus(new_corpus), "test.yaml")
    

if __name__ == "__main__":
    main()
