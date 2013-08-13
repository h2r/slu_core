from esdcs.groundings import PhysicalObject, Prism, Path, Place
from numpy import transpose as tp
from pr2_state import Pr2State, EndEffector, compute_places
#import tf.transformations
import sys, time
#from keyboard import *
import json
from numpy import arange
import spatial_features_cxx as sfe
from esdcs.context import Context


def compute_places(table, body):
    X, Y = table.points_xy
    table_xmin = min(X)
    table_xmax = max(X)
    table_ymin = min(Y)
    table_ymax = max(Y)

    body_x, body_y = body.centroid2d

    # red block start.
    # x: 0.638734,  y: 0.030862
    # red block end.
    # x: 0.7,  y: 0.03
    # x: 0.5,  y: 0.03
    # x: 0.4,  y: 0.03


    # x: 0.5,  y: 0.1
    # x: 0.5,  y: 0.3
    # x: 0.5,  y: -0.1 
    # x: 0.5,  y: -0.2
    # -0.3 and higher - kinect calibration

    # corners (left/right relative to pr2, back is close to pr2)
    # corners are more conservative than the initial numbers, but
    # I tested pickup and put down for all.
    # x: 0.7, y: -0.2 (front right)
    # x: 0.4, y: -0.2 (back right)
    # x: 0.7, y:  0.0 (front left)
    # x: 0.4, y:  0.0 (back left)

    #print "body", body_x, body_y
    body_xmin = 0.4
    body_xmax = 0.7
    body_ymin = -0.2
    body_ymax = 0.0

    #print "table min", table_xmin, table_ymin
    #print "table max", table_xmax, table_ymax

    xmin = max(body_xmin, table_xmin)
    xmax = min(body_xmax, table_xmax)
    ymin = max(body_ymin, table_ymin)
    ymax = min(body_ymax, table_ymax)


    size = max([xmax - xmin, ymax - ymin]) / 3
    places = []
    #        for x in [0.3, 0.5, 0.7]: # arange(-0.5, 1.5, 0.5):
    #            for y in arange(-0.35, 0.101, 0.1):

    pr = 0.03
    try:
        for x in arange(xmin, xmax + 0.01, size):
            for y in arange(ymin, ymax + 0.01, size):
                place = Place(Prism(tp([(x - pr, y - pr), (x + pr, y - pr),
                                        (x + pr, y + pr), (x - pr, y + pr)]),
                                    table.prism.zEnd, table.prism.zEnd + 0.1))
                if sfe.math2d_is_interior_point(place.centroid2d, table.prism.points_xy):
                    places.append(place)
    except:
        print "xmin", xmin
        print "xmax", xmax
        print "ymin", ymin
        print "ymax", ymax
        print "size", size
        raise


    return places



class WorldStateFromRos:
    """
    Represents the position of the pr2 as read from ROS, as physical objects. 
    """


    @staticmethod
    def create_and_subscribe(rosbridge):
        """
        Create a world state that is subscribed to the right ros
        topics to be automatically updated as new messages come in.
        """

        wsfr = WorldStateFromRos()

        def update_pose(arg):
            wsfr.update_pose(eval(arg["data"]), time.time() * Path.ONE_SECOND_IN_MICROS)

        rosbridge.subscribe("/blocknlp/slu_pose", 
                            "std_msgs/String", update_pose)

        def update_objects(arg):
            wsfr.update_objects(arg, time.time() * Path.ONE_SECOND_IN_MICROS)
        #rosbridge.subscribe("/blocknlp/object_list", 
        rosbridge.subscribe("/mit/object_list", 
                            "object_manager/ObjectList", update_objects)

        return wsfr

    def __init__(self):
        self.body_pobj = None
        self.rightee_pobj = None
        self.leftee_pobj = None
        self.objects = {}
        self.object_id_to_inhand = {}


    def generate_context(self):
        """
        Returns a Context generated from all of the current physical objects.
        """
        pobjs = self.objects.values();

        used_pobjs = [o for o in pobjs if o.path.length_meters > 0.1 and "block" in o.tags]



        used_tags = set(o.tags for o in used_pobjs)
        used_ids = set(o.id for o in used_pobjs)

        for o in pobjs:
            if o.id not in used_ids and o.tags not in used_tags:
                used_pobjs.append(o)
                used_tags.add(o.tags)
                used_ids.add(o.id)
            # if len(used_pobjs) >= 3:
            #    break
                
        table = [o for o in pobjs if "table" in o.tags][0]
        used_pobjs.append(table)
        used_pobjs.append(self.body_pobj);
        used_pobjs.append(self.leftee_pobj);
        used_pobjs.append(self.rightee_pobj);

        return Context(used_pobjs, [] )
    @property
    def held_object(self):
        held_oid = None
        #print "object_id_to_inhand", self.object_id_to_inhand
        for oid, value in self.object_id_to_inhand.iteritems():
            if value:
                if held_oid != None:
                    raise ValueError("more than one held object")
                else:
                    held_oid = oid
        if held_oid == None:
            return None
        else:
            return self.objects[held_oid]
                
    def update_objects(self, object_list_json, timestamp):
        """
        Updates the object locations and geometries from the specified
        ROS message.
        """
        if len(self.objects) == 0:
            verbose = True
        else:
            verbose = False
        self.object_id_to_inhand = {}
        self.objects = {}

        if self.rightee_pobj == None:
            return

        #keyboard()

        # TBD - what is actually coming in from ROSBRIDGE?
        if isinstance(object_list_json, str):
            js = json.loads(object_list_json);
        else:
            js = object_list_json

        obj_list = js["object_list"];


        self.objects = {}

        for o in obj_list:
            cx = o["pose"]["position"]["x"]; # centroid
            cy = o["pose"]["position"]["y"]; # centroid
            cz = o["pose"]["position"]["z"]; # centroid
            if o["inhand"]:
                #print "in hand", o["id"]
                if not self.object_id_to_inhand.get(o["id"], False) and verbose:
                    print "  - object %d was not in hand, now is " % (o["id"],)


                cx, cy, cz, theta = self.rightee_pobj.path.locationAtT(timestamp)
                self.object_id_to_inhand[o["id"]] = True
            else:
                # TBD - how to handle log timestamps!
                qx = o["pose"]["orientation"]["x"];
                qy = o["pose"]["orientation"]["y"];
                qz = o["pose"]["orientation"]["z"];
                qw = o["pose"]["orientation"]["w"];
                # theta from quaternion
                #(r,p,yaw) = tf.transformations.euler_from_quaternion([qx,qy,qz,qw]);
                if self.object_id_to_inhand.get(o["id"], False) and verbose:
                    print "  - object %d was in hand, now isn't " % (o["id"],)
                self.object_id_to_inhand[o["id"]] = False

            points_xyztheta = tp([(cx, cy, cz, 0)]);
            path = Path( [0], points_xyztheta )


            # if first time getting object, create
            if not self.objects.has_key( o["id"] ):
                if verbose:
                    print "  - creating object %d"%(o["id"])
                dx = o["dim"]["x"]; # dimensions
                dy = o["dim"]["y"];
                dz = o["dim"]["z"];
                r, g, b, a = o["color"]["r"], o["color"]["g"], o["color"]["b"], o["color"]["a"]
                #
                #if r > b:
                #    color = "red"
                #else:
                #    color = "blue"

                # tbd - prentice - updated to retrieve labels from object manager
                #color = rgb_to_name.rgb_to_name_h(r, g, b)
                color_unicode = o["label"]
                color = color_unicode.encode('ascii')
                if color == "purple":
                    color = "blue"

                # NOTE: centroid is center of top of the box, dim's are full dimensions
                self.objects[ o["id"] ] = PhysicalObject(Prism(tp([ (cx-dx/2.0, cy-dy/2.0),
                                                                    (cx+dx/2.0, cy-dy/2.0),
                                                                    (cx+dx/2.0, cy+dy/2.0),
                                                                    (cx-dx/2.0, cy+dy/2.0)]),
                                                            cz-dz, cz),
                                                         tags=("block", color), # tbd ...
                                                         #path=path,
                                                         lcmId=o["id"])

            else:
                self.objects[ o["id"] ] = self.objects[ o["id"] ].withExtendedPath(path);

        # TABLE
        if "table" in js:
            table = js["table"];
            cx = table["pose"]["pose"]["position"]["x"]
            cy = table["pose"]["pose"]["position"]["y"]
            cz = table["pose"]["pose"]["position"]["z"]
            if not self.objects.has_key("table"):
                if verbose:
                    print "  - creating table"
                x_min = table["x_min"]
                x_max = table["x_max"]
                y_min = table["y_min"]
                y_max = table["y_max"]
                self.objects[ "table" ] = PhysicalObject(Prism(tp([(cx+x_min, cy+y_min),
                                                                   (cx+x_max, cy+y_min),
                                                                   (cx+x_max, cy+y_max),
                                                                   (cx+x_min, cy+y_max)]),
                                                              cz-0.1, cz),
                                                        tags=("table",),
                                                        lcmId=Pr2State.AGENT_ID - 4);
                #points_xyztheta = tp([(cx, cy, cz, 0)]);
                #path = Path( [timestamp], points_xyztheta )
                #self.objects[ "table" ] = self.objects[ "table" ].withPath(path);


#        # for actual object_list, object
#        for o in obj_list:
#            # if first time getting object, create
#            if not self.objects.has_key( o.id ):
#                c = o.pose.position; # centroid
#                d = o.dim; # dimensions
#                # NOTE: centroid is center of top of the box, dim's are full dimensions
#                self.objects[ o.id ] = PhysicalObject(Prism(tp([ (c.x-d.x/2.0, c.y-d.y/2.0),
#                                                                 (c.x+d.x/2.0, c.y-d.y/2.0),
#                                                                 (c.x+d.x/2.0, c.y+d.y/2.0),
#                                                                 (c.x-d.x/2.0, c.y+d.y/2.0)]),
#                                                            c.z-d.z, c.z),
#                                                      tags=("block"), # tbd ...
#                                                      lcmId=Pr2State.AGENT_ID+2+o.id);
#            # extend path
#            # TBD - how to handle log timestamps!
#            timestamps = [ int(round(time.time() * 1000)) ];  # now
#            c = o.pose.position;
#            q = o.pose.orientation;
#            # theta from quaternion
#            (r,p,yaw) = euler_from_quaternion([q.x,q.y,q.z,q.w]);
#            points_xyztheta = [ (c.x, c.y, c.z, yaw) ];
#            path = Path( timestamps, points_xyztheta )
#            self.objects[ o.id ] = self.objects[ o.id ].withExtendedPath(path);


    def update_pose(self, data, timestamp):
        """
        Updates the pose using a dictionary of frame names to
        translation, rotation.  This is created using slu_manager.py
        in ROS.  The results are stored as self.body_pobj,
        self.rightee_pobj, and self.leftee_pobj in this class.
        """

        if timestamp == None:
            raise ValueError("Timestamp must not be None.")
        if "base_link" not in data:
            return 
        for i, key in enumerate(["right", "left"]):
            tf_key = key[0] + "_gripper_palm_link"
            if tf_key not in data:
                continue
            (x, y, z), rot = data[tf_key]
            #(x, y, z), rot = data[key[0] + "_gripper_l_finger_tip_frame"]
            points_xyztheta = tp([ (x, y, z, 0) ]);
            path = Path( [timestamp], points_xyztheta )

            # if first time, instantiate PhysicalObjects
            if ( self.__dict__["%see_pobj" % key] == None ):
                self.__dict__["%see_pobj" % key] = PhysicalObject(Prism(tp([(x - 0.1, y - 0.1),
                                                                            (x + 0.1, y - 0.1),
                                                                            (x + 0.1, y + 0.1),
                                                                            (x - 0.1, y + 0.1)]),
                                                                        z - 0.1, z + 0.1),
                                                                  tags=("robot", key, "hand"),
                                                                  lcmId=Pr2State.AGENT_ID + i, path=path)
                print "  - initializing %s\n"%key
            #(r, p, yaw) = tf.transformations.euler_from_quaternion(rot); # tbd rot data format
            self.__dict__["%see_pobj"%key] = self.__dict__["%see_pobj"%key].withExtendedPath(path);
            #print "%s x=%f y=%f z=%f"%(key, x, y, z)
        (x, y, z), rot = data["base_link"]
        points_xyztheta = tp([ (x, y, z, 0) ]);
        path = Path( [timestamp], points_xyztheta )

        if ( self.body_pobj == None ):
            self.body_pobj = PhysicalObject(Prism(tp([(x - 0.25, y - 0.25),
                                                      (x + 0.25, y - 0.25),
                                                      (x + 0.25, y + 0.25),
                                                      (x - 0.25, y + 0.25)]),
                                                  0, 1),
                                            tags=("robot", "base"),
                                            lcmId=Pr2State.AGENT_ID + i + 1, path=path)
            print "  - initializing base\n"
        #(r, p, yaw) = tf.transformations.euler_from_quaternion(rot); # tbd rot data format
        self.body_pobj = self.body_pobj.withExtendedPath(path);

    @property
    def blocks(self):
        return [o for (k, o) in self.objects.iteritems() if "block" in o.tags]

    @property
    def table(self):
        if "table" in self.objects:
            return self.objects["table"]
        else:
            return None

    @property
    def has_data(self):
        return self.body_pobj != None

    

    def current_state(self):
        if self.body_pobj == None:
            raise ValueError("No pose information.")
        elif self.table == None:
            raise ValueError("No table.")
        
        places = compute_places(self.table, self.body_pobj)
        print "making state", self.held_object
        #return Pr2State.from_pobj(self.body_pobj.atT(-1), self.rightee_pobj.atT(-1), self.leftee_pobj.atT(-1),
        #self.table.atT(-1), [b.atT(-1) for b in self.blocks], places)
        rightee_pobj = self.rightee_pobj.atT(-1)
        leftee_pobj = self.leftee_pobj.atT(-1)
        leftee = EndEffector(leftee_pobj.centroid3d + (0,), leftee_pobj)
        rightee = EndEffector(rightee_pobj.centroid3d + (0,), rightee_pobj, self.held_object)
        return Pr2State(self.body_pobj.atT(-1), [rightee, leftee], 
                        self.table.atT(-1), [b.atT(-1) for b in self.blocks], places)
        
