
def load_mrf_file(filename):

    myfile = open(filename, 'r')
    myhash = {}
    
    for line in myfile:
        splline = line.split(" ")

        imnum = int(splline[0])
        type = splline[2]
        prob = float(splline[4])
        try:
            myhash[type][imnum] = prob
        except(KeyError):
            myhash[type] = {}
            myhash[type][imnum] = prob            

    return myhash

def load_mrf_output(mrf_filename, class_name):

    myfile = open(mrf_filename, 'r')

    locs = {}
    for line in myfile:
        splline = line.split(" ")
        print splline
        ind = int(splline[1])
        mytype = splline[3]
        prob = float(splline[5])
        exists = int(splline[8])
        
        locs[ind] = {'type':mytype, 'prob':prob, 'exists':exists}

    return locs
        

def load_pclassfile(pclass_filename):
    myfile = open(pclass_filename, 'r')
    
    myhash = {}
    myhash_joint = {}
    myconfig = {}
    cnt = 0
    for myline in myfile:
        config = myline.split(" ");
        
        #print myline
        #threshold 0.82 tp 0.99 fp 0.01 tn 0.87 fn 0.13 
        if(len(config) == 12 and cnt == 0):
            myconfig["name"] = config[1]
            myconfig["thresh"] = float(config[3])
            myconfig["tp"] = float(config[5])
            myconfig["fp"] = float(config[7])
            myconfig["tn"] = float(config[9])
            myconfig["fn"] = float(config[11])
            #print "loading config"
            print myconfig
            #raw_input()
            cnt += 1
            continue
        
        if(config[0] != "image"):
            continue

        splline = myline.split("/")

        #print splline[0]
        filenum = int(splline[0].split(" ")[1].replace(":", ""))
        joint_prob = float(splline[0].split(" ")[3])

        myhash_joint[filenum] = joint_prob
        for i in range(1, len(splline)):
            window = splline[i].strip()
            if(window == ""):
                try:
                    a = myhash[filenum]
                except(KeyError):
                    myhash[filenum] = []
            else:
                #print "adding detections"
                #raw_input()
                #print window
                wspl = window.split(" ")
                
                size_width = float(wspl[6])
                size_height = float(wspl[7])
                prob_im = float(wspl[9])
                prob_c1 = float(wspl[11])
                prob_c2 = float(wspl[13])
                prob_c3 = float(wspl[15])
                prob_fin = float(wspl[17])

                height = None; disparity = None;
                if(len(wspl) >= 22):
                    height = float(wspl[21])
                    disparity = float(wspl[23])
                

                try:
                    myhash[filenum].append({"prob_im":prob_im, 
                                            "prob_c1":prob_c1, 
                                            "prob_c2":prob_c2, 
                                            "prob_c3":prob_c3, 
                                            "prob_fin":prob_fin, 
                                            "size_width":size_width, 
                                            "size_height":size_height,
                                            "height":height, 
                                            "disparity":disparity})
                except(KeyError):
                    myhash[filenum] = []
                    myhash[filenum].append({"prob_im":prob_im, 
                                            "prob_c1":prob_c1, 
                                            "prob_c2":prob_c2, 
                                            "prob_c3":prob_c3, 
                                            "prob_fin":prob_fin,
                                            "size_width":size_width, 
                                            "size_height":size_height,
                                            "height":height,
                                            "disparity":disparity})
        cnt += 1
        #print myhash[filenum]
        #raw_input()
    return myhash, myhash_joint, myconfig


def copy_and_save_pclassfile(pclass_filename_orig, 
                             pclass_filename_dest, myhash):
    myfile = open(pclass_filename_orig, 'r')
    myoutfile = open(pclass_filename_dest, 'w')
    
    for myline in myfile:
        config = myline.split(" ");
        
        if(config[0] != "image"):
            myoutfile.write(myline)
            continue

        splline = myline.split("/")
        myoutfile.write(splline[0])
        

        filenum = int(splline[0].split(" ")[1].replace(":", ""))

        #myhash_joint[filenum] = joint_prob
        windownum = 0
        for i in range(1, len(splline)):
            window = splline[i].strip()
            if(window == ""):
                continue
            else:
                myoutfile.write(" / ")
                wspl = window.split(" ")
                
                #size_width = float(wspl[6])
                #size_height = float(wspl[7])
                #prob_im = float(wspl[9])
                wspl[11] = str(myhash[filenum][windownum]['prob_c1'])
                wspl[13] = str(myhash[filenum][windownum]['prob_c2'])
                wspl[15] = str(myhash[filenum][windownum]['prob_c3'])

                p1 = myhash[filenum][windownum]['prob_c1']
                p2 = myhash[filenum][windownum]['prob_c2']
                p3 = myhash[filenum][windownum]['prob_c3']
                wspl[17] = str(p1*p2*p3*myhash[filenum][windownum]['prob_im'])
                windownum+=1

                for elt in wspl:
                    myoutfile.write(elt + " ")

        myoutfile.write("\n")

def load_fz(filename):

    myfile = open(filename, 'r')
    
    myhash = {}
    for myline in myfile:
        if(len(myline) == 0):
            continue

        filenum = int(myline.split(' ')[0].split(".")[0])
        splline = myline.split(';')
        
        myhash[filenum] = []

        #if there is nothing detected 
        if(int(myline.split(' ')[1]) == 0):
            continue

        detection_vals = splline[59].split(',')
        
        for elt in detection_vals:
            if(not elt == ''):
                myhash[filenum].append({"prob_im":float(elt)})
                #print float(elt)


    return myhash


def load_groundtruth(gtruth_filename):
    myfile = open(gtruth_filename, 'r')

    myhash = {}
    for myline in myfile:
        splline = myline.split(",")
        imnum = int(splline[0].split(".")[0])

        mytags = []
        for elt in splline[1:]:
            mytags.append(elt.strip())
        
        myhash[imnum] = mytags
        #print "key/val", splline[0], imnum, myhash[imnum]

    return myhash


def load_groundtruth_str(gtruth_filename):
    myfile = open(gtruth_filename, 'r')

    myhash = {}
    for myline in myfile:
        splline = myline.split(",")
        #imnum = int(splline[0].split(".")[0])
        imname = splline[0]

        mytags = []
        for elt in splline[1:]:
            mytags.append(elt.strip())
        
        myhash[imname] = mytags
        #print "key/val", splline[0], imnum, myhash[imnum]

    return myhash


