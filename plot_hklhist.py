import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from settings import hist_bincenters, hist_binedges
import helper

runs = [3,4,7,8,9]

xmin, xmax = hist_binedges[1][0], hist_binedges[1][-1]
ymin, ymax = hist_binedges[0][0], hist_binedges[0][-1]
coords = np.transpose(np.meshgrid(hist_bincenters[1], hist_bincenters[0],\
                        indexing='xy'), axes=(1,2,0))

for run in runs:
    filename = helper.getparam("filenames", run)
    sample = helper.getparam("samples", run)
    hist = np.load("data_hklmat/%s_hist.npy"%filename)
    counts = np.load("data_hklmat/%s_counts.npy"%filename)
    
    if run == 7: # center between two peaks is at y = 0.0075, yind = 85
        hist1 = np.sum(hist[:,83:88,:], axis=1)
        counts1 = np.sum(counts[:,83:88,:], axis=1)
    elif run == 9: # center between two peaks is at z = -0.0065, zind = 57
        hist1 = np.sum(hist[:,:,55:60], axis=2)
        counts1 = np.sum(counts[:,:,55:60], axis=2)
    else: # center is at yind = 70, zind = 70 
        hist1 = np.sum(hist[:,:,68:73], axis=2)
        counts1 = np.sum(counts[:,:,68:73], axis=2)
    
    intensities = np.nan_to_num(hist1*1./counts1)

    ## interpolate to fill up zero values
    mask_zero = (intensities==0) 
    mask_nonz = (intensities!=0) 
    intensities[mask_zero] = griddata(
         coords[mask_nonz], intensities[mask_nonz],
         coords[mask_zero], method="linear", fill_value=0)
    np.save("data_hklmat/%s_interpolated.npy"%(filename), intensities)
    print "saved interpolated data to: data_hklmat/%s_interpolated.npy"%(\
                                filename)
    
    fig, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4, \
                                    sharex=True, sharey=True, \
                                    figsize=(10, 15))
    im0 = ax0.imshow(np.log10(intensities), interpolation='nearest', \
                     origin='lower', #aspect='auto', \
                     extent=[xmin, xmax, ymin, ymax])
    fig.colorbar(im0, ax=ax0)
    ax0.set_title("run %d"%run)
    ax0.axvline(-0.01, color='r', ls='--')
    ax0.axvline(0.01, color='r', ls='--')

    im1 = ax1.imshow(counts[:,:,70], interpolation='nearest', \
                     origin='lower', #aspect='auto', \
                     extent=[xmin, xmax, ymin, ymax])
    fig.colorbar(im1, ax=ax1)
    im2 = ax2.imshow(counts[:,:,71], interpolation='nearest', \
                     origin='lower', #aspect='auto', \
                     extent=[xmin, xmax, ymin, ymax])
    fig.colorbar(im2, ax=ax2)
    im3 = ax3.imshow(counts[:,:,72], interpolation='nearest', \
                     origin='lower', #aspect='auto', \
                     extent=[xmin, xmax, ymin, ymax])
    fig.colorbar(im3, ax=ax3)
    
    ax0.set_xlim(xmin, xmax)
    ax0.set_ylim(ymin, ymax)

    plt.savefig("plots/%s_hklhist.pdf"%sample)
    plt.show()
