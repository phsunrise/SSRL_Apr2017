import numpy as np
from settings import Rlist, Rlist_colors
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.ion()
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'

suffix = "qperp_0p010"
datadir = "fit/%s/" % suffix

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
            ff = ff[:1620].reshape(162, 10).mean(axis=1)
            re = 2.8179e-5 # electron radius in Angstrom
            #print len(q), len(data), len(ff)
            yy = data/R**2*(re*ff)**2*1.e5
            color = Rlist_colors[i_R]
            ax.plot(q, yy, color=color, \
                    ls=ls[looptype], \
                    label=(r"$R=%d\mathrm{\AA}$"%R if looptype=='int' else ''))
            
            ### annotate at the peak
            #if looptype == 'int':
            #    rg = [1.*np.pi/(2.*R), 3.*np.pi/(2.*R)]
            #elif looptype == 'vac':
            #    rg = [-3.*np.pi/(2.*R), -1.*np.pi/(2.*R)]
            #indmin, indmax = np.searchsorted(q, rg)
            #ind = np.argmax(yy[indmin:indmax]) + indmin
            #ax.annotate(r"$R=%d\mathrm{\AA}$,%s"%(R, looptype), \
            #            xy=(q[ind], yy[ind]), xycoords='data', \
            #            xytext=(q[ind]-0.1, yy[ind]+0.1), textcoords='data', \
            #            arrowprops=dict(arrowstyle="->", \
            #                facecolor=color, connectionstyle="arc3"), \
            #            color=color)


    ax.set_xlim(-0.7, 0.7)
    ax.set_ylim(0., 1.)
    ax.set_xlabel(r"$q(220)$ $(\mathrm{\AA^{-1}})$")
    ax.set_ylabel(r"$q^4 R^{-2} d\sigma/d\Omega$ $(10^{-5}\mathrm{\AA^{-4}})$")
    ax.tick_params(top='on', right='on')
    #box = ax.get_position()
    #ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    #ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    fig.savefig("plots/slice_all_%d_%s.pdf" % (fit_ind, suffix), \
                bbox_inches='tight')
    fig.savefig("plots/slice_all_%d_%s.eps" % (fit_ind, suffix), \
                bbox_inches='tight')
