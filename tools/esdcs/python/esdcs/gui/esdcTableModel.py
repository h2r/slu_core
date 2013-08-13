from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()
COL_TYPE = counter.pp()
COL_R = counter.pp()
COL_STR = counter.pp()
COL_TEXT = counter.pp()

class Entry:
    def __init__(self, i, esdc):
        self.i = i
        self.text = esdc.text
        self.entireText = esdc.entireText
        self.type = esdc.type
        self.str = str(esdc)
        self.esdc = esdc
        self.r = " ".join(w.text for w in esdc.r)

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
    def setData(self, esdcs):
        self._data = []
        for i, esdc in enumerate(esdcs):
            self._data.append(Entry(i, esdc))
        self.reset()
        
    def get(self, i):
        return self._data[i]

    def selectedData(self):
        entry = self.get(self.view.currentIndex().row())
        return entry
    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_TYPE:
            return QVariant(e.type)
        elif col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_STR:
            return QVariant(e.str)
        elif col == COL_R:
            return QVariant(e.r)   
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_TYPE:
                return QVariant("Type")
            elif section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_STR:
                return QVariant("Str")
            elif section == COL_R:
                return QVariant("R")            
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
    def selectedEsdc(self):
        if  self.view.currentIndex().row() != -1:
            entry = self.get(self.view.currentIndex().row())
            return entry.esdc
        else:
            return None
