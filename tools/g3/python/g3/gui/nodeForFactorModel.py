from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()

COL_ID = counter.pp()
COL_TYPE = counter.pp()
COL_LINK_TYPE = counter.pp()
COL_EVIDENCE = counter.pp()

class Entry:
    def __init__(self, i, ggg, factor, node):
        self.i = i
        self.ggg = ggg
        self.node = node
        self.factor = factor
        self.id = str(self.node.id)
        self.type = self.node.type
        self.link_type = factor.link_for_node(node)
        ev = ggg.evidence_for_node(node)
        if isinstance(ev, list):
            self.evidence = " ".join(str(x) for x in ev)
        else:
            self.evidence = str(ev)
class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_ID, 100)
        self.view.setColumnWidth(COL_TYPE, 100)  
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, nodes_and_factors):
        self._data = []
        for i, (ggg, factor, node) in enumerate(nodes_and_factors):
            self._data.append(Entry(i, ggg, factor, node))
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
        elif col == COL_LINK_TYPE:
            return QVariant(e.link_type)
        elif col == COL_EVIDENCE:
            return QVariant(e.evidence)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_ID:
                return QVariant("Id")
            elif section == COL_TYPE:
                return QVariant("Type")
            elif section == COL_LINK_TYPE:
                return QVariant("Link Type")
            elif section == COL_EVIDENCE:
                return QVariant("Evidence")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
    def selectedNode(self):
        entry = self.selectedEntry()
        if entry != None:
            return entry.node
        else:
            return None
 


    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]


    def selectedNodes(self):
        return [self.get(idx.row()).node
                for idx in self.view.selectedIndexes()]

    def selectNode(self, node):
        idx = [(i, e) for (i, e) in enumerate(self._data) 
               if e.node == node][0][0]
        self.view.selectRow(idx)
    @property
    def entries(self):
        return self._data
