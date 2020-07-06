from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Spring Green Salad"

recipeSource = "http://www.foodnetwork.com/recipes/tyler-florence/spring-green-salad-recipe/index.html"

#replace None with Physical Objects
ingredientsList = [("10 cups mixed greens", kitchenState.Ingredient(contains=["greens"], homogenous=True, amount="10 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['greens']))),
                   ("2 tablespoons finely chopped chives", kitchenState.Ingredient(contains=["chives"], homogenous=True, amount="2 tablespoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['chives']))),
                   ("Kosher salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="to taste",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['salt']))),
                   ("freshly ground black pepper", kitchenState.Ingredient(contains=["pepper"], homogenous=True, amount="to taste",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=4, tags=['pepper']))),
                   ("3 tablespoons extra-virgin olive oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="3 tablespoons",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=5, tags=['oil']))),
                   ("1/2 lemon, juiced", kitchenState.Ingredient(contains=["lemon"], homogenous=True, amount="1/2",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['lemon'])))]
#"all-purpose flour" vs "flour"



#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Wash and dry greens, place in a large bowl.", "pour(greens)"),
                    ("Add chives and season with salt and pepper.", "pour(chives), pour(salt), pour(pepper)"),
                    ("drizzle over about 2 tablespoons of olive oil.", "pour(oil)"),
                    ("Toss well to coat.", "mix()"),
                    ("Squeeze lemon juice over the greens and toss again.", "pour(lemon), mix()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
