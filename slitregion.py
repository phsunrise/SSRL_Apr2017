import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
from settings import centralpix, plot_dir

data = np.load("data_npz/0p2dpa_2dscan_2_scan10_0000.npz")['data']
#data = np.load("data_npz/centerpix_1_040517-155118.npz")['data']

plt.imshow(data, interpolation='nearest')
plt.colorbar()
plt.gca().add_patch(patches.Rectangle((148, 60), 200, 132, fill=False, color='r'))
plt.annotate("central pixel", xy=(centralpix[1], centralpix[0]), \
             xytext=(centralpix[1]+100, centralpix[0]+30), \
             arrowprops=dict(facecolor="y", shrink=0.05), color="y")
plt.savefig(plot_dir+"test_slitregion.pdf")
plt.show()
