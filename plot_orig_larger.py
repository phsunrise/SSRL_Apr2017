import numpy as np
import pickle
import matplotlib.pyplot as plt
plt.ion()
from settings import centralpix

filenames = ["0p2dpaPristine_2dscan_1", "5dpa_2dscan_1"] # do not include "b_heimann"
a0 = 3.1648
qarray = np.linspace(-0.4, 0.4, 81)*2.*np.pi/a0

for i_run, filename in enumerate(filenames):
    i_file = 1 
    n = 0 
    intensities = []
    attfacs = np.zeros(81)
    times = np.load("data_npz/%s_times.npy"%filename)
    while True:
        try:
            data = np.load("data_npz/%s_scan%d_0000.npz"%(filename, i_file))['data']
            attfac = np.asscalar(np.load("data_npz/%s_scan%d_0000_attfac.npy"%(filename, i_file)))
            #print i_file, "\t", np.sum(data[centralpix[0]-n:centralpix[0]+n+1, centralpix[1]-n:centralpix[1]+n+1]) 
            intensity = np.sum(data[centralpix[0]-n:centralpix[0]+n+1, centralpix[1]-n:centralpix[1]+n+1])*attfac

            data = np.load("data_npz/%s_scan%d_0001.npz"%(filename, i_file))['data']
            attfac = np.asscalar(np.load("data_npz/%s_scan%d_0001_attfac.npy"%(filename, i_file)))

            intensity = np.sum(data[centralpix[0]-n:centralpix[0]+n+1, centralpix[1]-n:centralpix[1]+n+1])*attfac/times[(i_file-1)/7]/2.
            intensities.append(intensity)

            attfacs[(i_file-1)/7] = attfac
        except IOError:
            break
        i_file += 1
        if i_file % 50 == 0:
            print "done file %d" % i_file

    #print intensities
    if i_run == 0:
        intensities0 = np.array(intensities).reshape(81, 7)
    else:
        intensities = np.array(intensities).reshape(81, 7)

plt.figure()
plt.imshow(np.log10(intensities))
plt.colorbar()

intensities = intensities - intensities0
plt.figure()
plt.imshow(np.log10(intensities))
plt.colorbar()

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(qarray, intensities[:,0]*(qarray**4), 'bo--')
ax1.plot(qarray, intensities[:,1]*(qarray**4), 'ro--')
ax1.plot(qarray, intensities[:,2]*(qarray**4), 'go--')
#ax2 = ax1.twinx()
#ax2.semilogy(attfacs, 'b-')
#ax3 = ax1.twinx()
#ax3.plot(times, 'g-')
