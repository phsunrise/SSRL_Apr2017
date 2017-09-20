import numpy as np
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import ImageGrid
import helper
from settings import hist_bincenters, hist_binedges, a0_reciprocal

runs = [4, 3, 8, 9, 7]
qarray = hist_bincenters[0]*a0_reciprocal
xmin, xmax = hist_binedges[1][0]*a0_reciprocal, hist_binedges[1][-1]*a0_reciprocal
ymin, ymax = hist_binedges[0][0]*a0_reciprocal, hist_binedges[0][-1]*a0_reciprocal

fig, ax = plt.subplots(1, 1, figsize=(7,4))

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

    slices.append(data_orig)
    
    resample_shape = (162, 10)
    qarray_plot = np.mean(qarray[:np.prod(resample_shape)].reshape(*resample_shape), axis=1)

    ## uncomment the following to consider effect of multiple peaks
    #if run in [3, 8]: # 0.2dpa, 0.6dpa
    #    ind = [50] 
    #        # 50 for -0.010 rlu, 60 for -0.005, 80 for 0.005, 90 for 0.010 
    #elif run == 4: # 0.2dpa_ref
    #    ind = [50]
    #elif run == 7: # 5dpa
    #    ind = [57] # 57 for -0.0065, 83 for 0.0065
    #elif run == 9: # 2dpa
    #    ind = [58] # 58 for -0.006, 82 for 0.006
    ## not considering effect of multiple peaks
    ind = [50]

    inds.append(ind[0])

    data = np.zeros(resample_shape)
    for i in ind:
        data += np.mean(data_orig[:np.prod(resample_shape), i-2:i+3], \
                            axis=1).reshape(*resample_shape)
    data = data*1./len(ind)

    if run == 4: # 0.2dpa_ref
        data0 = data
        err_plot0 = np.std(data, axis=1)/np.sqrt(resample_shape[1])
        #data_plot = np.mean(data, axis=1)
        #np.savez("fit/run%d_data.npz"%run, qarray=qarray_plot, \
        #         data=data_plot, err=err_plot)
        #ax.errorbar(qarray_plot, qarray_plot**4*data_plot, \
        #            yerr=qarray_plot**4*err_plot, fmt='-', lw=0.8, label=sample)
        continue

    err_plot = ((np.std(data, axis=1)/np.sqrt(resample_shape[1]))**2+err_plot0**2)**0.5
    data = data - data0

    if sample == "0.6dpa":
        fig_temp, ax_temp = plt.subplots(1,1)
        ax_temp.plot(qarray[:1620], qarray[:1620]**4*data.reshape(1620))
        ax_temp.set_ylim(0., 0.15)
        ax_temp.set_xlim(-0.5, 0.5)
        ax_temp.set_title(sample)

    data_plot = np.mean(data, axis=1)
    np.savez("fit/run%d_data.npz"%run, qarray=qarray_plot, \
             data=data_plot, err=err_plot)
    
    ax.errorbar(qarray_plot, qarray_plot**4*data_plot, \
                yerr=qarray_plot**4*err_plot, fmt='-', lw=0.8, \
                label=helper.getsamplename(sample))
    #ax.errorbar(qarray_plot, data_plot, \
    #            yerr=err_plot, fmt='-', lw=0.8, \
    #            label=helper.getsamplename(sample))

ax.set_xlim(-0.7, 0.7)
ax.set_ylim(0., 0.2)
#ax.set_ylim(1.e0, 1.e4)
#ax.set_yscale('log')
#ax.axhline(y=0, color='k', ls='-', lw=0.5)
ax.legend()
ax.set_xlabel(r"$q$ $(\AA^{-1})$")
ax.set_ylabel(r"$q^4 I$")
fig.savefig("plots/q4I.pdf", bbox_inches='tight')

## plot the 2d images
fig = plt.figure(figsize=(6, 8))
grid = ImageGrid(fig, 111, nrows_ncols=(1,5), axes_pad=0.15, \
                 share_all=True, cbar_location='right', \
                 cbar_mode='single', cbar_size="15%", cbar_pad=0.15)
slices = np.log10(np.array(slices))
slices[slices<-1.e6] = np.nan
vmin, vmax = np.nanmin(slices), np.nanmax(slices)
vmax = 3.0 
print(vmin, vmax)
for i_run, run in enumerate(runs):
    ax = grid[i_run]
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", runs[i_run])
    data_orig = np.load("data_hklmat/%s_interpolated.npy"%filename)
    im = ax.imshow(np.log10(data_orig), extent=[xmin, xmax, ymin, ymax], \
                   origin='lower', interpolation='nearest', \
                   vmin=vmin, vmax=vmax)
    print("%s, slice at %f" % (sample, hist_bincenters[1][inds[i_run]]))
    #ax.axvline(x=hist_bincenters[1][inds[i_run]], color='r', ls='--')
    if run in [4]:
        ax.add_patch(Rectangle((hist_binedges[1][inds[i_run]-2]*a0_reciprocal, 0.), \
             (hist_binedges[1][inds[i_run]+3]-hist_binedges[1][inds[i_run]-2])*a0_reciprocal, \
             (hist_binedges[0][-1]-0.)*a0_reciprocal, \
             linewidth=0, facecolor='r', alpha=0.5))
        ax.add_patch(Rectangle((hist_binedges[1][90-2]*a0_reciprocal, hist_binedges[0][0]*a0_reciprocal), \
             (hist_binedges[1][90+3]-hist_binedges[1][90-2])*a0_reciprocal, \
             (0.-hist_binedges[0][0])*a0_reciprocal, \
             linewidth=0, facecolor='r', alpha=0.5))
    else:
        ax.add_patch(Rectangle((hist_binedges[1][inds[i_run]-2]*a0_reciprocal, hist_binedges[0][0]*a0_reciprocal), \
             (hist_binedges[1][inds[i_run]+3]-hist_binedges[1][inds[i_run]-2])*a0_reciprocal, \
             (hist_binedges[0][-1]-hist_binedges[0][0])*a0_reciprocal, \
             linewidth=0, facecolor='r', alpha=0.5))
    ax.set_ylim(-0.5, 0.5)
    ax.set_xticks([-0.05, 0, 0.05])
    ax.set_xticklabels([-5, 0, 5])
    ax.set_ylabel(r"$q[110]$ $(\mathrm{\AA^{-1}})$")
    ax.set_title(helper.getsamplename(sample))

fig.text(0.4, 0.1, r"$q[001]$ $(10^{-2}\mathrm{\AA^{-1}})$") # common x label
cbar = ax.cax.colorbar(im, ticks=[1., 2., 3.])
cbar.ax.set_yticklabels([r"$10^1$", r"$10^2$", r"$\geq 10^3$"])
ax.cax.toggle_label(True)
fig.savefig("plots/intensities.pdf", bbox_inches='tight')
plt.show()
