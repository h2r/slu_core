from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt4.QtGui import QApplication

from qt_utils import Counter
counter = Counter()
COL_IDX = counter.pp()
COL_NODE_ID = counter.pp()
COL_ASSIGNMENT_ID = counter.pp()
COL_NODE_TEXT = counter.pp()
COL_ENTIRE_TEXT = counter.pp()

COL_ENTROPY = counter.pp()
COL_BEST_NODE_PROB = counter.pp()
COL_BEST_NODE_COST = counter.pp()

COL_BEST_PROB = counter.pp()
COL_BEST_COST = counter.pp()
COL_CORRECT = counter.pp()
COL_IS_NULL_NODE = counter.pp()
COL_IS_ORIGINAL_COMMAND = counter.pp()
COL_INFERRED_TAGS = counter.pp()
COL_LABELED_TAGS = counter.pp()

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self.filter = lambda x: True

        self.setData([])
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_NODE_TEXT, 300)

    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, entries):
        for i, e in enumerate(entries):
            e.i = i
        self._data = entries
        self._unfilteredData = list(self._data)
        self.setFilter(self.filter)
        self.reset()

    @property
    def entries(self):
        return self._data
    def allData(self):
        return self._data

    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()


    def get(self, i):
        return self._data[i]



    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()
        if col == COL_NODE_ID:
            return QVariant(e.node.id)
        elif col == COL_IDX:
            return QVariant(e.i)
        elif col == COL_ASSIGNMENT_ID:
            return QVariant(e.annotation_id)
        elif col == COL_NODE_TEXT:
            return QVariant(e.text)
        elif col == COL_ENTIRE_TEXT:
            return QVariant(e.entire_text)
        elif col == COL_ENTROPY:
            if e.entropy != None:
                return QVariant("%e" % e.entropy)
            else:
                return QVariant("")
        elif col == COL_BEST_COST:
            return QVariant("%e" % e.best_cost)
        elif col == COL_BEST_PROB:
            return QVariant("%e" % e.best_prob)
        elif col == COL_BEST_NODE_COST:
            return QVariant("%e" % e.best_node_cost)
        elif col == COL_BEST_NODE_PROB:
            return QVariant("%e" % e.best_node_prob)
        elif col == COL_CORRECT:
            return QVariant(e.correct)
        elif col == COL_IS_NULL_NODE:
            return QVariant(e.is_null_node)
        elif col == COL_IS_ORIGINAL_COMMAND:
            return QVariant(e.is_original_command)
        elif col == COL_INFERRED_TAGS:
            return QVariant(e.inferred_tags)
        elif col == COL_LABELED_TAGS:
            return QVariant(e.labeled_tags)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_NODE_ID:
                return QVariant("Node Id")
            elif section == COL_IDX:
                return QVariant("Index")
            elif section == COL_ASSIGNMENT_ID:
                return QVariant("Assignment Id")
            elif section == COL_NODE_TEXT:
                return QVariant("Node Text")
            elif section == COL_ENTIRE_TEXT:
                return QVariant("Entire Text")
            elif section == COL_ENTROPY:
                return QVariant("Entropy")
            elif section == COL_BEST_COST:
                return QVariant("Best Cost")
            elif section == COL_BEST_PROB:
                return QVariant("Best Prob")
            elif section == COL_BEST_NODE_COST:
                return QVariant("Best Node Cost")
            elif section == COL_BEST_NODE_PROB:
                return QVariant("Best Node Prob")
            elif section == COL_CORRECT:
                return QVariant("Correct")
            elif section == COL_IS_NULL_NODE:
                return QVariant("Is Null Node")
            elif section == COL_IS_ORIGINAL_COMMAND:
                return QVariant("Is Original Command")
            elif section == COL_INFERRED_TAGS:
                return QVariant("Inferred Tags")
            elif section == COL_LABELED_TAGS:
                return QVariant("Labeled Tags")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()


    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(i.row())
                for i in self.view.selectionModel().selectedRows()]


    def selectedExamples(self):
        return [self.get(idx.row()).ex
                for idx in self.view.selectedIndexes()]



    def sort(self, col, order):
        if col == COL_NODE_ID:
            self._data.sort(key=lambda e: (e.node.id, e.id))
        elif col == COL_IDX:
            self._data.sort(key=lambda e: (e.i, e.id))
        elif col == COL_ASSIGNMENT_ID:
            self._data.sort(key=lambda e: (e.annotation.id, e.id))
        elif col == COL_NODE_TEXT:
            self._data.sort(key=lambda e: (e.text, e.id))
        elif col == COL_ENTIRE_TEXT:
            self._data.sort(key=lambda e: (e.entire_text, e.id))
        elif col == COL_ENTROPY:
            self._data.sort(key=lambda e: (e.entropy, e.id))
        elif col == COL_BEST_COST:
            self._data.sort(key=lambda e: (e.best_cost, e.id))
        elif col == COL_BEST_PROB:
            self._data.sort(key=lambda e: (e.best_prob, e.id))
        elif col == COL_BEST_NODE_COST:
            self._data.sort(key=lambda e: (e.best_node_cost, e.id))
        elif col == COL_BEST_NODE_PROB:
            self._data.sort(key=lambda e: (e.best_node_prob, e.id))
        elif col == COL_CORRECT:
            self._data.sort(key=lambda e: (e.correct, e.id))
        elif col == COL_IS_NULL_NODE:
            self._data.sort(key=lambda e: (e.is_null_node, e.id))
        elif col == COL_IS_ORIGINAL_COMMAND:
            self._data.sort(key=lambda e: (e.is_original_command, e.id))

        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()

    def sendToClipboard(self):
        result_str = ""
        for row_idx in self.view.selectionModel().selectedRows():
            for col_idx in range(0, counter.cnt):
                idx = self.index(row_idx.row(), col_idx)
                result_str += str(self.data(idx).toString()) + "\t"

            result_str += "\n"
        print "sending", result_str
        QApplication.clipboard().setText(result_str)

