from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()

COL_ID = counter.pp()
COL_TYPE = counter.pp()
COL_TEXT = counter.pp()
COL_HAS_UNGROUNDED_NODES = counter.pp()

class Entry:
    def __init__(self, i, factor, ggg):
        self.i = i
        self.factor = factor
        self.ggg = ggg
        self.id = str(self.factor.id)
        self.type = self.factor.type
        self.text = self.ggg.factor_to_esdc(self.factor).text
        self.has_ungrounded_nodes = str(self.ggg.has_ungrounded_nodes(self.factor))
        
class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_ID, 100)
        self.view.setColumnWidth(COL_TYPE, 100)  
        self.view.setColumnWidth(COL_TEXT, 200)  
        self.view.setColumnWidth(COL_HAS_UNGROUNDED_NODES, 130)  
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setEntries(self, entries):
        self._data = entries
        self.reset()

    def setData(self, factors, ggg):
        self._data = []
        for i, example in enumerate(factors):
            self._data.append(Entry(i, example, ggg))
        self.reset()
        
    def get(self, i):
        return self._data[i]
    

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_ID:
            return QVariant(e.id)
        elif col == COL_TYPE:
            return QVariant(e.type)
        elif col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_HAS_UNGROUNDED_NODES:
            return QVariant(e.has_ungrounded_nodes)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_ID:
                return QVariant("Id")
            elif section == COL_TYPE:
                return QVariant("Type")
            elif section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_HAS_UNGROUNDED_NODES:
                return QVariant("Ungrounded Nodes")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
    def selectedFactor(self):
        entry = self.selectedEntry()
        if entry != None:
            return entry.factor
        else:
            return None

    def selectFactor(self, factor):
        idx = [(i, e) for (i, e) in enumerate(self._data) 
               if e.factor == factor][0][0]
        self.view.selectRow(idx)
 


    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]


    def selectedFactors(self):
        return [self.get(idx.row()).factor
                for idx in self.view.selectedIndexes()]

