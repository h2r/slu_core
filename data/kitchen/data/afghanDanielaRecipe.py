from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#3
#Afghan Biscuits
#(from daniela)
#
#Ingredients:
#200g (7 oz) butter
#75g (3 oz) sugar
#175g (6 oz) flour
#25g (1 oz) cocoa powder
#50g cornflakes (or crushed weetbix)
#Instructions:
#Soften butter
#Add sugar and beat to a cream.
#Add flour and cocoa
#Add cornflakes last
#Put spoonfuls on a greased oven tray
#bake about 15 minutes at 180 oC (350 oF)

recipeName = "Afghan Biscuits Daniela"
recipeSource = "Daniela"

#replace None with Physical Objects
ingredientsList = [("200g (7 oz) butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="200g (7 oz)",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("75g (3 oz) sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="75g (3 oz)",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("175g (6 oz) flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="175g (6 oz) flour",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("25g (1 oz) cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="25g (1 oz)",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['cocoa']))),
                   ("50g cornflakes (or crushed weetbix)", kitchenState.Ingredient(contains=["cornflakes"], homogenous=True, amount="50g",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cornflakes'])))]

#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Soften butter.", "pour(butter), mix()"),
                    ("Add sugar and beat to a cream.", "pour(sugar), mix()"),
                    ("Add flour and cocoa.", "pour(flour), pour(cocoa_powder)"),
                    ("Add cornflakes last.", "pour(cornflakes), mix()"),
                    ("Put spoonfuls on a greased oven tray.", "scrape()"),
                    ("Bake about 15 minutes at 180 oC (350 oF).", "preheat(350), bake(15)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

