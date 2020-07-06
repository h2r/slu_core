from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#28 
#Chocolate Chippers 1
#http://www.cooks.com/rec/doc/0,1710,147185-226194,00.html
#
#1/2 c. shortening
#1/2 c. granulated sugar
#1/4 c. brown sugar
#1 egg
#1 tsp. vanilla
#1 c. sifted all purpose flour
#3/4 tsp. salt
#1/2 tsp. baking soda
#1 (6 oz.) pkg. semi-sweet chocolate pieces 
#1/2 c. broken nuts
#
#Preheat oven to 375 degrees. Cream shortening, sugars, egg and vanilla until light and fluffy. Sift together dry ingredients; stir into creamed mixture; blend well. Add chocolate and nuts. Drop from teaspoon 2 inches apart on a greased cookie sheet. Bake in moderate oven (375 degrees) 10 to 12 minutes. Remove from sheet immediately. Makes 3 dozen cookies.

recipeName = "Chocolate Chippers 1"
recipeSource = "http://www.cooks.com/rec/doc/0,1710,147185-226194,00.html"

#replace None with Physical Objects
ingredientsList = [("1/2 c. shortening", kitchenState.Ingredient(contains=["shortening"], homogenous=True, amount="1/2 c.",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['shortening']))),
                   ("1/2 c. granulated sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="1/2 c.",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("1/4 c. brown sugar", kitchenState.Ingredient(contains=["brown_sugar"], homogenous=True, amount="1/4 c.",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=3, tags=['brownsugar']))),
                   ("1 egg", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="1",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['egg']))),
                   ("1 tsp. vanilla", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 tsp.",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=5, tags=['vanilla']))),
                   ("1 c. sifted all purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 c.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=6, tags=['flour']))),
                   ("3/4 tsp. salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="3/4 tsp.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ("1/2 tsp. baking soda", kitchenState.Ingredient(contains=["baking_soda"], homogenous=True, amount="1/2 tsp.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=8, tags=['bakingsoda']))),
                   ("1 (6 oz.) pkg. semi-sweet chocolate pieces", kitchenState.Ingredient(contains=["chocolate_chips"], homogenous=True, amount="1 (6 oz.) pkg.",
                                                                         physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 3, 1, 2), lcmId=9, tags=['chocolate']))),
                   ("1/2 c. broken nuts", kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="1/2 c.",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=10, tags=['nuts'])))]

#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Preheat oven to 375 degrees.", "preheat(375)"),
                    ("Cream shortening, sugars, egg and vanilla until light an fluffy.", "pour(shortening), pour(sugar), pour(brown_sugar), pour(eggs), pour(vanilla_extract), mix()"),
                    ("Sift together dry ingredients; stir into creamed mixture.", "pour(flour), pour(salt), pour(baking_soda), mix()"),
                    ("Add chocolate and nuts.", "pour(chocolate_chips), pour(nuts), mix()"),
                    ("Drop from teaspoon 2 inches apart on a greased cookie sheet.", "scrape()"),
                    ("Bake in moderate oven (375 degrees) 10 to 12 minutes.", "bake(10)"),
                    ("Remove from sheet immediately.", "noop()"),
                    ("Makes 3 dozen cookies.", "noop()")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

