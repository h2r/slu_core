from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#27 
#Ingredients
#1/4 cup butter flavored shortening
#1 1/2 cups packed brown sugar
#2 eggs
#1/2 teaspoon vanilla extract
#1 cup all-purpose flour
#1 1/2 teaspoons baking powder 
#1/2 teaspoon salt
#1 cup chopped walnuts
#1/2 cup semisweet chocolate chips
#Directions
#Calculate
#Blonde Brownies
# In a mixing bowl, cream shortening and brown sugar. Add eggs, one at a time, beating well after each addition. Beat in vanilla. Combine flour, baking powder and salt; gradually add to the creamed mixture. Stir in nuts and chocolate chips. Spread into a greased 11-in. x 7-in. x 2-in. baking pan. Bake at 350 degrees F for 25-30 minutes or until a toothpick inserted near the center comes out clean. Cool on wire rack. Cut into bars.
#

recipeName = "Blonde Brownies"
recipeSource = "http://allrecipes.com/recipe/blonde-brownies/"

#TODO need to fix the prisms
ingredientsList = [("1/4 cup butter flavored shortening", kitchenState.Ingredient(contains=["shortening"], homogenous=True, amount="1/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['shortening']))),
                   ("1 1/2 cup packed brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1 1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['brownsugar']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1/2 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1/2 teaspoon",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['vanilla']))),
                   ("1 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("1 1/2 teaspoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 1/2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['bakingpowder']))),
                   ("1/2 teaspoons salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ("1 cup chopped walnuts", kitchenState.Ingredient(contains=["walnuts"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=8, tags=['walnuts']))),
                   ("1/2 cup semi-sweet chocholate chips", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=9, tags=['chocolatechips'])))]

instructionsList = [("In a mixing bowl, cream shortening and brown sugar.", "pour(shortening), pour(brown_sugar), mix()"),
                    ("Add eggs, one at a time, beating well after each addition.", "pour(eggs), mix()"),
                    ("Beat in vanilla.", "pour(vanilla_extract), mix()"),
                    ("Combine flour, baking powder and salt; gradually add to the creamed mixture.", "pour(flour), pour(baking_powder), pour(salt), mix()"),
                    ("Stir in nuts and chocolate chips.", "pour(walnuts), pour(chocolate_chips), mix()"),
                    ("Spread into a greased 11-in x 7-in x 2-in baking pan.", "scrape()"),
                    ("Bake at 350 degrees F for 25-30 minutes or until a toothpick inserted near the center comes out clean.", "preheat(350), bake(25)"),
                    ("Cool on wire rack.", "noop()"),
                    ("Cut into bars.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

