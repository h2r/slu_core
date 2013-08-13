from math import floor
from sys import maxint
from datatypes import tree_elt


def heapsort(A):
    build_max_heap(A)
    heap_size = len(A)-1
    
    iterations = range(2, len(A))
    iterations.reverse()

    for i in iterations:
        tmp = A[i]
        A[i] = A[1]
        A[1] = tmp
        heap_size -= 1
        max_heapify(A, 1, heap_size)
        
def heap_maximum(A):
    return A[1]

def heap_extract_max(A):
    if(len(A) < 1):
        print "heap underflow"
        sys.exit(0)

    max_hval = A[1]
    A[1] = A[len(A)-1]
    A.pop(len(A)-1)
    max_heapify(A, 1)
    
    return max_hval

def heap_increase_key(A, i, key):
    if key < A[i].key:
        print "error: new key is smaller than current key"
    print "set key"
    A[i].key = key

    while(i > 1 and A[heap_parent(i)].key < A[i].key):
        tmp = A[i]
        A[i] = A[heap_parent(i)]
        A[heap_parent(i)] = tmp
        i = heap_parent(i)

def max_heap_insert(A, elt):
    key = elt.key
    elt.key = -1 * maxint

    A.append(elt)
    heap_increase_key(A, len(A)-1, key)
    

def build_max_heap(A):
    iterations = range(1, int(floor(len(A)/2.0))+1)
    iterations.reverse()

    for i in iterations:
        max_heapify(A, i)

def max_heapify(A, i, heap_size=-1):
    l = heap_left(i)
    r = heap_right(i)
    largest = None

    if(heap_size < 0):
        heap_size = len(A)-1

    if(l <= heap_size and A[l].key > A[i].key):
        largest = l
    else:
        largest = i

    if(r <= heap_size and A[r].key > A[largest].key):
        largest = r

    if(not largest == i):
        tmp = A[i]
        A[i] = A[largest]
        A[largest] = tmp
        max_heapify(A, largest, heap_size)

def heap_parent(i):
    return int(floor(i/2.0))

def heap_left(i):
    return 2*i

def heap_right(i):
    return 2*i+1


if __name__ == "__main__":

    A = [None]

    A.append(tree_elt(0, 0))
    A.append(tree_elt(4, 4))
    A.append(tree_elt(2, 2))
    A.append(tree_elt(6, 6))
    A.append(tree_elt(8, 8))
    A.append(tree_elt(10, 10))
    A.append(tree_elt(50, 50))
    A.append(tree_elt(1, 1))

    print "original"
    print A
    build_max_heap(A)
    print "heapified"
    print A


    heap_increase_key(A, 4, 100)
    print "increased key"
    print A


    max_heap_insert(A, tree_elt(0.3, 0.3))
    print "insert_element"
    print A
    
    
    heapsort(A)

    print "sorted"
    print A

