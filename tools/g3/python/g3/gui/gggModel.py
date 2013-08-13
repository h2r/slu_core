from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()

COL_TEXT = counter.pp()

class Entry:
    def __init__(self, i, ggg):
        self.i = i
        self.ggg = ggg
        self.text = self.ggg.esdcs.text
        
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
    def setEntries(self, entries):
        self._data = entries
        self.reset()

    def setData(self, gggs):
        self._data = []
        for i, ggg in enumerate(gggs):
            self._data.append(Entry(i, ggg))
        self.reset()
        
    def get(self, i):
        return self._data[i]
    

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_TEXT:
            return QVariant(e.text)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_TEXT:
                return QVariant("Text")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        

    def selectedEntry(self):
        entries = self.selectedEntries()
        if len(entries) == 0:
            return None
        else:
            return entries[0]

    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]

    def selectedGGG(self):
        entry = self.selectedEntry()
        if entry == None:
            return None
        else:
            return entry.ggg
    

