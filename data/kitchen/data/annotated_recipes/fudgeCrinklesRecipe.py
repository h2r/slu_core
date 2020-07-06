from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#18
#Fudge Crinkles
#http://www.food.com/recipe/fudge-crinkles-a-great-4-ingredient-cake-mix-cookie-32614
#
#1 (18 1/4 ounce) box devil's food cake mix (Betty Crocker Super Moist suggested)
#1/2 cup vegetable oil
#2 large eggs
#confectioners sugar or granulated sugar, for rolling
#
#1 preheat oven to 350
#2 Stir (by hand) dry cake mix, oil and eggs in a large bowl until dough forms.
#3 Dust hands with confectioners' sugar and shape dough into 1" balls
#4 roll balls in confectioner's sugar and place 2 inches apart on ungreased cookie sheets
#5 Bake for 8-10 minutes or until center is just set
#6 Remove from pans after a minute or so and cool on wire racks

recipeName = "Fudge Crinkles"
recipeSource = "http://www.food.com/recipe/fudge-crinkles-a-great-4-ingredient-cake-mix-cookie-32614"

ingredientsList = [("1 (18 1/4 ounce) box devils' food cake mix (Betty Crocker Super Moist suggested)", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18 1/4 ounce)",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("1/2 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['oil']))),
                   ("2 large eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("confectioners sugar or granulated sugar, for rolling", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['sugar'])))]

instructionsList = [("1 Preheat oven to 350", "preheat(350)"),
                    ("2 Stir (by hand) dry cake mix, oil and eggs in a large bowl until dough forms.", "pour(cake_mix), pour(oil), pour(eggs), mix()"),
                    ("3 Dust hands with confectioners sugar and shape dough into 1 inch balls.", "scrape()"),
                    ("4 Roll balls in confectioners sugar and place 2 inches apart on ungreased cookie sheets.", "scrape()"),
                    ("5 Bake for 8-10 minutes or until center is just set.", "bake(8)"),
                    ("6 Remove from pans after a minute or so and cool on wire racks.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

