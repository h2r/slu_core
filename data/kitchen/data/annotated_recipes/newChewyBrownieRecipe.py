from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject

#2 cups sugar
#1 1/2 cups all-purpose flour
#1/3 cup baking cocoa 1 1/2 teaspoons salt
#1 teaspoon baking powder
#1 cup vegetable oil
#4 eggs
#2 tablespoons light corn syrup 1 teaspoon vanilla extract
#1 cup chopped nuts confectioners' sugar
#Directions
#Calculate
#1. In a mixing bowl, combine sugar, flour, cocoa, salt and baking powder. Combine oil, eggs, corn syrup and vanilla; add to dry ingredients. Fold in nuts if desired. Spread in a greased 13-in.x 9-in.x 2-in. baking pan. Bake at 350 degrees F for 25-27 minutes or until a toothpick inserted near the center comes out clean. Dust with confectioners' sugar while warm if desired.


recipeName = "Chewiest Brownies"
recipeSource = "http://allrecipes.com/recipe/chewiest-brownies/"

#TODO need to fix the prisms
ingredientsList = [
                   ("2 cups sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="2 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['sugar']))),
                   ("1 1/2 cups all-purpose flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['flour']))),
                   ("1/3 cup baking cocoa", kitchenState.Ingredient(contains=["cocoa_powder"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=1, tags=['cocoa']))),
                   ("1 1/2 teaspoons salt", kitchenState.Ingredient(contains=["salt"], homogenous=True, amount="1 1/2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=7, tags=['salt']))),
                   ("1 1/2 teaspoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], homogenous=True, amount="1 1/2 teaspoons",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=6, tags=['bakingpowder']))),
                   ("1 cup vegetable oil", kitchenState.Ingredient(contains=["oil"], homogenous=True, amount="1 cup",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['oil']))),
                   ("4 eggs", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="4",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=3, tags=['eggs']))),
                   ("2 tablespoons light corn syrup", kitchenState.Ingredient(contains=["corn_syrup"], homogenous=True, amount="2 tablespoons",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['cornsyrup']))),
                   ("1 teaspoon vanilla extract", kitchenState.Ingredient(contains=["vanilla_extract"], homogenous=True, amount="1 teaspoon",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['vanilla']))),
                   ("1 cup chopped nuts", kitchenState.Ingredient(contains=["nuts"], homogenous=True, amount="1 cup",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=4, tags=['nuts'])))]

instructionsList = [("in a mixing bowl, combine sugar, flour, cocoa, salt and baking powder.", "pour(sugar), pour(flour), pour(cocoa_powder), pour(salt), pour(baking_powder), mix()"),
                    ("combine oil, eggs, corn syrup, and vanilla.", "pour(oil), pour(eggs), pour(corn_syrup), pour(vanilla_extract), mix()"),
                    ("add to dry ingredients.", "noop()"),
                    ("fold in nuts if desired.", "pour(nuts), mix()"),
                    ("spread in greased 13-in x 9-in x 2-in baking pan.", "scrape()"),
                    ("bake at 350 degrees F for 25-27 minutes or until a toothpick inserted near the center comes out clean.", "preheat(350), bake(25)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

