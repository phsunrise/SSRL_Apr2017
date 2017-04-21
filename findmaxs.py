import numpy as np
import helper
from settings import ar # active region on the detector, due to slit 
from settings import hist_binedges, e_mat
import pickle

run = 7 

filename = helper.getparam("filenames", run)
i_scan = 1
maxs = []
while True:
    try:
        for i_file in [0, 1]:
            print "starting scan %d, file %d" % (i_scan, i_file)
            data = np.load("data_npz/%s_scan%d_%04d.npz"%(\
                           filename, i_scan, i_file))['data']
            _, t, monitor, normlz, filters, pd3 = np.load("data_npz/%s_scan%d_%04d_add.npy"%(\
                                    filename, i_scan, i_file))
            data = data*1./t*(monitor*normlz*1./pd3)
            data = data[ar[0]:ar[1], ar[2]:ar[3]]
            ma = np.max(data)
            maind = np.unravel_index(np.argmax(data), data.shape)

            hkl = np.transpose(np.load("data_npz/%s_scan%d_%04d_hkl.npy"%(\
                                filename, i_scan, i_file)), (1,2,0))
            hkl = hkl[ar[0]:ar[1], ar[2]:ar[3]]
            xyz = (hkl[maind[0], maind[1]]-np.array([2,2,0])).dot(e_mat)

            maxs.append((i_scan, i_file, ma, maind, xyz))
    except IOError:
        break

    i_scan += 1

pickle.dump(maxs, open("run%d_maxs.pickle"%run, 'wb'))

maxs.sort(key=lambda tup:tup[2])
for i_scan, i_file, ma, maind, xyz in maxs:
    print "%10d  (%4d, %4d)  %10f  %10f  %10f  %4d" % (\
            ma, maind[0], maind[1], xyz[0], xyz[1], xyz[2], i_scan)
