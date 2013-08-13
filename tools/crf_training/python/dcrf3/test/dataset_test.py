import unittest
from dcrf3 import dataset as ds
import gsl_utilities as gu
import numpy
class TestCase(unittest.TestCase):
    def testBinarize(self):

        name =  'OBJECT_f_0_l_context_max_all_wordnet'
        value =  0
        min_val =  0
        max_val =  0
        num_units =  36
        
        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                             max_val, num_units)
        self.assertEqual(v1, v2)
        
    def testBinarize2(self):
        name =  'OBJECT_f_0_f_the_F_landmarkPerimeter'
        value =  2.8284271247461898
        min_val =  2.0000000000002682
        max_val =  2.472687546993745
        num_units =  36
        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                             max_val, num_units)
        self.assertEqual(v1, v2)
        
        
    def testLinspace(self):
        v1 = list(numpy.linspace(0, 10, 5))
        v2 = gu.tklib_vector_linspace(0, 10, 5)
        self.assertEqual(v1, v2)


        
    def testBinarize3(self):
        name =  'OBJECT_f_0_f_context_truck_max_wordnet'
        value =  0.1111111111111111
        min_val =  0.25
        max_val =  0.25
        num_units =  36

        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                             max_val, num_units)
        self.assertEqual(v1, v2)

    def testBinarizeBig(self):
        name =  'OBJECT_f_0_l_0_w_null_avs_theta_end_F_avsg_0_-1'
        value =  30.0
        min_val =  -0.84760328128074047
        max_val =  2.2286751606299215e+252
        num_units =  36

        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                             max_val, num_units)
        self.assertEqual(v1, v2)

    def testBinarizeBig2(self):
        name =  'EVENT_end_l1_0_0_w_up_avs_theta_end_F_avsg_0_-1'
        value =  9.2964463465395086e+242
        min_val =  -5.3165064387342285e-42
        max_val =  9.2964463465395086e+242
        num_units =  36

        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                           max_val, num_units)
        self.assertEqual(v1, v2)

    def testBinarizeBig3(self):
        name =  'EVENT_start_l1_0_0_w_pick_avs_theta_end_F_avsg_0_1'
        value = -1.9400307942606223e+185
        min_val =  -1.9400307942606223e+185
        max_val =  1.7094660864289272e+262
        num_units =  36

        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                           max_val, num_units)
        self.assertEqual(v1, v2)


    def testBinarize4(self):
        name =  'OBJECT_f_0_f_context_max_flickr_trailer'
        value =  53
        min_val =  0
        max_val =  53
        num_units =  36

        v1 = ds.binarize_feature_uniform_p(name, value, min_val,
                                           max_val, num_units)
        v2 = ds.binarize_feature_uniform_c(name, value, min_val,
                                           max_val, num_units)
        self.assertEqual(v1, v2)
