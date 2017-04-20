import matplotlib.pyplot as plt
import numpy as np
import helper
from settings import hist_bincenters, hist_binedges
import sys

run = 9 

filename = helper.getparam("filenames", run)
sample = helper.getparam("samples", run)
hist = np.load("data_hklmat/%s_hist.npy"%filename)
counts = np.load("data_hklmat/%s_counts.npy"%filename)

# average over 3*3*3 blocks
hist = hist[740:881, :, :].reshape(47, 3, 47, 3, 47, 3) 
hist = np.sum(hist, axis=(1,3,5))
counts = counts[740:881, :, :].reshape(47, 3, 47, 3, 47, 3) 
counts = np.sum(counts, axis=(1,3,5))
hist_bincenters[0] = hist_bincenters[0][741:880][::3]
hist_bincenters[1] = hist_bincenters[1][1::3]
hist_bincenters[2] = hist_bincenters[2][1::3]
hist_binedges[0] = hist_binedges[0][740:882][::3]
hist_binedges[1] = hist_binedges[1][::3]
hist_binedges[2] = hist_binedges[2][::3]
for i in xrange(3):
    print len(hist_bincenters[i]), len(hist_binedges[i])

xmin, xmax = hist_binedges[1][0], hist_binedges[1][-1]
ymin, ymax = hist_binedges[0][0], hist_binedges[0][-1]

intensities = np.log10(hist*1./counts)
intensities[intensities < -1.e6] = np.nan
vmin, vmax = np.nanmin(intensities), np.nanmax(intensities)

fig, ax = plt.subplots(1, 1, figsize=(10, 10))
im = ax.imshow(np.zeros((intensities.shape[0], intensities.shape[1])), \
               origin='lower', extent=[xmin, xmax, ymin, ymax], \
               interpolation='nearest', vmin=vmin, vmax=vmax)
fig.colorbar(im, ax=ax)
ax.set_xlabel("[001]")
ax.set_ylabel("[110]")
for i in xrange(intensities.shape[2]):
    im.set_data(intensities[:,:,i])
    ax.set_title("%.4f"%(hist_bincenters[2][i]))
    plt.draw()
    fig.savefig("plots/run%d/run%d_%04d.png" % (run, run, i))
    print "done %d" % i
