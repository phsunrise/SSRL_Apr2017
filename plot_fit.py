import numpy as np
import scipy.optimize 
from settings import Rlist, Rlist_colors
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import helper
import os

runs = [3, 8, 9, 7] 

for run in runs:
    fdata = np.load("fit/run%d_data.npz"%(run))
    sample = helper.getparam("samples", run)

    q = fdata['qarray']
    data = fdata['data']
    err = fdata['err']
    C = np.load("fit/C.npy")
    q4I = q**4*data/C
    q4I_err = q**4*err/C

    fig = plt.figure(figsize=(15,12))
    ax = plt.subplot2grid((2,2), (0,0), colspan=2)
    plt.subplots_adjust(bottom=0.25)
    ax.errorbar(q, q4I, yerr=q4I_err, \
                ls='', color='r', marker='')
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0., 20.)

    ## range to be fitted
    fitrg = (-0.4, 0.4)
    indmin, indmax = np.searchsorted(q, fitrg)

    fit_ind = (2 if run == 7 else 0)
    q4I_th = []
    for looptype in ['int', 'vac']:
        for R in Rlist: 
            ## load theoretical data
            _data = np.load("fit/R%d_%d_%s.npz"%(R, fit_ind, looptype))['q4I']
            ## multiply by form factor
            _data *= np.load("fit/W_ff.npz")['ff']**2
            q4I_th.append(_data)
    q4I_th = np.array(q4I_th)
    print "reading coefficients from %s_cs.npz"%sample
    f = np.load("fit/%s_cs.npz"%sample)

    l_sum, = ax.plot(q, np.abs(np.concatenate((f['cs_int'], f['cs_vac']))).dot(q4I_th), 'b-')
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, np.abs(f['cs_vac'][i_R])*q4I_th[i_R+len(Rlist)], \
            color=Rlist_colors[i_R], \
            ls='--', label='%3d, vac, %.2e'%(R, f['cs_vac'][i_R]))
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, np.abs(f['cs_int'][i_R])*q4I_th[i_R], \
                color=Rlist_colors[i_R], \
                ls='-', label='%3d, int, %.2e'%(R, f['cs_int'][i_R]))

    ax.set_xlabel(r"$q$ $(\mathrm{\AA^{-1}})$")
    ax.set_ylabel(r"$q^4 S$ ($\mathrm{electrons\cdot\AA^{-4}}$)")
    ax.set_title(sample)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    ## bar chart
    edges = [5.]
    for i in xrange(len(Rlist)-1):
        edges.append((Rlist[i]+Rlist[i+1])/2.)
    edges.append(Rlist[-1]*2.-edges[-1])
    edges = np.array(edges)
    barwidth = edges[1:]-edges[:-1]
    ## vacancies 
    barheight = f['cs_vac']/barwidth
    ax1 = plt.subplot2grid((2,2), (1,0))
    ax1.hist(Rlist, bins=edges, weights=barheight, \
             color='g', edgecolor='k', alpha=0.8, log=True)
    ax1.errorbar(Rlist, barheight, yerr=f['cs_vac_err']/barwidth, \
                 color='r', capsize=2, ls='none')
    ax1.set_xlabel(r"$R$ ($\mathrm{\AA}$)")
    ax1.set_title(r"Vacancy, total (%.1f$\pm$%.1f)e-4 atom$^{-1}$" % (\
                            f['tot_vac']*1.e4, f['tot_vac_err']*1.e4))
    ## interstitials 
    barheight = f['cs_int']/barwidth
    ax2 = plt.subplot2grid((2,2), (1,1), sharex=ax1, sharey=ax1)
    ax2.hist(Rlist, bins=edges, weights=barheight, \
             color='b', edgecolor='k', alpha=0.8, log=True)
    ax2.errorbar(Rlist, barheight, yerr=f['cs_int_err']/barwidth, \
                 color='r', capsize=2, ls='none')
    ax2.set_xlabel(r"$R$ ($\mathrm{\AA}$)")
    ax2.set_ylabel(r"$\mathrm{d}c/\mathrm{d}R$ ($\mathrm{atom^{-1}\AA^{-1}}$)")
    ax2.set_title(r"Interstitial, total (%.1f$\pm$%.1f)e-4 atom$^{-1}$" % (\
                            f['tot_int']*1.e4, f['tot_int_err']*1.e4))
    #plt.subplots_adjust(wspace=0)

    ax1.set_xlim(0., 100.)
    ax1.set_ylim(1.e-9, 1.e-6)
    
    fig.savefig("plots/%s_fit.pdf"%sample, bbox_inches='tight')
    plt.show()
