from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#Peach Cobbler #1
# where did you get this from?

recipeName = "Peach Cobbler #1"

recipeSource = "http://www.internet.com/recipe.html"

# what is prism from point?
ingredientsList = [("1 (16 oz.) can sliced peaches with syrup", kitchenState.Ingredient(contains=["peaches"], homogenous=True, amount="1 (16 oz.) can",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['peaches']))),
                   ("1 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 c.",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 c. self-rising flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 c.",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("1 c. milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="1 c.",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['milk']))),
                   ("1 stick melted butter (optional)", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 stick",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['butter'])))]

# for time ranges do I want to average?
# what should we do with the vanilla ice cream?
instructionsList = [("Preheat oven to 350 degrees.", "preheat(350)"),
                    ("Pour all ingredients into large bowl.", "pour(peaches), pour(sugar), pour(flour), pour(milk), pour(butter)"),
                    ("Mix until well blended.", "mix()"),
                    ("Pour into ungreased 13x9x2 aluminum pan.", "scrape()"),
                    ("Bake 30-45 minutes or until golden brown", "bake(37.5)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
