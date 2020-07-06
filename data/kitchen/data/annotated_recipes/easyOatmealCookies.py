from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Easy Oatmeal Cookies #2"

recipeSource = "http://allrecipes.com/recipe/easy-oatmeal-cookies/"

#replace None with Physical Objects
ingredientsList = [("1 cup raisins", kitchenState.Ingredient(contains=["raisins"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['raisins']))),
                   ("1/2 cup hot water", kitchenState.Ingredient(contains=["water"], homogenous=True, amount="1/2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['water']))),
                   ("2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 cups",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("1 teaspoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 teaspoon",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['bakingsoda']))),
                   ("1 teaspoon salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 teaspoon",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['salt']))),
                   ("2 cups quick cooking oats", kitchenState.Ingredient(contains=["oats"], homogenous=True, amount="2 cups",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['oats']))),
                   ("1 teaspoon ground cinnamon", kitchenState.Ingredient(contains=["cinnamon"], homogenous=True, amount="1 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['cinnamon']))),
                   ("1 teaspoon ground nutmeg", kitchenState.Ingredient(contains=["nutmeg"], homogenous=True, amount="1 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=8, tags=['nutmeg']))),
                   ("1 cup packed brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 1, 1, 2), lcmId=9, tags=['brownsugar']))),
                   ("1/2 cup chopped walnuts", kitchenState.Ingredient(contains=["walnuts"], homogenous=True, amount="1/2 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 3, 1, 2), lcmId=10, tags=['walnuts']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 3, 1, 2), lcmId=10, tags=['eggs']))),
                   ("3/4 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="3/4 cup",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 3, 1, 2), lcmId=10, tags=['oil']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(1, 3, 1, 2), lcmId=10, tags=['vanilla'])))]



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat oven to 350 degrees F (175 degrees C).", "preheat(350)"),
                    ("Soak raisins in hot water and set aside.", "noop()"),
                    ("In large bowl, sift flour with soda, salt and spices.", "pour(baking_soda), pour(flour), pour(salt), pour(nutmeg), pour(cinnamon), mix()"),
                    ("Blend in rolled oats, sugar and nuts.", "pour(oats), pour(brown_sugar), pour(walnuts), mix()"),
                    ("In a separate bowl, beat eggs with fork and add oil, vanilla, and raisins and water mixture.", "pour(eggs), pour(oil), pour(vanilla_extract), pour(raisins), pour(water), mix()"),
                    ("Pour into dry ingredients, stirring until well mixed.", "mix()"),
                    ("Drop by teaspoonfuls about two inches apart onto ungreased cookie sheets.", "scrape()"),
                    ("Bake 10 to 13 minutes in the preheated oven, until the edges are golden.", "bake(10)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

