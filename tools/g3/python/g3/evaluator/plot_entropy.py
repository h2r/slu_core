#from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']))
#rc('text', usetex=True)


import numpy as na
from confusion_matrix import ConfusionMatrix
import pickle_util
import pylab as mpl
# mpl.rc('text', usetex=True)
# mpl.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']))
# mpl.rc('font', family='sans-serif')
from g3.inference import entropy_metrics as em
import yaml

from environ_vars import SLU_HOME

# Change the "pretty" names to the ones we use in the paper
ENTROPY_METRIC_PAPER_NAMES = {'Metric 1': r'Metric 1',
                              'Metric 2': r'Metric 2'}

markers = ["o", "+", "x", "*", "s", "h", "D", "1", "2", "3", "4", "v", "^", "|", "_"]
marker_i = 0


def filter_entries(node_entries):
    for tag, f in [
                   # ("all", lambda x: True),
                   # ("no null nodes", lambda x: not x.is_null_node),
                    ("no null and original commands",
                     lambda x: not x.is_null_node and x.is_original_command)
                   ]:
        if len(node_entries) == 0:
            print "skipping", tag, "because no entries even before filter"
            continue

        entries = [ne for ne in node_entries if f(ne)]
        if len(entries) == 0:
            print "skipping", tag, "because no entries"
            continue
        yield entries


def calculate_confusion_matrix(node_entries):
    entries = filter_entries(node_entries).next()
    tp = sum(ne.correct for ne in entries)
    fp = sum(not ne.correct for ne in entries)
    cm = ConfusionMatrix(tp, fp, 0, 0)
    return cm


def plot_entropy_curves(node_entries, pr_figure=None, threshold_figure=None):
    """
    Plots entropy curves for a list of NodeResults
    """
    entries_sets = filter_entries(node_entries)

    for entries in entries_sets:
        if len(entries) > 0:
            title = entries[0].entropy_metric.pretty_name
        else:
            title = ""
        print title

        entropies = [ne.entropy for ne in entries]
        correct = [ne.correct for ne in entries]

        make_pr_graph(entropies, correct, title, "")

def make_pr_graph(entropies, correct, graph_name, title, mpl_figure=None):
    """
    Plot entropy as a PR curve predicting whether examples are correct
    or incorrect.
    """
    if mpl_figure is None:
        mpl_figure = mpl.figure()

    axes = mpl_figure.gca()
    assert len(entropies) == len(correct), (len(entropies), len(correct))
    pairs = zip(entropies, correct)
    pairs.sort()

    max_entropy = float(pairs[-1][0])
    min_entropy = float(pairs[0][0])
    num_segments = 20.0
    segment_size = (max_entropy - min_entropy)/num_segments
    if segment_size == 0:
        segment_size = 0.01
    thresholds = na.arange(min_entropy, max_entropy + 1, segment_size)
    X_recall = []
    Y_precision = []

    for threshold in thresholds:
        predicted_correct = [(entropy, correct)
                             for (entropy, correct) in pairs
                             if entropy < threshold]
        predicted_incorrect = [(entropy, correct)
                             for (entropy, correct) in pairs
                               if entropy >= threshold]
        tp = len([(entropy, correct) for entropy, correct in predicted_incorrect
                 if not correct])
        fp = len([(entropy, correct) for entropy, correct in predicted_incorrect
                 if correct])

        tn = len([(entropy, correct) for entropy, correct in predicted_correct
                 if correct])
        fn = len([(entropy, correct) for entropy, correct in predicted_correct
                 if not correct])
        if tp == 0:
            continue
        cm = ConfusionMatrix(tp, fp, tn, fn)
        X_recall.append(cm.recall)
        Y_precision.append(cm.precision)

    global marker_i
    graph_name_paper = ENTROPY_METRIC_PAPER_NAMES[graph_name]
    axes.plot(X_recall, Y_precision, label=graph_name_paper,
              marker=markers[marker_i])
    marker_i = (marker_i + 1) % len(markers)
    axes.legend(loc='upper right')
    axes.set_xlabel("Recall")
    axes.set_ylabel("Precision")
    axes.set_ylim(0, 1.1)
    axes.set_xlim(0, 1.1)
    axes.set_title("Precision vs Recall")
    mpl_figure.savefig(title.replace(" ", "_") + ".eps")
    mpl.show()


def make_threshold_graph(entropies, correct, graph_name, title,
                         mpl_figure=None):
    """
    Plot the fraction correct at different entropy levels.
    entropy_lists is a list of lists of entropies for each node.
    correct is whether that node was correct.
    """
    if mpl_figure is None:
        mpl_figure = mpl.figure()
    axes = mpl_figure.gca()
    all_X = []
    assert len(entropies) == len(correct)
    pairs = zip(entropies, correct)
    pairs.sort()

    max_entropy = float(pairs[-1][0])
    min_entropy = float(pairs[0][0])
    num_segments = 20.0
    segment_size = (max_entropy - min_entropy)/num_segments
    if segment_size == 0:
        segment_size = 0.01
    thresholds = na.arange(min_entropy, max_entropy + 1, segment_size)
    X = []
    Y_fraction_correct = []
    Y_fraction_used = []
    no_data = []

    for t1, t2 in zip(thresholds, thresholds[1:]):
        entropy_pairs = [pair for pair in pairs if t1 <= pair[0] < t2]
        if(entropy_pairs and len(entropy_pairs) > 0):
            Y_fraction_correct.append(float(sum([pair[1] for pair in entropy_pairs]))/len(entropy_pairs))
            Y_fraction_used.append(float(len(entropy_pairs)) / len(correct))
            X.append(t1)
        else:
            no_data.append(t1)
    global marker_i
    axes.plot(X, Y_fraction_correct, label="%s Fraction Correct" % title,
              marker=markers[marker_i])
    marker_i = (marker_i + 1) % len(markers)

    axes.plot(X, Y_fraction_used, label="%s Fraction Used" % title, marker="x")
    all_X.extend(X)
    print "first bin", Y_fraction_correct[0], Y_fraction_used[0]
    print " last bin", Y_fraction_correct[-1], Y_fraction_used[-1]
    print


    axes.legend(loc='upper right')
    axes.set_xlabel("Entropy threshold")
    axes.set_ylabel("Fraction of Object Grounding Variables")
    axes.set_ylim(0, 1)

    axes.set_title("Fraction Correct in Bin")
    mpl_figure.savefig(title.replace(" ", "_") + ".eps")
    mpl.show()


def main():
    fname = "node_results_102.pck"
    print "loading", fname, "..."
    entries = pickle_util.load(fname)
    plot_entropy_curves(entries)
    print "done"

if __name__ == "__main__":
    main()

