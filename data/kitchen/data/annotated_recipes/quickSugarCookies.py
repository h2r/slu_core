from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject


recipeName = "Quick'N Easy Sugar Cookies"
recipeSource = "http://www.cooks.com/rec/view/0,1841,151163-255203,00.html"

#TODO check the prism locations
ingredientsList = [("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=1, tags=['eggs']))),
                   ("2/3 c. vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="2/3 cup",
                                                                    physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['oil']))),
                   ("2 tsp. vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['vanilla']))),
                   ("3/4 c. granulated sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="3/4 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=4, tags=['sugar']))),
                   
                   ("2 c. all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 cups",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("2 tsp baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="2 tsp",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=6, tags=['powder']))),
                   ("1/2 tsp. salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/2 teaspoon",
                                                             physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [
    ("In a medium-size mixing bowl, beat eggs with a fork until the whites and yolks are well blended.", "pour(eggs), mix()"),
    ("Add the vegetable oil and vanilla, stirring until blended with the eggs.", "pour(oil), pour(vanilla_extract), mix()"),
    ("Blend in the sugar.", "pour(sugar), mix()"),
    ("Sift together the flour, baking powder and salt.", "noop()"),
    ("Add these dry ingredients, a small portion at a time, to the above mixture, mixing until all ingredients are moist and batter is smooth.", "pour(flour), pour(baking_powder), pour(salt), mix()"),
    ("Drop batter by teaspoon, about 2 inches apart, onto an ungreased cookie sheet.", "scrape()"),
    ("Press each with the bottom of a glass that has been oiled and dipped in sugar.", "noop()"),
    ("Makes about 3 dozen 3 inch cookies.", "noop()"),
    ("Bake at 400 degrees for approximately 8 to 10 minutes.", "preheat(400), bake(10)"),
    ("Allow cookies to cool on the cookie sheet for 2 or 3 minutes before removing to a cake rack to complete cooling.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
