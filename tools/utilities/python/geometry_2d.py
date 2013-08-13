import re
from scipy import sqrt
from carmen_util import get_euclidean_distance
def centroid(polygon):
    """
    Compute the centroid of a polygon represented as a list of tuples. 

    Computed following this web page: 
    http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
    """
    cx = 0.0
    cy = 0.0
    a = signedArea(polygon)
    if a == 0:
        X, Y = transpose(polygon)
        return mean(X), mean(Y)
        #raise ValueError("Polygon with zero area." + `polygon`)
    for i in range(0, len(polygon)):
        j = (i + 1) % len(polygon)
        
        
        multiplier = \
            polygon[i][0]*polygon[j][1] - \
            polygon[j][0]*polygon[i][1]
        cx += multiplier * (polygon[i][0] + polygon[j][0])
        cy += multiplier * (polygon[i][1] + polygon[j][1])

    cx = cx / (6.0*a)
    cy = cy / (6.0*a)
    return cx, cy

def allSegments(polygon):
    for i, p1 in enumerate(polygon):
        j= (i + 1) % len(polygon)
        p2 = polygon[j]
        yield p1, p2



def isInteriorPoint(polygon, point):
    """
    Determine if a point is inside a polygon
    """
    x, y = point
    c = False
    for (x1, y1), (x2, y2) in allSegments(polygon):
        if x == x1 and y == y1:
            return True
        if ((((y1 <= y) and (y < y2)) or
             ((y2 <= y) and (y < y1))) and
            (x < ((x2 - x1) * (y - y1)) / float(y2 - y1) + x1)):
            c = not c
    return c




def pointToSmallPolygon(point, width=0.1):
    """
    Converts a point to a small square with width
    """
    offset = width * 0.5
    x, y = point
    return [(x - offset, y - offset),
            (x - offset, y + offset),
            (x + offset, y + offset),
            (x + offset, y - offset),]

def signedArea(polygon):
    """
    
    Sign depends on whether vertices are clockwise or
    counterclockwise.
    
    Computed following this web page: 
    http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
    """
    area = 0
    for i in range(0, len(polygon)):
        j = (i + 1) % len(polygon)
        area = area + \
            float(polygon[i][0]*polygon[j][1]) - \
            float(polygon[j][0]*polygon[i][1])
    area = 0.5 * area
    return area





class polygon:
    def __init__(self):
        self.X = []
        self.Y = []
        self.tag = None
        
        self.z = None
        self.debug = False

    def add_segment(self, x, y, z=0):
        self.X.append(x)
        self.Y.append(y)
        
        if self.z == None:
            self.z = z
        else:
            assert self.z == z, (self.z, z)
        
    @property
    def vertices(self):
        """
        returns the verticies as a list of tuples.  Each tuple is a point.
        """
        return [p for p in zip(self.X, self.Y)]

    def add_tag(self, str):
        #print "adding tag:", str
        self.tag = str

    def get_tag(self):
        return self.tag

    def is_finished(self):
        if(sqrt((self.X[-1]-self.X[0])**2.0+(self.Y[-1]-self.Y[0])**2.0) < 5):
            return True

    def num_segments(self):
        return len(self.X)
    
    def get_segment(self, i):
        return self.X[i], self.Y[i]

    def tostring(self):
        #print "tag", self.tag
        mystr = "";
        if(self.tag != None):
            mystr = "tag:"+self.tag 
        
        mystr += " polygon:"
        for i in range(len(self.X)):
            x, y = self.X[i], self.Y[i]
            mystr+= str(x) + "," + str(y)+":"
        mystr+="\n"
        return mystr

    def fromstring(self, mystr):
        tags = re.split("[ :]", mystr)
        doPoly=False
        for i in range(len(tags)):
            if(doPoly):
                #print "mystr", tags[i]
                vals = tags[i].split(",")
                if(len(vals) == 2):
                    v1, v2 = vals
                    v1 = float(v1)
                    v2 = float(v2)
                    self.add_segment(v1, v2, 0)
                elif len(vals) == 3:
                    x, y, z = vals
                    self.add_segment(float(x), float(y), float(z))

            if(tags[i] == "tag"):
                i+=1
                self.add_tag(tags[i])
            elif(tags[i] == "polygon"):
                doPoly = True
        return doPoly


    def isempty(self):
        if(len(self.X) ==0):
            return True
        return False

    
    def min_dist(self, pt):
        from pyTklib import NN
        return get_euclidean_distance(pt, NN(pt, [self.X, self.Y]))

    def centroid(self):
        if len(self) >= 3:
            return centroid(list(zip(self.X, self.Y)))
        else:
            return mean(self.X), mean(self.Y)


    def all_segments(self):
        """
        yield all segments in the polygon, including the one that
        connects the last point and the first point.
        """
        for i in range(len(self.X)):
            next = (i + 1) % len(self.X)
            yield [(self.X[i], self.Y[i]),
                   (self.X[next], self.Y[next])]


    def __len__(self):
        assert len(self.X) == len(self.Y)
        return len(self.X)

class point:
    def __init__(self, x=None, y=None, tag=None):
        self.x = x
        self.y = y
        self.tag = tag

    def tostring(self):
        mystr = "";
        if(self.tag != None):
            mystr = "tag:"+self.tag 
        
        mystr += " point:"
        mystr+= str(self.x) + "," + str(self.y)+":"
        mystr+="\n"
        return mystr

    def fromstring(self, mystr):
        tags = re.split("[ :]", mystr)
        doPt=False
        for i in range(len(tags)):
            if(doPt):
                #print "mystr", tags[i]
                vals = tags[i].split(",")
                if len(vals) == 2:
                    v1, v2 = vals
                    self.x = float(v1)
                    self.y = float(v2)
                    self.z = 0.0
                elif len(vals) == 3:
                    x, y, z = vals
                    self.x = float(x)
                    self.y = float(y)
                    self.z = float(z)
                    
            if(tags[i] == "tag"):
                i+=1
                self.tag = tags[i]
            elif(tags[i] == "point"):
                doPt = True

        return doPt

    def isempty(self):
        if(self.x == None or self.y == None or self.tag == None):
            return True
        return False

    def min_dist(self, pt):
        return get_euclidean_distance(pt, [self.x, self.y])

    def centroid(self):
        return self.x, self.y
import re
from scipy import sqrt
from carmen_util import get_euclidean_distance
def centroid(polygon):
    """
    Compute the centroid of a polygon represented as a list of tuples. 

    Computed following this web page: 
    http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
    """
    cx = 0.0
    cy = 0.0
    a = signedArea(polygon)
    if a == 0:
        X, Y = transpose(polygon)
        return mean(X), mean(Y)
        #raise ValueError("Polygon with zero area." + `polygon`)
    for i in range(0, len(polygon)):
        j = (i + 1) % len(polygon)
        
        
        multiplier = \
            polygon[i][0]*polygon[j][1] - \
            polygon[j][0]*polygon[i][1]
        cx += multiplier * (polygon[i][0] + polygon[j][0])
        cy += multiplier * (polygon[i][1] + polygon[j][1])

    cx = cx / (6.0*a)
    cy = cy / (6.0*a)
    return cx, cy

def allSegments(polygon):
    for i, p1 in enumerate(polygon):
        j= (i + 1) % len(polygon)
        p2 = polygon[j]
        yield p1, p2



def isInteriorPoint(polygon, point):
    """
    Determine if a point is inside a polygon
    """
    x, y = point
    c = False
    for (x1, y1), (x2, y2) in allSegments(polygon):
        if x == x1 and y == y1:
            return True
        if ((((y1 <= y) and (y < y2)) or
             ((y2 <= y) and (y < y1))) and
            (x < ((x2 - x1) * (y - y1)) / float(y2 - y1) + x1)):
            c = not c
    return c




def pointToSmallPolygon(point, width=0.1):
    """
    Converts a point to a small square with width
    """
    offset = width * 0.5
    x, y = point
    return [(x - offset, y - offset),
            (x - offset, y + offset),
            (x + offset, y + offset),
            (x + offset, y - offset),]

def signedArea(polygon):
    """
    
    Sign depends on whether vertices are clockwise or
    counterclockwise.
    
    Computed following this web page: 
    http://local.wasp.uwa.edu.au/~pbourke/geometry/polyarea/
    """
    area = 0
    for i in range(0, len(polygon)):
        j = (i + 1) % len(polygon)
        area = area + \
            float(polygon[i][0]*polygon[j][1]) - \
            float(polygon[j][0]*polygon[i][1])
    area = 0.5 * area
    return area





class polygon:
    def __init__(self):
        self.X = []
        self.Y = []
        self.tag = None
        
        self.z = None
        self.debug = False

    def add_segment(self, x, y, z=0):
        self.X.append(x)
        self.Y.append(y)
        
        if self.z == None:
            self.z = z
        else:
            assert self.z == z, (self.z, z)
        
    @property
    def vertices(self):
        """
        returns the verticies as a list of tuples.  Each tuple is a point.
        """
        return [p for p in zip(self.X, self.Y)]

    def add_tag(self, str):
        #print "adding tag:", str
        self.tag = str

    def get_tag(self):
        return self.tag

    def is_finished(self):
        if(sqrt((self.X[-1]-self.X[0])**2.0+(self.Y[-1]-self.Y[0])**2.0) < 5):
            return True

    def num_segments(self):
        return len(self.X)
    
    def get_segment(self, i):
        return self.X[i], self.Y[i]

    def tostring(self):
        #print "tag", self.tag
        mystr = "";
        if(self.tag != None):
            mystr = "tag:"+self.tag 
        
        mystr += " polygon:"
        for i in range(len(self.X)):
            x, y = self.X[i], self.Y[i]
            mystr+= str(x) + "," + str(y)+":"
        mystr+="\n"
        return mystr

    def fromstring(self, mystr):
        tags = re.split("[ :]", mystr)
        doPoly=False
        for i in range(len(tags)):
            if(doPoly):
                #print "mystr", tags[i]
                vals = tags[i].split(",")
                if(len(vals) == 2):
                    v1, v2 = vals
                    v1 = float(v1)
                    v2 = float(v2)
                    self.add_segment(v1, v2, 0)
                elif len(vals) == 3:
                    x, y, z = vals
                    self.add_segment(float(x), float(y), float(z))

            if(tags[i] == "tag"):
                i+=1
                self.add_tag(tags[i])
            elif(tags[i] == "polygon"):
                doPoly = True
        return doPoly


    def isempty(self):
        if(len(self.X) ==0):
            return True
        return False

    
    def min_dist(self, pt):
        from pyTklib import NN
        return get_euclidean_distance(pt, NN(pt, [self.X, self.Y]))

    def centroid(self):
        if len(self) >= 3:
            return centroid(list(zip(self.X, self.Y)))
        else:
            return mean(self.X), mean(self.Y)


    def all_segments(self):
        """
        yield all segments in the polygon, including the one that
        connects the last point and the first point.
        """
        for i in range(len(self.X)):
            next = (i + 1) % len(self.X)
            yield [(self.X[i], self.Y[i]),
                   (self.X[next], self.Y[next])]


    def __len__(self):
        assert len(self.X) == len(self.Y)
        return len(self.X)

class point:
    def __init__(self, x=None, y=None, tag=None):
        self.x = x
        self.y = y
        self.tag = tag

    def tostring(self):
        mystr = "";
        if(self.tag != None):
            mystr = "tag:"+self.tag 
        
        mystr += " point:"
        mystr+= str(self.x) + "," + str(self.y)+":"
        mystr+="\n"
        return mystr

    def fromstring(self, mystr):
        tags = re.split("[ :]", mystr)
        doPt=False
        for i in range(len(tags)):
            if(doPt):
                #print "mystr", tags[i]
                vals = tags[i].split(",")
                if len(vals) == 2:
                    v1, v2 = vals
                    self.x = float(v1)
                    self.y = float(v2)
                    self.z = 0.0
                elif len(vals) == 3:
                    x, y, z = vals
                    self.x = float(x)
                    self.y = float(y)
                    self.z = float(z)
                    
            if(tags[i] == "tag"):
                i+=1
                self.tag = tags[i]
            elif(tags[i] == "point"):
                doPt = True

        return doPt

    def isempty(self):
        if(self.x == None or self.y == None or self.tag == None):
            return True
        return False

    def min_dist(self, pt):
        return get_euclidean_distance(pt, [self.x, self.y])

    def centroid(self):
        return self.x, self.y
