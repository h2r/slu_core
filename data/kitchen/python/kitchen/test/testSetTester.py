from kitchen.annotatedRecipe import Corpus
from kitchen import kitchen_features
import random
import pickle_util
from dcrf3.train_lccrf import train_lccrf
from dcrf3 import dataset
from g3.inference import nodeSearch
from g3.cost_functions.cost_function_random import CostFnRandom
from esdcs.dataStructures import ExtendedSdc
from standoff import TextStandoff
from g3.esdcs_to_ggg import ggg_from_esdc
from kitchen.planningLanguage import decompile

def negativeExamples(task_planner, fe, start_state, esdc, ggg, name, labeled_states):

    results = task_planner.find_plan(start_state, [ggg], save_state_tree=True,
                                     search_depth_event=4)
    observations = []
    labeled_actions = [decompile([(a, s)]) for a, s in labeled_states] 
    for i, (cost, state, ggg) in enumerate(results):
        state_sequence = task_planner.state_sequence(state)
        actions = [decompile([(a, s)]) for a, s in state_sequence] 
        overlap = False
        for a in actions:
            if a in labeled_actions:
                overlap = True
        #if not overlap or len(actions) != len(labeled_actions):
        if labeled_states[-1][1] != state_sequence[-1][1]:
            features = fe.features(ggg, ggg.factors[0], state_sequence)
            example_id = "%s_%d_neg" % (name, i)
            obs = dataset.ContinuousObservation(example_id, False, False, 
                                                features, sdcs=[esdc])
            observations.append(obs)
        
    return observations

def recipesToDataset(recipes):
    observations = []
    task_planner = nodeSearch.BeamSearch(CostFnRandom())
    fe = kitchen_features.GGGFeatures()
    for recipe in recipes:
        print "training", recipe.name


        for idx in range(recipe.num_instructions):
            instruction = recipe.idx_to_instruction(idx)
            esdc = ExtendedSdc("EVENT", instruction, 
                               r=TextStandoff(instruction, (0, len(instruction))))
            ggg = ggg_from_esdc(esdc)

            states = recipe.idx_to_states(idx)
            example_id = "%s_%d" % (recipe.name, idx)
            features = fe.features(ggg, ggg.factors[0], states)
            obs = dataset.ContinuousObservation(example_id, True, True, features,
                                                sdcs=[esdc])
            observations.append(obs)
            negative_obs = negativeExamples(task_planner, 
                                            fe,
                                            recipe.idx_to_start_state(idx),
                                            esdc, 
                                            ggg,
                                            example_id, states)
            observations.extend(negative_obs)
            
            
    return dataset.ContinuousDataset(observations)

def main(forceFixedTestSet=False):
    recipes = list(Corpus("data/"))
    recipes.sort(key=lambda ar: ar.name)
    test_set_names = []
    forced_test_set_recipes = []
    other_recipes = [r for r in recipes if not r.name in test_set_names]
    
    assert len(other_recipes) + len(forced_test_set_recipes) == len(recipes)
    assert len(forced_test_set_recipes) == len(test_set_names)
    training = []
    testing = []
    
    while len(other_recipes) > 0:
        if len(testing) < 15:
            randVal = random.randrange(0, len(other_recipes)-1)
            testing.append(other_recipes.pop(randVal))
        else:
            training.append(other_recipes.pop(0))

    #testing.extend(forced_test_set_recipes)

    training_dataset = recipesToDataset(training)
    pickle_util.save("training.pck", training_dataset)

    testing_dataset = recipesToDataset(testing)
    pickle_util.save("testing.pck", testing_dataset)


    train_lccrf(training_dataset, "kitchenModel.pck", sigma=1.5)    

    print "training on", len(training)
    print "testing on", len(testing)

if __name__ == "__main__":
    main()
