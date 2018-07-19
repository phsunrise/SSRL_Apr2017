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

runs = [3,4,7,8,9] 

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
    bins = (hist_binedges[0][i_block*162:(i_block+1)*162+1], \
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
    hist = np.zeros([len(bins[i])-1 for i in xrange(3)])
    counts = np.zeros([len(bins[i])-1 for i in xrange(3)])
    while True:
        try:
            for i_file in [0,1]:
                print "starting scan %d, file %d" % (i_scan, i_file)
                print "data_npz/%s_scan%d_%04d.npz"%(\
                               filename, i_scan, i_file)
                data = np.load("data_npz/%s_scan%d_%04d.npz"%(\
                               filename, i_scan, i_file))['data']
                _, t, monitor, normlz, filters, pd3 = np.load("data_npz/%s_scan%d_%04d_add.npy"%(\
                                        filename, i_scan, i_file))
                sinThetai = np.asscalar(np.load("data_npz/%s_scan%d_%04d_sinThetai.npy"%(\
                                    filename, i_scan, i_file)))
                data = data*1./t*(monitor*normlz*1./pd3)*sinThetai # correct for effect of incident angle theta_i
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

        except IOError:
            break

        i_scan += 1

    np.save("data_hklmat/%s_hist_%04d.npy"%(filename, i_block), hist)
    np.save("data_hklmat/%s_counts_%04d.npy"%(filename, i_block), counts)
