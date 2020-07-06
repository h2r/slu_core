from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#21
#Simply Brownie Recipe
#http://cullyskitchen.com/simple-brownie-recipe/
#Ingredients
#1. 1 cup vegetable oil
#2. 2 cups sugar
#3. 2 Teaspoons Vanilla
#4. 4 Large eggs
#5. 1/2 teaspoon Baking Powder
#6. 2/3 cup Coco Powder
#7. 1/2 Teaspoon Salt
#8. 1 Cup flour
#
#Preheat your oven to 350 while you are preparing the Brownie Mix.
#1. Mix the oil, sugar, eggs and vanilla till they are well blended.
#2. Mix all the dry ingredients together separately.
#3. Add the dry ingredients to the egg mixture.
#4. Pour into a 9 x 13 baking dish or pan.
#Bake for about 30 minutes or until the Brownies start to separate from the edges of the baking dish or pan.

recipeName = "Simply Brownie Recipe"
recipeSource = "http://cullyskitchen.com/simple-brownie-recipe/"

#replace None with Physical Objects
ingredientsList = [("1 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['oil']))),
                   ("2 cups sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=2, tags=['sugar']))),
                   ("2 Teaspoons Vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla']))),
                   ("4 Large eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("1/2 teaspoon Baking Powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=5, tags=['bakingpowder']))),
                   ("2/3 cup Coco Powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="2/3 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['cocoa']))),
                   ("1/4 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/4 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ("1 Cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=8, tags=['flour'])))]

#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat your oven to 350 while you are preparing the Brownie Mix.", "preheat(350)"),
                    ("1. Mix the oil, sugar, eggs and vanilla till they are well blended.", "pour(oil), pour(sugar), pour(eggs), pour(vanilla_extract), mix()"),
                    ("2. Mix all the dry ingredients together separately", "pour(baking_powder), pour(cocoa_powder), pour(salt), pour(flour), mix()"),
                    ("3. Add the dry ingredients to the egg mixture.", "mix()"),
                    ("4. Pour into a 9 x 13 baking dish or pan.", "scrape()"),
                    ("Bake for about 30 minutes or until the Brownies start to separate from the edges of the baking dish or pan.", "bake(30)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

