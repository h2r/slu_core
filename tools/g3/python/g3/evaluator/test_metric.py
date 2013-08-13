print "execing file"



def metric(results, node):
    """
    Test file for quickly trying new metrics; evaled by evaluationResultsBrowser to avoid long load times.
    """
    from g3.inference import entropy_metrics
    #return entropy_metrics.compute_entropy_num_candidates(results, node)
    return 3

print "metric", metric
x = metric
