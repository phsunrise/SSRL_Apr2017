import numpy as np
import helper
from settings import ar
import glob
import matplotlib.pyplot as plt

filenames = ["plastic_1_040517-153101", "plastic_1_040517-153152"]
ts = [1., 100.]

alldata = np.array([]) 
for filename, t in zip(filenames, ts): 
    data = np.load("data_npz/%s.npz"%filename)['data'][ar[0]:ar[1], (ar[2]+80):ar[3]]
    plt.imshow(data)
    plt.show()
    data = data*1./t
    data = data.flatten()
    alldata = np.concatenate((alldata, data))
    print np.mean(data), np.std(data)

print "all data:", np.mean(alldata), np.std(alldata)
