'''
To run this scipt:
    python hklhist.py [i_block]
where [i_block] is the number of the block

The hist range is:
-0.405 to 0.405 in [110] direction, total 1621 bins
-0.035 to 0.035 in [001] direction, total 141 bins
-0.035 to 0.035 in [1-10] direction, total 141 bins

We divide along [110] direction into 10 blocks, first 9 are 162*141*141,
last one is 163*141*141
'''
import numpy as np
import helper
import os, sys
from settings import ar # active region on the detector, due to slit 
from settings import hist_binedges, hist_bincenters, e_mat
from settings import imshape, centralpix
import matplotlib.pyplot as plt

runs = [3] 

bins = (hist_binedges[0], hist_binedges[1], hist_binedges[2][70:72])
xmin, xmax = hist_binedges[1][0], hist_binedges[1][-1]
ymin, ymax = hist_binedges[0][0], hist_binedges[0][-1]
coords = np.transpose(np.meshgrid(hist_bincenters[1], hist_bincenters[0],\
                        indexing='xy'), axes=(1,2,0))

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8,10), \
                            sharex=True, sharey=True)
im1 = ax1.imshow(np.zeros((1621, 141)), interpolation="nearest", \
                     origin='lower', aspect='auto', \
                     extent=[xmin, xmax, ymin, ymax])
im2 = ax2.imshow(np.zeros((1621, 141)), interpolation="nearest", \
                     origin='lower', aspect='auto', \
                     extent=[xmin, xmax, ymin, ymax])
ax1.vlines(np.linspace(-0.03, 0.03, 7), ymin, ymax, linestyles='--', lw=0.5)
ax1.hlines(np.linspace(-0.40, 0.40, 81), xmin, xmax, linestyles='--', lw=0.5)
ax2.vlines(np.linspace(-0.03, 0.03, 7), ymin, ymax, linestyles='--', lw=0.5)
ax2.hlines(np.linspace(-0.40, 0.40, 81), xmin, xmax, linestyles='--', lw=0.5)
ax1.set_xlim(xmin, xmax)
ax1.set_ylim(ymin, ymax)

plt.ion()
plt.show()

for run in runs:
    filename = helper.getparam('filenames', run)
    print "starting run %d, filename=%s" % (\
                    run, filename)

    i_scan = 220 
    hist = np.zeros([len(bins[i])-1 for i in xrange(3)])
    counts = np.zeros([len(bins[i])-1 for i in xrange(3)])
    while True:
        try:
            for i_file in [1]:
                #print "starting scan %d, file %d" % (i_scan, i_file)
                data = np.load("data_npz/%s_scan%d_%04d.npz"%(\
                               filename, i_scan, i_file))['data']
                _step, t, _monitor, normlz, filters, pd3 = np.load("data_npz/%s_scan%d_%04d_add.npy"%(\
                                        filename, i_scan, i_file))
                
                #data = data*1./t*(pd3*1./normlz)
                data = data*1./t*(_monitor*normlz/pd3)
                data = data[ar[0]:ar[1], ar[2]:ar[3]].flatten()
                hkl = np.transpose(np.load("data_npz/%s_scan%d_%04d_hkl.npy"%(\
                                    filename, i_scan, i_file)), (1,2,0))
                hkl = hkl[ar[0]:ar[1], ar[2]:ar[3]].reshape((ar[1]-ar[0])*(ar[3]-ar[2]), 3)
                hkl = hkl - np.repeat([[2.,2.,0.]], len(hkl), axis=0)
                xyz = hkl.dot(e_mat)

                hist1, edges = np.histogramdd(xyz, bins=bins, weights=data)
                counts1, edges = np.histogramdd(xyz, bins=bins)
                
                hist = hist + hist1
                counts = counts + counts1

                imdata = np.log10(hist/counts)[:,:,0]
                im1.set_data(imdata)
                im1.autoscale()

                im2.set_data(counts[:,:,0])
                im2.autoscale()
                ax1.set_title("scan %d, file %d" %(i_scan, i_file))
                plt.draw()

                #if abs(1/_monitor - normlz/pd3) > 1.e-10:
                print "%4d\t%.2f\t%e\t%e\t%e\t%04d"%(i_scan, \
                    t, 1/_monitor, normlz/pd3, normlz/pd3*_monitor, filters)
                _xyz = xyz[(centralpix[0]-ar[0])*(ar[3]-ar[2])+centralpix[1]-ar[2]]
                print "\t[%.4f %.4f %.4f]"%(_xyz[0], _xyz[1], _xyz[2])

                #elif i_file == 0 and i_scan%5 ==0:
                #    print "done scan %4d" % i_scan

                if 250 < i_scan < 330 and i_scan % 7 == 0 and i_file == 1:
                    raw_input()


        except IOError:
            break

        i_scan += 1 

    #np.save("data_hklmat/%s_hist_%04d.npy"%(filename, i_block), hist)
    #np.save("data_hklmat/%s_counts_%04d.npy"%(filename, i_block), counts)
