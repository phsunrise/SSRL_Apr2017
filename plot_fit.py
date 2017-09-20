import numpy as np
import scipy.optimize 
from settings import Rlist, Rlist_colors
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
#from matplotlib.ticker import LogLocator 
import helper
import os

plot_individual = False
plot_R2 = False 

runs = [3, 8, 9, 7]

## all curves in one figure
fig_curve = plt.figure(figsize=(10.5,3.5))
ax_curve = fig_curve.add_subplot(1,1,1)
## all barplots
fig_bar, _ax = plt.subplots(nrows=4, ncols=2, \
                            sharey=True, figsize=(6,10))
axes_bar_vac = [_ax[0][0], _ax[1][0], _ax[2][0], _ax[3][0]]
axes_bar_int = [_ax[0][1], _ax[1][1], _ax[2][1], _ax[3][1]]
fig_bar.subplots_adjust(hspace=0, wspace=0)
## defect distribution combined, line plot
fig_all = plt.figure(figsize=(10,5))
ax_all = fig_all.add_subplot(1,1,1)

re = 2.8179e-5 # electron radius in Angstrom
for i_run, run in enumerate(runs):
    fdata = np.load("fit/run%d_data.npz"%(run))
    sample = helper.getparam("samples", run)
    print "Plotting sample %s..." % (sample)
    dpa = helper.getdpa(sample)

    q = fdata['qarray']
    data = fdata['data']
    err = fdata['err']
    C = np.load("fit/C.npy")
    q4I = q**4*data/C
    q4I_err = q**4*err/C

    ## range to be fitted
    fitrg = (-0.7, 0.7)
    indmin, indmax = np.searchsorted(q, fitrg)

    ax_curve.errorbar(q, q4I*re**2*1.e9, yerr=q4I_err*re**2*1.e9, \
                ls='', color='C%d'%i_run, marker='o', \
                markerfacecolor='none', label=str(dpa)+" DPA")
    if plot_individual:
        fig = plt.figure(figsize=(15,10))
        ax = plt.subplot2grid((2,2), (0,0), colspan=2)
        plt.subplots_adjust(bottom=0.25)
        ax.errorbar(q, q4I, yerr=q4I_err, \
                    ls='', color='r', marker='')
        ax.set_xlim(fitrg[0], fitrg[1])
        ax.set_ylim(0., 15.)

    #fit_ind = (2 if run == 7 else 0)
    fit_ind = 0
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

    ax_curve.plot(q, \
        np.abs(np.concatenate((f['cs_int'], f['cs_vac']))).dot(q4I_th)*re**2*1.e9, \
        ls='-', color='C%d'%i_run)
    if plot_individual:
        l_sum, = ax.plot(q, \
            np.abs(np.concatenate((f['cs_int'], f['cs_vac']))).dot(q4I_th), \
            'b-')
        for i_R, R in enumerate(Rlist):
            l, = ax.plot(q, np.abs(f['cs_vac'][i_R])*q4I_th[i_R+len(Rlist)], \
                color=Rlist_colors[i_R], \
                ls='--', label='%3d, vac, %.2e'%(R, f['cs_vac'][i_R]))
        for i_R, R in enumerate(Rlist):
            l, = ax.plot(q, np.abs(f['cs_int'][i_R])*q4I_th[i_R], \
                    color=Rlist_colors[i_R], \
                    ls='-', label='%3d, int, %.2e'%(R, f['cs_int'][i_R]))

        ax.set_xlabel(r"$q$ $(\mathrm{\AA^{-1}})$")
        ax.set_ylabel(r"$q^4 S$ $(\mathrm{electrons\cdot\AA^{-4}})$")
        ax.set_title(sample)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    ## bar chart
    edges = [2.5]
    for i in xrange(len(Rlist)-1):
        edges.append((Rlist[i]+Rlist[i+1])/2.)
    edges.append(Rlist[-1]*2.-edges[-1])
    edges = np.array(edges)
    barwidth = edges[1:]-edges[:-1]
    ## vacancies 
    if plot_R2:
        barheight = f['cs_vac']/barwidth*Rlist**2
        barerr = f['cs_vac_err']/barwidth*Rlist**2
    else:
        barheight = f['cs_vac']/barwidth
        barerr = f['cs_vac_err']/barwidth
    print zip(barheight, barerr)
    barerr_hi = (10.**(0.43429*barerr/barheight)-1.)*barheight
    barerr_lo = (1.-10.**(-0.43429*barerr/barheight))*barheight
    if plot_individual:
        ax1 = plt.subplot2grid((2,2), (1,0))
        ax1.hist(Rlist, bins=edges, weights=barheight, \
                 color='g', edgecolor='k', alpha=0.8, log=True)
        ax1.errorbar(Rlist, barheight, yerr=f['cs_vac_err']/barwidth, \
                     color='r', capsize=2, ls='none')
        ax1.set_xlim(100., 0.)
        ax1.set_xlabel(r"$R$ ($\mathrm{\AA}$)")
        ax1.set_title(r"Vacancy, total (%.1f$\pm$%.1f)e-4 atom$^{-1}$" % (\
                                f['tot_vac']*1.e4, f['tot_vac_err']*1.e4))

    axes_bar_vac[i_run].hist(Rlist, bins=edges, weights=barheight, \
             color='g', edgecolor='k', alpha=0.8, log=True)
    axes_bar_vac[i_run].errorbar(Rlist, barheight, \
                 yerr=barerr, \
                 #yerr=[barerr_lo, barerr_hi], \
                 color='r', capsize=2, ls='none')

    ## interstitials 
    if plot_R2:
        barheight = f['cs_int']/barwidth*Rlist**2
        barerr = f['cs_int_err']/barwidth*Rlist**2
    else:
        barheight = f['cs_int']/barwidth
        barerr = f['cs_int_err']/barwidth
    barerr_hi = (10.**(0.43429*barerr/barheight)-1.)*barheight
    barerr_lo = (1.-10.**(-0.43429*barerr/barheight))*barheight
    if plot_individual:
        ax2 = plt.subplot2grid((2,2), (1,1), sharex=ax1, sharey=ax1)
        ax2.hist(Rlist, bins=edges, weights=barheight, \
                 color='b', edgecolor='k', alpha=0.8, log=True)
        ax2.errorbar(Rlist, barheight, yerr=f['cs_int_err']/barwidth, \
                     color='r', capsize=2, ls='none')
        ax2.set_xlim(0., 100.)
        ax2.set_xlabel(r"$R$ ($\mathrm{\AA}$)")
        ax2.set_ylabel(r"$\mathrm{d}c/\mathrm{d}R$ ($\mathrm{atom^{-1}\AA^{-1}}$)")
        ax2.set_title(r"Interstitial, total (%.1f$\pm$%.1f)e-4 atom$^{-1}$" % (\
                                f['tot_int']*1.e4, f['tot_int_err']*1.e4))
    #plt.subplots_adjust(wspace=0)
    axes_bar_int[i_run].hist(Rlist, bins=edges, weights=barheight, \
             color='b', edgecolor='k', alpha=0.8, log=True)
    axes_bar_int[i_run].errorbar(Rlist, barheight, \
                 yerr=barerr, \
                 #yerr=[barerr_lo, barerr_hi], \
                 color='r', capsize=2, ls='none')

    if plot_individual:
        ax1.set_xlim(0., 100.)
        ax1.set_ylim(1.e-9, 1.e-5)

        #plt.tight_layout()
        fig.savefig("plots/%s_fit.pdf"%sample, bbox_inches='tight')
        #plt.show()

    ## setting axes and ticks
    #axes_bar_vac[i_run].tick_params(axis=u'both', direction='in', \
    #                    top=True, right=True)
    #axes_bar_int[i_run].tick_params(axis=u'both', direction='in', \
    #                    top=True, right=True)
    axes_bar_vac[i_run].text(70, 2e-6, str(dpa)+" DPA, vac")
    axes_bar_int[i_run].text(30, 2e-6, str(dpa)+" DPA, int")

    axes_bar_vac[i_run].set_xlim(100, 0)
    axes_bar_int[i_run].set_xlim(0, 100)
    if i_run == 3:
        axes_bar_vac[i_run].set_xticks([0, 20, 40, 60, 80, 100])
        axes_bar_int[i_run].set_xticks([0, 20, 40, 60, 80, 100])
    else:
        axes_bar_vac[i_run].set_xticks([])
        axes_bar_int[i_run].set_xticks([])

    if plot_R2:
        axes_bar_vac[i_run].set_ylim(1.e-7, 5.e-4)
    else:
        axes_bar_vac[i_run].set_ylim(1.e-10, 9.e-6)
        axes_bar_vac[i_run].set_yticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6])
    axes_bar_vac[i_run].tick_params(axis='y', which='both', \
                                    direction='in', left='on', right='off')
    axes_bar_int[i_run].tick_params(axis='y', which='both', \
                                    direction='in', left='off', right='on')

ax_curve.set_xlim(fitrg[0], fitrg[1])
#ax_curve.set_xticks(np.linspace(fitrg[0], fitrg[1], 11))
ax_curve.set_ylim(0., 10.)
ax_curve.set_xlabel(r"$q(220)$ $(\mathrm{\AA^{-1}})$")
ax_curve.set_ylabel(r"$q^4 d\sigma/d\Omega$ $(10^{-9}\mathrm{\AA^{-2}})$")
ax_curve.legend()
fig_curve.savefig("plots/data_with_fit_all.pdf", bbox_inches='tight')

fig_bar.text(0.5, 0.06, r"Loop radius $R$ $(\mathrm{\AA})$", ha='center')
if plot_R2:
    fig_bar.text(0.01, 0.5, r"$\mathrm{d}c/\mathrm{d}R \cdot R^2$ ($\mathrm{atom^{-1}\AA}$)", \
                 va='center', rotation='vertical')
else:
    fig_bar.text(0.01, 0.5, r"$\mathrm{d}c/\mathrm{d}R$ ($\mathrm{atom^{-1}\AA}^{-1}$)", \
                 va='center', rotation='vertical')
fig_bar.savefig("plots/bar_plot_all.pdf", bbox_inches='tight')

plt.show()
