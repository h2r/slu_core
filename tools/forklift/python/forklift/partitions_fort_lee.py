from collections import defaultdict
import pyTklib as tk
from numpy import array
import rndf_util as ru
import math

class partitions(object):
    """
    Make a topological map with three dimensions
    """
    def __init__(self, skel, boundingBox=None):
        self._skel = skel
        #self.tmap = self._skel.tmap
        #self.tmap_locs = self._skel.tmap_locs

        new_tmap_id = max(self._skel.tmap_locs[0].keys()) + 1


        self.tmap_locs = dict(self._skel.tmap_locs)

        new_locs = [(17.9, 42.3),
                    (17.68, 46.08),
                    (15.85, 48.32),
                    (10.28, 51.23),
                    (19.51, 40.42),
                    (20.51, 38.18),
                    ]
        for loc in new_locs:
            self.tmap_locs[0][new_tmap_id] = array(loc)
            new_tmap_id += 1


        tmap = defaultdict(lambda : set())        
        for key1, loc1 in self.tmap_locs[0].iteritems():
            tmap[key1].update([])
            if key1 in self._skel.tmap[0]:
                tmap[key1].update(self._skel.tmap[0][key1])
            for key2, loc2 in self._skel.tmap_locs[0].iteritems():
                if key1 != key2 and tk.math2d_dist(loc1, loc2) < 3:
                    tmap[key1].add(key2)
                    tmap[key2].add(key1)
                pass

        for key1, children in tmap.iteritems():
            if len(children) == 0:
                lst = sorted([(key2, tk.math2d_dist(self.tmap_locs[0][key1],
                                                    self.tmap_locs[0][key2]))
                             for key2 in self.tmap_locs[0].keys()
                              if key1 != key2],
                             key=lambda t: t[1])
                closest_child = lst[0][0]
                tmap[key1].add(closest_child)

                
        tmap[1].add(22)
        tmap[22].add(1)  
                
        tmap = dict((key, array(list(value))) for key, value in tmap.iteritems())
        for key, value in tmap.iteritems():
            assert len(value) != 0
        self.tmap = {0:tmap}
        
        #self.tmap = dict(self._skel.tmap)

class checkpoints(object):
    """
    Make a topological map with three dimensions
    """
    def __init__(self, rndfFname, boundingBox=None):
        self.rndf = ru.rndf(rndfFname)
        
        tmap = {}
        tmap_locs = {}

        indicies = []
        for chk_pt in self.rndf.checkpoints:
            indicies.append(chk_pt.id_int)

        for chk_pt in self.rndf.checkpoints:
           wp = chk_pt.waypoint
           x,y = ru.latlon_to_xy(wp.lat, wp.lon, self.rndf.origin)

           #manual removal of node in other zone near (30, 0)
           if math.hypot(x - 30, y - 0) < 10:
               continue
           
           tmap_locs[chk_pt.id_int] = (x,y)
        
        for i in tmap_locs:
           tmap[i] = indicies
           
        self.tmap = {0:tmap}
        self.tmap_locs = {0:tmap_locs}
        
