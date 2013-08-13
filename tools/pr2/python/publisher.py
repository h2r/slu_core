import rosbridge
import time

def received(args):
    print "got", args

rb = rosbridge.Rosbridge("localhost", 9090)

rb.subscribe("/object_list", "object_manager/ObjectList", received)
#rb.subscribe("/object_list", "std_msgs/String", received)

while True:
    rb.check()
    time.sleep(0.1)
#rb.publish("/stefie10", "std_msgs/String", 
#           {"data":"pick_up(1)"})  
