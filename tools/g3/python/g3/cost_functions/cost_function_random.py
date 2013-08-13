import random
from cost_function_crf import CostEntry

class CostFnRandom:
    
    def __init__(self, *args):
        pass
    def initialize_state(self, state):
        pass

    def cost(self, esdcs, assignments):
        return random.random()

    def compute_costs(self, input_factors, ggg, state_sequence, verbose=False):
        cost = 3
        return cost, [CostEntry(input_factors[0], ggg, None, None, None, cost)]
