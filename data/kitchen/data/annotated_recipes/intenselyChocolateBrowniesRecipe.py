from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#20
#Intensely Chocolate Cocoa Brownies
#http://www.food.com/recipe/intensely-chocolate-cocoa-brownies-118242
#
#1/2 cup butter
#1/2 cup cocoa
#1 cup sugar
#2 eggs
#1 teaspoon vanilla
#2/3 cup flour
#1/2 teaspoon baking powder
#1/4 teaspoon salt
#
#1 Preheat oven to 350 degrees
#2 Melt butter in sauce pan.  When melted remove from heat.  Add cocoa and stir well.  Add sugar, eggs and vanilla.  Mix until shiny and smooth.  Add flour, baking powder and salt.  Mix well. 
#3 Pour into an 8 inch or 9 inch pan.  Bake for 15-20 minutes.  Do not over bake.  Look for edges slightly pulling away from pan.  Cool and cut.  Enjoy!

recipeName = "Intensely Chocolate Cocoa Brownies"
recipeSource = "http://www.food.com/recipe/intensely-chocolate-cocoa-brownies-118242"

#replace None with Physical Objects
ingredientsList = [("1/2 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1/2 cup cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=2, tags=['cocoa']))),
                   ("1 cup sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['sugar']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("1 teaspoon vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=5, tags=['vanilla']))),
                   ("2/3 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2/3 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour']))),
                   ("1/2 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['bakingpowder']))),
                   ("1/4 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/4 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=8, tags=['salt'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("1. Preheat oven to 350 degrees F.", "preheat(350)"),
                    ("2. Melt butter in sauce pan.", "melt(butter)"),
                    ("When melted remove from heat.", "pour(butter)"),
                    ("Add cocoa and stir well", "pour(cocoa_powder), mix()"),
                    ("Add sugar, eggs and vanilla", "pour(sugar), pour(eggs), pour(vanilla_extract)"),
                    ("Mix until shiny and smooth.", "mix()"),
                    ("Add flour, baking powder and salt", "pour(flour), pour(baking_powder), pour(salt), mix()"),
                    ("Mix well.", "mix()"),
                    ("3. Pour into an 8 inch or 9 inch pan.", "scrape()"),
                    ("Bake for 15-20 minutes.", "bake(15)"),
                    ("Do not over bake.", "noop()"),
                    ("Look for edges slightly pulling away from pan.", "noop()"),
                    ("Cool and cut.", "noop()"),
                    ("Enjoy!", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

