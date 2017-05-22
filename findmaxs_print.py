import numpy as np
import pickle
from pprint import pprint
import sys

run = int(sys.argv[1]) 
maxs = pickle.load(open("run%d_maxs.pickle"%run, 'rb'))[::2]
maxs.sort(key=lambda tup:tup[2], reverse=True)

for i_scan, i_file, ma, maind, xyz in maxs:
    print "%10d  (%4d, %4d)  %10f  %10f  %10f  %4d" % (\
            ma, maind[0], maind[1], xyz[0], xyz[1], xyz[2], i_scan)
