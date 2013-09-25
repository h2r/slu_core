from PyQt4.QtCore import QObject, SIGNAL

class Capturer(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.figure = None
        self.animPlots = []

    def clearPlots(self):
        for p in self.animPlots:
            print "clear plots", p
            p.remove()
        self.animPlots = []

    def reset(self):
        self.doReset()
        self.clearPlots()
        

    def deactivate(self):
        self.reset()
        if self.figure != None:
            self.figure.canvas.mpl_disconnect(self.cid)
            self.figure = None
    @property
    def axes(self):
        return self.figure.gca()

    @property
    def canvas(self):
        return self.figure.canvas
    def activate(self, figure):
        self.figure = figure
        self.cid = self.figure.canvas.mpl_connect('button_release_event', 
                                                  self.buttonReleaseEvent)

        self.background = self.figure.canvas.copy_from_bbox(self.axes.bbox)        
        self.reset()
        self.draw()

    def doActivate(self, figure):
        raise NotImplementedError()


    def draw(self):
        self.clearPlots()

        plots = self.makePlots()
        self.canvas.restore_region(self.background)

        for plot in plots:
            self.animPlots.append(plot)
            self.axes.draw_artist(plot)


        self.figure.canvas.blit(self.axes.bbox)


        
class PointCapturer(Capturer):
    def __init__(self):
        Capturer.__init__(self)
        self.name = "Point"


    def doReset(self):
        self.point = None


    def buttonReleaseEvent(self, event):
        if event.button == 1:
            loc = event.xdata, event.ydata
            self.point = loc
            self.emit(SIGNAL("completedPoint"), (self.point))



    def makePlots(self):
        if self.point != None:
            x,y = self.point
            plot, = self.axes.plot([x], [y], 'ro-', animated=True, 
                                   scalex=False, scaley=False)
            return [plot]
        else:
            return []
        


class PolygonCapturer(Capturer):

    def __init__(self):
        Capturer.__init__(self)
        self.name = "polygon"

    def doReset(self):
        self.polygon = []


    def buttonReleaseEvent(self, event):
        loc = event.xdata, event.ydata
        self.polygon.append(loc)
        self.draw()
        print "button", event.button
        if event.button == 3 and len(self.polygon) != 0:
            self.emit(SIGNAL("completedPolygon"), (self.polygon))
            self.reset()



    def makePlots(self):
        print "polygon", self.polygon, self.polygon.__class__
        print self.polygon
        if len(self.polygon) != 0:
            X = [x for x, y in self.polygon]
            Y = [y for x, y in self.polygon]
            X.append(X[0])
            Y.append(Y[0])
            plot, = self.axes.plot(X, Y, 'ro-', animated=True, 
                                   scalex=False, scaley=False)
            plots = [plot]
        else:
            plots = []
        return plots

            


class PointOrientationCapturer(Capturer):

    def doReset(self):
        self.p1 = None
        self.p2 = None
        
        print "poc reset"

    def buttonReleaseEvent(self, event):
        if event.button == 1:
            loc = event.xdata, event.ydata
            if self.p1 == None:
                self.p1 = loc
                self.draw()                
            elif self.p2 == None:
                self.p2 = loc
                print "poc emit"
                self.draw()                
                self.emit(SIGNAL("completedPoint"), (self.p1, self.p2))
                


    def makePlots(self):
        print "poc plot"
        if self.p1 != None and self.p2 != None:
            x1,y1 = self.p1
            x2, y2 = self.p2
            plot, = self.axes.plot([x1, x2], [y1, y2], 'ro-', animated=True, 
                                   scalex=False, scaley=False)
            return [plot]
        
        elif self.p1 != None:
            x,y = self.p1
            plot, = self.axes.plot([x], [y], 'ro-', animated=True, 
                                   scalex=False, scaley=False)
            return [plot]
        
        else:

            return []
        


class PathCapturer(Capturer):

    def __init__(self):
        Capturer.__init__(self)
        self.name = "path"

    def doReset(self):
        self.points = []


    def buttonReleaseEvent(self, event):
        loc = event.xdata, event.ydata
        self.points.append(loc)
        self.draw()
        print "button", event.button
        if event.button == 3 and len(self.points) != 0:
            self.emit(SIGNAL("completedPoint"), (self.points))
            self.reset()



    def makePlots(self):
        if len(self.points) != 0:
            X = [x for x, y in self.points]
            Y = [y for x, y in self.points]
            plot, = self.axes.plot(X, Y, 'ro-', animated=True, 
                                   scalex=False, scaley=False)
            plots = [plot]
        else:
            plots = []
        return plots
