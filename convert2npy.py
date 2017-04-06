import numpy as np
import os, sys
import re
from settings import imshape

do_test = False 

if do_test:
    import matplotlib.pyplot as plt

    filename = "data/b_heimann_si_thtth_1_scan4_0050.raw"

    data = np.fromfile(open(filename, 'rb'), dtype=np.int32).reshape(imshape)
    plt.imshow(data, interpolation='nearest')
    plt.colorbar()
    plt.show()

else:
    wrongfiles = open("wrongfiles.txt", 'w')
    for root, dirs, files in os.walk(os.getcwd()+"/data"):
        for f in files:
            if f[-4:] == ".raw":
                if f[:10] != "b_heimann_" or not os.path.isfile(root+'/'+f+".pdi"):
                    print "file %s is wrong!" % (root+'/'+f)
                    wrongfiles.write(root+'/'+f+'\n')
                    continue

                elif os.path.isfile("data_npz/"+f[10:-4]+".npz"):
                    print "file %s already exists!" % f
                    continue

                ## read in .raw data
                data = np.fromfile(open(root+'/'+f, 'rb'), dtype=np.int32).reshape(imshape)

                ## read in angles from .pdi file
                for line in open(root+'/'+f+".pdi", 'r'):
                    if line.startswith("# Theta"):
                        #th, _, tth, chi, phi, gam, mu = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line)
                        values = line.split(' ')
                        values_valid = []
                        for value in values:
                            if len(value)>1 and value[-1] == ';':
                                value = value[:-1]
                            try:
                                value = float(value)
                                values_valid.append(value)
                            except ValueError:
                                continue
                        #print line
                        #print values_valid
                        th, tth, chi, phi, gam, mu = values_valid
                        break
                np.savez("data_npz/"+f[10:-4]+".npz", data=data, \
                         th=th, tth=tth, chi=chi, phi=phi, gam=gam, mu=mu)
                #np.save("data_npz/"+f[10:-4], data)
                print "done file %s" % (root+'/'+f)

    wrongfiles.close()
