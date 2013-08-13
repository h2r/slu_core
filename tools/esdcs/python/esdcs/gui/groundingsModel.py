from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()

COL_TAGS = counter.pp()
COL_TYPE = counter.pp()
COL_LOCATION = counter.pp()
COL_ID = counter.pp()
COL_HASH_STRING = counter.pp()


class Entry:
    def __init__(self, i, grounding):
        self.i = i
        self.grounding = grounding
        self.type = self.grounding.type
        if hasattr(self.grounding, "centroid3d"):
            self.location = "%.3f, %.3f, %.3f" % tuple(self.grounding.centroid3d)
        else:
            self.location = "%.3f, %.3f" % tuple(self.grounding.points_pts[0])
        if hasattr(self.grounding, "tags"):
            self.tags = ", ".join(self.grounding.tags)
        else:
            self.tags = "" 
        if hasattr(self.grounding, "lcmId"):
            self.id = self.grounding.lcmId
        else:
            self.id = None
        self.hash_string = grounding.hash_string

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_TYPE, 200)
        self.view.setColumnWidth(COL_LOCATION, 100)  
        
    def columnCount(self, parent=None):
        return counter.cnt

    def rowCount(self, parent=None):
        return len(self._data)
    def setData(self, groundings):
        self._data = []
        for i, grounding in enumerate(groundings):
            self._data.append(Entry(i, grounding))
        self.reset()
        
    def get(self, i):
        return self._data[i]
    

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_TYPE:
            return QVariant(e.type)
        elif col == COL_LOCATION:
            return QVariant(e.location)
        elif col == COL_TAGS:
            return QVariant(e.tags)        
        elif col == COL_ID:
            return QVariant(e.id)   
        elif col == COL_HASH_STRING:
            return QVariant(e.hash_string)   
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_TYPE:
                return QVariant("Name")
            elif section == COL_LOCATION:
                return QVariant("Location")
            elif section == COL_TAGS:
                return QVariant("Tags")
            elif section == COL_ID:
                return QVariant("Id")
            elif section == COL_HASH_STRING:
                return QVariant("Hash")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
    def selectedGrounding(self):
        entry = self.selectedEntry()
        if entry != None:
            return entry.grounding
        else:
            return None
 


    def selectedEntry(self):
        entries = self.selectedEntries()
        if len(entries) > 0:
            return entries[0]
        else:
            return None


    def selectedEntries(self):
        return [self.get(idx.row()) 
                for idx in self.view.selectionModel().selectedRows()]


    def selectedGroundings(self):
        return [self.get(idx.row()).grounding 
                for idx in self.view.selectionModel().selectedRows()]

    def sort(self, col, order):
        if col == COL_TAGS:
            self._data.sort(key=lambda e: e.tags)
        elif col == COL_TYPE:
            self._data.sort(key=lambda e: e.type)
        elif col == COL_LOCATION:
            self._data.sort(key=lambda e: e.location)
        elif col == COL_ID:
            self._data.sort(key=lambda e: e.id)
        elif col == COL_HASH_STRING:
            self._data.sort(key=lambda e: e.hash_string)
            
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
