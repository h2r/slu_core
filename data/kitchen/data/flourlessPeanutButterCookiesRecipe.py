from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#17
#Flourless Peanut Butter Cookies
#http://www.food.com/recipe/flourless-peanut-butter-cookies-17943
#
#1 cup peanut butter
#1 cup sugar
#1 large egg , beaten
#1 teaspoon baking soda
#
#1 Preheat oven to 350* and grease cookie sheets.
#2 Beat together peanut butter and sugar in a large bowl with an electric mixer until smooth.
#3 Add beaten egg and baking soda to peanut butter mixture and beat until well combined.
#4 Roll 1 teaspoon of dough into a ball and place on cookie sheet .
#5 Bake until puffed and golden pale, about 10 minutes.
#6 Cool cookies on baking sheet about 2 minutes and then transfer with spatula to rack to cool

recipeName = "Flourless Peanut Butter Cookies"
recipeSource = "http://www.food.com/recipe/flourless-peanut-butter-cookies-17943"

#replace None with Physical Objects
ingredientsList = [("1 cup peanut butter", kitchenState.Ingredient(contains=["peanut_butter"], homogenous=True, amount="1 cup peanut butter",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['peanutbutter']))),
                   ("1 cup sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 large egg, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['bakingsoda'])))]

instructionsList = [("1 Preheat oven to 350* and grease cookie sheets.", "preheat(350), grease()"),
                    ("2 Beat together peanut butter and sugar in a large bowl with an electric mixter until smooth.", "pour(peanut_butter), pour(sugar), mix()"),
                    ("3 Add beaten egg and baking soda to peanut buter mixture and beat until well combined.", "pour(eggs), pour(baking_soda), mix()"),
                    ("4 Roll 1 teaspoon of dough into a ball and place on cookie sheet.", "scrape()"),
                    ("5 Bake until puffed and golden pale, about 10 minutes.", "bake(10)"),
                    ("6 Cool cookies on baking sheet about 2 minutes and then transfer with spatula to rack and cool.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

