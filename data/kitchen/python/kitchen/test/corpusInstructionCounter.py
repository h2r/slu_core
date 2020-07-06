from kitchen import kitchenState, recipeManager, annotatedRecipe, planningLanguage
import pickle_util

def main():
    training_set = pickle_util.load("training.pck")
    totalRecipes = 0
    totalInstructions = 0
    arc = annotatedRecipe.Corpus(training_set=training_set)
    recipeCorpus = arc.recipes
    for i in recipeCorpus:
        totalRecipes += 1
        for j in i.instructions:
            totalInstructions += 1
    print "\n\n\n"
    print "Total Recipes:", totalRecipes
    print "Total Instructions", totalInstructions
    print "\n\n\n"
    return 1

if __name__ == "__main__":
    main()
