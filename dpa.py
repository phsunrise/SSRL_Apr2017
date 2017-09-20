import numpy as np
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
from scipy import integrate

data = np.genfromtxt("dpa_vs_z.csv", delimiter=',', skip_header=1)
z = data[:,0]
dpa = data[:,4]

fig = plt.figure(figsize=(6,4))
ax = fig.add_subplot(1,1,1)

ind = np.searchsorted(z, 1.0)
dpa_ave = np.mean(dpa[:ind])
print "Average to 1 um:", dpa_ave

ax.plot(z, data[:,1], label="5 MeV")
ax.plot(z, data[:,2], label="2 MeV")
ax.plot(z, data[:,3], label="500 keV")
ax.plot(z, dpa, label="Sum")
ax.set_xlim(0., 2.)
ax.set_ylim(0., 0.12)
ax.set_xlabel(r"Depth $z$ $(\mathrm{\mu m})$")
ax.set_ylabel("DPA")
ax.legend()
#ax.axhline(y=dpa_ave, color='r')
fig.savefig("plots/dpa_vs_z.pdf", bbox_inches='tight')

## now generate array for L/sin(th)
##    = Integrate{ dpa/dpa_ave*exp(-2*mu*z/sin(th)) / sin(th) }
q0 = 5.612 # for (220), in Angstrom^-1
q = q0+np.load("fit/run3_data.npz")['qarray']
sinth_array = q*1.23984/(4.*np.pi) # sin(th)
mu = 0.1870 # micron^-1

A2 = []
for sinth in sinth_array:
    integrand = dpa/dpa_ave * np.exp(-2.*mu*z/sinth) / sinth
    A2.append(integrate.simps(integrand, z))
np.save("fit/A2.npy", A2)
    
plt.show()
