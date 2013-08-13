import xml.dom.minidom as minidom
from forklift.arlcm import pallet_enum_t, object_enum_t


def getParameter(node, name, emptyStringIfEmpty=False):
    results = node.getElementsByTagName(name)
    assert len(results) == 1, (node.toprettyxml(), name, len(results))
    childNodes = results[0].childNodes
    if emptyStringIfEmpty and len(childNodes) == 0:
        return ""
    else:
        assert len(childNodes) == 1, (node.toprettyxml(), name)
        return str(childNodes[0].data)
def getData(node):
    childNodes = node.childNodes
    assert len(childNodes) == 1, node
    return childNodes[0].data


class Object:
    def __init__(self, xml):
        self.id = getParameter(xml, "id")
        self.type = xml.attributes["type"].value


        typeXml = xml.getElementsByTagName("type")[0]
        self.enum_type = typeXml.attributes["id"].value
        self.enum_value = int(getParameter(xml, "type"))
        
        if self.type == "pallet":
            enum_dict = pallet_enum_t.__dict__
        elif self.type == "object":
            enum_dict = object_enum_t.__dict__
        else:
            raise ValueError("Didn't get expected type: " + `self.type`)

        self.objectName = None
        for key, value in enum_dict.iteritems():
            if not key.startswith("_"):
                if value == self.enum_value:
                    self.objectName = key
        if self.objectName == None:
            raise ValueError("Couldn't find type: " + `self.type` + " in " + `enum_dict`)
        
        
        for node in xml.getElementsByTagName("position"):
            position = [float(s) for s in getData(node).split()]
            positionId = node.attributes["id"].value
            if positionId == "local-frame":
                self.positionLocalFrame = position
            elif positionId== "lat_lon_theta":
                self.latLonTheta = position
                self.lat = position[0]
                self.lon = position[1]
                self.theta = position[2]
            else:
                raise ValueError("Unexpected id: " + `positionId`)
        
                
                

class Objects:
    """
    Read the object xml file
    """
    def __init__(self, fname):
        xml = minidom.parse(fname)
        self.objects = []
        
        for objectXml in xml.getElementsByTagName("item"):
            self.objects.append(Object(objectXml))
            
    def __getitem__(self, idx):
        return self.objects[idx]
        
