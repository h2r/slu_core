import shutil, glob, random
from kitchen import evaluatorGui, trainFromRecipes


#dst = "test_temp/"
#backup = "backup/"

def main(instruction_level=False):
    instruction_level=False
    
    iterations = 3
    interval_size = 5
    numberOfInstructionsTested = 0
    dirname = "data/"
    #2/15
    required_recipes = ["data/afghanDanielaRecipe.py", "data/easyOatmealCookieRecipe.py",
                    "data/quickSugarCookies.py", "data/quickAndEasyMeatloaf.py", "data/simplyBrownieRecipe.py",
                        "data/cakeMixCookiesRecipe.py", "data/yellowCakeRecipe.py", "data/easyPlatzRecipe.py",
                        "data/easyBreadPudding.py", "data/deepDishBrownieRecipe.py",
                        "data/fudgeyFudgeBrownies.py", "data/simpleCocoaBrowniesRecipe.py",
                        "data/chocolateFudgeCookiesRecipe.py", "data/panFudgeCakeRecipe.py",
                        "data/sugarCookiesRecipe.py"]
    #5/15
    required_recipes_better = ["data/afghanBiscuitsRecipe.py", "data/almondCrescentCookies.py",
                               "data/brownieRecipe.py", "data/cakeMixCookies.py",
                               "data/newChewiestBrowniesRecipe.py", "data/chocolateFudgeCookiesRecipe.py",
                               "data/crackedSugarCookiesRecipe.py", "data/easyBreadPudding.py",
                               "data/easySugarCookieRecipe.py", "data/flourlessPeanutButterCookiesRecipe.py",
                               "data/fudgeCrinklesRecipe.py", "data/healthyTurkeyMeatloaf.py",
                               "data/panFudgeCakeRecipe.py", "data/peachCobblerRecipe.py",
                               "data/simplyBrownieRecipe.py"]
    #4/15
    rr_average = ["data/cakeMixCookiesIVRecipe.py", "data/chocolateAfghanRecipe.py",
                  "data/chocolateChippers1Recipe.py", "data/chocolateFudgeCookiesRecipe.py",
                  "data/chocPBPuddingCookiesRecipe.py", "data/easiestBrowniesEver.py",
                  "data/easyBreadPudding.py", "data/easyOatmealCookieRecipe.py",
                  "data/easySugarCookieRecipe.py", "data/fudgeCrinklesRecipe.py",
                  "data/fudgeyFudgeBrownies.py", "data/intenselyChocolateBrowniesRecipe.py",
                  "data/peachCobblerRecipe.py", "data/simpleBrownieRecipe.py",
                  "data/sugarAndSpiceCookies.py"]
    
    required_recipes = rr_average
    masterResults = []
    masterFileList = glob.glob(dirname+"*.py")
    numberOfFiles = len(masterFileList)
    numberOfTrain = numberOfFiles - len(required_recipes)
    while iterations > 0:
        results = []
        movedRecipes = 0
        fileList = glob.glob(dirname+"*.py")
        for recipe in fileList:
            #Create a backup of all the recipes
            backup = recipe.replace("/", "/backup/")
            shutil.copy2(recipe, backup)
            #Move recipes to test_temp for testing
            if recipe not in required_recipes:
                print "Moving", recipe
                movedRecipes += 1
                dst = recipe.replace("/", "/test_temp/")
                shutil.move(recipe, dst)
        #Remove the required recipes from the filelist
        for j in required_recipes:
            print "Removing:", j
            fileList.remove(j)

        #Move a random recipe back for training
        randVal = random.randrange(0, len(fileList))
        currentRecipeFilename = fileList.pop(randVal)
        src = currentRecipeFilename.replace("/", "/test_temp/")
        shutil.move(src, "data/")
        movedRecipes -= 1
        
        #Perform initial training
        trainFromRecipes.main(forceFixedTestSet=True)
        
        #Evaluate
        if instruction_level:
            results.append((numberOfTrain-movedRecipes, evaluatorGui.runInstructionEvaluation()))
        else:
            results.append((numberOfTrain-movedRecipes, evaluatorGui.runEndToEndEvaluation()[1]))
        
        while movedRecipes > 0:
            #Move interval_size recipes at once
            for i in range(interval_size):
                if len(fileList) == 0:
                    continue
                randVal = random.randrange(0, len(fileList))
                currentRecipeFilename = fileList.pop(randVal)
                src = currentRecipeFilename.replace("/", "/test_temp/")
                shutil.move(src, "data/")
                movedRecipes -= 1
            trainFromRecipes.main(forceFixedTestSet=True)
            if instruction_level:
                results.append((numberOfTrain-movedRecipes, evaluatorGui.runInstructionEvaluation()))
            else:
                results.append((numberOfTrain-movedRecipes, evaluatorGui.runEndToEndEvaluation()[1]))
        
        print results
        masterResults.append(results)
        iterations -= 1
    print "\n\n\n\n Master Results:\n"
    print masterResults
    
    return 0

if __name__ == "__main__":
    main()
