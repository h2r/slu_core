from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#2
#Chocolate Afghans
#(http://www.kidspot.co.nz/recipes-for+1644+20+Cakes-&-Baking+Chocolate-afghans.htm)
#
#180g butter, melted
#1/3 cup caster sugar
#1 1/2 cups plain flour
#1 cup cornflakes, crushed
#1/4 cup desiccated coconut
#2 tablespoons cocoa powder
#
#Preheat oven to 180 degrees C. Line two baking trays with baking paper. Cream butter and sugar using an electric beater until light and fluffy.
#Sift flour into a large bowl, add cornflakes, coconut and cocoa powder and stir to combine. Stir flour mixture into butter mixture until well combined.
#For each biscuit, place one tablespoon of mixture onto prepared baking trays about 3cm apart. Bake for 10-12 minutes until starting to brown. Cool on baking trays for 5 minutes then transfer to wire rack.
#
#(I truncated the recipe a bit)


recipeName = "Chocolate Afghans"
recipeSource = "http://www.kidspot.co.nz/recipes-for+1644+20+Cakes-&-Baking+Chocolate-afghans.htm"

#replace None with Physical Objects
ingredientsList = [("180g butter, melted", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="180g",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1/3 cup castor sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1/3 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 1/2 cups plain flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 1/2 cups",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("1 cup cornflakes, crushed", kitchenState.Ingredient(contains=["cornflakes"], homogenous=True, amount="1 cup",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cornflakes']))),
                   ("1/4 cup desiccatted coconut", kitchenState.Ingredient(contains=["coconut"], homogenous=True, amount="1/4 cup",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['coconut']))),
                   ("2 tablespoons cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="2 tablespoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=7, tags=['cocoa'])))]

#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Pre-heat the oven to 180C.", "preheat(350)"),
                    ("Line two baking trays with baking paper.", "noop()"),
                    ("Cream butter and sugar using an electric beater until light and fluffy.", "pour(butter), pour(sugar), mix()"),
                    ("Sift flour into a large bowl, add cornflakes, coconut, and cocoa powder and stir to combine.", "pour(flour), pour(cornflakes), pour(cocoa_powder), mix()"),
                    ("Stir flour mixture into butter mixture until well combined.", "mix()"),
                    ("For each biscuit, place one tablespoon of mixture onto prepared baking trays about 3cm apart", "scrape()"),
                    ("Bake for 10-12 minutes until starting to brown.", "bake(10)"),
                    ("Cool on baking trays for 5 minutes then transfer to wire rack.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

