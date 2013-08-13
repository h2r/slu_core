from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
import math

from qt_utils import Counter
counter = Counter()
COL_IDX = counter.pp()
COL_FEATURE_NAME = counter.pp()
COL_VALUE = counter.pp()
COL_WEIGHT = counter.pp()
COL_WEIGHT_ABS = counter.pp()

class Entry:
    def __init__(self, i, feature_name, value, weight):
        self.i = i
        self.feature_name = str(feature_name)
        self.value = value
        self.weight = weight
        self.weight_abs = math.fabs(weight)
        
class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.sort_col = None
        self.order = None
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_FEATURE_NAME, 300)
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, lccrf, obs):
        entries = []
        weightMap = lccrf.get_weights(obs)
        for i, (fname, weight) in enumerate(weightMap.iteritems()):
            if weight == None:
                weight = 0
            entries.append(Entry(i, fname, obs.features_obs[fname], weight))
        self.setEntries(entries)

    def setEntries(self, entries):
        self._data = list(entries)
        if self.sort_col != None:
            self.sort(self.sort_col, self.sort_order)
        self.reset()
        

    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()
        
    def get(self, i):
        return self._data[i]

    def selectedData(self):
        entry = self.get(self.view.currentIndex().row())
        return entry
    
    def selectedAnnotation(self):
        entry = self.get(self.view.currentIndex().row())
        return entry.annotation

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_FEATURE_NAME:
            return QVariant(e.feature_name)
        elif col == COL_IDX:
            return QVariant(e.i)
        elif col == COL_WEIGHT:
            return QVariant("%e" % e.weight)
        elif col == COL_VALUE:
            return QVariant("%e" % e.value)
        elif col == COL_WEIGHT_ABS:
            return QVariant("%e" % e.weight_abs)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_FEATURE_NAME:
                return QVariant("Feature Name")
            elif section == COL_IDX:
                return QVariant("Index")
            elif section == COL_WEIGHT:
                return QVariant("Weight")
            elif section == COL_VALUE:
                return QVariant("Value")
            elif section == COL_WEIGHT_ABS:
                return QVariant("Abs. Weight")

            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
        
    def sort(self, col, order):
        self.sort_col = col
        self.sort_order = order
        if col == COL_FEATURE_NAME:
            self._data.sort(key=lambda e: e.feature_name)
        elif col == COL_IDX:
            self._data.sort(key=lambda e: e.i)
        elif col == COL_WEIGHT:
            self._data.sort(key=lambda e: e.weight)
        elif col == COL_WEIGHT_ABS:
            self._data.sort(key=lambda e: e.weight_abs)
        elif col == COL_VALUE:
            self._data.sort(key=lambda e: e.value)
            
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
