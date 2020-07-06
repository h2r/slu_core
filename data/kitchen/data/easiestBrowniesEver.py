from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Easiest Brownies Ever"

recipeSource = "http://allrecipes.com/Recipe/Easiest-Brownies-Ever/Detail.aspx"

#replace None with Physical Objects
ingredientsList = [("1 cup butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("2 cups brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="2 cups",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['brown_sugar']))),
                   ("2 teaspoons vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="2 teaspoons",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanilla_extract']))),
					("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['eggs']))),
                   ("1 pinch salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 pinch",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['salt']))),
                   ("1 cup unsweetened cocoa powder", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cocoa_powder']))),
                   ("1 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour']))),
					("1 cup chopped walnuts", kitchenState.Ingredient(contains=["walnuts"], homogenous=True, amount="1 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['walnuts'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat the oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Grease a 9x11 inch baking dish. ", "grease()"),
                    ("In a large bowl, mix the butter and brown sugar until smooth. ", "pour(butter), pour(brown_sugar), mix()"),
					("Beat in the eggs one at a time, then stir in the vanilla extract.", "pour(eggs), mix(), pour(vanilla_extract), mix()"),
					("Mix in the flour, salt and cocoa powder just until moistened.", "pour(flour), pour(salt), pour(cocoa_powder), mix()"),
					("Stir in the walnuts, if using.", "pour(walnuts), mix()"),
					("Spread the batter evenly into the prepared pan.", "scrape()"),
					("Bake for 20 minutes in the preheated oven, or until the top is dry and the edges begin to pull away from the sides of the pan.", "bake(20)"),
					("Cool before cutting into squares.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

