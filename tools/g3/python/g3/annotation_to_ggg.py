from state import State
from esdcs.dataStructures import ExtendedSdc
from graph import GGG, Node, GroundingGraphStructure, Factor
from esdcs_to_ggg import ggg_from_esdc
from spatial_features.groundings import assignPathGroundings
from esdcs.esdcIo.annotationIo import Annotation

def compute_node_id(ggg, esdc):
    for factor_id in ggg.factor_ids:
        if ggg.factor_id_to_esdc(factor_id) == esdc:
            nid = ggg.factor_from_id(factor_id).nodes_for_link("top")[0].id
            return nid
    return None


def assignPathGroundingsToGGG(state, ggg):
    """
    Assign path groundings to a GGG, based on an annotation's agent
    path and stuff.  This deals with the implied 'you' of imperitive
    commands.
    """
    factors = [ggg.factor_from_id(f) for f in ggg.factor_ids]
    new_evidences = ggg.evidences
    for factor in factors:
        parent_node = factor.nodes_for_link("top")[0]
        if "EVENT" in parent_node.type:
            if len(new_evidences[parent_node.id]) == 0:
                new_evidences[parent_node.id] = [state.agent]
            #f of factor should be empty object grounded to agent
            #fig_node = factor.nodes_for_link("f")[0]
            #new_evidences = new_evidences.add(fig_node.id, [state.getAgentId()])
            
            if (factor.has_children("l") and len(factor.nodes_for_link("l")) 
                and "PATH" in factor.nodes_for_link("l")[0].type):
                child_node = factor.nodes_for_link("l")[0]                
                if len(new_evidences[child_node.id]) == 0:
                    new_evidences[child_node.id] =  [state.agent]
            elif (factor.has_children("l2") and 
                  len(factor.nodes_for_link("l2")) and 
                  "PATH" in factor.nodes_for_link("l2")[0].type):
                child_node = factor.nodes_for_link("l2")[0]
                figure_node = factor.nodes_for_link("l")[0]
                figure_gnd = ggg.evidences[figure_node.id]
                
                if figure_gnd and len(figure_gnd) > 0 and len(new_evidences[child_node.id]) == 0:
                    new_evidences[child_node.id] = figure_gnd
                    
    return new_evidences



class AnnotationState(State):
    def __init__(self):
        self.groundableDict = dict()
        self.object_ids = []
        self.place_ids = []
        self.grounding_to_id = {}

        self.unique_id = -1

    def getObjectsSet(self):
        return self.object_ids

    def getPlacesSet(self):
        return self.place_ids

    def getAgentId(self):
        return self.AGENT_ID

    @property
    def agent(self):
        return self.groundableDict[self.AGENT_ID]

    def setAgentGrounding(self, phys_obj):
        self.groundableDict[self.AGENT_ID] = phys_obj

    def addObject(self, obj_id, phys_obj):
        assert obj_id != None
        if not obj_id in self.object_ids:
            self.object_ids.append(obj_id)
        self.groundableDict[obj_id] = phys_obj

    def addPlace(self, place_id, phys_obj):
        if not place_id in self.place_ids:
            self.place_ids.append(place_id)
        self.groundableDict[place_id] = phys_obj


    def idForGrounding(self, grounding):
        try:
            if not grounding in self.grounding_to_id:
                self.grounding_to_id[grounding] = self.getUniqueId()
            
            return self.grounding_to_id[grounding]
        except:
            print "grounding", grounding, grounding.__class__
            raise



    def getUniqueId(self):
        self.unique_id += 1
        return self.unique_id

def ggg_to_annotation(ggg, assignment_id=None): 
    if assignment_id == None:
        assignment_id = "fromGGG%d" % id(ggg)
    
    a = Annotation(assignment_id, ggg.esdcs, context=ggg.context)

    for factor in ggg.factors:
        esdc = ggg.factor_to_esdc(factor)
        node = factor.nodes_for_link("top")[0]
        groundings = ggg.evidences[node.id]
        

        a.setGroundings(esdc, groundings)
        phi_value = ggg.evidences[factor.phi_node.id]
        if phi_value in [True, False]:
            a.setGroundingIsCorrect(esdc, phi_value)

    return a
        

def annotation_to_ggg_map(annotation, verbose=False):
    """
    Makes a separate ggg for each esdc.  This is necessary to
    correctly represent negative examples in training.  It returns the
    annotation state, which is necessary to map between grounding IDs
    (stored in the ggg.evidences) and actual grounding values.
    """
    esdc_to_ggg = {}
    a_state = AnnotationState()
    a_state.setAgentGrounding(annotation.agent)


    #necessary so that subgraphs have consistent groundings
    for esdc in annotation.flattenedEsdcs:
        assignPathGroundings(esdc, annotation)

    for i, center_esdc in enumerate(annotation.flattenedEsdcs):
        ggg = ggg_from_esdc(center_esdc)
        
        child_esdcs = [center_esdc]
        for field in center_esdc.fieldNames:
            child_esdcs.extend([esdc for esdc in center_esdc.children(field) if isinstance(esdc, ExtendedSdc)])

        center_node_id = compute_node_id(ggg, center_esdc)

        for i, esdc in enumerate(child_esdcs):

            node_id = compute_node_id(ggg, esdc)


            if node_id == None: #empty object for figure of event
                event_factor = ggg.esdc_to_factor(esdc)
                if event_factor == None:
                    continue
                node_id = event_factor.nodes_for_link("f")[0].id

            if i != 0 and node_id == center_node_id:
                continue

            new_evidence = ggg.evidences

            for grounding in annotation.getGroundings(esdc):
                new_id = a_state.idForGrounding(grounding)
                if esdc.type == "PLACE":
                    a_state.addPlace(new_id, grounding)
                else:
                    a_state.addObject(new_id, grounding)
                new_evidence = new_evidence.append_to_evidence(node_id, grounding)
            
            ggg = GGG.from_ggg_and_evidence(ggg, new_evidence)
            ggg.context = annotation.context

            ggg.annotation = annotation
        esdc_to_ggg[center_esdc] = ggg

    return a_state, esdc_to_ggg



def annotation_to_ggg(annotation, verbose=False):
    """
    Convert an annotation to a single merged ggg. 
    """
    
    a_state = AnnotationState()
    a_state.setAgentGrounding(annotation.agent)
    esdc_to_ggg = {}

    for top_level_esdc in annotation.esdcs:
        assignPathGroundings(top_level_esdc, annotation)
        ggg = ggg_from_esdc(top_level_esdc)
        new_evidence = ggg.evidences


        for esdc in annotation.flattenedEsdcs:
            node_id = compute_node_id(ggg, esdc)

            for grounding in annotation.getGroundings(esdc):
                #new_id = a_state.idForGrounding(grounding)
                new_id = grounding.id
                assert new_id != None
                if esdc.type == "PLACE":
                    a_state.addPlace(new_id, grounding)
                else:
                    a_state.addObject(new_id, grounding)
                new_evidence = new_evidence.append_to_evidence(node_id, grounding)

        ggg = GGG.from_ggg_and_evidence(ggg, new_evidence)
        ggg.context = annotation.context
        ggg.annotation = annotation
        esdc_to_ggg[top_level_esdc] = ggg

    return a_state, esdc_to_ggg


def annotations_to_flattened_gggs(annotations):
    """
    Return a list of gggs, one for each top level event. 
    """
    gggs = []
    for i, annotation in enumerate(annotations):
        astate, esdc_to_ggg = annotation_to_ggg(annotation)
        for esdc in sorted(esdc_to_ggg.keys()):
            ggg = esdc_to_ggg[esdc]
            #new_evidences = assignPathGroundingsToGGG(astate, ggg)
            #ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
            ggg.annotation = annotation
            gggs.append(ggg)
    return gggs


def collapse_null_nodes(ggg):
    """
    Might not push forward with this strategy. An attempt to merge
    figure and top, but it doesn't work because sometimes figure is a
    lambda node, and sometimes a gamma node. 
    """
    nodes = ggg.nodes
    factor_to_link_to_nodes = {}


    for factor in ggg.factors:
        d = dict((ln, [ggg.node_from_id(nid) for nid in nids]) 
                 for ln, nids in factor.link_name_to_node_ids.iteritems())
        factor_to_link_to_nodes[factor] = d
    
    for factor, ln_to_nodes in factor_to_link_to_nodes.iteritems():
        tops = factor.nodes_for_link("top")
        assert len(tops) == 1
        top = tops[0]
        
        figures = factor.nodes_for_link("f")
        assert len(figures) == 1
        figure = figures[0]

        for top_factor in top.factors:
            ln = top_factor.link_for_node(top)
            i = factor_to_link_to_nodes[top_factor][ln].index(top)
            factor_to_link_to_nodes[top_factor][ln][i] = figure

    all_nodes = set()
    new_factors = []
    for factor, ln_to_nodes in factor_to_link_to_nodes.iteritems():
        ln_to_node_ids = {}
        for ln, nodes in ln_to_nodes.iteritems():
            all_nodes.update(nodes)
            if ln != "top":
                ln_to_node_ids[ln] = [n.id for n in nodes]
            
        new_factors.append(Factor(factor.id, factor.type, ln_to_node_ids))

    new_nodes = [Node(n.id, n.type) for n in all_nodes]

    ggs = GroundingGraphStructure(new_nodes, new_factors)
    new_ggg = GGG(ggs, ggg.evidences, ggg._factor_id_to_esdc, 
                  context=ggg.context, parent_esdc_group=ggg.esdcs)
    return new_ggg

