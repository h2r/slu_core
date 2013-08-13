from scipy import *

def parse_libsvm(filename):
    myfile = open(filename, 'r');

    Y, X = [], []
    for line in myfile:
        
        line = line.split()

        #get the class number
        c_num = int(line[0])

        #get the sample from the line
        sample = []
        for i in range(1, len(line)):
            elt = line[i].split(":")[1]
            sample.append(float(elt));
        
        #append the sample
        X.append(sample)
        Y.append(c_num);

    X = transpose(X)
    myfile.close()

    return array(Y), X
