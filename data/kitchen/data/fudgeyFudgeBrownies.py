from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

recipeName = "Fudgy Fudge Brownies"
recipeSource = "http://www.cooks.com/rec/view/0,1613,137191-247197,).html"


ingredientsList = [("1 1/4 c. flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 1/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['flour']))),
                   ("1/4 c. cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cocoa']))),

                   ("1 tsp. baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['backing_powder']))),
                   ("1/2 tsp. salt",  kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1/2 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['salt']))),
                   ("3 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="3",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['eggs']))),
                   ("2 c. sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2 cups",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['sugar']))),
                   ("3/4 c. butter, melted", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="3/4 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),

                   ("1 tsp. vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 tsp",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['vanilla']))),
                   ("1 c. chopped walnuts (optional)", kitchenState.Ingredient(contains=["walnuts"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['walnuts']))),
]
instructionsList = [("Stir together flour, cocoa, baking powder, salt and walnuts.", "pour(flour), pour(cocoa_powder), pour(baking_powder), pour(salt), pour(walnuts), mix()"),
                    ("Mix well.", "mix()"),
                    ("Set aside.", "noop()"),
                    ("In large bowl, combine eggs, sugar, butter and vanilla.",
                     "pour(eggs), pour(sugar), pour(butter), pour(vanilla_extract)"),
                    ("Beat with wooden spoon until smooth.", "mix()"),
                    ("Stir in dry ingredients; mix well.","mix()"),
                    ("Spread batter evenly in 13 X 9 inch pan.", "scrape()"),
                    ("Bake in 350oF oven for about 25 minutes.", "preheat(350), bake(25)"),
                    ("Do not overbake.", "noop()"),
                    ("Brownies are ready when edges are just set and center is still soft.", "noop()"),
                    ("Cool on wire rack.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)












