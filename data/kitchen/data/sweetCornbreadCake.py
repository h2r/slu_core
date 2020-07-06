from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#8
#Sweet Cornbread Cake
#(http://allrecipes.com/recipe/sweet-cornbread-cake/detail.aspx)
#
#1 cup cornmeal
#3 cups all-purpose flour
#1 1/3 cups white sugar
#2 tablespoons baking powder 
#1 teaspoon salt
#2/3 cup vegetable oil
#1/3 cup melted butter
#2 tablespoons honey
#4 eggs, beaten
#2 1/2 cups whole milk
#
#1. Preheat oven to 350 degrees F (175 degrees C), and grease a 9x13 inch baking dish.
#2. Stir together the cornmeal, flour, sugar, baking powder, and salt in a mixing bowl. Pour in the vegetable oil, melted butter, honey, beaten eggs, and milk, and stir just to moisten.
#3. Pour the batter into the prepared baking dish and bake in the preheated oven for 45 minutes, until the top of the cornbread starts to brown and show cracks.

recipeName = "Sweet Cornbread Cake"
recipeSource = "http://allrecipes.com/recipe/sweet-cornbread-cake/detail.aspx"

#replace None with Physical Objects
#TODO: fix the prism id
ingredientsList = [("1 cup cornmeal", kitchenState.Ingredient(contains=["cornmeal"], homogenous=True, amount="1 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=1, tags=['cornmeal']))),
                   ("3 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="3 cups",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=2, tags=['flour']))),
                   ("1 1/3 cups white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/3 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['sugar']))),
                   ("2 tablespoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="2 tablespoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['bakingpowder']))),
                   ("1 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['salt']))),
                   ("2/3 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="2/3 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=6, tags=['vegetableoil']))),
                   ("1/3 cup melted butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/3 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=7, tags=['butter']))),
                   ("2 tablespoons honey", kitchenState.Ingredient(contains=["honey"], homogenous=True, amount="2 tablespoons",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=8, tags=['honey']))),
                   ("4 eggs, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=9, tags=['eggs']))),
                   ("2 1/2 cups whole milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="2 1/2 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=10, tags=['milk'])))]


instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C), and grease a 9x13 inch baking dish.", "preheat(350), grease()"),
                    ("2. Stir together the cornmeal, flour, sugar, baking powder, and salt in a mixing bowl.", "pour(cornmeal), pour(sugar), pour(baking_powder), pour(salt), mix()"),
                    ("Pour in the vegetable oil, melted butter, honey, beaten eggs, and milk, and stir just to moisten.", "pour(oil), pour(butter), pour(honey), pour(eggs), pour(milk), mix()"),
                    ("3. Pour the batter into the prepared baking dish and bake in the preheated oven for 45 minutes, until the top of the cornbread stats to brown and show cracks.", "scrape(), bake(45)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
