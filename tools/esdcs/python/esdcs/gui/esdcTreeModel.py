from PyQt4.QtCore import QAbstractItemModel, Qt, QVariant, QModelIndex
from qt_utils import Counter
from esdcs.dataStructures import breadthFirstTraverse

counter = Counter()
COL_VALUE = counter.pp()

class Entry:
    def __init__(self, displayValue, esdc=None):
        self.displayValue = displayValue
        self.esdc = esdc
        self.children = []
        self.parent = None


    def setParent(self, parent, indexCreator):
        self.parent = parent
        self.parent.appendChild(self)
        self.index = indexCreator(len(self.parent.children) - 1, 0, self)

    def appendChild(self, child):
        self.children.append(child)

    def childAt(self, row):
        return self.children[row]

    def rowOfChild(self, child):
        return self.children.index(child)

class Model(QAbstractItemModel):
    def __init__(self, view):
        QAbstractItemModel.__init__(self)        

        self.root = Entry("root", None)
        self.view = view
        self.view.setModel(self)
        self.esdcToEntry = {}
        
    def setData(self, esdcs):

        self.root = Entry("root", None)        
        childEsdcToParentEntry = {}
        self.esdcToEntry = {}
        
        def callback(esdc):
            entry = Entry(str(esdc.asPrettyMap()), esdc)
            self.esdcToEntry[esdc] = entry
            if esdc in childEsdcToParentEntry:
                parentEntry = childEsdcToParentEntry[esdc]
            else:
                parentEntry = self.root

            entry.setParent(parentEntry, self.createIndex)
            
                
            for fieldName in esdc.fieldNames:
                if esdc.childIsListOfWords(fieldName):
                    childEntry = Entry(fieldName + ":" +
                                       " ".join([x.text for x in
                                                 esdc.children(fieldName)]))
                    childEntry.setParent(entry, self.createIndex)
                elif esdc.childIsEsdcs(fieldName):
                    childEntry = childEntry = Entry("%s: esdc" % fieldName)
                    for child in esdc.children(fieldName):
                        childEsdcToParentEntry[child] = childEntry
                    
                    childEntry.setParent(entry, self.createIndex)

        breadthFirstTraverse(esdcs, callback)


        self.reset()                


    def index(self, row, column, parent):
        node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, node.childAt(row))

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root

    
    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        node = self.nodeFromIndex(child)
      
        if node is None:
            return QModelIndex()

        parent = node.parent
          
        if parent is None:
            return QModelIndex()
      
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
      
        assert row != - 1
        return self.createIndex(row, 0, parent)

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node == None:
            return 0
        else:
            return len(node.children)
        

    def  columnCount(self, parent):
        return counter.cnt

    def data(self, index, role):

        
        node = self.nodeFromIndex(index) 

        if role != Qt.DisplayRole:
            return QVariant()            
        col = index.column()
        if col == COL_VALUE:
            return QVariant(node.displayValue)
        else:
            raise ValueError("Bad id: " + `col`)
        
    def selectedData(self):
        return self.view.currentIndex().internalPointer()

    def selectedEsdc(self):
        entry = self.selectedData()
        if entry != None:
            return entry.esdc
        else:
            return None

    
    def selectEsdc(self, esdc):
        try:
            entry = self.esdcToEntry[esdc]
        except KeyError:
            print "key error for", esdc, len(self.esdcToEntry)
            for key, value in self.esdcToEntry.iteritems():
                print "***"
                print key
                print value
            raise


        
        self.view.setCurrentIndex(entry.index)

    
