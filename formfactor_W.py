import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import sys

q0 = 5.612 # for (220), in Angstrom^-1
#q = np.load("fit/run3_data.npz")['qarray']
q = np.load("fit/qperp_0p020/R10_0_vac.npz")['q']
x = (q + q0)/(4.*np.pi) # sin(tth/2)/lambda

element = 'W'

if element == 'W':
    data = np.genfromtxt("formfactor_table_71to80.txt")
    fp = -9.881 # f prime, value calculated from linear interpolation
                # of henke.lbl.gov table: (64.9743-74) @ 9900.58 eV,
                # (63.5971-74) @ 10060.7 eV, so -9.881 @ 10.000 keV
xx = data[:, 0]
yy = data[:, 4]+fp 

f = interp1d(xx, yy, kind='cubic')
print f(x)

plt.figure()
plt.plot(xx, yy, 'ro')
plt.plot(x, f(x), 'bo')
plt.title("W formfactor")

np.savez("fit/W_ff.npz", ff=f(x), q=q)

plt.show()
