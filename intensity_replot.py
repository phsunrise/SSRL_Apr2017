import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import helper
from settings import hist_bincenters, hist_binedges, a0_reciprocal
import pickle

runs = [4, 3, 8, 9, 7]
qarray = hist_bincenters[0]*a0_reciprocal
xmin, xmax = hist_binedges[1][0], hist_binedges[1][-1]
ymin, ymax = hist_binedges[0][0], hist_binedges[0][-1]
ratios = pickle.load(open("ratios.pickle", 'rb'))

fig, ax = plt.subplots(1, 1, figsize=(10,5))


ind = 50 # 50 for -0.10, 60 for -0.05, 80 for 0.05, 90 for 0.10 

slices = []
for run in runs:
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", run)
    data = np.load("data_hklmat/%s_interpolated.npy"%filename)
    if sample in ["0.2dpa_ref"]: # flip lower half
        data[:811, :] = np.fliplr(data[:811, :])
    slices.append(data)
    
    if sample == "0.2dpa_ref":
        data0 = data
        continue

    data = data - data0
    #data = data/ratios[run] - data0

    resample_shape = (162, 10)
    qarray_plot = np.mean(qarray[:np.prod(resample_shape)].reshape(*resample_shape), axis=1)
    data = np.mean(data[:np.prod(resample_shape), ind-2:ind+3], \
                        axis=1).reshape(*resample_shape)
    err_plot = np.std(data, axis=1)
    data_plot = np.mean(data, axis=1)
    
    ax.errorbar(qarray_plot, qarray_plot**4*data_plot, \
                 yerr=qarray_plot**4*err_plot, fmt='-', lw=0.8, label=sample)

ax.set_ylim(-0.1, 0.15)
ax.axhline(y=0, color='k', ls='-', lw=0.5)
ax.legend()
ax.set_xlabel(r"$q$ $(\AA^{-1})$")
ax.set_ylabel(r"$q^4 I$")
fig.savefig("plots/q4I.pdf")

## plot the 2d images
fig = plt.figure(figsize=(10, 12))
grid = ImageGrid(fig, 111, nrows_ncols=(1,5), axes_pad=0.15, \
                 share_all=True, cbar_location='right', \
                 cbar_mode='single', cbar_size="15%", cbar_pad=0.15)
slices = np.log10(np.array(slices))
slices[slices<-1.e6] = np.nan
vmin, vmax = np.nanmin(slices), np.nanmax(slices)
print vmin, vmax
for i_run, ax in enumerate(grid):
    sample = helper.getparam("samples", runs[i_run])
    im = ax.imshow(slices[i_run], extent=[xmin, xmax, ymin, ymax], \
                   origin='lower', interpolation='nearest', \
                   vmin=vmin, vmax=vmax)
    ax.axvline(x=-0.01, color='r', ls='--')
    ax.set_xlabel("[001]")
    ax.set_ylabel("[110]")
    ax.set_title(sample)

ax.cax.colorbar(im)
ax.cax.toggle_label(True)
fig.savefig("plots/intensities.pdf")
plt.show()
