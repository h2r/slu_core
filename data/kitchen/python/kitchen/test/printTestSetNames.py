from kitchen import kitchenState, recipeManager, annotatedRecipe, planningLanguage
import pickle_util

def main():
    training_set = pickle_util.load("training.pck")
    arc = annotatedRecipe.Corpus(training_set=training_set)
    recipeCorpus = arc.recipes
    for i in recipeCorpus:
        if i.is_training_set == False:
            print i.name

if __name__ == "__main__":
    main()
