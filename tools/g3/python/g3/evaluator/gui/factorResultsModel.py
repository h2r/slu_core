from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt4.QtGui import QApplication
import math
from qt_utils import Counter
counter = Counter()
COL_FACTOR_ID = counter.pp()
COL_TYPE = counter.pp()
COL_TEXT = counter.pp()
COL_PROB = counter.pp()
COL_COST = counter.pp()
class Entry:
    def __init__(self, i, ggg, factor):
        self.i = i
        self.ggg = ggg

        self.factor = factor
        nodes = factor.nodes_with_type("lambda")
        assert(len(nodes) == 1)
        self.text = " ".join([ts.text for ts in ggg.evidence_for_node(nodes[0])])
        self.type = self.factor.type
        try:
            self.cost = self.ggg.cost_for_factor(self.factor)
            self.prob = math.exp(-self.cost)
        except:
            self.cost = 0
            self.prob = 0


class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self.filter = lambda x: True

        self.setData([])
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_TEXT, 200)
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, entries):
        self._data = entries
        self._unfilteredData = list(self._data)
        self.setFilter(self.filter)
        self.reset()

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
        if col == COL_FACTOR_ID:
            return QVariant(e.factor.id)
        elif col == COL_TYPE:
            return QVariant(e.type)
        elif col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_COST:
            return QVariant("%e" % e.cost)
        elif col == COL_PROB:
            return QVariant("%e" % e.prob)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_FACTOR_ID:
                return QVariant("Factor Id")
            elif section == COL_TYPE:
                return QVariant("Type")
            elif section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_COST:
                return QVariant("Cost")
            elif section == COL_PROB:
                return QVariant("Probability")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        

    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]


    def selectedExamples(self):
        return [self.get(idx.row()).ex
                for idx in self.view.selectedIndexes()]



    def sort(self, col, order):
        if col == COL_FACTOR_ID:
            self._data.sort(key=lambda e: (e.factor.id, e.i))
        elif col == COL_TEXT:
            self._data.sort(key=lambda e: (e.text, e.i))
        elif col == COL_COST:
            self._data.sort(key=lambda e: (e.cost, e.i))
        elif col == COL_PROB:
            self._data.sort(key=lambda e: (e.prob, e.i))
            
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
            
