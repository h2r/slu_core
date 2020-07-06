from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#29 
#EASY OATMEAL COOKIES
#http://www.cooks.com/rec/view/0,1710,146184-243203,).html
#
#1 c. sugar
#1 c. butter
#1 c. flour
#2 c. Quick Oats
#1 tsp. baking soda (sifted with flour)
#
#Preheat oven to 350F.
#Mix with hands -- form small balls and flatten on ungreased pan. Bake for 8-12 minutes (depends on size of cookies made).

recipeName = "Easy Oatmeal Cookies"
recipeSource = "http://www.cooks.com/rec/view/0,1710,146184-243203,).html"

#replace None with Physical Objects
ingredientsList = [("1 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 c.",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("1 c. butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 c.",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=2, tags=['butter']))),
                   ("1 c. flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=3, tags=['flour']))),
                   ("2 c. Quick Oats", kitchenState.Ingredient(contains=["oats"], homogenous=True, amount="2 c.",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=4, tags=['oats']))),
                   ("1 tsp. baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 tsp.",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['bakingsoda'])))]

#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat oven to 350F.", "preheat(350)"),
                    ("Mix with hands -- form small balls and flatten on ungreased pan.", "pour(sugar), pour(butter), pour(flour), pour(oats), pour(baking_soda), mix(), scrape()"),
                    ("Bake for 8-12 minutes (depends on size of cookies made).", "bake(8)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

