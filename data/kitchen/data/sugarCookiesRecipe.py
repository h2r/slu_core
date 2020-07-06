from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#13
#Sugar Cookies
#(http://allrecipes.com/recipe/sugar-cookies/detail.aspx)
#1/2 cup butter
#1/2 cup shortening
#1 cup sugar
#1 egg
#1 teaspoon vanilla extract
#2 1/4 cups all-purpose flour 
#1/2 teaspoon baking powder 
#1/2 teaspoon baking soda 
#
#1. In a mixing bowl, cream butter, shortening and sugar. Add egg and vanilla; mix well. Combine flour, baking powder and baking soda; gradually add to the creamed mixture. Shape into 1-in. balls. Roll in sugar. Place on greased baking sheet; flatten with a glass. Bake at 350 degrees F for 10-12 minutes.

recipeName = "Sugar Cookies"
recipeSource = "http://allrecipes.com/recipe/sugar-cookies/detail.aspx"

#TODO check the prism locations
ingredientsList = [("1/2 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1/2 cup shortening", kitchenState.Ingredient(contains=["shortening"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['shortening']))),
                   ("1 cup sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['sugar']))),
                   ("1 egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=4, tags=['eggs']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=5, tags=['vanilla']))),
                   ("2 1/4 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 1/4 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=6, tags=['flour']))),
                   ("1/2 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['bakingpowder']))),
                   ("1/2 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=8, tags=['bakingsoda'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. In a mixing bowl, cream butter, shortening and sugar.", "pour(butter), pour(shortening), pour(sugar), mix()"),
                    ("Add egg and vanilla; mix well", 'pour(eggs), pour(vanilla_extract), mix()'),
                    ("Combine flour, baking powder and baking soda; gradually add to the creamed mixture.", "pour(flour), pour(baking_powder), pour(baking_soda), mix()"),
                    ("Shape into 1-in balls.", "noop()"),
                    ("Roll in sugar.", "noop()"),
                    ("Place on greased baking sheet; flatten with a glass.", "scrape()"),
                    ("Bake at 350 degrees F for 10-12 minutes.", "preheat(350), bake(10)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
