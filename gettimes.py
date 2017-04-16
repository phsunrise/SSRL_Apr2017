import numpy as np
import helper
import os, sys
import matplotlib.pyplot as plt
from pprint import pprint

runs = [3, 4]

for run in runs:
    filename = helper.getparam('filenames', run)

    times_array = []
    for root, dirs, files in os.walk(os.getcwd()+"/data"):
        if filename in files:
            for line in open(root+'/'+filename, 'r'):
                if line.startswith("#T "):
                    times_array.append(float(line.split(' ')[1]))
            break # found the file, so stop looping through directory

    if len(times_array) != 81*7:
        print "file %s is wrong!" % filename
        continue
    plt.semilogy(times_array[0::7], label="0")
    pprint(zip(range(81), times_array[0::7]))
    plt.semilogy(times_array[3::7], label="3")

    plt.legend()
    plt.show()

    np.save("times/%s_times.npy"%filename, times_array)
