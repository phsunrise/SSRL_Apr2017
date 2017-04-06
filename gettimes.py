import numpy as np
import pickle
import matplotlib.pyplot as plt

filename = "si_thtth_1_scan4" # do not include "b_heimann"

i_file = 0
maxs = []
while True:
    try:
        data = np.load("data_npz/%s_scan%d_0000.npz"%(filename, i_file))['data']
        #attfac = np.asscalar(np.load("data_npz/%s_%04d_attfac.npy"%(filename, i_file)))
        maxs.append(np.max(data))
    except IOError:
        break
    i_file += 1

print maxs
plt.figure()
plt.xlabel("scan step #")
plt.ylabel("max count")
plt.semilogy(maxs, 'ro-')

times = 10000./np.array(maxs)
times = np.ceil(times)
times[times>30.] = 30.
print times
plt.figure()
plt.plot(times)
plt.xlabel("scan step #")
plt.ylabel("time (s)")
plt.show()

np.save("times.npy", times)
