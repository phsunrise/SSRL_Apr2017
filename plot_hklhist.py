import numpy as np
import matplotlib.pyplot as plt
import helper

runs = [3, 4]

for run in runs:
    filename = helper.getparam("filenames", run)
    hist = np.load("data_hklmat/%s_hist.npy"%filename)
    counts = np.load("data_hklmat/%s_counts.npy"%filename)
    
    #hist = np.sum(hist[:,:,69:72], axis=2)
    #counts = np.sum(counts[:,:,69:72], axis=2)
    hist = hist[:,:,71]
    counts = counts[:,:,71]
    hist = np.nan_to_num(hist*1./counts)
    
    plt.imshow(np.log10(hist), interpolation='nearest')
    plt.colorbar()
    plt.title("run %d"%run)
    plt.show()
