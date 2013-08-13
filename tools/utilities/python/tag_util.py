#needed to load the tag files
from gsl_utilities import tklib_get_distance, tklib_normalize_theta
from carmen_gridmap import tklib_log_gridmap
from spatial_features_cxx import math2d_step_along_line, math2d_line_length
from copy import deepcopy
from carmen_util import get_euclidean_distance
#from annote_utils import *
import os
#from memoized import memoize
#import math2d
from scipy import transpose, mean, array
from scipy import transpose as tp
from math import atan2
from geometry_2d import point, polygon, isInteriorPoint

def save_polygons(polygons, points, filename):
    myfile = open(filename, 'w')
    for pol in polygons:
        if(not pol.isempty()):
            #print pol.tostring()
            myfile.write(pol.tostring())

    for p in points:
        if(not p.isempty()):
            #print p.tostring()
            myfile.write(p.tostring())

    myfile.close()

def load_polygons(filename):
    myfile = open(filename, 'r')
    polygons = []
    pts = []
    for line in myfile:
        p = polygon()
        pt = point()        

        if(p.fromstring(line)):
            polygons.append(p)
        elif(pt.fromstring(line)):
            pts.append(pt)
            
    
    myfile.close()
    return polygons, pts

class tag_file:
    def __init__(self, tag_filename, map_filename):
        self.map_filename = map_filename
        self.tag_filename = tag_filename
        self.polygons, self.points = load_polygons(tag_filename)
        self.map = None
        self.tag_names = None
        self.objects =  self.points + self.polygons 
        self.debug = False

        #this is for use in the Polygon package
        self.Polys = None

    def filter(self, boundingBox):
        if boundingBox == None:
            return
        self.points = [p for p in self.points 
                       if isInteriorPoint(boundingBox, 
                                          self.get_map().to_xy([p.x, p.y]))]
        
        self.polygons = [p for p in self.polygons
                         if isInteriorPoint(boundingBox, 
                                            self.get_map().to_xy(p.centroid()))]
        
        self.objects = self.points + self.polygons 
                                          
    def get_points_and_polygons_XY(self):
        """
        returns the points and polygons as XY locations
        """
        mymap = self.get_map()
        Pts =[]
        for p in self.points:
            xp, yp = mymap.to_xy([p.x, p.y])
            Pts.append([xp,yp])
            
        for p in self.polygons:

            XY_new = []
            for i in range(len(p.X)):
                XY_new.append(mymap.to_xy([p.X[i], p.Y[i]]))
            Pts.append(transpose(XY_new))

        return Pts


    def get_points_and_polygons(self):

        ret_list = deepcopy(self.polygons)
        ret_list.extend(self.points)

        return ret_list

    def __len__(self):
        return len(self.tag_names)
    
    def __getitem__(self, idx):
        return self.objects[idx]

    def scale_annotations(self, new_mapfilename):
        currmap = tklib_log_gridmap()
        currmap.load_carmen_map(new_mapfilename)
        
        print "1:", currmap.resolution
        print "2:", self.get_map().resolution
        sf = self.get_map().resolution/currmap.resolution

        print "sf:", sf

        newpolygons = []
        newpoints = []

        for pt in self.points:
            newpt = deepcopy(pt)
            newpt.x = newpt.x * sf
            newpt.y = newpt.y * sf

            newpoints.append(newpt)

        for poly in self.polygons:
            newpoly = deepcopy(poly)
            newpoly.X = array(newpoly.X) * sf
            newpoly.Y = array(newpoly.Y) * sf
            newpoly.X = newpoly.X.tolist()
            newpoly.Y = newpoly.Y.tolist()
            newpolygons.append(newpoly)

        return newpoints, newpolygons
    
    def get_nearest_tag(self, x, y):
        nt = None
        dt = 10000000000000000000
        nx, ny = 0, 0

        mymap = self.get_map()

        for p in self.points:
            xp, yp = mymap.to_xy([p.x, p.y])
            if(get_euclidean_distance([xp, yp],[x,y]) < dt):
                nt = p.tag
                dt = get_euclidean_distance([xp, yp],[x,y])
                nx, ny = xp, yp

        for p in self.polygons:
            p.tag
            xp, yp = mymap.to_xy([mean(p.X), mean(p.Y)])
            
            for i in range(len(p.X)):
                xp, yp = mymap.to_xy([p.X[i], p.Y[i]])
                if(get_euclidean_distance([xp, yp],[x,y]) < dt):
                    nt = p.tag
                    dt = get_euclidean_distance([xp, yp],[x,y])
                    nx, ny = xp, yp

        return nt, [nx, ny]


    def get_tag_locations(self, mytag):
        X, Y = [], []
        
        mymap = self.get_map()

        for p in self.points:
            #print mytag + ' not = ' + p.tag
            if(mytag == p.tag):
                x, y = mymap.to_xy([p.x, p.y])
                X.append(x)
                Y.append(y)
        for p in self.polygons:
            #print mytag + ' not = ' + p.tag
            if(mytag == p.tag):
                x, y = mymap.to_xy([mean(p.X), mean(p.Y)])
                X.append(x)
                Y.append(y)
        return X,Y

    def get_tag_names(self):
        if(self.tag_names == None):
            self.tag_names = []
            for p in self.points:
                if(p.tag not in self.tag_names):
                    self.tag_names.append(p.tag)
            for p in self.polygons:
                if(p.tag not in self.tag_names):
                    self.tag_names.append(p.tag)
        return self.tag_names

    def get_map(self):
        if(self.map == None):
            if not os.path.exists(self.map_filename):
                raise ValueError("map file " + `self.map_filename` + " doesn't exist!")
            self.map = tklib_log_gridmap()
            self.map.load_carmen_map(self.map_filename)
            self.carmen_map = self.map.to_probability_map_carmen()
        return self.map

    def is_visible_object(self, p1, obj, max_dist=5.0):
        if isinstance(obj, point):
            return self.is_visible_point(p1, obj, max_dist)
        elif isinstance(obj, polygon):
            return self.is_visible_polygon(p1, obj, max_dist)
        else:
            raise ValueError("Bad type for" + `obj`+
                             " + class " + `obj.__class__`)

    def is_visible_points(self, p1, tag_pts, max_dist=5.0):
        mymap = self.get_map()
        pts_xy = []
        for tag_pt in tag_pts:
            pts_xy.append(mymap.to_xy([tag_pt.x, tag_pt.y]))
            
        #print "get distance"
        D = []
        if(len(pts_xy) > 0):
            D = tklib_get_distance(transpose(pts_xy), p1);
        #print "after get distance"
        
        ret_val = []
        for i, pt in enumerate(pts_xy):
            #if(D[i] < max_dist):
            #    print "distance", D[i]
            #    print tag_pts[i].tag, "visible=", self.is_visible(p1, pt, edist=D[i])

            ret_val.append(self.is_visible(p1, pt, edist=D[i], max_dist=max_dist))
        
        return ret_val

    def is_visible_point(self, p1, tag_pt, max_dist=5.0):
        mymap = self.get_map()
        return self.is_visible(p1, mymap.to_xy([tag_pt.x, tag_pt.y]))

    #@memoize
    def is_visible(self, p1, p2, max_dist=5.0, edist=None):
        d_elt = None
        if(edist != None):
            d_elt = edist
        else:
            d_elt = get_euclidean_distance(p1, p2)
        

        if(d_elt >= max_dist+0.3):
            return False
        
        x, y = p1
        xp, yp = p2
        theta = atan2(yp-y, xp-x)
        mymap = self.get_map()
        d, = mymap.ray_trace(x, y, [theta])


        if(d_elt < d and d_elt < max_dist):
            return True
        elif(abs(d-d_elt) < 0.3 and d_elt<max_dist+0.3):
            return True
        else:
            return False

    #@memoize
    def is_visible_polygon(self, point, poly, max_dist=5.0):
        x, y = point 
        mymap = self.get_map()
        if isInteriorPoint([mymap.to_xy(p) for p in zip(poly.X, poly.Y)], 
                           point):
            return True
        
        points_pts = []
        for i in range(poly.num_segments()):
            xi, yi = poly.get_segment(i)
            xp, yp = mymap.to_xy([xi, yi])
            points_pts.append((xp, yp))

        
        pts = array(math2d_step_along_line(tp(points_pts), 
                                           math2d_line_length(points_pts)/10))
        for i in range(len(pts[0])):
            p = pts[:,i]
            
            if self.debug:
                print
                print "p", p, point
                idx = mymap.to_index(point)
                print "indices", idx
                print "resolution", mymap.to_xy([idx[0] + 1, idx[1] + 1])
                print "prob", mymap.get_value_probability(int(idx[0]), 
                                                          int(idx[1]))
            
            if self.is_visible(point, p, max_dist):
                return True

        return False    



    #@memoize
    def is_visible_polygon_fast(self, point, poly, max_dist=5.0):
        import Polygon
        x, y = point 
        mymap = self.get_map()

        points_xy = []
        for i in range(poly.num_segments()):
            xi, yi = poly.get_segment(i)
            xp, yp = mymap.to_xy([xi, yi])
            points_xy.append((xp, yp))
        
        p = Polygon.Polygon(points_xy)
        
        #return true if the point is inside using a fast library
        try: 
            if p.isInside(x, y): 
                return True
        except:
            return False
        
        #if isInteriorPoint(points_xy, point):
        #    return True

        #if isInteriorPoint([mymap.to_xy(p) for p in zip(poly.X, poly.Y)], 
        #                   point):
        #    return True
        
        steps_pts = points_xy 
        #math2d.stepAlongLine(math2d.polygonToLine(points_xy),
        #                                 math2d.length(points_xy)/10)
        
        D = tklib_get_distance(transpose(steps_pts), point);
        
        if(min(D) >= max_dist):
            return False
        
        for i, p in enumerate(steps_pts):
            if(D[i] >= max_dist):
                continue
            
            if self.is_visible(point, p, max_dist, edist=D[i]):
                return True
            
        return False    


    #@memoize
    def get_visible_tags(self, pt, max_dist=5.0):
        """ returns a set of all tags (strings) visible from pt in the
        tag file."""
        vobjs, iobjs = self.get_visible_objects(pt, max_dist)

        vtags = set([p.tag for p in vobjs])
        itags = set([p.tag for p in iobjs]) - vtags

        return frozenset(vtags), frozenset(itags)
    
    #@memoize
    def get_visible_objects(self, pt, max_dist=5.0):
        """ returns a list of all objects visible from pt in the tag file."""
        vpoints, ipoints = self.get_visible_points(pt, max_dist)
        vpolys, ipolys = self.get_visible_polygons(pt, max_dist)
        return vpoints + vpolys, ipoints + ipolys

    #@memoize
    def get_visible_polygons(self, pt, max_dist=5.0):
        """ returns a list of all polygons visible from pt in the tag file."""
        visible_polygons = []
        invisible_polygons = []
        for polygon in self.polygons:
            if self.is_visible_polygon(pt, polygon, max_dist):
                visible_polygons.append(polygon)
            #if self.is_visible_polygon(pt, polygon, max_dist):
            #    visible_polygons.append(polygon)
            else:
                invisible_polygons.append(polygon)

        return visible_polygons, invisible_polygons

    #@memoize
    def get_visible_points(self, ipt, max_dist=5.0):
        """ returns a list of all points visible from pt in the tag file."""
        visible_pts = []
        invisible_pts = []
        
        pts = self.points

        visible = self.is_visible_points(ipt, pts, max_dist)
        
        for i, pt in enumerate(pts):
            if(visible[i]):
                visible_pts.append(pt)
            else:
                invisible_pts.append(pt)

        return visible_pts, invisible_pts

    def get_visible_points_orient(self, x, y, rtheta, fov, max_dist=5.0):
        visible_pts = []
        invisible_pts = []
        
        pts = self.points
        mymap = self.get_map()

        for pt in pts:
            xp, yp = mymap.to_xy([pt.x, pt.y]);
            theta = atan2(yp-y, xp-x)
            
            #print pt.tag, " th:", theta, " rtheta:", rtheta
            #print "normalized", abs(tklib_normalize_theta(theta - rtheta))

            if(abs(tklib_normalize_theta(theta - rtheta)) >= fov/2.0):
                continue
            
            #this probably just made a bug
            d, = mymap.ray_trace(x, y, [theta])
            #d_elt = sqrt((y-yp)**2.0 + (x-xp)**2.0)
            d_elt = get_euclidean_distance([x,y], [xp, yp])
            
            if(d_elt < d and d_elt < max_dist):
                visible_pts.append(pt)
            elif(abs(d-d_elt) < 0.3 and d_elt<max_dist+0.3):
                visible_pts.append(pt)
            else:
                invisible_pts.append(pt)



        return visible_pts, invisible_pts



    #these should eventually be deprecated
    def get_visible_polygons_orient(self, x, y, rtheta, fov, max_dist=5.0):
        polygons = self.polygons
        mymap = self.get_map()

        visible_polygons = []
        invisible_polygons = []
        for polygon in polygons:
            seen = False
            for i in range(polygon.num_segments()):
                xi, yi = polygon.get_segment(i)
                xp, yp = mymap.to_xy([xi, yi])
            
                theta = atan2(yp-y, xp-x)

                if(abs(tklib_normalize_theta(theta - rtheta)) > fov/2.0):
                    continue
                
                d, = mymap.ray_trace(x, y, [theta])
                #d_elt = sqrt((y-yp)**2.0 + (x-xp)**2.0)
                d_elt = get_euclidean_distance([x,y], [xp, yp])

                if(d_elt < d and d_elt<max_dist):
                    visible_polygons.append(polygon)
                    seen = True
                    break
                elif(abs(d-d_elt) < 0.3 and d_elt<max_dist+0.3):
                    visible_polygons.append(polygon)
                    seen = True
                    break
            if(not seen):
                invisible_polygons.append(polygon)
        



        return visible_polygons, invisible_polygons

    def to_Polygons(self):
        import Polygon
        if(self.Polys != None):
            return self.Polys
            
        mymap = self.get_map()
        
        self.Polys = []
        for p in self.polygons:
            xy = [mymap.to_xy(p.get_segment(i)) for i in range(len(p.X))]
            self.Polys.append(Polygon.Polygon(xy))
            
        return self.Polys
        
    
    def get_contained_polygons(self, pt):
        ps = self.to_Polygons()
        
        ret_vals = []
        for i, p in enumerate(ps):
            if(p.isInside(pt[0], pt[1])):
                ret_vals.append(self.polygons[i])
        
        return ret_vals
    
    '''def as_slimd_polygons(self):
        """
        Convert the points and polygons into a format that makes slimd
        happy.  The points are converted to tiny polygons.  And all
        the vertices are converted to the right coordinate system.  It
        returns a list of polygons. 
        """
        slimd_polygons = list(self.polygons)
        for point in self.points:
            width = 0.001
            x,y = point.x, point.y
            points = pointToSmallPolygon(width)
            X = [x for x,y in points]
            Y = [y for x,y in points]
            p = polygon()
            p.X = X
            p.Y = Y
            p.tag =point.tag 
            slimd_polygons.append(p)

        for p in slimd_polygons:
            points = [self.get_map().to_xy(point)
                      for point in zip(p.X, p.Y)]
            X = [x for x, y in points]
            Y = [y for x, y in points]
            p.X = X
            p.Y = Y
        return slimd_polygons'''

    def toXml(self, doc):
        tagFileXml = doc.createElement("tagFile")
        mymap = self.get_map()
        pointsXml = doc.createElement("points")


        for p in self.points:
            pointXml = doc.createElement("point")
            mx, my  =  mymap.to_xy([p.x, p.y])
            pointXml.setAttribute("x", str(mx))
            pointXml.setAttribute("y", str(my))
            pointXml.setAttribute("tag", p.tag)
            pointsXml.appendChild(pointXml)

        tagFileXml.appendChild(pointsXml)            

        polygonsXml = doc.createElement("polygons")

        for p in self.polygons:
            polygonXml = doc.createElement("polygon")
            polygonXml.setAttribute("tag", p.tag)
            pointsXml = doc.createElement("points")
            for x, y in zip(p.X, p.Y):
                mx, my = mymap.to_xy([x, y])
                pointXml = doc.createElement("point")
                pointXml.setAttribute("x", str(x))
                pointXml.setAttribute("y", str(y))
                pointsXml.appendChild(pointXml)
            polygonXml.appendChild(pointsXml)
            polygonsXml.appendChild(polygonXml)

        tagFileXml.appendChild(polygonsXml)            
        return tagFileXml
        
        
        
        
