import sys, os
import numpy as np
import scipy.optimize
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.ion()
from scipy.interpolate import griddata
from settings import a0, hist_bincenters, hist_binedges, a0_reciprocal
from settings import Rlist, Rlist_colors, R_edges, R_barwidth
from settings import slices
import helper

runs = [4,3,8,9,7]

q = hist_bincenters[0][:1620].reshape(162, 10).mean(axis=1) * a0_reciprocal
## range to be fitted
fitrg = (-0.7, 0.7)
indmin, indmax = np.searchsorted(q, fitrg)
q = q[indmin:indmax]

intensities0 = np.zeros((len(slices), indmax-indmin))
fig_raw, ax_raw = plt.subplots(1, 1, figsize=(7, 3))
for i_run, run in enumerate(runs):
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", run)
    hist = np.load("data_hklmat/%s_hist.npy"%filename)
    counts = np.load("data_hklmat/%s_counts.npy"%filename)

    ## flip lower half of run 4
    if run == 4:
        hist[:811, :, :] = np.flip(hist[:811, :, :], 1)
        counts[:811, :, :] = np.flip(counts[:811, :, :], 1)
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))

    for i_s, (yind, zind, qperp) in enumerate(slices):
        hist_slice = np.sum(hist[:, (yind-2):(yind+3), (zind-2):(zind+3)], axis=(1,2))
        hist1 = hist_slice[:1620].reshape(162, 10).sum(axis=1)[indmin:indmax]
        hist1_std = hist_slice[:1620].reshape(162, 10).std(axis=1)[indmin:indmax]
        counts_slice = np.sum(counts[:, (yind-2):(yind+3), (zind-2):(zind+3)], axis=(1,2))
        counts1 = counts_slice[:1620].reshape(162, 10).sum(axis=1)[indmin:indmax]
        
        ## plot raw data
        if (yind, zind) == (50, 70):
            ax_raw.errorbar(q, np.nan_to_num(hist1*1./counts1), \
                            yerr=np.nan_to_num(hist1_std*1./counts1), \
                            color=('k' if run==4 else Rlist_colors[i_run-1]), \
                            label=helper.getsamplename(sample))

        if run == 4:
            intensities0[i_s] = np.nan_to_num(hist1*1./counts1)
            ax.plot(q, (intensities0[i_s]-intensities0[0])*q**4, \
                    color=Rlist_colors[i_s])
            np.save("fit/run%d_slice_%d.npy"%(run, i_s), intensities0[i_s])

        else:
            intensities = np.nan_to_num(hist1*1./counts1) - \
                                intensities0[i_s]
            intensities_err = (intensities0.max(axis=0) - intensities0.min(axis=0))*0.5
            np.save("fit/run%d_slice_%d.npy"%(run, i_s), intensities)

            q4I = q**4 * intensities
            ax.plot(q, q4I, ls='-', color=Rlist_colors[i_s]) 

    ax.set_title(sample)
    ax.set_xlabel("q (rlu)")
    ax.set_xlim(-0.7, 0.7)
    if run == 4:
        ax.set_ylim(-0.05, 0.1)
    else:
        ax.set_ylim(0., 0.2)

## plot the slices
fig, ax = plt.subplots(1, 1)
for i_s, (yind, zind, qperp) in enumerate(slices):
    ax.scatter(hist_bincenters[1][yind], hist_bincenters[2][zind],
               color=Rlist_colors[i_s], label=str(i_s))
ax.legend()

ax_raw.set_xlim(-0.7, 0.7)
ax_raw.set_yscale('log')
ax_raw.set_ylim(1, 500)
ax_raw.set_xlabel(r"$q(220)$ $(\mathrm{\AA^{-1}})$")
ax_raw.set_ylabel(r"$I$ (arb. unit)")
ax_raw.legend()
fig_raw.savefig("plots/intensities_raw.pdf", bbox_inches='tight')
