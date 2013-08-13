from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt4.QtGui import QApplication

from math import exp
from qt_utils import Counter

import os
from dataEvaluation import video_fname
from g3.inference.esdcSearch import filter_shortest_plans

counter = Counter()
COL_IDX = counter.pp()
COL_HAS_VIDEO = counter.pp()
COL_ESDC_TYPE = counter.pp()
COL_TEXT = counter.pp()
COL_SCORE = counter.pp()
COL_SCENARIO = counter.pp()
COL_ESDC_NUM = counter.pp()
COL_RANDOM = counter.pp()
COL_VIDEO_FNAME = counter.pp()
COL_ASSIGNMENT_ID = counter.pp()

import random
class Entry:
    def __init__(self, i, turkCorpus, results):
        self.i = i
        plans = [(result.cost, result.state, result.ggg) for result in results]
        i, r = filter_shortest_plans(plans,
                                     maximum_cost_difference=0.1)
            
        result = results[i]
        self.result = result
        self.annotation = result.annotation
        self.results = results
        self.random = random.randint(0, 10000000)
        self.esdcs = self.result.esdcs
        self.videoFname = video_fname.from_command_log(result.lcmFname)
        # Try different extensions (avi, mp4) for video
        self.videoFname = video_fname.from_command_log(result.lcmFname,\
                                                           extension=".mp4")
        if os.path.exists(self.videoFname) == False:
            self.videoFname = video_fname.from_command_log(result.lcmFname)



        self.esdcType = self.esdcs[0].type
        self.text = self.esdcs.text

        if self.result.annotation.assignmentId != None:
            self.assignmentId = self.result.annotation.assignmentId
            self.scenario = turkCorpus.assignmentForId(self.assignmentId).scenario
            self.scenarioName = self.scenario.name
        else:
            self.assignmentId = None
            self.scenario = None
            self.scenarioName = None

        self.probability = exp(-1.0*self.result.cost)
        
        self.esdcNum = self.result.esdcNum
        self.refresh()

    def refresh(self):
        self.hasVideo = os.path.exists(self.videoFname)
        
class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_TEXT, 200)

        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, turkCorpus, resultsFile):
        self._data = []
        #print "loaded", len(resultsDict), "annotations"
        #load the plans
        #for i, item in enumerate(resultsDict.items()):
        #    annotationId, results = item
        #    resultList, annotation = results
            
        #    print "loaded", len(resultList), "plans"
        #    #load the esdcs
        #    for j, result in enumerate(resultList):
        #        self._data.append(Entry(i, turkCorpus, annotation, result))
        for i, result in enumerate(resultsFile.results):
            self._data.append(Entry(i, turkCorpus, result))
            
        self._unfilteredData = list(self._data)
        self.reset()
    def refresh(self):
        for e in self._data:
            e.refresh()
        self.reset()
    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()
        
    def get(self, i):
        return self._data[i]

    def selectedData(self):
        return [self.get(e.row()) 
                for e in self.view.selectionModel().selectedRows()]
        
    def selectedAnnotation(self):
        entry = self.get(self.view.currentIndex().row())
        return entry.annotation

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_IDX:
            return QVariant("%d" % idx.row())
        elif col == COL_SCORE:
            return QVariant("%e" % e.probability)
        elif col == COL_SCENARIO:
            return QVariant(e.scenarioName)
        elif col == COL_ESDC_TYPE:
            return QVariant(e.esdcType)
        elif col == COL_VIDEO_FNAME:
            return QVariant(os.path.basename(e.videoFname))
        elif col == COL_HAS_VIDEO:
            return QVariant(e.hasVideo)                
        elif col == COL_ESDC_NUM:
            return QVariant("%d" % e.esdcNum)
        elif col == COL_RANDOM:
            return QVariant("%d" % e.random)
        elif col == COL_ASSIGNMENT_ID:
            return QVariant(e.assignmentId)           
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_IDX:
                return QVariant("Index")
            elif section == COL_SCORE:
                return QVariant("Probability")
            elif section == COL_SCENARIO:
                return QVariant("Scenario")
            elif section == COL_ESDC_TYPE:
                return QVariant("Type")                                    
            elif section == COL_ESDC_NUM:
                return QVariant("Esdc Index")
            elif section == COL_VIDEO_FNAME:
                return QVariant("Video")
            elif section == COL_HAS_VIDEO:
                return QVariant("Has Video")                        
            elif section == COL_RANDOM:
                return QVariant("Random")
            elif section == COL_ASSIGNMENT_ID:
                return QVariant("Assignment Id")            
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
        
    def sort(self, col, order):
        if col == COL_TEXT:
            self._data.sort(key=lambda e: e.text)
        elif col == COL_SCORE:
            self._data.sort(key=lambda e: e.probability)
        elif col == COL_SCENARIO:
            self._data.sort(key=lambda e: e.scenarioName)
        elif col == COL_ESDC_TYPE:
            self._data.sort(key=lambda e: e.esdcType)
        elif col == COL_ESDC_NUM:
            self._data.sort(key=lambda e: e.esdcNum)
        elif col == COL_RANDOM:
            self._data.sort(key=lambda e: e.random)
        elif col == COL_ASSIGNMENT_ID:
            self._data.sort(key=lambda e: e.assignmentId)
        elif col == COL_VIDEO_FNAME:
            self._data.sort(key=lambda e: e.videoFname) 
        elif col == COL_HAS_VIDEO:
            self._data.sort(key=lambda e: e.hasVideo) 

        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
            
    def sendToClipboard(self):

        result_str = ""
        for row_idx in self.view.selectionModel().selectedRows():
            for col_idx in range(0, counter.cnt):
                idx = self.index(row_idx.row(), col_idx)
                result_str += str(self.data(idx).toString()) + "\t"
                
            result_str += "\n"
        print "sending", result_str
        QApplication.clipboard().setText(result_str)
            
