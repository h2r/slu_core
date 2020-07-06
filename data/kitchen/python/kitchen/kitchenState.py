from g3.state import State, Action
from esdcs.groundings import PhysicalObject, Prism, Place, Path
import random
from esdcs.context import Context

#TODO: Test using own BFS code

#Simple object classes

use_physical_object = False

class Ingredient():
#TODO: to physical object method
    #contains: list of strings of the actual names of the Ingredients ["Flour", "Sugar"]
    #homogenous: Boolean that shows if the ingredient is homogenous.
    #Amount: String of measure of ingredient "1 cup" or "1/2 tbsp"
    def __init__(self, contains, homogenous, amount, physicalObject=None):
        self.contains = contains
        self.homogenous = homogenous
        self.amount = amount
        if use_physical_object:
            if physicalObject == None:
                #generate a random lcmID for each ingredient
                randomID = random.randint(5,1000)
                self.phyObj = PhysicalObject(prism_from_point(1, 5, 1, 2),lcmId = randomID, tags=contains)
            else:
                self.phyObj = physicalObject
        else:
            self.phyObj = None
        
    @property
    def name(self):
        return self.phyObj.tags[0]

    def __str__(self):
        return "Ingredients [" + ", ".join(self.contains) + "]"
    def ros_str(self):
        return '%s = Ingredient("%s", "%s")' % (self.name, self.name, self.amount)

    def __eq__(self, otherIngredient):
        if otherIngredient == None:
            return False
        
        if len(self.contains) != len(otherIngredient.contains):
            #print "Failed ingredient equality check 1"
            return False
        for i in self.contains:
            iTrue = False
            for j in otherIngredient.contains:
                if i == j:
                    if j != i:
                        raise ValueError("EQUALITY ERROR! NOT SYMMETRIC")
                    iTrue = True
            if iTrue == False:
                #print "Failed ingredient equality check 2"
                return False
        
        if self.amount == otherIngredient.amount:
            if self.homogenous == otherIngredient.homogenous:
                if self.phyObj == otherIngredient.phyObj:
                    return True
                #print "Ingredients failed the physicalObject equality test."
        return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        hashValue = 0
        listHash = 0
        for i in self.contains:
            listHash += hash(i)
        hashValue += 3*hash(listHash)
        hashValue += 5*hash(self.homogenous)
        hashValue += 7*hash(self.amount)
        if use_physical_object:
            hashValue += 11*hash(self.phyObj)
        return hashValue

class Oven():
    #Temperature: an int representing the temperature of the oven in degrees F
    #empty: a Boolean that represents the emptiness of the oven s(True if empty).
    def __init__(self, temperature, empty,physicalObject=None):
        self.temp = temperature
        self.empty = empty
        if use_physical_object:
            if physicalObject == None:
                self.phyObj = PhysicalObject(prism_from_point(11, 3, 1, 2), lcmId = 21, tags=['Oven'])
            else:
                self.phyObj = physicalObject
        else:
            self.phyObj = None
            
    def __eq__(self, otherOven):
        if otherOven == None:
            #print "Other oven is None"
            return False

        if (self.temp == otherOven.temp) or (self.temp > 0 and otherOven.temp > 0):
            if self.empty == otherOven.empty:
                if self.phyObj == otherOven.phyObj:
                    return True
                print "Oven physical object equality check failed."
                return False
            print "Oven: empty equality check failed."
            return False
        print "Oven: temperature equality check failed.", self.temp, "and", otherOven.temp
        return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        hashValue = 0
        hashValue += 3*hash(self.temp)
        hashValue += 5*hash(self.empty)
        if use_physical_object:
            hashValue += 7*hash(self.phyObj)
        return hashValue
    def __str__(self):
        out = "The oven at temperature: " +  str(self.temp)
        return str(out)

class MixingBowl():
    #@param contains: list of Ingredient objects that are in the mixing bowl (have been poured in)
    #@param onTable: A Boolean that is true if the mixing bowl is still on the table (and has not yet been scraped)
    #@param isHomogenous: A boolean representing the homogenity of the mixing bowl's contents (True if homogenous)
    def __init__(self, contains, onTable, isHomogenous, physicalObject=None):
        #Is this deep copied?
        self.contains = list(contains)
        self.homogenous = isHomogenous
        self.onTable = onTable
        self.name = "bowl"
        if use_physical_object:
            if physicalObject == None:
                self.phyObj = PhysicalObject(prism_from_point(1, 3, 1, 2),lcmId = 22, tags=['Mixing Bowl'])
            else:
                self.phyObj = physicalObject
        else:
            self.phyObj = None
    def __str__(self):
        tempOut = "["
        for i in self.contains:
            tempOut = tempOut + (str(i)) + ", "
        return "The Mixing Bowl (which contains: " + str(tempOut) + "])"
    def __eq__(self, otherBowl):
        if otherBowl == None:
            return False
        
        if len(self.contains) != len(otherBowl.contains):
            #print "Failed mixing bowl equality check 1"
            return False
        for i in self.contains:
            iTrue = False
            for j in otherBowl.contains:
                if i == j:
                    if j != i:
                        print "EQUALITY ERROR! NOT SYMMETRIC"
                    iTrue = True
            if iTrue == False:
                #This is a common point of failure
                #print "Failed mixing bowl equality check 2"
                return False

        #if self.homogenous == otherBowl.homogenous:
        if self.onTable == otherBowl.onTable:
            if self.phyObj == otherBowl.phyObj:
                return True
            #print "Mixing Bowl failed the physicalObject equality test."

        return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        hashValue = 0
        hashValue += 3*hash(self.homogenous)
        hashValue += 5*hash(self.onTable)
        listHash = 0
        for i in self.contains:
            listHash += hash(i)
        hashValue += 7*hash(listHash)
        if use_physical_object:
            hashValue += 11*hash(self.phyObj)
        return hashValue

class Pan():
    #@param contains: list of Ingredient objects that in the pan (have been scraped in)
    #@param onTable: A Boolean that is true if the pan is still on the table (aka not in the oven)
    #@param onTable: A Boolean that is true if the pan has already been baked.
    def __init__(self, contains, onTable, isCooked, physicalObject=None):
        self.contains = list(contains)
        self.onTable = onTable
        self.cooked = isCooked
        self.name = "pan"
        if use_physical_object:
            if physicalObject == None:
                self.phyObj = PhysicalObject(prism_from_point(1, 1, 1, 2),lcmId = 23, tags=['Pan'])
            else:
                self.phyObj = physicalObject
        else:
            self.phyObj = None
    def __str__(self):
        return "Pan [" + ", ".join(str(o) for o in self.contains) + "])"
    def __eq__(self, otherPan):
        if otherPan == None:
            return False

        if len(self.contains) != len(otherPan.contains):
            print "Pan: failed contains equality check 1"
            print "I contain:", self.contains
            print "He contains:", otherPan.contains
            return False
        for i in self.contains:
            iTrue = False
            for j in otherPan.contains:
                if i == j:
                    if j != i:
                        print "EQUALITY ERROR! NOT SYMMETRIC"
                    iTrue = True
            if iTrue == False:
                print "Pan: Failed contains equality check 2"
                return False
            
        if self.onTable == otherPan.onTable:
            if self.cooked == otherPan.cooked:
                if self.phyObj == otherPan.phyObj:
                    return True
                print "Pan failed the physicalObject equality test."
                return False
            print "Pan: failed cooked equality test."
            return False
        print "Pan: failed onTable equality test.", self.onTable, otherPan.onTable
        return False
        return False
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        hashValue = 0
        hashValue += 3*hash(self.onTable)
        hashValue += 5*hash(self.cooked)
        listHash = 0
        for i in self.contains:
            listHash += hash(i)
        hashValue += 7*hash(listHash)
        if use_physical_object:
            hashValue += 11*hash(self.phyObj)
        return hashValue
    
class Table():
    #@param contains: list of Ingredient objects that on the table (have not been used yet)
    def __init__(self, contains):
        self.contains = list(contains)
    def __eq__(self, otherTable):
        if otherTable == None:
            return False
            
        if len(self.contains) != len(otherTable.contains):
            print "Failed table equality check 1"
            return False
        for i in self.contains:
            iTrue = False
            for j in otherTable.contains:
                if i == j:
                    if j != i:
                        print "EQUALITY ERROR! NOT SYMMETRIC"
                    iTrue = True
            if iTrue == False:
                print "Failed table equality check 2"
                return False
        return True
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        #Likely to collide. Is this okay?
        hashValue = 0
        for i in self.contains:
            hashValue += hash(i)
        return hashValue
    def __str__(self):
        return "Table ["  + ",".join(str(o) for o in self.contains) + "]"

def prism_from_point(x,y,z1,z2):
     return Prism([(x-1, x+1, x+1, x-1), (y-1, y-1, y+1, y+1)], z1, z2)

#-------------------------------------------------------------------------------------
#real stuff

class KitchenState(State):
#TODO: Add cost function, getObjects, getPlaces (shoud return the empty list), physicalObjects (seach for groundings.py)
    
##    @staticmethod
##    def init_state():      
##        brownieState = KitchenState()
##        flour = Ingredient(contains=["Flour"], homogenous=True, amount="1/2 cup",
##                                           physicalObject=PhysicalObject(prism_from_point(3, 1, 1, 2), lcmId = 5, tags=['Flour']))
##        sugar = Ingredient(contains=["Sugar"], homogenous=True, amount="1 cup",
##                                           physicalObject=PhysicalObject(prism_from_point(5, 1, 1, 2), lcmId = 6, tags=['Sugar']))
##        eggs = Ingredient(contains=["Eggs"], homogenous=True, amount="2",
##                                           physicalObject=PhysicalObject(prism_from_point(7, 1, 1, 2), lcmId = 7, tags=['Eggs']))
##        butter = Ingredient(contains=["Butter"], homogenous=True, amount="1/2 cup",
##                                           physicalObject=PhysicalObject(prism_from_point(3, 3, 1, 2), lcmId = 8, tags=['Butter']))
##        vanilla = Ingredient(contains=["Vanilla"], homogenous=True, amount="1 teaspoon",
##                                           physicalObject=PhysicalObject(prism_from_point(5, 3, 1, 2), lcmId = 9, tags=['Vanilla']))
##        cocoa = Ingredient(contains=["Cocoa"], homogenous=True, amount="6 tablespoons",
##                                           physicalObject=PhysicalObject(prism_from_point(7, 3, 1, 2), lcmId = 10, tags=['Cocoa']))
##        brownieState.table.contains = [flour, sugar, eggs, butter, vanilla, cocoa]
##        return brownieState

    def __init__(self):
        self.reset()

    def to_context(self):
        if use_physical_object == False:
            return Context([], [])
        return Context([i.phyObj for i in self.table.contains], [])

    @property
    def ingredients(self):
        return self.table.contains


    def getObjectsSet(self):
        if use_physical_object == False:
            return []
        #objectIDs = []
        #TODO: Integrate the ingredient IDs
        #ingredientIDs = [i.phyObj.id for i in self.table.contains]
        objectIDs = [i.phyObj.id for i in self.table.contains]
        #print "The ingredient IDs are: ", ingredientIDs
        if self.pan.onTable == True:
            objectIDs.append(self.pan.phyObj.id)
        if self.mixing_bowl.onTable == True:
            objectIDs.append(self.mixing_bowl.phyObj.id)
        objectIDs.append(self.oven.phyObj.id)
        return objectIDs
    
    def getGroundableById(self, ID):
        if use_physical_object == False:
            return None
        
        if ID == self.pan.phyObj.id:
            return self.pan.phyObj
        elif ID == self.oven.phyObj.id:
            return self.oven.phyObj
        elif ID == self.mixing_bowl.phyObj.id:
            return self.mixing_bowl.phyObj
        elif ID == self.AGENT_ID:
            return self.agent
        else:
            for ing in self.table.contains:
                if ID == ing.phyObj.id:
                    return ing.phyObj
        raise ValueError("No object found with that ID")

    #Stefanie suggested simply returning an empty list
    @property
    def topological_locations(self):
        '''Returns the coordinates of the locations of the topological
          nodes for this state's topological map.'''
        locations = []
        return locations

    #I had a note from a meeting to return an empty list,
    #but I don't remember why.
    def getPlacesSet(self):
        return []

    def getPosition(self):
        return [1, 1]

    @property
    def agent(self):
        #Check to make sure this is reasonable
        if use_physical_object == False:
            return None
        return PhysicalObject(prism_from_point(1, 6, 1, 2), lcmId = State.AGENT_ID, tags=['Robot'])
    
    def getSequence(self):
        return self.action_sequence

    def getAgentId(self):
        return State.AGENT_ID

    @property
    def objects(self):
         #TODO: Implement me? Does this work?
         return [self.getGroundableById(oid) for oid in self.getObjectsSet()]
    
    def reset(self):
        self.action_sequence = []
        self.table = Table([])
        self.pan = Pan([], True, False)
        self.mixing_bowl = MixingBowl([], True, True)
        self.oven = Oven(0, True)
        self.groundableDict = dict()
        self.orientation = 0
        self.AGENT_ID = -100
        #self.object_ids = []

    def __str__(self):
        return "\n".join([" ".join(["table", str(self.table)]),
                          " ".join(["pan", str(self.pan)]),
                          " ".join(["bowl", str(self.mixing_bowl)]),
                          " ".join(["oven", str(self.oven)])])
    
        

    def __eq__(self, otherState):
        if otherState == None:
            return False
            
        if self.AGENT_ID == otherState.AGENT_ID:
            if self.orientation == otherState.orientation:
                if self.groundableDict == otherState.groundableDict:
                    if self.oven == otherState.oven:
                        if self.pan == otherState.pan:
                            if self.mixing_bowl == otherState.mixing_bowl:
                                if self.table == otherState.table:
                                    return True
##                                    if self.action_sequence == otherState.action_sequence:
##                                        return True
                                print "Failed Table equality check."
                                return False
                            print "Failed Mixing Bowl equality check."
                            return False
                        print "Failed Pan equality check."
                        return False
                    print "Failed Oven equality check."
                    return False
                print "Failed groundableDict equality check."
                return False
            print "Failed orientation equality check."
            return False
        print "Failed AGENT_ID equality check."
        return False
    
    def __ne__(self, other):
        return not(self == other)

    def __hash__(self):
        hashValue = 0
        hashValue += 3*hash(self.AGENT_ID)
        hashValue += 5*hash(self.orientation)
        #hashValue += 7*hash(self.groundableDict)
        hashValue += 11*hash(self.oven)
        hashValue += 13*hash(self.pan)
        hashValue += 17*hash(self.mixing_bowl)
        #table might throw off the hash value
        hashValue += 19*hash(self.table)
        #hashValue += 23*hash(self.action_sequence)
        return hashValue
        
    def copy(old_state):
        state = KitchenState()
        state.action_sequence = list(old_state.action_sequence)
        state.table = Table(old_state.table.contains)
        state.pan = Pan(old_state.pan.contains, old_state.pan.onTable, old_state.pan.cooked, old_state.pan.phyObj)
        state.mixing_bowl = MixingBowl(old_state.mixing_bowl.contains, old_state.mixing_bowl.onTable, old_state.mixing_bowl.homogenous, old_state.mixing_bowl.phyObj)
        state.oven = Oven(old_state.oven.temp, old_state.oven.empty, old_state.oven.phyObj)
        state.groundableDict = dict(old_state.groundableDict)
        return state

    def getSuccessors(self, groundings=[]):
        #TODO: What do with groundings?
        states = []
        
        # null action
        a = None
        s = KitchenState.copy(self)
        s.action_sequence.append((self, None))
        #TODO: What is agent?
        #states.append((s, a, [s.agent]))
        states.append((s, a, []))

        #Oven block
        if (self.oven.temp < 1): #If the oven is off
            #TODO: fix target temp
            desiredOvenTemp = 350
            a = ChangeOvenTemp(desiredOvenTemp)
            s, mg = a.execute(self)
            states.append((s, a, mg))
        else: #If oven is on
            if (self.oven.empty == True): #And oven is empty
                if ( len(self.pan.contains) > 0): #and the pan is non-empty
                    if (self.pan.cooked == False and self.pan.onTable == True): #The pan hasn't been cooked yet
                        #TODO: fix Duration
                        duration = 20
                        a = Bake(self.pan, duration)
                        s, mg = a.execute(self)
                        states.append((s, a, mg))
                    else: #The pan is already cooked
                        #print "can't bake, already cooked"
                        pass
                else: #and if pan is empty
                    #print "can't bake, empty pan"
                    pass
            else: #and if the oven is not empty
                #print "can't bake, stuff in oven"
                #TODO: remove? We need to work out the time and baking issues
                #We might have baking as an atomic action, which no longer requires oven.empty
                pass

        #Pan block
        if (self.pan.onTable == True): #If pan is on the table
            if (self.mixing_bowl.onTable == True): #If the mixing bowl is on the table
                if (len(self.mixing_bowl.contains) > 0): #if the mixing bowl contains something
                    a = Scrape(self.mixing_bowl, self.pan)
                    s, mg = a.execute(self)
                    states.append((s, a, mg))
                else: #if the mixing bowl is empty
                    #print "can't scrape, bowl is empty"
                    pass
            else: #If the mixing_bowl is not on the table
                #print "can't scrape, bowl not on table"
                pass
        else: #If pan is not on the table
            #print "can't scrape, pan not on table"
            pass

        #Mixing_bowl block
        if (self.mixing_bowl.onTable == True): #If the mixing bowl is on the table
            if (self.mixing_bowl.homogenous == False): #If the mixing bowl is heterogeneous
                a = Mix(self.mixing_bowl)
                s, mg = a.execute(self)
                states.append((s, a, mg))
                    
            if (len(self.table.contains) > 0): #If the table contains ingredients
                for i in self.table.contains: #For each ingredient
                    a = Pour(i, self.mixing_bowl)
                    s, mg = a.execute(self)
                    states.append((s, a, mg))
            else: #Table has no ingredients
                pass
        else: #Mixing bowl is not on table
            pass
        return states

class Pour(Action):
    """ 
    Only applies to pouring ingredients into the mixing_bowl.
    """
    def __init__(self, ing, bowl):
        self.source = ing
        self.dest = bowl
        self.name = "pour"
        self.args = [ing, bowl]

    def execute(self, in_state, tstep=1):
        next_state = KitchenState.copy(in_state)
        #What do these do?
        modified_groundings = []
        #agent = next_state.agent

        #Quick and dirty way to remove the ingredient from the table contains list
        for i in range(len(next_state.table.contains)):
            if ( (self.source.contains == next_state.table.contains[i].contains) and
                 (self.source.homogenous == next_state.table.contains[i].homogenous) and
                 (self.source.amount == next_state.table.contains[i].amount) ):
                #Remove the duplicate ingredient
                next_state.table.contains.pop(i)
                break
        
        next_state.mixing_bowl.contains.append( Ingredient(self.source.contains, self.source.homogenous, self.source.amount, self.source.phyObj) )
        next_state.mixing_bowl.homogenous = False
        next_state.action_sequence.append((in_state, self))
        return next_state, modified_groundings
    
    def __str__(self):
        return "Pour: " + str(self.source) + " into: " + str(self.dest)
    
    def toPlanningLanguage(self):
        return "pour(" + str(self.source.contains[0]) + ")"

class Scrape(Action):
    #Only applies to pouring the mixing_bowl into the pan
    def __init__(self, bowl, pan):
        #Scrape the mixing_bowl contents into the pan
        self.source = bowl
        self.dest = pan
        self.name = "scrape"   
        self.args = [bowl, pan]

    def execute(self, in_state, tstep=1):
        modified_groundings = []
        next_state = KitchenState.copy(in_state)

        #Creates an nonempty, onTable, uncooked pan
        next_state.pan = Pan( self.dest.contains + self.source.contains , True, False)
        #Set the mixing bowl to be empty, off the table, and homogenous
        next_state.mixing_bowl= MixingBowl([], False, True)

        next_state.action_sequence.append((in_state, self))
        return next_state, modified_groundings
    
    def __str__(self):
        return "Scrape: " + str(self.source) + " into:  " + str(self.dest) + "."

    def toPlanningLanguage(self):
        return "scrape()"

#I'm treating bake as an atomic action, so I'm not using oven.empty
class Bake(Action):
    def __init__(self, pan, duration):
        #Put the pan in the oven for duration minutes
        self.pan = pan
        self.duration = duration
        self.name = "bake"
        self.args = [pan, duration]

    def execute(self, in_state, tstep=1):
        modified_groundings = []
        next_state = KitchenState.copy(in_state)
        
        next_state.pan.cooked = True
        #TODO: onTable = False?
        next_state.pan.onTable = False
        
        #Restriction
        next_state.mixing_bowl.onTable = False

        next_state.action_sequence.append((in_state, self))
        return next_state, modified_groundings
    
    def __str__(self):
        return "Bake: " + str(self.pan) + " for " + str(self.duration) + " minutes."

    def toPlanningLanguage(self):
        return "bake(" + str(self.duration) + ")"

class ChangeOvenTemp(Action):
    def __init__(self, temperature):
        self.temp = temperature
        self.name = "preheat"
        self.args = [temperature]
        
    def execute(self, in_state, tstep=1):
        modified_groundings = []
        next_state = KitchenState.copy(in_state)
        
        next_state.oven.temp = self.temp
        
        next_state.action_sequence.append((in_state, self))
        return next_state, modified_groundings
    
    def __str__(self):
        return "Changing the oven temp to " + str(self.temp) + "degrees F."

    def toPlanningLanguage(self):
        return "preheat(" + str(self.temp) + ")"


class Mix(Action):
    def __init__(self, bowl):
        self.mixing_bowl = bowl
        self.name = "mix"
        self.args = [bowl]
        
    def execute(self, in_state, tstep=1):
        modified_groundings = []
        next_state = KitchenState.copy(in_state)
        
        #This is not general, but does it matter?
        next_state.mixing_bowl.homogenous = True
        
        next_state.action_sequence.append((in_state, self))
        return next_state, modified_groundings
    
    def __str__(self):
        return "Mixing " + str(self.mixing_bowl) + "."

    def toPlanningLanguage(self):
        return "mix()"

class NullAction(Action):
    def __init__(self, *args):
        self.name = "noop"
        self.args = []

    def execute(self, in_state, tstep=1):
        return in_state, []
    def __str__(self):
        return "Placeholder for unsupported actions"
    def toPlanningLanguage(self):
        #should this return None instead?
        return "null()"



