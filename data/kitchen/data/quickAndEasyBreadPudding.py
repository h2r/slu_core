from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Quick and Easy Bread Pudding"
recipeSource = "http://www.cooks.com/rec/view/0,1940,155168-242204,00.html"


ingredientsList = [("3 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="3",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['eggs']))),
                   ("2 cups milk or skim milk", kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="2 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['milk']))),

                   ("1/2 pound light brown sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1/2 pound",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("4 slices wheat or white bread",  kitchenState.Ingredient(contains=["bread"], homogenous=True, amount="4 slices",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['bread']))),
                   ("2 Tbsps. butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="2 tbsps",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),]

instructionsList = [("Beat eggs lightly.", "pour(eggs), mix()"),
                    ("Add milk, sugar, crumbled bread and pour into a 1 quart baking dish.", "pour(milk), pour(sugar), pour(bread), scrape()") ,
                    ("Dot with butter and bake 40-45 minutes until firm and brown at 350 degrees.", "preheat(350), bake(40)"),
                    ("Serves 6.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
