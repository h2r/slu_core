from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#7
#Easy Platz (Coffee Cake)
#(http://allrecipes.com/recipe/easy-platz-coffee-cake/detail.aspx)
#
#2 cups all-purpose flour
#1 1/2 cups white sugar
#2 teaspoons baking powder 
#1 teaspoon salt
#2/3 cup margarine
#2 eggs, beaten
#2/3 cup milk
#1 cup blackberries
#
#1. Preheat oven to 350 degrees F (175 degrees C). Grease and flour a 9 inch square pan.
#2. In a large bowl, combine flour, sugar, baking powder and salt. Cut in margarine until mixture resembles coarse crumbs. Set aside 3/4 cup of crumb mixture, to be used as a topping for the cake. Mix eggs and milk together and then blend into remaining mixture in bowl.
#3. Spread batter into prepared pan. Sprinkle blackberries evenly over the top. Sprinkle reserved crumb mixture over fruit.
#4. Bake in the preheated oven for 25 to 30 minutes, or until a toothpick inserted into the center of the cake comes out clean.

recipeName = "Easy Platz (Coffee Cake)"
recipeSource = "http://allrecipes.com/recipe/easy-platz-coffee-cake/detail.aspx"

#replace None with Physical Objects
#TODO: fix the prism id
ingredientsList = [("2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 cups",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=1, tags=['flour']))),
                   ("1 1/2 cups white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/2 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("2 teaspoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="2 teaspoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=3, tags=['bakingpowder']))),
                   ("1 teaspoons salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 teaspoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['salt']))),
                   ("2/3 cup margarine", kitchenState.Ingredient(contains=["margarine"], homogenous=True, amount="2/3 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=5, tags=['margarine']))),
                   ("2 eggs, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=6, tags=['eggs']))),
                   ("2/3 cup milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="2/3 cup",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=7, tags=['milk']))),
                   ("1 cup blackberries", kitchenState.Ingredient(contains=["blackberries"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=8, tags=['blackberries'])))]
# TODO: what do we do with the pouring over the top
instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Grease and flour a 9 inch square pan.", "grease()"),
                    ("2. In a large bowl, combine flour, sugar, baking powder and salt.", "pour(flour), pour(sugar), pour(baking_powder), pour(salt), mix()"),
                    ("Cut in margarine until mixture resembles coarse crumbs.", "pour(margarine), mix()"),
                    ("Set aside 3/4 cup of crumb mixture, to buse used as a topping for the cake.", "noop()"),
                    ("Mix eggs and milk together and then blend into remaining mixture in bowl.", "pour(eggs), pour(milk), mix()"),
                    ("3. Spread batter into prepared pan.", "scrape()"),
                    ("Sprinkle blackberries evenly over the top.", "pour(blackberries)"),
                    ("Sprinkle reserved crumb mixture over fruit.", "noop()"),
                    ("4. Bake in the preheated oven for 25 to 30 minutes, or until a toothpick inserted into the center of the cake comes out clean.", "bake(25)"),]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
