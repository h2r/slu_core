import math
import sys
import rndf_util as ru
import spatial_features_cxx as sf
import numpy as na

def tmapFromRndf(loc_xy, rndf):
    '''Reads in an RNDF and returns a topological map of nodes based on
        the information provided.
    '''
    tmap = {}
    tmap_locs = {}

    if loc_xy != None:
        indicies = [0]
        tmap_locs[0] = loc_xy #first node is starting position, if specified

    #find start zone
    start_zone = None

    for zone in rndf.zone_polygons:
        if ru.is_interior_point(zone, loc_xy[0:2]):
            start_zone = zone
            break

    #remaining nodes are checkpoints in RNDF
    for chk_pt in rndf.checkpoints:
        wp = chk_pt.waypoint
        x,y = ru.latlon_to_xy(wp.lat, wp.lon, rndf.origin)
        #constrain map to single zone
        if start_zone and not ru.is_interior_point(start_zone, loc_xy[0:2]):
            continue

        assert chk_pt.id_int != 0

        indicies.append(chk_pt.id_int)      #add index of checkpoint            
        tmap_locs[chk_pt.id_int] = (x,y)    #add coordinates of checkpoint
        
    for i in tmap_locs:
        tmap[i] = indicies
            
    return tmap, tmap_locs  

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
    
    def __init__(self, rndfFname=None, 
                 tmap=None, tmap_locs=None, loc_xy=None):
        self.rndfFname = rndfFname

        if rndfFname:   #if RNDF given, create a tmap from it
            self.tmap, self.tmap_locs = tmapFromRndf(loc_xy, rndfFname)
        elif tmap and tmap_locs:    #otherwise simply store the tmap
            self.tmap = tmap
            self.tmap_locs = tmap_locs
        else:
            raise ValueError("Must supply rndf, skel file, or tmap and tmap_locs.")

    def __repr__(self):
        args = []
        for key in ["rndfFname", "tmap", 
                    "tmap_locs"]:
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

        
                    
    
                
