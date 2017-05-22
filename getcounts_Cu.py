import numpy as np
import helper
from settings import ar
import glob
import matplotlib.pyplot as plt

filename = ""
t = 5.

alldata = np.array([]) 
for filename in glob.glob("data_npz/copper_scan_2_*.npz"):
    if "084631" in filename:
        continue
    data = np.load(filename)['data'][ar[0]:(ar[1]-50), ar[2]:ar[3]]
    plt.imshow(data)
    plt.colorbar()
    plt.show()
    data = data*1./t
    data = data.flatten()
    alldata = np.concatenate((alldata, data))
    print np.mean(data), np.std(data)

print "all data:", np.mean(alldata), np.std(alldata)
