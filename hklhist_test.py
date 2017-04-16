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
from settings import hist_binedges, e_mat
import pickle
import matplotlib.pyplot as plt

runs = [3] 

if len(sys.argv) < 2: # debug mode; generate file list and exit
    filelist = {}
    for run in runs:
        filelist[run] = []
        filename = helper.getparam('filenames', run)
        for i_block in xrange(10):
            if not (os.path.isfile("data_hklmat/%s_hist_%04d.npy"%(\
                        filename, i_block))
                    and os.path.isfile("data_hklmat/%s_counts_%04d.npy"%(\
                        filename, i_block))):
                filelist[run].append(i_block)
        print "run %d:"%run, filelist[run]

    with open("hklhist_filelist.pickle", 'wb') as f:
        pickle.dump(filelist, f)
    sys.exit(0)

i_block = int(sys.argv[1])
if i_block != 9:
    bins = (hist_binedges[0][i_block*162:i_block*162+163], \
            hist_binedges[1], \
            hist_binedges[2])
else:
    bins = (hist_binedges[0][i_block*162:], \
            hist_binedges[1], \
            hist_binedges[2])
    

for run in runs:
    filename = helper.getparam('filenames', run)
    print "starting run %d, filename=%s" % (\
                    run, filename)

    i_scan = 1 
    while True:
        if i_scan != 280:
            i_scan += 1
            continue
        try:
            for i_file in [0,1]:
                data = np.load("data_npz/%s_scan%d_%04d.npz"%(\
                                filename, i_scan, i_file))['data']
                _, t, monitor, _, _ = np.load("data_npz/%s_scan%d_%04d_add.npy"%(\
                                        filename, i_scan, i_file))
                data = data*1./monitor
                data = data[ar[0]:ar[1], ar[2]:ar[3]].flatten()
                hkl = np.transpose(np.load("data_npz/%s_scan%d_%04d_hkl.npy"%(filename, i_scan, i_file)), (1,2,0))
                hkl = hkl[ar[0]:ar[1], ar[2]:ar[3]].reshape((ar[1]-ar[0])*(ar[3]-ar[2]), 3)
                hkl = hkl - np.repeat([[2.,2.,0.]], len(hkl), axis=0)
                xyz = hkl.dot(e_mat).reshape(ar[1]-ar[0], ar[3]-ar[2], 3)
                for ind in xrange(3):
                    plt.figure()
                    plt.imshow(xyz[:,:,ind], interpolation="nearest")
                    plt.colorbar()
                    plt.show()

            hist1, edges = np.histogramdd(xyz, bins=bins, weights=data)
            counts1, edges = np.histogramdd(xyz, bins=bins)
            
            if i_file == 0:
                hist = hist1
                counts = counts1
            else:
                hist = hist + hist1
                counts = counts + counts1

        except IOError:
            break

        print "done scan %d" % i_scan
        i_scan += 1

    np.save("data_hklmat/%s_hist_%04d.npy"%(filename, i_block), hist)
    np.save("data_hklmat/%s_counts_%04d.npy"%(filename, i_block), counts)
