import numpy as na
import math
from probability import compute_entropy_from_distribution



class Metric:
    """
    Class to represent a named entropy metric.
    """
    @staticmethod
    def from_name(name):
        metric_map = Metric.make_metric_map()
        return metric_map[name]

    @staticmethod
    def make_metric_map():
        metrics = [
            Metric("metric1",  "Metric 1", compute_entropy_metric1, -0.815),
            Metric("metric1a", "Metric 1", compute_entropy_metric1a, 0.00),
            Metric("metric2",  "Metric 2", compute_entropy_metric2, 0.969),
            Metric("metric2_event",  "Metric 2", compute_entropy_metric2, 0.969),
            # Metric("metric3",  "Metric 3", compute_entropy_metric3, 0.00),
            ]
        return dict((m.name, m) for m in metrics)

    def __init__(self, name, pretty_name, function, threshold):
        """
        name: Short, computer-option-representable name for the metric
        (e.g., "metric1"),

        pretty_name:  Nicely formatted name.  e.g., "Metric 1"

        function: function that takes a list of end_gggs with
        evidences populated and nodes and computes entropy.

        threshold: The threshold value for entropy for this
        function below which a node would be considered
        certain or correct in decision-based question asking.
        """
        self.name = name
        self.pretty_name = pretty_name
        self.metric = function
        self.threshold = threshold

    def compute_metric(self, *args, **margs):
        entropy = self.metric(*args, **margs)
        if na.isnan(entropy):
            raise ValueError("nan")
        return entropy

    def entropy_for_node_result(self, node_result):
        return self.compute_metric([r.end_ggg for r in node_result.results],
                                   node_result.node)

    def entropy_for_node_results(self, node_results):
        node = node_results[0].node
        for nr in node_results:
            assert nr.node == node
        return self.compute_metric([nr.end_ggg for nr in node_results], node)






def make_object_id_to_results(end_gggs, node):
    obj_id_to_results = {}
    for end_ggg in end_gggs:
        assert len(end_ggg.evidence_for_node(node)) == 1
        pobj = end_ggg.evidence_for_node(node)[0]
        if node.is_event:
            pobj_id = pobj.hash_string
        else:
            pobj_id = pobj.id
        obj_id_to_results.setdefault(pobj_id, [])
        obj_id_to_results[pobj_id].append(end_ggg)
    return obj_id_to_results

def make_node_to_object_ids(end_gggs):
    """
    Returns a map that goes from a node in the grounding graph to the
    set of object IDs that appear as values for that node.

    All the grounding graphs in end_gggs should have the same nodes
    and factors, but different evidences.
    """
    node_to_object_ids = {}
    ggg = end_gggs[0]

    for end_ggg in end_gggs:
        for node in ggg.gamma_nodes:
            evidence = end_ggg.evidence_for_node(node)
            if len(evidence) != 1:
                continue
                raise ValueError("Evidence != 1: " +  `len(evidence)` +
                                 " node: " + `node.type` +
                                 " esdc: " + `end_ggg.node_to_top_esdc(node)`)
            grounding = evidence[0]
            node_to_object_ids.setdefault(node, set())
            if node.is_event:
                node_to_object_ids[node].add(grounding.hash_string)
            else:
                node_to_object_ids[node].add(grounding.id)

    return node_to_object_ids


def compute_normalizer(end_gggs):
    node_to_object_ids = make_node_to_object_ids(end_gggs)
    probs = [float(1.0)/len(v) for v in node_to_object_ids.values()]
    return na.prod(probs)


def estimate_binding_probability(obj_id, end_gggs, normalizer):
    """
    Estimate the probability of the given node binding to the given object ID from the end_gggs generated from the inference process. This implements Equation 17 from the 2012 RSS paper.
    """
    prob = 0.0
    for end_ggg in end_gggs:
        cost = end_ggg.cost()
        probability = math.exp(-cost)
        prob = prob + probability * normalizer
    return prob


def compute_entropy_metric2(end_gggs, node):
    obj_id_to_results = make_object_id_to_results(end_gggs, node)
    normalizer = compute_normalizer(end_gggs)
    probabilities = []
    for i, (oid, end_gggs) in enumerate(obj_id_to_results.iteritems()):
        prob = estimate_binding_probability(oid, end_gggs, normalizer)
        probabilities.append(prob)
    return compute_entropy_from_distribution(probabilities)


def compute_entropy_metric1a(end_gggs, node):
    return -math.exp(-end_gggs[0].cost())

def compute_entropy_metric1(end_gggs, node):
    return -math.exp(-end_gggs[0].cost_for_node(node))


def compute_entropy_nodes(results, node, n=None):
    """
    Returns the number of candidates we saw in the top twenty results
    when sorted by node.
    """
    results = list(sorted(results, key=lambda r: r.end_ggg.cost_for_node(node)))
    obj_id_to_probs = {}
    if n != None:
        results = results[0:n]
    seen_probs = set()
    for r in results:
        #cost = r.end_ggg.cost_for_node(node)
        cost = r.end_ggg.cost_for_node(node)
        if cost in seen_probs:
            continue
        seen_probs.add(cost)
        evidence = r.end_ggg.evidence_for_node(node)
        if len(evidence) == 0:
            continue
        pobj = evidence[0]
        obj_id_to_probs.setdefault(pobj.id, [])
        obj_id_to_probs[pobj.id].append(math.exp(-r.end_ggg.cost()))

    probabilities = na.array([sum(p) for p in obj_id_to_probs.values()])

    return len(probabilities)


def compute_entropy_metric3(end_gggs, node, n=None):
    raise ValueError("This code for 'metric3' is no longer in use. It was developed for the 2012 HRI conference paper, but was never included. If you're looking for 'Metric 3' as mentioned in the 2012 JHRI paper, then you actually want 'metric2_event'. Sorry about that.")
    """
    Returns the number of candidates we saw in the inference as
    the entropy.
    """
    obj_id_to_probs = {}
    if n != None:
        end_gggs = end_gggs[0:n]
    for end_ggg in end_gggs:
        #cost = r.end_ggg.cost_for_node(node)

        evidence = end_ggg.evidence_for_node(node)
        if len(evidence) == 0:
            continue
        pobj = evidence[0]
        obj_id_to_probs.setdefault(pobj.id, [])
        obj_id_to_probs[pobj.id].append(math.exp(-end_ggg.cost()))

    probabilities = na.array([sum(p) for p in obj_id_to_probs.values()])

    return len(probabilities)


def compute_entropy_uniform_samples(results, node, n=None):
    """
    Compute entropy by taking each result as a sample from the joint,
    unweighted.
    """
    if n != None:
        results = results[0:n]
    obj_id_to_results = {}
    for r in results:
        pobj = r.end_ggg.evidence_for_node(node)[0]
        obj_id_to_results.setdefault(pobj.id, [])
        obj_id_to_results[pobj.id].append(r)

    probabilities = [len(value) for key, value in obj_id_to_results.iteritems()]
    return compute_entropy_from_distribution(probabilities)

def compute_entropy_samples_weighted_by_node_prob(results, node, n=None):
    """
    Compute entropy by taking each result as a sample from the joint,
    unweighted.
    """
    if n != None:
        results = results[0:n]

    obj_id_to_results = make_object_id_to_results(results, node)
    probabilities = []
    for i, (oid, results) in enumerate(obj_id_to_results.iteritems()):
        prob = 0.0
        for r in results:
            cost = r.end_ggg.cost_for_node(node)
            probability = math.exp(-cost)
            prob = prob + probability
        probabilities.append(prob)

    return compute_entropy_from_distribution(probabilities)



def compute_entropy_samples_weighted_by_overall_prob(results, node, n=None):
    """
    Compute entropy by taking each result as a sample from the joint,
    weighted by probability of the overall graph for that sample (with
    Phi)
    """
    if n != None:
        results = results[0:n]

    obj_id_to_results = make_object_id_to_results(results, node)
    probabilities = []
    for i, (oid, results) in enumerate(obj_id_to_results.iteritems()):
        prob = 0.0
        for r in results:
            cost = r.end_ggg.cost()
            probability = math.exp(-cost)
            prob = prob + probability
        probabilities.append(prob)

    return compute_entropy_from_distribution(probabilities)





def compute_entropy_mean(results, node):
    """
    Compute entropy by taking the mean of observed probabilities
    for a particular value for a node.  This one works out to be
    essentially the same as compute_entropy_num_candidates.
    """
    obj_id_to_probs = {}
    for r in results:
        cost = r.end_ggg.cost_for_node(node)
        pobj = r.end_ggg.evidence_for_node(node)[0]
        obj_id_to_probs.setdefault(pobj.id, [])
        obj_id_to_probs[pobj.id].append(math.exp(-cost))

    probabilities = na.array([na.mean(p) for p in obj_id_to_probs.values()])


    #probabilities = na.array([math.exp(-r.end_ggg.cost_for_factor(node.factor_for_link("top")))
    #                          for r in results])

    return compute_entropy_from_distribution(probabilities)

    #if len(probabilities) > 1:
    #    entropy = entropy / math.log(len(probabilities))

# metrics = Metric.make_metric_map()

# def named_metric(name):
#     return metrics[name]
