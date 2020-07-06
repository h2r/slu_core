from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName="CAKE MIX COOKIES"
recipeSource="http://www.cooks.com/rec/view/0,1610,130188-253193,00.html"
ingredientsList= [("1 package of cake mix (any flavor)",
                   kitchenState.Ingredient(contains=["cake_mix"], homogenous=True, amount="1 package",
                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['cake', 'mix']))),
                  ("1 large egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                          physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['eggs']))),
                  ("1/4 cup of oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1/4 cup",
                                                          physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['oil']))),
                  ("1/4 cup of water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="1/4 cup",
                                                               physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['water']))),
                  ("1 cup of chopped nuts, raisins, oatmeal, coconut, chocolate chips, etc. (anything you like in cookies)", kitchenState.Ingredient(contains=["toppings"], homogenous=True, amount="1 cup",
                                                               physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['toppings']))),
                  ]


instructionsList = [("Preheat oven to 350F.", "preheat(350)"),
                    ("Combine cake mix, egg, oil, and water.", "pour(cake_mix), pour(eggs), pour(oil), pour(water)"),
                    ("Beat until well blended. ", "mix()"),
                    ("Stir in remaining ingredient (s).", "pour(toppings), mix()"),
                    ("Drop by teaspoon about 1 inch apart onto greased cooke sheet.", "scrape()"),
                    ("Bake for 15 minutes or until done.", "bake(15)"),
                    ("Makes about 4 dozen. ", "noop()"), ("Yummy!", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)



