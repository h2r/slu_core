from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#27 
#Chocolate Fudge Cookies
#http://allrecipes.com/recipe/chocolate-fudge-cookies/detail.aspx
#
#1 (18.25 ounce) package devil's food cake mix 
#2 eggs
#1/2 cup vegetable oil
#1 cup semi-sweet chocolate chips
#
#1. Preheat oven to 350 degrees F (175 degrees C). Grease cookie sheets.
#2. In a medium bowl, stir together the cake mix, eggs and oil until well blended. Fold
#in the chocolate chips. Roll the dough into walnut sized balls. Place the cookies 2
#inches apart on the cookie sheet.
#3. Bake for 8 to 10 minutes in the preheated oven. Allow cookies to cool on baking
#sheet for 5 minutes before removing to a wire rack to cool completely.

recipeName = "Chocolate Fudge Cookies"
recipeSource = "http://allrecipes.com/recipe/chocolate-fudge-cookies/detail.aspx"

#TODO need to fix the prisms
ingredientsList = [("1 (18.25 ounce) package devil's food cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18.25 ounce) package",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=2, tags=['eggs']))),
                   ("1/2 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=3, tags=['oil']))),
                   ("1 cup semi-sweet chocholate chips", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['chocolatechips'])))]

instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Grease cookie sheets.", "grease()"),
                    ("2. In a medium bowl, stir together the cake mix, eggs and oil until well blended.", "pour(cake_mix), pour(eggs), pour(oil), mix()"),
                    ("Fold in the chocolate chips.", "pour(chocolate_chips), mix()"),
                    ("Roll the dough into walnut sized balls.", "scrape()"),
                    ("Place the cookies 2 inches apart on the cookie sheet.", "noop()"),
                    ("Bake for 8 to 10 minutes in the preheated oven.", "bake(8)"),
                    ("Allow cookies to cool on baking sheet for 5 minutes before removing to a wire rack to cool completely.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

