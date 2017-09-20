import numpy as np
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import helper
from settings import Rlist, a0
Rlist = np.array(Rlist)
A_atom = np.sqrt(2.)/4.*a0**2 # each atom occupies sqrt(2)/4*a0^2 area on loop plane

runs = [3, 8, 9, 7] 

fig = plt.figure(figsize=(5,4))
ax = fig.add_subplot(1,1,1)
ax.errorbar(-10, 0, 0, fmt='go', capsize=5, label='vac')
ax.errorbar(-10, 0, 0, fmt='bo', capsize=5, label='int')

fig1 = plt.figure(figsize=(5,4))
ax1 = fig1.add_subplot(1,1,1)
ax1.errorbar(-10, 0, 0, fmt='go', capsize=5, label='vac')
ax1.errorbar(-10, 0, 0, fmt='bo', capsize=5, label='int')

for run in runs:
    sample = helper.getparam("samples", run)
    dpa = helper.getdpa(sample)
    f = np.load("fit/%s_cs.npz"%sample)
    cs_int = f['cs_int']
    cs_int_err = f['cs_int_err']
    cs_vac = f['cs_vac']
    cs_vac_err = f['cs_vac_err']

    tot_int = np.sum(Rlist**2*np.pi/A_atom*cs_int)
    tot_int_err = np.sum((Rlist**2*np.pi/A_atom*cs_int_err)**2)**0.5
    sum_cR2 = np.sum(Rlist**2*cs_int)
    sum_c = np.sum(cs_int)
    R_ave_int = np.sqrt(1.*sum_cR2/sum_c)
    R_ave_int_err = 1./2*R_ave_int*np.sum(((Rlist**2/sum_cR2-1./sum_c)*cs_int_err)**2)**0.5

    tot_vac = np.sum(Rlist**2*np.pi/A_atom*cs_vac)
    tot_vac_err = np.sum((Rlist**2*np.pi/A_atom*cs_vac_err)**2)**0.5
    sum_cR2 = np.sum(Rlist**2*cs_vac)
    sum_c = np.sum(cs_vac)
    R_ave_vac = np.sqrt(1.*sum_cR2/sum_c)
    R_ave_vac_err = 1./2*R_ave_vac*np.sum(((Rlist**2/sum_cR2-1./sum_c)*cs_vac_err)**2)**0.5

    ax.errorbar(x=dpa, y=tot_int, yerr=tot_int_err, fmt='bo', \
                capsize=5)
    ax.errorbar(x=dpa, y=tot_vac, yerr=tot_vac_err, fmt='go', \
                capsize=5)

    ax1.errorbar(x=dpa, y=R_ave_int, yerr=R_ave_int_err, fmt='bo', \
                capsize=5)
    ax1.errorbar(x=dpa, y=R_ave_vac, yerr=R_ave_vac_err, fmt='go', \
                capsize=5)

ax.set_xlim(0., 6.)
ax.set_ylim(0., 1.6e-3)
ax.set_xlabel("DPA")
ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax.set_ylabel(r"Total defect density (atom$^{-1}$)")
ax.legend()
#ax.set_title("Defect density vs DPA")
fig.savefig("plots/def_vs_dpa.pdf", bbox_inches='tight')

ax1.set_xlim(0., 6.)
ax1.set_ylim(0., 25.)
ax1.set_xlabel("DPA")
ax1.set_ylabel(r"Average loop radius ($\mathrm{\AA}$)")
ax1.legend()
#ax.set_title("Defect density vs DPA")
fig1.savefig("plots/R_ave.pdf", bbox_inches='tight')

plt.show()
