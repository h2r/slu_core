import math
import sys
import spatial_features_cxx as sf
import numpy as na

def tmapFromObjectsAndPlaces(loc_xy, objects, places):
    place_indices = set()
    for o in objects:
        distances = [sf.math2d_dist(o.centroid2d, p.centroid2d) for p in places]
        min_idx = na.argmin(distances)
        distances[min_idx] = sys.maxint
        # second closest place, so it's not the one right on top of the object.
        min_idx = na.argmin(distances)
        place_indices.add(min_idx)
    return tmapFromObjects(loc_xy, [places[i] for i in place_indices],
                           add_offset=False)

def tmapFromObjects(loc_xy, objects, add_offset=True):
    """
    Takes in a set of objects and returns a topographical map based on
    the locations of the objects.
    """
    tmap = {}
    tmap_locs = {}
    locs = set()
    indices = []
    id_cntr = 0

    if loc_xy != None:
        indices.append(id_cntr)
        tmap_locs[id_cntr] = loc_xy
        locs.add(tuple(loc_xy))
        id_cntr += 1

    for x,y in [o.centroid2d for o in objects]:

        if not (x, y) in locs:
            locs.add((x, y))
            indices.append(id_cntr)    # add index of object          
            tmap_locs[id_cntr] = (x,y)  # add coordinates of object
            id_cntr += 1
            if add_offset:
                offset = sf.math2d_get_scale(sf.math2d_bbox(o.points_xy))
                # add offset location for movements
                indices.append(id_cntr)
                tmap_locs[id_cntr] = (x + offset, y)
                id_cntr += 1
            


    for i in tmap_locs:
        tmap[i] = indices

    return tmap, tmap_locs  

class ActionMap:
    """
    Takes in an RNDF or a topographical map and defines an action map
    accordingly.
    """
    
    def __init__(self, tmap=None, tmap_locs=None, loc_xy=None):

        if tmap and tmap_locs:    #otherwise simply store the tmap
            self.tmap = tmap
            self.tmap_locs = tmap_locs
        else:
            raise ValueError("Must supply rndf, skel file, or tmap and tmap_locs.")

    def __repr__(self):
        args = []
        for key in ["tmap", "tmap_locs"]:
            args.append(key + "=" + repr(eval("self.%s" % key)))
        result = "ActionMap(" + ",".join(args) + ")"
        return result

    def list_locations(self):
        #returns list of all locations in the tmap
       return self.tmap_locs.values()

    def list_indicies(self):
        #returns list of all indices of nodes in the tmap
        return self.tmap_locs.keys()

    def neighbors_by_index(self, idx):
        #returns the list of indices in the tmap
        return sorted(self.tmap.keys())

    def index_to_location(self, idx):
        #returns the coordinate representation of the location index
        return self.tmap_locs[idx]

    def nearest_index(self, loc):
        #returns the index of the nearest node in the tmap
        x = loc[0]
        y = loc[1]
        min_dist = float('inf')
        min_idx = None
        for i in self.tmap_locs:
            lx, ly = self.tmap_locs[i]
            d = math.hypot(x - lx, y - ly)
            if d < min_dist:
                min_dist = d
                min_idx  = i
        return min_idx

        
                    
    
                
