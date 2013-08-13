class Node(object):
    """
    A random variable in the grounding graph.
    """
    types = ["phi", "gamma_OBJECT", "gamma_PLACE", "gamma_PATH",
             "gamma_EVENT", "lambda", 'gamma_BOUND_OBJECT']

    @staticmethod
    def fromYaml(dct):
        dct.setdefault('bound_object_id', None)
        return Node(dct['id'], dct['type'], dct['bound_object_id'])

    @staticmethod
    def copy(node, new_id=None):
        return Node(node.id, node.type, node.bound_object_id)

    def check_rep(self):
        assert self.type in Node.types, self.type
    def __repr__(self):
        return 'Node(%s, "%s")' % (self.id, self.type)

    @property
    def is_gamma(self):
        return self.type.startswith("gamma")
    @property
    def is_lambda(self):
        return self.type == "lambda"
    @property
    def is_phi(self):
        return self.type == "phi"

    @property
    def is_object(self):
        return self.is_gamma and self.type.endswith("OBJECT")

    @property
    def is_place(self):
        return self.is_gamma and self.type.endswith("PLACE")

    @property
    def is_path(self):
        return self.is_gamma and self.type.endswith("PATH")

    @property
    def is_event(self):
        return self.is_gamma and self.type.endswith("EVENT")

    @property
    def is_bound(self):
        return self.bound_object_id is not None

    @property
    def grounding_type(self):
        assert self.is_gamma, "asking for grounding type when not gamma."
        return self.type.split("_")[-1]

    def __init__(self, node_id, node_type, bound_obj_id=None):
        self.id = node_id
        self.type = node_type
        self.factors = []
        self.graph = None
        if bound_obj_id is None:
            self.bound_object_id = None
        else:
            self.bound_object_id = bound_obj_id

    def link_for_factor(self, factor):
        """
        Return the name of the link to this factor.
        """
        assert factor in self.factors
        return factor.link_for_node(self)

    def factor_for_link(self, link):
        for factor in self.factors:
            if factor.link_for_node(self) == link:
                return factor
        return None

    def toYaml(self):
        return {
                "id": self.id,
                "type": self.type,
                "bound_object_id": self.bound_object_id
                }
