import numpy as np
import matplotlib.pyplot as plt
import helper

run = 4 
filename = helper.getparam("filenames", run)

i_file = 0
while True:
    try:
        f = np.load("data_npz/%s_%04d.npz" % (filename, i_file))
        data = f["data"]
        hkl = np.load("data_npz/%s_%04d_hkl.npy" % (filename, i_file))

        maxarg = np.unravel_index(np.argmax(data), data.shape)
        print hkl[:, maxarg[0], maxarg[1]]
    except IOError:
        break

    i_file += 1
