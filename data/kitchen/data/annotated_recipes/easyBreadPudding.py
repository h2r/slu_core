from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Easy Bread Pudding"
recipeSource = "http://www.cooks.com/rec/view/0,1740,149185-250203,00.html"


ingredientsList = [("4 slices buttered toast", kitchenState.Ingredient(contains=["bread"], homogenous=True, amount="3",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['bread']))),
                   ("1 (20 oz.) can peaches", kitchenState.Ingredient(contains=["peaches"], homogenous=True, amount="1 can",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['peaches']))),

                   ("3 eggs, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="3",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['eggs']))),
                   ("1/3 c. sugar",  kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1/3 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("Dash of salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="dash",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['salt']))),
                   ("1/2 tsp. nutmeg", kitchenState.Ingredient(contains=["nutmeg"], homogenous=True, amount="1/2 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['nutmeg']))),

                   ("1 tsp. vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['vanilla']))),
                   ("3 c. milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="3 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['milk']))),
]

instructionsList = [("Place toast in bottom of deep baking dish.", 
                     "pour(bread)"),
                    ("Drain peaches and save juice.", "noop()"),
                    ("Put peaches over top of toast.", "pour(peaches)"),
                    ("Mix other ingredients and 1/2 of peach juice.",
                     "pour(eggs), pour(sugar), pour(salt), pour(nutmeg), pour(vanilla_extract), pour(milk), mix()"),
                    ("Pour over fruit and toast.", "scrape()"),
                    ("Bake 45 minutes at 350 degrees F.", "preheat(350), bake(45)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)









