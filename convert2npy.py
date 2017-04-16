import numpy as np
import os, sys
import re
from settings import imshape, centralpix

do_test = False 

if do_test:
    import matplotlib.pyplot as plt

    filename = "data/b_heimann_0p2dpa_2dscan_2_scan280_0000.raw"

    data = np.fromfile(open(filename, 'rb'), dtype=np.int32).reshape(imshape)
    print data[centralpix]
    plt.imshow(data, interpolation='nearest')
    plt.colorbar()
    plt.show()

else:
    wrongfiles = open("npz_wrongfiles.txt", 'w')
    for root, dirs, files in os.walk(os.getcwd()+"/data"):
        for f in files:
            if f[-4:] == ".raw":
                ## must have a corresponding ".pdi" 
                if os.path.isfile(root+'/'+f+".pdi"):
                    pdifile = root+'/'+f+".pdi"
                elif os.path.isfile(root+'/'+f[:-4]+".pdi"):
                    pdifile = root+'/'+f[:-4]+".pdi"
                else:
                    print "file %s is wrong!" % (root+'/'+f)
                    wrongfiles.write(root+'/'+f+'\n')
                    continue

                ## if have "b_heimann_" at the beginning, take it out
                if f[:10] == "b_heimann_":
                    npzfile = "data_npz/"+f[10:-4]+".npz"
                else:
                    npzfile = "data_npz/"+f[:-4]+".npz"

                if os.path.isfile(npzfile):
                    print "file %s already exists!" % npzfile 
                    continue

                ## read in .raw data
                data = np.fromfile(open(root+'/'+f, 'rb'), dtype=np.int32).reshape(imshape)

                ## read in angles from .pdi file
                for line in open(pdifile, 'r'):
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
                np.savez(npzfile, data=data, \
                         th=th, tth=tth, chi=chi, phi=phi, gam=gam, mu=mu)
                print "done file %s" % (root+'/'+f)

    wrongfiles.close()
