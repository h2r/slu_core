from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#23
#Simple Fudge Brownies
#http://www.food.com/recipe/simple-fudge-brownies-141647
#
#2 cup butter
#1 cup sugar
#1 teaspoon vanilla
#2 eggs
#6 tablespoons cocoa
#1/2 cup all-purpose flour
#
#Cream first 3 ingredients with a mixer.
#Blend in cocoa, flour and eggs.
#Bake at 350F for 25 to 30 minutes.
#Frost with your favorite icing or mix icing sugar, butter and cocoa.
#Cut into 15-20 small squares (it's pretty rich!).

recipeName = "Simple Fudge Brownies"
recipeSource = "http://www.food.com/recipe/simple-fudge-brownies-141647"

ingredientsList = [("2 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 cup sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 teaspoon vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("6 tablespoons cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="6 tablespoons",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cocoa']))),
                   ("1/2 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour'])))]

#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Cream first 3 ingredients with a mixer.", "pour(butter), pour(sugar), pour(vanilla_extract), mix()"),
                    ("Blend in cocoa, flour and eggs.", "pour(cocoa_powder), mix(), pour(flour), mix(), pour(eggs), mix()"),
                    ("Bake at 350F for 25 to 30 minutes.", "preheat(350), scrape(), bake(25)"), 
                    ("Frost with your favorite icing or mix icing sugar, butter and cocoa.", "frost()"),
                    ("Cut into 15-20 small squares (its pretty rich!)", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

