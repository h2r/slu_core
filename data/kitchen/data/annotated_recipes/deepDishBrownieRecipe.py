from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#5
#Deep Dish Brownies
#(http://allrecipes.com/recipe/deep-dish-brownies/detail.aspx)
#
#3/4 cup butter, melted
#1 1/2 cups white sugar
#1 1/2 teaspoons vanilla extract
#3 eggs
#3/4 cup all-purpose flour
#1/2 cup unsweetened cocoa powder 
#1/2 teaspoon baking powder
#1/2 teaspoon salt
#
#1. Preheat oven to 350 degrees F (175 degrees C). Grease an 8 inch square pan.
#2. In a large bowl, blend melted butter, sugar and vanilla. Beat in eggs one at a time.
#Combine the flour, cocoa, baking powder and salt. Gradually blend into the egg
#mixture. Spread the batter into the prepared pan.
#3. Bake in preheated oven for 40 to 45 minutes, or until brownies begin to pull away
#from the sides of the pan. Let brownies cool, then cut into squares. Enjoy!

recipeName = "Deep Dish Brownies"
recipeSource = "http://allrecipes.com/recipe/deep-dish-brownies/detail.aspx"

#replace None with Physical Objects
ingredientsList = [("3/4 cup butter, melted", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="3/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 1/2 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 1/2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 1/2 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla']))),
                   ("3 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="3",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("3/4 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="3/4 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("1/2 cup unsweetened cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['cocoa']))),
                   ("1/2 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=7, tags=['bakingpowder']))),
                   ("1/2 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=8, tags=['salt'])))]


#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Grease 8 inch square pan", "grease()"),
                    ("2. In a large bowl, blend melted butter, sugar and vanilla.", "pour(butter), pour(sugar), pour(vanilla_extract), mix()"),
                    ("Beat in eggs one at a time.", "pour(eggs), mix()"),
                    ("Combine the flour, cocoa, baking powder and salt.", "pour(flour), pour(cocoa_powder), pour(baking_powder), pour(salt), mix()"),
                    ("Spread the batter into the prepared pan.", "scrape()"),
                    ("3. Bake in preheated oven for 40 to 45 minutes, or until brownies begin to pull away.", "bake(40)"),
                    ("Let brownies cool, then cut into squares", "noop()"),
                    ("Enjoy!", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

