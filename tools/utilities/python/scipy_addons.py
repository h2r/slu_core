#import scipy.linalg
from numpy import *
from pyTklib import tklib_randint

'''def null(A, eps=1e-15):
    u, s, vh = scipy.linalg.svd(A*1.0)
    null_mask = (s <= eps)

    null_space = scipy.compress(null_mask, u, axis=0)
    print "vh", vh
    print "null space", null_space
    return null_space'''

def perm(from_num, to_num, num):
    ret_rand = []
    if(num > abs(from_num - to_num)):
        return None
    
    for i in range(num):
        r = tklib_randint(from_num, to_num);
        while(r in ret_rand):
            r = tklib_randint(from_num, to_num);
        
        ret_rand.append(r);

    return ret_rand

def matrix_concatenate(A, B):

    retval = array(list(concatenate((A[i,:],B[i,:])) for i in range(len(A))))
    return retval

def repmat(A,rep):
    for i in range(len(rep)):
        A = repeat(A, rep[i], axis=i)
    return A
    

def test1():
    A = ones([1,2,5])
    B = repmat(A, [2,1,1])
    print B

def test2():
    A = array([[1,2],[3,4]])
    B = array([[5,6],[7,8]])

    print matrix_concatenate(A, B)


def test3():
    print sort(perm(0, 100, 100))
    print len(perm(0, 100, 100))


if __name__=="__main__":
    test3()
