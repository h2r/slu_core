from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#16
#Easy Cake Mix Cookies
#http://www.food.com/recipe/easy-cake-mix-cookies-5287
#
#1 (18 ounce) box package cake mix (any flavor)
#1/3 cup vegetable oil
#2 eggs
#
#1. Combine cake mix, oil and eggs.  Mix Well.
#2. Bake at 350F for about 10 minutes.
#3. Remove from oven and let cool on pan for several minutes before removing to rack to finish cooling.

recipeName = "Easy Cake Mix Cookies"
recipeSource = "http://www.food.com/recipe/easy-cake-mix-cookies-5287"

#replace None with Physical Objects
ingredientsList = [("1 (18 1/4 ounce) box chocolate cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18 1/4 ounce) box",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("1/3 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1/3 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['oil']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs'])))]

instructionsList = [("Combine cake mix, oil and eggs.", "pour(cake_mix), pour(oil), pour(eggs), mix()"),
                    ("Mix well.", "mix()"),
                    ("Bake at 350F for about 10 minutes.", "scrape(), preheat(350), bake(10)"),
                    ("Remove from oven and let cool on pan for several minutes before removing to rack to finish cooling.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

