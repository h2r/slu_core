

class OptimizationError(Exception):
    def __init__(self, comment):
        self.comment = comment
    def __str__(self):
        return self.comment
    def __repr__(self):
        return self.comment

class ClassifierNotTrainedError(Exception):
    def __init__(self, comment):
        self.comment = comment
    def __str__(self):
        return self.comment
    def __repr__(self):
        return self.comment
