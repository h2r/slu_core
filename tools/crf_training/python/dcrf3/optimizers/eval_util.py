import os
from pyTklib import kNN_index

def get_region_to_topo(gtruth_tagfile, dests):
    gtf = gtruth_tagfile
    
    #see which destinations are contained in a region
    r_to_dest = {}
    for i in range(len(dests[0])):
        d = dests[:,i]
        
        #print "d", d
        ps = gtf.get_contained_polygons(d)
        
        #get the hash
        for p in ps:
            if(r_to_dest.has_key(p.tag)):
                r_to_dest[p.tag].append(d)
            else:
                r_to_dest[p.tag]= [d]
    
    #get the nearest region in case no destinations are contained
    # in the region
    for tag in gtf.get_tag_names():
        if(not r_to_dest.has_key(tag)):
            XY = gtf.get_tag_locations(tag)
            i, = kNN_index([XY[0][0], XY[1][0]], dests, 1)
            r_to_dest[tag]=[dests[:,i]]
    
    return r_to_dest
        

def get_output_filename(dirname, dg_model=None):
    if(dg_model != None):
        basefn = str(dg_model.__class__).split('.')[-2]+".output"
    else:
        basefn="output"

    i = 0
    myfn = "%s/%s_%d.pck" % (dirname, basefn, i)
    while(os.path.exists(myfn)):
        i += 1
        myfn = "%s/%s_%d.pck" % (dirname, basefn, i)
    
    return myfn
