from pylab import amin, cm, imshow, transpose, sign, array, gray
from carmen_gridmap import carmen_util_read_gridmap
from matplotlib import colors

def carmen_read_map(filename):
    return carmen_util_read_gridmap(filename)


def carmen_cmap_gray():

    'set the default colormap to carmen and apply to current image if any. See help(colormaps).'
    
    lower = 0.8
    upper = 1.0
    
    _carmen_data = {'red':   ((0., lower, upper),
                              (0.5, lower, upper), 
                              (0.75, lower, upper),
                              (1.0, lower, upper)),
                    'green': ((0., lower, upper),
                              (0.5, lower, upper),
                              (0.75, lower, upper), 
                              (1.0, lower, upper)),
                    'blue':  ((0., lower, upper),
                              (0.5, lower, upper),
                              (0.75, lower, upper), 
                              (1.0, lower, upper))}



    carmen_cmap = colors.LinearSegmentedColormap('carmen', _carmen_data, cm.LUTSIZE)
    '''cm.datad['carmen']=_carmen_data
    rc('image', cmap='carmen');

    im=gci()

    if im is not None:
        im.set_cmap(carmen_cmap)
        pass
    draw_if_interactive()'''
    return carmen_cmap



def carmen_cmap_white():
    'set the default colormap to carmen and apply to current image if any. See help(colormaps).'
    
    lower = 0.75
    upper = 1.0
    
    _carmen_data = {'red':   ((0., lower, upper),
                              (0.5, lower, upper), 
                              (0.75, lower, upper),
                              (1.0, lower, upper)),
                    'green': ((0., lower, upper),
                              (0.5, lower, upper),
                              (0.75, lower, upper), 
                              (1.0, lower, upper)),
                    'blue':  ((0., lower, upper),
                              (0.5, lower, upper),
                              (0.75, lower, upper), 
                              (1.0, lower, upper))}



    carmen_cmap = colors.LinearSegmentedColormap('carmen', _carmen_data, cm.LUTSIZE)
    '''cm.datad['carmen']=_carmen_data
    rc('image', cmap='carmen');
    im=gci()

    if im is not None:
        im.set_cmap(carmen_cmap)
    draw_if_interactive()'''
    
    return carmen_cmap



def carmen_cmap_grey():
    print "****makingcmap\n\n"
    'set the default colormap to carmen and apply to current image if any. See help(colormaps).'

    _carmen_data = {'red':   ((0., 0., 1.0),(0.3, 0.2, 1.0), (0.45, 0.2, 1.0),(1.0, 0.2, 1.0)),
                    'green': ((0., 0., 1.0),(0.3, 0.2, 1.0),(0.45, 0.2, 1.0), (1.0, 0.2, 1.0)),
                    'blue':  ((0., 0., 1.0),(0.3, 0.2, 1.0),(0.45, 0.2, 1.0), (1.0, 0.2, 1.0))}

    carmen_cmap = colors.LinearSegmentedColormap('carmen', _carmen_data, cm.LUTSIZE)
    '''cm.datad['carmen']=_carmen_data
    rc('image', cmap='carmen');
    im=gci()
    
    if im is not None:
        im.set_cmap(carmen_cmap)
    draw_if_interactive()'''

    return carmen_cmap

def carmen_cmap(set_rc=True):
    'set the default colormap to carmen and apply to current image if any. See help(colormaps).'

    _carmen_data = {'red':   ((0., 0., 0.),(0.5, 0.0, 1.0), (0.75, 0.0, 1.0),(1.0, 0.0, 1.0)),
                    'green': ((0., 0., 0.),(0.5, 0.0, 1.0),(0.75, 0.0, 1.0), (1.0, 0.0, 1.0)),
                    'blue':  ((0., 0., 1.0),(0.5, 0.0, 1.0),(0.75, 0.0, 1.0), (1.0, 0.0, 1.0))}

    carmen_cmap = colors.LinearSegmentedColormap('carmen', _carmen_data, cm.LUTSIZE)
    '''cm.datad['carmen']=_carmen_data
    if set_rc:
        rc('image', cmap='carmen');
    im=gci()
    
    if im is not None:
        im.set_cmap(carmen_cmap)
    draw_if_interactive()'''
    
    return carmen_cmap

def plot_tklib_log_gridmap(gridmap, curraxis=None, curr_plt=None, cmap=None, subplt=None, set_rc=True):
    print "initial curr_plt", curr_plt
    matrix = gridmap.to_probability_map_carmen()
    plot_map(matrix, gridmap.x_size, gridmap.y_size,
             gridmap.x_offset, gridmap.y_offset, gridmap.theta_offset,
             cmap, curraxis, curr_plt, subplt, set_rc=set_rc)

def plot_map(themap, x_size, y_size, x_offset=0, y_offset=0, theta_offset=0,
             cmap=None, curraxis=None, curr_plt=None, subplt=None, set_rc=True):
    ret_plt = None
    if(amin(themap)>=0.0):
        themap[0][0]=-1.0
    
    extent= [0 + x_offset, x_size + x_offset,
             0 + y_offset, y_size + y_offset]

    if(cmap == "binary"):
        print "binary"
        mypltmap = sign(themap)
        gray()
        return imshow(transpose(mypltmap), origin=1, extent=extent)

    mycmap = None
    if(cmap == None):
        print "doing cmap"
        mycmap = carmen_cmap(set_rc=set_rc)
    else:
        #mycmap = carmen_cmap_gray()
        #print "colormap:", cmap
        #
        mycmap = eval(cmap+"()")


    print "--------------------------"
    print curr_plt
    if(curr_plt != None):
        print "setting data"
        curr_plt.set_data(transpose(themap))
    if(subplt != None):
        print "showing image"
        ret_plt = subplt.imshow(transpose(themap), origin=1, extent=extent, cmap=mycmap)
    else:
        print "plotting", extent
        ret_plt = imshow(transpose(themap), origin=1, extent=extent, cmap=mycmap)

    print "---------------------------"
    return ret_plt

#def update_map(myid, data, myfig, myaxis):
#    myid.set_data(data)

if __name__=="__main__":
    #themap = carmen_read_map("/home/tkollar/installs/carmen/data/nsh_level_3.map")
    themap = carmen_read_map("/home/tkollar/local/tklib/tools/trajopt/data/maps/hurdles.cmf.gz")

    themap["map"] = array(themap["map"])
    themap["map"][0,0]=-1.0

    resolution = themap["resolution"]
    plot_map(themap["map"], themap["x_size"]*resolution, themap["y_size"]*resolution)

