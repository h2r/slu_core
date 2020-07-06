import numpy as np
import matplotlib, scipy
import matplotlib.pyplot as mpl
import scipy.stats



yData = [[ 0 , 0 , 0 , 0 , 0 , 0 , 0 , 1 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ],[ 1 , 0 , 0 , 0 , 0 , 0 , 1 , 1 , 0 , 1 , 1 , 0 , 0 , 0 , 0 ],
[ 2 , 1 , 0 , 0 , 0 , 1 , 2 , 0 , 1 , 2 , 1 , 1 , 1 , 4 , 0 ],[ 3 , 3 , 1 , 2 , 2 , 2 , 3 , 2 , 2 , 3 , 1 , 2 , 2 , 3 , 1 ],
[ 3 , 2 , 2 , 2 , 3 , 2 , 2 , 3 , 3 , 4 , 1 , 3 , 2 , 3 , 3 ],[ 0 , 3 , 4 , 2 , 2 , 1 , 1 , 2 , 3 , 2 , 3 , 3 , 3 , 2 , 4 ],
[ 2 , 3 , 4 , 2 , 4 , 3 , 2 , 4 , 3 , 5 , 2 , 1 , 2 , 3 , 3 ],[ 4 , 3 , 4 , 3 , 1 , 3 , 3 , 4 , 2 , 4 , 1 , 3 , 1 , 3 , 3 ],
[ 4 , 2 , 4 , 5 , 2 , 1 , 3 , 3 , 3 , 3 , 1 , 4 , 2 , 1 , 5 ],[ 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 ]]

xData = [1 ,6 ,11 ,16 ,21 ,26 ,31 ,36 ,41 ,45]

#Instruction-level performance
"""
yData=[[ 32 , 34 , 33 , 33 , 35 , 33 , 33 , 34 , 33 , 36 , 33 , 34 , 35 , 33 , 34 , 35 , 33 , 33 , 34 , 32 ],
[ 48 , 44 , 47 , 46 , 45 , 45 , 45 , 47 , 45 , 47 , 49 , 45 , 43 , 46 , 45 , 46 , 44 , 47 , 46 , 46 ],
[ 51 , 51 , 49 , 47 , 49 , 48 , 48 , 50 , 53 , 51 , 54 , 45 , 47 , 48 , 48 , 47 , 49 , 54 , 48 , 48 ],
[ 53 , 52 , 52 , 49 , 49 , 53 , 52 , 48 , 54 , 51 , 54 , 57 , 47 , 55 , 48 , 52 , 47 , 55 , 51 , 50 ],
[ 51 , 55 , 52 , 52 , 55 , 53 , 51 , 54 , 55 , 55 , 50 , 55 , 53 , 53 , 52 , 56 , 57 , 59 , 54 , 53 ],
[ 56 , 56 , 54 , 54 , 56 , 53 , 51 , 54 , 60 , 56 , 55 , 58 , 50 , 54 , 55 , 56 , 55 , 54 , 58 , 53 ],
[ 58 , 57 , 54 , 56 , 57 , 56 , 52 , 54 , 55 , 56 , 53 , 58 , 53 , 59 , 59 , 54 , 58 , 56 , 58 , 56 ],
[ 56 , 58 , 60 , 54 , 56 , 59 , 54 , 56 , 54 , 55 , 57 , 58 , 56 , 56 , 57 , 55 , 56 , 58 , 58 , 58 ],
[ 57 , 54 , 56 , 61 , 54 , 54 , 57 , 58 , 56 , 55 , 56 , 59 , 56 , 57 , 60 , 56 , 58 , 58 , 59 , 58 ],
[ 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 , 55 ]]
"""
xData=[1 ,6 ,11 ,16 ,21 ,26 ,31 ,36 ,41, 45]

#Instruction
yData = [[ 60 , 58 , 54 , 54 , 54 , 57 , 56 , 54 , 55 , 57 , 57 , 55 , 53 , 55 , 55 , 57 , 57 , 56 , 55 , 48 , 55 , 56 , 54 , 58 , 55 ],
[ 63 , 62 , 61 , 61 , 67 , 66 , 67 , 65 , 63 , 61 , 66 , 65 , 62 , 61 , 67 , 66 , 65 , 65 , 62 , 66 , 68 , 66 , 63 , 63 , 61 ],
[ 65 , 65 , 66 , 66 , 67 , 65 , 69 , 68 , 65 , 64 , 65 , 67 , 72 , 65 , 68 , 68 , 73 , 70 , 63 , 67 , 68 , 67 , 68 , 65 , 62 ],
[ 68 , 73 , 67 , 69 , 71 , 69 , 70 , 68 , 66 , 66 , 70 , 69 , 70 , 66 , 70 , 66 , 69 , 70 , 68 , 70 , 66 , 67 , 72 , 68 , 65 ],
[ 72 , 74 , 69 , 68 , 71 , 74 , 78 , 77 , 67 , 70 , 76 , 70 , 73 , 69 , 75 , 73 , 71 , 73 , 73 , 74 , 72 , 74 , 71 , 68 , 72 ],
[ 72 , 78 , 70 , 77 , 71 , 70 , 75 , 76 , 73 , 76 , 75 , 73 , 73 , 75 , 75 , 72 , 69 , 73 , 75 , 74 , 75 , 73 , 74 , 70 , 73 ],
[ 75 , 75 , 76 , 77 , 72 , 72 , 74 , 77 , 73 , 75 , 75 , 77 , 75 , 72 , 73 , 75 , 71 , 76 , 77 , 76 , 75 , 76 , 75 , 71 , 75 ],
[ 74 , 77 , 72 , 78 , 76 , 77 , 73 , 81 , 78 , 76 , 79 , 74 , 73 , 71 , 73 , 74 , 78 , 76 , 77 , 78 , 72 , 73 , 78 , 73 , 76 ],
[ 75 , 76 , 76 , 75 , 76 , 79 , 77 , 80 , 79 , 77 , 77 , 73 , 77 , 77 , 75 , 78 , 79 , 78 , 78 , 74 , 78 , 77 , 77 , 73 , 77 ],
[ 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 , 78 ]]

#E2E
yData = [[ 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ],
[ 1 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 1 , 1 , 0 , 0 , 0 ],
[ 0 , 0 , 0 , 0 , 0 , 0 , 0 , 1 , 0 , 1 , 0 , 1 , 0 , 0 ],
[ 0 , 2 , 0 , 0 , 1 , 1 , 0 , 1 , 1 , 0 , 1 , 0 , 0 , 0 ],
[ 2 , 2 , 2 , 0 , 1 , 2 , 1 , 2 , 1 , 0 , 1 , 1 , 1 , 0 ],
[ 2 , 1 , 2 , 1 , 2 , 1 , 3 , 3 , 3 , 2 , 5 , 3 , 1 , 2 ],
[ 2 , 1 , 3 , 1 , 4 , 0 , 1 , 5 , 3 , 2 , 3 , 1 , 2 , 3 ],
[ 3 , 1 , 1 , 1 , 4 , 1 , 3 , 3 , 2 , 1 , 2 , 3 , 2 , 2 ],
[ 1 , 2 , 3 , 2 , 2 , 3 , 2 , 1 , 2 , 2 , 3 , 1 , 2 , 2 ],
[ 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 ]]

def main(yData, xData=range(len(yData))):
    scale = 118
    #TODO: Something with xData
    iterations = range(len(yData))
    Y = [scipy.mean(yData[iteration][1:])*(1.0/scale)
                    for iteration in iterations]
    yerr = [scipy.stats.sem(yData[iteration][1:])*(1.0/scale)
                       for iteration in iterations]
    mpl.errorbar(xData, Y, yerr=yerr, label="Recipes successfully inferred", ecolor='r')
    mpl.xlabel('Number of recipes in the training set')
    mpl.ylabel('Fraction correct')
    #mpl.legend()
    #mpl.title('Fraction of Correctly Followed Recipes vs. the Size of the Training Corpus\nEnd-to-end Evaluation')
    mpl.xlim(xmin=0)
    mpl.ylim(ymin=0)
    mpl.show()
    mpl.close('all')

main(yData, xData)