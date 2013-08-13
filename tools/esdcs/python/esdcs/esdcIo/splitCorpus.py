from esdcs.esdcIo import annotationIo
import os
def main():
    """
    Splits a corpus yaml file into multiple smaller files, for faster
    annotation saving and loading.
    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--corpus_fname", dest="corpus_fname")
    parser.add_option("--page_size", dest="page_size", type="int")
    parser.add_option("--result_dir", dest="result_dir", metavar="FILE")
    (options, args) = parser.parse_args()
    
    corpus = annotationIo.load(options.corpus_fname)

    pages = []
    current_page = []
    for annotation in corpus:
        current_page.append(annotation)
        if len(current_page) >= options.page_size:
            pages.append(current_page)
            current_page = []
    if len(current_page) != 0:
        pages.append(current_page)
    if not os.path.exists(options.result_dir):
        os.makedirs(options.result_dir)
    basename = os.path.basename(options.corpus_fname)
    name = basename[0:-5]
    extension = basename[-5:]
    assert extension == ".yaml"
    for page_i, page in enumerate(pages):
        fname = "%s/%s.page_%d.yaml" % (options.result_dir, name, page_i)
        annotationIo.save(page, fname)

if __name__ == "__main__": 
    main()
