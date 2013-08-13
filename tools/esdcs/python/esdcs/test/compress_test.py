import unittest
from esdcs.dataStructures import ExtendedSdc, _getEntireText, ExtendedSdcGroup
from esdcs import dataStructures
from esdcs import groundings
from numpy import array
from assert_utils import assert_array_equal as aeq

class TestCase(unittest.TestCase):

    def testCompress1(self):
        timestamps =  array([ 1.,  2.])
        points =  array([[ 10.5,  10.5],
                         [ 50.5,  50.5],
                         [  0. ,   0.1],
                         [  0. ,   0. ]])
        
        t1, p1 = groundings.compressP(timestamps, points)
        t2, p2 = groundings.compressC(timestamps, points)
        aeq(t1, t2)
        aeq(p1, p2)
        
    def testCompress(self):
        timestamps =  array([  1.,   2.,   3.,   4.,   5.,   6.,   7.,   8.,   9.,  10.,  11.,
                               12.,  13.,  14.,  15.,  16.,  17.,  18.,  19.,  20.,  21.,  22.,
                               23.])
        points =  array([[ 15.13386494,  15.13386494,  15.23543712,  15.48414417,
                           15.73285121,  15.98155825,  16.2302653 ,  16.47897234,
                           16.72767938,  16.97638643,  17.22509347,  17.47380051,
                           17.72250755,  17.9712146 ,  18.21992164,  18.46862868,
                           18.71733573,  18.96604277,  19.21474981,  19.46345686,
                           19.7121639 ,  19.88544197,  19.93128986],
                         [ 48.36429004,  48.36429004,  48.35911822,  48.33372517,
                           48.30833213,  48.28293908,  48.25754603,  48.23215299,
                           48.20675994,  48.1813669 ,  48.15597385,  48.13058081,
                           48.10518776,  48.07979471,  48.05440167,  48.02900862,
                           48.00361558,  47.97822253,  47.95282949,  47.92743644,
                           47.90204339,  47.88435166,  47.87859746],
                        [  0.        ,   0.        ,   0.        ,   0.        ,
                           0.        ,   0.        ,   0.        ,   0.        ,
                           0.        ,   0.        ,   0.        ,   0.        ,
                           0.        ,   0.        ,   0.        ,   0.        ,
                           0.        ,   0.        ,   0.        ,   0.        ,
                           0.        ,   0.        ,   0.        ],
                         [  0.        ,   0.        ,   6.18143766,   6.18143766,
                            6.18143766,   6.18143766,   6.18143766,   6.18143766,
                            6.18143766,   6.18143766,   6.18143766,   6.18143766,
                            6.18143766,   6.18143766,   6.18143766,   6.18143766,
                            6.18143766,   6.18143766,   6.18143766,   6.18143766,
                            6.18143766,   6.18143766,   6.13522597]])

        t1, p1 = groundings.compressP(timestamps, points)
        t2, p2 = groundings.compressC(timestamps, points)
        aeq(t1, t2)
        aeq(p1, p2)



