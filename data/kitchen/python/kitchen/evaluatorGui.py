from kitchen import kitchenState, recipeManager, annotatedRecipe, planningLanguage
import pickle_util


class Evaluator():
    def __init__(self):
        self.score = 0
        self.successCount = 0
        self.totalCount = 0
        self.noopSuccessCount = 0
    def evaluateInstructions(self, targetRecipe):
        #Can a single instruction be interpreted as multiple instructions? Does it even matter?
        model_fname = "kitchenModel_1.5.pck"
        rm = recipeManager.RecipeManager(model_fname)
        pl = planningLanguage.PlanningLanguage()
        tc = 0
        sc = 0
        nsc = 0
        
        
        #A list of (planningLanguage, is_correct) tuples. Used mainly for GUI
        completePath = []
        
        print "Evaluating (instruction-level): " + targetRecipe.name
        for i in range(len(targetRecipe.instructions)):

            self.totalCount += 1
            tc += 1
            instruction = targetRecipe.instructions[i]
            #print "instruction", instruction
            initialState = targetRecipe.idx_to_start_state(i)
            instructionInferredPlan = rm.find_plan(instruction[0], initialState)
            desiredPlan = pl.compileAnnotation(instruction[1], initialState)
            desiredEndState = desiredPlan[-1][1]

            if len(instructionInferredPlan) == 0:
                #print "Zero length instruction for:", instruction
                if len(desiredPlan) == 1:
                    if desiredPlan[-1][0].name == "noop":
                        self.noopSuccessCount += 1
                        nsc += 1
                        completePath.append(("| noop()", True))
                    else:
                        completePath.append(("None", False))
                else:
                    completePath.append(("None", False))
            else:
                #print "inferred plan", instructionInferredPlan
                actualEndState = instructionInferredPlan[-1][1][-1][1]
                #print "actualEndState", actualEndState
                #plInferredPath = planningLanguage.decompile(instructionInferredPlan[-1][1])
                plInferredPath = ""
                for i in instructionInferredPlan:
                    plInferredPath = plInferredPath + " | " + planningLanguage.decompile(i[1])
                if desiredEndState == actualEndState:
                    self.successCount += 1
                    sc += 1
                    print instructionInferredPlan
                    completePath.append((plInferredPath, True))
                else:
                    completePath.append((plInferredPath, False))
                    print "State is not the same for instruction", instruction
                    print "Inferred path was: ", planningLanguage.decompile(instructionInferredPlan[0][1])
##                    print "Desired mixing bowl:", desiredEndState.mixing_bowl
##                    print "Actual mixing bowl:", actualEndState.mixing_bowl
                    print "\n"
                        
        print "\n\nResults for the instruction-level evaluation of :", targetRecipe.name
        print "Total Instructions:", tc, "\nSuccess:", sc
        print "Noop Success:", nsc
        print "Failures:", tc - (sc+nsc), "\n\n"
        return completePath

    def evaluateEndToEnd(self, targetRecipe, useBeam=True):
        #A list of (planningLanguage, is_correct) tuples. Used mainly for GUI
        completePath = []

        self.totalCount += 1
        model_fname = "kitchenModel_1.5.pck"
        training_set = pickle_util.load("training.pck")
        rm = recipeManager.RecipeManager(model_fname)
        pl = planningLanguage.PlanningLanguage()
        print "\nEvaluating (end-to-end):", targetRecipe.name
        recipeText = targetRecipe.instruction_text
        initialState = targetRecipe.start_state

        if useBeam:
            inferredPlan = rm.find_beam_plan(recipeText, initialState)
        else:
            inferredPlan = rm.find_plan(recipeText, initialState)
        
        print "\ninferred", inferredPlan
        actualEndState = inferredPlan[-1][1][-1][1]
        print "\ndesired states", targetRecipe.states
        
        desiredEndState = targetRecipe.states[-1][-1][1]
        
        plInferredPath = ""
        for i in inferredPlan:
            plInferredPath = plInferredPath + " | " + planningLanguage.decompile(i[1])
        print "\nPL inferred:", plInferredPath
        plActual = ""
        for i in targetRecipe.instructions:
            plActual = plActual + " | " + i[1]
        print "\nPL Desired:", plActual, "\n"
        #print desiredEndState
        #print "end state", actualEndState

        
        
        if desiredEndState == actualEndState:
            self.successCount += 1
            print "\n\nResults for the End-to-End evaluation for :", targetRecipe.name
            print "Success"
        else:
            print "\nResults for the End-to-End evaluation for :", targetRecipe.name
            print "Failure"
        return 0
        
        
        


def runInstructionEvaluation(runTestSet=True):
    training_set = pickle_util.load("training.pck")
    totalRecipes = 0
    arc = annotatedRecipe.Corpus(training_set=training_set)
    recipeCorpus = arc.recipes
    ev = Evaluator()
    for i in recipeCorpus:
        if i.is_training_set == runTestSet:
            continue
        totalRecipes += 1
        ev.evaluateInstructions(i)
    
    print "\n\nOverall results for the entire instruction-level evaluation."
    print "Total Recipes:", totalRecipes
    print "Total Instructions:", ev.totalCount, "\nSuccess:", ev.successCount
    print "Noop Success:", ev.noopSuccessCount
    print "Failures:", ev.totalCount - (ev.successCount+ev.noopSuccessCount)
    right = ev.successCount + ev.noopSuccessCount
    print "%.3f%% (%d/%d)" % (float(right)/ev.totalCount * 100, 
                              right, ev.totalCount)
    print "\n\n"
    return (ev.totalCount, ev.successCount, ev.noopSuccessCount)



def runEndToEndEvaluation(runTestSet=True):
    training_set = pickle_util.load("training.pck")
    totalRecipes = 0
    arc = annotatedRecipe.Corpus(training_set=training_set)
    recipeCorpus = arc.recipes
    ev = Evaluator()
    for i in recipeCorpus:
        if i.is_training_set == runTestSet:
            continue
        totalRecipes += 1
        result = ev.evaluateEndToEnd(i)
        if result != 0:
            print "Failure 1"
            return 1
        
    print "\n\nOverall results for the entire end-to-end evaluation."
    print "Total Recipes:", totalRecipes
    print "Success:", ev.successCount
    print "Failures:", ev.totalCount - ev.successCount
    right = ev.successCount + ev.noopSuccessCount
    print "%.3f%% (%d/%d)" % (float(right)/ev.totalCount * 100, 
                              right, ev.totalCount)
    print "\n\n"
    return (totalRecipes, ev.successCount)

def main(argv):
    eArg = 0
    print "arg", argv
    for i in argv:
        if "--evaluate=" in i:
            j = i.replace("--evaluate=", "")
            eArg = int(j)
    print eArg
    if eArg == 1:
        runInstructionEvaluation()
    elif eArg == 2:
        runEndToEndEvaluation()
    else:
        print "Error with the args"

if __name__=="__main__":
    import sys
    main(sys.argv)









