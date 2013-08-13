import unittest
from quaternion import Quaternion
from assert_utils import assert_array_equal as aeq
import math

class TestCase(unittest.TestCase):
    def testIdentity(self):
        quat = Quaternion.from_roll_pitch_yaw(0, 0, 0)

        vector = [0, 0, 1]

        vector2 = quat.rotate(vector)
        aeq(vector, vector2)

    def testQuaternion(self):
        vector = [1, 1, 1]
        quat = Quaternion.from_roll_pitch_yaw(math.pi/2, 0, 0)
        vector2 = quat.rotate(vector)
        aeq(vector2, [1, -1, 1])
        aeq(vector, quat.conjugate.rotate(quat.rotate(vector)))


        vector2 = Quaternion.from_roll_pitch_yaw(0, math.pi/2, 0).rotate(vector)
        aeq(vector2, [1, 1, -1])


        vector2 = Quaternion.from_roll_pitch_yaw(math.pi/2, 0, 0).rotate(vector)
        aeq(vector2, [1, -1, 1])

        
    def testAxisAngle(self):
        vector = [1, 1, 1]
        quat = Quaternion.from_axis_angle(math.pi/2, 0, 0)
        vector2 = quat.rotate(vector)

        aeq(vector2, [1, -1, 1])

        vector2 = Quaternion.from_axis_angle(0, math.pi/2, 0).rotate(vector)
        aeq(vector2, [1, 1, -1])


        vector2 = Quaternion.from_axis_angle(math.pi/2, 0, 0).rotate(vector)
        aeq(vector2, [1, -1, 1])

        
        print "leg0"
        quat = Quaternion.from_axis_angle(0.3, 1.56, -0.38)
        print "rpy", [math.degrees(x) for x in quat.to_roll_pitch_yaw()]
        aeq(quat.rotate([1, 0, 0]), [-0.02672053, -0.0458008,  -0.99859316])


        print "leg1"
        quat = Quaternion.from_axis_angle(1.6, 0.95, -1.6)
        print "rpy", [math.degrees(x) for x in quat.to_roll_pitch_yaw()]
        aeq(quat.rotate([1, 0, 0]), [-0.01924605,  0.03368216, -0.99924727])

        print "leg2"
        quat = Quaternion.from_axis_angle(2.48, -0.74, -2.38)
        print "rpy", [math.degrees(x) for x in quat.to_roll_pitch_yaw()]
        aeq(quat.rotate([1, 0, 0]), [0.02983124, -0.03904517, -0.99879206])

        

