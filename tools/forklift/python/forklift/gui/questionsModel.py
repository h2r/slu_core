from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from qt_utils import Counter
from numpy import sign

counter = Counter()
COL_COST = counter.pp()
OBJ_TAGS = counter.pp()
ESDC_TAGS = counter.pp()
TO_HUMAN = counter.pp()
#COL_PATH_LENGTH = counter.pp()


class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_COST, 150)  
        self.view.setColumnWidth(OBJ_TAGS, 150) 
        self.view.setColumnWidth(ESDC_TAGS, 150) 
        self.view.setColumnWidth(TO_HUMAN, 800) 
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    
    def setData(self, qns_cache):
        
        def compare_n3s(entry1,entry2):
            return int(sign(entry2[1] - entry1[1]))
        
        
        
        self._data = sorted(qns_cache,compare_n3s)
        #for i, (cost, groundings) in enumerate(plans):
        #self._data.append(Entry(cost, groundings))

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
        elif col == COL_COST:
            return QVariant("%e" % e[1])  #question cost
        elif col == OBJ_TAGS:
            qn = e[0]
            desc = qn.obj_description(qn)
            return QVariant(desc) 
        elif col == ESDC_TAGS:
            qn = e[0]
            desc = qn.esdc_description(qn)
            return QVariant(desc)   
        elif col == TO_HUMAN:
            qn = e[0]
            desc = qn.to_human(qn)
            return QVariant(desc)       
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_COST:
                return QVariant("Question Reward")
            if section == OBJ_TAGS:
                return QVariant("Object Tags")
            if section == ESDC_TAGS:
                return QVariant("ESDC Tags")     
            if section == TO_HUMAN:
                return QVariant("Human understandable question")           
#            elif section == COL_PATH_LENGTH:
#                return QVariant("Path Length")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
    def selectedAnnotation(self):
        if  self.view.currentIndex().row() != -1:
            entry = self.get(self.view.currentIndex().row())
            return entry[2]
        else:
            return None
