from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Super Easy Salad"

recipeSource = "http://allrecipes.com/recipe/super-easy-salad/"

#replace None with Physical Objects
ingredientsList = [("2 medium cucumbers, quartered and thinly sliced", kitchenState.Ingredient(contains=["cucumbers"], homogenous=True, amount="2",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cucumbers']))),
                   ("1 medium onion, chopped", kitchenState.Ingredient(contains=["onions"], homogenous=True, amount="1",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['onion']))),
                   ("1 bunch radishes, thinly sliced", kitchenState.Ingredient(contains=["radishes"], homogenous=True, amount="1 bunch",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['radishes']))),
                   ("3/4 cup mayonnaise", kitchenState.Ingredient(contains=["mayo"], homogenous=True, amount="3/4 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['mayo']))),
                   ("1/2 cup Ranch dressing", kitchenState.Ingredient(contains=["ranch"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['ranch']))),
                   ("salt to taste", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="to taste",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['salt']))),
                   ("ground black pepper to taste", kitchenState.Ingredient(contains=["pepper"], homogenous=True, amount="to taste",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['pepper'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("In a bowl, toss together the cucumbers, onion, and radishes.", "pour(cucumbers), pour(onions), pour(radishes), mix()"),
                    ("In a separate bowl, mix the mayonnaise and Ranch dressing.", "pour(mayo), pour(ranch), mix()"),
                    ("Season with salt and pepper.", "pour(salt), pour(pepper)"),
                    ("Mix into the vegetables.", "mix()"),
                    ("Chill in the refrigerator at least 2 hours before serving.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

