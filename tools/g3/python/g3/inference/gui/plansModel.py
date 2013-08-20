from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from spatial_features_cxx import math2d_line_length
import math
from qt_utils import Counter
counter = Counter()
COL_IDX = counter.pp()
COL_PROBABILITY = counter.pp()
COL_COST = counter.pp()
COL_BEST = counter.pp()
COL_PATH_LENGTH = counter.pp()
COL_PLAN_STRING = counter.pp()

class Plan:
    @staticmethod
    def from_inference_result(task_planner, raw_plans):
        plans = []
        for i, p in enumerate(raw_plans):
            cost, state, ggg = p
            state_sequence = task_planner.state_sequence(state)
            
            plans.append(Plan(state, ggg, cost, state_sequence, False))
        return plans

    def __init__(self, state, ggg, cost, state_sequence, is_best):
        self.idx = None
        self.state = state
        self.state_sequence = state_sequence
        self.ggg = ggg
        self.cost, i = cost
        self.probability = math.exp(-self.cost)
        self.is_best = is_best
        self.path_length = math2d_line_length(state.getGroundableById(state.getAgentId()).path.points_xy)


        entries = []
        for action, next_state in self.state_sequence:
            entries.append("%s(%s)" % (action.name, 
                                       ", ".join([str(s) for s in action.args])))
        self.plan_string = "(%s,)" % ", ".join(entries)



class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.view = view
        self.view.setModel(self)

        self.view.setColumnWidth(COL_COST, 150)  
        self.view.setColumnWidth(COL_PROBABILITY, 150)  
        self.view.setColumnWidth(COL_BEST, 150)  
        self.view.setColumnWidth(COL_PLAN_STRING, 500)  
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    
    def setData(self, plans):
        for i, p in enumerate(plans):
            assert isinstance(p, Plan), p
            p.idx = i

        self._data = plans
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
        elif col == COL_IDX:
            return QVariant("%d" % e.idx)
        elif col == COL_COST:
            return QVariant("%e" % e.cost)
        elif col == COL_PROBABILITY:
            return QVariant("%e" % e.probability)
        elif col == COL_BEST:
            return QVariant(str(e.is_best))
        elif col == COL_PATH_LENGTH:
            return QVariant("%e" % e.path_length)        
        elif col == COL_PLAN_STRING:
            return QVariant("%s" % e.plan_string)        
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_COST:
                return QVariant("Cost")
            elif section == COL_IDX:
                return QVariant("Idx")
            elif section == COL_PROBABILITY:
                return QVariant("Probability")
            elif section == COL_BEST:
                return QVariant("Selected Plan")
            elif section == COL_PATH_LENGTH:
                return QVariant("Path Length")
            elif section == COL_PLAN_STRING:
                return QVariant("Plan String")
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

    def sort(self, col, order):
        if col == COL_COST:
            self._data.sort(key=lambda e: e.cost)
        elif col == COL_IDX:
            self._data.sort(key=lambda a: e.edx)
        elif col == COL_PROBABILITY:
            self._data.sort(key=lambda e: e.probability)
        elif col == COL_BEST:
            self._data.sort(key=lambda e: e.is_best)
        elif col == COL_PATH_LENGTH:
            self._data.sort(key=lambda e: e.path_length)
        elif col == COL_PLAN_STRING:
            self._data.sort(key=lambda e: e.plan_string)
        else:
            raise ValueError()
        
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
