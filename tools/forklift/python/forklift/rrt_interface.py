import cPickle
from numpy import transpose, arctan2
import agile
import random
import sys

pi = 3.141

def hash_float(num):
    return int(round(num))

def round_orientation(num):
    #reduces orientation to 4 cardinal directions +- 45 degrees
    val =  int(3/pi * (num + pi/3))
    if val >= 5:
        val = 4
    elif val < 0:
        val = 0
    return val

def cacheRRT(action_map, cacheFname, obstacles=None):
    my_rrt = rrt()
    my_rrt.clearCache()

    if obstacles:
        my_rrt.setObstacles(obstacles)

    total = len(action_map.list_locations())**3 
    i = 0

    for x1,y1 in action_map.list_locations():
        for x2,y2 in action_map.list_locations():
            for x3,y3 in action_map.list_locations():
                stheta = arctan2(y2 - y1, x2 - x1)
                ftheta = arctan2(y3 - y2, x3 - x2)
                my_rrt.getPath(x2, y2, stheta, x3, y3, ftheta, 10)
                i+=1
                if i % 50 == 0:
                    print i,'of',total
    print "saving", cacheFname
    cPickle.dump(my_rrt.pathDict, open(cacheFname,'wb'), 2)

class rrt:
    def __init__(self, cacheFname=None):
        if not cacheFname:
           self.cacheFname = "../../data/directions/forklift/rrt_cache.pck"
        else:
            self.cacheFname = cacheFname

        try:
            print 'loading RRT cache'
            self.pathDict = cPickle.load(open(self.cacheFname,'rb'))
        except:
            self.pathDict = {}

        self.rrt = agile.mp_rrtstar_create()

    def setObstacles(self, obs_polys):
        agile.bb_planner_remove_obstacles(self.rrt)
        agile.mp_obstacle_test(self.rrt, obs_polys)
        
    def setSeed(self, seed):
        agile.set_random_seed( seed )

    def getPath(self, sx, sy, stheta, fx, fy, ftheta, iterations=1):
        args = (sx, sy, round_orientation(stheta), fx, fy, round_orientation(ftheta))
        args = tuple([hash_float(f) for f in args])

        if not args in self.pathDict:
            #print 'calculating path', args
            path = agile.bb_planner_get_path(self.rrt, sx, sy, stheta, fx, fy, ftheta, iterations)
            self.pathDict[args] = path

        return self.pathDict[args]

    def saveCache(self):
        cPickle.dump(self.pathDict, open(self.cacheFname,'wb'), 2)
        print 'rrt cache saved to', self.cacheFname

    def clearCache(self):
        self.pathDict = {}
        self.saveCache()
        
def test_rrt():
    my_rrt = agile.mp_rrtstar_create()
    agile.set_random_seed( 0 )
    random.seed( 0 )

    for i in range(10000):
        x1 = random.uniform(0,40)
        x2 = random.uniform(0,40)
        y1 = random.uniform(0,40)
        y2 = random.uniform(0,40)
        th1 = random.uniform(0,pi*2)
        th2 = random.uniform(0,pi*2)

        path = agile.bb_planner_get_path(my_rrt, x1, y1, th1, x2, y2, th2, 10)

        if i % 50 == 0:
            print 'run', i
def main():        

    cacheFname = "../../data/directions/forklift/rrt_cache.pck"
    skel_map = "../../data/directions/forklift/partitions/forklift_full_part.pck"
    rndf_map = "../../data/directions/forklift/Lee_RNDF_demo.txt"

    from forklift.task_planner import task_planner
    from forklift.action_map import action_map

    am = action_map(skel_map, connectAllNodes=True, rndfFname=rndf_map)

    cacheRRT(am, cacheFname)

if __name__=="__main__":
    if len(sys.argv) > 1:
        test_rrt()
    else:
        main()
    
