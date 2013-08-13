from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()
COL_IDX = counter.pp()
COL_ASSIGNMENT_ID = counter.pp()
COL_COMMAND = counter.pp()
COL_CONTEXT_SIZE = counter.pp()
COL_CONTEXT_OBJECTS_SIZE = counter.pp()
COL_CONTEXT_PLACES_SIZE = counter.pp()

class Entry:
    def __init__(self, i, annotation):
        self.i = i
        self.annotation = annotation
        self.assignmentId = annotation.assignmentId
        self.entireText = annotation.entireText
        self.esdcs = annotation.esdcs
        self.context_size = len(self.annotation.context.groundings)
        self.context_objects_size = len(self.annotation.context.objects)
        self.context_places_size = len(self.annotation.context.places)

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_ASSIGNMENT_ID, 35)
        self.view.setColumnWidth(COL_COMMAND, 500)  

        
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent=None):
        return len(self._data)
    def setData(self, data, path=None):
        self._data = []
        for i, annotation in enumerate(data):
            self._data.append(Entry(i, annotation))
        self._unfilteredData = list(self._data)
        self.reset()
    def get(self, i):
        return self._data[i]

    def selectAnnotation(self, annotation):
        for i, entry in enumerate(self._data):
            if entry.annotation == annotation:
                self.view.selectRow(i)

    def selectedData(self):
        entry = self.get(self.view.currentIndex().row())
        return entry
    
    def selectedAnnotation(self):
        entry = self.get(self.view.currentIndex().row())
        return entry.annotation


    def selectedEntries(self):
        return [self.get(i.row())
                for i in self.view.selectionModel().selectedRows()]

    def selectedAnnotations(self):
        return [e.annotation for e in self.selectedEntries()]

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_ASSIGNMENT_ID:
            return QVariant(e.assignmentId)
        elif col == COL_IDX:
            return QVariant(e.i)
        elif col == COL_COMMAND:
            return QVariant(e.entireText)
        elif col == COL_CONTEXT_SIZE:
            return QVariant(e.context_size)
        elif col == COL_CONTEXT_OBJECTS_SIZE:
            return QVariant(e.context_objects_size)
        elif col == COL_CONTEXT_PLACES_SIZE:
            return QVariant(e.context_places_size)

        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_ASSIGNMENT_ID:
                return QVariant("Assignment ID")
            elif section == COL_IDX:
                return QVariant("Index")
            elif section == COL_COMMAND:
                return QVariant("Command")
            elif section == COL_CONTEXT_SIZE:
                return QVariant("Context Size")
            elif section == COL_CONTEXT_OBJECTS_SIZE:
                return QVariant("Context Objects")
            elif section == COL_CONTEXT_PLACES_SIZE:
                return QVariant("Context Places")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()


    def sort(self, col, order):
        if col == COL_ASSIGNMENT_ID:
            self._data.sort(key=lambda e: e.assignmentId)
        elif col == COL_IDX:
            self._data.sort(key=lambda e: e.i)
        elif col == COL_COMMAND:
            self._data.sort(key=lambda e: e.entireText)
        elif col == COL_CONTEXT_SIZE:
            self._data.sort(key=lambda e: e.context_size)
        elif col == COL_CONTEXT_OBJECTS_SIZE:
            self._data.sort(key=lambda e: e.context_objects_size)
        elif col == COL_CONTEXT_PLACES_SIZE:
            self._data.sort(key=lambda e: e.context_places_size)


            
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
