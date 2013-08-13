from datatypes import *


class bst:
    def __init__(self):
        self.root = None

class bst_tree_elt(tree_elt):
    def __init__(self, key, data):
        tree_elt.__init__(self, key, data)
        self.parent = None
        self.right = None
        self.left = None


def bst_inorder_tree_walk(x):
    if(not x == None):
        if(not x.left == None):
            print str(x.key) + "->" + str(x.left.key) + ";"
        else:
            print str(x.key) + "->NoneL"+str(x.key)+";"
        if(not x.right == None):
            print str(x.key) + "->" + str(x.right.key) + ";"
        else:
            print str(x.key) + "->NoneR"+str(x.key)+";"
        
        bst_inorder_tree_walk(x.left)
        bst_inorder_tree_walk(x.right)


def bst_tree_search(x, key):
    if(x==None or key==x.key):
        return x

    if(key < x.key):
        return bst_tree_search(x.left, key)
    else:
        return bst_tree_search(x.right, key)

def bst_minimum(x):
    while(not x.left == None):
        x = x.left

    return x

def bst_maximum(x):
    while(not x.right == None):
        x = x.right

    return x

def bst_successor(x):
    if(not x.right == None):
        return bst_minimum(x.right)

    y = x.parent

    while(not y == None and x == y.right):
        x = y
        y = y.parent

    return y

def bst_insert(T, z):
    y = None
    x = T.root

    while(not x == None):
        y = x

        if(z.key < x.key):
            x = x.left
        else:
            x = x.right

    z.parent = y

    if(y == None):
        T.root = z
    elif(z.key < y.key):
        y.left = z
    else:
        y.right = z

def bst_delete(T, z):
    y = None
    
    
    if(z.left == None or z.right == None):
        y = z
    else:
        y = bst_successor(z)

    if(not y.left == None):
        x = y.left
    else:
        x = y.right

    if(not x == None):
        x.parent = y.parent

    if(y.parent == None):
        T.root = x
    elif(y == y.parent.left):
        y.parent.left = x
    else:
        y.parent.right = x


    if(not y==z):
        z.key = y.key
        z.data = y.data

    return y
    

    
    
    
if __name__ == "__main__":
    T = bst()

    z = bst_tree_elt(8, 8)
    z1 = bst_tree_elt(6, 6)
    bst_insert(T,z)
    bst_insert(T,bst_tree_elt(0, 0))
    bst_insert(T,bst_tree_elt(4, 4))
    bst_insert(T,bst_tree_elt(2, 2))
    bst_insert(T,z1)
    bst_insert(T,bst_tree_elt(50, 50))    
    bst_insert(T,bst_tree_elt(10, 10))
    bst_insert(T,bst_tree_elt(1, 1))

    bst_delete(T,z1)
    
    print "digraph G {"
    bst_inorder_tree_walk(T.root)
    print "}"

    #print bst_maximum(T.root)
    #print bst_minimum(T.root)
    #bst_insert(T)

