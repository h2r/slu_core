from kitchen import kitchenState, recipeManager, annotatedRecipe, planningLanguage
import pickle_util

def main():
    training_set = pickle_util.load("training.pck")
    totalRecipes = 0
    totalIngredients = 0
    ingredientsList = []
    arc = annotatedRecipe.Corpus(training_set=training_set)
    recipeCorpus = arc.recipes
    for i in recipeCorpus:
        totalRecipes += 1
        for j in i.ingredients:
            if j[1].contains[0] == "onion":
                print i.name
            if j[1].contains[0] not in ingredientsList:
                ingredientsList.append(j[1].contains[0])
            totalIngredients += 1
    ingredientsList.sort()
    print "\n\n\n"
    print "Total Recipes:", totalRecipes
    print "Total Ingredients", totalIngredients
    print "Ingredient List:", ingredientsList
    print "\n\n\n"
    return 1

if __name__ == "__main__":
    main()
