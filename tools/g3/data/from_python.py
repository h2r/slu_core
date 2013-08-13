import yaml

## To make sure the yaml is properly formatted

#node_1 = {
#    "id":"node_1",
#    "type":"lambda",
#    "value":{"Path":"none"}
#}

#node_2 = {
#    "id":"node_2",
#    "type":"gamma",
#    "value":{"Path":"none"}
#}

#factor_1 = {
#    "id":"factor_1",
#    "type":"LG_factor",
#    "nodes":{
#        "L_node":"node_1",
#        "G_node":"node_2"
#    }
#}


#graph = {
#    "GG":{
#        "nodes":[node_1,node_2],
#        "factors":[factor_1]
#    }
#}

#yamlrep = yaml.dump(graph)

import hashlib
h = hashlib.md5()
#h.update(yamlrep)

#print yamlrep

#print h.hexdigest()
#print type(h.hexdigest())

#bindings = [
#    {
#        "id":"node_1",
#        "value": "value_1"
#    },
#    {
#        "id":"node_2",
#        "value": "value_2"
#    }
#]

#dump = yaml.dump(bindings)
#h.update(dump)
#print h.hexdigest()




