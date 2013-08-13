import unittest
from stopwords import stopwords

class TestCase(unittest.TestCase):
    def testStopwords(self):
        self.assertTrue("the" in stopwords)
        self.assertFalse("fish" in stopwords)
        self.assertTrue("a" in stopwords)
