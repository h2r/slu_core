from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from qt_utils import Counter
import math
counter = Counter()
COL_TEXT = counter.pp()
COL_ESDC = counter.pp()
COL_ALL_GROUNDINGS = counter.pp()
COL_GROUNDINGS = counter.pp()
COL_PHI_VALUE = counter.pp()
COL_PROBABILITY = counter.pp()
COL_COST = counter.pp()
COL_RECOMPUTED_PROBABILITY = counter.pp()
COL_RECOMPUTED_COST = counter.pp()
COL_OVERALL_COST = counter.pp()
COL_OVERALL_PROB = counter.pp()

class Entry:
    def __init__(self, i, candidate, lccrf):
        self.i = i
        self.candidate = candidate
        self.factor = candidate.factor
        self.ggg = candidate.ggg
        self.states = candidate.states

        self.esdc = self.ggg.factor_to_esdc(self.factor)
        self.text = self.esdc.text
        self.esdc_str = str(self.esdc)
        self.cost = candidate.cost
        self.probability = candidate.probability
        self.overall_cost = candidate.overall_cost
        self.overall_prob = candidate.overall_prob

        self.all_groundings = self.ggg.groundings
        self.all_groundings_str = str([str(g) for g in self.all_groundings])

        self.groundings = self.ggg.groundings_for_factor(self.factor)
        self.groundings_str = str([str(g) for g in self.groundings])
        self.phi_value = candidate.phi_value


        self.recomputed_cost = - lccrf.lccrf.log_probability(self.candidate.dobs, self.phi_value)
        self.recomputed_prob = math.exp(-self.recomputed_cost)

        
class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_TEXT, 200)
        self.view.setColumnWidth(COL_ESDC, 150)
        self.view.setColumnWidth(COL_PROBABILITY, 100)
        self.view.setColumnWidth(COL_COST, 100)
        self.view.setColumnWidth(COL_RECOMPUTED_PROBABILITY, 100)
        self.view.setColumnWidth(COL_RECOMPUTED_COST, 100)
        self.view.setColumnWidth(COL_OVERALL_COST, 100)
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, candidates, lccrf):
        self._data = [Entry(i, c, lccrf) for i, c in enumerate(candidates)]
        self.reset()

    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()
        
    def get(self, i):
        return self._data[i]

    def selectedEntries(self):
        return [self.get(idx.row()) for idx in self.view.selectedIndexes()]

    def selectedEntry(self):
        entries = self.selectedEntries()
        if len(entries) == 0:
            return None
        else:
            return entries[0]

    
    def selectedAnnotation(self):
        entry = self.get(self.view.currentIndex().row())
        return entry.annotation

    
    def data(self, idx, role=Qt.DisplayRole):

        e = self.get(idx.row())
        col = idx.column()
        if role != Qt.DisplayRole:
            return QVariant()            
        if col == COL_ESDC:
            return QVariant(e.esdc_str)
        elif col == COL_TEXT:
            return QVariant(e.text)
        elif col == COL_ALL_GROUNDINGS:
            return QVariant(e.all_groundings_str)
        elif col == COL_GROUNDINGS:
            return QVariant(e.groundings_str)
        elif col == COL_PROBABILITY:
            #return QVariant("%e" % e.probability)
            return QVariant("%.60f" % e.probability)
        elif col == COL_COST:
            return QVariant("%e" % e.cost)
        elif col == COL_RECOMPUTED_PROBABILITY:
            return QVariant("%e" % e.recomputed_prob)
        elif col == COL_RECOMPUTED_COST:
            return QVariant("%e" % e.recomputed_cost)
        elif col == COL_OVERALL_COST:
            return QVariant("%e" % e.overall_cost)
        elif col == COL_OVERALL_PROB:
            return QVariant("%e" % e.overall_prob)
        elif col == COL_PHI_VALUE:
            return QVariant(str(e.phi_value))
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_ESDC:
                return QVariant("ESDC")
            elif section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_ALL_GROUNDINGS:
                return QVariant("All Groundings")
            elif section == COL_GROUNDINGS:
                return QVariant("Groundings")
            elif section == COL_PROBABILITY:
                return QVariant("Esdc Prob")
            elif section == COL_COST:
                return QVariant("Esdc Cost")
            elif section == COL_RECOMPUTED_PROBABILITY:
                return QVariant("Recomputed Prob")
            elif section == COL_RECOMPUTED_COST:
                return QVariant("Recomputed Cost")
            elif section == COL_OVERALL_COST:
                return QVariant("Overall Cost")
            elif section == COL_OVERALL_PROB:
                return QVariant("Overall Prob")
            elif section == COL_PHI_VALUE:
                return QVariant("Phi Value")
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
        
    def sort(self, col, order):
        if col == COL_ESDC:
            self._data.sort(key=lambda e: e.esdc_str)
        elif col == COL_ALL_GROUNDINGS:
            self._data.sort(key=lambda e: e.all_groundings_str)
        elif col == COL_GROUNDINGS:
            self._data.sort(key=lambda e: e.groundings_str)
        elif col == COL_COST:
            self._data.sort(key=lambda e: e.cost)
        elif col == COL_PROBABILITY:
            self._data.sort(key=lambda e: e.probability)
        elif col == COL_RECOMPUTED_COST:
            self._data.sort(key=lambda e: e.recomputed_cost)
        elif col == COL_RECOMPUTED_PROBABILITY:
            self._data.sort(key=lambda e: e.recomputed_prob)
        elif col == COL_OVERALL_COST:
            self._data.sort(key=lambda e: e.overall_cost)
        elif col == COL_OVERALL_PROB:
            self._data.sort(key=lambda e: e.overall_prob)
        elif col == COL_PHI_VALUE:
            self._data.sort(key=lambda e: e.phi_value)
        elif col == COL_TEXT:
            self._data.sort(key=lambda e: e.text)
            
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
            
