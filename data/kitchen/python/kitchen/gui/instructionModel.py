from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt4.QtGui import QApplication

from qt_utils import Counter
import math

counter = Counter()
COL_IDX = counter.pp()
COL_TEXT = counter.pp()
COL_ANNOTATION = counter.pp()
COL_COST = counter.pp()
COL_PROBABILITY = counter.pp()

class Entry:
    @staticmethod
    def from_annotated_recipe(ar, idx, start_state, cost):
        text = ar.idx_to_instruction(idx)        
        annotation = ar.idx_to_annotation(idx)        
        return Entry(idx, text, annotation, start_state, cost)

    def __init__(self, idx, text, annotation, start_state, cost):
        self.idx = idx
        self.text = text
        self.annotation = annotation
        self.start_state = start_state
        self.cost = cost
        self.probability = math.exp(-cost)

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self.filter = lambda x: True

        self.setData([])
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_TEXT, 300)
        self.view.setColumnWidth(COL_ANNOTATION, 300)


        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setRecipe(self, ar):
        entries = [Entry.from_annotated_recipe(ar, i, ar.idx_to_start_state(i),
                                               0) 
                   for i in range(ar.num_instructions)]
        self.setData(entries)

    def setData(self, entries):
        self._data = list(entries)
        self._unfilteredData = list(self._data)
        self.setFilter(self.filter)
        self.reset()

    @property
    def entries(self):
        return self._data
    def allData(self):
        return self._data

    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()

        
    def get(self, i):
        return self._data[i]
    

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_IDX:
            return QVariant(e.idx)
        elif col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_ANNOTATION:
            return QVariant(e.annotation)
        elif col == COL_COST:
            return QVariant("%e" % e.cost)
        elif col == COL_PROBABILITY:
            return QVariant("%e" % e.probability)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_IDX:
                return QVariant("Idx")
            elif section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_ANNOTATION:
                return QVariant("Annotation")
            elif section == COL_COST:
                return QVariant("Cost")
            elif section == COL_PROBABILITY:
                return QVariant("Probability")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        

    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(i.row()) 
                for i in self.view.selectionModel().selectedRows()]


    def selectedExamples(self):
        return [self.get(idx.row()).ex
                for idx in self.view.selectedIndexes()]



    def sort(self, col, order):
        if col == COL_IDX:
            self._data.sort(key=lambda e: e.idx)
        elif col == COL_TEXT:
            self._data.sort(key=lambda e: e.text)
        elif col == COL_ANNOTATION:
            self._data.sort(key=lambda e: e.annotation)

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
            
