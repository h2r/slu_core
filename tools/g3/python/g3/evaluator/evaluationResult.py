import math
class EvaluationResult:
    """
    This is a result of the evaluation. It includes the start state,
    esdc, and end state.  A list of these get stored by evaluateCorpus.py
    """
    def __init__(self, esdcs, esdc_num, start_state, start_gggs, 
                 end_state, end_ggg, cost, annotation):
        self.annotation = annotation
        self.esdcs = esdcs
        self.esdc_num = esdc_num
        self.start_state = start_state
        self.start_gggs = start_gggs

        self.end_state = end_state
        self.end_ggg = end_ggg
        self.cost = cost 

        self.entireText = annotation.esdcs.entireText
        self.searchedText = (' ').join([esdc.text for esdc in esdcs])
        
    @property
    def prob(self):
        return -math.exp(self.cost)
