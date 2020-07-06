import unittest
from kitchen import kitchenState, annotatedRecipe, planningLanguage, evaluatorGui, recipeManager
from esdcs.groundings import PhysicalObject, Prism
import pickle_util
import cProfile

class TestCase(unittest.TestCase):

        
    def testAnnotatedRecipeName(self):
        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl", "pour(flour), mix(flour)")]
        a = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
        #print "\n", a.recipe
        expectedOutput = "Temp Name\nTemp Source\n1/2 cup flour\nMix flour into mixing bowl\n"
        self.assertEqual(a.recipe_text, expectedOutput)

    def testAnnotatedRecipeIdxToInstruction(self):
        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl", "pour(flour), mix(flour)")]
        a = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
        self.assertEqual(a.idx_to_instruction(0), "Mix flour into mixing bowl")

    def testAnnotatedRecipeIdxToAnnotation(self):
        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl", "pour(flour), mix(flour)")]
        a = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
        self.assertEqual(a.idx_to_annotation(0), "pour(flour), mix(flour)")

    def testPlanningLanguageEmpty(self):
        actualOutput = planningLanguage.PlanningLanguage()
        self.assertNotEqual(actualOutput, None)

    def testPlanningLanguageCompile(self):
        emptyState = kitchenState.KitchenState()
        emptyState.table.contains = [kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour']))]
        planningObject = planningLanguage.PlanningLanguage()
        stateActionPair = planningObject.compileAnnotation("pour(flour)", emptyState)
        print stateActionPair

    def testKitchenEmpty(self):
        output = kitchenState.KitchenState()
        self.assertTrue(len(output.table.contains) == 0)

    def testAnnotatedRecipeCorpusGlob(self):
        output = annotatedRecipe.Corpus("data/")
        print output.recipes
        print output.recipes[0].recipe_text

    def testAnnotatedRecipeIdxToStates(self):
        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl", "pour(flour), mix(flour)")]
        a = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
        print a.idx_to_states(0)
        self.assertEqual(a.idx_to_annotation(0), "pour(flour), mix(flour)")

    def testEqualityEmptyKitchenState(self):
        a = kitchenState.KitchenState()
        b = kitchenState.KitchenState()
        self.assertTrue(a == b)

    def testEqualityFails(self):
        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl", "pour(flour), mix(flour)")]
        a = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList).start_state
        b = kitchenState.KitchenState()
        self.assertFalse(a == b)

    def testEqualitySimpleKitchenState(self):
        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl", "pour(flour), mix(flour)")]
        a = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList).start_state
        b = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList).start_state
        self.assertTrue(a == b)

    def testEvaluatorSimple(self):
        a = evaluatorGui.Evaluator()
        #a.evaluateEndToEnd()

    def dest_viterbi_simple(self):
        model_fname = "kitchenModel_1.5.pck"
        training_set = pickle_util.load("training.pck")
        rm = recipeManager.RecipeManager(model_fname)

        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl.", "pour(flour), mix(flour)"),
                    ("Preheat the oven to 350 F.", "preheat(350)"),
                    ("Bake at 350 F for 30 minutes.", "bake(30)")]
        ar = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
        rm.find_viterbi_plan(ar.instruction_text, ar.start_state)
        
##    def test_wrong_instruction(self):
##        print "\n\n\n---------------"
##        model_fname = "kitchenModel_1.5.pck"
##        training_set = pickle_util.load("training.pck")
##        rm = recipeManager.RecipeManager(model_fname)
##
##        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
##                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
##                                                                                                             lcmId = 5, tags=['Flour']))),
##                   ("1/2 cup putty", kitchenState.Ingredient(contains=["putty"], homogenous=True,
##                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
##                                                                                                             lcmId = 5, tags=['putty'])))]
##        instList = [("Pour the putty into the bowl.", "pour(putty)"),
##                    ("Mix in the flour.", "pour(flour), mix()"),
##                    ("Bake at 350 for 20 minutes.", "preheat(350), bake(20)")]
##        ar = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
##        plan = rm.find_plan(ar.instruction_text, ar.start_state)
##        print plan, "\n--End of entire plan--"
##        for i in plan:
##            for j in i[1]:
##                print j[0]
##            print "-"
##        print "-------------"
##        plan_vit = rm.find_viterbi_plan(ar.instruction_text, ar.start_state)
##        print plan_vit
##        print plan_vit[0][-1][1]

    def test_dijkstra_simple(self):
        model_fname = "kitchenModel_1.5.pck"
        training_set = pickle_util.load("training.pck")
        rm = recipeManager.RecipeManager(model_fname)

        ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                             amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                             lcmId = 5, tags=['Flour'])))]
        instList = [("Mix flour into mixing bowl.", "pour(flour), mix(flour)"),
                    ("Preheat the oven to 350 F.", "preheat(350)"),
                    ("Bake for 30 minutes.", "bake(30)")]
        ar = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
        result = rm.find_dijkstra_plan(ar.instruction_text, ar.start_state)
        print result
        

        

def prism_from_point(x,y,z1,z2):
     return Prism([(x-1, x+1, x+1, x-1), (y-1, y-1, y+1, y+1)], z1, z2)
