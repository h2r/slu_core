import glob
from kitchen import kitchenState, planningLanguage

class AnnotatedRecipe():
    #The initial state is a kitchenState with the ingredients layed out,
    #a list of ingredients as a string, and a list of Ingredient objects
    
    #There is also a list of annotated instructions that contains
    #instrunction-annotation pairs in a tuple.

    
    def __init__(self, recipeName, recipeSource, ingredientsList, instructionsList):
        """
        This constructor takes as params:
        recipeName - The name of the recipe as a string
        recipeSource - The source of the recipe
        ingredientsList, a list of tuples containing a string representation
           of that ingredient and a ingredient object, e.g.
           [("1/2 cup flour", Ingredient("flour", "1/2 cup"))]
        instructionsList - a list of tuples containing a string of a single
           'instruction' and its corresponding annotation (collection of
           actions) as a string (for now).
           e.g. [("Mix flour and eggs", "Pour(flour), Pour(eggs), Mix()")]
        """
        self.name = recipeName
        self.source = recipeSource
        self.is_training_set = None
        self.start_state = kitchenState.KitchenState()
        #build kitchen state
        kitchenTable = []
        for i in ingredientsList:
            kitchenTable.append(i[1])
        self.start_state.table.contains = kitchenTable
        
        self.ingredients = ingredientsList
        self.instructions = instructionsList

        self.pl = planningLanguage.PlanningLanguage()
 
        self.states = []
        start_state = self.start_state
        for i in self.instructions:
            results = self.pl.compileAnnotation(i[1], start_state)
            self.states.append(results)
            start_state = results[-1][1]

        self.num_instructions = len(self.instructions)


        

    @property
    def recipe_text(self):
        """ Returns a string of the complete recipe (including
        ingredients list)"""

        wholeRecipe = self.name + "\n" + self.source + "\n"
        for i in self.ingredients:
            wholeRecipe = wholeRecipe + i[0] + "\n"
        for j in self.instructions:
            wholeRecipe = wholeRecipe + j[0] + "\n"
        return wholeRecipe

    @property
    def instruction_text(self):
        result = ""
        for j in self.instructions:
            result += j[0] + "\n"
        return result

    @property
    def ingredients_text(self):
        result = ""
        for i in self.ingredients:
            result += i[0] + "\n"
        return result
        
    
    def idx_to_instruction(self, idx):
        """
        Returns the instruction at the given index as a string,
        or None if index out of bounds
        """
        if (idx < 0 or idx > len(self.instructions)-1):
            raise ValueError("Invalid Idx: " + `idx`)
        return self.instructions[idx][0]

    
    def idx_to_annotation(self, idx):
        """
        Returns the annotations that correspond to
        the instruction at the given index (as a string for now)
        or None is idx is out of bounds
        """
        if (idx < 0 or idx > len(self.instructions)-1):
            raise ValueError("Invalid Idx: " + `idx`)
        return self.instructions[idx][1]

    def idx_to_states(self, idx):
        if (idx < 0 or idx > len(self.states)-1):
            raise ValueError("Invalid Idx: " + `idx`)
        return self.states[idx]

    def idx_to_start_state(self, idx):
        if idx == 0:
            return self.start_state
        else:
            states = self.states[idx - 1]
            return states[-1][1]

class Corpus():
    def __init__(self, dirname="data/", training_set=None):
        self.dirname = dirname
        self.fileList = glob.glob(dirname+"*.py")
        self.recipes = self._evalFiles()

        if training_set != None:
            training_names = set()
            for obs in training_set.observations:
                training_names.add(obs.id.split("_")[0])

            for recipe in self.recipes:
                if recipe.name in training_names:
                    recipe.is_training_set = True
                else:
                    recipe.is_training_set = False

        else:
            training_names = None




        names = set()
        for recipe in self.recipes:
            if recipe.name in names:
                raise ValueError("Repated name: " + recipe.name)
            names.add(recipe.name)
            

    def __len__(self):
        return len(self.recipes)

    def __iter__(self):
        return iter(self.recipes)

    def __getitem__(self, idx):
        return self.recipes[idx]
        
    def _evalFiles(self):
        annotatedRecipes = []
        for i in self.fileList:
            try:
                tempDict = dict()
                execfile(i, tempDict)
                assert("annotatedRecipeObject" in tempDict.keys())
                annotatedRecipes.append(tempDict["annotatedRecipeObject"])
            except:
                print "Exception on", i
                raise
        return annotatedRecipes
        
