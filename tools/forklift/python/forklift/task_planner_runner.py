from arlcm.pallet_t import pallet_t
from arlcm.object_t import object_t
from arlcm.object_enum_t import object_enum_t
from task_planner import task_planner
from esdcs.extractor.stanfordParserExtractor import Extractor
import esdcs.dataStructures as ds
import fork_state
import action_map
import math
from rndf_util import rndf, is_interior_point

def gen_cost(esdc, dict, action_map=None):
    if esdc.type == "OBJECT":
        cost = 10
        for f in esdc.f:
            #print dir(f)
            if dict[esdc].get_tag().find(f.text) > -1:
                cost = cost - 5
        return cost
    if esdc.type == "PLACE":
        cost = 10
        for l in esdc.l:
            obj = dict[l]
            loc = dict[esdc]
            if is_interior_point(obj, loc):
                return 0
        return cost
    if esdc.type == "EVENT":
        ss = dict[esdc]
        c = 0
        for i in range(len(ss)-1):
            l1 = action_map.tmap_locs[ss[i][0].agent]
            l2 = action_map.tmap_locs[ss[i+1][0].agent]
            
            c += math.hypot(l1[0] - l2[0], l1[1] - l2[1])

            if ss[i][1] and (isinstance(ss[i][1], fork_state.pickup) or isinstance(ss[i][1], fork_state.place)):
                c+=10
                
        endx, endy = ss[-1][0].get_pos(action_map)
        goalx, goaly = (7, 54)
        dist_to_goal = math.hypot(endx - goalx, endy - goaly)
        
        return c + dist_to_goal**2
    
    return 0

def tp_test():
    ex = Extractor()
    #parse = ex.extractEsdcs("Pick up the tire pallet next to the truck.")
    parse = ex.extractEsdcs("Put the tire pallet on storage.")
    esdc = parse[0]
       
    am = action_map.action_map("../../data/directions/forklift/partitions/forklift_full_part.pck")
    tp = task_planner(am, gen_cost, gen_cost, gen_cost, gen_cost)

    s1 = fork_state.fork_state()
    s1.pallets = [pallet_t(), pallet_t()]
    s1.objects = [object_t(), object_t()]
  
    s1.pallets[0].id = 0
    s1.pallets[0].label = pallet_t.LABEL_TIRE
    s1.pallets[0].pos = [88,125,0]
    s1.pallets[0].bbox_min = [88,125,0]
    s1.pallets[0].bbox_max = [89,126,0]

    s1.pallets[1].id = 1
    s1.pallets[1].label = pallet_t.LABEL_ENGINE
    s1.pallets[1].pos = [113, 41, 0]
    s1.pallets[1].bbox_min = [113,41,0]
    s1.pallets[1].bbox_max = [114,42,0]

    s1.objects[0].object_type = object_enum_t.FLATBED_TRUCK
    s1.objects[0].pos = [88,125,0]
    s1.objects[0].bbox_min = [88,125,0]
    s1.objects[0].bbox_max = [89,126,0]

    s1.objects[1].object_type = object_enum_t.FLATBED_TRAILER
    s1.objects[1].pos = [88,125,0]
    s1.objects[1].bbox_min = [88,125,0]
    s1.objects[1].bbox_max = [89,126,0]

    rndf_map = rndf("../../data/directions/forklift/Lee_RNDF_demo.txt")
    s1.zones = rndf_map.zone_polygons[:]
    
    s1.agent = 0

    plan = tp.find_plan(esdc, s1, 100)
    c, p = plan[0]
    
    def printMapping(x):
        if hasattr(p[x], 'tag'):
            print 'mapped ', x.type, map(lambda s: s.text, x.f), ' to ', p[x].tag
        elif x.type == 'EVENT':
            print 'mapped', x.type, 'to:'
            ss = p[x]
            for s,a in ss:
                if a != None:
                    print a, am.index_to_location(a.to_loc)
        else:
            print 'mapped', x.type, '('+str(x)+')', ' to ', p[x]
        print '---------------------'
    
    print '-----------------'
    ds.breadthFirstTraverse(esdc, printMapping)
    print c
    
tp_test()
