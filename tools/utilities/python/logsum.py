import math

def  sumLogProb (a, b):
    """
    Copied from mallet; limits overflow. 
    """
    if (a > b):
        return a + math.log (1 + math.exp(b-a))
    else:
        return b + math.log (1 + math.exp(a-b))

