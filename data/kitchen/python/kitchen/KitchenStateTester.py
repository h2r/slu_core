import kitchenState
kitchen = kitchenState

#a = kitchen.Ingredient(["Flour"], True, "1 cup")
#print a

startState = kitchen.BakeState()
A = kitchen.Ingredient(["Flour"], True, "1 cup")
B = kitchen.Ingredient(["Sugar"], True, "2 cups")
startState.table = kitchen.Table([A, B])

successors = startState.getSuccessors()
for i in successors:
    print i[0], i[1]

print "Turning oven on"
nextState = successors[1][0]
successors = nextState.getSuccessors()
for i in successors:
    print i[0], i[1]
    
print "Pouring Flour"
nextState = successors[1][0]
successors = nextState.getSuccessors()
for i in successors:
    print i[0], i[1]

print "mixing the mixing bowl"
nextState = successors[2][0]
successors = nextState.getSuccessors()
for i in successors:
    print i[0], i[1]
    
print "Scraping the mixing bowl"
nextState = successors[1][0]
successors = nextState.getSuccessors()
for i in successors:
    print i[0], i[1]

print "Baking the pan"
nextState = successors[1][0]
successors = nextState.getSuccessors()
for i in successors:
    print i[0], i[1]

print nextState.action_sequence
