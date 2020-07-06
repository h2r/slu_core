from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Almond Crescent Cookies"

recipeSource = "http://simplyrecipes.com/recipes/almond_crescent_cookies/"

#replace None with Physical Objects
ingredientsList = [("1 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("2/3 cup sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2/3 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla_extract']))),
					("1 teaspoon almond extract", kitchenState.Ingredient(contains=["almond_extract"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['almond_extract']))),
                   ("1 cup almond flour", kitchenState.Ingredient(contains=["almond_flour"], homogenous=True, amount="1 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['almond flour']))),
                   ("1/4 cup powdered sugar", kitchenState.Ingredient(contains=["powdered_sugar"], homogenous=True, amount="1/4 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['powdered sugar']))),
                   ("2 1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Cream the butter and the sugar together until light and fluffy.", "pour(butter), pour(sugar), mix()"),
                    ("Add the extracts and mix.", "pour(vanilla_extract), pour(almond_extract), mix()"),
                    ("Add the flour and almond flour.", "pour(almond_flour), pour(flour)"),
					("Mix thoroughly.", "mix()"),
					("Take generous tablespoons of the dough (it will be slightly crumbly) and roll it into a small ball, about an inch in diameter, and then shape into a crescent shape.", "noop()"),
					("Place onto parchment paper and bake at 350F for 15-20 minutes or until a light golden brown.", "scrape(), preheat(350), bake(20)"),
					("Dust with powdered sugar.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

