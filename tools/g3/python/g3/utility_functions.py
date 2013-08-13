import re

            
        

def depth_first_order_on_leaving(nbrs_dict, curr_nd, expanded, visited):
    # caution! it will only work on trees, not on multiply-connected graphs
    #print curr_nd
    expanded.append(curr_nd)
    for next_nd in nbrs_dict[curr_nd]:
        if next_nd not in expanded:
            visited = depth_first_order_on_leaving(nbrs_dict, next_nd, 
                                                   expanded, visited)
    visited.append(curr_nd)
    return visited

    



def ggg_to_dot_language(ggg, use_edge_labels=False):
    def get_node_by_id(idkey):
        for node in gstr["GG"]["nodes"]:
            if node['id']==idkey:
                return node

    gstr = ggg._graph.toYaml()
    gev = ggg.evidences
    dot = "digraph esdc_parse {\n"
   
    dot += '  super_root [label="" color="#FFFFFF"];\n'
    
    def node_label(nd):
        if gev.has_key(nd):
            result = re.escape(gev.get_string(nd))
        else:
            result = get_node_by_id(nd)['type'].replace("gamma_","")
        result = str(nd) + ": " + result
        return result
        
    def node_attr(nd):
        ans = ''
        if nd=="0" or nd==0: #hack for root node
            ans += ' style=filled fillcolor="#6BC3FA" pos="-0.5,3" pin=true'
        if gev.has_key(nd):
            return ' fontsize=20 shape=box style=filled fillcolor="#CFE8D2"'+ans
        if get_node_by_id(nd)['type']=='phi':
            return ' style=filled fillcolor="#CCCCCC"'+ans
        return ans

    
    nd_ids = [ node['id'] for node in gstr["GG"]["nodes"]]
    for nid in nd_ids:
        dot += '  '+str(nid)+' [label="'+str(node_label(nid))+'"'+\
                    node_attr(nid)+'];\n'
    
    dot += "\n"
    
    for node in gstr["GG"]["nodes"]:
        if node['type']=="gamma_EVENT":
            dot += '    super_root -> '+node['id']+'[color="#FFFFFF"];\n'
        
    fctr_ids = [ factor['id'] for factor in gstr["GG"]["factors"]]
    for fid in fctr_ids:
        #dot += '  '+str(fid)+' [label="factor_'+fid+'" shape=box];\n'
        dot += '  '+str(fid)+' [label="" shape=box style=filled'+\
                ' fillcolor="#000000" fixedsize="true" height="0.3" width="0.3"];\n'
    
    dot += "\n\n"
    
    def edge_relabel(lbl):
        if lbl in ['top','phi']:
            return '" "'        
        return str(lbl)
    
    for factor in gstr["GG"]["factors"]:
        for nkey in factor['nodes'].keys():
            for nd in factor['nodes'][nkey]:
                attr = ""
                if use_edge_labels:
                    attr = " [ label="+edge_relabel(nkey)+' fontcolor="#858585"]' 
                    # edge label and grey color
                dot += "  "+factor['id']+" -> "+nd+attr+";\n"
    
    dot += "}\n"
    return dot


    
