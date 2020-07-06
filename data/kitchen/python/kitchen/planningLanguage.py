from kitchen import kitchenState

def decompile(state_actions):
    """
    Convert a sequence of states and actions into a planning language string.
    """
    terms = []
    for action, state in state_actions:
        args = []
        for arg in action.args:
            if hasattr(arg, "name"):
                name = arg.name
            else:
                name = str(arg)
            args.append(name)

        terms.append(action.name + "(" + ",".join(args) + ")")
    return "; ".join(terms)
                             

class PlanningLanguage():
    def __init__(self):
        pass
    
    def mix(self, targetBowl=None):
        if targetBowl == None:
            targetBowl = self.current_state.mixing_bowl
        action = kitchenState.Mix(targetBowl)
        newState = action.execute(self.current_state)[0]
        self.states.append(newState)
        return (action, newState)

    def pour(self, sourceIng, targetBowl=None):
        """
        This method will execute a Pour action on the most recent state
        sourceBowl should be an ingredient that is in the currentState.
        table.contains list. Target bowl is always the mixing_bowl
        """
        if targetBowl == None:
            targetBowl = self.current_state.mixing_bowl
        action = kitchenState.Pour(sourceIng, targetBowl)
        newState = action.execute(self.current_state)[0]
        self.states.append(newState)
        return (action, newState)

    def scrape(self, sourceBowl=None, targetPan=None):
        if sourceBowl == None:
            sourceBowl = self.current_state.mixing_bowl
        if targetPan == None:
            targetPan = self.current_state.pan
        action = kitchenState.Scrape(sourceBowl, targetPan)
        newState = action.execute(self.current_state)[0]
        self.states.append(newState)
        return (action, newState)

    def preheat(self, temp):
        action = kitchenState.ChangeOvenTemp(temp)
        newState = action.execute(self.current_state)[0]
        self.states.append(newState)
        return (action, newState)

    def bake(self, duration, targetPan=None):
        if targetPan == None:
            targetPan = self.current_state.pan
        action = kitchenState.Bake(targetPan, duration)
        newState = action.execute(self.current_state)[0]
        self.states.append(newState)
        return (action, newState)

    def noop(self, *arg):
        """
        This is a null action which returns the current state and a NullAction instance
        """
        action = kitchenState.NullAction()
        return (action, self.current_state)

    @property
    def current_state(self):
        return self.states[-1]

    def compileAnnotation(self, annotation, start_state):
        """
        This method will take in an annotation (a string of
        planningLanguage actions) and evaluate them. (eval())
        This will return a list of (state, action) pairs.
        """
        self.states = [start_state]
        
        if not annotation.endswith(","):
            annotation = annotation + ","

        #TODO: I need to add each ingredient to the dict.
        #cook is added to account for "Cook raisins in one cup water; cool." instruction in raisinCookieRecipe
        #   We might need to tweak that; cook could imply bake...
        evalLocalDict = dict({"mix":self.mix, "pour":self.pour, "scrape":self.scrape,
                              "bake":self.bake, "preheat":self.preheat,
                              "mixingBowl":start_state.mixing_bowl, "pan":start_state.pan, 
                              "frost":self.noop, "melt":self.noop, "line":self.noop,
                              "grease":self.noop, "noop": self.noop, "cut":self.noop})
        for i in start_state.table.contains:
            #This is the first element of contains, which is the item's name
            for j in i.contains:
                key = str(j)
                value = i
                evalLocalDict[key] = value
        try:
            result = eval(annotation, evalLocalDict)
            return result
        except:
            print "exception on", annotation
            raise




