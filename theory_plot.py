import numpy as np
from settings import Rlist, Rlist_colors
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'

qarray = np.load("fit/run3_data.npz")['qarray']

fit_inds = [0, 2] 
for fit_ind in fit_inds:
    fig, ax = plt.subplots(1, 1, figsize=(14,5))
    ls = {'int':':', 'vac':'--'}

    for i_R, R in enumerate(Rlist):
        for looptype in ['int', 'vac']:
            data = np.load("fit/R%d_%d_%s.npz"%(R, fit_ind, looptype))['q4I']
            ax.plot(qarray, data/R**2, color=Rlist_colors[i_R], \
                    ls=ls[looptype], \
                    label=('%d'%R if looptype=='int' else ''))

    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0., 10.)
    ax.set_xlabel(r"$q$ $(\AA^{-1})$")
    ax.set_ylabel(r"$q^4 I/R^2$")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    fig.savefig("plots/slice_all_%d.pdf"%fit_ind)

plt.show()
