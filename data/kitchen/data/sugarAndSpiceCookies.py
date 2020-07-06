from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Sugar and Spice Cookies"

recipeSource = "http://allrecipes.com/recipe/sugar-and-spice-cookies/detail.aspx"

#replace None with Physical Objects
ingredientsList = [("1 3/4 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 3/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['flour']))),
                   ("1 teaspoon baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 teaspoon",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['bakingpowder']))),
                   ("1 teaspoon ground cinnamon", kitchenState.Ingredient(contains=["cinnamon"], homogenous=True, amount="1 teaspoon",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['cinnamon']))),
                   ("1/4 teaspoon ground nutmeg", kitchenState.Ingredient(contains=["nutmeg"], homogenous=True, amount="1/4 teaspoon",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['nutmeg']))),
                   ("1 pinch ground cloves", kitchenState.Ingredient(contains=["cloves"], homogenous=True, amount="1 pinch",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['cloves']))),
                   ("1/2 cup softened butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['butter']))),
                   ("1 cup packed brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['brownsugar']))),
                   ("1 egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=8, tags=['egg']))),
                   ("1/2 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1/2 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 1, 1, 2), lcmId=9, tags=['vanilla'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Mix the flour, the baking powder, cinnamon, nutmeg, and cloves together in a bowl.", "pour(flour), pour(baking_powder), pour(cinnamon), pour(nutmeg), pour(cloves), mix()"),
                    ("Cream the butter and brown sugar together with an electric mixer in a large bowl until smooth.", "pour(butter), pour(brown_sugar), mix()"),
                    ("beat the egg and vanilla extract into the butter mixture.", "pour(eggs), pour(vanilla_extract), mix()"),
                    ("Add the flour mixture in small amount to the butter mixture, beating each addition until blended.", "mix()"),
                    ("Form the dough into a ball, wrap with plastic wrap, and refrigerate at least 1 hour or up to 3 days.", "noop()"),
                    ("Preheat an oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Grease baking sheets.", "noop()"),
                    ("Roll the dough out on a floured work surface with a rolling pin to about 1/8-inch thickness.", "noop()"),
                    ("Cut with 2-inch cookie cutters.", "noop()"),
                    ("Arrange the cut cookies onto the prepared baking sheets.", "scrape()"),
                    ("Bake in the preheated oven until the edges begin to brown, 10 to 12 minutes.", "bake(10)"),
                    ("Allow the cookies to cool on the baking sheet for 1 minute before removing to a wire rack to cool completely.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

