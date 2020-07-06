from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#25
#Simple White Cake
#http://allrecipes.com/recipe/simple-white-cake/
#
#1 cup white sugar
#1/2 cup butter
#2 eggs
#2 teaspoons vanilla extract
#1 1/2 cups all-purpose flour
#1 3/4 teaspoons baking powder
#1/2 cup milk
#
#1. Preheat oven to 350 degrees F (175 degrees C). Grease and flour a 9x9 inch pan or line a muffin pan with paper liners.
#2. In a medium bowl, cream together the sugar and butter. Beat in the eggs, one at a time, then stir in the vanilla. Combine flour and baking powder, add to the creamed mixture and mix well. Finally stir in the milk until batter is smooth. Pour or spoon batter into the prepared pan.
#3. Bake for 30 to 40 minutes in the preheated oven. For cupcakes, bake 20 to 25 minutes. Cake is done when it springs back to the touch.
#                                                                                                                

recipeName = "Simple White Cake"
recipeSource = "http://allrecipes.com/recipe/simple-white-cake/"

#TODO check the prism locations
ingredientsList = [("1 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=1, tags=['sugar']))),
                   ("1/2 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['butter']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=4, tags=['vanilla']))),
                   ("1 1/2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 1/2 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=5, tags=['flour']))),
                   ("1 3/4 teaspoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 3/4 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=6, tags=['bakingpowder']))),
                   ("1/2 cup milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=7, tags=['milk'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C)", "preheat(350)"),
                    ("Grease and flour a 9x9 inch pan or line a muffin pan with paper liners.", "grease()"),
                    ("2. In a medium bowl, cream together the sugar and butter.", "pour(sugar), pour(butter), mix()"),
                    ("Beat in the eggs, one at a time, then stir in the vanilla.", "pour(eggs), mix(), pour(vanilla_extract), mix()"),
                    ("Combine flour and baking powder, add to the creamed mixture and mix well.", "pour(flour), mix(), pour(baking_powder), mix()"),
                    ("Finally stir in the milk until batter is smooth.", "pour(milk), mix()"),
                    ("Pour or spoon batter into the prepared pan.", "scrape()"),
                    ("3. Bake for 30 to 40 minutes in the preheated oven.", "bake(30)"),
                    ("Cake is done when it springs back to the touch.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
