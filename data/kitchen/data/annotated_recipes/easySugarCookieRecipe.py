from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#11
#Easy Sugar Cookies
#(http://allrecipes.com/recipe/easy-sugar-cookies/detail.aspx)
#
#2 3/4 cups all-purpose flour 
#1 teaspoon baking soda
#1/2 teaspoon baking powder 
#1 cup butter, softened
#1 1/2 cups white sugar
#1 egg
#1 teaspoon vanilla extract
#
#1. Preheat oven to 375 degrees F (190 degrees C). In a small bowl, stir together flour, baking soda, and baking powder. Set aside.
#2. In a large bowl, cream together the butter and
#sugar until smooth. Beat in egg and vanilla.  Gradually blend in the dry ingredients. Roll rounded teaspoonfuls of dough into balls, and place onto ungreased cookie sheets.
#3. Bake 8 to 10 minutes in the preheated oven, or until golden. Let stand on cookie sheet two minutes before removing to cool on wire racks.

recipeName = "Easy Sugar Cookies"
recipeSource = "http://allrecipes.com/recipe/easy-sugar-cookies/detail.aspx"

#TODO check the prism locations
ingredientsList = [("2 3/4 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 3/4 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['flour']))),
                   ("1 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 teaspoon",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['bakingsoda']))),
                   ("1/2 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['bakingpowder']))),
                   ("1 cup butter, softened", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=4, tags=['butter']))),
                   ("1 1/2 cups white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/2 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['sugar']))),
                   ("1 egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=6, tags=['egg']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['vanilla'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 375 degrees. (190 degrees C)", "preheat(375),"),
                    ("2. In a small bowl, stir together flour, baking soda, and baking powder.  Set aside.", "pour(flour), pour(baking_soda), pour(baking_powder), mix()"),
                    ("Beat in egg and vanilla.", "pour(eggs), pour(vanilla_extract), mix()"),
                    ("Gradually blend in the dry ingredients.", "mix()"),
                    ("Roll rounded teaspoonfulls of dough into balls, and place onto ungreased cookie sheets.", "scrape()"),
                    ("Bake 8 to 10 minutes in the preheated oven, or until golden.", "bake(8)"),
                    ("Let stand on cookie sheet two minutes before removing to cool on wire racks.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
