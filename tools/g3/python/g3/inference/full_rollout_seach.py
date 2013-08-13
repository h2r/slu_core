import sys
import re
import gc

from g3.graph import GGG, Evidences
from g3.annotation_to_ggg import assignPathGroundingsToGGG





#=========================================================================

###
### Given a grounding graph, returns all the nodes that are
### ungrounded and are able to be grounded
### EXCLUDING PATH and EVENT nodes.
def find_all_ungrounded_groundable_nodes( ggg ):
    # loop over each factor
    ungrounded_groundable_nodes = {}
    for f in ggg.factors:
        ungrounded_groundable_nodes.update( dict( (node.id, node) for node in f.nodes if not (ggg.evidences[node.id] 
                                                                               or node.type == "gamma_PATH" 
                                                                               or node.type == "gamma_EVENT"
                                                                               or node.type == "lambda")) )
    
    return ungrounded_groundable_nodes.values()


#=========================================================================

###
### Given a set of groundable nodes (the actual node objects) and a 
### state object, returns a map between node ids and a list of the
### potential values the node can be grounded to.
### The potential values are usually ids of groundable objects, except for
### PHI nodes whose potential values are aalways the list of [True, False]
def compute_mapping_of_potential_value_ids_for_groundable_nodes( groundable_nodes, state ):
    
    potential_values = {}
    for node in groundable_nodes:
        if node.is_object:
            potential_values[ node.id ] = state.getObjectsSet()
        elif node.is_place:
            potential_values[ node.id ] = state.getPlacesSet()
        elif node.is_phi:
            potential_values[ node.id ] = [ True, False ]
        else:
            raise ValueError('Unkown node' + `node`)
        
    return potential_values


#=========================================================================

###
### Returns the total number of possible assignments given a 
### mapping between node ids and potetial grounding values
def compute_total_assignments_for_potential_values_mapping( mapping ):
    max_index = 1;
    for values in mapping.values():
        max_index = max_index * len(values)
    return max_index

#=========================================================================

###
### An Assignment Map is a map between nodes ids and an index
### into the list of possible groundings for that node
###
### This returns the intial assignment map given a mapping of potetnail
### grounding values for hte nodes 
### ( as per compute_total_assignments_for_potential_values_mapping )
def initial_assignment_map( potential_values_map ):
    assignment_map = dict( (node_id, 0) for node_id in potential_values_map )
    return assignment_map


#=========================================================================

###
### Returns a map between node ids and the actual object values assigned
### to the nodes for the given assignment map
def assignment_for_assignment_map( potential_values_map, assignment_map ):
    assignment = {}
    for node_id in potential_values_map:
        assignment[ node_id ] = potential_values_map[ node_id ][ assignment_map[node_id] ]
    return assignment


#=========================================================================

###
### Returns true iff the given assignment map is the 'last' assignment map
### This is used to know when to termintate after calling next_assignment_map
### repeatedly from and initial_assignment_map.
def is_last_assignment_map( potential_values_map, assignment_map ):
    for node_id in assignment_map:
        if assignment_map[ node_id ] < len( potential_values_map[node_id] ) - 1:
            return False
    return True

#=========================================================================

###
### Given an assignment map, returns the next assignment map.
### The ordering of the maps are fixed so that all assignments possible
### are seen exactly once by calling next_assignment_map from
### and initial_assignment_map until is_last_assignment_map is true
def next_assignment_map( potential_values_map, assignment_map ):
    if is_last_assignment_map( potential_values_map, assignment_map ):
        raise ValueError('At Last Assignment Map' )
    node_ids_sorted = sorted( assignment_map.keys(), key=lambda str_id: int(str_id) )
    return increment_assignment_map_by_one( potential_values_map, assignment_map, node_ids_sorted, len(node_ids_sorted)-1 )

#=========================================================================

###
### Internal helper function which takes an assignment map
### and an ordering of nodes and node index and adds one to
### the index, overflowing onto the previous node in the ordering
### and returning the new assignment map
def increment_assignment_map_by_one( potential_values_map, assignment_map, node_ids_sorted, node_index ):
    node_id = node_ids_sorted[ node_index ]
    new_assignment_map = {}
    new_assignment_map.update( assignment_map )
    # Ok, if incrementing causes a roll over, deal with that
    if assignment_map[ node_id ] >= len( potential_values_map[node_id] ) - 1:
        new_assignment_map[ node_id ] = 0
        return increment_assignment_map_by_one( potential_values_map, new_assignment_map, node_ids_sorted, node_index - 1 )
    else:
        # otherwise just add one to the assignment
        new_assignment_map[ node_id ] = new_assignment_map[ node_id ] + 1
        return new_assignment_map
  
    
#=========================================================================

###
### Print out all the possible assignment maps for a map of node ids
### to potential grounding values.
### This is mainly useful as a tool of how to use the
### assignment map interface to iterate over all assignments
def print_all_assignments( potential_values_map ):
    a = initial_assignment_map( potential_values_map )
    while not is_last_assignment_map( potential_values_map, a ):
        print a
        a = next_assignment_map( potential_values_map, a )
    print a


#=========================================================================

###
### Returns a new Evidences object which ensures that
### All PATH and EVENT evidences use the given state's agent
def ensure_path_is_agent_state( state, ggg ):

    new_evidences = Evidences.copy( ggg.evidences )
    
    # find all PATHs and EVENTs
    for node in ggg.nodes:
        if node.is_path or node.is_event:
            
            # set the path or event evidence to be the agent of the state
            new_evidences[ node.id ] = [state.agent]

    return new_evidences


#=========================================================================

###
### Given a grounding graph, a state, a cost function and an assignment map
### with paired potential_values map (as per compute_total_assignments_for_potential_values_mapping )
### Returns a new grounding graph whose groundings have been assigned according
### to the assignment graph and whose factors have all been computed 
### according to the cost function and whose PATH and EVENT nodes have been
### grounded to the agent for hte given state.
def assign_graph( ggg, state, cost_function, potential_values_map, assignment_map ):
    new_evidences = ggg.evidences
    # assing the path grounding
    #new_evidences = assignPathGroundingsToGGG( state, ggg )
    new_evidences = ensure_path_is_agent_state( state, ggg )

    for node_id in assignment_map:
        node = ggg.node_from_id( node_id )
        if node.is_phi:
            new_evidences = new_evidences.add( node_id, potential_values_map[node_id][assignment_map[node_id]] )
        else:
            new_evidences = new_evidences.add( node_id, [ state.getGroundableById( potential_values_map[node_id][assignment_map[node_id]]) ] )

    
    # ok, create the graph with the groundable object assigned
    # And we calculate the cost of all factors
    new_ggg = GGG.from_ggg_and_evidence_history( ggg, new_evidences )
    for f in ggg.factors:
        new_ggg = GGG.from_ggg_and_evidence_history( new_ggg, new_evidences )
        cost = cost_function( f, new_ggg )
        new_evidences = new_evidences.add( f.id, cost )
    new_ggg = GGG.from_ggg_and_evidence_history( ggg, new_evidences )

    return new_ggg
        

#=========================================================================

###
### For a given state and cost function,
### try all possible assignments of ungrounded objectcs and 
### returns a (ggg,cost) tuple with the minimum cost grounding graph
### and it's cost
def find_lowest_cost_assigned_graph( ggg, state, cost_function ):
    
    ungrounded_nodes = find_all_ungrounded_groundable_nodes( ggg )
    potential_values_map = compute_mapping_of_potential_value_ids_for_groundable_nodes( ungrounded_nodes, state )
    
    a = initial_assignment_map( potential_values_map )
    min_ggg = None
    min_cost = float('inf')
    counter = 0
    while not is_last_assignment_map( potential_values_map, a ):

        new_ggg = assign_graph( ggg, state, cost_function, potential_values_map, a )
        cost = new_ggg.cost()
        counter = counter + 1

        if cost < min_cost:
            min_ggg = new_ggg
            min_cost = cost
            print "New Min: a=" + str(a) + ", c=" + str(min_cost)

        a = next_assignment_map( potential_values_map, a )

    # Don'e forget to evaluate the last assignment
    new_ggg = assign_graph( ggg, state, cost_function, potential_values_map, a )
    cost = new_ggg.cost()
    counter = counter + 1
    
    if cost < min_cost:
        min_ggg = new_ggg
        min_cost = cost
        print "New Min: a=" + str(a) + ", c=" + str(min_cost)

    print "Tried " + str(counter) + " different assignments"

    gc.collect()
    
    # return a tuple with the min assigned graph and it's cost
    return (min_ggg, min_cost)

#=========================================================================

###
### Returns a set of states which are all of the reachable states
### from given initial state and given depth
def find_all_state_action_sequences_for_depth( state, depth ):
    final_states = []
    if depth < 1:
        final_states.append( state )
        return final_states
    sa_pairs = state.getSuccessors()
    for s, a, mg in sa_pairs:
        final_states.extend( find_all_state_action_sequences_for_depth( s, depth - 1 ) )
    return final_states


#=========================================================================

###
### Search over all possible states for given depth, for all
### possible groundings, for the lowest cost grounding graph
### and return a (state,ggg,cost) tuple for this minimum cost graph/state
def find_lowest_cost_state_sequence_and_assigned_graph( init_state, depth, ggg, cost_function ):
    
    # first, get all of the wanted state sequences
    ss = find_all_state_action_sequences_for_depth( init_state, depth )
    
    # now just find the lowest cost assigned graph for each of them
    min_state = None
    min_ggg = None
    min_cost = float('inf')
    for state in ss:
        new_ggg, new_cost = find_lowest_cost_assigned_graph( ggg, state, cost_function )
        if new_cost < min_cost:
            min_ggg = new_ggg
            min_cost = new_cost
            min_state = state
            print "New Min cost=" + str(min_cost) + " State=" + str(min_state) 
            sys.stdout.flush()
            
    
    return (min_state, min_ggg, min_cost)



