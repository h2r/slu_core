

import intervalmap
import math

# Mapping from hue values to color names
g_hue_to_name_imap = intervalmap.IntervalMap()
# -- original colors --
#g_hue_to_name_imap[ 0:7 ] = "red"
#g_hue_to_name_imap[ 340:360 ] = "red"
#g_hue_to_name_imap[ 8:38 ] = "orange"
#g_hue_to_name_imap[ 38:76 ] = "yellow"
#g_hue_to_name_imap[ 76:156 ] = "green"
#g_hue_to_name_imap[ 156:260 ] = "blue"
#g_hue_to_name_imap[ 260:340 ] = "purple"
# -- colors in 4th floor --
g_hue_to_name_imap[ 0:38 ] = "orange"
g_hue_to_name_imap[ 38:76 ] = "yellow"
g_hue_to_name_imap[ 76:216 ] = "green"
g_hue_to_name_imap[ 216:240 ] = "blue"
g_hue_to_name_imap[ 240:300 ] = "purple"
g_hue_to_name_imap[ 300:360 ] = "red"


# list of a*b* and name tuples
g_lab_color_points_ab = [ ( (9.0   , 80.0  , 67.0  ) , "red"    ),
                          ( (66.0  , -86.0 , 83.0  ) , "green"  ),
                          ( (-7.0  , 79.9  , -107.0) , "blue"   ),
                          ( (91.0  , -21.0 , 94.0  ) , "yellow" ),
                          ( (88.0  , -4.0  , 15.0  ) , "yellow" ),
                          ( (78.0  , -12.0 , 91.0  ) , "yellow" ),
                          ( (62.0  , 0.0   , 86.0  ) , "orange" ),
                          ( (17.0  , 98.0  , -60.0 ) , "purple" ),
                          ( (-50.0 , 0.0   , 0.0   ) , "black"  ) ]



# return the index of hte min in list
def min_index( lst, key=lambda x: x ):
    if len(lst) < 1:
        return None
    if len(lst) == 1:
        return 0
    idx = 0
    min_v = lst[0]
    min_v_key = key(min_v)
    for i,v in enumerate(lst):
        k = key(v)
        if k < min_v_key:
            idx = i
            min_v = v
            min_v_key = k
    return idx


# Takes *normalized* rgb values ( from 0.1 ) and 
# returns HSV values ( 0-360, 0-1, 0-1 )
def rgb_to_hsv( nR, nG, nB ):
    m = min(nR,nG,nB)
    M = max(nR,nG,nB)
    H = 0
    S = 0
    if (M!=m):
        f = 0
        if (nR==m):
            f = (nG-nB)
        else:
            if (nG==m):
                f = (nB-nR)
            else:
                f = (nR-nG)
        i = 0
        if (nR==m):
            i = 3
        else:
            if (nG==m):
                i = 5
            else:
                i = 1;
        H = (i-f/(M-m));
        if (H>=6):
            H = H - 6
        H*=60;
        S = (M-m)/M;
    return (H,S,M)


def _cimg_Labf(x):
    if x >= 0.008856:
        return math.pow(x,1/3.0)
    else:
        return 7.787*x+16.0/116
    

def xyz_to_lab( X, Y, Z ):
    Xn = 0.412453 + 0.357580 + 0.180423
    Yn = 0.212671 + 0.715160 + 0.072169
    Zn = 0.019334 + 0.119193 + 0.950227
    XXn = X/Xn
    YYn = Y/Yn
    ZZn = Z/Zn
    fX = _cimg_Labf(XXn)
    fY = _cimg_Labf(YYn)
    fZ = _cimg_Labf(ZZn)
    l = (116.0*Y - 16)
    a = (500.0*(fX - fY))
    b = (200.0*(fY - fZ))
    return (l,a,b)


# Normalized RGB to XYZ
def rgb_to_xyz( nR, nG, nB ):
    R = nR
    G = nG
    B = nB
    x = (0.412453*R + 0.357580*G + 0.180423*B)
    y = (0.212671*R + 0.715160*G + 0.072169*B)
    z = (0.019334*R + 0.119193*G + 0.950227*B)
    return (x,y,z)
    

# Normalized RGB to La*b*
def rgb_to_lab( r, g, b ):
    x,y,z = rgb_to_xyz( r,g,b )
    return xyz_to_lab( x,y,z )



# Normalized RGB to name
def rgb_to_name( r,g,b ):
    
    # first turn to HSV
    h,s,v = rgb_to_hsv( r,g,b )
    
    # check teh saturatio nand value to black and gray
    if s < 0.5:
        if v < 0.5:
            return "black"
        return "gray"
    
    # return name for hue
    return g_hue_to_name_imap[ h ]

# RGB to Name, ignore saturation and value, just look at hue
def rgb_to_name_h( r,g,b ):
    # first turn to HSV
    h,s,v = rgb_to_hsv( r,g,b )
    # return name for hue
    return g_hue_to_name_imap[ h ]


# normalzied RGB to name using L*a*b* space
def rgb_to_name_lab( r, g, b ):
    l,a,b = rgb_to_lab( r,g,b )
    
    # check for black first
    #if l < 0.5 and abs(a) < 5 and abs(b) < 5:
    #    return "black"
    
    # now find closest from set points
    distances = []
    for (ql, qa,qb), name in g_lab_color_points_ab:
        distances.append( math.sqrt( (l-ql)*(l-ql) + (a-qa)*(a-qa) + (b-qb)*(b-qb) ) )
    idx = min_index( distances )
    return g_lab_color_points_ab[idx][1]
    


if __name__ == "__main__":
    import sys
    r = float(sys.argv[1])
    g = float(sys.argv[2])
    b = float(sys.argv[3])
    if r > 1 or g > 1 or b > 1:
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
    print "HSV= " + str( rgb_to_hsv(r,g,b) )
    print "XYZ= " + str( rgb_to_xyz(r,g,b) )
    print "LAB= " + str( rgb_to_lab(r,g,b) ) + "  NAME= " + rgb_to_name_lab(r,g,b)
    print "Name = " + rgb_to_name(r,g,b )


    names_to_rgb = {}
    names_to_rgb_lab = {}
    for r in range(0,255,25):
        for g in range( 0,255,25 ):
            for b in range( 0,255,25 ):
                nr = r / 255.0
                ng = g / 255.0
                nb = b / 255.0
                
                name = rgb_to_name( nr, ng, nb )
                name_lab = rgb_to_name_lab( nr, ng, nb )
                
                if name not in names_to_rgb:
                    names_to_rgb[ name ] = []
                if name_lab not in names_to_rgb_lab:
                    names_to_rgb_lab[ name_lab ] = []
                
                names_to_rgb[ name ].append( (r,g,b) )
                names_to_rgb_lab[ name_lab ].append( (r,g,b) )


    # print out a simple webpage for each
    fout = open( "rgb_names.html", "w" )
    fout.write( "<html><body>\n" )
    for name in names_to_rgb.iterkeys():
        fout.write( "<h2>HSV " + str(name) + "</h2><ul>\n")
        for r,g,b in names_to_rgb[ name ]:
            nr = r/255.0
            ng = g/255.0
            nb = b/255.0
            h,s,v = rgb_to_hsv( nr,ng,nb )
            x,y,z = rgb_to_xyz( nr,ng,nb )
            l,a,bb = rgb_to_lab( nr,ng,nb )
            fout.write( "<li style=\"background-color: rgb(%d,%d,%d)\">" % (r,g,b))
            fout.write( "rgb(%d,%d,%d) hsv(%f,%f,%f) xyz(%f,%f,%f) lab(%f,%f,%f)</li>\n" % ( r, g, b, h, s, v, x, y, z, l, a, bb ) )
        fout.write("</ul>\n<br>\n\n")
    fout.write( "</body></html>\n" )
    fout.close()

    fout = open( "rgb_names_lab.html", "w" )
    fout.write( "<html><body>\n" )
    for name in names_to_rgb_lab.iterkeys():
        fout.write( "<h2>LAB " + str(name) + "</h2><ul>\n")
        for r,g,b in names_to_rgb_lab[ name ]:
            nr = r/255.0
            ng = g/255.0
            nb = b/255.0
            h,s,v = rgb_to_hsv( nr,ng,nb )
            x,y,z = rgb_to_xyz( nr,ng,nb )
            l,a,bb = rgb_to_lab( nr,ng,nb )
            fout.write( "<li style=\"background-color: rgb(%d,%d,%d)\">" % (r,g,b))
            fout.write( "rgb(%d,%d,%d) hsv(%f,%f,%f) xyz(%f,%f,%f) lab(%f,%f,%f)</li>\n" % ( r, g, b, h, s, v, x, y, z, l, a, bb ) )
        fout.write("</ul>\n<br>\n\n")
    fout.write( "</body></html>\n" )
    fout.close()
