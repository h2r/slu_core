import landmark_icon_cache
import math
import matplotlib.patches
from esdcs.groundings import PhysicalObject, Path, Place
from matplotlib_util import size_of_axes_in_data_coordinates

def drawPath(axes, path, plotArgs, shouldDrawStartAndEnd=True, 
             shouldDrawLengthOne=True):
    artists = []
    X, Y = path.points_xy
    artists.extend(axes.plot(X, Y, **plotArgs))
    if len(path) == 1 and shouldDrawLengthOne:
        artists.append(axes.scatter(X, Y))

    if shouldDrawStartAndEnd:
        x, y, z, theta = path.points_ptsztheta[0]
        artists.extend(drawRobot(axes, x, y, theta,
                                 facecolor="green"))
        x, y, z, theta = path.points_ptsztheta[-1]            
        artists.extend(drawRobot(axes, x, y, theta,
                                 facecolor="red"))            

    return artists

def drawRobotFromStateApp(axes, stateApp):
    x, y, z = stateApp.curr_location
    theta = math.degrees(stateApp.curr_orientation)
    return drawRobot(x, y, theta, axes)

def drawRobot(axes, x, y, theta_rad, facecolor="white"):
    theta_deg = math.degrees(theta_rad)
    artists = []
    
    # draw it the same size regardless of the coordinate system.
    size = size_of_axes_in_data_coordinates(axes)
    #size=10
    plot = matplotlib.patches.Wedge((x, y), size * 0.02, 
                                    theta_deg + 45, theta_deg - 45,
                                    zorder=10,
                                    facecolor=facecolor)

    axes.add_artist(plot)
    artists.append(plot)
    return artists

def drawGrounding(axes, grounding, plotArgs=dict(color="black"),
                  shouldDrawPrismPath=True, shouldDrawIcon=True, 
                  shouldDrawText=True, shouldDrawPrism=True,
                  shouldDrawStartAndEnd=None):
    if isinstance(grounding, PhysicalObject) or isinstance(grounding, Place):
        return drawObject(axes, grounding, plotArgs, shouldDrawPrismPath,
                          shouldDrawIcon=shouldDrawIcon, 
                          shouldDrawText=shouldDrawText,
                          shouldDrawStartAndEnd=shouldDrawStartAndEnd,
                          shouldDrawPrism=shouldDrawPrism)
    elif isinstance(grounding, Path):
        return drawPath(axes, grounding, plotArgs, shouldDrawStartAndEnd,
                        shouldDrawLengthOne=True)
    elif isinstance(grounding, list):
        return []
    else:
        raise ValueError("Unexpected type: " + `grounding`)

    
def drawObject(axes, physicalObject, plotArgs=dict(color="black"),
               shouldDrawPath=True, shouldDrawPrismPath=False, 
               shouldDrawStartAndEnd=None, shouldDrawIcon=True, 
               shouldDrawText=True, shouldDrawPrism=True):
    artists = []
    obj = physicalObject
    if shouldDrawPrism:
        artists.extend(drawPrism(axes, obj.prism, plotArgs))
    x, y = obj.prism.centroid2d()

    tagMap = {("tires", "pallet"):"tire_pallet",
              ("generator", "accessories", "pallet"):"box_pallet",
              ("flatbed", "trailer", "wheel"):"wheel",
              ("flatbed", "trailer"):"trailer"
              }
    if obj.tags in tagMap:
        tag = tagMap[obj.tags]
    else:
        tag = obj.tags[0] if len(obj.tags) > 0 else None
    icon = landmark_icon_cache.getIcon(tag)
    if icon != None and shouldDrawIcon:
        width, height, channels = icon.shape
        draw_width = 1.5
        draw_height = draw_width*width/height
        lower_left_x = x - draw_width / 2.0
        lower_left_y = y - draw_height / 2.0

        img = axes.imshow(icon, origin="lower",
                          extent=(lower_left_x,
                                  lower_left_x + draw_width, 
                                  lower_left_y,
                                  lower_left_y + draw_height))
        artists.append(img)
    else:

        if len(obj.tags) > 0 and shouldDrawText:
            artists.append(axes.text(x, y, " ".join(obj.tags), size=16))
    if shouldDrawPath and hasattr(obj, "path") and obj.path != None:
        if shouldDrawStartAndEnd == None:
            if len(obj.path) <= 1:
                shouldDrawStartAndEnd = False
            else:
                shouldDrawStartAndEnd = True

        artists.extend(drawPath(axes, obj.path, plotArgs, 
                                shouldDrawStartAndEnd, shouldDrawLengthOne=False))

    if shouldDrawPrismPath and hasattr(obj, "path") and obj.path != None:
        for t in obj.path.timestamps:
            prism = obj.prismAtT(t)
            drawPrism(axes, prism, dict(color="blue"))

        
    return artists


def drawPrism(axes, prism, plotArgs=dict(color="black")):    
    artists = []
    artists.extend(axes.plot(prism.pX,
                             prism.pY,
                             **plotArgs))

    return artists


def entireTextAsFormattedLabelText(esdc):
    start, end = esdc.range
    entireText = esdc.entireText
    if end - start < 0:
        return entireText
    else:
        labelText = (entireText[0:start]+ 
                     "<b>" + entireText[start:end] + "</b>" +
                     entireText[end:])
        return labelText
    
    
