from kitchen import kitchenState, annotatedRecipe, planningLanguage, evaluatorGui, recipeManager
from esdcs.groundings import PhysicalObject, Prism
import pickle_util
import cProfile

recipeName = "Afghan Biscuits Daniela"
recipeSource = "Daniela"

#replace None with Physical Objects
ingredientsList = [("200g (7 oz) butter", kitchenState.Ingredient(contains=["butter"], homogenous=True, amount="200g (7 oz)",
                                                              physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 1, 1, 2), lcmId=1, tags=['butter']))),
                   ("75g (3 oz) sugar", kitchenState.Ingredient(contains=["sugar"], homogenous=True, amount="75g (3 oz)",
                                                           physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 1, 1, 2), lcmId=2, tags=['sugar']))),
                   ("175g (6 oz) flour", kitchenState.Ingredient(contains=["flour"], homogenous=True, amount="175g (6 oz) flour",
                                                                  physicalObject=PhysicalObject(kitchenState.prism_from_point(7, 1, 1, 2), lcmId=3, tags=['flour']))),
                   ("25g (1 oz) cocoa powder", kitchenState.Ingredient(contains=["cocoa"], homogenous=True, amount="25g (1 oz)",
                                                      physicalObject=PhysicalObject(kitchenState.prism_from_point(3, 3, 1, 2), lcmId=4, tags=['cocoa']))),
                   ("50g cornflakes (or crushed weetbix)", kitchenState.Ingredient(contains=["cornflakes"], homogenous=True, amount="50g",
                                                                   physicalObject=PhysicalObject(kitchenState.prism_from_point(5, 3, 1, 2), lcmId=5, tags=['cornflakes'])))]

#What should we do about the last 2 instructions? They are both unsupported/invalid.
#Will eventually move from strings to actual actions - NOT. We will pass the string to the compileAnnotation method in PlanningLanguage
instructionsList = [("Soften butter.", "pour(butter), mix()"),
                    ("Add sugar and beat to a cream.", "pour(sugar), mix()"),
                    ("Add flour and cocoa.", "pour(flour), pour(cocoa)"),
                    ("Add cornflakes last.", "pour(cornflakes), mix()"),
                    ("Put spoonfuls on a greased oven tray.", "scrape()"),
                    ("Bake about 15 minutes at 180 oC (350 oF).", "preheat(350), bake(15)")]

annotatedRecipeObject = annotatedRecipe.AnnotatedRecipe(recipeName, recipeSource, ingredientsList, instructionsList)


def test_dijkstra_simple():
    model_fname = "kitchenModel_1.5.pck"
    training_set = pickle_util.load("training.pck")
    rm = recipeManager.RecipeManager(model_fname)

    ingList = [("1/2 cup flour", kitchenState.Ingredient(contains=["flour"], homogenous=True,
                                                         amount="1/2 cup", physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2),
                                                                                                         lcmId = 5, tags=['Flour'])))]
    instList = [("Mix flour into mixing bowl.", "pour(flour), mix(flour)"),
                ("Preheat the oven to 350 F.", "preheat(350)"),
                ("Bake for 30 minutes.", "bake(30)")]
    ar = annotatedRecipe.AnnotatedRecipe("Temp Name", "Temp Source", ingList, instList)
    #result = rm.find_beam_plan(annotatedRecipeObject.instruction_text, annotatedRecipeObject.start_state)
    result = rm.find_dijkstra_plan(annotatedRecipeObject.instruction_text, annotatedRecipeObject.start_state)
    print result.cost

def prism_from_point(x,y,z1,z2):
     return Prism([(x-1, x+1, x+1, x-1), (y-1, y-1, y+1, y+1)], z1, z2)

command = """test_dijkstra_simple()"""
cProfile.runctx( command, globals(), locals(), filename="dijkstra_no_phyobj.profile" )
#cProfile.runctx( command, globals(), locals(), filename="dijkstra_phyobj.profile" )
#cProfile.runctx( command, globals(), locals(), filename="beam_5_no_phyobj.profile" )
