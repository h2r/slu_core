import numpy as na
from numpy import transpose as tp
from assert_utils import assert_sorta_eq, array_equal
import math
from bisect import bisect_left
from affineMatrix import AffineMatrix
import spatial_features_cxx as sf
id_counter = 0
from hash_utils import fasthash
from dataStructures import contains
from quaternion import Quaternion

def ptsToYaml(points_pts):
    return [[float(x), float(y)] for x, y in points_pts]

def thetaToYaml(points_ptstheta):
    return [[float(x), float(y), float(t)]
            for x, y, t in points_ptstheta]

def xyzThetaToYaml(points_ptstheta):
    return [[float(v) for v in values]
            for values in points_ptstheta]

def assignPathGroundings(esdc, annotation):
    """
    Assign path groundings to an esdc, basede on an annotation's agent
    path and stuff.  This deals with the implied 'you' of imperitive
    commands.
    """
    if esdc.type == "EVENT":
        if annotation.getGroundings(esdc) == []:
            annotation.setGrounding(esdc, annotation.agent)        
        #if esdc.childIsEsdcs("f"):
        #    fgroundings = annotation.getGroundings(esdc.children("f")[0])
        #    if len(fgroundings) > 0 and fgroundings[0].path:
        #        annotation.setGrounding(esdc, fgroundings[0])
            
        if len(esdc.l) and esdc.l[0].type == "PATH" and annotation.agent != None:
            child_esdc = esdc.l[0]
            if annotation.getGroundings(child_esdc) == []:
                annotation.setGrounding(child_esdc, annotation.agent.path)
        elif len(esdc.l2) and esdc.l2[0].type == "PATH":
            child_esdc = esdc.l2[0]
            figure_gnd = annotation.getGroundings(esdc.l[0])

            if len(figure_gnd):
                figure = figure_gnd[0]
                if annotation.getGroundings(child_esdc) == []:
                    annotation.setGrounding(child_esdc, figure.path)


"""
Computed following this web page: 
http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
"""
def signedArea(polygon):
    area = 0
    for i in range(0, len(polygon)):
        j = (i + 1) % len(polygon)
        area = area + \
            float(polygon[i][0]*polygon[j][1]) - \
            float(polygon[j][0]*polygon[i][1])
    area = 0.5 * area
    return area



def ptsToXyth(fig_pts):
    fig_xy = na.transpose(fig_pts)
    Xst, Yst = fig_xy[:,:-1]
    Xend, Yend = fig_xy[:,1:]
    
    Theta = na.arctan2(Yend-Yst, Xend-Xst);
    Theta = list(Theta)
    Theta.append(Theta[-1])
    return [fig_xy[0], fig_xy[1], Theta]



def ptsToXyzth(fig_pts, z):
    try:
        fig_xy = na.transpose(fig_pts)
        Xst, Yst = fig_xy[:,:-1]
        Xend, Yend = fig_xy[:,1:]
   
        Theta = na.arctan2(Yend-Yst, Xend-Xst);
        Theta = list(Theta)
        Theta.append(Theta[-1])
        return [fig_xy[0], fig_xy[1], na.zeros(len(Theta)) + z, Theta]
    except:
        print "exception, figure points were", fig_pts
        raise




class Prism:
    """
    Represents a prism, or a 3d object with a polygon base and a height.
    """


    @staticmethod
    def from_pose(points_xy, zStart, zEnd, dloc, quaternion=Quaternion.null()):
        """
        Creates a prism at a pose with the specified geometry
        """
        assert not na.any(na.isnan(points_xy)), points_xy

        dx, dy, dz = dloc
        X, Y = points_xy
        X = X + dx
        Y = Y + dy

        lower_points_xyz = na.array([X, Y, na.zeros(len(points_xy[0])) + zStart + dz])
        upper_points_xyz = na.array([X, Y, na.zeros(len(points_xy[0])) + zEnd + dz])

        dloc = na.array([dx, dy, dz])

        lower_points_xyz = tp([quaternion.rotate(p - dloc) + dloc for p in tp(lower_points_xyz)])
        upper_points_xyz = tp([quaternion.rotate(p - dloc) + dloc for p in tp(upper_points_xyz)])
        if na.any(na.isnan(lower_points_xyz) + na.isnan(upper_points_xyz)):
            print "points_xy", points_xy
            print "z", zStart, zEnd
            print "dloc", dloc
            raise ValueError("nan")
        return Prism(lower_points_xyz, upper_points_xyz)

    @staticmethod
    def from_point(x,y, z1, z2, width=1):
        """
        Creates a prism from a point with the specified width.
        """
        width = width/2.0
        return Prism.from_points_xy([(x-width, x+width, x+width, x-width), 
                                     (y-width, y-width, y+width, y+width)], z1, z2)

    @staticmethod
    def from_points_xy(points_xy, zStart, zEnd):
        """
        Create a prism from points_xy, zStart, zEnd, facing vertically
        up with no rotation.
        """
        X, Y = points_xy
        lower_points_xyz = na.array([X, Y, na.zeros(len(points_xy[0])) + zStart])
        upper_points_xyz = na.array([X, Y, na.zeros(len(points_xy[0])) + zEnd])
        return Prism(lower_points_xyz, upper_points_xyz)

    def __init__(self, lower_points_xyz, upper_points_xyz):


        assert not na.any(na.isnan(lower_points_xyz)), lower_points_xyz
        assert not na.any(na.isnan(upper_points_xyz)), upper_points_xyz

        self.lower_points_xyz = lower_points_xyz
        self.upper_points_xyz = upper_points_xyz
        
        # approximate the older API for backwards compatibility
        self.points_xy = self.lower_points_xyz[0:2]
        self.zStart = float(min(self.lower_points_xyz[2]))
        self.zEnd = float(max(self.upper_points_xyz[2]))

        self.untranslated_points_xy = na.array([self.points_xy[0] - self.centroid2d()[0],
                                                self.points_xy[1] - self.centroid2d()[1]])
        self.untranslated_points_pts = na.transpose(self.untranslated_points_xy)

        try:
            self.X, self.Y = self.points_xy
        except:
            print self.points_xy
            raise
        self.points_pts = tp(self.points_xy)
        # closed polygon, with start point, for plotting.
        self.pX, self.pY = na.transpose(na.append(self.points_pts,
                                                  [self.points_pts[0]], axis=0))


        self.points_ptsz = []
        for z in [self.zStart, self.zEnd]:
            for x, y in self.points_pts:
                self.points_ptsz.append((x, y, z))
        self.points_ptsz = na.array(self.points_ptsz)
        self.points_xyz = na.transpose(self.points_ptsz)


    def __hash__(self):
        
        return (hash(tuple(tuple(x) for x in self.points_pts)) + 
                13 * hash(self.zStart) + 17 * hash(self.zEnd))

    def __eq__(self, other):
        if not isinstance(other, Prism):
            return False
        return (array_equal(self.lower_points_xyz, other.lower_points_xyz) and
                array_equal(self.upper_points_xyz, other.upper_points_xyz))
    def __ne__(self, other):
        return not (self == other)
    def centroid2d(self):
        result = sf.math2d_centroid(self.points_xy)
        assert not any(na.isnan(result)), self.points_xy
        return result
    def centroid3d(self):
        return tuple(self.centroid2d()) + ((self.zStart + self.zEnd)/2,)
    def __repr__(self):
        return "Prism(%s, %s)" % tuple(repr(x)
                                       for x in [self.lower_points_xyz,
                                                 self.upper_points_xyz])

    def __str__(self):
        return repr(self)
    def toYaml(self):
        return {"lower_points": xyzThetaToYaml(tp(self.lower_points_xyz)),
                "upper_points": xyzThetaToYaml(tp(self.upper_points_xyz)),
                }

    @staticmethod
    def fromYaml(yaml):
        if yaml == None:
            return None
        elif "points" in yaml:
            return Prism.from_points_xy(na.transpose(yaml["points"]),
                                        yaml["zStart"], yaml["zEnd"])
        elif "lower_points" in yaml:
            return Prism(na.transpose(yaml["lower_points"]),
                         na.transpose(yaml["upper_points"]))
        else:
            raise ValueError("Unknown format: " + str(yaml))
    
    @staticmethod
    def fromPolygon(polygon, zStart, zEnd):
        return Prism((polygon.X, polygon.Y),
                     zStart, zEnd)
    
    @staticmethod
    def fromLcmObject(obj):
        #x0,y0,z0 = [obj.pos[i] + obj.bbox_min[i] for i in range(3)]
        #x1,y1,z1 = [obj.pos[i] + obj.bbox_max[i] for i in range(3)]
        x0,y0,z0 = [obj.bbox_min[i] for i in range(3)]
        x1,y1,z1 = [obj.bbox_max[i] for i in range(3)]        
        import libbot_rotations
        if len(obj.orientation) != 0:
            m = libbot_rotations.quat_pos_to_matrix(obj.orientation, obj.pos)
            points = na.array([(x0, y0, z0, 1),
                               (x0, y1, z0, 1),
                               (x1, y1, z0, 1),
                               (x1, y0, z1, 1)])

            points_xyz = na.transpose([na.dot(m, p) for p in points])[0:3]
            X, Y, Z = points_xyz
            
        else:
            xs, ys, zs = obj.pos
            points_xyz = na.transpose([(xs+x0, ys+y0, zs+z0),
                                       (xs+x0, ys+y1, zs+z0),
                                       (xs+x1, ys+y1, zs+z0),
                                       (xs+x1, ys+y0, zs+z0)])
                                      #(x1, y1, z1)])
            Z = [z0, z1]
        return Prism.from_points_xy(points_xyz[0:2], min(Z), max(Z))

def compressC(timestamps, points_xyztheta):
    if len(timestamps) == 0:
        return timestamps, points_xyztheta
    try:
        result = sf.math3d_compress([float(t) for t in timestamps], points_xyztheta)
        newtimestamps = result[-1]
        newpoints = result[0:-1]
        return newtimestamps, newpoints
    except:
        print 'timestamps', repr(timestamps)
        print 'points', repr(points_xyztheta)

def compressP(timestamps, points_xyztheta):
    points = tp(points_xyztheta)
    assert len(points) == len(timestamps), (len(points), len(timestamps))
    ctimestamps = []
    cpoints = []
    
    for t, pt in zip(timestamps, points):
        if len(cpoints) == 0 or not all (pt == cpoints[-1]):
            ctimestamps.append(t)
            cpoints.append(pt)
    return ctimestamps, tp(cpoints)

compress = compressC
def compressCompare(timestamps, points):
    print "timestamps = ", repr(timestamps)
    print "points = ", repr(points)
    pts, ppts = compressP(timestamps, points)
    cts, cpts = compressC(timestamps, points)
    from math2d import assert_array_equal
    print "timestamps"
    assert_array_equal(pts, cts)
    print "points"
    assert_array_equal(ppts, cpts)
    #assert list(pts) == list(cts), (pts, cts)
    #assert list(ppts) == list(cpts), (cts, cpts)
    return cts, cpts

def points_xyztheta_to_xyzquat(points_xyztheta):
    new_points = []
    for pt in tp(points_xyztheta):
        quat = Quaternion.from_yaw(pt[-1])
        new_points.append(na.append(pt[0:3], quat.q))
    new_points = na.array(new_points)
    return tp(new_points)

def points_xyzquat_to_xyztheta(points_xyzquat):
    new_points = []
    for pt in tp(points_xyzquat):
        quat = Quaternion(pt[3:])
        roll, pitch, yaw = quat.to_roll_pitch_yaw()
        new_points.append(na.append(pt[0:3], [yaw]))
    return tp(new_points)

    

class Path:
    ONE_SECOND_IN_MICROS = 1000000.0
    @staticmethod
    def copy(obj):
        return Path(obj.timestamps, obj.points_xyztheta)

    @staticmethod
    def from_xyztheta(timestamps, points_xyztheta):
        return Path(timestamps, points_xyztheta_to_xyzquat(na.array(points_xyztheta)))

    def __init__(self, timestamps, points_xyzquat):
        """
        Timestamps are in microseconds.
        """
        assert_sorta_eq(na.array(points_xyzquat).shape[0], 7)

        self.type = self.__class__.__name__
        try:
            timestamps, points_xyzquat = compress(timestamps, points_xyzquat)
        except:
            print timestamps
            print points_xyzquat
            raise


        self.timestamps = [long(x) for x in timestamps]

        self.points_xyzquat = na.array(points_xyzquat)
        assert_sorta_eq(self.points_xyzquat.shape[0], 7)
        self.points_xyztheta = points_xyzquat_to_xyztheta(self.points_xyzquat)
        self.updateRep()

    def withCroppedRange(self, start_t, end_t):
        """
        Return a new path with the range cropped to start_t and end_t
        """
        start_i = self.indexAtT(start_t)
        end_i = self.indexAtT(end_t)
        if start_i == end_i:
            if end_i < len(self.timestamps):
                end_i += 1
            elif start_i >= 1:
                start_i -= 1
            else:
                return self
            

        return Path.from_xyztheta(self.timestamps[start_i:end_i], 
                                  self.points_xyztheta[:, start_i:end_i])

    def __eq__(self, other):
        if not isinstance(other, Path):
            return False
        return (array_equal(self.points_xyztheta, other.points_xyztheta) and
                array_equal(self.timestamps, other.timestamps))

    def __hash__(self):
        return hash(tuple(self.timestamps))

    def __repr__(self):
        return self.repr

    @property
    def centroid2d(self):
        
        return na.mean(self.points_pts, axis=0)
    
    @property
    def centroid3d(self):
        return na.mean(na.transpose(self.points_xyz), axis=0)


    def updateRep(self):
        self.X, self.Y, self.Z, self.theta = self.points_xyztheta
        self.points_xy = self.points_xyztheta[0:2]
        self.points_xytheta = self.points_xyztheta[[0, 1, 3]]
        self.points_xyz = self.points_xyztheta[0:3]
        self.points_pts = self.points_xy.transpose()

        self.points_ptsztheta = self.points_xyztheta.transpose()
        
        self.start_t = self.timestamps[0]
        self.end_t = self.timestamps[-1]
        self.range = self.start_t, self.end_t

        self.length_seconds = (self.end_t - self.start_t) / Path.ONE_SECOND_IN_MICROS
        self.repr = "Path(%s, %s)" % tuple(repr(x) for x in 
                                           (self.timestamps, 
                                            self.points_xyztheta))
        self.hash_string = fasthash(self.repr)
        self.id = self.hash_string

    @property
    def length_meters(self):
        length = 0
        for p1, p2 in zip(self.points_ptsztheta, self.points_ptsztheta[1:], ):
            length += sf.math3d_dist(p1, p2)
        return length

    def max_dist_from_start(self):
        start = self.points_ptsztheta[0]
        
        distances = [sf.math3d_dist(start, p) for p in self.points_ptsztheta]

        return max(distances)
        
    def __len__(self):
        return len(self.timestamps)

    def indexAtT(self, t):
        if t == -1:
            t = self.timestamps[-1]
        closestIndex = bisect_left(self.timestamps, t)
        if closestIndex == len(self.timestamps):
            closestIndex = len(self.timestamps) - 1
        return closestIndex
    def locationAtT(self, t):
        index = self.indexAtT(t)
        location = tp(self.points_xyztheta)[index]
        return location

    def rotationAtT(self, t):
        """
        Returns the rotation at time t, as a quaternion
        """
        index = self.indexAtT(t)
        return Quaternion(tp(self.points_xyzquat)[index][3:])

        

    def toYaml(self):
        return {"points_xyzquat": xyzThetaToYaml(tp(self.points_xyzquat)),
                "timestamps": [str(x) for x in self.timestamps]}

    def contains(self, r2):
        return contains(self.range, r2)
    
    @staticmethod
    def fromYaml(yaml):
        if yaml == None:
            return None
        else:
            if "points_xyztheta" in yaml:
                return Path.from_xyztheta(timestamps=[float(long(x)) for x in yaml["timestamps"]],
                                          points_xyztheta = tp(yaml["points_xyztheta"]))
            elif "points_xyzquat" in yaml:
                return Path(timestamps=[float(long(x)) for x in yaml["timestamps"]],
                            points_xyzquat = tp(yaml["points_xyzquat"]))
            else:
                raise ValueError("Unsupported format yet.")

                
class Place:
    @staticmethod
    def copy(obj):
        return Place(obj.prism, obj.tags)

    def withCroppedRange(self, start_t, end_t):
        return self

    def __init__(self, prism, tags=[]):
        self.prism = prism
        self.type = self.__class__.__name__
        self.centroid2d = self.prism.centroid2d()
        self.centroid3d = self.prism.centroid3d()
        self.tags = tuple(tags)

        self.updateRep()


    def updateRep(self):
        self.X = self.prism.X
        self.Y = self.prism.Y
        self.points_xy = self.prism.points_xy
        self.points_pts = self.prism.points_pts

        self.start_t = 0
        self.end_t = 0
        self.repr = "Place(%s, %s)" % tuple(repr(x) for x in [self.prism, self.tags])
        self.hash_string = fasthash(self.repr)
        self.id = self.hash_string
        
        f_xyzth = tp([self.centroid3d + (0,)])
        f_xyzth[2] = self.prism.zStart
        self.path = Path.from_xyztheta([0], f_xyzth)


    def prismAtT(self, t):
        return self.prism

    def __hash__(self):
        return hash(self.prism) + 13 * hash(self.tags)
    
    def __eq__(self, other):
        if not isinstance(other, Place):
            return False
        return (self.prism == other.prism and self.tags == other.tags)

    def __repr__(self):
        return self.repr


    def __ne__(self, other):
        return not (self == other)
    
    def toYaml(self):
        return {"prism":self.prism.toYaml(),}
    
    @staticmethod
    def fromYaml(yaml):
        if yaml == None:
            return None
        else:
            return Place(Prism.fromYaml(yaml["prism"]))
                         
    @staticmethod
    def fromLcmObject(obj, posToLocation):
        points = [posToLocation((point.x, point.y, point.z))
                  for point in obj.points]
        zStart = points[0][-1]
        zEnd = points[1][-1]
        for x, y, z in points[2:]:
            assert math.fabs(z - 0) < 0.00000000001
        points_xy = tp([(x, y) for x, y, z in points])
        
        return Place(Prism(points_xy, zStart, zEnd))

class PhysicalObject:
    @staticmethod
    def copy(obj):
        return PhysicalObject(obj.prism, obj.tags, obj.path, obj.lcmId)

    """
    An object with a tag and 3d geometry and a quaternion rotation.

    * We will only represent the prism/geometry and tag of the object.

    * The polygon points are at an absolute offset in space.  Then the
      quaternion is applied.  It would be better if they were relative
      to an origin and then rotation/orientation was applied from the
      path.  However I didn't do it that way a long time ago, and
      changing the feature computation now is too complicated.
    """
    def __init__(self, prism, tags, path=None, lcmId=None):
        self.type = self.__class__.__name__
        self.tags = tuple(tags)

        self.prism = prism
        self.lcmId = lcmId
        self.id = lcmId
        self.path = path

        self.updateRep()

    def updateRep(self):
        self.centroid2d = self.prism.centroid2d()
        self.centroid3d = self.prism.centroid3d()
    
        self.X = self.prism.X
        self.Y = self.prism.Y

        
        if self.path == None:
            f_xyzth = tp([self.centroid3d + (0,)])
            f_xyzth[2] = self.prism.zStart
            self.path = Path.from_xyztheta([0], f_xyzth)

        self.timestamps = self.path.timestamps

        self.start_t = self.path.start_t
        self.end_t = self.path.end_t
        
        self.points_xy = self.prism.points_xy
        self.points_pts = self.prism.points_pts

        self.repr = ("PhysicalObject(%s, %s, %s, %s)" % 
                     tuple(repr(x) for x in (self.prism, self.tags, 
                                             self.path, self.id)))
        self.hash = 13* hash(self.tags) + 17 * hash(self.prism) + 23 * hash(self.path)
        self.hash_string = fasthash(self.repr)
        
    def __str__(self):
        return str(self.tags)

    def __repr__(self):
        return self.repr

    def __eq__(self, other):
         if not isinstance(other, PhysicalObject):
             return False
         return ((self.tags == other.tags and self.prism == other.prism) and
                 self.path == other.path)

    def __hash__(self):
        return self.hash

    def freeze(self):
        self.frozen = True
        
    def unfreeze(self):
        self.frozen = False

    def atT(self, time):
        new_prism = self.prismAtT(time)
        return PhysicalObject(new_prism, self.tags, lcmId=self.id)        

    def withCroppedRange(self, start_t, end_t):
        new_path = self.path.withCroppedRange(start_t, end_t)
        new_prism = self.prismAtT(start_t)
        return PhysicalObject(new_prism, self.tags, new_path, self.id)


    def withPath(self, path):
        """
        Returns a new physical object with the path; translates the
        prism to the start of the new path.
        """

        prism_now = self.prismAtT(0)
        
        xstart, ystart = prism_now.centroid2d()
        zstart = prism_now.zStart
        xend, yend = path.points_pts[0]

        zend = path.points_xyz[2][0]
        dx = xend - xstart
        dy = yend - ystart
        dz = zend - zstart
        
        new_points = [((x + dx), (y + dy)) for x, y in prism_now.points_pts]
        new_prism = Prism(tp(new_points), prism_now.zStart + dz, 
                          prism_now.zEnd + dz)
        
        return PhysicalObject(new_prism, self.tags, path, self.id)

    def withExtendedPath(self, path):
        """
        Returns a new physical object whose path is the concanation of
        this object's path and the new path.
        """
        new_pts_xyzquat = na.append(self.path.points_xyzquat, 
                                    path.points_xyzquat, axis=1)
        new_timestamps = na.append(self.path.timestamps, path.timestamps)
        new_path = Path(new_timestamps, new_pts_xyzquat)

        return PhysicalObject(self.prism, self.tags, new_path, self.id)

    def withoutPath(self):
        """
        Returns a new physical object with no path.
        """
        start = self.prismAtT(0)
        return PhysicalObject(start, self.tags, lcmId=self.id)

    def withoutHistory(self):
        """
        Returns a new physical object with no path, but locations at the end of the current path.
        """
        start = self.prismAtT(-1)
        return PhysicalObject(start, self.tags, lcmId=self.id)
        

#    @MemoizeInstance
    def prismAtT(self, t):
        dx, dy, dz, dtheta = self.path.locationAtT(t) - self.path.locationAtT(0)
        quat0 = self.path.rotationAtT(0)
        quat = quat0.conjugate * self.path.rotationAtT(t)
        
        dloc = na.array([dx, dy, dz])
        cloc = self.centroid3d
        
        lower_points_xyz = tp([quat.rotate(p - cloc) + cloc + dloc for p in tp(self.prism.lower_points_xyz)])
        upper_points_xyz = tp([quat.rotate(p - cloc) + cloc + dloc for p in tp(self.prism.upper_points_xyz)])

        return Prism(lower_points_xyz, upper_points_xyz)
        

    def __ne__(self, other):
        return not (self == other)
    def toYaml(self):
        if self.path:
            return {"prism":self.prism.toYaml(),
                    "tag":list(self.tags),
                    "lcmId": self.lcmId,
                    "path":self.path.toYaml()}
        else:
            return {"prism":self.prism.toYaml(),
                    "tag":list(self.tags),
                    "lcmId":self.lcmId}
                    
    @staticmethod
    def fromYaml(yaml):
        if yaml == None:
            return None
        else:
            try:
                return PhysicalObject(Prism.fromYaml(yaml["prism"]),
                                      yaml["tag"],
                                      Path.fromYaml(yaml.get("path")),
                                      lcmId=yaml.get("lcmId"))
            except:
                print yaml
                raise

    @staticmethod
    def fromPolygon(polygon, zStart, zEnd):
        return PhysicalObject(Prism.fromPolygon(polygon,
                                                zStart, zEnd),
                              polygon.tag.split())

        
def toYaml(groundings):
    return [[g.__class__.__name__, g.toYaml()] for g in groundings]

def fromYaml(groundings):
    if groundings == None:
        return None
    else:
        return [eval(clsName).fromYaml(yaml) for clsName, yaml in groundings]
    
def copy_grounding(grounding):
    if isinstance(grounding, PhysicalObject):
        return PhysicalObject.copy(grounding)
    elif isinstance(grounding, Place):
        return Place.copy(grounding)
    elif isinstance(grounding, Path):
        return Path.copy(grounding)
    else:
        raise ValueError("Don't know how to copy " + `grounding`)




def find_closest_object(objects, point):
    if len(objects) == 0:
        return None
    else:
        sorted_objects = list(sorted(objects, 
                                     key=lambda o: sf.math2d_dist(o.centroid2d,
                                                                   point)))
        return sorted_objects[0]
