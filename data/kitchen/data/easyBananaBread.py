from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Easy Banana Bread"
recipeSource = "http://www.cooks.com/rec/view/0,174,144187-255202,00.html"


ingredientsList = [("1 1/2 c. self-rising flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 1/2 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['flour']))),
                   ("3 bananas, mashed", kitchenState.Ingredient(contains=["bananas"], homogenous=True, amount="3",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['bananas']))),

                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['eggs']))),
                   ("1/2 stick butter",  kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1/2 stick",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("1 tsp. vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['vanilla']))),
                   ("1 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['sugar']))),]

instructionsList = [("Cream together butter, eggs and sugar until smooth.",
                     "pour(butter), pour(eggs), pour(sugar), mix()"),
                    ("Add bananas and vanilla; beat well.", "pour(bananas), pour(vanilla_extract), mix()"), 
                    ("Mix in flour.", "pour(flour), mix()"),
                    ("Bake at 325 degrees F for about 1 hour or until golden brown.",
                     "scrape(), preheat(325), bake(60)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)


