from copy import deepcopy
from scipy import *

def median_filter(myimage, filter_size):
    new_map = deepcopy(myimage)

    #for i in range(filter_size, len(myimage)-filter_size):
    #    for j in range(filter_size, len(myimage[0])-filter_size):
    for i in range(len(myimage)):
        for j in range(len(myimage[0])):
            if(i <= filter_size or j < filter_size
               or i >= len(myimage)-filter_size or j > len(myimage[0])-filter_size):
                new_map[i,j]=0.0
                continue

            neigh = myimage[i-filter_size:i+filter_size+1,j-filter_size:j+filter_size+1]
            v = median(neigh.flatten())
            new_map[i,j] = v

    return new_map

def skeletonize(b_map, max_num_iterations):
    for i in range(max_num_iterations):
        print "iteration, ", i
        if(i%2 == 0):
            b_map, num_deleted = skeletonize_iter(b_map, True)
        else:
            b_map, num_deleted = skeletonize_iter(b_map, False)

        if(num_deleted == 0):
            return b_map
        
    return b_map

def skeletonize_iter(binary_map, is_step1):
    new_map = deepcopy(binary_map)
    num_deleted = 0
    for i in range(len(binary_map)):
        for j in range(len(binary_map[0])):
            #print len(binary_map), len(binary_map[0])
            en = binary_map[i-1:i+2,j-1:j+2]
            
            if(i == 0 or i == len(binary_map) - 1
               or j == 0 or j == len(binary_map[0]) - 1):
                new_map[i,j] = 0.0
            elif(binary_map[i][j] == 0.0):
                continue
            elif(skeletonize_is_deleted(en, is_step1)):
                num_deleted +=1
                new_map[i,j] = 0.0

    return new_map, num_deleted

def skeletonize_is_deleted(en, is_step1=True):

    if(not len(en) == 3 or not len(en[0]) == 3):
        print "not an eight neighbor"
        exit(1)
    else:

        s = sum(en)
        n = skeletonize_num_transitions(en)

        if(is_step1):
            p1 = en[0,1]*en[1,2]*en[2,1]
            p2 = en[1,2]*en[2,1]*en[1,0]
        else:
            p1 = en[1,0]*en[0,1]*en[1,2]
            p2 = en[0,1]*en[2,1]*en[1,0]

        if(s <= 7 and s >= 3 and n == 1 and p1 == 0 and p2 == 0):
            return True

    return False

def skeletonize_num_transitions(en):
    flat_en = concatenate((en[0,:], en[1:,2], [en[2,1], en[2,0], en[1,0]]))
    
    zero_one_count = 0
    for i in range(len(flat_en)):
        if(flat_en[i-1] == 0 and flat_en[i] == 1):
            zero_one_count += 1
            
    return zero_one_count
