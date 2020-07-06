from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#27 
#Chocolate Peanut Butter Pudding Cookies
#http://allrecipes.com/recipe/chocolate-peanut-butter-pudding-cookies/detail.aspx
#
#1 cup butter, softened
#1/4 cup white sugar
#3/4 cup packed brown sugar
#1 teaspoon vanilla extract
#2 eggs
#2 1/4 cups all-purpose flour
#1 teaspoon baking powder
#1 (3.9 ounce) package instant chocolate pudding mix 
#1 3/4 cups peanut butter chips
#
#1. Preheat oven to 350 degrees F (175 degrees C).
#2. In a large bowl, cream together the butter, white sugar and brown sugar until
#smooth. Beat in the eggs one at a time, then stir in the vanilla. Combine the flour, baking powder and instant pudding mix; stir into the creamed mixture. Fold in the peanut butter chips. Drop by rounded spoonfuls onto ungreased cookie sheets.
#3. Bake for 8 to 10 minutes in the preheated oven. Allow cookies to cool on baking sheet for 5 minutes before removing to a wire rack to cool completely.


recipeName = "Chocolate Peanut Butter Pudding Cookies"
recipeSource = "http://allrecipes.com/recipe/chocolate-peanut-butter-pudding-cookies/detail.aspx"

#replace None with Physical Objects
ingredientsList = [("1 cup butter, softened", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['butter']))),
                   ("1/4 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("3/4 cup packed brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="3/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=3, tags=['brownsugar']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=4, tags=['vanilla']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['eggs']))),
                   ("2 1/4 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 1/4 cups",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour']))),
                   ("1 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=8, tags=['bakingpowder']))),
                   ("1 (3.9 ounce) package instant chocolate pudding mix", kitchenState.Ingredient(contains=["pudding"], homogenous=True, amount="1 (3.9 ounce) package",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=9, tags=['pudding']))),
                   ("3/4 cups peanut butter chips", kitchenState.Ingredient(contains=["pb_chips"], homogenous=True, amount="3/4 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=10, tags=['pbchips'])))]

#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("2. In a large bowl, cream together the butter, white sugar and brown sugar until smooth.", "pour(butter), pour(sugar), pour(brown_sugar), mix()"),
                    ("Beat in the eggs one at a time, then stir in the vanilla.", "pour(eggs), mix(), pour(vanilla_extract), mix()"),
                    ("Combine the flour, baking powder and instant pudding mix; stir into the creamed mixture.", "pour(flour), pour(baking_powder), pour(pudding), mix()"),
                    ("Fold in the peanut butter chips.", "pour(pb_chips), mix()"),
                    ("Drop by rounded spoonfuls onto ungreased cookie sheet.", "scrape()"),
                    ("Bake 8-10 minutes in the preheated oven.", "bake(8)"),
                    ("Allow cookies to cool on baking sheet for 5 minutes before removing to a wire rack to cool completely.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

