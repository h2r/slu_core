import unittest
from environ_vars import SLU_HOME


class TestCase(unittest.TestCase):
    
    def testLoadFromCls(self):
        import jpype
        java = jpype.JPackage("java")


        pkg = jpype.JPackage("edu.mit.csail.spatial.esdcs")
        clsFile = pkg.LoadClassifier
        print "cls", clsFile
        print "clsfile", dir(clsFile)
        print "file:", SLU_HOME+"/tools/esdcs/data/classifier.ser"
        print "classpath", java.lang.System.getProperty("java.class.path")
        clsFile.load(SLU_HOME+"/tools/esdcs/data/classifier.ser")
        
