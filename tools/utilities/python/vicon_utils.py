import socket
from sys import *
from struct import *
from string import replace


#this is an outdated file that will probably never
# be used again
class Vicon:
    def __init__(self, addr):
        self.addr = addr
        self.s = self.init_vicon(addr)

    def init_vicon(self, addr):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.bind(('', 8025))
        s.connect((addr, 800))

        return s

    def get_info(self):
        #send the request for information
        myreq = pack('ll', 1, 0)
        self.s.send(myreq);
        
        #recieve the data of the possible things to look at
        mystr = self.s.recv(8192)#, socket.MSG_WAITALL)
        size = calcsize('llll')
        mypacket, mytype, cnt, numletters = unpack('llll', mystr[0:size])
        long_size = calcsize('l')
        ret_strs = []
        curr_start = size

        for i in range(cnt):
            if(curr_start+numletters <= len(mystr)):
                str_i = mystr[curr_start:curr_start+numletters]
            else:
                mystr = mystr + self.s.recv(8192)
                str_i = mystr[curr_start:curr_start+numletters]
            
            ret_strs.append(str_i)
            if(i < cnt-1):
                try:
                    numtmp, = unpack('l', mystr[curr_start+numletters:curr_start+numletters+long_size])
                except:
                    mystr = mystr + self.s.recv(8192)
                    numtmp, = unpack('l', mystr[curr_start+numletters:curr_start+numletters+long_size])
                    
                curr_start=curr_start+numletters+long_size
                numletters = numtmp

        return ret_strs

    def get_data(self):
        #send the request for data
        myreq = pack('ll', 2, 0)
        self.s.send(myreq);

        #recieve the data of the possible things to look at
        mydata = self.s.recv(8192)

        #unpack the header
        head_size = calcsize('lll')
        mypacket, mytype, cnt = unpack('lll', mydata[0:head_size])

        ret_vals = []
        double_size = calcsize('d')
        curr_start = head_size
        for i in range(cnt):
            try:
                db, = unpack('d', mydata[curr_start:curr_start+double_size])
            except:
                mydata = mydata + self.s.recv(8192)
                db, = unpack('d', mydata[curr_start:curr_start+double_size])
            ret_vals.append(db)
            curr_start = curr_start+double_size

        return ret_vals

def test_vicon(addr):
    print "getting connection"
    vic = Vicon(addr)
    print "getting info"
    info = vic.get_info()
    print "getting data"
    data = vic.get_data()

    for i in range(len(info)):
        print info[i], data[i]

if __name__ == "__main__":

    if(len(argv) == 1):
        hostaddr = "128.30.99.206"
        test_vicon(hostaddr)
    elif(len(argv) == 2):
        hostaddr = argv[1]
        test_vicon(hostaddr)
    else:
        print "usage: \n>>python Vicon_utils.py hostaddr"
