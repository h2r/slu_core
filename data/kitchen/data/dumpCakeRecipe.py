from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

# Dump Cake #1
# where did you get this from?

recipeName = "Dump Cake #1"
recipeSource = "http://www.internet.com/recipe.html"

# what is prism from point?
# how do I deal with the (pecans OR almonds)
ingredientsList = [("1 20 ounce can crushed pineapple", kitchenState.Ingredient(contains=["pineapple"], homogenous=True, amount="1 20 ounce can",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['pineapple']))),
                   ("1 21 ounce can cherry pie filling", kitchenState.Ingredient(contains=["filling"], homogenous=True, amount="1 21 ounce can",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['filling']))),
                   ("1 box dry yellow cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 box",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['cake']))),
                   ("1 cup butter, melted", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['butter']))),
                   ("1-1/4 cups coconut", kitchenState.Ingredient(contains=["coconut"], homogenous=True, amount="1-1/4 cups",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['coconut']))),
                   ("1 cup chopped pecans or sliced almonds", kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['pecans'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("Preheat oven to 350 degrees.", "preheat(350)"),
                    ("Layer ingredients as listed in a lightly greased 9 x 11 pan.", "pour(pineapple), pour(filling), pour(cake_mix), pour(butter), pour(coconut), pour(nuts)"),
                    ("Bake for 1 hour.", "scrape(), bake(60)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
