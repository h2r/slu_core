from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#4
#Absolutely Best Brownies
#(http://allrecipes.com/recipe/absolutely-best-brownies/detail.aspx)
#
#Ingredients
#1/2 cup butter, melted
#1 cup white sugar
#2 eggs
#1/2 cup self-rising flour
#1/3 cup unsweetened cocoa powder 
#1/4 teaspoon salt
#1 teaspoon vanilla extract
#1/2 cup chopped walnuts (optional)
#
#Instructions
#1. Preheat oven to 350 degrees F (175 degrees C). Grease and flour an 8x8 or 9x9 inch baking pan.
#2. In a medium bowl, beat together the butter and sugar. Add eggs, and mix well. Combine the flour, cocoa and salt; stir into the sugar mixture. Mix in the vanilla and stir in walnuts if desired. Spread evenly into the prepared pan.
#3. Bake for 25 to 30 minutes in the preheated oven, or until edges are firm. Cool before cutting into squares.


recipeName = "Absolutely Best Brownies"
recipeSource = "http://allrecipes.com/recipe/absolutely-best-brownies/detail.aspx"

#replace None with Physical Objects
ingredientsList = [("1/2 cup butter, melted", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1/2 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['flour']))),
                   ("1/3 cup unsweetened cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1/3 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['cocoa']))),
                   ("1/4 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/4 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['salt']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['vanilla']))),
                   ("1/2 cup chopped walnuts (optional)", kitchenState.Ingredient(contains=["walnuts"], homogenous=True, amount="1/2 cup",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=8, tags=['walnuts'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Grease and flour an 8x8 or 9x9 inch baking pan", "grease()"),
                    ("In a medium bowl, beat together the butter and sugar.", "pour(butter), pour(sugar), mix()"),
                    ("Combine the flour, cocoa and salt; stir into the sugar mixture.", "pour(flour), pour(cocoa_powder), pour(salt), mix()"),
                    ("Mix in the vanilla and stir in the walnuts if desired.", "pour(vanilla_extract), mix(), pour(walnuts), mix()"),
                    ("Spread evenly into the prepared pan.", "scrape()"),
                    ("Bake for 25 to 30 minues in the preheated oven, or until edges are firm.", "bake(25)"),
                    ("Cool before cutting into squares", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

