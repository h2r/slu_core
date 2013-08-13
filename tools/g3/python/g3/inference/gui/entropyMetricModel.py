from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from qt_utils import Counter
counter = Counter()
COL_NAME = counter.pp()
COL_PRETTY_NAME = counter.pp()
COL_ENTROPY = counter.pp()

class Entry:
    def __init__(self, metric, node_results):
        self.metric = metric
        self.node_results = node_results
        self.entropy = self.metric.entropy_for_node_results(node_results)
        self.name = self.metric.name
        self.pretty_name = self.metric.pretty_name
    

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_NAME, 150)  

        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    
    def setData(self, metrics, node_results):
        self._data = [Entry(m, node_results) for m in metrics]
        self._data.sort(key=lambda e: e.metric.name)
        self.reset()
        
    def get(self, i):
        if i == -1:
            return None
        else:
            return self._data[i]

    def selectedData(self):
        entry = self.get(self.view.currentIndex().row())
        return entry
    
    def data(self, idx, role=Qt.DisplayRole):
        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_NAME:
            return QVariant(e.name)
        elif col == COL_PRETTY_NAME:
            return QVariant(e.pretty_name)
        elif col == COL_ENTROPY:
            return QVariant("%e" % e.entropy) 
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_NAME:
                return QVariant("Name")
            elif section == COL_PRETTY_NAME:
                return QVariant("Pretty Name")
            elif section == COL_ENTROPY:
                return QVariant("Entropy")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
    def selectedPlan(self):
        if  self.view.currentIndex().row() != -1:
            entry = self.get(self.view.currentIndex().row())
            return (entry.state, entry.ggg)
        else:
            return None
    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]

    def selectedEntry(self):
        entries = self.selectedEntries()
        if len(entries) == 0:
            return None
        else:
            return entries[0]

