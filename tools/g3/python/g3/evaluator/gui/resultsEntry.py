import math
import random


class Entry:
    """
    Represents a result from the inference.  It contains the "best"
    result and the n-best list of other results.  The nbest list is
    stored as EvaluationResults, but you can also get them as Entry
    classes themselves; these Entry classes will have a single result
    in the n-best list.  The reason is to make it easy to use the same
    table model in evaluationResultsBrowser for the "best" set of
    results, and also the entries in the n-best list table.
    """

    @staticmethod
    def entries_from_results_file(resultsFile):
        """
        Create a bunch of entries from a results file shelf.
        """
        data = []
        for i, (ggg, result_list) in enumerate(resultsFile.results):
            data.append(Entry(i, ggg, result_list))
        return data

    def __init__(self, i, gggs, results):
        self.i = i
        self.start_gggs = gggs
        #results = results[0:20]
        self.results = results

        self.best_result = results[0]
        assert self.best_result.start_gggs == self.start_gggs
        self.annotation = self.best_result.annotation
        self.start_state = self.best_result.start_state

        self.random = random.randint(0, 10000000)
        self.esdcs = self.best_result.esdcs
        self.end_ggg = self.best_result.end_ggg

        self.esdcType = self.esdcs[0].type
        self.text = self.esdcs.text

        if self.best_result.annotation.assignmentId != None:
            self.assignmentId = self.best_result.annotation.assignmentId
        else:
            self.assignmentId = None

        self.cost = self.best_result.cost
        self.probability = math.exp(-self.cost)

        self.esdcNum = self.best_result.esdc_num
        self.event_node_result = None

    def results_as_entries(self):
        """
        Returns the stuff in the N_best list of this class as Entries.
        """
        data = []
        for i, r in enumerate(self.results):
            data.append(Entry(i, self.start_gggs, [r]))
        return data

    def best_result_as_entry(self):
        return Entry(0, self.start_gggs, [self.best_result])

