
import unittest
from numpy import transpose as tp, array
from spatial_features.groundings import Path, Prism, PhysicalObject
import math
from assert_utils import assert_array_equal as aeq

class TestCase(unittest.TestCase):
    def testPath(self):
        pobj = PhysicalObject(Prism.from_points_xy(tp([(0, 0), (1, 0), (1, 1), (0, 1)]), 0, 3),
                              ["tires"],
                              path=Path.from_xyztheta([0, 1, 2],
                                        tp([(3, 3, 0, 0), (3, 3, 0, math.pi/4), (4, 4, 1, math.pi/4)])))
        

        self.assertEqual(pobj.prismAtT(0),
                         pobj.prism)

        aeq(pobj.path.locationAtT(1),
            (3, 3, 0, math.pi/4))

        self.assertEqual(pobj.prismAtT(1),
                         Prism.from_points_xy(array([[ 0.5       ,  1.20710678,  0.5       , -0.20710678],
                                                          [-0.20710678,  0.5       ,  1.20710678,  0.5       ]]), 0.0, 3.0))

        aeq(pobj.path.locationAtT(2),
            (4, 4, 1, math.pi/4))
        
        self.assertEqual(pobj.prismAtT(2),
                         Prism.from_points_xy(array([[ 1.5       ,  2.20710678,  1.5       ,  0.79289322],
                                           [ 0.79289322,  1.5       ,  2.20710678,  1.5       ]]),
                                    1.0, 4.0))


        aeq(pobj.path.locationAtT(-1),
            pobj.path.locationAtT(len(pobj.path.timestamps)))
        

    def testRotateAroundOrigin(self):
        pobj = PhysicalObject(Prism.from_points_xy(tp([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]), 0, 3),
                              ["tires"],
                              path=Path.from_xyztheta([0, 1],
                                        tp([(3, 3, 0, 0), (3, 3, 0, math.pi/4)])))
        
        self.assertEqual(pobj.centroid2d, [0, 0])
        print "prism"
        self.assertEqual(pobj.prismAtT(1),
                         Prism.from_points_xy(array([[ -5.55111512e-17,   7.07106781e-01,   5.55111512e-17,
                                              -7.07106781e-01],
                                           [ -7.07106781e-01,  -5.55111512e-17,   7.07106781e-01,
                                              5.55111512e-17]]), 0.0, 3.0))
                         
        


    def testRotateAwayFromOrigin(self):

        pobj = PhysicalObject(Prism.from_points_xy(tp([(0, 0), (1, 0), (1, 1), (0, 1)]), 0, 3),
                              ["tires"],
                              path=Path.from_xyztheta([0, 1],
                                        tp([(3, 3, 0, 0), (3, 3, 0, math.pi/4)])))
        
        aeq(pobj.centroid2d, (0.5, 0.5))
        newp = pobj.prismAtT(1)
        self.assertEqual(newp,
                         Prism.from_points_xy(array([[ 0.5       ,  1.20710678,  0.5       , -0.20710678],
                                           [-0.20710678,  0.5       ,  1.20710678,  0.5       ]]),
                                    0.0, 3.0))

        aeq(newp.centroid2d(),
            (0.5, 0.5))
                         
