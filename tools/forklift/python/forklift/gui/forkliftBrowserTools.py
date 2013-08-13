from forklift import forkState
from optparse import OptionParser

class ForkliftBrowserTools:
    
    def init_state(self):
        '''Returns the starting agent state.'''
        state, new_am = forkState.waverly_state_truck()
        
        return state

    def manipulated_object_index(self, state):
        '''Returns the index in the objects set of an object that has been
        manipulated by the agent. In the case of the forklift, this is the
        pallet.'''
        pallet = state.held_pallet
        objects = state.getObjectsSet()
        for i, obj in enumerate(objects):
            print "obj", obj
            print "pallet", pallet
            if pallet and pallet.lcmId == obj: #other ways to compare?
                return i

    def topological_xy(self, state):
        '''Returns the coordinates of the locations of the topological
        nodes for this state's topological map.'''
        locations = []
        for i in state.actionMap.list_indicies():
            for n in state.actionMap.neighbors_by_index(i):
                xy1 = state.actionMap.index_to_location(i)
                locations.append(xy1)
        return locations

    def list_node_indices(self, state):
        '''Returns the indices of all the nodes in the relevant map.'''
        return state.actionMap.list_indicies()
