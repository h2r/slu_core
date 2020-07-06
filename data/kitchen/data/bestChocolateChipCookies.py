from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject
#6
#Best Chocolate Chip Cookies
#(http://allrecipes.com/recipe/best-chocolate-chip-cookies/)
#
#1 cup butter, softened
#1 cup white sugar
#1 cup packed brown sugar
#2 eggs
#2 teaspoons vanilla extract
#3 cups all-purpose flour
#1 teaspoon baking soda
#2 teaspoons hot water
#1/2 teaspoon salt
#2 cups semisweet chocolate chips 
#1 cup chopped walnuts
#
#1. Preheat oven to 350 degrees F (175 degrees C).
#2. Cream together the butter, white sugar, and brown sugar until smooth. Beat in the
#eggs one at a time, then stir in the vanilla. Dissolve baking soda in hot water. Add to batter along with salt. Stir in flour, chocolate chips, and nuts. Drop by large spoonfuls onto ungreased pans.
#3. Bake for about 10 minutes in the preheated oven, or until edges are nicely browned.


recipeName = "Best Chocolate Chip Cookies"
recipeSource = "http://allrecipes.com/recipe/best-chocolate-chip-cookies/"

#replace None with Physical Objects
#TODO: fix the prism positions
ingredientsList = [("1 cup butter, softened", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 cup packed brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['brownsugar']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=5, tags=['vanilla']))),
                   ("3 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="3 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour']))),
                   ("1 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=7, tags=['bakingsoda']))),
                   ("2 teaspoons hot water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="2 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=8, tags=['water']))),
                   ("1/2 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=9, tags=['salt']))),
                   ("2 cups semisweet chocolate chips", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="2 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=10, tags=['chocolatechips']))),
                   ("1 cup chopped walnuts", kitchenState.Ingredient(contains=["walnuts"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=11, tags=['walnuts'])))]



#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("1. Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("2. Cream together the butter, white sugar, and brown sugar until smooth.", "pour(butter), pour(sugar), pour(brown_sugar), mix()"),
                    ("Beat in the eggs one at a time, then stir in the vanilla.", "pour(eggs), mix(), pour(vanilla_extract), mix()"),
                    ("Dissolve baking soda in hot water.  Add to batter along with salt.", "pour(baking_soda), pour(water), pour(salt)"),
                    ("Stir in flour, chocolate chips, and nuts.", "pour(flour), mix(), pour(chocolate_chips), mix(), pour(walnuts), mix()"),
                    ("Drop by large spoonfuls onto ungreased pans.", "scrape()"),
                    ("3. Bake for about 10 minutes in preheated oven, or until edges are nicely browned.", "bake(10)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

