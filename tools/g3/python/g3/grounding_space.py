

def breadth_first(active_set, s1, a, mg):
    active_set.append((0, s1))
    return active_set


class GroundingSpace:
    """
    fork of grounding space from esdcs
    """
    def __init__(self, context=None, start_state=None, event_depth=1, salient_tags=[]):
        self.start_state = start_state
        self.context = context
        self.event_depth = event_depth
        self.objects = [o for o in context.objects]
        # self.objects = [o for o in context.objects if o != context.agent]
        self.salient_tags = salient_tags

        if self.start_state == None:
            raise ValueError("Must pass in a start state.")

        assert self.context != None
        assert self.start_state != None

        self.context = context
        self.events = self.events_as_search()
        #self.paths = [p.path for events in self.events for p in events]
        #assert len(self.events) > 0
        #assert len(self.paths) > 0


    def events_as_search(self, callback=breadth_first):
        movable_objects = [o for o in self.context.objects if "pallet" in o.tags]
        pobj_lists = []
        states = []

        active_set = [(0, self.start_state)]

        for i in range(self.event_depth):
            new_active_set = []
            for cost, s in active_set:
                for (s1, a, mg) in s.getSuccessors(groundings=movable_objects):
                    pobj_lists.append(mg)
                    new_active_set = callback(new_active_set, s1, a, mg)
                    states.append((s1, a, mg))

            active_set = new_active_set
        return states

    def grounding_space(self, node):
        """
        Returns the space of possible values for a node, given the context.
        For a node which is already bound to a value (as in the case of yes/no dialog), returns only the value for that node.
        """
        if node.is_object:
            if len(self.salient_tags) > 0:
                return [o for o in self.objects if not set(self.salient_tags).isdisjoint(set(o.tags))]
            return self.objects
        elif node.is_place:
            return self.context.places
        elif node.is_event:
            return self.events
        else:
            raise ValueError("Unexpected node type: %s" % node)
