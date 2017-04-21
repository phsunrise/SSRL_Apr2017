import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
from settings import centralpix, plot_dir
import helper
import sys

run, i_scan = int(sys.argv[1]), int(sys.argv[2])

filename = helper.getparam("filenames", run)
data = np.load("data_npz/%s_scan%d_0000.npz" % (filename, i_scan))['data']
#data = np.load("data_npz/centerpix_1_040517-155118.npz")['data']

plt.imshow(data, interpolation='nearest')
plt.colorbar()
plt.gca().add_patch(patches.Rectangle((148, 60), 200, 132, fill=False, color='r'))
plt.annotate("central pixel", xy=(centralpix[1], centralpix[0]), \
             xytext=(centralpix[1]+100, centralpix[0]+30), \
             arrowprops=dict(facecolor="y", shrink=0.05), color="y")
plt.savefig(plot_dir+"test_slitregion.pdf")
plt.show()
