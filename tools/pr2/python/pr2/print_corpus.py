from esdcs.esdcIo import annotationIo
def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--corpus-filename",dest="corpus_fnames", 
                      help="Corpus  Filename", metavar="FILE", action="append")
    (options, args) = parser.parse_args()
    corpus = annotationIo.load_all(options.corpus_fnames)
    
    for annotation in corpus:
        print annotation.entireText
        
if __name__ == '__main__':
    main()
