from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt4.QtGui import QApplication

from qt_utils import Counter
counter = Counter()
COL_IS_TRAINING_SET = counter.pp()
COL_NAME = counter.pp()
COL_SOURCE = counter.pp()
COL_INGREDIENTS_TEXT = counter.pp()
COL_INSTRUCTION_TEXT = counter.pp()


class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self.filter = lambda x: True

        self.setData([])
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_INSTRUCTION_TEXT, 300)


        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
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
        if col == COL_NAME:
            return QVariant(e.name)
        elif col == COL_SOURCE:
            return QVariant(e.source)
        elif col == COL_IS_TRAINING_SET:
            return QVariant(e.is_training_set)
        elif col == COL_INGREDIENTS_TEXT:
            return QVariant(e.ingredients_text)
        elif col == COL_INSTRUCTION_TEXT:
            return QVariant(e.instruction_text)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_NAME:
                return QVariant("Name")
            elif section == COL_SOURCE:
                return QVariant("Source")
            elif section == COL_INGREDIENTS_TEXT:
                return QVariant("Ingredients Text")
            elif section == COL_IS_TRAINING_SET:
                return QVariant("In Training Set?")
            elif section == COL_INSTRUCTION_TEXT:
                return QVariant("Instruction Text")
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
        if col == COL_NAME:
            self._data.sort(key=lambda e: e.name)
        elif col == COL_SOURCE:
            self._data.sort(key=lambda e: (e.source, e.name))
        elif col == COL_INGREDIENTS_TEXT:
            self._data.sort(key=lambda e: (e.ingredients_text, e.name))
        elif col == COL_IS_TRAINING_SET:
            self._data.sort(key=lambda e: (e.is_training_set, e.name))
        elif col == COL_INSTRUCTION_TEXT:
            self._data.sort(key=lambda e: (e.instruction_text, e.name))
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
            
