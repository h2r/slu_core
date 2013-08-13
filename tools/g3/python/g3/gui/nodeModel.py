from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant


from qt_utils import Counter
counter = Counter()

COL_IDX = counter.pp()
COL_ID = counter.pp()
COL_TYPE = counter.pp()
COL_TEXT = counter.pp()
COL_GROUNDINGS = counter.pp()

class Entry:
    def __init__(self, i, node, ggg=None):
        self.i = i
        self.node = node
        self.id = str(self.node.id)
        self.type = self.node.type
        if ggg == None:
            self.ggg = self.node.graph.ggg
        else:
            self.ggg = ggg
        esdc = self.ggg.node_to_top_esdc(node)
        self.text = esdc.text if esdc != None else None
        evidence = self.ggg.evidence_for_node(self.node)
        if node.is_gamma:
            self.groundings = ",".join([str(g.tags) for g in evidence])
        else:
            self.groundings = str(evidence)
        
class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_ID, 70)
        self.view.setColumnWidth(COL_TYPE, 200)  
        self.view.setColumnWidth(COL_TEXT, 200)  
        
    def columnCount(self, parent):
        return counter.cnt
    @property
    def entries(self):
        return self._data
    def rowCount(self, parent):
        return len(self._data)
    def setData(self, nodes, ggg=None):
        self._data = []
        for i, example in enumerate(nodes):
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
        elif col == COL_IDX:
            return QVariant(e.i)
        elif col == COL_TYPE:
            return QVariant(e.type)
        elif col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_GROUNDINGS:
            return QVariant(e.groundings)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_ID:
                return QVariant("Id")
            elif section == COL_IDX:
                return QVariant("Idx")
            elif section == COL_TYPE:
                return QVariant("Type")
            elif section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_GROUNDINGS:
                return QVariant("Groundings")
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
 
    def selectNode(self, node):
        idx = [(i, e) for (i, e) in enumerate(self._data) 
               if e.node == node][0][0]
        self.view.selectRow(idx)
 


    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]


    def selectedNodes(self):
        return [self.get(idx.row()).node
                for idx in self.view.selectedIndexes()]

