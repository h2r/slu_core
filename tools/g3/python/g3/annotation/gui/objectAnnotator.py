import matplotlib_qt
import numpy as na
import os
from esdcs.gui import context3d 
from esdcs.gui.drawUtils import drawGrounding, drawObject, drawPath
from esdcs.esdcIo import annotationIo
from spatial_features.groundings import Path, PhysicalObject, Place
from esdcs.context import Context
from standoff import TextStandoff
import qt_utils

from path_segmentation import uniform_segmenter
from path_segmentation import pause_segmenter
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
import basewindow
from PyQt4.QtGui import QMainWindow, QFileDialog, QItemSelection, QItemSelectionModel

from PyQt4.QtCore import SIGNAL
import objectAnnotator_ui
import pylab as mpl
from esdcs.gui import annotationModel, esdcTreeModel
from esdcs.gui import groundingsModel, drawUtils
from corpusMturk import readCorpus
from numpy import transpose as tp
        
#from gis.mapping.osmSemanticMap import OsmSemanticMap, osm_way_to_physical_obj

#from pyPgSQL import PgSQL
from username import username

import traceback

#PgSQL.fetchReturnsList = 1

def errorhandler(errstr, errflag):
    traceback.print_stack()

na.seterrcall(errorhandler)
na.seterr(all='ignore')

class MainWindow(QMainWindow, objectAnnotator_ui.Ui_MainWindow):
    def mpl_draw(self):
        self.restoreLimits()
        self.figure.canvas.draw()

    def __init__(self, mturkCorpus=None, stateType=None, ground_children=False):
        QMainWindow.__init__(self)

        if mturkCorpus != None:
            self.corpus = readCorpus.Corpus(mturkCorpus)
        else:
            self.corpus = None
        self.ground_children = ground_children
        self.artists = []
        self.state = None
        self.stateType = stateType
        self.artistsDict = {}
        self.pathNodes = {}
        self.currPath = []


        self.setupUi(self)
        self.figure = mpl.figure()
        self.axes = self.figure.gca()
        self.axes.set_aspect("equal")
        self.oldParent = self.figure.canvas.parent()
        self.figure.canvas.setParent(self)
        self.matplotlibFrame.layout().addWidget(self.figure.canvas)
        self.toolbar = NavigationToolbar2QT(self.figure.canvas, self)
        self.addToolBar(self.toolbar)
#        self.limits = [0, 60, 20, 60]
        self.limits = [-71.15, -71.05, 42.35, 42.41]
        self.entireText = None
        self.addPathButton.setEnabled(False)
        self.restoreLimits()


        self.contextWindow = context3d.MainWindow()
        self.contextWindow.show()
        self.connect(self.contextWindow.glWidget,
                     SIGNAL("selectedGrounding()"),
                     self.selectedGrounding)

        self.connect(self.sourceEdit,
                     SIGNAL("editingFinished()"),
                     self.updateSource)


        self.connect(self.shouldDrawAgentCheckBox, SIGNAL("stateChanged(int)"),
                     self.draw)

        self.connect(self.annotationFilter,
                     SIGNAL("editingFinished()"),
                     self.filterAnnotations)

        self.figure.canvas.mpl_connect('draw_event', self.updateLimits)
        self.figure.canvas.mpl_connect('pick_event', self.onpick)

        self.esdcModel = esdcTreeModel.Model(self.esdcTreeView)
        self.annotationModel = annotationModel.Model(self.annotationTable)
        self.groundingsModel = groundingsModel.Model(self.groundingsTable)
        self.contextModel = groundingsModel.Model(self.contextTable)
        
        self.pathSegmentsModel = groundingsModel.Model(self.pathSegmentsTable)

        self.largePathSegmentsModel = groundingsModel.Model(self.largePathSegmentsTable)
        
        self.path_segmenter = uniform_segmenter.Segmenter()
        self.large_path_segmenter = pause_segmenter.Segmenter()

        print "connecting"

        self.connect(self.pathSegmentsTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.draw)
        self.connect(self.largePathSegmentsTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectLargePathSegments)
        self.connect(self.esdcTreeView.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectEsdc)

        self.connect(self.annotationTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectAnnotation)

        self.connect(self.contextTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectContext)

        self.connect(self.groundingsTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectGrounding)

        self.connect(self.addAgentPathSegmentsButton,
                     SIGNAL("clicked()"),
                     self.addAgentPathSegments)
        
        self.connect(self.updateStateButton,
                     SIGNAL("clicked()"),
                     self.updateState)

        self.connect(self.addGroundingButton,
                     SIGNAL("clicked()"),
                     self.addGrounding)

        self.connect(self.clearGroundingsButton,
                     SIGNAL("clicked()"),
                     self.clearGroundings) 
        
        self.connect(self.addPathButton,
                     SIGNAL("clicked()"),
                     self.addPath)

        self.connect(self.actionNextEsdc,
                     SIGNAL("triggered()"),
                     self.nextEsdc)

        self.connect(self.actionClearGroundings,
                     SIGNAL("triggered()"),
                     self.clearGroundings) 

        self.connect(self.actionNextNan,
                     SIGNAL("triggered()"),
                     self.selectNanAnnotation)        

        self.connect(self.actionPreviousEsdc,
                     SIGNAL("triggered()"),
                     self.previousEsdc)                
        


        self.connect(self.actionNextCommand,
                     SIGNAL("triggered()"),
                     self.nextCommand)

        self.connect(self.actionPreviousCommand,
                     SIGNAL("triggered()"),
                     self.previousCommand)                

        
        self.connect(self.actionSave,
                     SIGNAL("triggered()"),
                     self.save)                
        self.connect(self.actionLoad,
                     SIGNAL("triggered()"),
                     self.load)

        self.connect(self.actionPath_Nodes,
                     SIGNAL("triggered()"),
                     self.path_mode)
        
        self.connect(self.actionGroundings,
                     SIGNAL("triggered()"),
                     self.groundings_mode)

        self.connect(self.classComboBox,
                     SIGNAL("currentIndexChanged(int)"),
                     self.updateClass)   

        self.connect(self.actionNextEmptyAnnotation,
                     SIGNAL("triggered()"),
                     self.selectNextEmptyAnnotation)

        
        self.connect(self.actionGroundingIsCorrect,
                     SIGNAL("triggered()"),
                     self.setGroundingIsCorrect)

        self.connect(self.actionGroundingIsNotCorrect,
                     SIGNAL("triggered()"),
                     self.setGroundingIsNotCorrect)

        


    def selectAnnotation(self):
        print "selecting annotation"
        entry = self.annotationModel.selectedData()
        annotation = entry.annotation


        if len(annotation.context.groundings) == 0:
            new_context = Context.from_groundings(annotation.groundings)
            self.contextWindow.setContext(new_context)
        else:
            self.contextWindow.setContext(annotation.context)
        self.contextModel.setData(annotation.context.groundings)
        self.drawWithoutGroundings()
        
        self.esdcModel.setData(annotation.esdcs)
        self.esdcTreeView.expandAll()

        self.esdcList = sorted([e for e in annotation.esdcs.flattenedEsdcs
                                #if annotation.getGroundings(e) != [] and e.type == "PLACE"
                                if e.type in ["EVENT", "OBJECT", "PLACE", "PATH"]
                                #if e.type in ["OBJECT", "PLACE"]
                                ],
                               key=lambda esdc: esdc.range[0])
        #self.esdcList = [e for e in annotation.esdcs]

        if len(self.esdcList) > 0:
            print "selecting first esdc", self.esdcList[0]
            self.esdcModel.selectEsdc(self.esdcList[0])
        self.entireText = annotation.entireText
        
        #paths = self.path_segmenter.segment_path(annotation.agent.path)
        #self.pathSegmentsModel.setData(paths)
        #paths = self.large_path_segmenter.segment_path(annotation.agent.path)
        #self.largePathSegmentsModel.setData(paths)
        #self.pathSegmentsTable.selectRow(0)
        self.annotationFnameEdit.setText(annotation.fname)
        
    def updateSource(self):
        annotation = self.annotationModel.selectedData().annotation
        esdc = self.esdcModel.selectedEsdc()        
        value = str(self.sourceEdit.text())
        if value == "None":
            value = None
        annotation.setSource(esdc, value)

        
        
    def updateClass(self, value=None):
        annotation = self.annotationModel.selectedData().annotation
        esdc = self.esdcModel.selectedEsdc()        
        print "value", value, value.__class__
        if not isinstance(value, bool):
            value = None
        print "value", value, value.__class__
        if esdc != None:
            if value == None:
                value = eval(str(self.classComboBox.currentText()))
            else:
                idx = self.classComboBox.findText(str(value))
                self.classComboBox.setCurrentIndex(idx)

            print "updating", value
            annotation.setGroundingIsCorrect(esdc, value)

    def setGroundingIsCorrect(self):
        self.updateClass(value=True)
        self.nextEsdc()
        
    def setGroundingIsNotCorrect(self):
        self.updateClass(value=False)
        self.nextEsdc()

    def selectEsdc(self):
        esdc = self.esdcModel.selectedEsdc()
        if esdc != None:
            annotation = self.annotationModel.selectedAnnotation()
            labelText = drawUtils.entireTextAsFormattedLabelText(esdc)
            self.esdcTextWidget.setText(labelText)
            groundings = annotation.getGroundings(esdc)
            self.groundingsModel.setData(groundings)

            self.contextWindow.highlightGroundings(groundings)
            self.contextWindow.clearSelection()

            cls = annotation.isGroundingCorrect(esdc)
            idx = self.classComboBox.findText(str(cls))
            self.classComboBox.setCurrentIndex(idx)

            source = annotation.getSource(esdc)
            if source == None:
                source = "None"
            self.sourceEdit.setText(source)
            
        else:
            self.esdcTextWidget.setText(self.entireText)
        
#        self.draw()
        
    def updateLimits(self, mplEvent):
        self.saveLimits()
    def saveLimits(self):
        self.limits = self.axes.axis()
    def restoreLimits(self):
        if self.limits != None:
            self.axes.axis(self.limits)

    def clearGroundings(self):
        print "clearing groundings"
        esdc = self.esdcModel.selectedEsdc()
        if esdc != None:
            annotation = self.annotationModel.selectedAnnotation()
            annotation.removeAllGroundings(esdc)
            self.groundingsModel.setData(annotation.getGroundings(esdc))
            self.contextWindow.highlightGroundings(annotation.getGroundings(esdc))
            if self.ground_children:
                self.add_child_groundings(annotation, esdc, None)
                # for child in esdc.childTokens('f'):
                #     if isinstance(child, TextStandoff) or child.isEmpty():
                #         continue
                #     annotation.removeAllGroundings(child)
            self.draw()
            
    def updateState(self, state=None, redraw=True):
        if state == None:
            self.state, am = self.stateApp.get_current_state()
        else:
            self.state = state
        if redraw:
            self.draw()



    def drawState(self):
        artists = []
        if self.state != None:
            for obj in self.state.get_objects():
                self.artists.extend(drawGrounding(self.axes, obj,
                                                  plotArgs=dict(color="blue")))
            
        return artists
        

    def draw(self):
        self.axes.clear()
            
        self.artists = []
        self.artists.extend(self.drawState())
        self.artists.extend(self.drawGrounding())
        self.artists.extend(self.populate_objects(pickerType=4))
        if self.shouldDrawAgent:
            self.artists.extend(self.drawAgent())
        self.artists.extend(self.drawContext())
        #self.artists.extend(drawRobotFromStateApp(self.axes, self.stateApp))
        self.addPathButton.setEnabled(False)

        self.artists.extend(self.drawPathSegments())

        #self.restoreLimits()
        self.figure.canvas.draw()

    def drawPathSegments(self):
        artists = []
        for path in self.pathSegmentsModel.selectedGroundings():
            artists.extend(drawGrounding(self.axes, path,
                                         plotArgs=dict(color="orange", lw=2)))
        return artists

    def drawForPath(self):
        self.axes.clear()
            
        self.artists = []
        self.artistsDict = {}
        self.artists.extend(self.drawState())
        self.artists.extend(self.drawGrounding())
        self.artists.extend(self.populate_objects(pickerType=None))
        annotation = self.annotationModel.selectedAnnotation()
        path = tp(annotation.agent.path.points_xy)
        for point in path:
            artist = self.axes.plot(point[0], point[1], "bo-", markersize=10, picker=5)
            print artist
            self.pathNodes[artist[0]] = (point[0], point[1])
 
        self.addPathButton.setEnabled(True)
        self.figure.canvas.draw()

    def drawWithoutGroundings(self):
        self.axes.clear()

        self.artists=[]
        self.artists.extend(self.drawState())
        self.artists.extend(self.drawAgent())
        self.artists.extend(self.populate_objects(pickerType=2))
        
        self.addPathButton.setEnabled(False)
        #print "drawing", self.artists
        self.figure.canvas.draw()

    def populate_objects(self, pickerType):
        if self.stateType == "gis":
            return self.populate_objects_gis(pickerType=pickerType)
        else:
            return self.populate_objects_annotation()

    def populate_objects_annotation(self):
        annotation = self.annotationModel.selectedAnnotation()
        artists = []
        for o in annotation.context.objects:
            objartists = drawObject(self.axes, o,
                                    plotArgs={"color":"blue", "picker":1})
            for a in objartists:
                self.artistsDict[a] = o
            artists.extend(objartists)                
        return artists

    def populate_objects_gis(self, pickerType=None):
        artists = []
        self.artistsDict = {}
        annotation = self.annotationModel.selectedAnnotation()
        #print annotation.agent.path
        path = tp(annotation.agent.path.points_xyztheta)
        #print "path is", path
        #formattedPath = ['%s %s' % (x, y) for x, y in path]
        smap = OsmSemanticMap(username(), "bigbubba", "osm", start_loc=path[0])
        buildings = {}
        highways = {}
        for point in path:
            vobjs = smap.visible_objects((point[0], point[1]), epsilon=0.001)
            for obj in vobjs:
                buildings[obj.id] = obj
            vstreets = smap.get_visible_highways((point[0], point[1]), epsilon=0.001)
            print "vstreets is:", vstreets
            for street in vstreets:
                path, id = osm_way_to_physical_obj(street[0], smap.cur)
                highways[id] = path
                
        for building in buildings.values():
            objartists = drawObject(self.axes, building,
                                    plotArgs={"color":"blue", "picker":pickerType})
            for a in objartists:
                self.artistsDict[a] = building
            artists.extend(objartists)
        print "highways are:", highways
        for path in highways.values():
            for p in path:
                wayartists = drawObject(self.axes, p,
                                      plotArgs={"color":"blue", "picker":pickerType},
                                        shouldDrawText=False) 
                for a in wayartists:
                    self.artistsDict[a] = p
                artists.extend(wayartists)
        return artists

    def drawAgent(self, pickerType=None):
        artists = []
        annotation = self.annotationModel.selectedAnnotation()
        if annotation.agent != None:
            artists.extend(drawPath(self.axes, annotation.agent.path,
                            shouldDrawStartAndEnd=False, 
                            plotArgs={"color":"green", "picker":pickerType}))
        return artists

    def drawGrounding(self):
        artists = []
        esdc = self.esdcModel.selectedEsdc()

        if esdc != None:
            annotation = self.annotationModel.selectedAnnotation()
            for grounding in annotation.getGroundings(esdc):
                artists.extend(drawGrounding(self.axes, grounding,
                                             plotArgs={"color":"yellow"}))

        #sgrounding = self.groundingsModel.selectedGrounding()
        sgrounding = None
        if sgrounding != None:
            artists.extend(drawGrounding(self.axes, sgrounding,
                                         plotArgs={"color":"red"}))

        return artists


    def drawContext(self):
        artists = []
        for grounding in self.contextModel.selectedGroundings():
            artists.extend(drawGrounding(self.axes, grounding,
                                         plotArgs={"color":"purple"}))

        return artists

        
    def socketActivated(self, arg):
        self.stateApp.lc.handle()

    def path_mode(self):
        self.drawForPath()

    def groundings_mode(self):
        self.drawWithoutGroundings()
        
    def selectPlace(self, place):
        annotation = self.annotationModel.selectedAnnotation()
        esdc = self.esdcModel.selectedEsdc()        
        annotation.addGrounding(esdc, place)
        self.groundingsModel.setData(annotation.getGroundings(esdc))
        if self.ground_children:
            self.add_child_groundings(annotation, esdc, place)
            # for child in esdc.childTokens('f'):
            #     if isinstance(child, TextStandoff) or child.isEmpty():
            #         continue
            #     annotation.addGrounding(child, place)

    def selectedGrounding(self):
        groundings = self.contextWindow.selectedGroundings()
        for g in groundings:
            self.annotateGrounding(g)

    def annotateGrounding(self, grounding):
        if isinstance(grounding, PhysicalObject):
            self.selectObject(grounding)
        elif isinstance(grounding, Place):
            self.selectPlace(grounding)
        else:
            raise ValueError("Unexpected type: " + `grounding`)

    def addAgentPathSegments(self):
        groundings = self.pathSegmentsModel.selectedGroundings()
        timestamps = []
        points_ptsztheta = []
        for path in groundings:
            timestamps.extend(path.timestamps)
            points_ptsztheta.extend(path.points_ptsztheta)
        path = Path(timestamps, tp(points_ptsztheta))
        annotation = self.annotationModel.selectedAnnotation()
        agent = annotation.agent
        prism = agent.prismAtT(path.start_t)
        pobj = PhysicalObject(prism, agent.tags, path, agent.id)
        self.annotateGrounding(pobj)
            
        
    def addGrounding(self):
        for grounding in self.contextModel.selectedGroundings():
            print "adding", grounding
            self.annotateGrounding(grounding)

    def selectObject(self, obj):
        annotation = self.annotationModel.selectedAnnotation()
        esdc = self.esdcModel.selectedEsdc()
        annotation.addGrounding(esdc, obj)
        self.groundingsModel.setData(annotation.getGroundings(esdc))
        if self.ground_children:
            self.add_child_groundings(annotation, esdc, obj)
            # for child in esdc.childTokens('f'):
            #     if isinstance(child, TextStandoff) or child.isEmpty():
            #         continue
            #     print "adding object grounding for child"
            #     annotation.addGrounding(child, obj)

    def add_child_groundings(self, annotation, esdc, g):
        for child in esdc.children('f'):
            if isinstance(child, TextStandoff) or child.isEmpty():
                continue
            if g is None:
                annotation.removeAllGroundings(child)
            else:
                annotation.addGrounding(child, g)
            self.add_child_groundings(annotation, child, g)

    def addPath(self):
        annotation = self.annotationModel.selectedAnnotation()
        esdc = self.esdcModel.selectedEsdc()
        timestamps = [0 for p in self.currPath]
        points_xyztheta = [tp(self.currPath)[0], tp(self.currPath)[1], [0 for p in self.currPath], [0 for p in self.currPath]]
        path = Path(timestamps, points_xyztheta)
        annotation.addGrounding(esdc, path)
        self.groundingsModel.setData(annotation.getGroundings(esdc))
        self.pathNodes = {}
        self.currPath = []
        self.drawForPath()

    def selectGrounding(self):
        self.draw()

    def selectContext(self):
        self.draw()
        
    def nextEsdc(self):
        selectedEsdc = self.esdcModel.selectedEsdc()
        index = self.esdcList.index(selectedEsdc)
        newIndex = index + 1
        newEsdc = self.esdcList[index]
        
        while newEsdc.isEmpty() and newIndex < len(self.esdcList):
            newEsdc = self.esdcList[index]
            newIndex = newIndex + 1
            
        if newIndex == len(self.esdcList):
            self.nextCommand()
        else:
            esdc = self.esdcList[index]
            while esdc.isEmpty():
                newIndex += 1
                esdc = self.esdcList[index]
            self.selectByIndex(newIndex)

        
    def previousEsdc(self):
        selectedEsdc = self.esdcModel.selectedEsdc()
        index = self.esdcList.index(selectedEsdc)
        self.selectByIndex(index - 1)

    def nextCommand(self):
        self.annotationTable.selectRow(self.annotationTable.currentIndex().row()
                                       + 1)

    def previousCommand(self):
        self.annotationTable.selectRow(self.annotationTable.currentIndex().row()
                                       - 1)        

    def selectByIndex(self, index):
        if index >= len(self.esdcList):
            index = len(self.esdcList) - 1
        if index < 0:
            index = 0
        nextEsdc = self.esdcList[index]
        self.esdcModel.selectEsdc(nextEsdc)
    def save(self, fname=None):
        if fname != "" and fname != None:
            self.fnames = [fname]
            annotationIo.save(fname)
        annotationIo.save_separate_files(self.annotations)
            
            

    def load(self, fname=None):
        if fname == None:
            fname = str(QFileDialog.getOpenFileName(self, "Open File", self.fname))
        
        if fname != "":
            print "loading", fname
            self.setWindowTitle(self.windowTitle() + ": " + str(fname))
            if isinstance(fname, str):
                fnames = [fname]
            else:
                fnames = fname
            self.fnames = fnames
            self.annotations = annotationIo.load_all(self.fnames)
            if self.corpus != None:
                print "corpus", self.corpus
                self.annotations = [a for a in self.annotations 
                                    if os.path.exists(self.corpus.assignmentForId(a.assignmentId).scenario.lcmlog)]
            self.annotationModel.setData(self.annotations)
            #self.selectAnnotationBeforeEmptyAnnotation()
            #self.selectNanAnnotation()
            self.annotationTable.selectRow(0)
            #self.selectByMatch("pick up the furthest skid of tires and load them onto the trailer")
            #self.selectByMatch("Go forward pick up pallets")

    def selectByMatch(self, query):
        for i, annotation in enumerate(self.annotations):
            if query in annotation.entireText:
                self.annotationTable.selectRow(i)
                break
            
    def selectNanAnnotation(self):
        for i, annotation in enumerate(reversed(self.annotations)):
            foundNan = False
            for groundings in annotation.groundings:
                for g in groundings:
                    if any(na.isnan(x) for x in g.points_xy.flat):
                        foundNan = True
                        break
            if foundNan:
                break
                
        self.annotationTable.selectRow(len(self.annotations) - i - 1)        
            
    def selectNextEmptyAnnotation(self):
        start =  self.annotationTable.currentIndex().row() + 1

        for i in range(start, self.annotationModel.rowCount()):
            annotation = self.annotationModel.get(i).annotation
            print "checking", i
            if annotation.emptyGroundings():
                break
        print "selecting", i
        self.annotationTable.selectRow(i)
            
    def onpick(self, event):
        print "called onpick"
        artist = event.artist
        plotArgs={"color":"red"}
        artist.set(**plotArgs)
        if self.artistsDict:
            if artist in self.artistsDict:
                print self.artistsDict[artist]
                self.selectObject(self.artistsDict[artist])
        if self.pathNodes:
            if artist in self.pathNodes:
                print self.pathNodes[artist]
                self.currPath.append(self.pathNodes[artist])
                print self.currPath
                artist.set_markerfacecolor("red")
        self.figure.canvas.draw()

    @property
    def shouldDrawAgent(self):
        return qt_utils.isChecked(self.shouldDrawAgentCheckBox)


    def filterAnnotations(self):
        expr = self.annotationFilter.text()
        print expr
        try:
            filterFunction = eval(str(expr))
        except:
            raise
        self.annotationModel.setFilter(filterFunction)
        
    def selectLargePathSegments(self):
        selection = QItemSelection()
        for path in self.largePathSegmentsModel.selectedGroundings():

            for i in range(self.pathSegmentsModel.rowCount()):
                entry = self.pathSegmentsModel.get(i)
                if path.contains(entry.grounding.range):
                    idx = self.pathSegmentsModel.index(i, 0)
                    selection.select(idx, idx)
                    #self.pathSegmentsTable.selectRow(i)
                    #break
        print 'adding path', selection
        self.pathSegmentsTable.selectionModel().select(selection,
                                                       QItemSelectionModel.Rows | QItemSelectionModel.SelectCurrent)


def main():
    from optparse import OptionParser
    app = basewindow.makeApp()
    parser = OptionParser()
    parser.add_option("--corpus-filename",dest="corpus_fname",  metavar="FILE",
                      action="append")
    parser.add_option("--mturk-corpus-filename",dest="mturk_corpus_fname", 
                      metavar="FILE")
    parser.add_option("--state-type",dest="state_type", 
                      metavar="FILE")
    parser.add_option("--automatically_ground_children", dest="ground_children", 
                      action="store_true", metavar="BOOL",
                      help="Whenever an ESDC is grounded, ground all children from its figure field to the same object")

    (options, args) = parser.parse_args()

    wnd = MainWindow(options.mturk_corpus_fname, options.state_type, options.ground_children)
    wnd.show()
    wnd.load(options.corpus_fname)

    app.exec_()

if __name__=="__main__":
    main()

