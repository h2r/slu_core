from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#Brownies #1
#http://www.squidoo.com/simple-brownie-recipes

recipeName = "Brownies #1"

recipeSource = "http://www.squidoo.com/simple-brownie-recipes"

#replace None with Physical Objects
ingredientsList = [("1/2 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 cup sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 teaspoon vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("6 tablespoons cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="6 tablespoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cocoa']))),
                   ("1/2 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("1. Cream first 3 ingredients with a mixer.", "pour(butter), pour(sugar), pour(vanilla_extract), mix()"),
                    ("2. Blend in cocoa, flour and eggs.", "pour(cocoa_powder), pour(flour), pour(eggs), mix()"),
                    ("3. Bake at 350F for 25 to 30 minutes.", "scrape(), preheat(350), bake(30)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

