import numpy as np
import pickle
from pprint import pprint
import sys

run = int(sys.argv[1]) 
maxs = pickle.load(open("run%d_maxs.pickle"%run, 'rb'))
maxs.sort(key=lambda tup:tup[2])

for tup in maxs:
    print "%10d\t%10f\t%10f\t%10f\t%4d" % (tup[2], tup[3][0], tup[3][1], tup[3][2], tup[0])
