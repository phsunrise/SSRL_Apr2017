import numpy as np
import sys
from orimat import qvec, qvec_array 
from settings import imshape
import time
import pickle
import matplotlib.pyplot as plt

runs = [5, 6] 
scans = pickle.load(open("scans.pickle", 'rb'))
hkl_centers = []

for run in runs:
    filename = scans['filenames'][run] 
    orimat = np.load("orimats/%s.npy"%(scans['orimats'][run]))
    print "starting run %d, filename=%s, orimat=" % (\
                    run, filename)
    print orimat

    i_file = 0 
    now = time.time()
    while True:
        try:
            f = np.load("data_npz/%s_%04d.npz"%(filename, i_file))
            tth = float(np.asscalar(f['tth']))
            th = float(np.asscalar(f['th']))
            chi = float(np.asscalar(f['chi']))
            phi = float(np.asscalar(f['phi']))

            pixs_i, pixs_j = np.meshgrid(np.arange(imshape[0]), np.arange(imshape[1]), \
                                    indexing='ij')
            pixs = [pixs_i.ravel(), pixs_j.ravel()]
            hkl_mat = orimat.dot(qvec_array(tth, th, chi, phi, pixs=pixs))
            hkl_mat = hkl_mat.reshape(np.append(3, imshape))
            hkl_centers.append(orimat.dot(qvec(tth, th, chi, phi)))

            np.save("data_npz/%s_%04d_hkl.npy"%(\
                        filename, i_file), hkl_mat)
            print "done %s_%04d, using %f s" % (\
                        filename, i_file, time.time()-now)
            now = time.time()

        except IOError:
            break

        i_file += 1

hkl_centers = np.array(hkl_centers) - np.repeat([[2.,2.,0.]], \
                                            len(hkl_centers), axis=0)
y = hkl_centers.dot(np.array([1.,1.,0.])/np.sqrt(2.))
x = hkl_centers.dot(np.array([0.,0.,1.]))
plt.scatter(x, y)
plt.show()
