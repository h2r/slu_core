from g3.inference import nodeSearch
from g3.cost_functions.cost_function_crf import CostFnCrf
from esdcs.dataStructures import ExtendedSdc
from sentenceTokenizer import SentenceTokenizer
from standoff import TextStandoff
from g3.esdcs_to_ggg import ggg_from_esdc
from kitchen import kitchen_features
import math
import copy


class RecipeManager:
    """
    This is the high-level class that manages calls to recipe
    inference.
    """

    def __init__(self, model_fname):
        self.newcf = CostFnCrf.from_mallet(model_fname, guiMode=True,
                                           feature_extractor_cls=kitchen_features.GGGFeatures)
        self.task_planner = nodeSearch.BeamSearch(self.newcf)
        self.sentence_tokenizer = SentenceTokenizer()

    def make_ggg_for_instruction(self, text):
        esdc = ExtendedSdc("EVENT", text, 
                           r=TextStandoff(text, 
                                          (0, len(text))))
        ggg = ggg_from_esdc(esdc)
        return esdc, ggg

    def find_plan(self, recipe_text, initial_state):
        """
        Returns a sequence of states and actions, given the text of
        the recipe (not including the ingredients) and the initial
        KitchenState.

        Returns a list of (instruction, state_seq), where each
        instruction is a TextStandoff into the original recipe.

        The state_seq is a list of (action, state).  The action is the
        action that was executed to create the state.  The sequence
        starts with initial_state, but this state is not returned in
        the list.

        To iterate through the results, do something like this: 
        
        for instruction, state_seq in whole_sequence:
          for action, state in state_seq:
             print "action", action

        """

        instructions = self.sentence_tokenizer.tokenize(recipe_text)
        current_state = initial_state
        whole_sequence = []
        for instruction in instructions:
            #print "inst",  type(instruction), instruction
            if len(instruction.text) < 3:
                continue
            try:
                esdc, ggg = self.make_ggg_for_instruction(instruction.text)
                results = self.task_planner.find_plan(current_state, [ggg],
                                                      save_state_tree=True,
                                                      allow_null_action=False,
                                                      search_depth_event=7,
                                                      beam_width_event=10,
                                                      beam_width=10
                                                      )
                if len(results) != 0:
                    state_sequence = self.sequence(results[0])
                    (cost, idx), state, ggg = results[0]
                    #print "sequence: ", results[0]
                    #probability = math.exp(-cost)
                    #print probability

                    whole_sequence.append((instruction, state_sequence, cost))
                    current_state = state_sequence[-1][1]
            except:
                print "recipe", recipe_text
                print "exception on", instruction
                raise
        return whole_sequence

    def find_viterbi_plan(self, recipe_text, initial_state):
        preprocessed_instructions = self.sentence_tokenizer.tokenize(recipe_text)
        instructions = []
        for i in preprocessed_instructions:
            if len(i.text) > 3:
                instructions.append(i)
        #FOR TESTING ONLY. PLEASE REMOVE THE FOLLOWING LINE
        #instructions = instructions[0:2]
        #print "length of instructions", len(instructions), "down from", len(preprocessed_instructions)
        
        viterbi_results = self.recurse_viterbi( initial_state, [], instructions, 0 )
        #print "VIT RES                ", viterbi_results, len(viterbi_results)
        print "Number of possible paths found:", len(viterbi_results)
        lowest = viterbi_results[0][-1]
        index = 0
        for i in range(len(viterbi_results)):
            
            for j in viterbi_results[i][0]:
                pass
                #print j
##                state_sequence = self.sequence(j)
##                for k in state_sequence:
##                    print k
                
            if viterbi_results[i][-1] < lowest:
                lowest = viterbi_results[i][-1]
                index = i
            elif viterbi_results[i][-1] == lowest:
                print "tie: " + str(i)
        print index, lowest
        print viterbi_results[index]
        for i in viterbi_results[index][0]:
            #print self.sequence(i)
            pass
        return viterbi_results[index]
        #return whole_sequence

    
    def recurse_viterbi(self, initial_state, current_path, instructions, depth=0):
        #print "Viterbi time"
        #Is this the correct starting probability?
        #Format: ([complete path], probability)
        #current_state = current_path[-1][1]
        current_state = initial_state
        instruction = instructions[depth]
        esdc, ggg = self.make_ggg_for_instruction(instruction.text)
        results = self.task_planner.find_plan(current_state, [ggg],
                                                      save_state_tree=True,
                                                      allow_null_action=False,
                                                      search_depth_event=10,
                                                      beam_width_event=5,
                                                      beam_width=5
                                                      )
        for i in results:
            temp = self.sequence(i)
            for j in temp:
                pass
                #This will print out the possible children of the current state as returned by find_plan.
                #print j
            #print "\\"
        #print "-"
        whole_sequence = []
        if depth < (len(instructions) - 1):
            #print "Recursing. Results length:", len(results)
            viterbi_results = []
            #Recurse some more
            for i in results:
                (cost, idx), state, ggg = i
                viterbi_results.extend( self.recurse_viterbi(state ,current_path+[i], instructions, (depth+1)) )
            return viterbi_results
        
        else:
            #print "Not recursing. Results length:", len(results)
            possible_paths = []
            for i in results:
                #print len(current_path)
                (cost, idx), state, ggg = i
                #temp_path = copy.deepcopy(current_path)
                #temp_path.append((state, cost))
                totalProb = cost
                for i in current_path:
                    totalProb += i[0][0]
                possible_paths.append( ( current_path+[i] , totalProb) )
                #possible_paths.append( (temp_path, totalProb) )
            return possible_paths

    def find_dijkstra_plan(self, recipe_text, initial_state):
        #print "Dijkstra time! :)"
        pathFound = False
        preprocessed_instructions = self.sentence_tokenizer.tokenize(recipe_text)
        instructions = []
        for i in preprocessed_instructions:
            if len(i.text) > 3:
                instructions.append(i)
            pass
        depth = len(instructions)
        paths = []
        paths.append(KitchenPath(initCost=0.0, initPath=[initial_state]))
        print paths
        while(len(paths)>0):
            print "looking for new path", len(paths)
            likeliestPath = min(paths, key=lambda x:x.cost)
            paths.remove(likeliestPath)
            print "found my short path of cost", likeliestPath.cost, "at depth", likeliestPath.depth
            currentState, currentDepth = likeliestPath.currentNode()
            if (currentDepth == depth):
                print "Possible paths expanded: ", len(paths)
                return (likeliestPath.wholePath(), likeliestPath.cost)
            currentInstruction = instructions[currentDepth]
            esdc, ggg = self.make_ggg_for_instruction(currentInstruction.text)
            results = self.task_planner.find_plan(currentState, [ggg],
                                                      save_state_tree=True,
                                                      allow_null_action=False,
                                                      search_depth_event=10,
                                                      beam_width_event=5,
                                                      beam_width=5
                                                      )
            if len(results) != 0:
                for i in results:
                    (cost, idx), state, ggg = i
                    print likeliestPath
                    paths.append(likeliestPath.addNode(i))
                
        print "No paths found :("


    def find_beam_plan(self, recipe_text, initial_state):
        beam_width = 2
        preprocessed_instructions = self.sentence_tokenizer.tokenize(recipe_text)
        instructions = []
        for i in preprocessed_instructions:
            if len(i.text) > 3:
                instructions.append(i)
            pass
        depth = len(instructions)
        paths = []
        paths.append(KitchenPath(initCost=0.0, initPath=[initial_state]))
        
        for i in range(len(instructions)):
            print "Instruction level:", i
            tempPaths = []
            currentInstruction = instructions[i]
            for j in range(len(paths)):
                print "Path #:", j
                currentState, currentDepth = paths[j].currentNode()
                esdc, ggg = self.make_ggg_for_instruction(currentInstruction.text)
                results = self.task_planner.find_plan(currentState, [ggg],
                                                          save_state_tree=True,
                                                          allow_null_action=False,
                                                          search_depth_event=7,
                                                          beam_width_event=10,
                                                          beam_width=10
                                                          )
                if len(results) != 0:
                    k = 0
                    while (k < min(beam_width, len(results))):
                        state_sequence = self.sequence(results[k])
                        (cost, idx), state, ggg = results[k]
                        tempPaths.append(paths[j].addNode(results[k], (currentInstruction, state_sequence, cost)))
                        k += 1
                else:
                    tempPaths.append(paths[j].copy())
                    
            paths = tempPaths
        likeliestPath = min(paths, key=lambda x:x.cost)
        return likeliestPath.getWholeSequence()
        


    def sequence(self, plan):
        cost, state, ggg = plan
        return self.task_planner.state_sequence(state)
    
            
class KitchenPath:
    def __init__(self, initCost=0.0, initPath=[], initRawPath=[], ws=[]):
        self.cost = initCost
        self.path = initPath
        self.rawPath = initRawPath
        self.whole_sequence = ws
    def __lt__(self, other):
        return self.cost < other.cost
    def addNode(self, rawPathNode, sequence_step=None):
        (newCost, idx), newState, ggg = rawPathNode
        
        return KitchenPath(initCost=(self.cost+newCost), initPath=self.path+[newState], initRawPath=self.rawPath+[rawPathNode], ws=self.whole_sequence+[sequence_step])
    def copy(self):
        return KitchenPath(self.cost, self.path, self.rawPath, self.whole_sequence)
    def currentNode(self):
        return self.path[-1], len(self.path)-1
    @property
    def depth(self):
        return len(self.rawPath)
    def wholePath(self):
        return self.path
    def getRawPath(self):
        return self.rawPath
    def getWholeSequence(self):
        return self.whole_sequence




    
