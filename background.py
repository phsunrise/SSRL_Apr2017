import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from settings import hist_bincenters, hist_binedges
import helper
import pickle

runs = [4,3,8,9,7]

xmin, xmax = hist_binedges[1][0], hist_binedges[1][-1]
ymin, ymax = hist_binedges[0][0], hist_binedges[0][-1]
coords = np.transpose(np.meshgrid(hist_bincenters[1], hist_bincenters[0],\
                        indexing='xy'), axes=(1,2,0))

bgregion = np.ones((1621, 141, 141)).astype(bool)
## first take out central region
bgregion[40:1581, :, :] = False
bgregion[:, 40:101, :] = False
bgregion[:, :, 40:101] = False

for run in runs:
    filename = helper.getparam("filenames", run)
    #hist = np.load("data_hklmat/%s_hist.npy"%filename)
    counts = np.load("data_hklmat/%s_counts.npy"%filename)
    bgregion = np.logical_and(bgregion, counts > 0)
    print "done run %d" % run

print "total %d cells" % np.sum(bgregion)
bgsums = []
ratios = {} 
for run in runs:
    filename = helper.getparam("filenames", run)
    hist = np.load("data_hklmat/%s_hist.npy"%filename)[bgregion]
    counts = np.load("data_hklmat/%s_counts.npy"%filename)[bgregion]
    bgsum = np.sum(hist*1./counts)
    bgsums.append(bgsum)
    if run == 4:
        bgsum0 = bgsum
    else:
        ratios[run] = bgsum*1./bgsum0
    print "done run %d" % run

print bgsums
print ratios
pickle.dump(ratios, open("ratios.pickle", 'wb'))
