from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import SIGNAL, QSocketNotifier
from g3.cost_functions.cost_function_crf import CostFnCrf
from pr2.gui import sluEvaluatorGui_ui
import traceback
import basewindow
from optparse import OptionParser
from pr2.slu_evaluator import SluEvaluator
from esdcs.gui import annotationModel, esdcTreeModel

class MainWindow(QMainWindow, sluEvaluatorGui_ui.Ui_MainWindow):
    def __init__(self, sluEvaluator):
        QMainWindow.__init__(self)

        self.setupUi(self)        
        self.sluEvaluator = sluEvaluator

        self.sluEvaluator.setWaitCallback(self.waitCallback)
        
        self.annotationModel = annotationModel.Model(self.annotationTable)
        self.annotationModel.setData(self.sluEvaluator.corpus)



        self.connect(self.annotationTable.selectionModel(),
                     SIGNAL("selectionChanged (QItemSelection,QItemSelection)"),
                     self.selectAnnotation)

        self.socket = QSocketNotifier(self.sluEvaluator.rosbridge.fileno,
                                      QSocketNotifier.Read)

            
        self.connect(self.socket,
                     SIGNAL("activated(int)"),
                     self.checkSocket)

        self.connect(self.executeCommandButton,
                     SIGNAL("clicked()"),
                     self.executeCommand)
        self.is_executing = False

    def waitCallback(self):
        #print "processing events"
        app.processEvents()
        self.updateStatus()

    def checkSocket(self):
        self.sluEvaluator.rosbridge.check()  
        self.updateStatus()
        
    def updateStatus(self):
        #print "updating status", self.sluEvaluator.status
        self.statusEdit.setPlainText(self.sluEvaluator.status)
        self.commandEdit.setPlainText(self.sluEvaluator.command)


    def selectAnnotation(self):
        pass

    def executeCommand(self):
        if not self.is_executing: 
            self.is_executing = True
            for annotation in self.annotationModel.selectedAnnotations():
                self.sluEvaluator.playback_annotation(annotation)
            self.is_executing = False
app = None
def main():
    global app
    app = basewindow.makeApp()

    parser = OptionParser()
    parser = OptionParser()
    parser.add_option("--corpus-filename",dest="corpus_filenames", 
                      help="Corpus  Filename", metavar="FILE", action="append")
    (options, args) = parser.parse_args()

    se = SluEvaluator(options.corpus_filenames)


    wnd = MainWindow(se)

    wnd.show()
    app.exec_()


if __name__=="__main__":
    main()


