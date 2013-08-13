import Image
from sys import argv
from glob import glob
from scipy import array, transpose, argmin
from pyTklib import kNN_index, tklib_normalize_theta_array
from carmen_util import load_carmen_logfile
from pylab import imread
from scipy import absolute
from math import pi
from shutil import copy

class logfile_du:
    def __init__(self, log_scanmatch_fn, image_dir):
        
        self.log_fn = log_scanmatch_fn
        self.image_dir = image_dir

        self.times = None
        self.times_index = None
        
        self.load()

    def load(self):
        self.load_images()
        self.load_logfile()
        
        self.times = set()
        for ts in self.timestamp_to_image.keys():
            self.times.add(ts)
        for ts in self.timestamp_to_fread.keys():
            self.times.add(ts)
        for ts in self.timestamp_to_odom.keys():
            self.times.add(ts)
        
        self.times = list(self.times)
        self.times.sort()
        self.times = array(self.times)

        #get freadings XY representation
        t_to_f = self.timestamp_to_fread
        self.freadings_XY = transpose([[t_to_f[i].location.x, t_to_f[i].location.y] 
                                       for i in sorted(self.timestamp_to_fread.keys())])

        self.freadings_Th = transpose([t_to_f[i].location.theta
                                       for i in sorted(self.timestamp_to_fread.keys())])
        
        
    def load_images(self):
        myfiles = glob(self.image_dir+"/*.txt")

        self.timestamp_to_image = {}
        
        for f in myfiles:
            image_num = f.split("/")[-1].split(".")[0]
            
            myfile = open(f, 'r')
            ts = int(myfile.readline().split(":")[-1])/10e5
            self.timestamp_to_image[ts] = image_num

    def load_logfile(self):
        readings = load_carmen_logfile(self.log_fn)
        freadings, rreadings, t_pos, o_readings = readings

        self.timestamp_to_fread = {}
        for r in freadings:
            self.timestamp_to_fread[r.timestamp] = r

        self.timestamp_to_odom = {}
        for r in o_readings:
            self.timestamp_to_odom[r.timestamp] = r


    def set_timestamp(self, ts=None):
        if(ts == None):
            i = 0
        else:
            i = argmin(abs(self.times -ts))

        self.times_index = i

    def next_reading(self):
        if(self.times_index == None):
            self.set_timestamp()
        
        #print self.times_index
        #raw_input()

        self.times_index += 1
        
        ret_vals = []; ret_types = [];
        
        if(self.timestamp_to_fread.has_key(self.times[self.times_index])):
            ret_vals.append(self.timestamp_to_fread[self.times[self.times_index]])
            ret_types.append("front_reading")

        if(self.timestamp_to_odom.has_key(self.times[self.times_index])):
            ret_vals.append(self.timestamp_to_odom[self.times[self.times_index]])
            ret_types.append("odom")

        if(self.timestamp_to_image.has_key(self.times[self.times_index])):
            ret_vals.append(self.timestamp_to_image[self.times[self.times_index]])
            ret_types.append("image")

        return ret_vals, ret_types

    
    def get_image(self, image_str):
        #im = Image.open(self.image_dir+"/"+image_str+".jpg")
        return imread(self.image_dir+"/"+image_str+".jpg")

    def save_image(self, from_image_str, to_image_path):
        #im = Image.open(self.image_dir+"/"+image_str+".jpg")
        #return imread(self.image_dir+"/"+image_str+".jpg")
        return copy(self.image_dir+"/"+from_image_str+".jpg", to_image_path)

    def get_readings(self, pose):
        I, = (absolute(tklib_normalize_theta_array(self.freadings_Th-pose[2])) < pi/3.0).nonzero();
        freadings_tmp = self.freadings_XY[:,I]
        
        myi, = kNN_index(pose[0:2], freadings_tmp, 1)
        i = I[myi]
        #i = I[i_theta]
        
        ts = sorted(self.timestamp_to_fread.keys())[int(i)]

        fread = self.timestamp_to_fread[ts]
        image = None
        odom = None

        self.set_timestamp(ts)

        #get the readings
        done = False; seen_im = False; seen_odom=False
        if(len(self.timestamp_to_odom) == 0):
            seen_odom=True

        while(not done):
            if(seen_im and seen_odom):
                done = True

            vals, types = self.next_reading()

            if(types[0] == "image"):
                image = vals[0]
                seen_im = True
            elif(types[0] == "odom"):
                odom = vals[0]
                seen_odom = True
        
        return fread, image, odom

        


