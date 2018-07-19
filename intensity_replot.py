import numpy as np
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.rcParams['xtick.top'] = plt.rcParams['ytick.right'] = True
plt.ion()
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import ImageGrid
import helper
from orimat import qvec
from settings import e0, e1, e2, hist_bincenters, hist_binedges, a0_reciprocal

do_plotsurface = False # set to True to plot surface orientation

runs = [4, 3, 8, 9, 7]
qarray = hist_bincenters[0]*a0_reciprocal
xmin, xmax = hist_binedges[1][0]*a0_reciprocal, hist_binedges[1][-1]*a0_reciprocal
ymin, ymax = hist_binedges[0][0]*a0_reciprocal, hist_binedges[0][-1]*a0_reciprocal

## plot the 2d images
fig = plt.figure(figsize=(6, 8))
grid = ImageGrid(fig, 111, nrows_ncols=(1,5), axes_pad=0.15, \
                 share_all=True, cbar_location='right', \
                 cbar_mode='single', cbar_size="15%", cbar_pad=0.15)
for i_run, run in enumerate(runs):
    ax = grid[i_run]
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", runs[i_run])
    orimat = np.load("orimats/%s.npy"%(helper.getparam("orimats", run)))
    data_orig = np.load("data_hklmat/%s_interpolated_xy.npy"%filename)
    im = ax.imshow(np.log10(data_orig), extent=[xmin, xmax, ymin, ymax], \
                   origin='lower', interpolation='nearest', \
                   vmax=3.0)

    if do_plotsurface:
        surf_norm = orimat.dot(qvec(50., 25., 90., 0.))
        surf_norm = surf_norm/np.linalg.norm(surf_norm)
        print "hkl of surface =", surf_norm 
        surf_norm = orimat.dot(qvec(60., 30., 90., 45.))
        surf_norm = surf_norm/np.linalg.norm(surf_norm)
        print "hkl of surface =", surf_norm, "(to check if th and phi matters)"
        xx = np.array([-1., 1.]) * surf_norm.dot(e1)
        yy = np.array([-1., 1.]) * surf_norm.dot(e0)
        ax.plot(xx, yy, 'r--')

    #ax.axvline(x=hist_bincenters[1][inds[i_run]], color='r', ls='--')

    ## indices: 30 -> -0.020rlu, 50 -> -0.010rlu, 
    ##          90 -> 0.010rlu, 110 -> 0.020rlu
    ### flipping
    if run in [4]:
        ax.add_patch(Rectangle((hist_binedges[1][30-2]*a0_reciprocal, 0.), \
             (hist_binedges[1][50+3]-hist_binedges[1][30-2])*a0_reciprocal, \
             (hist_binedges[0][-1]-0.)*a0_reciprocal, \
             linewidth=0, facecolor='r', alpha=0.5))
        ax.add_patch(Rectangle((hist_binedges[1][90-2]*a0_reciprocal, hist_binedges[0][0]*a0_reciprocal), \
             (hist_binedges[1][110+3]-hist_binedges[1][90-2])*a0_reciprocal, \
             (0.-hist_binedges[0][0])*a0_reciprocal, \
             linewidth=0, facecolor='r', alpha=0.5))
    else:
        ax.add_patch(Rectangle((hist_binedges[1][30-2]*a0_reciprocal, \
                     hist_binedges[0][0]*a0_reciprocal), \
             (hist_binedges[1][50+3]-hist_binedges[1][30-2])*a0_reciprocal, \
             (hist_binedges[0][-1]-hist_binedges[0][0])*a0_reciprocal, \
             linewidth=0, facecolor='r', alpha=0.5))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xticks([-0.05, 0, 0.05])
    ax.set_xticklabels([-5, 0, 5])
    ax.set_title(helper.getsamplename(sample))

fig.text(0.35, 0.04, r"$q(220)[001]$ $(10^{-2}\mathrm{\AA^{-1}})$") # common x label
fig.text(0.015, 0.55, r"$q(220)[110]$ $(\mathrm{\AA^{-1}})$", rotation=90)
cbar = ax.cax.colorbar(im, ticks=[1., 2., 3.])
cbar.ax.set_yticklabels([r"$10^1$", r"$10^2$", r"$\geq 10^3$"])
ax.cax.toggle_label(True)
fig.savefig("plots/intensities.pdf", bbox_inches='tight')
