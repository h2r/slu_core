from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant

import numpy as na
from qt_utils import Counter
counter = Counter()

COL_NAME = counter.pp()
COL_VALUE = counter.pp()

class Entry:
    def __init__(self, name, value):
        self.name = name
        self.value = value

        if na.isnan(value):
            self.sortable_value = -na.inf
        else:
            self.sortable_value = value

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_NAME, 400)
        self.view.setColumnWidth(COL_VALUE, 200)  
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, nameToValue):
        self._data = []
        for i, (name, value) in enumerate(nameToValue.iteritems()):
            self._data.append(Entry(name, value))
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
        if col == COL_NAME:
            return QVariant(e.name)
        elif col == COL_VALUE:
            return QVariant(e.value)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_NAME:
                return QVariant("Name")
            elif section == COL_VALUE:
                return QVariant("Value")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()


    def sort(self, col, order):
        if col == COL_NAME:
            self._data.sort(key=lambda e: e.name)
        elif col == COL_VALUE:
            self._data.sort(key=lambda e: e.sortable_value)
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
            
        
