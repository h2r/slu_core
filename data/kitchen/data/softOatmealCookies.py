from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Soft Oatmeal Cookies"

recipeSource = "http://allrecipes.com/recipe/soft-oatmeal-cookies/"

#replace None with Physical Objects
ingredientsList = [("1 cup butter, softened", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 cup white sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['whitesugar']))),
                   ("1 cup packed brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1 cup",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['brownsugar']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['eggs']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['vanilla']))),
                   ("2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 cups",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['flour']))),
                   ("1 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['bakingsoda']))),
                   ("1 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=8, tags=['salt']))),
                   ("1 1/2 teaspoons ground cinnamon", kitchenState.Ingredient(contains=["cinnamon"], homogenous=True, amount="1 1/2 teaspoons",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 1, 1, 2), lcmId=9, tags=['cinnamon']))),
                   ("3 cups quick cooking oats", kitchenState.Ingredient(contains=["oats"], homogenous=True, amount="3 cups",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 3, 1, 2), lcmId=10, tags=['oats'])))]



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("In a medium bowl, cream together butter, white sugar, and brown sugar.", "pour(butter), pour(sugar), pour(brown_sugar), mix()"),
                    ("Beat in eggs one at a time, then stir in vanilla.", "pour(eggs), pour(vanilla_extract), mix()"),
                    ("Combine flour, baking soda, salt, and cinnamon.", "pour(flour), pour(baking_soda), pour(salt), pour(cinnamon), mix()"),
                    ("stir into the creamed mixture.", "mix()"),
                    ("Mix in oats.", "pour(oats), mix()"),
                    ("Cover, and chill dough for at least one hour.", "noop()"),
                    ("Preheat the oven to 375 degrees F (190 degrees C).", "preheat(375)"),
                    ("Grease cookie sheets.", "grease()"),
                    ("Roll the dough into walnut sized balls, and place 2 inches apart on cookie sheets.", "scrape()"),
                    ("Flatten each cookie with a large fork dipped in sugar.", "noop()"),
                    ("Bake for 8 to 10 minutes in preheated oven.", "bake(8)"),
                    ("Allow cookies to cool on baking sheet for 5 minutes before transferring to a wire rack to cool completely.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

