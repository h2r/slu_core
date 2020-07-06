from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#10
#Easy Party Cake
#(http://allrecipes.com/recipe/easy-party-cake/detail.aspx)
#
#1 (18.25 ounce) package yellow cake mix
#1 (3 ounce) package orange flavored gelatin mix 
#4 eggs
#3/4 cup vegetable oil
#2/3 cup water
#
#1. Preheat oven to 350 degrees F (175 degrees C). Grease and flour a 9x5 inch loaf pan.
#2. In a large bowl, stir together cake mix and gelatin mix. Make a well in the center and pour in eggs, oil and water. Mix well and pour into a 9x5 inch loaf pan.
#3. Bake in the preheated oven for 60 minutes, or until a toothpick inserted into the center of the cake comes out clean. Allow to cool.

recipeName = "Easy Party Cake"
recipeSource = "http://allrecipes.com/recipe/easy-party-cake/detail.aspx"

#TODO chekc the prism locations
ingredientsList = [("1 (18.25 ounce) package yellow cake mix", kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 (18.25 ounce) package",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cake']))),
                   ("1 (3 ounce) package orange flavored gelatin mix", kitchenState.Ingredient(contains=["gelatin"], homogenous=True, amount="1 (3 ounce) package",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['gelatin']))),
                   ("4 eggs, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['eggs']))),
                   ("3/4 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="3/4 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['oil']))),
                   ("2/3 cup water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="2/3 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=5, tags=['water'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 350 degrees. (175 degrees C)", "preheat(350)"),
                    ("Grease and flour a 9x5 inch loaf pan.", "grease()"),
                    ("2. In a large bowl, stir together cake mix and gelatin mix.", "pour(cake_mix), pour(gelatin), mix()"),
                    ("3. Bake in the preheated oven for 60 minutes, or until a toothpick inserted into the center of the cake comes out clean.", "scrape(), bake(55)"),
                    ("Allow to cool.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
