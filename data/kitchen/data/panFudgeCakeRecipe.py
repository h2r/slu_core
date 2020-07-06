from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#14
#1 Pan Fudge Cake
#http://low-cholesterol.food.com/recipe/1-pan-fudge-cake-2(35
#
#1 1/2 cups sugar
#1/2 cup cocoa
#1 1/2 teaspoons baking soda
#2 cups flour
#3/4 teaspoon salt
#1 1/2 teaspoons vanilla
#3/4 cup vegetable oil
#1 1/2 cups water
#1 1/2 teaspoons vinegar
#
#1 Preheat oven to 350 degrees.
#2 In an ungreased 9x13 pan- yes UNgreased, sift all dry
#ingredients.
#3 Add the liquids and stir just until blended.
#4 Bake for 25 minutes.
#5 Frost with your favorite frosting, cake is extremely moist so care must be taken that you don't tear up the top of the cake.

recipeName = "Pan Fudge Cake"
recipeSource = "http://low-cholesterol.food.com/recipe/1-pan-fudge-cake-2(35"

#TODO check the prism locations
ingredientsList = [("1 1/2 cups sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/2 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("1/2 cup cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['cocoa']))),
                   ("1 1/2 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=3, tags=['bakingsoda']))),
                   ("2 cups flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 1/4 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['flour']))),
                   ("3/4 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="3/4 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=5, tags=['salt']))),
                   ("1 1/2 teaspoons vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 1/2 teaspoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['vanilla']))),
                   ("3/4 cups vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="3/4 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=7, tags=['oil']))),
                   ("1 1/2 cups water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="1 1/2 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=8, tags=['water']))),
                   ("1 1/2 teaspoons vinegar", kitchenState.Ingredient(contains=["vinegar"], homogenous=True, amount="1 1/2 teaspoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=9, tags=['vinegar'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 350 degrees.", "preheat(350)"),
                    ("2. In an ungreased 9x13 pan - yes ungreased, sift all dry ingredients", 'pour(sugar), pour(cocoa_powder), pour(baking_soda), pour(flour), pour(salt), mix()'),
                    ("3. Add the liquids and stir just until blended.", 'pour(vanilla_extract), pour(oil), pour(water), pour(vinegar), mix()'),
                    ("4. Bake for 25 minutes", "bake(25)"),
                    ("5. Frost with your favorite frosting, cake is extremely moist so care must be taken that you don't tear up the top of the cake.", "frost()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
