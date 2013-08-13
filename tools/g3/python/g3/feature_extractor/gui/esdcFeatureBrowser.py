import matplotlib_qt
from esdcs.gui.drawUtils import drawGrounding
from optparse import OptionParser
from environ_vars import SLU_HOME
import pylab as mpl
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import basewindow
from PyQt4.QtGui import QMainWindow, QFileDialog
from PyQt4.QtCore import SIGNAL
from esdcs.esdcIo import annotationIo
from g3.feature_extractor.gui import esdcFeatureBrowser_ui
from esdcs.gui import annotationModel
import featureModel
from corpusMturk import readCorpus
from esdcs.gui import esdcTreeModel
from g3.feature_extractor.grounded_features import GGGFeatures
from g3.feature_extractor.esdc_features import EsdcFeatures
from g3.annotation_to_ggg import annotation_to_ggg_map

class MainWindow(QMainWindow, esdcFeatureBrowser_ui.Ui_MainWindow):

    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()

    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self):
        if self.limits != None:
            self.axes.axis(self.limits)


    def __init__(self, feature_extractor=None):
        QMainWindow.__init__(self)
        

        self.feature_extractor = feature_extractor
        if self.feature_extractor == None:
            self.feature_extractor = GGGFeatures()

        self.setupUi(self)

        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)
        self.limits = [0, 60, 20, 60]
        self.entireText = None
        self.restoreLimits()
        


        
        self.esdcModel = esdcTreeModel.Model(self.esdcTreeView)
        self.annotationModel = annotationModel.Model(self.annotationTable)
        self.featureModel = featureModel.Model(self.featureTable)

        self.connect(self.annotationTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectAnnotation)

        self.connect(self.esdcTreeView.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.onSelectEsdc)

        self.connect(self.esdcFilter,
                     SIGNAL("editingFinished()"),
                     self.filterEsdcs)

        
        self.esdcToFvalues = {}
        self.esdcToFnames = {}


    def loadAnnotations(self, annotations):
        self.annotations = annotations
        self.annotationModel.setData(self.annotations)
        for i, annotation in enumerate(reversed(self.annotations)):
            if not annotation.emptyGroundings():
                break
        #self.annotationTable.selectRow(len(self.annotations) - i - 1)
        self.annotationTable.selectRow(len(self.annotations) - 3)
        
        
    def load(self, fname=None):
        if fname == None:
            fname= QFileDialog.getLoadFileName(self, "Open File", self.fname)
        if fname != "":
            self.fname = fname
            annotations = annotationIo.load(self.fname)

            self.loadAnnotations(annotations)

    def selectAnnotation(self):
        annotation = self.annotationModel.selectedAnnotation()
        
        self.esdcModel.setData(annotation.esdcs)
        self.esdcTreeView.expandAll()

        a_state, gggs = annotation_to_ggg_map(annotation)
        self.esdcToFvalues = {}
        self.esdcToFnames = {}

        for g_index, (esdc, ggg) in enumerate(gggs.iteritems()):
            print "extracting features", esdc
            factor_id_to_fvalues, factor_id_to_fnames = self.feature_extractor.extract_features(a_state, ggg,
                                                                                                factors=None)

            for factor_id in factor_id_to_fvalues.keys():
                esdc = ggg.factor_id_to_esdc(factor_id)
                print "loading", esdc
                #assert not esdc in self.esdcToFvalues
                self.esdcToFvalues[esdc] = factor_id_to_fvalues[factor_id]
                self.esdcToFnames[esdc] = factor_id_to_fnames[factor_id]
            
        self.draw()

    def draw(self):
        self.axes.clear()
        artists = []
        annotation = self.annotationModel.selectedAnnotation()
        for groundings in annotation.groundings:
            for g in groundings:
                artists.extend(drawGrounding(self.axes, g,
                                             plotArgs={"color":"black"}))
        esdc = self.esdcModel.selectedEsdc()                
        if esdc != None:
            for grounding in annotation.getGroundings(esdc):
                print "esdc grounding", repr(grounding.points_pts)
                print "path", hasattr(grounding, "path")
                if hasattr(grounding, "path"):
                    print "path", grounding.path.points_xy
                    print "path len", len(grounding.path.points_xy)

                artists.extend(drawGrounding(self.axes, grounding,
                                             plotArgs={"color":"yellow",
                                                       "zorder":100,
                                                       }))

        self.restoreLimits()
        self.figure.canvas.draw()



    def selectEsdc(self, esdc):
        self.esdcModel.selectEsdc(esdc)
        
    def onSelectEsdc(self):
        esdc = self.esdcModel.selectedEsdc()
        print "onSelectEsdc", esdc
        if esdc != None and esdc in self.esdcToFvalues:
            fvals = self.esdcToFvalues[esdc]
            fnames = self.esdcToFnames[esdc]
            print "selected esdc", esdc
            self.featureModel.setData(dict(zip(fnames, fvals)))
        self.draw()

    def filterEsdcs(self):
        expr = self.esdcFilter.text()
        print expr
        try:
            filterFunction = eval(str(expr))
        except:
            raise
        self.annotationModel.setFilter(filterFunction)


def main(argv):
    feature_extractors = dict((x.__name__, x) for x in 
                               [GGGFeatures,
                                EsdcFeatures])

    parser = OptionParser()
    parser.add_option("--feature-extractor",dest="feature_extractor", 
                      help="Feature extractor class name")
    (options, args) = parser.parse_args()    
    cls = feature_extractors.get(options.feature_extractor, None)
    feature_extractor = cls() if cls != None else None
    app = basewindow.makeApp()

    wnd = MainWindow(feature_extractor)
    corpusFname = argv[1]


    wnd.load(corpusFname)    
    wnd.show()
    app.exec_()

if __name__=="__main__":
    import sys
    main(sys.argv)

