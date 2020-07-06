from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#19
#http://www.food.com/recipe/impossible-peanut-butter-cookies-15411
#
#1 cup peanut butter (your choice, smooth or chunky)
#1 cup granulated sugar
#1 large egg
#
#1 Mix peanut butter, sugar, and egg together until smooth.
#2 Drop by teaspoon onto cookie sheet two inches apart.  
#3 Press with fork; press again in opposite direction
#4 Bake 10 to 12 minutes at 350 degrees Fahrenheit.
#5 Do not brown; do not over bake.

recipeName = "Impossible Peanut Butter Cookies"
recipeSource = "http://www.food.com/recipe/impossible-peanut-butter-cookies-15411"

#replace None with Physical Objects
ingredientsList = [("1 cup peanut butter (your choice, smooth or chunky)", kitchenState.Ingredient(contains=["peanut_butter"], homogenous=True, amount="1 cup peanut butter",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['peanutbutter']))),
                   ("1 cup granulated sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 large egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs'])))]

instructionsList = [("1 Mix peanut butter, sugar, and eggs together until smooth.", "pour(peanut_butter), pour(sugar), pour(eggs), mix()"),
                    ("2 Drop by teaspoon onto cookie sheet two inches apart.", "scrape()"),
                    ("3 Press with form; press gain in opposite direction.", "noop()"),
                    ("4 Bake 10 to 12 minutes at 350 degrees Fahrenheit", "preheat(350), bake(10)"),
                    ("5 Do not brown; do not over bake.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

