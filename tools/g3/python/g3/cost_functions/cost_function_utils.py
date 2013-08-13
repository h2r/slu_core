def make_cost_function_class(name_str):
    from cost_function_crf import CostFnCrf
    from cost_function_random import CostFnRandom
    from cost_function_naive_bayes import CostFnNaiveBayes
    from cost_function_qa import CostFnQa
    cost_map = {}
    for cost_class in [CostFnCrf, CostFnRandom, CostFnNaiveBayes, CostFnQa]:
        cost_map[cost_class.__name__] = cost_class
    if name_str not in cost_map:
        raise ValueError("Cost function name not recognized. Expected values are: %s" % cost_map.keys())
    return cost_map[name_str]
