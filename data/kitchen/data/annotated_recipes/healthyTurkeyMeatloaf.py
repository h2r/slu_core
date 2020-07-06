from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Healthy and Easy Turkey Meatloaf"
recipeSource = "http://www.cooks.com/rec/view/0,2226,159182-235200,00.html"

#replace None with Physical Objects
ingredientsList = [("1 to 1 1/2 lbs. of lean ground turkey, uncooked", kitchenState.Ingredient(contains=["turkey"], homogenous=True, amount="1 to 1 1/2 pounds",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['turkey']))),
                   ("1/2 green pepper, diced", kitchenState.Ingredient(contains=["green_pepper"], homogenous=True, amount="1/2",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['green_pepper']))),
                   ("1/2 red pepper, diced", kitchenState.Ingredient(contains=["red_pepper"], homogenous=True, amount="1/2",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['red_pepper']))),
                   ("1 egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['egg']))),
                   ("1/2 cup of plain breadcrumbs", kitchenState.Ingredient(contains=["breadcrumbs"], homogenous=True, amount="1/2 cup",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['breadcrumbs'])))]

instructionsList = [("In a large mixing bowl, mix together the uncooked ground turkey with the peppers and egg.", "pour(red_pepper), pour(green_pepper), pour(eggs), mix()"),
                    ("Mix together until egg yolk has spread to all areas of the mixture (works best if you mix with your hands).", "mix()"),
                    ("Add the breadcrumbs and lightly mix around with hands (do not over touch the mixture).", "pour(breadcrumbs), mix()"),
                    ("Put into a greased loaf pan in the oven for 40 minutes at 350 degrees F or until center of loaf reads 160 degrees F on an instant-read thermometer.",
                     "preheat(350), bake(40)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

