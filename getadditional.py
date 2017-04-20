import numpy as np
import os, sys

wrongfiles = open("add_wrongfiles.txt", 'w')
for root, dirs, files in os.walk(os.getcwd()+"/data"):
    for f in files:
        if f[-4:] == ".csv":
            filename = root+'/'+f
            data = np.genfromtxt(filename, delimiter=',', \
                                 usecols=[0,2,3,10,11,15], skip_header=1)
            ## these columns are: step #, time, monitor, normlz, filters, pd3 
            try:
                attfac = data[:,3]/data[:,5]
            except IndexError:
                wrongfiles.write(filename+'\n')
                print "File %s is wrong" % filename
                continue
 
            for row, i_file in enumerate(data[:,0]):
                basename = f[:-4] + "_%04d" % (int(i_file))
                if os.path.isfile("data_npz/%s.npz"%basename):
                    np.save("data_npz/%s_add.npy"%basename, data[row])
                    print "saved to file data_npz/%s_add.npy"%basename
                else:
                    wrongfiles.write(filename+"_%04d\n"%i_file)
                    print "File %s_%04d is wrong" % (filename, i_file)
                    break

wrongfiles.close()
