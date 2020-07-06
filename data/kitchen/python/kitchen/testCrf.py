import pickle_util
from dcrf3.gui import resultsModel
from mallet.learners.crf_mallet import CRFMallet
from dcrf3.test_lccrf_esdc import make_confusion_matrix

def main():
    dataset = pickle_util.load("testing.pck")
    lcrf = CRFMallet.load("kitchenModel_1.5.pck")
    results = []
    for i, obs in enumerate(dataset.observations):
        entry = resultsModel.Entry(i, lcrf, obs)
        results.append(entry)
    cm = make_confusion_matrix(results)
    cm.print_all()
    


if __name__ == "__main__":
    main()
