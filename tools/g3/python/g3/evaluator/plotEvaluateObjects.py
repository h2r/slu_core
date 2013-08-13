import pickle_util
import numpy as na
import scipy
import pylab as mpl
def main():
    print "loading"
    confusion_matrices = pickle_util.load("confusion_matrices.pck")
    print "loaded", confusion_matrices
    confusion_matrices.sort(key = lambda x: x[0])
    X = []
    Y = []
    Yerr = []
    for num_results, cms in confusion_matrices:
        print "num_results", num_results
        f_scores = [cm.fscore for cm in cms]
        print na.mean(f_scores)
        error = scipy.stats.sem(f_scores)
        X.append(num_results)
        Y.append(na.mean(f_scores))
        Yerr.append(error)
    mpl.errorbar(X, Y, yerr=Yerr)
    mpl.xlabel("Number of Training Examples")
    mpl.ylabel("F-Score")
    mpl.show()
        
if __name__=="__main__":
    main()
