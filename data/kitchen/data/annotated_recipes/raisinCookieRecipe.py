from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#Raisin Cookies #1
#http://www.cooks.com/rec/doc/0,1610,151175-255201,00.html

recipeName = "Raisin Cookies #1"

recipeSource = "http://www.cooks.com/rec/doc/0,1610,151175-255201,00.html"

ingredientsList = [("1 c. raisins", kitchenState.Ingredient(contains=["raisins"], homogenous=True, amount="1 c.",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['raisins']))),
                   ("1 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 c.",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1 c. shortening", kitchenState.Ingredient(contains=["shortening"], homogenous=True, amount="1 c.",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['shortening']))),
                   ("2 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['eggs']))),
                   ("2 c. quick oatmeal", kitchenState.Ingredient(contains=["oatmeal"], homogenous=True, amount="2 c.",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['oatmeal']))),
                   ("1 tsp. soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1 tsp.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['soda']))),
                   ("1/2 c. nuts, optional", kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="1/2 c.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 1, 1, 2), lcmId=7, tags=['nuts']))),
                   ("2 c. flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="2 c.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(9, 3, 1, 2), lcmId=8, tags=['flour'])))]

#"Add other ingredients" doesn't have an explicit order
instructionsList = [("Cook raisins in one cup water; cool.", "noop()"),
                    ("Cream sugar and shortening.", "pour(sugar), pour(shortening), mix()"),
                    ("Add eggs, beat well.", "pour(eggs), mix()"),
                    ("Add raisin mixture and other ingredients.", "pour(raisins), pour(oatmeal), pour(baking_soda), pour(nuts), pour(flour), mix()"),
                    ("Drop by spoonfuls on cookie sheet.", "scrape()"),
                    ("Bake about 10 minutes in 350 degree oven. Do not over bake.", "preheat(350), bake(10)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)
