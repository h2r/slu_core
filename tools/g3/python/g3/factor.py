from memoized import MemoizeInstance
from hash_utils import fasthash

class Factor:
    """
    A factor in the grounding graph.
    """
    link_names = ["top","phi","f","r","l","l2"]

    def __init__(self, factor_id, factor_type, link_name_to_node_ids):
        self.id = factor_id
        self.type = factor_type
        self.link_name_to_node_ids = link_name_to_node_ids

        self.nodes = []
        for l in Factor.link_names:
            self.link_name_to_node_ids.setdefault(l, [])

        self.graph = None
        self._repr = ("Factor(%s, %s, %s)" %
                      tuple(repr(x) for x in (self.id, self.type,
                                         self.link_name_to_node_ids)))

        self.hash_string = fasthash(self._repr)
    def has_children(self, link_name):
        if len(self.link_name_to_node_ids[link_name]) != 0: #
            #len(self.link_name_to_nodes[link_name]) > 0:
            return True
        else:
            return False


    def toYaml(self):
        return {"id":self.id,
                "type":self.type,
                "nodes": self.link_name_to_node_ids}

    @property
    def phi_node(self):
        phi_nodes = self.nodes_with_type("phi")
        assert len(phi_nodes) == 1, phi_nodes
        return phi_nodes[0]

    @property
    def lambda_node(self):
        lambda_nodes = self.nodes_with_type("lambda")
        assert len(lambda_nodes) == 1, lambda_nodes
        return lambda_nodes[0]

    @property
    def gamma_nodes(self):
        gamma_nodes = self.nodes_with_type("gamma")
        return gamma_nodes

    def remove_node(self, node):
        """
        Remove a node from this factor's dictionary. Note that this does not
        remove the node from the GroundingGraphStructure. Raises ValueError
        if unsuccessful.
        """
        links = [l for l in self.link_name_to_node_ids if node.id in self.link_name_to_node_ids[l]]
        if len(links) == 0:
            raise ValueError("Couldn't find any links from this factor to the given node. Factor: %s, Node: %s" % (self, node))
        elif len(links) > 1:
            raise ValueError("Too many links (%d, should be 1) from this factor to the given node. Factor: %s, Node: %s" % (len(links), self, node))
        else:
            self.link_name_to_node_ids[links[0]].remove(node.id)

    @MemoizeInstance
    def nodes_for_link(self, link_name):
        """
        Nodes for one of the link types (e.g., figure, relation,
        landmark, landmark2, but represented as abbreviations in the
        link_names variable.)
        """
        return [self.graph.node_from_id(nid) for nid in
                self.link_name_to_node_ids[link_name]]

    def link_for_node(self, node):
        """
        Return the name of the link for this node.
        """
        links = []
        for l in self.link_names:
            nodes = self.nodes_for_link(l)
            if node in nodes:
                links.append(l)
        assert len(links) == 1, (self, links, node)
        return links[0]

    def nodes_with_type(self, node_type):
        """
        Nodes of a particular type, e.g., gamma, lambda, etc.  Type
        names are in Node.types.  If you say "gamma" it return sall
        the gamma nodes even though all the gamma types are gamma_*.
        """
        nodes = [node for node in self.nodes if node.type.startswith(node_type)]
        return nodes

    def __repr__(self):
        return self._repr

    def __eq__(self, factor):
        return repr(self) == repr(factor)

    def __hash__(self):
        return hash(self._repr)