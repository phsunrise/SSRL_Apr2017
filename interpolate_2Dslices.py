import sys, os
import numpy as np
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.rcParams['xtick.top'] = plt.rcParams['ytick.right'] = True
plt.ion()
from matplotlib.gridspec import GridSpec
from scipy.interpolate import griddata
from settings import a0, hist_bincenters, hist_binedges, a0_reciprocal
from settings import Rlist, Rlist_colors, R_edges, R_barwidth
from settings import slices
import helper

runs = [4,3,8,9,7]

for i_run, run in enumerate(runs):
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", run)
    hist = np.load("data_hklmat/%s_hist.npy"%filename)
    counts = np.load("data_hklmat/%s_counts.npy"%filename)

    nx, ny, nz = hist.shape
    
    intensities = hist[:,:,68:73].sum(axis=2) * \
                        1./counts[:,:,68:73].sum(axis=2)
    xx, yy = np.meshgrid(range(nx), range(ny), indexing='ij')
    coords = np.array([xx.ravel(), yy.ravel()]).T
    intensities = intensities.ravel()
    mask = np.isnan(intensities)
    intensities[mask] = griddata(
            coords[~mask], intensities[~mask],
            coords[mask], method="linear")
    intensities = intensities.reshape(nx, ny)
    np.save("data_hklmat/%s_interpolated_xy.npy"%(filename), intensities)

    intensities = hist[:,68:73,:].sum(axis=1) * \
                        1./counts[:,68:73,:].sum(axis=1)
    xx, zz = np.meshgrid(range(nx), range(nz), indexing='ij')
    coords = np.array([xx.ravel(), zz.ravel()]).T
    intensities = intensities.ravel()
    mask = np.isnan(intensities)
    intensities[mask] = griddata(
            coords[~mask], intensities[~mask],
            coords[mask], method="linear")
    intensities = intensities.reshape(nx, nz)
    np.save("data_hklmat/%s_interpolated_xz.npy"%(filename), intensities)

    print "Done run %d" % run
