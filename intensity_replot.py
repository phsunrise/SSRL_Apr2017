import numpy as np
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
from mpl_toolkits.axes_grid1 import ImageGrid
import helper
from settings import hist_bincenters, hist_binedges, a0_reciprocal
import pickle

runs = [4, 3, 8, 9, 7]
qarray = hist_bincenters[0]*a0_reciprocal
xmin, xmax = hist_binedges[1][0]*a0_reciprocal, hist_binedges[1][-1]*a0_reciprocal
ymin, ymax = hist_binedges[0][0]*a0_reciprocal, hist_binedges[0][-1]*a0_reciprocal
ratios = pickle.load(open("ratios.pickle", 'rb'))

fig, ax = plt.subplots(1, 1, figsize=(10,5))

slices = []
inds = []
for run in runs:
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", run)
    data_orig = np.load("data_hklmat/%s_interpolated.npy"%filename)
    if run in [4]: # flip lower half
        data_orig[:811, :] = np.fliplr(data_orig[:811, :])
    if run in []: # flip upper half
        data_orig[811:, :] = np.fliplr(data_orig[811:, :])

    #if run != 4:
    #    data_orig = data_orig/ratios[run]
    slices.append(data_orig)
    
    resample_shape = (162, 10)
    qarray_plot = np.mean(qarray[:np.prod(resample_shape)].reshape(*resample_shape), axis=1)

    if run in [3, 8]: # 0.2dpa, 0.6dpa
        ind = [50] 
            # 50 for -0.010, 60 for -0.005, 80 for 0.005, 90 for 0.010 
    elif run == 4: # 0.2dpa_ref
        ind = [50]
    elif run == 7: # 5dpa
        ind = [57] # 57 for -0.0065, 83 for 0.0065
    elif run == 9: # 2dpa
        ind = [58] # 58 for -0.006, 82 for 0.006
    inds.append(ind[0])

    data = np.zeros(resample_shape)
    for i in ind:
        data += np.mean(data_orig[:np.prod(resample_shape), i-2:i+3], \
                            axis=1).reshape(*resample_shape)
    data = data*1./len(ind)

    if run == 4: # 0.2dpa_ref
        data0 = data
        err_plot0 = np.std(data, axis=1)
        #data_plot = np.mean(data, axis=1)
        #np.savez("fit/run%d_data.npz"%run, qarray=qarray_plot, \
        #         data=data_plot, err=err_plot)
        #ax.errorbar(qarray_plot, qarray_plot**4*data_plot, \
        #            yerr=qarray_plot**4*err_plot, fmt='-', lw=0.8, label=sample)
        continue

    err_plot = (np.std(data, axis=1)**2+err_plot0**2)**0.5
    data = data - data0
    data_plot = np.mean(data, axis=1)
    np.savez("fit/run%d_data.npz"%run, qarray=qarray_plot, \
             data=data_plot, err=err_plot)
    
    ax.errorbar(qarray_plot, qarray_plot**4*data_plot, \
                yerr=qarray_plot**4*err_plot, fmt='-', lw=0.8, label=sample)

ax.set_ylim(-0.05, 0.15)
ax.set_xlim(-0.6, 0.6)
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
    print "%s, slice at %f" % (sample, hist_bincenters[1][inds[i_run]])
    ax.axvline(x=hist_bincenters[1][inds[i_run]], color='r', ls='--')
    ax.set_xticks([-0.05, 0.05])
    ax.set_xlabel(r"[001]")
    ax.set_ylabel(r"[110] $(\AA^{-1})$")
    ax.set_title(sample)

ax.cax.colorbar(im)
ax.cax.toggle_label(True)
fig.savefig("plots/intensities.pdf")
plt.show()
