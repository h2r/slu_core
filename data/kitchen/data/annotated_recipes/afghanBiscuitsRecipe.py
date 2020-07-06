from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#1
#Afghan Biscuits
#(http://australianfood.about.com/od/bakingdesserts/r/AfghanBiscuits.htm)
#
#Ingredients:
#200 grams of butter, at room temperature 
#1/2 cup of castor sugar
#1 1/2 cups of all-purpose flour
#3 Tbsp unsweetened cocoa powder
#1 1/2 cups of unsweetened corn flakes (Kellogg's)
#Preparation:
#1. Pre-heat the oven to 350F (180C). Line a baking sheet with baking paper. Set aside.
#2. Cream the butter and sugar until light and fluffy.
#3. Sift together the flour and cocoa powder and mix into butter mixture with a wooden spoon.
#Fold in cornflakes and don't worry if they crumble.
#4. Roll or press 1 1/2 teaspoonfuls of the dough into balls and flatten them slightly. Place them
#about 2 inches apart on the baking sheet.
#5. Bake in the oven for 10-15 minutes. Remove from oven and cool on a wire rack.
#
#(I truncated the recipe a bit)

recipeName = "Afghan Biscuits"
recipeSource = "http://australianfood.about.com/od/bakingdesserts/r/AfghanBiscuits.htm"

#replace None with Physical Objects
ingredientsList = [("200g butter, at room temperature", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="200g",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1/2 cup of castor sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 1/2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 1/2 cups",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("3 Tbsp unsweetened cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="3 Tbsp",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['cocoa']))),
                   ("1 1/2 cups of unsweetened corn flakes (Kellogg's)", kitchenState.Ingredient(contains=["cornflakes"], homogenous=True, amount="1 1/2 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cornflakes'])))]

#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Pre-heat the oven to 350F (180C).", "preheat(350)"),
                    ("Cream the butter and sugar until light and fluffy.", "pour(butter), pour(sugar), mix()"),
                    ("Sift together the flour and cocoa powder and mix into butter mixture with a wooden spoon.", "pour(flour), pour(cocoa_powder), mix()"),
                    ("Fold in cornflakes and don't worry if they crumble", "pour(cornflakes), mix()"),
                    ("Roll or press 1 1/2 teaspoonfuls of the dough into balls and flatten them slightly.", "scrape()"),
                    ("Place them about 2 inches apart on the baking sheet.", "noop()"),
                    ("Bake in the oven for 10-15 minutes", "bake(10)"),
                    ("Remove from oven and cool on a wire rack", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

