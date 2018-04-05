import numpy as np
from settings import Rlist, Rlist_colors
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'

datadir = "fit/qperp_0p020/"

fit_inds = [0, ] 
for fit_ind in fit_inds:
    fig, ax = plt.subplots(1, 1, figsize=(12,4))
    ls = {'int':'-', 'vac':'--'}

    for i_R, R in enumerate(Rlist):
        for looptype in ['int', 'vac']:
            _f = np.load(datadir+"R%d_%d_%s.npz"%(R, fit_ind, looptype))
            data = _f['q4I']
            q = _f['q']
            ff = np.load("fit/W_ff.npz")['ff']
            re = 2.8179e-5 # electron radius in Angstrom
            #print len(q), len(data), len(ff)
            ax.plot(q, data/R**2*(re*ff)**2*1.e5, color=Rlist_colors[i_R], \
                    ls=ls[looptype], \
                    label=(r"$R=%d\mathrm{\AA}$"%R if looptype=='int' else ''))

    ax.set_xlim(-0.7, 0.7)
    ax.set_ylim(0., 1.)
    ax.set_xlabel(r"$q(220)$ $(\mathrm{\AA^{-1}})$")
    ax.set_ylabel(r"$q^4 R^{-2} d\sigma/d\Omega$ $(10^{-5}\mathrm{\AA^{-4}})$")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    fig.savefig("plots/slice_all_%d.pdf"%fit_ind, bbox_inches='tight')

plt.show()
