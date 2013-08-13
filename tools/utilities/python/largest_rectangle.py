from scipy import *
from pylab import *
from datatypes import *
from carmen_util import *


from scipy import *
from pylab import *
from datatypes import *
from carmen_util import *
from heapq import heappush, heappop, heapify


class heap_point(point):
    def __cmp__(self, other_pt):
        if(self.y < other_pt.y):
            return -1
        elif(self.y > other_pt.y):
            return 1
        else:
            return 0

def get_largest_rectangle(range_reading):
    range_pts = range_to_heap_points(range_reading)

    heap = []
    for pt in range_pts:
        heappush(heap, pt)

    max_x_extent = 0
    max_y_extent = 0
    max_area = 0

    #initial conditions
    first_pt = heappop(heap)
    
    while(len(heap) > 0):
        tmp_x_extent = abs(first_pt.x)
        
        while(len(heap)> 0 and abs(first_pt.x) >= tmp_x_extent):
            first_pt = heappop(heap)

        tmp_y_extent = abs(first_pt.y)

        if(tmp_x_extent*tmp_y_extent>max_area):
            max_x_extent = tmp_x_extent
            max_y_extent = tmp_y_extent
            max_area = tmp_x_extent*tmp_y_extent

    return max_x_extent, max_y_extent


def range_to_x_y(range_reading):
    X, Y = [], []
    for i in range(len(range_reading)):
        angle = i*math.pi/180.0
        X.append(range_reading[i]*cos(angle))
        Y.append(range_reading[i]*sin(angle))
        
    return X, Y

def range_to_heap_points(range_reading):
    pts = []
    for i in range(len(range_reading)):
        angle = i*math.pi/180.0
        pts.append(heap_point(range_reading[i]*cos(angle),range_reading[i]*sin(angle)))
        
    return pts



if(__name__ == "__main__"):

    odometry, laser_readings = load_logfile("/afs/csail.mit.edu/u/t/tkollar/installs/carmen/data/edmonton.log")

    ion()
    laser_pts_plt, = plot([],[])
    xy_extents_plt, = plot([], [])
    axis([-20, 20, -1, 20])
    for reading in laser_readings:
        X, Y = range_to_x_y(reading.data)
        #print X, Y
        laser_pts_plt.set_data(X,Y)


        pts = range_to_heap_points(reading.data)
        x_extent, y_extent = get_largest_rectangle(reading.data)

        xy_extents_plt.set_data([-x_extent, -x_extent, x_extent, x_extent, -x_extent],
                                [0, y_extent, y_extent, 0, 0]);
        
        draw()

