from itertools import chain
import utility_functions as gu
import os
import re
import subprocess
from esdcs.dataStructures import ExtendedSdcGroup
from esdcs import context
import graph_to_tex
from esdcs.context import MergedContext
from g3.evidences import Evidences
from g3.factor import Factor
from g3.node import Node

def node_is_empty_figure_of_event(ggg, node):
    """
    Check if the node is the empty figure of an event; we skip it for
    now.  It will be filled in later with the top-level event
    grounding.
    """
    for factor in node.factors:
        esdc = ggg.factor_to_esdc(factor)
    if not node.is_object:
        return False
    if len(node.factors) != 1:
        return False

    factor = node.factors[0]

    esdc = ggg.factor_to_esdc(factor)

    if esdc.type == "EVENT" and factor.link_for_node(node) == "f":
        return True
    else:
        return False


def empty_grounding_graph_yaml():
    return {"GG":{"nodes":[],"factors":[]}}

class GroundingGraphStructure:
    """
    A bipartite factor graph, consisting of random variable nodes and
    factors.  Each factor connects to one or more nodes; each node
    participates in one or more factor.  This class contains the
    structure of the grounding graph, without bindings for the
    variables.
    """

    def __init__(self, nodes, factors):

        self.nodes = nodes
        self.factors = factors
        for node in self.nodes:
            node.graph = self
        for factor in self.factors:
            factor.graph = self

        self.node_id_to_node = dict((node.id, node) for node in nodes)

        self.factor_id_to_factor = dict((factor.id, factor)
                                        for factor in factors)
        self.factor_to_factor_id = dict((factor, factor.id)
                                        for factor in factors)


        for factor in self.factors:
            for link_name, node_ids in factor.link_name_to_node_ids.iteritems():
                for nid in node_ids:
                    node = self.node_from_id(nid)
                    if node != None:
                        factor.nodes.append(node)
                        node.factors.append(factor)

    @property
    def gamma_nodes(self):
        return [n for n in self.nodes if n.type.startswith("gamma")]

    @property
    def gamma_event_nodes(self):
        return [n for n in self.gamma_nodes if n.is_event]

    @property
    def lambda_nodes(self):
        return [n for n in self.nodes if n.type.startswith("lambda")]

    @property
    def phi_nodes(self):
        return [n for n in self.nodes if n.type.startswith("phi")]


    @staticmethod
    def empty_graph():
        return GroundingGraphStructure([], [])
    @staticmethod
    def fromYaml(dct):
        nodes = []
        factors = []

        # create the nodes
        for node_dict in dct["GG"]["nodes"]:
            nn = Node.fromYaml(node_dict)
            # nn = Node(node_dict["id"], node_dict["type"])
            nodes.append(nn)


        #node_id_to_node = dict((n.id, n) for n in nodes)
        #import traceback
        #traceback.print_stack()

        for factor_dict in dct["GG"]["factors"]:
            link_name_to_node_ids = dict()
            for link_name, node_ids in factor_dict["nodes"].iteritems():
                link_name_to_node_ids[link_name] = list(node_ids)
            factor = Factor(factor_dict["id"], factor_dict["type"],
                            link_name_to_node_ids)
            factors.append(factor)

        graph = GroundingGraphStructure(nodes, factors)

        return graph

    def toYaml(self):
        dct = empty_grounding_graph_yaml()
        for nd in self.nodes:
            dct["GG"]["nodes"].append(nd.toYaml())
        for fct in self.factors:
            dct["GG"]["factors"].append(fct.toYaml())
        return dct

    def attach_graph(self,other_graph):
        # try to keep it immutable
        my_dict = self.toYaml()
        other_dict = other_graph.toYaml()
        dct = empty_grounding_graph_yaml()
        # copy over the nodes
        dct["GG"]["nodes"].extend(my_dict["GG"]["nodes"])
        dct["GG"]["nodes"].extend(other_dict["GG"]["nodes"])
        # copy over the factors
        dct["GG"]["factors"].extend(my_dict["GG"]["factors"])
        dct["GG"]["factors"].extend(other_dict["GG"]["factors"])
        return GroundingGraphStructure.fromYaml(dct)

    def create_factor_id_to_node_ids(self):
        nbrs_dict = {} #TODO write it up
        for node in self.nodes:
            nid = node.id
            nbrs_dict[nid] = [factor.id for factor in node.factors]
        for factor in self.factors:
            fid = factor.id
            nbrs_dict[fid] = [node.id for node in factor.nodes]
        return nbrs_dict

    def reorder_factor_id_to_node_id(self, factor_id_to_node_id):
        factor_ids = self.factor_ids
        for factor_id in factor_ids:
            curr_f = self.factor_from_id(factor_id)
            factor_id_to_node_id[factor_id]=[]
            for link_name in Factor.link_names:
                if curr_f.has_children(link_name):
                    factor_id_to_node_id[factor_id].extend(curr_f.link_name_to_node_ids[link_name])

    @property
    def node_ids(self):
        return [node.id for node in self.nodes]

    def node_from_id(self,nd_id):
        for node in self.nodes:
            if node.id == nd_id:
                return node
        return None

    @property
    def factor_ids(self):
        return [factor.id for factor in self.factors]

    def factor_from_id(self,fct_id):
        for factor in self.factors:
            if factor.id == fct_id:
                return factor
        return None
        return None

    def copy(self):
        return GroundingGraphStructure(self.toYaml)

    def nodes_depth_first(self, start_node_id):
        factor_id_to_node_ids = self.create_factor_id_to_node_ids()
        self.reorder_factor_id_to_node_id(factor_id_to_node_ids)
        node_order = gu.depth_first_order_on_leaving(factor_id_to_node_ids,
                                                     start_node_id, [], [])
        return node_order

    def factors_depth_first(self, start_node_id):
        factor_ids = self.factor_ids
        return [self.factor_from_id(f)
                for f in self.nodes_depth_first(start_node_id)
                if f in factor_ids]

    def remove_node(self, node):
        """
        Remove a node from the graph structure and remove references to it from
        all connected factors.
        """
        self.nodes.remove(node)
        self.node_id_to_node.pop(node.id)
        for factor in node.factors:
            factor.remove_node(node)

    def remove_node_by_id(self, nid):
        self.remove_node(self.node_from_id(nid))

def empty_ggg():
    return GGG(GroundingGraphStructure(None), Evidences(None), {})

class GGG:
    """
    A grounding graph, together with bindings for the variables.  This
    class is the top-level, public-facing API.
    """

    @staticmethod
    def copy(ggg):
        return GGG(ggg._graph, Evidences.copy(ggg.evidences), ggg._factor_id_to_esdc,
                   context=ggg.context, parent_esdc_group=ggg.esdcs,
                   factor_id_to_cost=dict(ggg._factor_id_to_cost),
                   esdc_to_node_id=ggg.esdc_to_node_id)
    

    @staticmethod
    def from_ggg_and_evidence(ggg, new_evidence):
        return GGG(ggg._graph, new_evidence, ggg._factor_id_to_esdc,
                   context=ggg.context, parent_esdc_group=ggg.esdcs,
#                   factor_id_to_cost=dict(ggg._factor_id_to_cost))
                   factor_id_to_cost=None,
                   esdc_to_node_id=ggg.esdc_to_node_id)

    @staticmethod
    def from_ggg_and_evidence_history(ggg, new_evidence, gggs=None):
        if gggs == None:
            gggs = ggg.gggs
        return GGG(ggg._graph, new_evidence, ggg._factor_id_to_esdc,
                   gggs, context=ggg.context,
                   factor_id_to_cost=dict(ggg._factor_id_to_cost),
                   esdc_to_node_id=ggg.esdc_to_node_id)

    @staticmethod
    def from_ggg_and_parent_esdc_group(ggg, parent_esdcs):
        return GGG(ggg._graph, ggg.evidences, ggg._factor_id_to_esdc,
                   context=ggg.context, parent_esdc_group=parent_esdcs,
                   factor_id_to_cost=dict(ggg._factor_id_to_cost),
                   esdc_to_node_id=ggg.esdc_to_node_id)


    @staticmethod
    def unlabeled_ggg(labeled_ggg, context):
        new_evidences = labeled_ggg.evidences_without_groundings()
        new_evidences = labeled_ggg.evidences_without_groundings()
        for factor in labeled_ggg.factors:
            new_evidences[factor.phi_node.id] = True

        ggg = GGG(labeled_ggg.graph,
                  new_evidences,
                  labeled_ggg._factor_id_to_esdc,
                  context=context,
                  esdc_to_node_id=labeled_ggg.esdc_to_node_id)

        return ggg

    def __init__(self, graph, evidences, factor_id_to_esdc, gggs=[],
                 context=None, parent_esdc_group=None, factor_id_to_cost=None,
                 esdc_to_node_id=None):

        self._graph = graph
        self._graph.ggg = self
        self.evidences = evidences
        self._factor_id_to_esdc = factor_id_to_esdc

        if factor_id_to_cost == None:
            self._factor_id_to_cost = {}
        else:
            self._factor_id_to_cost = factor_id_to_cost

        self._esdc_to_factor_id = dict((esdc, fid)
                                       for fid, esdc
                                       in self._factor_id_to_esdc.iteritems())

        self.flattened_esdcs = self._esdc_to_factor_id.keys()
        if len(self.flattened_esdcs) == 0:
            self.esdcs = None
            self.entireText = None
            self.text = None
        else:
            if parent_esdc_group != None:
                self.esdcs = parent_esdc_group
            else:
                parent = None
                for e in self.flattened_esdcs:
                    if parent == None or e.contains(parent):
                        parent = e
                if parent == None:
                    raise ValueError("can't find container: " +
                                     `self.flattened_esdcs`)
                self.esdcs = ExtendedSdcGroup([parent])
            self.entireText = self.esdcs.entireText
            self.text = self.esdcs.text

        self.gggs = gggs

        # print self.evidences
        # print [n for n in self.nodes if "OBJECT" in n.type]


        self.gamma_nodes = self.graph.gamma_nodes
        self.lambda_nodes = self.graph.lambda_nodes
        self.phi_nodes = self.graph.phi_nodes
        
        should_sort = True
        for l in self.lambda_nodes:
            from standoff import FakeStandoff
            if any([isinstance(x, FakeStandoff) for x in self.evidence_for_node(l)]) or len(self.evidence_for_node(l)) == 0:
                should_sort = False
                break
        if should_sort:
            def key(node):
                if node.is_lambda:
                    return self.evidence_for_node(node)[0].range
                else:
                    return node.id
            self.graph.nodes = sorted(self.graph.nodes, key=key)

        for n in self.nodes:
            self.evidences.setdefault(n.id, [])
        self.context = context


        if esdc_to_node_id != None:
            self.esdc_to_node_id = dict((key, value) for key, value in
                                        esdc_to_node_id.iteritems()
                                        if key != None)
        else:
            self.esdc_to_node_id = dict()
#            for esdc in self.flattened_esdcs:
#                self.esdc_to_node_id.setdefault(esdc, None)

            for node in self.nodes:
                self.esdc_to_node_id.setdefault(self.node_to_top_esdc(node),
                                                node.id)

        #self.check_rep()

    def with_cropped_range(self, start_t, end_t):
        new_evidences = Evidences.copy(self.evidences)
        for n in self.gamma_nodes:
            evidence = [e.withCroppedRange(start_t, end_t)
                       for e in self.evidence_for_node(n)]
            new_evidences[n.id] = evidence

        result = GGG(self._graph, new_evidences, self._factor_id_to_esdc,
                     context=self.context.withCroppedRange(start_t, end_t),
                     parent_esdc_group=self.esdcs)
        return result

    @property
    def object_groundings(self):
        return list(chain(*
                [self.evidence_for_node(n, [])
                 for n in self.nodes if "OBJECT" in n.type]))

    @property
    def graph(self):
        return self._graph
    def evidences_without_groundings(self):
        evidences = Evidences.copy(self.evidences)

        for n in self.gamma_nodes:
            if not n.is_bound:
                evidences[n.id] = []
        return evidences

    def remove_cost_entries(self):
        """
        Removed saved cost entries.  These are useful for debugging
        since they contain the feature vectors, but use a huge amount
        of memory when pickling things.
        """
        self._factor_id_to_cost = dict((key, (cost, None))
                                       for key, (cost, ce) in self._factor_id_to_cost.iteritems())

    @property
    def object_nodes(self):
        return [n for n in self.gamma_nodes if n.is_object]

    @property
    def lexicalized_object_nodes(self):
        return [n for n in self.gamma_nodes
                if (n.is_object and
                    not node_is_empty_figure_of_event(self, n))]

    @property
    def event_nodes(self):
        return [n for n in self.gamma_nodes if n.is_event]

    def factor_is_grounded(self, factor):
        for node in factor.gamma_nodes:
            if not self.is_grounded(node):
                return False
        return True

    def is_grounded(self, node):
        return not self.is_ungrounded(node)

    def is_ungrounded(self, node):
        evidence = self.evidence_for_node(node)
        assert evidence != None
        if len(evidence) == 0:
            return True
        else:
            return False

    @property
    def has_ungrounded_lambda_nodes(self):
        for node in self.lambda_nodes:
            if self.is_ungrounded(node):
                return True
        return False
    def has_ungrounded_nodes(self, factor):
        for node in factor.gamma_nodes:
            if self.is_ungrounded(node):
                return True
        return False

    @property
    def all_grounded(self):
        return all(self.is_grounded(n) for n in self.gamma_nodes)

    def check_rep(self):
        for e in self.flattened_esdcs:
            assert e in self._esdc_to_factor_id
            #assert self.esdcs.contains(e), e.text # not true with merging.
        for factor_id, esdc in self._factor_id_to_esdc.iteritems():
            assert factor_id in self.factor_ids,  (factor_id, str(esdc))
            assert factor_id in self.factor_ids
            assert self.factor_from_id(factor_id) != None

        for esdc, nid in self.esdc_to_node_id.iteritems():
            if nid != None:
                if not nid in self.node_ids:
                    print self.node_ids
                    assert False, nid




    def esdc_to_factor_id(self, esdc):
        if esdc in self._esdc_to_factor_id:
            fid = self._esdc_to_factor_id[esdc]
            return fid
        else:
            return None

    def esdc_to_factor(self, esdc):
        fid = self.esdc_to_factor_id(esdc)
        if fid != None:
            return self.factor_from_id(fid)
        else:
            return None
    def factor_to_esdc(self, factor):
        return self.factor_id_to_esdc(factor.id)


    def node_to_esdcs(self, node):
        """
        Returns all ESDCs directly connected to this node.
        """
        return [self.factor_to_esdc(f) for f in node.factors]

    def node_to_top_esdc(self, node):
        """
        Return the ESDCs that are "for" this node.  The text of these
        esdcs will best describe what this node is supposed to be.
        """
        for esdc, e_node_id in self.esdc_to_node_id.iteritems():
            if e_node_id == node.id and self.esdcs.contains(esdc):
                return esdc
        for factor in self.factors_for_node(node):
            e = self.factor_to_esdc(factor)
            if self.esdcs.contains(e):
                return e
            # factor = node.factor_for_link("top")
            # if factor != None:
            #     return self.factor_to_esdc(factor)
            # else:
            #     return None
        return None

    def factor_id_to_esdc(self, factor_id):
        return self._factor_id_to_esdc[factor_id]

    def node_id_to_esdcs(self, node_id):
        return self.node_to_esdcs(self.node_from_id(node_id))


    def factor_from_id(self, factor_id):
        return self._graph.factor_from_id(factor_id)

    def node_from_id(self, node_id):
        return self._graph.node_from_id(node_id)

    def set_evidence_for_node_id(self, node_id, value):
        self.evidences[node_id] = value

    def set_evidence_for_node(self, node, value):
        self.set_evidence_for_node_id(node.id, value)

    def clear_evidence_for_node_id(self, node_id):
        self.set_evidence_for_node_id(node_id, [])

    def clear_evidence_for_node(self, node):
        self.set_evidence_for_node(node, [])




    def evidence_for_node(self, node, default_value=None):
        return self.evidence_for_node_id(node.id, default_value=default_value)

    def evidence_for_node_id(self, node_id, default_value=None):
        if default_value == None:
            return self.evidences[node_id]
        else:
            return self.evidences.get(node_id, default_value)
    @property
    def groundings(self):
        return list(chain(*[self.evidences[node.id]
                            for node in self.nodes
                            if (isinstance(self.evidences[node.id], list) and
                                node.type != "lambda")]))



    def groundings_for_factor(self, factor):
        return list(chain(*[self.evidences[node.id]
                            for node in factor.nodes if node.is_gamma]))

    def toContext(self):
        return context.Context.from_groundings(self.groundings)

    @property
    def factor_ids(self):
        return self._graph.factor_ids

    @property
    def factors(self):
        return self._graph.factors

    @property
    def nodes(self):
        return self._graph.nodes

    @property
    def node_ids(self):
        return self._graph.node_ids

    @property
    def max_id(self):
        return max([int(x.id) for x in self.nodes + self.factors])

    def nodes_for_link(self, name):
        """
        Return nodes in the graph with a particular link type. (Link
        types are in Factor.link_names)
        """
        nodes = []
        for factor in self.factors:
            nodes.extend(factor.nodes_for_link(name))
        return nodes

    def nodes_with_type(self, node_type):
        """
        Return nodes in the graph with a particular type. (Type names are in Nodes.type)
        """
        nodes = set()
        for factor in self.factors:
            nodes.update(factor.nodes_with_type(node_type))
        return nodes

    def factors_for_node(self, target_node, links='top'):
        """
        Find the factors in the GGG which have the given node at the given link. Returns a list of factors. Returns [] if none found.

        Can also take in a list of possible link names.
        """
        if not isinstance(links, list):
            links = [links]
        target_factors = []
        for factor in self.factors:
            if any(target_node in factor.nodes_for_link(l) for l in links):
                target_factors.append(factor)
        return target_factors

    def set_node_for_esdc(self, original_esdc, node):
        self.esdc_to_node_id[original_esdc] = node.id

    def inferred_context(self):

        return MergedContext(self.context, self.groundings)


    def node_id_for_esdc(self, esdc):
        if esdc in self.esdc_to_node_id.keys():
            return self.esdc_to_node_id[esdc]
        else:
            return None

    def node_for_esdc(self, esdc):
        return self.node_id_to_node(self.node_id_for_esdc(esdc))

    def node_id_to_node(self, node_id):
        return self._graph.node_id_to_node[node_id]

    @staticmethod
    def fromYaml(yml):
        return GGG(GroundingGraphStructure(yml),Evidences(yml))

    def attach_ggg(self, ggg):
        self._graph = self._graph.attach_graph(ggg.graph)
        self.evidences = self.evidences.update_evidences(ggg.evidences)
        return self

    def factors_depth_first(self, start_node_id):
        return self._graph.factors_depth_first(start_node_id)

        node = self.node_from_id(start_node_id)
        active_factors = []
        active_factors.extend(node.factors)

        results = []

        while len(active_factors) != 0:
            new_active_factors = []
            for factor in active_factors:
                if not factor in results:
                    results.append(factor)
                    for node in factor.nodes:
                        new_active_factors.extend(node.factors)
            active_factors = new_active_factors

        return results

    def cost(self):
        return sum(self.costs)

    @property
    def costs(self):
        return [t[0] for t in self._factor_id_to_cost.values()]

    def cost_for_factor(self, factor):
        return self.cost_for_factor_id(factor.id)

    def cost_for_factor_id(self, factor_id):
        return self._factor_id_to_cost[factor_id][0]

    def entry_for_factor_id(self, factor_id):
        return self._factor_id_to_cost[factor_id][1]

    def entry_for_factor(self, factor):
        return self.entry_for_factor_id(factor.id)

    def set_cost_for_factor_id(self, factor_id, cost, entry):
        self._factor_id_to_cost[factor_id] = (cost, entry)

    def set_cost_for_factor(self, factor, cost, entry):
        return self.set_cost_for_factor_id(factor.id, cost, entry)

    def has_cost_for_factor_id(self, factor_id):
        return factor_id in self._factor_id_to_cost

    def has_cost_for_factor(self, factor):
        return self.has_cost_for_factor_id(factor.id)

    def costs_for_node(self, node):
        return [self.cost_for_factor(f) for f in node.factors
                if self.has_cost_for_factor(f)]
    def cost_for_node(self, node):
        return sum(self.costs_for_node(node))
    
    def null_costs(self):
        for f in self.factors:
            self.null_cost_for_factor(f)

    def null_costs_for_node(self, node):
        for f in node.factors:
            self.null_cost_for_factor(f)
    def null_cost_for_factor(self, factor):
        self.null_cost_for_factor_id(factor.id)

    def null_cost_for_factor_id(self, factor_id):
        if factor_id in self._factor_id_to_cost:
            del self._factor_id_to_cost[factor_id]


    def to_latex(self, fname):
        graph_to_tex.to_tex_file(self, fname)

    def dot_name(self, node):
        if node.type == 'lambda':
            return node.id + '_' + "'" + self.evidence_for_node(node)[0].text + "'"
        else:
            return node.id + '_' + node.type


    def to_file(self, fname, use_edge_labels=True):
        """
        Convert this GGG to dot language and, optionally,
        run dot to convert it to a PDF.
        """
        basename = os.path.basename(fname)
        tmpname = "/tmp/" + basename
        f = open(tmpname, "w")
        print >>f, self._to_dot()
        f.close()
        basename, extension = os.path.splitext(fname)

        if extension == ".pdf":
            cmd = "dot %s -Tpdf -o %s" % (tmpname, fname)
            print "calling", cmd
            subprocess.call(cmd, shell=True)
        elif extension == ".dot":
            subprocess.call("cp %s %s" % (tmpname, fname), shell=True)
        else:
            raise ValueError("Unexpected extension: " + `fname`)
    def lambda_nodes_to_text(self):
        results = []
        for n in self.lambda_nodes:
            evidence = self.evidence_for_node(n)
            results.extend([str(e) for e in evidence])
        return " ".join(results)

    def _to_dot(self):
        """
        Convert this GGG to graphviz dot language.
        """
        dot = "digraph esdcparse {\n"
        gev = self.evidences

        def node_label(node):
            if gev.has_key(node.id) and not gev.get_string(node.id)=='':
                result = re.escape(gev.get_string(node.id))
            else:
                result = node.type.replace("gamma_","")
            result = str(node.id) + ": " + result
            return result

        def enquote(string):
            return '"' + string + '"'

        edges = []
        for factor in self._graph.factors:
            factor_name = node_label(factor)
            # dot += '  ' + factor.id + ' [shape=box label="" style=filled fillcolor="#000000" fixedsize="true" height="0.3" width="0.3"];\n'
            dot += '  ' + factor.id + ' [shape=box label="'+factor_name+'"];\n'
            for link, ids in factor.link_name_to_node_ids.iteritems():
                for nid in ids:
                    node = self.node_from_id(nid)
                    # import pdb; pdb.set_trace()
                    if link == 'top':
                        edge = [node.id, factor.id, link]
                    else:
                        edge = [factor.id, node.id, link]
                    if link == 'phi':
                        dot += '  subgraph { rank=same; ' + node.id + '; ' + factor.id + ';}\n'
                        dot += '  ' + node.id + ' [label='+node.id+' shape=diamond width=0.5 height=0.5 fixedsize=true];\n'
                    else:
                        dot += '  ' + node.id + ' [label='+enquote(node_label(node)) + '];\n'
                    edges.append(edge)
        for edge in edges:
            dot += '  %s -> %s [dir=none label=%s]\n' % (edge[0], edge[1], edge[2])
            # dot += '  ' + edge[0] + ' -> ' + edge[1] + '[dir=none]\n'

        dot += "}\n"
        return dot

    @property
    def top_event_node(self):
        return find_top_node(self)

    @property
    def top_event_ggg(self):
        return self.node_to_top_esdc(find_top_node(self))

    def create_esdc_tree(self):
        queue = []
        queue.append([1, "x", self.top_event_node])
        visited = set([])
        full = ""
        yaml = ""
        while len(queue) > 0:
            depth, link, candidate = queue.pop(0)
            if isinstance(candidate, Node):
                if candidate.is_gamma:
                    if len(set([f.id for f in candidate.factors]) & visited) != len(candidate.factors):
                        yaml += " " * 2 * depth + link + ":\n"
                        yaml += " " * 2 * (depth + 1) + candidate.type[6:] + ":\n"
                        factors = candidate.factors
                        for factor in factors:
                            if factor.id not in visited:
                                visited = visited | set([factor.id])
                                queue.insert(0, [depth + 1, "factor", factor])
                if candidate.is_lambda:
                    text = " ".join([ts.text for ts in self.evidence_for_node(candidate)])
                    yaml += " " * 2 * depth + link + ":\n"
                    yaml += " " * 2 * depth + "- - " + text + "\n"
                    yaml += " " * 2 * (depth + 1) + "- [" + str(len(full)) + ", " + str(len(full+text)) + "]\n"
                    full += text + " "
            if isinstance(candidate, Factor):
                for link in ["l2", "l", "r", "f"]:
                    nodes = candidate.nodes_for_link(link)
                    for node in nodes:
                        if node.id not in visited:
                            visited = visited | set([node.id])
                            queue.insert(0, [depth + 1, link, node])
        return "- '" + full[:-1] + "'\n- - " + yaml[9:-1]


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

