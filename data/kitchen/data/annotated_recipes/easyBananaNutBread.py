from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Easy Banana Nut Bread"
recipeSource = "http://www.cooks.com/rec/doc/0,174,146186-252203,00.html"


ingredientsList = [("1 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("2 eggs, slightly beaten", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['eggs']))),

                   ("2 c. Bisquick", kitchenState.Ingredient(contains=["bisquick"], homogenous=True, amount="2 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['bisquick']))),
                   ("1 c. chopped nuts",  kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['nuts']))),
                   ("1/4 c. shortening", kitchenState.Ingredient(contains=["shortening"], homogenous=True, amount="1/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['shorening']))),
                   ("1 c. crushed very ripe bananas (2-3)", kitchenState.Ingredient(contains=["bananas"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['bananas']))),]

instructionsList = [("Cream sugar and shortening.", "pour(sugar), pour(shortening), mix()"),
                    ("Add eggs, bananas, Bisquick and nuts; stir until well mixed.", "pour(eggs), pour(bananas), pour(bisquick), pour(nuts), mix()"),
                    ("Pour into greased and floured 9 x 5 x 3 inch pan.", "scrape()"),
                    ("Bake 1 hour at 350 degrees.", "preheat(350), bake(60)"),
                    ("Remove from pan and on rack before slicing.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)


