from pyDog import *
from carmen_util import *

class littledog_logfile:
    def __init__(self, filename):
        self.las, self.cob, self.flul, self.flll, self.frul, self.frll, self.rlul, self.rlll, self.rrul, self.rrll, self.imu, self.ft, self.enc_mocap, self.enc_body  = load_logfile_new(filename)
        self.robot = LittleDog().__disown__()

        #if you want to see what's there, this is the way to do it
        #ld   = pyLittledog.littledog_message_subscribe(self.robot)
	#hk   = pyLittledog.hokuyo_message_subscribe(self.robot)
        
        self.mocap_index = 0
        self.laser_index = 0

        #initialize the indices
        #find the initial pose when we start taking readings
        print "laser", self.las[0].timestamp
        print "cob", self.cob[0].timestamp

        
        while(self.cob[self.mocap_index].timestamp <= self.las[self.laser_index].timestamp):
            self.mocap_index+=1
        if(self.mocap_index > 0):
            self.mocap_index=self.mocap_index-1

        
    def get_next_reading_by_laser(self):
        #for reading in self.las:
        self.laser_index+=1
        if(len(self.las) <= self.laser_index):
            return None
        
        print "*********"
        print self.las[self.laser_index].timestamp
        print self.cob[self.mocap_index].timestamp
        
        while(self.las[self.laser_index].timestamp > self.cob[self.mocap_index].timestamp):
            print "in loop", self.mocap_index
            self.mocap_index+=1

        retval = [self.las[self.laser_index], self.cob[self.mocap_index], self.flul[self.mocap_index], self.flll[self.mocap_index],
                  self.frul[self.mocap_index], self.frll[self.mocap_index],self.rlul[self.mocap_index], self.rlll[self.mocap_index],
                  self.rrul[self.mocap_index], self.rrll[self.mocap_index],self.imu[self.mocap_index], self.ft[self.mocap_index],
                  self.enc_mocap[self.mocap_index], self.enc_body[self.mocap_index]]
        
        return retval

    def publish_next_reading(self):
        body, flul, flll, frul, frll, rlul, rlll, rrul, rrll, imu, feet, enc_mocap, enc_body  = self.get_current_readings()
        
	self.robot.publish_littledog_message(body, flul, flll, frul, frll, rlul, rlll, rrul, rrll,
                                             enc_mocap, enc_body, imu.get_ypr(), imu.get_rates_xyz(), imu.get_acc_xyz(), feet,
                                             0, 0, 0, 0, imu.dog_ts, imu.timestamp, enc_body.stepleg, "nicksgroup")
        #increment the index for mocap
        self.mocap_index += 1

        #if the new incremented timestamp is larger than the lazer's then publish the laser
        #as well
        
        if(self.cob[self.mocap_index].timestamp > self.las[self.laser_index].timestamp):
            print "laser", self.laser_index
            
            las = self.get_current_laser()
            self.robot.publish_littledog_hokuyo_message(las.data)
            self.laser_index += 1


    def get_current_readings(self):
        retval = [self.cob[self.mocap_index], self.flul[self.mocap_index], self.flll[self.mocap_index],
                  self.frul[self.mocap_index], self.frll[self.mocap_index],self.rlul[self.mocap_index], self.rlll[self.mocap_index],
                  self.rrul[self.mocap_index], self.rrll[self.mocap_index],self.imu[self.mocap_index], self.ft[self.mocap_index],
                  self.enc_mocap[self.mocap_index], self.enc_body[self.mocap_index]]

        return retval

    def get_current_laser(self):
        return self.las[self.laser_index]

    def publish_current_readings(self):
        #laser, imu and mocap are independent and need to be matched to the closest time
        body, flul, flll, frul, frll, rlul, rlll, rrul, rrll, imu, feet, enc_mocap, enc_body  = self.get_current_readings()

	self.robot.publish_littledog_message(body, flul, flll, frul, frll, rlul, rlll, rrul, rrll,
                                             enc_mocap, enc_body, imu.get_ypr(), imu.get_rates_xyz(), imu.get_acc_xyz(), feet,
                                             0, 0, 0, 0, imu.dog_ts, imu.timestamp, enc_body.stepleg, "nicksgroup")

        las = self.get_current_laser()
        self.robot.publish_littledog_hokuyo_message(las.data)

