from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

# 1 2/3 cups granulated sugar
#3/4 cup butter or margarine, melted
#2 tablespoons water
#2 large eggs
#2 teaspoons vanilla extract
#1 1/3 cups all-purpose flour
#3/4 cup NESTLE TOLL HOUSE Baking Cocoa 
#1/2 teaspoon baking powder
#1/4 teaspoon salt
#3/4 cup chopped nuts
#powdered sugar
#1. PREHEAT oven to 350 degrees F. Grease 13x9-inch baking pan.
#2. COMBINE sugar, butter and water in large bowl. Stir in eggs and vanilla extract.
#Combine flour, cocoa, baking powder and salt in medium bowl; stir into sugar
#mixture. Stir in nuts. Spread into prepared baking pan.
#3. BAKE for 18 to 25 minutes or until wooden pick inserted in center comes out
#slightly sticky. Cool completely in pan on wire rack. Sprinkle with powdered sugar. Cut into bars.


recipeName = "Chewy Cocoa Brownies"
recipeSource = "http://allrecipes.com/recipe/chewy-cocoa-brownies/"

#TODO need to fix the prisms
ingredientsList = [("1 2/3 granulated sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 2/3 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['sugar']))),
                   ("3/4 cup butter or margarine, melted", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="3/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("2 tablespoons water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['water']))),
                   ("2 large eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['vanilla']))),
                   ("1/3 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1/3 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("3/4 cup NESTLE TOLL HOUSE Baking Cocoa ", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="3/4 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=9, tags=['"], ']))),
                   ("1/2 teaspoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['baking_powder']))),
                   ("1/4 teaspoons salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/4 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ("3/4 cup chopped nuts", kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="3/4 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=8, tags=['nuts'])))]

instructionsList = [("PREHEAT oven to 350 degrees F.", "preheat(350)"),
                    ("Grease 13x9-inch baking pan", "grease()"),
                    ("COMBINE sugar, butter and water in large bowl.", "pour(sugar), pour(butter), pour(water), mix()"),
                    ("Stir in eggs and vanilla extract", "pour(eggs), pour(vanilla_extract), mix()"),
                    ("Combine flour, cocoa, baking powder and salt in medium bowl; stir into sugar mixture.", "pour(flour), pour(cocoa_powder), pour(baking_powder), pour(salt), mix()"),
                    ("Stir in nuts.", "pour(nuts), mix()"),
                    ("Spread into prepared baking pan", "scrape()"),
                    ("BAKE for 18 to 25 minutes or until wooden pick inserted in center comes out slightly sticky.", "bake(18)"),
                    ("Cool completely in pan on wire rack.", "noop()"),
                    ("Sprinkle with powdered sugar.", "noop()"),
                    ("Cut into bars", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

