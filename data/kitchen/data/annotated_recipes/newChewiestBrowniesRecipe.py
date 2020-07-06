from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#1 cup unsweetened cocoa powder 1/2 cup melted butter
#2 cups white sugar
#2 eggs
#1/4 teaspoon salt
#1 cup all-purpose flour
#2 teaspoons vanilla extract
#1/3 cup confectioners' sugar for decoration
#Directions
#????????????????????1. Preheat oven to 300 degrees F (150 degrees C). Line one 9x13 inch pan with greased parchment paper.
#2. Combine the cocoa, melted butter, sugar, eggs, salt , flour and vanilla. Mix until well combined. It should be very thick and sticky.
#3. Spread mixture into the prepared pan. Bake at 300 degrees F (150 degrees C) for 30 minutes. Cool completely before cutting into squares.


recipeName = "Chewiest Brownies #2"
recipeSource = "http://allrecipes.com/recipe/chewiest-brownies/"

#TODO need to fix the prisms
ingredientsList = [("1 cup unsweetened cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['cocoa']))),
                   ("1/2 cup melted butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("2 cups white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['sugar']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1/4 teaspoons salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/4 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ("1 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['vanilla'])))]

instructionsList = [("preheat oven to 300 degrees F.", "preheat(300)"),
                    ("Line one 13x9-inch pan with greased parchment paper", "grease()"),
                    ("Combine the cocoa, melted butter, sugar, eggs, salt, flour and vanilla.", "pour(cocoa_powder), pour(butter), pour(sugar), pour(eggs), pour(salt), pour(flour), pour(vanilla_extract), mix()"),
                    ("Mix until well combined.", "mix()"),
                    ("It should be thick and sticky.", "noop()"),
                    ("Spread mixture into the prepared pan", "scrape()"),
                    ("Bake at 300 degrees F (150 degrees C) for 30 minutes", "bake(30)"),
                    ("Cool completely before cutting into squares", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

