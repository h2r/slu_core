import socket
from sys import *
from struct import *
from string import replace
from vicon_utils import *

class point3D:
    def __init__(self, x, y, z, o):
        self.x = x
        self.y = y
        self.z = z
        self.o = o

    def __str__(self):
        return "X:"+ str(self.x)+ " Y:" + str(self.y)+ " Z:" +str(self.z)
    
    def __repr__(self):
        return "X:"+str(self.x)+ " Y:"+ str(self.y)+ "Z:"+ str(self.z)

class hurdle_vicon:
    def __init__(self, tx=None,ty=None,tz=None, ax=None,ay=None,az=None):
        self.AX = tx
        self.AY = ty
        self.AZ = tz
        self.TX = ax
        self.TY = ay
        self.TZ = az

        self.baX = tx
        self.baY = ty
        self.baZ = tz
        self.btX = ax
        self.btY = ay
        self.btZ = az

        self.aX = tx
        self.aY = ty
        self.aZ = tz
        self.tX = ax
        self.tY = ay
        self.tZ = az
        
        self.right_back = point3D(None, None, None, None)
        self.left_back = point3D(None, None, None, None)
        self.center_back = point3D(None, None, None, None)
        self.left_front = point3D(None, None, None, None)
        self.right_front = point3D(None, None, None, None)
        self.center = point3D(None, None, None, None)

    def get_rotation_matrix(self, ax, ay, az):
        M = zeros([3,3])*1.0
        theta = sqrt( ax*ax + ay*ay + az*az );

        if (theta < 1e-15):
            M[0][0] = 1.0; M[1][1] = 1.0; M[2][2] = 1.0;
            M[0][1] = 0.0; M[0][2] = 0.0; M[1][0] = 0.0;
            M[1][2] = 0.0; M[2][0] = 0.0; M[2][1] = 0.0;
        else:
            x = ax/theta;
            y = ay/theta;
            z = az/theta;

            c = cos(theta);
            s = sin(theta);

            M[0][0] = c + (1-c)*x*x;
            M[0][1] =     (1-c)*x*y + s*(-z);
            M[0][2] =     (1-c)*x*z + s*y;
            M[1][0] =     (1-c)*y*x + s*z;
            M[1][1] = c + (1-c)*y*y;
            M[1][2] =     (1-c)*y*z + s*(-x);
            M[2][0] =     (1-c)*z*x + s*(-y);
            M[2][1] =     (1-c)*z*y + s*x;
            M[2][2] = c + (1-c)*z*z;

        return M

    def get_translation_vector(self):
        return [self.TX, self.TY, self.TZ]

    def __str__(self):
        return self.mytostring()+"\n"+str(self.right_back)+"\n"+str(self.left_back) +"\n"+str(self.center_back) +"\n"+str(self.right_front) +"\n"+str(self.left_front) +"\n"+str(self.center) +"\n"


    def __repr__(self):
        return self.mytostring()+"\n"+str(self.right_back)+"\n"+str(self.left_back) +"\n"+str(self.center_back) +"\n"+str(self.right_front) +"\n"+str(self.left_front) +"\n"+str(self.center) +"\n"

    def mytostring(self):
        return "AX:"+str(self.AX)+"AY:" + str(self.AY)+ "AZ:"+ str(self.AZ)+" TX:"+ str(self.TX)+ " TY:"+ str(self.TY)+ " TZ: " + str(self.TZ)

class robot_vicon:
    def __init__(self, tx=None,ty=None,tz=None, ax=None,ay=None,az=None):
        self.AX = None
        self.AY = None
        self.AZ = None
        self.TX = None
        self.TY = None
        self.TZ = None

        self.baX = None
        self.baY = None
        self.baZ = None
        self.btX = None
        self.btY = None
        self.btZ = None

        self.aX = None
        self.aY = None
        self.aZ = None
        self.tX = None
        self.tY = None
        self.tZ = None

    def __str__(self):
        return self.mytostring()

    def __repr__(self):
        return self.mytostring()
    
    def mytostring(self):
        return "AX:"+str(self.AX)+"AY:" + str(self.AY)+ "AZ:"+ str(self.AZ)+" TX:"+ str(self.TX)+ " TY:"+ str(self.TY)+ " TZ: " + str(self.TZ)
    
class Vicon_hurdles:
    def __init__(self, addr):
        self.myvic = Vicon(addr)
        self.curr_info = self.myvic.get_info()
        
    def get_vicon_data(self):
        mydata = self.myvic.get_data()
        if(not len(self.curr_info) == len(mydata)):
            self.curr_info = myvic.get_info()
        
        return self.parse_data(self.curr_info, mydata)


    def parse_data(self, myinfo, mydata):
        ret_hurdles = {"robot":robot_vicon()}

        i = 0;
        for mystr in myinfo:

            if(":" in mystr):
                object_name, object_other = mystr.split(":")
                object_part, object_val = object_other.split(" ")
                object_prop = object_val[1:len(object_val)-1]
                object_prop = replace(object_prop, "-", "")
                

                if(object_name[1:len(object_name)] == "hurdle"):
                    hurdle_num = int(object_name[0])

                    if(object_part.lower() == "object"):
                        try:
                            #add the relevant property here
                            exec("ret_hurdles[hurdle_num]."+object_prop + "= mydata[i]");
                        except:
                            ret_hurdles[hurdle_num]=hurdle_vicon()
                            #add the relevant property here
                            exec("ret_hurdles[hurdle_num]."+object_prop +" = mydata[i]");
                    else:
                        try:
                            #add the relevant property here
                            exec("ret_hurdles[hurdle_num]."+object_part+"."+object_prop[1].lower()+"=mydata[i]");
                        except:
                            ret_hurdles[hurdle_num]=hurdle_vicon()
                            #add the relevant property here
                            exec("ret_hurdles[hurdle_num]."+object_part+"."+object_prop[1].lower()+"=mydata[i]");
                if(object_name == "robot" and object_part.lower() == "object"):
                    exec("ret_hurdles['robot']."+object_prop + "= mydata[i]");
            i+=1
        
        return ret_hurdles
        

def run_vicon(addr):
    print "opening vicon", addr
    myvic = Vicon_hurdles(addr)
    print "getting data"
    data = myvic.get_vicon_data()
    print "got data"
    raw_input("press enter")
    print data["robot"]
    print data[0].mytostring()
    print data[1].mytostring()
    print data[2].mytostring()
    print data[3].mytostring()

if __name__ == "__main__":

    if(len(argv) == 1):
        hostaddr = "128.30.99.206"
        run_vicon(hostaddr)
    elif(len(argv) == 2):
        hostaddr = argv[1]
        run_vicon(hostaddr)
    else:
        print "usage: \n>>python Vicon_utils.py hostaddr"
