from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#12
#Cracked Sugar Cookies I
#(http://allrecipes.com/recipe/cracked-sugar-cookies-i/detail.aspx)
#
#1 1/4 cups white sugar
#1 cup butter
#3 egg yolks
#1 teaspoon vanilla extract
#2 1/2 cups all-purpose flour 
#1 teaspoon baking soda
#1/2 teaspoon cream of tartar
#1. Preheat oven to 350 degrees F (180 degrees C). Lightly grease 2 cookie sheets. 2. Cream together sugar and butter. Beat in egg yolks and vanilla.
#3. Add flour, baking soda, and cream of tartar. Stir.
#4. Form dough into walnut size balls and place 2 inches apart on cookie sheet. Don't
#flatten. Bake 10 to 11 minutes, until tops are cracked and just turning color.

recipeName = "Cracked Sugar Cookies I"
recipeSource = "http://allrecipes.com/recipe/cracked-sugar-cookies-i/detail.aspx"

#TODO check the prism locations
ingredientsList = [("1 1/4 cups white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 1/4 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("1 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['butter']))),
                   ("3 egg yolks", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="3",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=4, tags=['vanilla']))),
                   ("2 1/2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 1/2 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("1 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['bakingsoda']))),
                   ("1/2 teaspoon cream of tartar", kitchenState.Ingredient(contains=["cream_of_tartar"], homogenous=True, amount="1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['creamoftartar'])))]

# this is where the second argument for pour comes in handy (since I want it in the cookie sheet)
# do I really want to scrape or should I just do it all in the cookie sheet?
instructionsList = [("1. Preheat oven to 350 degrees. (180 degrees C)", "preheat(350)"),
                    ("Lightly grease 2 cookie sheets", 'grease()'),
                    ("2. Cream together sugar and butter.", "pour(sugar), pour(butter), mix()"),
                    ("Beat in egg yolks and vanilla.", "pour(eggs), pour(vanilla_extract), mix()"),
                    ("3. Add flour, baking soda, and cream of tartar.", "pour(flour), pour(baking_soda), pour(cream_of_tartar)"),
                    ("Stir.", "mix()"),
                    ("4. Form dough into walnut size balls and place 2 inches apart on cookie sheet.", "scrape()"),
                    ("Don't flatten.", "noop()"),
                    ("bake 10 to 11 minutes, until tops are cracked and just turning color.", "bake(10)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
