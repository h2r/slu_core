from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#26 
#Cake Mix Cookies VII
#http://allrecipes.com/recipe/cake-mix-cookies-vii/detail.aspx
#
#1 (18.25 ounce) package yellow cake mix 
#1 teaspoon baking powder
#2 eggs
#1/2 cup vegetable oil
#1 cup semisweet chocolate chips
#
#1. Preheat oven to 350 degrees F (175 degrees C).
#2. In a medium bowl, stir together the cake mix and baking powder. Add eggs and oil,
#then mix until well blended. Stir in chocolate chips, or your choice of additions.
#Drop by rounded spoonfuls onto cookie sheets.
#3. Bake for 8 to 10 minutes in the preheated oven. 

recipeName = "Cake Mix Cookies VII"
recipeSource = "http://allrecipes.com/recipe/cake-mix-cookies-vii/detail.aspx"

#TODO need to fix the prisms
ingredientsList = [("1 (18.25 ounce) package yellow cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18.25 ounce) package",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("1 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 teaspoon",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['bakingpowder']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("1/2 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=2, tags=['oil']))),
                   ("1 cup semisweet chocholate chips", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['chocolatechips'])))]

instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("2. In a medium bowl, stir together the cake mix and baking powder.", "pour(cake_mix), pour(baking_powder), mix()"),
                    ("Add eggs and oil, then mix until well blended.", "pour(eggs), pour(oil), mix()"),
                    ("Stir in chocolate chips, or your choice of additions..", "pour(chocolate_chips), mix()"),
                    ("Drop by rounded spoonfuls onto cookie sheets.", "scrape()"),
                    ("Bake for 8 to 10 minutes in the preheated oven.", "bake(8)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

