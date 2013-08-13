from scipy.stats import hmean
class ConfusionMatrix:
    def __init__(self, num_true_positives, num_false_positives, 
                 num_true_negatives, num_false_negatives):
        self.num_true_positives = num_true_positives
        self.num_false_positives = num_false_positives
        self.num_true_negatives = num_true_negatives
        self.num_false_negatives = num_false_negatives
        
        self.num_results = (self.num_true_positives + self.num_false_positives + 
                            self.num_true_negatives + self.num_false_negatives)

        self.num_positives = self.num_true_positives + self.num_false_positives
        self.precision = ((float(self.num_true_positives) / self.num_positives) 
                          if self.num_positives != 0 else 0)

        self.num_true = self.num_true_positives + self.num_false_negatives
        self.recall = ((float(self.num_true_positives) / self.num_true) 
                       if self.num_true != 0 else 0)

        if self.precision == 0 or self.recall == 0:
            self.fscore = 0
        else:
            self.fscore = hmean([self.precision, self.recall])

        self.num_correct = self.num_true_positives + self.num_true_negatives

        if self.num_results == 0:
            self.accuracy = 0
        else:
            self.accuracy = ((self.num_correct) /
                             float(self.num_results))

        self.num_correct = self.num_true_positives + self.num_true_negatives

    def __eq__(self, obj):
        return (isinstance(obj, ConfusionMatrix) and
                obj.num_true_positives == self.num_true_positives and
                obj.num_false_positives == self.num_false_positives and
                obj.num_true_negatives == self.num_true_negatives and
                obj.num_false_negatives == self.num_false_negatives)
                
    def accuracy_string(self):
        return "%.3f (%d of %d)" % (self.accuracy,
                                    self.num_correct, 
                                    self.num_results)
    def precision_string(self):
        return "%.3f (%d of %d)" % (self.precision,
                                    self.num_true_positives, 
                                    self.num_positives)


    def recall_string(self):
        return "%.3f (%d of %d)" % (self.recall,
                                    self.num_true_positives, 
                                    self.num_true)

    def print_accuracy(self, desc):
        print desc, self.accuracy_string()


    def print_precision(self, desc):
        print desc, self.precision_string()


    def print_recall(self, desc):
        print desc, self.recall_string()



    def summary(self, desc=""):
        r = (desc + " " + self.accuracy_string() + " "
             "%.3f precision " % self.precision + 
             "%.3f recall " % self.recall + 
             "%.3f fscore" % self.fscore + "\n" +
             "%d TP " % self.num_true_positives + 
             "%d TN " % self.num_true_negatives +  
             "%d FP " % self.num_false_positives + 
             "%d FN " % self.num_false_negatives)
        return r


    def print_all(self, desc=""):
        print desc, self.accuracy_string(),
        print "%.3f" % self.precision, "precision",
        print "%.3f" % self.recall, "recall",
        print "%.3f" % self.fscore, "fscore"

        print self.num_true_positives, "TP",
        print self.num_true_negatives, "TN",
        print self.num_false_positives, "FP",
        print self.num_false_negatives, "FN"
        

