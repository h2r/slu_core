from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

# Yellow Cake #1
# where did you get this from?

recipeName = "Yellow Cake #1"

recipeSource = "http://www.internet.com/recipe.html"

# what is prism from point?
ingredientsList = [("2/3 c. shortening", kitchenState.Ingredient(contains=["shortening"], homogenous=True, amount="2/3 c.",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['shortening']))),
                   ("1 1/4 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/4 c.",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("2 1/4 c. flour (self-rising)", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 1/4 c.",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("1 c. milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="1 c.",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['milk']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['eggs']))),
                   ("1 tsp. vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 tsp.",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['vanilla'])))]

# how do I represent grease and flour?
instructionsList = [("Preheat oven to 350 degrees.", "preheat(350)"),
                    ("Grease and flour 2 round pans or a 9 x 13 inch pan.", "grease(pan)"),
                    ("Add all ingredients.", "pour(shortening), pour(sugar), pour(flour), pour(milk), pour(eggs), pour(vanilla_extract)"),
                    ("Pour in pans and bake in oven for 30 minutes.", "scrape(), bake(30)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
