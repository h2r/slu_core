"""
This code creates a GGG class from an ESDC tree-parse.

@input Python dictionary containing the ESDC:
    Example: {'EVENT': {'r': 'Go', 'l': {'PATH': {'r': [['past', [3, 7]]], 'l': {'OBJECT': {'r': [['past', [18, 22]]], 'l': 'the stairs', 'f': 'the truck'}}}}}}
@output GGG class representing this graph.

Properties of the GGG graph.

- nodetypes: lambda, phi, gamma_OBJECT, gamma_PLACE, 
             gamma_PATH, gamma_EVENT
             
For each ESDC up to two factors are created
    - figure factor:
        connected to a lambda node child("f"), 
        and a correspondence variable node ("phi")
    - relation factor 
        connected to a correspondence variable node ("phi")
        relation lambda node ("r")
        and optionally "l" and "l2" gamma_OBJECT nodes
    Both factors are connected to the parent gamma_?? node as "top"        
"""


from standoff import TextStandoff


from g3.graph import GroundingGraphStructure, Evidences, GGG, \
    empty_grounding_graph_yaml
from esdcs.dataStructures import ExtendedSdc, wrapValueInList

#from esdcs.esdcIo import yamlReader, yamlWriter
#TODO import TextStandoff from somewhere


class IDCounter:
    def __init__(self):
        self.count = -1
    def next_id_will_be(self):
        return str(self.count + 1)
    def next_id(self):
        self.count += 1
        return str(self.count)

def gamma_node_type(desc):
    return "gamma_"+desc
    
def ggg_from_esdc_group(esdc_group, cntr=None, create_lambda=False, use_top_id=None):
    assert len(esdc_group) == 1
    return ggg_from_esdc(esdc_group[0])
     
def gggs_from_esdc_group(esdc_group):
    gggs = []
    for esdc in esdc_group:
        gggs.append(ggg_from_esdc(esdc))
    return gggs                  

def ggg_from_esdc(esdc, cntr=None, create_lambda=False, use_top_id=None):
    """
    Create a grounding graph from an esdc.
    """

    factors_to_esdcs = {}
    
    if cntr == None:
        #global counter
        cntr = IDCounter()

    def idstr():
        return str(cntr.next_id())
      
    ans_gg = empty_grounding_graph_yaml()
    ans_ev = Evidences()
     
    # Hack to compensate for the nested figure hack.
    if create_lambda or isinstance(esdc, TextStandoff):
        my_id = idstr()
        ans_gg["GG"]["nodes"].append(
            {"id": my_id ,
             "type": "lambda"
             })
        
        if isinstance(esdc, ExtendedSdc):
            # This should normally never happen, figure should only contain text
            ans_ev[my_id] = esdc[0].fields['f']
        else:
            ans_ev[my_id] = wrapValueInList(esdc)
        return GGG(GroundingGraphStructure.fromYaml(ans_gg), 
                   ans_ev, factors_to_esdcs)

     
    # ESDC type?
    node_desc = esdc.type
    
    # top node
    if use_top_id != None:
        top_id = use_top_id
    else:
        top_id = idstr()
         #TODO factors to esdcs
        top_type = gamma_node_type(node_desc)
        ans_gg["GG"]["nodes"].append(
            {"id": top_id, "type":top_type})
        
    curr_graph_structure = GroundingGraphStructure.empty_graph()
    curr_evidences = Evidences()  
    
    if esdc.isLeafObject():
        
        if len(esdc.fields['f']) > 0:            
            corr_f_id = idstr()
            ans_gg["GG"]["nodes"].append(
                {"id": corr_f_id, "type":"phi"})

            
            # curr_f_factor and curr_rll_factor
            curr_factor_id = idstr()
            curr_f_factor = {
                "id": curr_factor_id,
                "type": "factor_f_"+node_desc,
                "nodes":{"top": [top_id],"phi":[corr_f_id]}}
            factors_to_esdcs[curr_factor_id] = esdc
            
            curr_f_factor["nodes"]['f']= [cntr.next_id_will_be()]
            new_esdc = esdc.fields['f'] 
            next_ggg = ggg_from_esdc(new_esdc, cntr, create_lambda=True)
            factors_to_esdcs.update(next_ggg._factor_id_to_esdc)
            curr_graph_structure = \
                curr_graph_structure.attach_graph(next_ggg._graph)
            curr_evidences = Evidences.merge(curr_evidences, next_ggg.evidences)
            
            ans_gg["GG"]["factors"].append(curr_f_factor)
    
    else:  # not a leaf object:      
        # must have relation    

        # correspondence    
        corr_rl_id = idstr()
        ans_gg["GG"]["nodes"].append(
            {"id":corr_rl_id, "type":"phi"})

        # curr_f_factor and curr_rll_factor
        curr_factor_id = idstr()
        curr_rl_factor = {
            "id":str(curr_factor_id),
            "type": "factor_rl_"+node_desc,
            "nodes":{"top":[top_id],"phi":[corr_rl_id]}}      

        curr_rl_factor["nodes"]["r"] = [cntr.next_id_will_be()]
        new_esdc = esdc.fields['r']
        factors_to_esdcs[curr_factor_id] = esdc
        next_ggg = ggg_from_esdc(new_esdc, cntr, create_lambda=True)
        factors_to_esdcs.update(next_ggg._factor_id_to_esdc)
        curr_graph_structure = \
            curr_graph_structure.attach_graph(next_ggg._graph)
        curr_evidences = Evidences.merge(curr_evidences, next_ggg.evidences)

        for child in ["f","l","l2"]:
            if node_desc == "OBJECT" and child=='f':
                to_use_top_id = top_id
            else:
                to_use_top_id = None
            curr_rl_factor["nodes"][child] = []
            for new_esdc in esdc.fields[child]: 
                if not to_use_top_id:              
                    next_id_will_be = cntr.next_id_will_be()
                    curr_rl_factor["nodes"][child].append(next_id_will_be)
                next_ggg = ggg_from_esdc(new_esdc,     
                                         cntr, use_top_id=to_use_top_id)
                factors_to_esdcs.update(next_ggg._factor_id_to_esdc)
                curr_graph_structure = \
                    curr_graph_structure.attach_graph(next_ggg._graph)
                curr_evidences = Evidences.merge(curr_evidences, 
                                                 next_ggg.evidences)
        ans_gg["GG"]["factors"].append(curr_rl_factor)  
    

    gbase = GroundingGraphStructure.fromYaml(ans_gg)

    return GGG(gbase.attach_graph(curr_graph_structure),
               curr_evidences,
               factors_to_esdcs)

     
     
     
     
     
#############################################
def is_esdc(dct):
    if type(dct)==type({}):
        if len(dct.keys())==1 and \
            dct.keys()[0] in ['EVENT','OBJECT','PATH','PLACE']\
            and is_sdc(dct[dct.keys()[0]]):            
            return True
    return False
    
def is_sdc(dct):
    if type(dct)==type({}):
        for key in dct.keys():
            if key not in ['r','f','l','l2']:
                return False
        return True
    return False    
    

def esdc_has_nice_format(esdc):
    if not is_esdc(esdc):
        raise BaseException(str(esdc)+"\nError: not proper dictionary")
    esdc_type = esdc.keys()[0]
    sdc = esdc[esdc_type]
    if esdc_type == "EVENT":
        if not (sdc.has_key('r') and (sdc.has_key('l') or sdc.has_key('f'))):
            raise Exception(str(sdc)+"\nError: EVENT Esdc needs to have both relation and landmark/figure")
        if sdc.has_key('l'):
            lf_has_nice_format(sdc['l'])
        if sdc.has_key('f'):
            lf_has_nice_format(sdc['f'])
        return True
    if esdc_type == "OBJECT":
        if sdc.has_key('r'):
            r_has_nice_format(sdc['r'])
        if sdc.has_key('f'):
            lf_has_nice_format(sdc['f'])
        if sdc.has_key('l'):
            lf_has_nice_format(sdc['l'])
        return True    
    if esdc_type == "PATH":
        if sdc.has_key('r'):
            r_has_nice_format(sdc['r'])
        if sdc.has_key('f'):
            lf_has_nice_format(sdc['f'])
        if sdc.has_key('l'):
            lf_has_nice_format(sdc['l'])
        return True     
    if esdc_type == "PLACE":
        if sdc.has_key('r'):
            r_has_nice_format(sdc['r'])
        if sdc.has_key('f'):
            lf_has_nice_format(sdc['f'])
        if sdc.has_key('l'):
            lf_has_nice_format(sdc['l'])
        return True         
            
    raise (esdc,"\nError: the type of esdc needs to be EVENT or OBJECT")
        
def lf_has_nice_format(lf):
    """
    For landmarks and figures
    """
    if type(lf)==type("string"):
        return True
    elif type(lf)==type([]):
        return True #text standoffs
    esdc_has_nice_format(lf)
    
def r_has_nice_format(r):
    """
    For relations
    """
    if type(r)==type("string"):
        return True
    elif type(r)==type([]):
        return True #text standoffs
    raise (r,"needs to be string")
