from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#15
#Cake Mix Cookies
#http://www.food.com/recipe/cake-mix-cookies-15559
#
#1 (18 1/4 ounce) box chocolate cake mix
#1/2 cup vegetable oil
#2 eggs
#2 cups chocolate chips
#1/2 cup chopped nuts (optional)
#
#Combine cake mix, oil and eggs in a bowl and mix well.
#Stir in chips and nuts, if using.
#Drop by teaspoons on ungreased cookie sheet and bake at 350 degrees for 8-10 minutes.
#Upon removing from oven, let the cookies stand on sheet for two minutes, then cool on racks.
recipeName = "Cake Mix Cookies"
recipeSource = "http://www.food.com/recipe/cake-mix-cookies-15559"

#replace None with Physical Objects
ingredientsList = [("1 (18 1/4 ounce) box chocolate cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18 1/4 ounce) box",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("1/2 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['oil']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("2 cups chocholate chips", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="2 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['chocolatechips']))),
                   ("1/2 cup chopped nuts (optional)", kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['nuts'])))]

instructionsList = [("Combine cake mix, oil and eggs in a bowl and mix well.", "pour(cake_mix), pour(oil), pour(eggs), mix()"),
                    ("Stir in chips and nuts, if using.", "pour(chocolate_chips), mix(), pour(nuts), mix()"),
                    ("Drop by teaspoons on ungreased cookie sheet and bake at 350 degrees for 8-10 minutes.", "scrape(), preheat(350), bake(8)"),
                    ("Upon removing from oven, let the cookies stand on sheet for two minutes, then cool on racks", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

