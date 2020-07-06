
import basewindow
from kitchen.gui import recipeBrowser_ui
from PyQt4.QtGui import QMainWindow
from kitchen.gui import instructionModel
from kitchen.recipeManager import RecipeManager
from PyQt4.QtCore import SIGNAL
from qt_window_manager import WindowManager
from g3.inference.gui import costFunctionBrowser
from kitchen import planningLanguage

class MainWindow(QMainWindow, recipeBrowser_ui.Ui_MainWindow):
    def __init__(self, recipe_manager):
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.recipe_manager = recipe_manager
        self.instructionModel = instructionModel.Model(self.instructionTable)

        self.windowManager = WindowManager(self.windowsMenu)
        self.recipe_manager = RecipeManager("kitchenModel_1.5.pck")
        self.costFunctionBrowser = costFunctionBrowser.MainWindow([0, 10, 0, 10],
                                                                  self.recipe_manager.task_planner)
        self.costFunctionBrowser.save_state_tree = True
        self.costFunctionBrowser.allow_null_action = False

        self.windowManager.addWindow(self.costFunctionBrowser)


        self.connect(self.instructionTable.selectionModel(),
                     SIGNAL("selectionChanged ( QItemSelection, QItemSelection )"),
                     self.selectInstruction)   
        

        self.connect(self.inferPlanButton,
                     SIGNAL("clicked()"),
                     self.inferPlan)

        self.connect(self.sendToRobotButton,
                     SIGNAL("clicked()"),
                     self.sendToRobot)

        self.connect(self.sendInstructionToCfbButton,
                     SIGNAL("clicked()"),
                     self.sendInstructionToCfb)

        self.start_state = None

    def selectInstruction(self):
        print "select instruction"

    def sendInstructionToCfb(self):
        entry = self.instructionModel.selectedEntry()
        esdc, ggg = self.recipe_manager.make_ggg_for_instruction(entry.text)
        self.costFunctionBrowser.gggs = [ggg]
        self.costFunctionBrowser.esdcs = [esdc]
        
        self.costFunctionBrowser.followCommand(entry.text, 
                                               state=entry.start_state,
                                               esdcs=[esdc])

        for plan in self.costFunctionBrowser.plansList:
            result = self.recipe_manager.sequence(plan)
            string = planningLanguage.decompile(result)
            print "planning language", string
        



    def sendToRobot(self):

        ingredients_str = "\n".join(i.ros_str() for i in self.start_state.ingredients)
            
            
        plan_string = "\n".join([e.annotation 
                                 for e in self.instructionModel.entries])
        print "send to robot."
        print "ingredients"
        print ingredients_str
        print "plan"
        print plan_string
        self.sendToRos(ingredients_str + '\n' + plan_string)

    def sendToRos(self, string):
        import roslib
        roslib.load_manifest('bakebot')
        from services.bakebot_recipe_service import BakebotClient
        status = BakebotClient.execute_recipe(string, debug=True)
        print "ros status", status


    def inferPlan(self):
        print "follow command"
        recipe_text = str(self.recipeTextEdit.toPlainText())
        sequence = self.recipe_manager.find_plan(recipe_text, 
                                                 self.start_state)
        entries = []
        for i, (instruction, states, cost) in enumerate(sequence):
            if i == 0:
                start_state = self.start_state
            else:
                start_state = sequence[i - 1][1][-1][1]
            annotation = planningLanguage.decompile(states)
            
            entry = instructionModel.Entry(i, instruction.text, annotation,
                                           start_state, cost)
            entries.append(entry)
        self.instructionModel.setData(entries)
        
        
    def load(self, annotated_recipe):
        self.recipeTextEdit.setPlainText(annotated_recipe.instruction_text)
        self.recipeTitleLabel.setText(annotated_recipe.name)
        self.start_state = annotated_recipe.start_state
        self.annotated_recipe = annotated_recipe
        

