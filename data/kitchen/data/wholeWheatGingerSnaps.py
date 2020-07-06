from kitchen import kitchenState, annotatedRecipe
from esdcs.groundings import PhysicalObject
# Whole Wheat Ginger Snaps
recipeSource= "http://allrecipes.com/recipe/whole-wheat-ginger-snaps/detail.aspx"
recipeName = "Whole Wheat Ginger Snaps"


ingredientsList = [("1 cup butter or margarine", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="1 cup")),
                   ("1 1/2 cups white sugar", kitchenState.Ingredient(contains=["eggs"], homogenous=True, amount="2")),
                   ("1 cup molasses", kitchenState.Ingredient(contains=["molasses"], homogenous=True, amount="1 cup")),
                   ("4 cups whole wheat flour", kitchenState.Ingredient(contains=["flour"], 
                                                                        homogenous=True, amount="4 cups")),
                   ("1 tablespoon baking soda", kitchenState.Ingredient(contains=["baking_soda"], 
                                                                        homogenous=True, amount="1 tablespoon")),
                   ("2 teaspoons baking powder", kitchenState.Ingredient(contains=["baking_powder"], 
                                                                         homogenous=True, amount="2 teaspoons")),                  
                   ("1 tablespoon ground ginger", kitchenState.Ingredient(contains=["ginger"], 
                                                                         homogenous=True, amount="1 tablespoon")),                  
                   
                   ("1 1/2 teaspoons ground nutmeg", kitchenState.Ingredient(contains=["nutmeg"], 
                                                                         homogenous=True, amount="1 1/2 teaspoons")),                  
                   
                   ("1 1/2 teaspoons ground cinnamon", kitchenState.Ingredient(contains=["cinnamon"], 
                                                                         homogenous=True, amount="1 1/2 teaspoons")),                  
                   ("1 1/2 teaspoons ground cloves", kitchenState.Ingredient(contains=["cloves"], 
                                                                         homogenous=True, amount="1 1/2 teaspoons")),                  
                   ("1 1/2 teaspoons ground allspice", kitchenState.Ingredient(contains=["allspice"], 
                                                                         homogenous=True, amount="1 1/2 teaspoons")),                  
                   ("1 cup white sugar for decoration", kitchenState.Ingredient(contains=["sugar"], 
                                                                               homogenous=True, amount="1 cup")),                  ]
                   


instructionsList = [("Preheat the oven to 350 degrees F (175 degrees C).", "preheat(350)"),
 ("Grease cookie sheets.", "grease()"),
 ("In a large bowl, cream together the butter and 1 1/2 cups of sugar until smooth.", "pour(butter), pour(sugar), mix()"),
 ("Mix in the eggs, and then the molasses.", "pour(eggs), pour(molasses), mix()"),
 ("Combine the whole wheat flour, baking soda, baking powder, ginger, nutmeg, cinnamon, cloves, and allspice, heaping the measures if you like a lot of spice.", "pour(flour), pour(baking_powder), pour(ginger), pour(nutmeg), pour(cinnamon), pour(cloves), pour(allspice)"),
 ("Stir the dry ingredients into the molasses mixture just until blended.", "mix()"),
 ("Roll the dough into small balls, and dip the top of each ball into the remaining white sugar. ", "noop()"),
 ("Place the cookies about 2 inches apart on the cookie sheets.", "scrape()"),
 ("Bake for 10 to 15 minutes in the preheated oven, until the tops are cracked.", "bake(10)"),
 ("Bake longer for crispy cookies, less time for chewy cookies.", "noop()"),
 ("Cool on wire racks.", "noop()")]



annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)

