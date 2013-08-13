from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant
from math import exp
from qt_utils import Counter
from confusion_matrix import ConfusionMatrix
counter = Counter()

COL_ESDC_TYPE = counter.pp()
COL_TEXT = counter.pp()
COL_ASSIGNMENT_ID = counter.pp()
COL_LOG_PROBABILITY = counter.pp()
COL_PROBABILITY = counter.pp()
COL_ACTUAL_CLASS = counter.pp()
COL_PREDICTED_CLASS = counter.pp()
COL_TP = counter.pp()
COL_FP = counter.pp()
COL_TN = counter.pp()
COL_FN = counter.pp()
COL_CORRECT = counter.pp()


class Entry:
    def __init__(self, i, crf, obs, threshold=0.5):
        self.i = i
        self.crf = crf
        obs = self.crf.dataset.convert_observation(obs)
        self.obs = obs
        self.threshold = threshold
        self.node = self.obs.node
        self.annotation = self.obs.annotation
        if obs.sdcs != None:
            self.esdc = obs.sdcs[0]
            self.esdcs = [self.esdc]
            self.esdcType = self.esdc.type
            self.text = self.esdc.text
        else:
            self.esdc = None
            self.esdcs = None
            self.esdcType = None
            self.text = None


        self.actualClass = obs.label
        if obs.annotation != None:
            self.assignmentId = obs.annotation.id
        else:
            self.assignmentId = None
            

        self.log_probability = crf.log_probability(obs, phi_value=True)
        self.probability = exp(self.log_probability)
        if self.probability > self.threshold:
            self.predictedClass = True
        else:
            self.predictedClass = False
        self.correct = self.actualClass == self.predictedClass        
        self.tp = self.actualClass and self.predictedClass
        self.fp = not self.actualClass and self.predictedClass
        self.tn = not self.actualClass and not self.predictedClass
        self.fn = self.actualClass and not self.predictedClass

class Model(QAbstractTableModel):
    def __init__(self, view):
        QAbstractTableModel.__init__(self)
        self._data = []
        self.sort_col = None
        self.order = None
        self.filter = lambda x: True
        self.view = view
        self.view.setModel(self)
        self.view.setColumnWidth(COL_TEXT, 200)
        
    def columnCount(self, parent):
        return counter.cnt

    def rowCount(self, parent):
        return len(self._data)
    def setData(self, crf, examples):
        self._data = []
        for i, example in enumerate(examples):
            self._data.append(Entry(i, crf, example))

        self._unfilteredData = list(self._data)
        self.setFilter(self.filter)
        if self.sort_col != None:
            self.sort(self.sort_col, self.order)
        self.reset()

    def setFilter(self, filterFunction):
        self.filter = filterFunction
        self._data = [e for e in self._unfilteredData if filterFunction(e)]
        self.reset()
        
    def get(self, i):
        return self._data[i]

    def selectedEntry(self):
        entry = self.get(self.view.currentIndex().row())
        return entry

    def selectedEntries(self):
        return [self.get(e.row()) 
                for e in self.view.selectionModel().selectedRows()]

    
    def confusionMatrix(self):
        entries = self.selectedEntries()
        return ConfusionMatrix(len([e for e in entries if e.tp]),
                               len([e for e in entries if e.fp]),
                               len([e for e in entries if e.tn]),
                               len([e for e in entries if e.fn]))
                                           
    
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
        elif col == COL_LOG_PROBABILITY:
            return QVariant("%e" % e.log_probability)
        elif col == COL_PROBABILITY:
            return QVariant("%e" % e.probability)
        elif col == COL_ASSIGNMENT_ID:
            return QVariant(str(e.assignmentId))
        elif col == COL_ACTUAL_CLASS:
            return QVariant(e.actualClass)
        elif col == COL_PREDICTED_CLASS:
            return QVariant(e.predictedClass)
        elif col == COL_CORRECT:
            return QVariant(e.correct)
        elif col == COL_TP:
            return QVariant(e.tp)
        elif col == COL_FP:
            return QVariant(e.fp)
        elif col == COL_TN:
            return QVariant(e.tn)
        elif col == COL_FN:
            return QVariant(e.fn)
        elif col == COL_ESDC_TYPE:
            return QVariant(e.esdcType)                                
        else:
            raise ValueError("Bad id: %s" % col)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == COL_TEXT:
                return QVariant("Text")
            elif section == COL_LOG_PROBABILITY:
                return QVariant("Log Probability")
            elif section == COL_PROBABILITY:
                return QVariant("Probability")
            elif section == COL_ACTUAL_CLASS:
                return QVariant("Actual Class")
            elif section == COL_ASSIGNMENT_ID:
                return QVariant("Assignment ID")
            elif section == COL_PREDICTED_CLASS:
                return QVariant("Predicted Class")
            elif section == COL_CORRECT:
                return QVariant("Correct")
            elif section == COL_TP:
                return QVariant("TP")
            elif section == COL_FP:
                return QVariant("FP")
            elif section == COL_TN:
                return QVariant("TN")
            elif section == COL_FN:
                return QVariant("FN")
            elif section == COL_ESDC_TYPE:
                return QVariant("Type")                                    
            else:
                raise ValueError("Bad id: %s" % section)
        else:
            return QVariant()
        
        
    def sort(self, col, order):
        self.sort_col = col
        self.order = order
        if col == COL_TEXT:
            self._data.sort(key=lambda e: e.text)
        elif col == COL_LOG_PROBABILITY:
            self._data.sort(key=lambda e: e.log_probability)
        elif col == COL_PROBABILITY:
            self._data.sort(key=lambda e: e.probability)
        elif col == COL_ASSIGNMENT_ID:
            self._data.sort(key=lambda e: e.assignmentId)
        elif col == COL_ACTUAL_CLASS:
            self._data.sort(key=lambda e: e.actualClass)
        elif col == COL_PREDICTED_CLASS:
            self._data.sort(key=lambda e: e.predictedClass)
        elif col == COL_CORRECT:
            self._data.sort(key=lambda e: e.correct)
        elif col == COL_TP:
            self._data.sort(key=lambda e: e.tp)
        elif col == COL_FP:
            self._data.sort(key=lambda e: e.fp)
        elif col == COL_TN:
            self._data.sort(key=lambda e: e.tn)
        elif col == COL_FN:
            self._data.sort(key=lambda e: e.fn)
        elif col == COL_ESDC_TYPE:
            self._data.sort(key=lambda e: e.esdcType)
            
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.reset()
            
