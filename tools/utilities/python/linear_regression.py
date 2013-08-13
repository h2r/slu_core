from rpy import r
from datatypes import *

#x1 and y1 are lists of x and y points
def fit_line(x1, y1):
    myline = None

    if(len(x1)==2):
        tmp_line = line(0,0)
        myline = tmp_line.get_line_from_points(point(x1[0],y1[0],0), point(x1[1], y1[1],0))
    elif(len(x1) > 2):
        retHash = r.lsfit(x1,y1)['coefficients']
        slope1 = retHash['X']
        intercept1 = retHash['Intercept']
        
        #slope1, intercept1, = stats.linregress(x1,y1)[0:2]
        myline = line(slope1, intercept1)

    return myline
