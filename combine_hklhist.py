import numpy as np
import helper

runs = [5,6]
runs = [3,4,7,8,9]

for run in runs:
    filename = helper.getparam("filenames", run)
    hist = np.zeros((1621, 141, 141))
    counts = np.zeros((1621, 141, 141))

    for i_block in xrange(9):
        hist[i_block*162:(i_block+1)*162, :, :] = np.load(\
                "data_hklmat/%s_hist_%04d.npy"%(filename, i_block))
        counts[i_block*162:(i_block+1)*162, :, :] = np.load(\
                "data_hklmat/%s_counts_%04d.npy"%(filename, i_block))

    i_block = 9 
    hist[i_block*162:, :, :] = np.load(\
            "data_hklmat/%s_hist_%04d.npy"%(filename, i_block))
    counts[i_block*162:, :, :] = np.load(\
            "data_hklmat/%s_counts_%04d.npy"%(filename, i_block))

    np.save("data_hklmat/%s_hist.npy"%(filename), hist)
    np.save("data_hklmat/%s_counts.npy"%(filename), counts)

    print "done run %d" % run
