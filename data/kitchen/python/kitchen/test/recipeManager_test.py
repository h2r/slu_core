import unittest
from kitchen.recipeManager import RecipeManager
from kitchen.annotatedRecipe import Corpus

class TestCase(unittest.TestCase):

    def testRecipeManager(self):
        manager = RecipeManager("kitchenModel_1.5.pck")
        recipes = Corpus("data/")
        recipe = recipes[0]
        try:
            seq = manager.find_plan(recipe.instruction_text, recipe.start_state)
            for instruction, state_seq, cost in seq:
                for action, state in state_seq:
                    print "action", action.name
        except:
            print "problem on", recipe.name
            raise
        
        
