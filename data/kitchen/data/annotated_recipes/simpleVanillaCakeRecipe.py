from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#24
#Simple Vanilla Cake Recipe
#http://recipes.kaboose.com/vanilla-cake.html
#
#2 cups (5 mL) sugar
#4 eggs
#2-1/2 cups (625 mL) all-purpose flour
#1 cup (250 mL) milk
#3/4 cup (175 mL) vegetable oil
#2-1/4 teaspoons (11 mL) baking powder
#1 teaspoon (5 mL) vanilla
#
#1. Preheat oven to 350 degrees F (180 degrees C). Line two 9-inch (23-cm) round cake pans or one 9x13-inch (23 x 33 cm) rectangular baking pan with parchment paper. Grease the paper and the sides of the pan well.
#2. In a large mixing bowl, with an electric mixer, beat sugar and eggs together until slightly thickened, about 1 minute. Add flour, milk, oil, baking powder, and vanilla and beat for another minute, just until the batter is smooth and creamy. Don't overbeat. Pour batter into the prepared baking pan(s).
#3. Bake in preheated oven for 30 to 40 minutes or until the tops are golden and a toothpick poked into the center of the layer comes out clean. (A single rectangular pan will take longer to bake than two round ones.) Loosen the sides of the cake from the pan with a thin knife, then turn out onto a rack and peel off the paper. Let cool completely before covering with frosting, if desired.


recipeName = "Simple Vanilla Cake Recipe"
recipeSource = "http://recipes.kaboose.com/vanilla-cake.html"

#TODO check the prism locations
ingredientsList = [("2 cups (5 mL) sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2 cups",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=1, tags=['sugar']))),
                   ("4 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=2, tags=['eggs']))),
                   ("2-1/2 cups (625 mL) all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2-1/2 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("1 cup (250 mL) milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=4, tags=['milk']))),
                   ("3/4 cup (175 mL) vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="3/4 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=5, tags=['oil']))),
                   ("2-1/4 teaspoons (11 mL) baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="2-1/4 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=6, tags=['bakingpowder']))),
                   ("1 teaspoon (5 mL) vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['vanilla'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 350 degrees F (180 degrees C)", "preheat(350)"),
                    ("Line two 9-inch (23-cm) round cake pans or one 9x13-inch (23 x 33 cm) rectangular baking pan with parchment paper", "line()"),
                    ("Grease the paper and the sides of the pan well", "grease()"),
                    ("2. In large mixing bowl, with an electric mixer, beat sugar and eggs together until slightly thickened, about 1 minute", "pour(sugar), pour(eggs), mix()"),
                    ("Add flour, milk, oil, baking powder, and vanilla and beat for another minute, just until the batter is smooth and cramy.", "pour(flour), pour(milk), pour(oil), pour(baking_powder), pour(vanilla_extract), mix()"),
                    ("Don't overbeat.", "noop()"),
                    ("Pour batter", "noop()"),
                    ("Pour batter into the prepared baking pan(s)", "scrape()"),
                    ("3. Bake in preheated oven for 30 to 40 minutes or until the tops are golden and a toothpick poked in the center of the layer comes out clean.", "bake(30)"),
                    ("(A single rectangular pan will take longer to bake than two rounds ones.)", "noop()"),
                    ("Loosen the sides of the cake from the pan with a thin knife, then turn out onto a rack and peel off the paper.", "noop()"),
                    ("Let cool completely before covering with frosting, if desired", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
