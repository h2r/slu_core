class Evidences:
    """
    Bindings for variables in a grounding graph.  A mapping between
    node_ids and groundings.
    """

    def __init__(self, node_id_to_groundings=None):
        if node_id_to_groundings == None:
            node_id_to_groundings = {}
        self.node_id_to_groundings = node_id_to_groundings

    @staticmethod
    def copy(evidences):
        new_copy = Evidences()
        for key in evidences.keys():
            new_copy[key] = evidences[key]
        return new_copy


    def repr(self):
        return repr("Evidences(%s)" % repr(self.node_id_to_groundings))

    @staticmethod
    def merge(e1, e2):
        evidences = Evidences()
        for key in e1.keys():
            evidences[key] = e1[key]
        for key in e2.keys():
            evidences[key] = e2[key]

        return evidences


    def __setitem__(self, node_id, value):
        if isinstance(value, list):
            for l in value:
                y = 1
                assert not value.__class__ == y.__class__
        self.node_id_to_groundings[node_id] = value

    def __getitem__(self, key):
        return self.node_id_to_groundings[key]        
    def __contains__(self, key):
        return key in self.node_id_to_groundings

    def replace_groundings(self, modified_groundings):
        for k, value in self.node_id_to_groundings.iteritems():
            if isinstance(value, list):
                new_value = []
                for g in value:
                    replacement = [mg for mg in modified_groundings if (hasattr(g, "id") and  
                                                                        mg.id == g.id)]
                    if len(replacement) == 0:
                        new_value.append(g)
                    else:
                        assert(len(replacement) == 1)
                        new_value.append(replacement[0])
                self.node_id_to_groundings[k] = new_value
    def setdefault(self, key, value):
        if isinstance(value, list):
            for l in value:
                y = 1
                assert not l.__class__ == y.__class__
        self.node_id_to_groundings.setdefault(key, value)

    def get(self, key, default):
        return self.node_id_to_groundings.get(key, default)

    def get_string(self, key):
        value = self[key]
        if isinstance(value, list):
            return ", ".join(str(x) for x in value)
        else:
            return str(value)
        
    def keys(self):
        return self.node_id_to_groundings.keys()

    def has_key(self, key):
        return key in self.node_id_to_groundings.keys()


    def add(self, node_id, value):
        ev = Evidences()
        ev[node_id] = value

        if isinstance(value, list):
            for l in value:
                y = 1
                assert not l.__class__ == y.__class__
        return Evidences.merge(self, ev)
        
    def append_to_evidence(self, node_id, appendix):
        if isinstance(appendix, list):
            for l in appendix:
                y = 1
                assert not l.__class__ == y.__class__


        old_ev = self.get(node_id, [])
        if isinstance(old_ev, list):
            if appendix in old_ev:
                return self
            else:
                return self.add(node_id, old_ev+[appendix])
        else:
            raise BaseException("Prior Evidence for the node is not ")
