from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject


recipeName = "Quick and Easy Meatloaf"
recipeSource = "http://www.cooks.com/rec/view/0,1941,152172-241204,00.html"


ingredientsList = [("1 lb. ground beef", kitchenState.Ingredient(contains=["beef"], homogenous=True, amount="1 pound",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['beef']))),
                   ("1/4 c. chopped onions", kitchenState.Ingredient(contains=["onions"], homogenous=True, amount="1/4 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['onions']))),
                   ("1 slice white bread", kitchenState.Ingredient(contains=["bread"], homogenous=True, amount="1 slice",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['bread']))),
                   ("1 egg, beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['egg']))),
                   ("Ketchup", kitchenState.Ingredient(contains=["ketchup"], homogenous=True, amount="",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['ketchup']))),
                   ("Salt and pepper", kitchenState.Ingredient(contains=["salt", "pepper"], homogenous=True, amount="",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['salt_and_pepper']))),
                   ]

instructionsList = [("Preheat oven to 325 degrees.", "preheat(325)"),
                    ("Combine ground beef and chopped onions.", 
                     "pour(beef), pour(onions), mix()"),
                    ("Soak bread in beaten egg.", "pour(bread), pour(eggs), mix()"),
                    ("Combine with beef and onion.", "mix()"),
                    ("Shape into loaf.", "scrape()"),
                    ("Top with ketchup, salt, and pepper.", 
                     "pour(ketchup), (pour(salt) or pour(pepper))"),
                    ("Bake at 350 degrees for 1 hour.", "bake(60)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

