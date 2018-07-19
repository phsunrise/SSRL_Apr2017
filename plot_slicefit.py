import os
import numpy as np
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.rcParams['xtick.top'] = plt.rcParams['ytick.right'] = True
plt.ion()
from settings import A_atom, Rlist, R_edges, R_barwidth
from settings import slices
import helper

## Figure for raw data including all slices
fig, (axes1, axes2) = plt.subplots(2, 4, sharex=True, sharey=True, figsize=(15, 8))
## Figure for bar plot 
fig_bar, _ax = plt.subplots(nrows=4, ncols=2, \
                            sharey=True, figsize=(6,10))
axes_bar_vac = [_ax[0][0], _ax[1][0], _ax[2][0], _ax[3][0]]
axes_bar_int = [_ax[0][1], _ax[1][1], _ax[2][1], _ax[3][1]]
## Figure for total defect density
fig_tot, ax_tot = plt.subplots(1, 1, figsize=(5,4))
ax_tot.errorbar(-10, 0, 0, fmt='go', fillstyle='none', capsize=5, label='vac')
ax_tot.errorbar(-10, 0, 0, fmt='bs', capsize=5, label='int')
## Figure for average radius 
fig_R, ax_R = plt.subplots(1, 1, figsize=(5,4))
ax_R.errorbar(-10, 0, 0, fmt='go', fillstyle='none', capsize=5, label='vac')
ax_R.errorbar(-10, 0, 0, fmt='bs', capsize=5, label='int')

## File for output
f_table = open("fit_results.csv", 'w')
f_table.write("csum in 1/atom, tot in 1/atom, Ravg in Angstrom\n\n")
f_table.write("DPA\ttype\tcsum\t+\t-\ttot\t+\t-\tRavg\t+\t-\n")

runs = [3, 8, 9, 7]
for i_run, (run, ax1, ax2) in enumerate(zip(runs, axes1, axes2)):
    sample = helper.getparam('samples', run)
    dpa = helper.getdpa(sample)

    cs_int = np.zeros((len(slices), len(Rlist)))
    cs_vac = np.zeros((len(slices), len(Rlist)))
    cs_int_err = np.zeros((len(slices), len(Rlist)))
    cs_vac_err = np.zeros((len(slices), len(Rlist)))
    dcR2_int = np.zeros((len(slices), len(Rlist)))
    dcR2_vac = np.zeros((len(slices), len(Rlist)))
    tot_int = np.zeros(len(slices))
    tot_vac = np.zeros(len(slices))
    R_ave_int = np.zeros(len(slices))
    R_ave_vac = np.zeros(len(slices))
    R_ave_all = np.zeros(len(slices))

    i_s_ave = [] # indices to take the average
    for i_s, (yind, zind, qperp) in enumerate(slices):
        f = np.load("fit/run%d_slice_%d_cs.npz" % (run, i_s))
        cs_int[i_s] = f['cs_int']
        cs_vac[i_s] = f['cs_vac']
        cs_int_err[i_s] = f['cs_int_err']
        cs_vac_err[i_s] = f['cs_vac_err']
        ## convert to R^2*dc/dR
        dcR2_int[i_s] = cs_int[i_s] * Rlist**2 / R_barwidth
        dcR2_vac[i_s] = cs_vac[i_s] * Rlist**2 / R_barwidth
        
        i_s_ave.append(i_s)
        if i_s in [1,2,3]:
            if qperp == 'qperp_0p010':
                ax1.plot(Rlist+1, dcR2_vac[i_s], 'ko', alpha=0.8) 
                ax2.plot(Rlist+1, dcR2_int[i_s], 'ko', alpha=0.8) 
            else:
                ax1.plot(Rlist+1, dcR2_vac[i_s], 'mo', alpha=0.8) 
                ax2.plot(Rlist+1, dcR2_int[i_s], 'mo', alpha=0.8) 
        else:
            ax1.plot(Rlist-1, dcR2_vac[i_s], 'go:', alpha=0.3) 
            ax2.plot(Rlist-1, dcR2_int[i_s], 'go:', alpha=0.3) 

        ## plot total concentration, where each loop is counted by number of atoms
        tot_int[i_s] = np.sum(Rlist**2*np.pi/A_atom*cs_int[i_s])
        sum_c_int = np.sum(cs_int[i_s])
        sum_cR2_int = np.sum(Rlist**2*cs_int[i_s])
        R_ave_int[i_s] = np.sqrt(1.*sum_cR2_int/sum_c_int)

        ## Calculation of the uncertainty in R_ave_int using error propagation
        #R_ave_int_err = np.sum((Rlist**2*sum_c_int - sum_cR2_int)**2 * cs_int_err[i_s]**2)**0.5 / (2.*R_ave_int[i_s]*sum_c_int**2)
        #print "%.2f +- %.2f" % (R_ave_int[i_s], R_ave_int_err)

        tot_vac[i_s] = np.sum(Rlist**2*np.pi/A_atom*cs_vac[i_s])
        sum_c_vac = np.sum(cs_vac[i_s])
        sum_cR2_vac = np.sum(Rlist**2*cs_vac[i_s])
        R_ave_vac[i_s] = np.sqrt(1.*sum_cR2_vac/sum_c_vac)

        R_ave_all[i_s] = np.sqrt(1.*(sum_cR2_int+sum_cR2_vac)/\
                                            (sum_c_int+sum_c_vac))

    cs_int_ave = cs_int[i_s_ave].mean(axis=0)
    cs_vac_ave = cs_vac[i_s_ave].mean(axis=0)
    dcR2_int_ave = dcR2_int[i_s_ave].mean(axis=0)
    dcR2_vac_ave = dcR2_vac[i_s_ave].mean(axis=0)

    cs_int_ave_err_p = cs_int.max(axis=0) - cs_int_ave
    cs_int_ave_err_n = cs_int_ave - cs_int.min(axis=0)
    cs_int_ave_err = cs_int[i_s_ave].std(axis=0)
    cs_vac_ave_err_p = cs_vac.max(axis=0) - cs_vac_ave
    cs_vac_ave_err_n = cs_vac_ave - cs_vac.min(axis=0)
    cs_vac_ave_err = cs_vac[i_s_ave].std(axis=0)
    dcR2_int_ave_err_p = dcR2_int.max(axis=0) - dcR2_int_ave
    dcR2_int_ave_err_n = dcR2_int_ave - dcR2_int.min(axis=0)
    dcR2_int_ave_err = dcR2_int[i_s_ave].std(axis=0)
    dcR2_vac_ave_err_p = dcR2_vac.max(axis=0) - dcR2_vac_ave
    dcR2_vac_ave_err_n = dcR2_vac_ave - dcR2_vac.min(axis=0)
    dcR2_vac_ave_err = dcR2_vac[i_s_ave].std(axis=0)

    ax1.errorbar(Rlist, dcR2_vac_ave, \
                 #yerr=[dcR2_vac_ave_err_n, dcR2_vac_ave_err_p], \
                 yerr = dcR2_vac_ave_err, \
                 fmt='ro', ecolor='r')
    ax2.errorbar(Rlist, dcR2_int_ave, \
                 #yerr=[dcR2_int_ave_err_n, dcR2_int_ave_err_p], \
                 yerr = dcR2_int_ave_err, \
                 fmt='ro', ecolor='r')

    ax2.set_yscale('log')
    ax2.set_ylim(3.e-7, 3.e-4)
    ax1.set_title("%s dpa, vac"%dpa)
    ax2.set_title("int")
    ax2.set_xlabel(r"$R$ $(\AA)$")

    ## bar plot
    axes_bar_vac[i_run].hist(Rlist, bins=R_edges, weights=dcR2_vac_ave, \
             color='g', edgecolor='k', alpha=0.8, log=True)
    axes_bar_vac[i_run].errorbar(Rlist, dcR2_vac_ave, \
                 #yerr=[dcR2_vac_ave_err_n, dcR2_vac_ave_err_p], \
                 yerr = dcR2_vac_ave_err, \
                 color='r', capsize=2, ls='none')
    axes_bar_int[i_run].hist(Rlist, bins=R_edges, weights=dcR2_int_ave, \
             color='b', edgecolor='k', alpha=0.8, log=True)
    axes_bar_int[i_run].errorbar(Rlist, dcR2_int_ave, \
                 #yerr=[dcR2_int_ave_err_n, dcR2_int_ave_err_p], \
                 yerr = dcR2_int_ave_err, \
                 color='r', capsize=2, ls='none')
    axes_bar_vac[i_run].set_xlim(100, 0)
    axes_bar_int[i_run].set_xlim(0, 100)

    axes_bar_vac[i_run].set_xticks([0, 20, 40, 60, 80, 100])
    axes_bar_int[i_run].set_xticks([0, 20, 40, 60, 80, 100])
    if i_run != 3:
        axes_bar_vac[i_run].set_xticklabels([])
        axes_bar_int[i_run].set_xticklabels([])

    axes_bar_vac[i_run].set_ylim(5.e-7, 2.e-4)
    axes_bar_vac[i_run].set_yticks([1e-6, 1e-5, 1e-4])
    axes_bar_vac[i_run].text(70, 8.e-5, str(dpa)+" DPA, vac")
    axes_bar_int[i_run].text(30, 8.e-5, str(dpa)+" DPA, int")

    ## total concentrations
    ## print total concentration, where each loop is counted once
    cs_int_sum = cs_int.sum(axis=1)
    cs_int_sum_ave = cs_int_sum[i_s_ave].mean()
    cs_int_sum_err = cs_int_sum[i_s_ave].std()
    cs_int_sum_err_p = cs_int_sum.max() - cs_int_sum_ave
    cs_int_sum_err_n = cs_int_sum_ave - cs_int_sum.min()
    cs_vac_sum = cs_vac.sum(axis=1)
    cs_vac_sum_ave = cs_vac_sum[i_s_ave].mean()
    cs_vac_sum_err = cs_vac_sum[i_s_ave].std()
    cs_vac_sum_err_p = cs_vac_sum.max() - cs_vac_sum_ave
    cs_vac_sum_err_n = cs_vac_sum_ave - cs_vac_sum.min()

    print "%.1f dpa: int = %.2e +%.1e / -%.1e / +-%.1e, vac = %.2e +%.1e / -%.1e / +-%.1e" % (dpa, \
        cs_int_sum_ave, cs_int_sum_err_p, cs_int_sum_err_n, cs_int_sum_err, \
        cs_vac_sum_ave, cs_vac_sum_err_p, cs_vac_sum_err_n, cs_vac_sum_err)

    ## total concentration, where each loop is counted by number of atoms
    tot_int_ave = tot_int[i_s_ave].mean()
    tot_int_err = tot_int[i_s_ave].std()
    tot_int_err_p = tot_int.max() - tot_int_ave
    tot_int_err_n = tot_int_ave - tot_int.min()
    tot_vac_ave = tot_vac[i_s_ave].mean()
    tot_vac_err = tot_vac[i_s_ave].std()
    tot_vac_err_p = tot_vac.max() - tot_vac_ave
    tot_vac_err_n = tot_vac_ave - tot_vac.min()
    print "Per atom: int = %.2e +%.1e / -%.1e / +-%.1e, vac = %.2e +%.1e / -%.1e / +-%.1e" % (\
             tot_int_ave, tot_int_err_p, tot_int_err_n, tot_int_err, \
             tot_vac_ave, tot_vac_err_p, tot_vac_err_n, tot_vac_err)

    ax_tot.errorbar(x=dpa-0.03, y=tot_int_ave*1.e3, \
                #yerr=[[tot_int_err_n*1.e3], [tot_int_err_p*1.e3]], \
                yerr = tot_int_err*1.e3, \
                fmt='bs', capsize=5)
    ax_tot.errorbar(x=dpa+0.03, y=tot_vac_ave*1.e3, \
                #yerr=[[tot_vac_err_n*1.e3], [tot_vac_err_p*1.e3]], \
                yerr = tot_vac_err*1.e3, \
                fmt='go', fillstyle='none', capsize=5)

    ## Average radius
    R_ave_int_ave = R_ave_int[i_s_ave].mean()
    R_ave_int_err = R_ave_int[i_s_ave].std()
    R_ave_int_err_p = R_ave_int.max() - R_ave_int_ave
    R_ave_int_err_n = R_ave_int_ave - R_ave_int.min()
    R_ave_vac_ave = R_ave_vac[i_s_ave].mean()
    R_ave_vac_err = R_ave_vac[i_s_ave].std()
    R_ave_vac_err_p = R_ave_vac.max() - R_ave_vac_ave
    R_ave_vac_err_n = R_ave_vac_ave - R_ave_vac.min()
    R_ave_all_ave = R_ave_all[i_s_ave].mean()
    R_ave_all_err = R_ave_all[i_s_ave].std()
    R_ave_all_err_p = R_ave_all.max() - R_ave_all_ave
    R_ave_all_err_n = R_ave_all_ave - R_ave_all.min()

    print "Average R: int = %.2f +%.2f / -%.2f / +-%.2f, vac = %.2f +%.2f / -%.2f / +-%.2f, all = %.2f +%.2f / -%.2f / +-%.2f" % (
                R_ave_int_ave, R_ave_int_err_p, R_ave_int_err_n, R_ave_int_err, \
                R_ave_vac_ave, R_ave_vac_err_p, R_ave_vac_err_n, R_ave_vac_err, \
                R_ave_all_ave, R_ave_all_err_p, R_ave_all_err_n, R_ave_all_err)

    ax_R.errorbar(x=dpa-0.03, y=R_ave_int_ave, \
                #yerr=[[R_ave_int_err_n], [R_ave_int_err_p]], \
                yerr=R_ave_int_err, \
                fmt='bs', capsize=5)
    ax_R.errorbar(x=dpa+0.03, y=R_ave_vac_ave, \
                #yerr=[[R_ave_vac_err_n], [R_ave_vac_err_p]], \
                yerr=R_ave_vac_err, \
                fmt='go', fillstyle='none', capsize=5)

    f_table.write("%.1f\tvac\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\n" % (\
                dpa, cs_vac_sum_ave, cs_vac_sum_err_p, cs_vac_sum_err_n,\
                tot_vac_ave, tot_vac_err_p, tot_vac_err_n,\
                R_ave_vac_ave, R_ave_vac_err_p, R_ave_vac_err_n))
    f_table.write("%.1f\tint\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\n" % (\
                dpa, cs_int_sum_ave, cs_int_sum_err_p, cs_int_sum_err_n,\
                tot_int_ave, tot_int_err_p, tot_int_err_n,\
                R_ave_int_ave, R_ave_int_err_p, R_ave_int_err_n))
    f_table.write("%.1f\tall\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\t%.2e\n" % (\
                dpa, (cs_int_sum_ave+cs_vac_sum_ave), \
                (cs_int_sum_err_p+cs_vac_sum_err_n), \
                (cs_int_sum_err_n+cs_vac_sum_err_n), \
                (tot_int_ave+tot_vac_ave), \
                (tot_int_err_p+tot_vac_err_p), \
                (tot_int_err_n+tot_vac_err_n), \
                R_ave_all_ave, R_ave_all_err_p, R_ave_all_err_n))

# final figure adjustments
# Bar plot
fig_bar.text(0.5, 0.05, r"Loop radius $R$ $(\mathrm{\AA})$", ha='center')
fig_bar.text(0.01, 0.5, \
             r"$\mathrm{d}c/\mathrm{d}R \cdot R^2$ ($\mathrm{atom^{-1}\AA}$)", \
             va='center', rotation='vertical')
fig_bar.savefig("plots/bar_plot_all_R2.pdf", bbox_inches='tight')

# total concentration plot
ax_tot.set_xlim(0., 6.)
ax_tot.set_ylim(0., 2.)
ax_tot.set_xlabel("DPA")
ax_tot.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax_tot.set_ylabel(r"Total defect density (per 1000 atoms)")
ax_tot.legend()
fig_tot.savefig("plots/def_vs_dpa.pdf", bbox_inches='tight')

ax_R.set_xlim(0., 6.)
ax_R.set_ylim(0., 40.)
ax_R.set_xlabel("DPA")
ax_R.set_ylabel(r"Average loop radius ($\mathrm{\AA}$)")
ax_R.legend()
fig_R.savefig("plots/R_ave.pdf", bbox_inches='tight')

f_table.close()
