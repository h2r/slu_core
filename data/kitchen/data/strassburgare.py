from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Strassburgare"

recipeSource = "http://allrecipes.com/recipe/strassburgare/detail.aspx"

#replace None with Physical Objects
ingredientsList = [("1 cup butter, softened", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1/2 cup confectioners' sugar", kitchenState.Ingredient(contains=["confection_sugar"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['confectionsugar']))),
                   ("1 1/2 tablespoons vanilla sugar", kitchenState.Ingredient(contains=["vanilla_sugar"], homogenous=True, amount="1 1/2 tablespoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['vanillasugar']))),
                   ("1 cup all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['flour']))),
                   ("1/2 cup potato flour", kitchenState.Ingredient(contains=["potato_flour"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['potatoflour']))),
                   ("1 drop red food coloring", kitchenState.Ingredient(contains=["food_coloring"], homogenous=True, amount="1 drop",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['foodcoloring'])))
                   ]



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat oven to 325 degrees F (165 degrees C).", "preheat(325)"),
                    ("With an electric mixer, beat the butter and confectioners' sugar together in a bowl until smooth and creamy.", "pour(butter), pour(confection_sugar), mix()"),
                    ("beat in the vanilla sugar.", "pour(vanilla_sugar), mix()"),
                    ("In a separate bowl, whisk the flour with potato flour.", "pour(flour), pour(potato_flour), mix()"),
                    ("Stir the flour mixture into the butter mixture, about 1/4 cup at a time, until all the flour is mixed in.", "mix()"),
                    ("Stir in the food coloring until the dough is evenly colored.", "pour(food_coloring), mix()"),
                    ("Place the dough into a cookie press fitted with a decorative tip.", "noop()"),
                    ("Press out 1 1/2-inch cookies onto an ungreased baking sheet.", "scrape()"),
                    ("Bake cookies in the preheated oven until the bottoms are just lightly browned, about 10 minutes.", "bake(10)"),
                    ("Allow to cool on the baking sheet for about 5 minutes before removing to finish cooling on wire racks.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

