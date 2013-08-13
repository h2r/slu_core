
from PyQt4.QtCore import *
from datetime import datetime
from counter import Counter

def isChecked(box):
    return box.checkState() == Qt.Checked



class CheckboxDrawer:
    def __init__(self, wnd, checkBox):
        self.wnd = wnd
        self.checkBox = checkBox
        self.wnd.connect(self.checkBox, SIGNAL("stateChanged(int)"),
                         self.updateState)
        self.plots = []

    def clearPlots(self):
        for p in self.plots:
            p.remove() 
        self.plots = []

    def doDraw(self, axes):
        raise ValueError("Implement me.")
    
    def draw(self):
        self.plots += self.doDraw(self.wnd.figure.gca())



    def updateState(self, state=None):
        if state == None:
            state = self.checkBox.checkState()
        if state == Qt.Checked:
            self.draw()
        elif state == Qt.Unchecked:
            self.clearPlots()
            self.wnd.mpl_draw()
        elif state == Qt.PartiallyChecked:
            pass
        else:
            raise ValueError("Unepxected state: " + `state`)




def toRow(idx):
    if (isinstance(idx, QModelIndex)):
        return idx.row()
    else:
        return idx

def toInt(variant):
    if variant == None:
        return None
    else:
        return variant.toInt()[0]
def currentBoxData(box):
    return convertVariant(box.itemData(box.currentIndex()))

def toDateTime(qdatetime):
    if isinstance(qdatetime, QVariant):
        qdatetime = qdatetime.toDateTime()
    return datetime.fromtimestamp(qdatetime.toTime_t())


"""
Convert variant to a natural python type:
"""
def convertVariant(q):
    if not isinstance(q, QVariant):
        return q
    elif q.type() == QVariant.Bool:
        return q.toBool()
    elif q.type() == QVariant.String:
        return str(q.toString())
    elif q.type() == QVariant.Int:
        return q.toInt()[0]
    elif q.type() == QVariant.Invalid:
        return None
    else:
        raise ValueError("Can't convert " + `q` + " class " + `q.__class__` + " type: " + `q.type()`)
        
class QtException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
