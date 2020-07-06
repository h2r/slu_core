from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Cucumber Slices with Dill"

recipeSource = "http://allrecipes.com/Recipe/Cucumber-Slices-With-Dill/Detail.aspx"

#replace None with Physical Objects
ingredientsList = [("4 large cucumbers, sliced", kitchenState.Ingredient(contains=["cucumbers"], homogenous=True, amount="4",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cucumbers']))),
                   ("1 onion, thinly sliced", kitchenState.Ingredient(contains=["onions"], homogenous=True, amount="1",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['onions']))),
                   ("1 tablespoon dried dill weed", kitchenState.Ingredient(contains=["dill_weed"], homogenous=True, amount="1 tablespoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['dillweed']))),
                   ("1 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['sugar']))),
                   ("1/2 cup white vinegar", kitchenState.Ingredient(contains=["vinegar"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['vinegar']))),
                   ("1/2 cup water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['water']))),
                   ("1 teaspoon salt ", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['salt'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("In a large serving bowl, combine cucumbers, onions and dill.", "pour(cucumbers), pour(onions), pour(dill_weed), mix()"),
                    ("In a medium size bowl combine sugar, vinegar, water and salt.", "pour(sugar), pour(vinegar), pour(water), pour(salt), mix()"),
                    ("stir until the sugar dissolves.", "mix()"),
                    ("Pour the liquid mixture over the cucumber mixture.", "noop()"),
                    ("Cover and refrigerate at least 2 hours before serving (the longer this dish marinates the tastier it is).", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

