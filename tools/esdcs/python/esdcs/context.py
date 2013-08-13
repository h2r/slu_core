from spatial_features import groundings
import numpy as na
from numpy import transpose as tp
from hash_utils import fasthash
import spatial_features_cxx as sf
from spatial_features.groundings import PhysicalObject, Place

def unique_groundings(groundings):
    hashes = set()
    result = []
    for g in groundings:
        if not g.hash_string in hashes:
            hashes.add(g.hash_string)
            result.append(g)
    return result

class MergedContext:
    """
    Faster version that doesn't compute all convience fields.
    """
    def __init__(self, context, new_objects):
        self.context = context
        self.new_objects = new_objects

        self.new_object_ids = set(o.id for o in new_objects)

        self.objects = unique_groundings(o for o in context.objects if not o in self.new_object_ids)
        self.places = context.places

        self.objects.extend(new_objects)

        self.grounding_id_to_grounding = dict(self.context.grounding_id_to_grounding)

        for o in self.objects:
            self.grounding_id_to_grounding[o.id] = o

        self.agent = self.grounding_id_to_grounding.get(self.getAgentId())

        self.hash_string = fasthash(context.hash_string +
                                    " ".join(o.hash_string for o in new_objects))


    def update_rep(self):
        self.centroid3d = na.zeros(3)
        count = 0.0
        self.start_t = None
        self.end_t = None
        for g in self.groundings:
            if hasattr(g, "centroid3d"):
                self.centroid3d += g.centroid3d
                count += 1
            if hasattr(g, "start_t"):
                if self.start_t == None or g.start_t < self.start_t and g.start_t != 0:
                    self.start_t = g.start_t
                if self.end_t == None or g.end_t > self.end_t:
                    self.end_t = g.end_t

        if self.start_t == None or self.end_t == None:
            assert self.start_t == None
            assert self.end_t == None
            self.start_t = 0
            self.end_t = 0
        self.length_seconds = (self.end_t - self.start_t) / 1000000.0
        self.centroid3d = self.centroid3d / count

        self.repr = ("Context(%s, %s)" %
                     tuple(repr(x) for x in (self.objects, self.places)))
        self.hash_string = fasthash(self.repr)

    @property
    def start_t(self):
        self.update_rep()
        return self.start_t

    @property
    def end_t(self):
        self.update_rep()
        return self.end_t

    @property
    def centroid3d(self):
        self.update_rep()
        return self.centroid3d
    @property
    def groundings(self):
        return self.grounding_id_to_grounding.values()

    def getAgentId(self):
        return self.context.getAgentId()

    def getGroundableById(self, gid):
        return self.grounding_id_to_grounding[gid]

    def asContext(self):
        return Context.from_groundings(self.groundings)

    def toYaml(self):
        return self.asContext().toYaml()


class Context:
    """
    Contextual information about the world.  It contains the location
    of objects over time, but is not associated with robot state.
    """
    @staticmethod
    def merge_context(context, new_objects):

        new_object_ids = set(o.id for o in new_objects)

        merged_objects = [o for o in context.objects if not o in new_object_ids]
        merged_objects.extend(new_objects)

        new_context = Context(merged_objects, context.places)
        return new_context
    @staticmethod
    def empty_context():
        return Context([], [])

    @staticmethod
    def from_groundings(groundings, agent_id=-100):
        objects = [g for g in groundings if isinstance(g, PhysicalObject)]
        places = [g for g in groundings if isinstance(g, Place)]
        return Context(objects, places, agent_id=agent_id)

    def withoutPaths(self):
        """
        Returns a new context without any paths.
        """
        return Context([o.withoutPath() for o in self.objects],
                       self.places, self.agent_id)

    def __init__(self, objects, places, agent_id=-100):

        self.objects = unique_groundings(objects)
        self.places = unique_groundings(places)
        self.agent_id = agent_id


        centroids = ([o.centroid2d for o in self.objects] +
                     [p.centroid2d for p in self.places])

        if len(centroids) != 0:

            bbox = sf.math2d_bbox(tp(centroids))

            self.static_bbox_pts = sf.math2d_bbox_to_polygon(bbox)
            self.static_scale = sf.math2d_dist(self.static_bbox_pts[0],
                                               self.static_bbox_pts[1])
        else:
            self.static_bbox_pts = []
            self.static_scale = 1.0


        self.moving_objects = [o for o in objects if o.path != None]

        self.paths = [o.path for o in self.moving_objects]

        self.groundings = self.objects + self.places + self.paths

        self.grounding_id_to_grounding = dict((g.id, g)
                                              for g in self.groundings)

        #assert len(self.groundings) == len(self.grounding_id_to_grounding), ("duplicate ids",
        #                                                                     sorted([g.id for g in self.groundings]),
        #                                                                     sorted(self.grounding_id_to_grounding.keys()))


        self.agent = self.grounding_id_to_grounding.get(self.getAgentId())

        self.update_rep()


    def update_rep(self):
        self.centroid3d = na.zeros(3)
        count = 0.0
        self.start_t = None
        self.end_t = None
        for g in self.groundings:
            if hasattr(g, "centroid3d"):
                self.centroid3d += g.centroid3d
                count += 1
            if hasattr(g, "start_t"):
                if self.start_t == None or g.start_t < self.start_t and g.start_t != 0:
                    self.start_t = g.start_t
                if self.end_t == None or g.end_t > self.end_t:
                    self.end_t = g.end_t

        if self.start_t == None or self.end_t == None:
            assert self.start_t == None
            assert self.end_t == None
            self.start_t = 0
            self.end_t = 0
        self.length_seconds = (self.end_t - self.start_t) / 1000000.0
        self.centroid3d = self.centroid3d / count

        self.repr = ("Context(%s, %s)" %
                     tuple(repr(x) for x in (self.objects, self.places)))
        self.hash_string = fasthash(self.repr)
        self.ids = set(g.id for g in self.groundings)

    def getObjectsSet(self):
        return self.objects

    def getPlacesSet(self):
        return self.places

    def getAgentId(self):
        return self.agent_id
    def getGroundableById(self, gid):
        return self.grounding_id_to_grounding[gid]

    def toYaml(self):
        yamlData = {}
        yamlData["objects"] = groundings.toYaml(self.objects)
        yamlData["places"] = groundings.toYaml(self.places)
        return yamlData

    def object_from_id(self, oid):
        objects = [o for o in self.objects if o.id == oid]
        assert len(objects) == 1, "This context seems to have multiple objects with the same ID: %s" % self.objects
        return objects[0]

    def __eq__(self, o):
        if isinstance(o, Context):
            if o.repr == self.repr:
                return True
            else:
                return False
    def __hash__(self):
        return hash(self.repr)

    def __repr__(self):
        return self.repr

    def withCroppedRange(self, start_t, end_t):
        """
        Returns a new context with everything cropped to the specified
        time range.
        """
        new_objects = [o.withCroppedRange(start_t, end_t) for o in self.objects]
        return Context(new_objects, self.places)


    def withGrounding(self, grounding):
        if isinstance(grounding, PhysicalObject):
            return Context(self.objects + [grounding],  self.places)
        elif isinstance(grounding, Place):
            return Context(self.objects, self.places + [grounding])
        else:
            raise ValueError("Weird grounding: " + `grounding.__class__` +
                             " g " + `grounding`)



    def withGroundings(self, groundings):
        new_objects = list(self.objects)
        new_places = list(self.places)
        for g in groundings:
            if isinstance(g, PhysicalObject):
                new_objects.append(g)
            elif isinstance(g, Place):
                new_places.append(g)
            else:
                raise ValueError("Weird grounding: " + `g.__class__` +
                                 " g " + `g`)
        return Context(new_objects, new_places)


    @staticmethod
    def fromYaml(yamlData):
        objects = groundings.fromYaml(yamlData["objects"])
        places = groundings.fromYaml(yamlData["places"])
        return Context(objects, places)



