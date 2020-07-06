from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject


recipeName="EASY BLUEBERRY COBBLER"
recipeSource="http://www.cooks.com/rec/view/0,186,143161-232207,00.html"
ingredientsList= [("3/4 stick butter",
                   kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="3/4 stick",
                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['butter']))),
                  ("3/4 cup sugar",                   
                   kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="3/4 cup",
                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                  ("1 cup self-rising flour",                   
                   kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['flour']))),
                  ("1 cup milk",
                  kitchenState.Ingredient(contains=["milk"], homogenous=True, amount="1 cup",
                                          physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['milk']))),
                  ("1 can blueberry pie filling",  kitchenState.Ingredient(contains=["filling"], homogenous=True, amount="1 can",
                                          physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['pie', 'filling', 'blueberry'])))]

instructionsList = [("Preheat oven to 350F.", "preheat(350)"),
                    ("Melt butter and pour into a 2.5 or 3 quart casserole baking.", "pour(butter)"),
                    ("Mix sugar, flour and milk.", "pour(sugar), pour(flour), pour(milk), mix()"),
                    ("Pour mixture over butter, but do not mix.", "scrape()"),
                    ("Pour the pie filling on top, but do not mix.", "pour(filling)"),
                    ("Bake at 350F for 1 hour.", "bake(60)"),
                    ("Serve warm with ice cream or as is.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

