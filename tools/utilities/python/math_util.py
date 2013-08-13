


def unique_combinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in unique_combinations(items[i+1:],n-1):
                yield [items[i]]+cc


def combinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in combinations(items[:i]+items[i+1:],n-1):
                yield [items[i]]+cc

def combinations_self(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in combinations_self(items,n-1):
                yield [items[i]]+cc

 
def binom(n, m):
    b = [0] * (n + 1)
    b[0] = 1
    for i in xrange(1, n + 1):
        b[i] = 1
        j = i - 1
        while j > 0:
            b[j] += b[j - 1]
            j -= 1
    return b[m]




if __name__=="__main__":
    


    print
    print "Unique Combinations of 2 letters from 'love'"
    i = 0
    for uc in uniqueCombinations(range(15),10): 
        i+=1
        print uc
    print "num elts:", i


