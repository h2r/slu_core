import pyTklib

class tklib_ipc_handler(pyTklib.pyTklibHandler):
    
    def __init__(self):
        pyTklib.carmen_ipc_initialize(1, ["python"])
        pyTklib.carmen_publish_define_messages()
        pyTklib.pyTklibHandler.__init__(self)
        
    def run_cb(self, my_type, msg_functor):
        #print my_type
        msg = eval("self."+msg_functor)
        self.callback(my_type, msg)

    def set_destinations(self, dests):
        pyTklib.carmen_publish_trajopt_set_destinations_message(dests);

    def callback(self, the_type, msg):
        print the_type
        
        if(the_type == "ekf_message"):
            print msg.keys()
            print msg["timestamp"]
            print msg["host_name"]
            print msg["mean"]
            print msg["cov"]
        elif(the_type == "gridmapping_pose_message"):
            print "x", msg.x, " y", msg.y, " theta", msg.theta
            print "ts:", msg.timestamp, "host", msg.host
        elif(the_type == "trajopt_go_message"):
            print "ts:", msg.timestamp, " host:", msg.host
        elif(the_type == "trajopt_stop_message"):
            print "ts:", msg.timestamp, " host:", msg.host
        elif(the_type == "trajopt_config_message"):
            print "dests:", msg.num_destinations, " ts:", msg.timestamp, " host:", msg.host
        elif(the_type == "trajopt_destinations_message"):
            print "dests", msg
        elif(the_type == "spline_free_request"):
            print "*****************"
            print "magnitude", msg.get_start_magnitude(), msg.get_end_magnitude()
            print "get_start_pose", msg.get_start_pose()
            print "get_end_pose", msg.get_end_pose()
        elif(the_type == "curr_spline"):
            print "*****************"
            print "magnitude", msg.get_start_magnitude(), msg.get_end_magnitude()
            print "get_start_pose", msg.get_start_pose()
            print "get_end_pose", msg.get_end_pose()


 
    def __del__(self):
        pyTklib.pyTklibHandler.__del__(self)


