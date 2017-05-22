import numpy as np
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'

fig, ax = plt.subplots(1,1, figsize=(10,5))
for sample, run, color in [("0.2dpa", 3, 'r'), ("5dpa", 7, 'b')]:
    f = np.load("fit/run%d_data.npz"%run)
    q = f['qarray']
    ind = np.searchsorted(q, -0.2)
    data = f['data']*q**4
    ax.plot(q, data, color=color, ls='-', label="%s, Apr17"%sample)

    f = np.load("fit/Nov2016/%s_q4I_3.npz"%sample)
    q = f['q']
    #print len(q)
    q = np.mean(q.reshape(128, 8), axis=1)
    data1 = f['q4I']
    data1 = np.mean(data1.reshape(128, 8), axis=1)
    ind1 = np.searchsorted(q, -0.2)
    data1 *= data[ind]/data1[ind1]
    ax.plot(q, data1, color=color, ls='--', label="%s, Nov16"%sample)

ax.set_ylim(0.0, 0.15)
ax.set_xlim(-0.4, 0.4)
ax.set_xlabel(r"$q$ $(\AA^{-1})$")
ax.set_ylabel(r"$q^4 I$ (arbit. units)")
ax.set_title("Comparison between two experiments")
ax.legend()

fig.savefig("plots/comparison.pdf")
plt.show()
