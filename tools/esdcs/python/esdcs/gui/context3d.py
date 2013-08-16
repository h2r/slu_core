import sys
import yaml
from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL, Qt
import basewindow
from PyQt4 import QtGui, QtOpenGL
from OpenGL import GLU
from spatial_features.groundings import Prism, Path, PhysicalObject, Place
from esdcs.context import Context
import spatial_features_cxx as sf
import math
import numpy as na
from numpy import transpose as tp
from assert_utils import assert_sorta_eq
import spatial_features_cxx as sf
from  OpenGL.GL import glBegin, GL_LINES, glVertex2f, glEnd, glPushMatrix, \
    glTranslatef, glVertex3f, glEnable, GL_DEPTH_TEST, glViewport, \
    glMatrixMode, GL_PROJECTION, glLoadIdentity, GL_MODELVIEW, glClear, \
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glTranslate, glScale, glRotate, \
    glPopMatrix, glPopAttrib, glPushAttrib, GL_BLEND, GL_SRC_ALPHA, \
    GL_ONE_MINUS_SRC_ALPHA, glBlendFunc, GL_ENABLE_BIT, GL_LINE_BIT, \
    glColor3f, glDisable, GL_QUADS, glVertex3i, GL_COLOR_MATERIAL, \
    GL_POLYGON_BIT, GL_POLYGON_OFFSET_FILL, glPolygonOffset, glVertex2d, \
    glScalef, GL_RENDER, glFlush, glPushName, glInitNames, \
    glRenderMode, GL_SELECT, GL_VIEWPORT, glGetIntegerv, glSelectBuffer, \
    GL_DEPTH_COMPONENT, glReadPixels, GL_DOUBLE, GL_FLOAT, GL_LINE_LOOP, \
    GL_LINE_STRIP, glRotatef, glMultMatrixf

from math import sin, cos, atan2, degrees
color_map = {
    "red":(1, 0, 0),
    "green":(0, 1, 0),
    "blue":(0, 0, 1),
    "yellow":(1, 1, 0),
    "black":(0, 0, 0),
    "yellow":(1, 1, 0),
    "cyan":(0, 255, 255),
}

import context3d_ui

def rotation_matrices(rpy):
    roll, pitch, yaw = rpy
    rx = na.array([[1, 0, 0, 0],
                   [0, cos(roll), -sin(roll), 0],
                   [0, sin(roll), cos(roll), 0],
                   [0, 0, 0, 1]
                   ])
    ry = na.array([[cos(pitch), 0, sin(pitch), 0],
                   [0, 1, 0, 0],
                   [-sin(pitch), 0, cos(pitch), 0],
                   [0, 0, 0, 1]
                   ])
    rz = na.array([[cos(yaw), -sin(yaw), 0, 0],
                   [sin(yaw), cos(yaw), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]
                   ])
    return rx, ry, rz

def lookAt(point_xyz, camera_xyz):
    """
    Implemented following the math here:
    http://pyopengl.sourceforge.net/documentation/manual/gluLookAt.3G.html
    """
        #eye_xyz - 
    eye_xyz = na.array(camera_xyz)
    center_xyz = na.array(point_xyz)
    UP = na.array([0, 0, 1])
    F = center_xyz - eye_xyz
    f = F / na.linalg.norm(F)
    s = na.cross(f, UP)
    u = na.cross(s, f)
    M = na.array([[s[0], s[1], s[2], 0],
                  [u[0], u[1], u[2], 0],
                  [-f[0], -f[1], -f[2], 0],
                  [    0,     0,     0, 1]])
    return M



def round_to_125(value):

    v = 1;

    while (v < value):
        if (v < value):
            v *= 2;
        if (v < value):
            v = v/2 * 5;
        if (v < value):
            v *= 2;

    return v;



class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.yRotDeg = 0.0
        self.camera_xyz = na.array([10, 10, 10])
        self.camera_rpy = na.array([0, 0, 0])
        self._selected_groundings = []
        self._highlighted_groundings = {}
        self.groundingFilter = lambda x: True
        self.placeOnObjectFilter = lambda x: True
        self.clearModes()
        self.placeHeight = 0.1

        self.setContext(Context.empty_context(), updateGL=False)


    def highlightGroundings(self, groundings, color="green"):
        self._highlighted_groundings[color] = groundings
        start_ts = [self._context.start_t]
        end_ts = [self._context.end_t]
        for g in groundings:
            if not g:
                continue
            if g.start_t != 0:
                start_ts.append(g.start_t)

            if g.end_t != 0:
                end_ts.append(g.end_t)
                
        self.end_t = max(end_ts)
        self.start_t = min(start_ts)
    def setFilter(self, groundingFilter):
        self.groundingFilter = groundingFilter
        self.updateGL()
        
    def clearModes(self):
        self.movingCamera = False
        self.rotatingCamera = False
        self.placeMode = False
        self.objectMode = False

    def clearSelection(self):
        self._selected_groundings = []
        self.updateGL()
    def setTime(self, time):
        self._t = time
        self.updateGL()

    def drawPath(self, path, color):
        glPushMatrix()
        glColor3f(*color_map[color])
        glBegin(GL_LINE_STRIP);
        for (x, y, z, theta) in path.points_ptsztheta:
            glVertex3f(x, y, z)
        glEnd();    
        glPopMatrix()        

    def drawPrism(self, prism, color="blue"):
        glPushMatrix()
        glColor3f(*color_map[color])

        for pts_xyz in [prism.lower_points_xyz, prism.upper_points_xyz]:
            glBegin(GL_LINE_LOOP);
            for x, y, z in tp(pts_xyz):
                glVertex3f(x, y, z)
            glEnd();

        glBegin(GL_LINES);
        for lower_xyz, upper_xyz in zip(tp(prism.lower_points_xyz), tp(prism.upper_points_xyz)):
            glVertex3f(*lower_xyz)
            glVertex3f(*upper_xyz)
        glEnd();


        glPopMatrix()


    def drawObject(self, physicalObject, color):
        glPushMatrix()
        prism = physicalObject.prismAtT(self._t)
        self.drawPrism(prism, color)
        if physicalObject.path != None:
            self.drawPath(physicalObject.path, color)
        x, y, z = prism.centroid3d()
        glColor3f(*color_map["black"])

        self.renderText(x, y, z, 
                        str(physicalObject.id) + " " + str(physicalObject.tags))
        glPopMatrix()



    def drawGrounding(self, g, color=None):
        if color == None:
            if g in self._selected_groundings:
                color = "yellow"
            else:
                color = "blue"
        if isinstance(g, PhysicalObject):
            self.drawObject(g, color)
        elif isinstance(g, Path):
            self.drawPath(g, "cyan")
        elif isinstance(g, Place):
            self.drawPrism(g.prism, color)
        else:
            raise ValueError("Unexpected type: " + `g`)



    def pickPoint(self, wx, wy, wz=None):
        wy = self._height - wy
        if wz == None:
            wz = glReadPixels (wx, wy, 
                               1, 1, GL_DEPTH_COMPONENT, GL_FLOAT);
        try:
            return na.array(GLU.gluUnProject(wx, wy, wz))
        except ValueError:
            return None
        
    def findIntersect(self, here_point, select_point, obj=None,
                      grounding_filter=lambda x: True):
        if obj == None:
            obj = self.findClosestGrounding(select_point, grounding_filter)
        p = obj.prism
        x, y, z = sf.math3d_intersect_line_plane(tp([select_point, here_point]),
                                                 tp([(x, y, p.zEnd)
                                                     for x, y in p.points_pts]))
        
        assert_sorta_eq(z, p.zEnd)
        z = p.zEnd
        return (x, y, z), obj
        
    def mousePressEvent(self, event):
        select_point = self.pickPoint(event.x(), event.y())
        if select_point == None:
            return
        if self.placeMode:
            x, y, z = select_point
            z = 0.0001
            if self.placeOnTopOf:
                here_point = self.pickPoint(event.x(), event.y(), 0)
                point, obj = self.findIntersect(here_point, select_point,
                                                self.onTopOfObj,
                                                self.placeOnObjectFilter)
                if self.onTopOfObj == None:
                    self.onTopOfObj = obj
                if self.onTopOfObj == obj:
                    self.place_footprint.append(point)
                    self.updateGL()
            else:
                self.place_footprint.append((x, y, z))                    
                self.updateGL()
        elif self.objectMode:
            
            self.selectGrounding(select_point)
            self.clearModes()
        else:
            self.start = select_point
            self.start_wnd = event.x(), self._height - event.y()


            if event.button() == Qt.RightButton:
                self.rotatingCamera = True
            else:
                self.movingCamera = True



    def findClosestGrounding(self, point, grounding_filter=lambda x: True):
        distances = []
        groundings = [g for g in self._context.groundings 
                      if (hasattr(g, "centroid3d") and 
                          not isinstance(g, Path)) and grounding_filter(g)]
        if len(groundings) != 0:
            for o in groundings:
                distances.append(sf.math3d_dist(point, o.centroid3d))


            idx = na.argmin(distances)

            grounding = groundings[idx]
            return grounding
        else:
            return None

    def selectGrounding(self, point):
        grounding = self.findClosestGrounding(point)
        if grounding != None:
            self._selected_groundings = [grounding] 
            self.emit(SIGNAL("selectedGrounding()"))
            self.updateGL()


    def setSelectedGroundings(self, groundings):
        self._selected_groundings = groundings 
        self.emit(SIGNAL("selectedGrounding()"))
        self.updateGL()


    def mouseReleaseEvent(self, event):
        self.movingCamera = False
        self.rotatingCamera = False
        if self.placeMode:
            if event.button() == Qt.RightButton:
                place = self.makePlace()
                self.placeMode = False
                self._selected_groundings.append(place)
                self.emit(SIGNAL("selectedGrounding()"))
                self.clearModes()

                
    def mouseMoveEvent(self, event):
        if self.movingCamera:
            here = self.pickPoint(event.x(), event.y())
            
            dpos = here - self.start
            dpos[2] = 0
            self.camera_xyz = self.camera_xyz - dpos
            self.updateGL()
        if self.rotatingCamera:
            #here = self.pickPoint(event.x(), event.y())
            #dpos = here - self.start
            #self.camera_look_at = here
            rotX, rotY, rotZ = self.camera_rpy
            startx, starty = self.start_wnd
            
            herex = event.x()
            herey = self._height - event.y()

            dx = (herex - startx) / float(self._width)
            dy = (herey - starty) / float(self._height)
            
            rotX = rotX - dy*10
            rotZ = rotZ + dx*10
            self.camera_rpy = (rotX, rotY, rotZ)
            self.updateGL()
            
    def drawSky(self):
        glDisable (GL_DEPTH_TEST);
        glMatrixMode (GL_MODELVIEW);
        glPushMatrix ();
        glLoadIdentity ();
        glMatrixMode (GL_PROJECTION);
        glPushMatrix ();
        glLoadIdentity ();
        glColor3f (1.0,1.0,1.0);
        glBegin (GL_QUADS);
        glVertex3i (-1, -1, 1);
        glVertex3i (1, -1, 1);
        glVertex3i (1, 1, 1);
        glVertex3i (-1, 1, 1);
        glEnd ();
        glPopMatrix ();
        glMatrixMode (GL_MODELVIEW);
        glPopMatrix ();
        glEnable (GL_DEPTH_TEST);
        #glEnable (GL_COLOR_MATERIAL);
        
    def drawGround(self):
        GROUND_SIZE = 1000
        glColor3f (0.9, 0.9, 0.9);
        glPushAttrib (GL_POLYGON_BIT);
        glEnable (GL_POLYGON_OFFSET_FILL);
        glPolygonOffset (2.0, 2.0);
        
        glDisable(GL_COLOR_MATERIAL);
        glPushMatrix ();
        glTranslatef (0, 0, 0)
        glScalef (GROUND_SIZE, GROUND_SIZE, 1.0);
        glBegin (GL_QUADS);
        glVertex2d ( 1,  1);
        glVertex2d ( 1, -1);
        glVertex2d (-1, -1);
        glVertex2d (-1,  1);
        glEnd ();
        glPopMatrix ();
        glPopAttrib ();

        
    def drawGrid(self):

        grids_per_screen = 10;
        eye_dist = self.camera_xyz[2]
        meters_per_grid = round_to_125 (eye_dist / grids_per_screen);
        num_lines = 300;

        glPushAttrib (GL_DEPTH_BUFFER_BIT | GL_ENABLE_BIT | GL_LINE_BIT);
        glEnable (GL_BLEND);
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glEnable (GL_DEPTH_TEST);


        glPushMatrix();
        glTranslatef (0, 0, 0);
        glColor3f (0.2, 0.2, 0.2);        
        glBegin (GL_LINES);

        for i in range(num_lines):            
            glVertex2f ((-num_lines/2 + i) * meters_per_grid,
                        - num_lines/2 * meters_per_grid)
            glVertex2f ((-num_lines/2 + i) * meters_per_grid,
                        num_lines/2 * meters_per_grid)
            
            glVertex2f (- num_lines/2 * meters_per_grid,
                          (-num_lines/2 + i) * meters_per_grid)
            glVertex2f (num_lines/2 * meters_per_grid,
                        (-num_lines/2 + i) * meters_per_grid)
            
        glEnd ()
        glPopMatrix ();
        glPopAttrib ();

    def selectPlaceOnGroundMode(self):
        self.selectPlaceMode(onTopOf=False)
    def selectPlaceOnObjectMode(self):
        self.selectPlaceMode(onTopOf=True)

    def selectPlaceMode(self, onTopOf):
        self.objectMode = False
        self.placeMode = True
        self.placeOnTopOf = onTopOf
        self.onTopOfObj = None
        self.place_footprint = []
        self.clearSelection()

    def selectObjectMode(self):
        self.objectMode = True
        self.placeMode = False


    def zoomReset(self):
        self.camera_xyz = na.array(self._context.centroid3d) + 20
        if not any([na.isnan(n) for n in self._context.centroid3d]):
            centroid = self._context.centroid3d
        else:

            points = []
            for color, groundings in self._highlighted_groundings.iteritems():
                for g in groundings:
                    if not any ([na.isnan(n) for n in g.centroid3d]):
                        points.append(g.centroid3d)
            centroid = na.mean(points, axis=0)
            print "centroid", centroid
        self.lookAt(centroid)

    def lookAtCentroid(self):
        self.lookAt(self._context.centroid3d)

    def zoomOut(self):
        self.camera_xyz[2] += 1
        self.updateGL()

    def zoomIn(self):
        self.camera_xyz[2] -= 1
        self.updateGL()

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0,  150))
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        if height == 0: height = 1
        
        self._width = width
        self._height = height
        self.updateGL()

    def updateCamera(self):
        glViewport(0, 0, self._width, self._height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self._width / float(self._height)

        GLU.gluPerspective(45.0, aspect, 1, 60)

        
        cx, cy, cz = self.camera_xyz
        rotX, rotY, rotZ = self.camera_rpy
        #print "rotationg", rotX, rotY, rotZ
        #print "moving", cx, cy, cz

        glMatrixMode(GL_MODELVIEW)    
        glLoadIdentity()

        glRotatef(rotX,1.0,0.0,0.0);
        glRotatef(rotY,0.0,1.0,0.0);
        glRotatef(rotZ,0.0,0.0,1.0);
        glTranslatef(-cx, -cy, -cz); 	


    def lookAt(self, vector):
        
        x, y, z = (self.camera_xyz - vector)

        rotX = -degrees(atan2(y, z))
        rotY = 0
        rotZ = 180 + degrees(atan2(x, y)) 
        self.camera_rpy = [rotX, rotY, rotZ]
        self.updateGL()
        
    def paintGL(self):
        self.updateCamera()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.drawSky()
        self.drawGround()
        self.drawGrid()
        
        #self.drawCube()
        drawn_groundings = set()
        for g in self._selected_groundings:
            if not g in drawn_groundings:
                self.drawGrounding(g, color="yellow")
                drawn_groundings.add(g)
        for color, groundings in self._highlighted_groundings.iteritems():
            for g in groundings:
                if not g in drawn_groundings:
                    self.drawGrounding(g, color=color)
                    drawn_groundings.add(g)
        for g in self._context.groundings:
            if not g in drawn_groundings and self.groundingFilter(g):
                self.drawGrounding(g, color="blue")
                drawn_groundings.add(g)


        self.drawActivePlace()
    def drawActivePlace(self):
        if self.placeMode:
            if len(self.place_footprint) <= 2:
                glPushMatrix()
                glColor3f(*color_map["yellow"])
                glBegin(GL_LINES)  
                for (x, y, z) in self.place_footprint:
                    glVertex3f(x, y, z)
                    glVertex3f(x, y, z + self.placeHeight)
                glEnd()
                glPopMatrix()
            else:
                place = self.makePlace()
                self.drawPrism(place.prism, color="yellow")

    def makePlace(self):
        zStart = None
        points_pts = []
        for x, y, z in self.place_footprint:
            if zStart == None:
                zStart = z
            else:
                assert z == zStart, (z, zStart)
            points_pts.append((x, y))
        if zStart == None:
            zStart = 0
        place = Place(Prism.from_points_xy(tp(points_pts), zStart=zStart, zEnd=zStart + self.placeHeight))
        return place

    def drawCube(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslate(0.0, 0.0, -50.0)
        glScale(20.0, 20.0, 20.0)
        glRotate(self.yRotDeg, 0.2, 1.0, 0.3)
        glTranslate(-0.5, -0.5, -0.5)
        glColor3f(1, 1, 1)

        glBegin(GL_LINES);

        glVertex3f(0., 0., 0.);
        glVertex3f(1., 0., 0.);
        glVertex3f(1., 0., 0.);
        glVertex3f(1., 1., 0.);
        glVertex3f(1., 1., 0.);
        glVertex3f(0., 1., 0.);
        glVertex3f(0., 1., 0.);
        glVertex3f(0., 0., 0.);

        glVertex3f(0., 0., 1.);
        glVertex3f(1., 0., 1.);
        glVertex3f(1., 0., 1.);
        glVertex3f(1., 1., 1.);
        glVertex3f(1., 1., 1.);
        glVertex3f(0., 1., 1.);
        glVertex3f(0., 1., 1.);
        glVertex3f(0., 0., 1.);

        glVertex3f(0., 0., 0.);
        glVertex3f(0., 0., 1.);
        glVertex3f(1., 0., 0.);
        glVertex3f(1., 0., 1.);
        glVertex3f(1., 1., 0.);
        glVertex3f(1., 1., 1.);
        glVertex3f(0., 1., 0.);
        glVertex3f(0., 1., 1.);
        glEnd();
        glPopMatrix()
    def spin(self):
        self.yRotDeg = (self.yRotDeg  + 1) % 360.0
        self.parent.statusBar().showMessage('rotation %f' % self.yRotDeg)
        self.updateGL()

    def setContext(self, context, updateGL=True):
        self._context = context
        self.start_t = self._context.start_t
        self.end_t = self._context.end_t
        self._t = self._context.start_t
        #self.zoomReset()
        
        if updateGL:
            self.updateGL()

    @property
    def context(self):
        return self._context


class MainWindow(QtGui.QMainWindow, context3d_ui.Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        if basewindow.batch_mode:
            self.glWidget = None
            return
        self.context = None
        self.glWidget = GLWidget(self)
        self.openglFrame.layout().addWidget(self.glWidget)
        self.connect(self.actionSaveContext,
                     SIGNAL("triggered()"),
                     self.saveContext) 


        self.connect(self.actionClearModes,
                     SIGNAL("triggered()"),
                     self.glWidget.clearModes) 
        self.connect(self.actionLookAtCentroid,
                     SIGNAL("triggered()"),
                     self.glWidget.lookAtCentroid) 

        self.connect(self.actionZoomOut,
                     SIGNAL("triggered()"),
                     self.glWidget.zoomOut) 

        self.connect(self.actionZoomReset,
                     SIGNAL("triggered()"),
                     self.glWidget.zoomReset) 



        self.connect(self.actionZoomIn,
                     SIGNAL("triggered()"),
                     self.glWidget.zoomIn) 

        self.connect(self.actionSelectPlaceOnGround,
                     SIGNAL("triggered()"),
                     self.glWidget.selectPlaceOnGroundMode) 

        self.connect(self.actionSelectPlaceOnObject,
                     SIGNAL("triggered()"),
                     self.glWidget.selectPlaceOnObjectMode) 

        self.connect(self.actionSelectObject,
                     SIGNAL("triggered()"),
                     self.glWidget.selectObjectMode) 
        self.connect(self.timelineSlider,
                     SIGNAL("valueChanged(int)"),
                     self.timeChanged) 

        self.connect(self.groundingFilter,
                     SIGNAL("editingFinished()"),
                     self.filterGroundings)
        self.connect(self.placeOnObjectFilter,
                     SIGNAL("editingFinished()"),
                     self.filterPlaceOnObject)

        self.connect(self.placeHeightEdit,
                     SIGNAL("editingFinished()"),
                     self.setPlaceHeight)




        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(20)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), 
                               self.glWidget.spin)

        self.placeHeightEdit.setText(str(self.glWidget.placeHeight))
        #self.timer.start()
        self.filterPlaceOnObject()

    def filterGroundings(self):
        expr = str(self.groundingFilter.text())
        print "filter", expr
        groundingFilter = eval(expr)
        self.glWidget.setFilter(groundingFilter)

    def saveContext(self):
        fname = QtGui.QFileDialog.getSaveFileName(self, "Context file name")
        with open(fname, "w") as save_file:
            yaml.dump(self.glWidget.context.toYaml(), save_file)
    def filterPlaceOnObject(self):
        expr = str(self.placeOnObjectFilter.text())
        print "filter", expr
        placeOnObjectFilter = eval(expr)
        self.glWidget.placeOnObjectFilter = placeOnObjectFilter


    def setPlaceHeight(self):
        self.glWidget.placeHeight = float(str(self.placeHeightEdit.text()))
        
        
    def timeChanged(self, value):
        if self.glWidget != None:
            f = value / float(self.timelineSlider.maximum() -
                              self.timelineSlider.minimum())
            self.glWidget.setTime(self.glWidget.start_t + 
                                  (self.glWidget.end_t - 
                                   self.glWidget.start_t) * f)



    def setContext(self, context):
        if self.glWidget != None:
            self.glWidget.setContext(context)
        self.context = context

    def selectedGroundings(self):
        if self.glWidget != None:
            return self.glWidget._selected_groundings


    def highlightGroundings(self, groundings, color="green"):
        if self.glWidget != None:
            self.glWidget.highlightGroundings(groundings, color=color)
            self.glWidget.updateGL()
    def selectGroundings(self, groundings):
        if self.glWidget != None:
            self.glWidget.setSelectedGroundings(groundings)


    def clearSelection(self):
        if self.glWidget != None:
            self.glWidget.clearSelection()

def main():
    import basewindow
    app = basewindow.makeApp()
    win = MainWindow()

    obj1 = PhysicalObject(Prism(tp([(0, 0), (1, 0), (1, 1), (0, 1)]), 0, 3),
                          ["tires"],
                          path=Path([0, 1, 2],
                                    tp([(3, 3, 0, 0), (3, 3, 0, math.pi/4), (4, 4, 1, math.pi/4)])))


    obj2 = PhysicalObject(Prism(tp([(2, 2), (3, 2), (3, 3), (2, 3)]), 0, 3),
                          ["boxes"],
                          path=Path([0, 1, 2],
                                    tp([(3, 3, 0, 0), (3, 3, 0, math.pi/4), (4, 4, 1, math.pi/4)])))
    
    obj3 = PhysicalObject(Prism(tp([(5, 5), (10, 5), (10, 10), (5, 10)]), 0, 3),
                          ["truck"])

    
    context = Context([obj1, obj2, obj3], [])
    win.show()
    win.setContext(context)
    sys.exit(app.exec_())
    
        
if __name__ == "__main__":
    main()
