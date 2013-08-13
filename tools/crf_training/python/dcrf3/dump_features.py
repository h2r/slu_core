from mallet.learners.crf_mallet import CRFMallet
import sys
def main():
    model_fname = sys.argv[1]
    model = CRFMallet.load(model_fname)
    for key, value in model.feature_name_to_weight.iteritems():
        print key, value

if __name__=="__main__":
    main()
    
