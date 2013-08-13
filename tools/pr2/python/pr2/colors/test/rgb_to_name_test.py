import unittest
from pr2.colors.rgb_to_name import rgb_to_name

class TestCase(unittest.TestCase):

    def testColor(self):
        self.assertEqual(rgb_to_name(0, 0, 0), 'black')

        self.assertEqual(rgb_to_name(0, 0, 1), 'purple')
        self.assertEqual(rgb_to_name(0, 1, 0), 'green')

        self.assertEqual(rgb_to_name(1, 0, 0), 'orange')
