import numpy as np
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.rcParams['xtick.top'] = plt.rcParams['ytick.right'] = True
from scipy import integrate
from settings import hist_bincenters, a0_reciprocal

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
ax.tick_params(top='on', right='on')
ax.legend()
#ax.axhline(y=dpa_ave, color='r')
fig.savefig("plots/dpa_vs_z.pdf", bbox_inches='tight')

## now generate array for L/sin(th)
##    = Integrate{ dpa/dpa_ave*exp(-2*mu*z/sin(th)) / sin(th) }
q0 = 5.612 # for (220), in Angstrom^-1
q1 = hist_bincenters[0][:1620].reshape(162, 10).mean(axis=1) * a0_reciprocal
q = q0 + q1
sinth_array = q*1.23984/(4.*np.pi) # sin(th)
mu = 0.1870 # micron^-1

A2 = []
for sinth in sinth_array:
    ## NOTE: the overall sinth factor is taken care of in the hklhist script
    integrand = dpa/dpa_ave * np.exp(-2.*mu*z/sinth)
    A2.append(integrate.simps(integrand, z))
np.save("fit/A2.npy", A2)
    
plt.show()
