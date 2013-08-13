from scipy import transpose, array
from pyTklib import kNN_index

class topological_edge:
    def __init__(self, start_i, end_i, path):
        self.start_i = start_i
        self.end_i = end_i
        self.path = path

class topological_node:
    def __init__(self, index, xy):
        self.index = index
        self.xy = xy


class topological_map:
    def __init__(self, adj_list=None, nodes=None, edges=None):
        self.adj_list = adj_list
        self.nodes = nodes
        self.edges = edges

        #cache the edges
        self.edges_path = {}
        for edge in self.edges:
            if(not self.edges_path.has_key(edge.start_i)):
                self.edges_path[edge.start_i] = {}
            self.edges_path[edge.start_i][edge.end_i] = edge

        self.nodes_cache = {}
        for node in self.nodes:
            self.nodes_cache[node.index] = node

        self.nodes_xy = transpose([node.xy for node in self.nodes])
        #print "nodes_xy:", self.nodes_xy
        
    def closest_node(self, xy):
        #nodes_xy = transpose([node.xy for node in self.nodes])
        i, = kNN_index(xy, self.nodes_xy, 1)
        
        return self.nodes[int(i)]

    def next_nodes(self, node_list_I):
        next_nodes = []; 
        for next_i in self.adj_list[node_list_I[-1]]:
            if(not next_i in node_list_I):
                next_nodes.append(self.nodes_cache[next_i])
        
        return next_nodes

    def get_path(self, node_list_I):
        #print "node list:", node_list_I, len(node_list_I)
        if(len(node_list_I) == 1):
            n_xy = self.nodes_cache[node_list_I[0]].xy
            path = array([[n_xy[0], n_xy[0]],[n_xy[1], n_xy[1]],[1.5707, 1.5707]])
            return path
        
        path = [[],[],[]]
        for i in range(len(node_list_I)-1):
            #X position
            path[0].extend(self.edges_path[node_list_I[i]][node_list_I[i+1]].path[0])
            
            #Y position
            path[1].extend(self.edges_path[node_list_I[i]][node_list_I[i+1]].path[1])
            
            #Theta (orientation)
            path[2].extend(self.edges_path[node_list_I[i]][node_list_I[i+1]].path[2])
 
        return array(path)
