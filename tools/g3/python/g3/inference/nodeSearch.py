
from g3.graph import GGG, Evidences, node_is_empty_figure_of_event
from g3.grounding_space import GroundingSpace
from esdcs.dataStructures import parentsToChildren
import math
import numpy as na
na.random.seed(10)

def get_child_nodes_and_factors(graph, start_node):
    """
    Returns a list of nodes and a list of factors
    found while traversing the graph using all but
    'top' links (i.e. 'child' nodes and factors),
    starting the traversal at start_node.
    """
    child_nodes = []
    child_node_queue = []
    child_factors = []
    child_factor_queue = []
    visited_nodes = []

    child_nodes.append(start_node)
    child_node_queue.append(start_node)

    while(child_node_queue):
        #print "queue", len(child_node_queue)
        current_node = child_node_queue.pop(0)
        if current_node in visited_nodes:
            continue
        visited_nodes.append(current_node)

        factors = [factor for factor in current_node.factors if factor.link_for_node(current_node) == 'top']
        child_factors.extend(factors)
        child_factor_queue.extend(factors)
        for f in child_factor_queue:
            nodes = [node for node in f.nodes if (f.link_for_node(node) != 'top')]
            child_nodes.extend(nodes)
            child_node_queue.extend([n for n in nodes if n not in visited_nodes])
        child_factor_queue = []

    unique_nodes = []
    unique_factors = []

    for node in child_nodes:
        if node not in unique_nodes:
            unique_nodes.append(node)
    for factor in child_factors:
        if factor not in unique_factors:
            unique_factors.append(factor)
    return (unique_nodes, unique_factors)


def find_top_node(ggg):
    for node in ggg.nodes: #get top level event node
        if (node.type == 'gamma_EVENT' and
            False not in [factor.link_for_node(node) == 'top'
                          for factor in node.factors]):
            return node

    top_esdc = ggg.esdcs[0]
    try:
        return ggg.node_for_esdc(top_esdc)
    except:
        print "top", top_esdc
        for esdc, node_id in ggg.esdc_to_node_id.iteritems():
            print "esdc to node id", esdc, node_id

        raise


def sorted_nodes_by_esdcs(ggg):
    """
    Sort nodes according to the order in the language, so we ground in
    the right order.  Also skips paths, since they will be filled in
    with the top-level event grounding.
    """
    reversed_esdcs = list(reversed(parentsToChildren(ggg.esdcs)))
    nodes = []
    seen_node_ids = set()
    for esdc in reversed_esdcs:
        factor = ggg.esdc_to_factor(esdc)
        if factor != None:
            for node in factor.gamma_nodes:
                evidence = ggg.evidence_for_node(node)
                assert evidence != None
                if (len(evidence) == 0 and
                    not node_is_empty_figure_of_event(ggg, node) and
                    not node.id in seen_node_ids and
                    not node.is_path):
                    nodes.append(node)
                    seen_node_ids.add(node.id)
    last_event = None
    for node in nodes:
        if node.is_event:
            last_event = node

    return [n for n in nodes if not n.is_event or n == last_event]

def sorted_nodes_by_traversal(ggg):
    """
    Sort nodes by traversal order (reversed, so that child nodes are first), and
    then sort event nodes to the end of the list.
    """

    top_node = ggg.top_event_node
    child_nodes, child_factors = get_child_nodes_and_factors(ggg.graph, top_node)
    nodes = list(reversed([node for node in child_nodes if
                      node.is_gamma and
                      not node_is_empty_figure_of_event(ggg, node) and
                      not node.is_path and not ggg.evidence_for_node(node)
                      ]))
    return [n for n in nodes if not n.is_event] + [n for n in nodes if n.is_event]




def prune_deterministic(active_set, beam_width):
    active_set.sort(key=lambda x: x[0])
    return active_set[0:beam_width]

def prune_random(active_set, beam_width):
    if len(active_set) <= beam_width:
        return active_set
    else:
        remaining_active_set = list(active_set)
        new_active_set = []
        while len(new_active_set) < beam_width:
            probabilities = [math.exp(-x[0][0]) for x in remaining_active_set]
            # probabilities = [-x[0][0] for x in remaining_active_set]
            # probabilities = probability.normalize(probabilities)
            sum_prob = sum(probabilities)
            probabilities = [p / sum_prob for p in probabilities]
            sample = na.random.multinomial(1, probabilities)
            idx = na.argmax(sample)
            #idx = na.argmax(probabilities)
            new_entry = remaining_active_set.pop(idx)
            new_active_set.append(new_entry)
        return new_active_set


# prune = prune_random
prune = prune_deterministic

class BeamSearch:

    def __init__(self, cf_obj, useRrt=False, useSkip=True):
        self.useRrt = useRrt
        self.useSkip = useSkip
        self.cf_obj = cf_obj
        self.factor_callback=lambda ggg, factor: True

        if self.useRrt:
            raise ValueError("Implement rrt stuff.")


    def find_plan(self, start_state, start_gggs,
                  beam_width=10, beam_width_sequence=5,
                  search_depth_event=5, beam_width_event=2, verbose=False,
                  save_state_tree=False, allow_null_action=False, factor_callback=lambda ggg, factor: True):
        """
        Infers groundings for the ggg, given the current start state.
        Parameters set the search depth and beam width, as well as
        whether it should save meta data.  allow_null_action is
        whether it is allowed to not perform an action (based on the
        search depth)

        Returns a list of tuples [((cost, idx), start_state, ggg)] The
        idx is to break ties in a deterministic way when costs are
        equal.
        """
        self.factor_callback = factor_callback
        self.state_tree = {start_state: (None, None)}
        #verbose = True
        if verbose:
            print "*********** find plan node search"
            print "beam_width", beam_width
            print "beam_width_sequence", beam_width_sequence
            print "search_depth_event", search_depth_event
            print "beam_width_event", beam_width_event
            print "start_state", start_state.getPosition()
            for g in start_gggs:
                for e in g.esdcs:
                    print str(e)

        assert len(start_gggs) == 1
        start_ggg = GGG.unlabeled_ggg(start_gggs[0], start_state.to_context())
        if verbose:
            print "context", start_state.getPlacesSet()
            print "context", start_ggg.context.places
        assert start_ggg.context.agent != None
        for factor in start_ggg.factors:
            start_ggg.evidences[factor.phi_node.id] = True

        context = start_state.to_context()
        gspace = GroundingSpace(context, start_state=start_state)
        self.cf_obj.initialize_state(start_state)


        new_evidences = Evidences.copy(start_ggg.evidences)

        nodes = sorted_nodes_by_traversal(start_ggg)
#        nodes = sorted_nodes_by_esdcs(start_ggg)

        active_set_i = 0
        self.cost(start_ggg, [start_state], verbose=verbose)
        active_set = [((start_ggg.cost(), active_set_i), start_state, start_ggg)]
        active_set_i += 1

        for node in nodes:
            if verbose:
                print "doing", node, node.type
                print "esdc", str(start_ggg.node_to_top_esdc(node))
                print "active nodes: ", len(active_set)
            active_set = prune(active_set, beam_width)
            new_active_set = []
            for cost, state, ggg in active_set:
                if node.is_event:
                    new_stuff, active_set_i = \
                        self.do_events(gspace, ggg, node, start_state,
                                       beam_width_event, search_depth_event,
                                       active_set_i, verbose, save_state_tree,
                                       allow_null_action)
                    new_active_set.extend(new_stuff)
                else:
                    candidate_values = gspace.grounding_space(node)
                    if verbose:
                        print "values in gspace:", len(candidate_values)
                    for grounding in candidate_values:
                        new_evidences = ggg.evidences.add(node.id, [grounding])
                        new_ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
                        cost = self.cost(new_ggg, state_sequence=None, verbose=verbose)
                        if not na.isinf(cost):
                            new_active_set.append(((cost, active_set_i),
                                               start_state, new_ggg))
                            active_set_i += 1
            # if len(new_active_set) < 1 and not node.is_event:
            #     # If we couldn't find any plans, then just bind this
            #     # node to nothing
            #     for cost, state, ggg in active_set:
            #         new_evidences = ggg.evidences.add(node.id, [])
            #         new_ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
            #         cost = self.cost(new_ggg, state_sequence=None, verbose=verbose)
            #         if not na.isinf(cost):
            #             new_active_set.append(((cost, active_set_i),
            #                                start_state, new_ggg))
            #             active_set_i += 1
            # assert len(new_active_set)
            active_set = new_active_set

        active_set.sort(key=lambda x: x[0])
        if verbose:
            print "returning", len(active_set)

        # assert len(active_set)
        return active_set

    def cost(self, new_ggg, state_sequence, verbose=False):
        """
        Compute scores for the ggg, for all incomplete factors, and
        save them by mutating the ggg.
        """
        verbose = False
        overall_cost = 0
        all_entries = []
        for factor in new_ggg.factors:
            esdc = new_ggg.factor_to_esdc(factor)
            if verbose:
                print "esdc", esdc
                print "factor id", factor.id
                print "empty", esdc.isEmpty()
                print "has ungrounded nodes", new_ggg.has_ungrounded_nodes(factor)

                for node in factor.gamma_nodes:
                    if new_ggg.is_ungrounded(node):
                        print "node", node.id, new_ggg.node_to_top_esdc(node)


            if not esdc.isEmpty() and not new_ggg.has_ungrounded_nodes(factor):
                if not new_ggg.has_cost_for_factor(factor):
                    cost, entries = self.cf_obj.compute_costs([factor], new_ggg,
                                                              state_sequence,
                                                              verbose=verbose)
                    assert len(entries) == 1
                    if verbose:
                        print "computing cost"
                    entry = entries[0]
                    all_entries.append(entry)
                    self.factor_callback(new_ggg, factor)
                else:
                    if verbose:
                        print "not computing"
                if verbose:
                    print "cost", new_ggg.cost_for_factor(factor)

                overall_cost += new_ggg.cost_for_factor(factor)
        if verbose:
            print "overall cost", overall_cost
        for e in all_entries:
            e.overall_cost = overall_cost
            e.overall_prob = math.exp(-e.overall_cost)


        return overall_cost

    def do_events(self, gspace, ggg, node, start_state, beam_width_event,
                  search_depth, active_set_i, verbose=False,
                  save_state_tree=False, allow_null_action=False):

        if verbose:
            print "************** DOING EVENTS"
        assert node.is_event
        new_stuff = []
        i = 0
        active_set = [((0, i), start_state)]
        i += 1
        # objects = [o for o in ggg.context.objects if "pallet" in o.tags]
        # Only allow manipulations of objects that have been bound already in the ggg
        objects = ggg.object_groundings
        if verbose:
            print "doing events to", search_depth
        for depth in range(search_depth):
            new_active_set = []
            for cost, s in active_set:
                children = s.getSuccessors(groundings=objects)
                if verbose:
                    print "children", len(children)

                for (s1, action, modified_groundings) in children:
                    if action == None and not allow_null_action:
                        continue

                    agent = s1.agent
                    if save_state_tree:
                        self.state_tree[s1] = (s, action)
                    if verbose:
                        print "************************************************** action", action
                    if verbose:
                        print "modified groundings"
                        for mg in modified_groundings:
                            print mg, mg.hash_string
                        print "nodes and groundings in ggg"
                        for n in ggg.gamma_nodes:

                            print "n", n, str(ggg.node_to_top_esdc(n)),
                            for glist in ggg.evidence_for_node(n, []):
                                print "groundings", glist
                        print "groundings in ggg"
                        for g in ggg.object_groundings:
                            print g, g.hash_string

                    new_evidences = ggg.evidences.add(node.id, [agent])
                    new_evidences.replace_groundings(modified_groundings)
                    factor = node.factor_for_link("top")
                    assert factor != None
                    for n in ggg.gamma_nodes:
                        if ggg.is_ungrounded(n):
                            new_evidences = new_evidences.add(n.id, [agent])
                    new_ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)

                    object_groundings = []
                    for n in factor.gamma_nodes:
                        if n.is_object:
                            object_groundings.extend(new_ggg.evidence_for_node(n))
                            
                    #object_groundings = new_ggg.object_groundings
                    object_grounding_ids = [o.id for o in object_groundings]
                    if verbose:
                        print "object groundings"
                        for og in object_groundings:
                            print og, og.hash_string
                        print "object grounding ids", [og.id for og in object_groundings]
                        print "active ids", s.active_ids
                        print "modified grounding ids", [g.id for g in modified_groundings]
                    skip = False
                    for mg in modified_groundings:

                        if (not mg.id in object_grounding_ids and mg.id != s.AGENT_ID
                            and mg.id not in s.active_ids):
                            if verbose:
                                print "skipping because"
                                print "mg.id", mg.id
                                print "active ids", s.active_ids
                                print "grounding ids", object_grounding_ids
                                print "agent", s.AGENT_ID
                            skip = True
                            break
                    if verbose:
                        print "skip", skip
                    if not self.useSkip:
                        skip = False
                    if not skip:
                        if save_state_tree:
                            sequence = self.state_sequence(s1)
                        else:
                            sequence = None
                        cost = self.cost(new_ggg, sequence, verbose=verbose)
                        if na.isinf(cost):
                            raise ValueError("Infinite cost")
                        new_stuff.append(((cost, active_set_i), s1, new_ggg))
                        active_set_i += 1

                        new_active_set.append(((cost, i), s1))
                        i += 1
                    if verbose:
                        print "**************************************************"
            active_set = prune(new_active_set, beam_width_event)

        return new_stuff, active_set_i

    def state_sequence(self, state):

        states = []
        current_state = None
        current_action = None
        next_state = state
        while next_state != None:
            current_state, current_action = self.state_tree[next_state]
            if current_action != None:
                states.append((current_action, next_state))
            next_state = current_state


        states.reverse()
        return states
