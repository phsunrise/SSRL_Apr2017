import numpy as np
import glob
import os

filenames = glob.glob("data/*.csv")
indexerrorfiles = []

for filename in filenames:
    print "reading %s" % filename
    data = np.genfromtxt(filename, delimiter=',', \
                         usecols=[0,5,12,17], skip_header=1)
    ## these columns are: step #, monitor counts, normlz, pd3 
    try:
        attfac = data[:,2]/data[:,3]
    except IndexError:
        indexerrorfiles.append(filename)
        continue
    
    for row, i_file in enumerate(data[:,0]):
        basename = filename[:-4] + "_%04d" % (int(i_file))
        if os.path.isfile(basename+".npz"):
            np.save(basename+"_attfac.npy", attfac[row])
            print "saved to file", basename+"_attfac.npy"

print indexerrorfiles
