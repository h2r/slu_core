#from occupancy_grid_mapping2D import occupancy_grid_map
#from tag_util import *
import math
from math import cos, sin, sqrt, atan2
from geometry_2d import point, polygon
from cPickle import dump

def rndf_to_carmen_gridmap(rndf, mapfilename, tagfilename):
    print "TO GRID MAP"
    box = rndf.bounding_box()
    origin = rndf.origin

    corner1 = latlon_to_xy(origin[0], origin[1], origin)
    corner2 = latlon_to_xy(box[2], box[3], origin)
    
    xsize = abs(corner1[1] - corner2[1])
    ysize = abs(corner1[0] - corner2[0])
    
    ogm = occupancy_grid_mapper(0.9, 0.9, .5, xsize+20, ysize+20, 0.1, [0,0], 0.17)

    #get zone polygons
    free_polygons = rndf.zone_polygons[:]
    print free_polygons
    #get obstacle polygons
    obs_polygons = rndf.obs_polygons[:]
   
    #get lane polygons
    lane_polygons = rndf.lane_polygons[:]

    tot_points = int(xsize/ogm.map.resolution)*int(ysize/ogm.map.resolution)
    num_checked = 0
    
    for j in range(0,int(xsize/ogm.map.resolution)):
        for i in range(0,int(ysize/ogm.map.resolution)):
            xy = ogm.map.to_xy([i,j])
            
            is_free = 0
            for poly in free_polygons:
                dist = math.hypot(xy[0] - poly.cx, xy[1] - poly.cy)
                if dist < poly.radius and is_interior_point(poly, xy):
                    is_free = 1
                    break

            for poly in lane_polygons:
                dist = math.hypot(xy[0] - poly.cx, xy[1] - poly.cy)
                if is_free or (dist < poly.radius and is_interior_point(poly, xy)):
                    is_free = 1
                    break
                
            for obs in obs_polygons:
                dist = math.hypot(xy[0] - obs.cx, xy[1] - obs.cy)
                if dist < obs.radius and is_interior_point(obs, xy):
                    is_free = -1
                    break
                
            if is_free > 0:
                ogm.map.set_value(i,j,-100)
            elif is_free < 0:
                ogm.map.set_value(i,j, 100)

            if(num_checked % 10000 == 0):
                print 'on point',num_checked,'of',tot_points
            num_checked += 1

    #print ogm.map.to_probability_map()
    ogm.map.save_carmen_map(mapfilename)
    tag_polys = [o for o in obs_polygons if obs.tag] + free_polygons
    out_polys = []
    for poly in tag_polys:
        p = polygon()
        p.tag = poly.tag
        for i in range(len(poly.X)):
            p.X.append(round(poly.X[i]/ogm.map.resolution))
            p.Y.append(round(poly.Y[i]/ogm.map.resolution))
        out_polys.append(p)
        
    tag_points = []
    for pt in rndf.checkpoints:
        if not pt.name:
            continue
        xy = latlon_to_xy(pt.waypoint.lat, pt.waypoint.lon, origin)
        x = round(xy[0]/ogm.map.resolution)
        y = round(xy[1]/ogm.map.resolution)
        tag_points.append(point(x, y, pt.name.lower()))
                          
    save_polygons(out_polys, tag_points, tagfilename)

    return ogm

def latlon_to_xy(lat, lon, center):
    c_lat, c_lon = center
    REQ = 6378.135e3 #meters
    RPO = 6356.750e3
    
    latrad = math.pi / 180 * c_lat
    center_r = REQ*RPO / sqrt(REQ*REQ - (REQ*REQ - RPO*RPO) * cos(latrad)**2)

    dlon = (lon - c_lon) * math.pi / 180;
    dlat = (lat - c_lat) * math.pi / 180;

    x = sin(dlon) * center_r * cos(c_lat * math.pi / 180);
    y = sin(dlat) * center_r;

    return [x, y]

def xy_to_latlon(x, y, center):
    c_lat, c_lon = center
    REQ = 6378.135e3 #meters
    RPO = 6356.750e3
    
    latrad = math.pi / 180 * c_lat
    center_r = REQ*RPO / sqrt(REQ*REQ - (REQ*REQ - RPO*RPO) * cos(latrad)**2)

    dlon = math.asin( x / (center_r * math.cos( c_lat * math.pi / 180)))
    dlat = math.asin( y / center_r)

    lat = c_lat + dlat * 180 / math.pi;
    lon = c_lon + dlon * 180 / math.pi;

    return [lat, lon]

def is_interior_point(polygon, point):
    """
    Determine if a point is inside a polygon
    """
    x, y = point
    c = False
    for (x1, y1), (x2, y2) in polygon.all_segments():
        if x == x1 and y == y1:
            return True
        if ((((y1 <= y) and (y < y2)) or
             ((y2 <= y) and (y < y1))) and
            (x < ((x2 - x1) * (y - y1)) / float(y2 - y1) + x1)):
            c = not c
    return c

def find_region_by_point(point, rndf):

    for zone in rndf.zones:
        if is_interior_point(zone.poly, point):
            return zone
    for seg in rndf.segments:
        for lane in seg.lanes:
            if is_interior_point(lane.poly, point):
                return lane
    return None
                
def xy_path_to_waypoints(path, rndf):
    '''
    takes a sequence of xy points and returns the RNDF transition waypoints
    along the path
    '''
    trans_region = None
    actual_region = None
    point = path[0]
    rndf_waypoints = []
    
    actual_region = find_region_by_point(point, rndf)
    assert(actual_region != None)
    trans_region = actual_region

    for pos in range(1, len(path)):
        point = path[pos]
        if not is_interior_point(actual_region.poly, point):
            #just exited current region, need rndf transitons
            min_dist = float('inf')
            exit_transition = None
            for tup in trans_region.exits:
                wp = rndf.get_object_by_id(tup[0])
                xy = latlon_to_xy(wp.lat, wp.lon, rndf.origin)
                dist = math.hypot(xy[0] - point[0], xy[1] - point[1])
                if dist < min_dist:
                    min_dist = dist
                    exit_transition = tup
            
            rndf_waypoints.append(exit_transition)
            trans_region = rndf.get_object_by_id(exit_transition[1].rsplit(".",1)[0])
            actual_region = find_region_by_point(point, rndf)
        else:
            pass

    return rndf_waypoints

def robot_pose_to_rndf(xyz, trans_xyz, trans_theta, trans_latlon, rndf):
    '''
    Turns an xyz in the robot frame to an xyz in the rndf frame as defined by the trans parameters
    trans_xyz is a robot xyz corresponding to trans_latlon
    trans_th is the heading of the robot relative to north
    '''
    th = trans_theta
    x1, y1, z1 = xyz
    x2, y2, z2 = trans_xyz
    #unrotate robot coordinate frame
#    dx = -sec2th*((trans_xyz[0]-xyz[0])*math.cos(th) + (-trans_xyz[1] + xyz[1])*math.sin(th))
#    dy = -sec2th*((trans_xyz[1]-xyz[1])*math.cos(th) + (-trans_xyz[0] + xyz[0])*math.sin(th))
    deltaX = x1 - x2; deltaY = y1 - y2;
    dx = deltaX*math.cos(th) + deltaY*math.sin(th)
    dy = deltaY*math.cos(th) - deltaX*math.sin(th)

    lat, lon = xy_to_latlon(dx, dy, trans_latlon)
    rndf_x, rndf_y = latlon_to_xy(lat, lon, rndf.origin)
    rndf_z = xyz[2] - trans_xyz[2]

    return (rndf_x, rndf_y, rndf_z)

def rndf_pose_to_robot(xyz, trans_xyz, trans_theta, trans_latlon, rndf):
    '''
    Turns an xyz in the rndf frame to an xyz in the robot frame as defined by the trans parameters
    trans_xyz is a robot xyz corresponding to trans_latlon
    trans_th is the heading of the robot relative to north
    '''
    th = trans_theta
    lat, lon = xy_to_latlon(xyz[0], xyz[1], rndf.origin)
    dx, dy = latlon_to_xy(lat, lon, trans_latlon)

    robot_x = dx * math.cos(th) + dy * math.sin(th) + trans_xyz[0]
    robot_y = dx * math.sin(th) + dy * math.cos(th) + trans_xyz[1]
    robot_z = xyz[2] + trans_xyz[2]

    return (robot_x, robot_y, robot_z)


class rndf_waypoint:
    def __init__(self):
        self.id = 0
        self.lat = 0
        self.lon = 0
        self.parent = None

class rndf_lane:
    def __init__(self):
        self.id = 0
        self.num_waypoints = 0
        self.width = 0
        self.exits = []
        self.waypoints = []
        self.poly = None

class rndf_spot:
    def __init__(self):
        self.id = 0
        self.width = 0
        self.waypoints = []
        self.checkpoint_id = 0
        self.parent = None

class rndf_checkpoint:
    def __init__(self):
        self.id = 0
        self.id_int = 0
        self.waypoint = None
        self.name = None

class rndf_segment:
    def __init__(self):
        self.id = 0
        self.parent = None
        self.num_lanes = 0
        self.segment_name = None
        self.lanes = []

class rndf_zone:
    def __init__(self):
        self.id = 0
        self.num_spots = 0
        self.name = None
        self.num_peripoints = 0
        self.perimeter = []
        self.spots = []
        self.exits = []
        self.poly = None

class rndf_obstacle:
    def __init__(self):
        self.name = None
        self.lat = 0
        self.lon = 0
        self.w1 = 0
        self.w2 = 0
        self.height = 0
        self.orient = 0
        
class rndf:

    def __init__(self, rndf_filename, enhance=False):
        self.filename = rndf_filename

        rndf_file = open(rndf_filename, 'r')
        self.enhance = enhance
        self.segments = []
        self.zones = []
        self.obstacles = []
        self.checkpoints = []
        self.id_dict = {}
        segment_num = 0
        zone_num = 0
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]

            if cmd == "RNDF_name":
                self.name = arg[0]
            elif cmd == "num_segments":
                self.num_segments = int(arg[0])
            elif cmd == "num_zones":
                self.num_zones = int(arg[0])
            elif cmd == "format_version":
                if arg:
                    self.format_version = arg[0]
            elif cmd == "creation_date":
                self.creation_date = arg[0]
            elif cmd == "segment":
                segment = rndf_segment()
                segment.id = int(arg[0])
                segment.parent = self
                self.parse_segment(rndf_file, segment)
                self.segments.append(segment)
                self.id_dict[segment.id] = segment
            elif cmd == "zone":
                zone = rndf_zone()
                zone.id = int(arg[0])
                zone.parent = self
                self.parse_zone(rndf_file, zone)
                self.zones.append(zone)
                self.id_dict[zone.id] = zone
            elif cmd == "num_obstacles":
                self.num_obstacles = int(arg[0])
                #read in all obstacles
                for i in range(self.num_obstacles):
                    o = rndf_obstacle()
                    self.read_obstacle(rndf_file, o)
                    self.obstacles.append(o)
            elif cmd == "end_file":
                break
            
        #2nd pass to get checkpoints/exits
        rndf_file = open(rndf_filename, 'r')
        zone_num = 0
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]
            
            if cmd == "zone":
                zone = self.zones[zone_num]
                zone_num += 1
                self.parse_zone_pass2(rndf_file, zone)
            elif cmd == "end_file":
                break

        self.build_polygons()

    def get_object_by_id(self, idstring):
        return self.id_dict[idstring]
    
    def bounding_box(self):
        min_lat = float('inf')
        for z in self.zones:
            min_lat = min([min_lat]+[p.lat for p in z.perimeter])
        for obs in self.obstacles:
            min_lat = min([min_lat, obs.lat])

        max_lat = -float('inf')
        for z in self.zones:
            max_lat = max([max_lat]+[p.lat for p in z.perimeter])
        for obs in self.obstacles:
            max_lat = max([max_lat, obs.lat])

        min_lon = float('inf')
        for z in self.zones:
            min_lon = min([min_lon]+[p.lon for p in z.perimeter])
        for obs in self.obstacles:
            min_lon = min([min_lon, obs.lon])
            
        max_lon = -float('inf')
        for z in self.zones:
            max_lon = max([min_lon]+[p.lon for p in z.perimeter])
        for obs in self.obstacles:
            max_lon = max([max_lon, obs.lon])

        return [min_lat, min_lon, max_lat, max_lon]
    
    def parse_segment(self, rndf_file, segment):
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]

            if cmd == "segment_name":
                segment.name = arg[0]
            elif cmd == "num_lanes":
                segment.num_lanes = int(arg[0])
            elif cmd == "lane":
                lane = rndf_lane()
                lane.id = arg[0]
                lane.parent = segment
                self.parse_lane(rndf_file, lane)
                segment.lanes.append(lane)
                self.id_dict[lane.id] = lane
            elif cmd == "end_segment":
                return segment

    def parse_lane(self, rndf_file, lane):
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]

            if cmd == "num_waypoints":
                lane.num_waypoints = int(arg[0])
            elif cmd == "lane_width":
                lane.width = int(arg[0])
            elif cmd == "exit":
                lane.exits.append([arg[0], arg[1]])
            elif len(cmd.split(".")) == 3:
                ids = cmd.split(".")
                seg_id = ids[0]
                lane_id = ids[1]
                pt_id = ids[2]

                #parse waypoint
                wp = rndf_waypoint()
                wp.id = cmd
                wp.lat = float(arg[0])
                wp.lon = float(arg[1])
                wp.parent = lane

                lane.waypoints.append(wp)
                self.id_dict[wp.id] = wp
            elif cmd == "end_lane":
                return lane

    def parse_zone(self, rndf_file, zone):
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]

            if cmd == "zone_name":
                zone.name = arg[0]
            elif cmd == "num_spots":
                zone.num_spots = arg[0]
            elif cmd == "spot":
                spot = rndf_spot()
                spot.id = arg[0]
                spot.parent = zone
                self.parse_spot(rndf_file, spot)
                zone.spots.append(spot)
                self.id_dict[spot.id] = spot
            elif cmd == "perimeter":
                zoneid = arg[0].split(".")[0]
                periid = arg[0].split(".")[1]
                self.parse_perimeter(rndf_file, zone)
                self.id_dict[arg[0]] = zone #make perimeter id also point to zone
            elif cmd == "end_zone":
                return zone
            

    def parse_spot(self, rndf_file, spot):
         while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]

            if cmd == "spot_width":
                spot.width = arg[0]
            elif len(cmd.split(".")) == 3:
                ids = cmd.split(".")
                seg_id = ids[0]
                lane_id = ids[1]
                pt_id = ids[2]

                #parse waypoint
                wp = rndf_waypoint()
                wp.id = cmd
                wp.lat = float(arg[0])
                wp.lon = float(arg[1])
                wp.parent = spot

                spot.waypoints.append(wp)
                self.id_dict[wp.id] = wp
            elif cmd == "end_spot":
                return spot

    def parse_perimeter(self, rndf_file, zone):
         while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]

            if cmd == "num_perimeterpoints":
                zone.num_peripoints = arg[0]
            elif cmd == "exit":
                zone.exits.append([arg[0], arg[1]])
            elif len(cmd.split(".")) == 3:
                ids = cmd.split(".")
                zone_id = ids[0]
                pt_id = ids[2]

                #parse waypoint
                wp = rndf_waypoint()
                wp.id = cmd
                wp.lat = float(arg[0])
                wp.lon = float(arg[1])
                wp.parent = zone

                zone.perimeter.append(wp)
                self.id_dict[wp.id] = wp
            elif cmd == "end_perimeter":
                return

    def read_obstacle(self, rndf_file, obstacle):
        l = rndf_file.readline()
        args = l.split()

        obstacle.id = args[0]
        obstacle.lat = float(args[1])
        obstacle.lon = float(args[2])
        obstacle.w1 = float(args[3])
        obstacle.w2 = float(args[4])
        obstacle.height = float(args[5])
        obstacle.orient = float(args[6])

        if len(args) == 11:
            obstacle.name = args[10].replace("_"," ")
        else:
            obstacle.name = None


    def parse_zone_pass2(self, rndf_file, zone):
        spot_num = 0
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]
            if cmd == "spot":
                spot = zone.spots[spot_num]
                spot_num += 1
                self.parse_spot_pass2(rndf_file, spot)
            elif cmd == "end_zone":
                return

    def parse_spot_pass2(self, rndf_file, spot):
        while rndf_file:
            l = rndf_file.readline()
            if len(l) < 2:
                continue
            cmds = l.split()
            #skip blank lines and comments
            if not cmds or "/*" in cmds[0]:
                 continue
            cmd = cmds[0]
            arg = cmds[1:]
            if cmd == "checkpoint":
                chk_id = arg[0]
                for pt in spot.waypoints:
                    if pt.id == chk_id:
                        wpt = pt
                        break
                chk_pt = rndf_checkpoint()
                chk_pt.waypoint = wpt
                chk_pt.id = chk_id
                chk_pt.id_int = int(arg[1])

                if len(arg) == 3:
                    chk_pt.name = arg[2]
                    if self.enhance and (len(chk_pt.name) == 2 or len(chk_pt.name.split('-')) == 2):
                        chk_pt.name = chk_pt.name.replace('A','Alpha')
                        chk_pt.name = chk_pt.name.replace('B','Bravo')
                        chk_pt.name = chk_pt.name.replace('C','Charlie')
                        chk_pt.name = chk_pt.name.replace('D','Delta')
                        print 'renamed checkpoint: ', chk_pt.name
                else:
                    chk_pt.name = None
                    
                self.checkpoints.append(chk_pt)
            elif cmd == "end_spot":
                return

    def build_polygons(self):
        box = self.bounding_box()
        self.origin = [box[0], box[1]] #put origin at min lat, lon

        #build zone polygons
        self.zone_polygons = []
        for zone in self.zones:
            p = polygon()
            p.id = zone.id
            for pt in zone.perimeter:
                xy = latlon_to_xy(pt.lat, pt.lon, self.origin)
                p.add_segment(xy[0], xy[1])
            p.add_tag(zone.name.lower())

            p.cx, p.cy = p.centroid()
            p.radius = max([math.hypot(p.X[i] - p.cx, p.Y[i] - p.cy) for i in range(len(p.X))])

            self.zone_polygons.append(p)
            zone.poly = p

        #build obstacle polygons
        self.obs_polygons = []
        for obs in self.obstacles:
            p = polygon()
            p.id = obs.id
            cx,cy = latlon_to_xy(obs.lat, obs.lon, self.origin)
            cosx = obs.w2/2.0*cos(obs.orient)
            siny = obs.w1/2.0*sin(obs.orient)
            sinx = obs.w2/2.0*sin(obs.orient)
            cosy = obs.w1/2.0*cos(obs.orient)
            
            pts = [[cx+cosx+siny, cy-sinx+cosy],
                   [cx-cosx+siny, cy+sinx+cosy],
                   [cx-cosx-siny, cy+sinx-cosy],
                   [cx+cosx-siny, cy-sinx-cosy]]
            
            for pt in pts:
                p.add_segment(pt[0], pt[1])

            if obs.name:
                p.add_tag(obs.name.lower())
            
            p.cx, p.cy = p.centroid()
            p.radius = max([math.hypot(p.X[i] - p.cx, p.Y[i] - p.cy) for i in range(len(p.X))])
            
            self.obs_polygons.append(p)

        #build lane polygons
        self.lane_polygons = []
        for seg in self.segments:
            for lane in seg.lanes:
                p = polygon()
                p.id = lane.id
                #first pass
                ft_to_m = 0.3048 #m/ft
                dx = 4 #hack to make the lanes longer so they connect to the zones, should be 0
                
                for i in range(len(lane.waypoints)-1):
                    x1,y1 = latlon_to_xy(lane.waypoints[i].lat, lane.waypoints[i].lon, self.origin)
                    x2,y2 = latlon_to_xy(lane.waypoints[i+1].lat, lane.waypoints[i+1].lon, self.origin)
                    th = atan2(y2-y1,x2-x1)
                    lw = (lane.width/2)*ft_to_m
                    
                    p.add_segment(x1+cos(th)*-dx - sin(th)*-lw, y1+sin(th)*-dx + cos(th)*-lw)
                    p.add_segment(x2+cos(th)*dx - sin(th)*-lw, y2+sin(th)*dx + cos(th)*-lw)
                #complete polygon   
                for i in range(len(lane.waypoints)-1,0,-1):
                    x1,y1 = latlon_to_xy(lane.waypoints[i].lat, lane.waypoints[i].lon, self.origin)
                    x2,y2 = latlon_to_xy(lane.waypoints[i-1].lat, lane.waypoints[i-1].lon, self.origin)
                    th = atan2(y1-y2,x1-x2)
                    lw = (lane.width/2)*ft_to_m

                    p.add_segment(x1+cos(th)*dx - sin(th)*lw, y1+sin(th)*dx + cos(th)*lw)
                    p.add_segment(x2+cos(th)*-dx - sin(th)*lw, y2+sin(th)*-dx + cos(th)*lw)

                p.cx, p.cy = p.centroid()
                p.radius = max([math.hypot(p.X[i] - p.cx, p.Y[i] - p.cy) for i in range(len(p.X))])

                self.lane_polygons.append(p)
                lane.poly = p
            
if __name__=="__main__":

    #rndf_src = "../data/directions/forklift/Belvoir_RNDF.txt"
    rndf_src = "../data/directions/forklift/Lee_RNDF_demo.txt"
    test_rndf = rndf(rndf_src, True)

    carmen_map_output = "../data/directions/forklift/forklift.cmf"
    tagfile_output = "../data/directions/forklift/tags/forklift_tags.tag"
    rndf_output = "../data/directions/forklift/rndf_model.rndf"
    
    og = rndf_to_carmen_gridmap(test_rndf, carmen_map_output, tagfile_output)
    dump(test_rndf, open(rndf_output, 'wb'), 2)

##    rndf_src = "Belvoir_at_Waverly_RNDF.txt"
##    test_rndf = rndf(rndf_src, True)
##
##    carmen_map_output = "../../../../data/directions/waverly/waverly.cmf"
##    tagfile_output = "../../../../data/directions/waverly/tags/waverly_tags.tag"
##
##    rndf_to_carmen_gridmap(test_rndf, carmen_map_output, tagfile_output)




