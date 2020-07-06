from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#9
#Easy Dump Cake
#(http://allrecipes.com/recipe/easy-dump-cake/detail.aspx)
#
#1 (18.25 ounce) package yellow cake mix
#1 (5.9 ounce) package instant chocolate pudding mix 
#4 eggs, beaten
#2/3 cup vegetable oil
#2/3 cup white sugar
#1/3 cup water
#1 (8 ounce) container sour cream
#1 cup semisweet chocolate chips
#
#1. Preheat oven to 350 degrees F (175 degrees C). Grease and flour a Bundt pan.
#2. In a bowl, mix the yellow cake mix, pudding mix, eggs, vegetable oil, sugar, and water.  Gently fold in the sour cream and chocolate chips.  Pour batter into the prpared Bundt pan.
#3. Bake in the preheated oven for 55 minutes.  Cool in pan for 10 minutes before transferring to cooling racks.

recipeName = "Easy Dump Cake"
recipeSource = "http://allrecipes.com/recipe/easy-dump-cake/detail.aspx"

#TODO chekc the prism locations
ingredientsList = [("1 (18.25 ounce) package yellow cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18.25 ounce) package",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("1 (5.9 ounce) package instant chocolate pudding mix", kitchenState.Ingredient(contains=["pudding"], homogenous=True, amount="1 (5.9 ounce) package",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['pudding']))),
                   ("4 eggs, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['eggs']))),
                   ("2/3 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="2/3 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['oil']))),
                   ("2/3 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2/3 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['sugar']))),
                   ("1/3 cup water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="1/3 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['water']))),
                   ("1 (8 ounce) container sour cream", kitchenState.Ingredient(contains=["sour_cream"], homogenous=True, amount="1 (8 ounce) container",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['sourcream']))),
                   ("1 cup semisweet chocolate chips", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=8, tags=['chocolatechips'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 350 degrees. (175 degrees C)", "preheat(350)"),
                    ("Grease and flour a Bundt pan.", "grease()"),
                    ("2. In a bowl, mix the yellow cake mix, pudding mix, eggs, vegetable oil, sugar, and water.", "pour(cake_mix), pour(pudding), pour(eggs), pour(sugar), pour(water), mix()"),
                    ("3. Bake for in a preheated oven for 55 minutes.", "scrape(), bake(55)"),
                    ("Cool in pan for 10 minutes before transferring to cooling racks", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
