import basewindow
import pickle_util
from kitchen.gui import recipeEvaluationBrowser_ui
from kitchen import planningLanguage, evaluatorGui
from PyQt4.QtGui import QMainWindow
from kitchen.gui import recipeModel, instructionModel, recipeBrowser, inferredInstructionModel
from kitchen.annotatedRecipe import Corpus
from kitchen.recipeManager import RecipeManager
from PyQt4.QtCore import SIGNAL, Qt
from qt_window_manager import WindowManager
from g3.inference.gui import costFunctionBrowser

class MainWindow(QMainWindow, recipeEvaluationBrowser_ui.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.recipeModel = recipeModel.Model(self.recipeTable)
        self.instructionModel = instructionModel.Model(self.instructionTable)
        self.inferredInstructionModel =inferredInstructionModel.Model(self.inferredTable)

        #self.modeManager = WindowManager(self.modeMenu)

        self.recipe_manager = RecipeManager("kitchenModel_1.5.pck")

##        self.recipeBrowser = recipeBrowser.MainWindow(self.recipe_manager)
##        self.recipeBrowser.show()
##        self.windowManager.addWindow(self.recipeBrowser)
        
        self.costFunctionBrowser = costFunctionBrowser.MainWindow([0, 10, 0, 10],
                                                                  self.recipe_manager.task_planner)
        self.costFunctionBrowser.save_state_tree = True
        self.costFunctionBrowser.allow_null_action = False


        #self.windowManager.addWindow(self.costFunctionBrowser)

        self.ev = evaluatorGui.Evaluator()
        #TODO: Set title based on mode
        self.setWindowTitle("Recipe Evaluation Browser - Instruction Level Mode")
        
        

        self.connect(self.recipeTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectRecipe)

        self.connect(self.instructionTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectInstruction) 
        

##        self.connect(self.sendInstructionButton,
##                     SIGNAL("clicked()"),
##                     self.sendInstruction)
##
##        self.connect(self.sendRecipeButton,
##                     SIGNAL("clicked()"),
##                     self.sendRecipe)
        

    def sendRecipe(self):
        ar = self.recipeModel.selectedEntry()
        self.recipeBrowser.load(ar)

    def selectInstruction(self):
        ar = self.recipeModel.selectedEntry()

    def sendInstruction(self):
        entry = self.instructionModel.selectedEntry()
        recipe = self.recipeModel.selectedEntry()


        esdc, ggg = self.recipe_manager.make_ggg_for_instruction(entry.text)
        self.costFunctionBrowser.gggs = [ggg]
        self.costFunctionBrowser.esdcs = [esdc]
        start_state = recipe.idx_to_start_state(entry.idx)
        print 'start', start_state
        self.costFunctionBrowser.followCommand(entry.text, 
                                               state=start_state,
                                               esdcs=[esdc])
        
        for plan in self.costFunctionBrowser.plansList[0:10]:
            result = self.recipe_manager.sequence(plan)
            string = planningLanguage.decompile(result)
            print "planning language", string
        
        

    def selectRecipe(self):
        ar = self.recipeModel.selectedEntry()
        self.recipeTextEdit.setPlainText(ar.recipe_text)
        self.instructionModel.setRecipe(ar)
        self.instructionTable.selectRow(0)
        self.inferredInstructionModel.setRecipe(ar)

        
    def load(self, fname):


        self.recipeTable.selectRow(0)
        self.instructionTable.selectRow(0)

        training_set = pickle_util.load("training.pck")
        print "training", training_set
        recipes = Corpus(fname, training_set)

        self.recipeModel.setData(recipes)
        self.recipeTable.sortByColumn(recipeModel.COL_IS_TRAINING_SET, Qt.AscendingOrder)
        self.recipeTable.selectRow(0)


def main():
    basewindow.batch_mode = True
    app = basewindow.makeApp()
    
    wnd = MainWindow()
    wnd.load("data/")
    wnd.show()
    app.exec_()

if __name__=="__main__":
    main()

