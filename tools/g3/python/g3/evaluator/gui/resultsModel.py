from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt4.QtGui import QApplication
from g3.evaluator.evaluate_nodes import compute_node_results
from g3.evaluator.gui.resultsEntry import Entry

from qt_utils import Counter


counter = Counter()
COL_IDX = counter.pp()
COL_ESDC_TYPE = counter.pp()
COL_TEXT = counter.pp()
COL_PROBABILITY = counter.pp()
COL_COST = counter.pp()
COL_EVENT_ENTROPY = counter.pp()
COL_ESDC_NUM = counter.pp()
COL_RANDOM = counter.pp()
COL_ASSIGNMENT_ID = counter.pp()


class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self.filter = lambda x: True
        self.setData([])
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_TEXT, 200)

    def compute_node_entropies(self):
        for entry in self._data:
            event_node_results = compute_node_results([entry],
                                                  entropy_metric="metric2",
                                                  include_events=True,
                                                  include_objects=False)
            assert len(event_node_results) == 1, "I expect only one event node result, got: %d" % len(event_node_results)
            entry.event_node_result = event_node_results[0]

    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)

    def loadResultsFile(self, resultsFile):
        self.setData(Entry.entries_from_results_file(resultsFile))

    def loadResults(self, result_entry):
        self.setData(result_entry.results_as_entries())

    def setData(self, data):
        self._data = data
        self._unfilteredData = list(self._data)
        self.setFilter(self.filter)
        self.compute_node_entropies()
        self.reset()

    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()

    def get(self, i):
        return self._data[i]

    def selectedData(self):
        return [self.get(e.row())
                for e in self.view.selectionModel().selectedRows()]

    def selectedAnnotation(self):
        entry = self.get(self.view.currentIndex().row())
        return entry.annotation


    def data(self, idx, role=Qt.DisplayRole):
        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()
        if col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_IDX:
            return QVariant("%d" % idx.row())
        elif col == COL_PROBABILITY:
            return QVariant("%e" % e.probability)
        elif col == COL_COST:
            return QVariant("%e" % e.cost)
        elif col == COL_ESDC_TYPE:
            return QVariant(e.esdcType)
        elif col == COL_ESDC_NUM:
            return QVariant("%d" % e.esdcNum)
        elif col == COL_RANDOM:
            return QVariant("%d" % e.random)
        elif col == COL_ASSIGNMENT_ID:
            return QVariant(e.assignmentId)
        elif col == COL_EVENT_ENTROPY:
            return QVariant("%e" % e.event_node_result.entropy)
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_IDX:
                return QVariant("Index")
            elif section == COL_PROBABILITY:
                return QVariant("Probability")
            elif section == COL_COST:
                return QVariant("Cost")
            elif section == COL_ESDC_TYPE:
                return QVariant("Type")
            elif section == COL_ESDC_NUM:
                return QVariant("Esdc Index")
            elif section == COL_RANDOM:
                return QVariant("Random")
            elif section == COL_ASSIGNMENT_ID:
                return QVariant("Assignment Id")
            elif section == COL_EVENT_ENTROPY:
                return QVariant("Event Node Entropy")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()

    def sort(self, col, order):
        if col == COL_TEXT:
            self._data.sort(key=lambda e: e.text)
        elif col == COL_PROBABILITY:
            self._data.sort(key=lambda e: e.probability)
        elif col == COL_COST:
            self._data.sort(key=lambda e: e.cost)
        elif col == COL_COST:
            self._data.sort(key=lambda e: e.cost)
        elif col == COL_ESDC_TYPE:
            self._data.sort(key=lambda e: e.esdcType)
        elif col == COL_ESDC_NUM:
            self._data.sort(key=lambda e: e.esdcNum)
        elif col == COL_RANDOM:
            self._data.sort(key=lambda e: e.random)
        elif col == COL_ASSIGNMENT_ID:
            self._data.sort(key=lambda e: e.assignmentId)
        elif col == COL_EVENT_ENTROPY:
            self._data.sort(key=lambda e: e.event_node_result.entropy)

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

