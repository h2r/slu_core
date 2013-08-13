import tag_util
import numpy as na
import math

class UtClass:
    def __init__(self, name, properties):
        self.name = name
        self.properties = {}
        self.children = []
        for p in properties:
            self.addProperty(p)
        self.location = None
        self.static_mesh = None
    def addProperty(self, line):
        firstEq = line.find("=")
        if firstEq != -1:
            key = line[0:firstEq]
            value = line[firstEq+1:]
        else:
            key, value = line.split()
        key = key.strip()
        value = value.strip()
        if key == "Location":
            pts = value[1:-1].split(",")
            value = [float(p.split("=")[1].strip()) for p in pts]
            self.location = value
        elif key == "Tag":
            value = value[1:-1]
            self.tag = value
        elif key == "StaticMesh":
            self.static_mesh = value
        self.properties[key] = value

    def flatten(self):
        for child in self.children:
            yield child
            for grandchild in child.flatten():
                yield grandchild
        
    @property
    def location_xy(self):
        if self.location == None:
            return None
        elif len(self.location) == 2:
            x, y = self.location
            return x, y
        elif len(self.location) == 3:
            x, y, z = self.location
            return x, y
        else:
            raise ValueError("Unexpected location structure: " + `self.location`)
            
def readFile(fname):
    """
    Takes as input a t3d file, and outputs a tag file.  The t3d file
    was created by opening a .ut2 file in the unreal editor and saving
    it as an unreal text file.  I was able to do this on wine/Ubuntu
    even though the editor doesn't render on ubuntu.
    """
    f = open(fname)
    root = UtClass("root", [])
    classStack = [root]


    for lineno, line in enumerate(f):
        lineno += 1 # 1-based and not zero based
        try:
            if line.strip() == "":
                continue
            currentClass = classStack[-1]

            tokens = line.split()
            if tokens[0] == "Begin":
                name = tokens[1]

                if len(tokens) == 2:
                    properties = []
                else:
                    properties = tokens[2:]
                cls = UtClass(name, properties)            
                currentClass.children.append(cls)
                classStack.append(cls)
            elif tokens[0] == "End":
                name = tokens[1]
                assert currentClass.name == name, (currentClass.name, name)
                classStack.pop()
            else:
                currentClass.addProperty(line)

        except:
            print "line", lineno
            print line
            raise
    return root

def extract_tag(actor):
    tag = None
    if actor.tag != None:
        if  "door" in actor.tag.lower():
            tag = "door"

    if actor.static_mesh != None:
        if  ".car1" in actor.static_mesh:
            tag = "car"
        elif "Streetlight" in actor.static_mesh:
            tag = "streetlight"
        elif ".van1" in  actor.static_mesh:
            tag = "van"

        elif ".blazerBlue" in actor.static_mesh:
            tag = "blue_blazer"
        elif ".Blazer" in actor.static_mesh:
            tag = "blazer"
        elif "Tree" in actor.static_mesh:
            tag = "tree"
        elif "Casino" in actor.static_mesh:
            tag = "casino"
        elif "SignNoPArking" in actor.static_mesh:
            tag = "no_parking_sign"
        elif "speedlimit" in actor.static_mesh:
            tag = "speedlimit_sign"
        elif "NewsBoxes" in actor.static_mesh:
            tag = "newsboxes"
    return tag
def write_tag_file(actors, translate_function, output_fname):
    points = []
    for a in actors:
        tag = extract_tag(a)
        if tag != None:
            location = a.location
            x, y, = a.location_xy
            cx, cy = translate_function(x, y)
            point = tag_util.point(cx, cy, tag)

            if tag in ["blazer", "blue_blazer", "van"]:
                print tag, x, y
            points.append(point)

    print "writing", len(points), "tags to", output_fname
    tag_util.save_polygons([], points, output_fname)

def derive_transform(a1, a2, b1, b2):
    a1x, a1y = a1
    a2x, a2y = a2
    b1x, b1y = b1
    b2x, b2y = b2

    affine = na.identity(3)
    
    # translate A point to (0, 0)
    affine = na.dot(na.array([[1, 0, -a1x], [0, 1, -a1y], [0, 0, 1]]), affine)
    
    # scale to B size
    scale = math.hypot(b2x - b1x, b2y - b1y) / math.hypot(a2x - a1x, a2y - a1y)
    affine = na.dot(na.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]]), affine)
    
    # rotate to B orientation
    #theta = math.atan2(a2x - a1x, a2y - a1y) - math.atan2(b2x - b1x, b2y - b1y)
    # we know it's 90.
    theta = math.pi/2
    print "theta", math.degrees(theta)
    affine = na.dot(na.array([[math.cos(theta), -math.sin(theta), 0], 
                              [math.sin(theta), math.cos(theta), 0], 
                              [0, 0, 1]]), affine)


    # reflect across y axis
    affine = na.dot(na.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                    affine)

    
    # translate back to B point
    affine = na.dot(na.array([[1, 0, b1x], [0, 1, b1y], [0, 0, 1]]), affine)
    ax, bx, cx, ay, by, cy = affine[0,0], affine[0,1], affine[0,2], affine[1,0], affine[1,1], affine[1,2]
    return lambda x, y: (ax * x + bx * y + cx, ay * x + by * y + cy)

    


def main():
    import sys
    fname = sys.argv[1]
    output_fname = sys.argv[2]
    print "loading", fname
    utmap = readFile(fname)
    actors = [cls for cls in utmap.flatten() if cls.name == "Actor"]

    # to carmen as in navigator gui
    #translate_function = derive_transform((-2235, -413), (5255, 1343),
    #                        (20.9, 10.6), (28.1, 40.2))

    # to carmen as in annote_util
    translate_function = derive_transform((-2235, -413), (5255, 1343),
                                          (209, 107), (280, 406))
    
    
    write_tag_file(actors, translate_function, output_fname)


if __name__ == "__main__":
    main()
"""
blazer in bottom middle
carmen
20.9, 10.6 
unreal
-2235.00, -413.00

van in top right
carmen
28.1, 40.2
unreal
5255, 1343

blue blzer in upper left
carmen
11.6, 34.6
unreal
3601, -2845


"""
