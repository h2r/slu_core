from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Simple Brownie Recipe"

recipeSource = "http://www.squidoo.com/simple-brownie-recipe"

#replace None with Physical Objects
ingredientsList = [("1 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['vegetable_oil']))),
                   ("2 cups sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla_extract']))),
					("4 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1/ teaspoons salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 pinch",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['salt']))),
                   ("2/3 cup  cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="2/3 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cocoa_powder']))),
                   ("1 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour']))),
					("1/2 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1/2 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['baking_powder'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat your oven to 350 while you are preparing the Brownie Mix.", "preheat(350)"),
                    ("Mix the oil, sugar, eggs and vanilla till they are well blended.", "pour(oil), pour(sugar), pour(eggs), pour(vanilla_extract), mix()"),
                    ("Mix all the dry ingredients together separately.", "pour(salt), pour(cocoa_powder), pour(flour), pour(baking_powder)"),
					("Add the dry ingredients to the egg mixture.", "mix()"),
					("Pour into a 9 x 13 baking dish or pan.", "scrape()"),
					("Bake for about 30 minutes or until the Brownies start to separate from the edges of the baking dish or pan.", "bake(30)"),
					("Let cool toughly and Enjoy.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

