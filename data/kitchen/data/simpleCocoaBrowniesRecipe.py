from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#22
#Simple Cocoa Brownies
#http://simpledailyrecipes.com/103/simple-cocoa-brownies/
#
#1 cup dark brown sugar
#1/2 cup butter
#1 teaspoon vanilla
#2 eggs
#2/3 cup all purpose flour
#1/2 cup baking cocoa
#1/2 teaspoon baking powder
#1/4 teaspoon salt
#
#Heat oven to 350oF degrees. Line bottom of 8x8 inch nonstick pan with wax paper. Spray pan with nonstick cooking spray.
#Beat sugar, butter, vanilla and eggs in large bowl with electric mixer on medium speed. Stir in remaining ingredients until moistened. Spread batter evenly in pan.
#Bake 15-20 minutes or until toothpick inserted in center comes out clean. Cool 10-15 minutes, flip onto serving dish, remove wax liner, then allow to cool completely.

recipeName = "Simple Cocoa Brownies"
recipeSource = "http://simpledailyrecipes.com/103/simple-cocoa-brownies/"

#replace None with Physical Objects
ingredientsList = [("1 cup dark brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['brownsugar']))),
                   ("1/2 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['butter']))),
                   ("1 teaspoon vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['eggs']))),
                   ("2/3 cup all purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2/3 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("1/2 cup baking cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['cocoa']))),
                   ("1/2 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['bakingpowder']))),
                   ("1/4 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/4 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=8, tags=['salt'])))]

#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Heat oven to 350oF degrees.", "preheat(350)"),
                    ("Line bottom of 8x8 inch nonstick pan with wax paper.", "noop()"),
                    ("Spray pan with nonstick cooking spray.", "noop()"),
                    ("Beat sugar, butter, vanilla and eggs in large bowl with electric mixer on medium speed.", "pour(brown_sugar), pour(butter), pour(vanilla_extract), pour(eggs), mix()"),
                    ("Stir in remaining ingredients until moistened.", "pour(flour), pour(cocoa_powder), pour(baking_powder), pour(salt), mix()"),
                    ("Spread batter evenly in pan.", "scrape()"),
                    ("Bake 15-20 minutes or until toothpick inserted in center comes out clean.", "bake(15)"),
                    ("Cool 10-15 minutes, flip onto serving dish, remove wax liner, then allow to cool completely", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

