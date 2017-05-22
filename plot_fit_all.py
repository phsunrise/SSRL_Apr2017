import numpy as np
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import helper

runs = [3, 8, 9, 7] 

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.errorbar(-10, 0, 0, fmt='go', capsize=5, label='vacancies')
ax.errorbar(-10, 0, 0, fmt='bo', capsize=5, label='interstitials')

for run in runs:
    sample = helper.getparam("samples", run)
    dpa = helper.getdpa(sample)

    f = np.load("fit/%s_cs.npz"%sample)
    ax.errorbar(x=dpa, y=f['tot_vac'], yerr=f['tot_vac_err'], fmt='go', \
                capsize=5)
    ax.errorbar(x=dpa, y=f['tot_int'], yerr=f['tot_int_err'], fmt='bo', \
                capsize=5)

ax.set_xlim(0., 6.)
ax.set_xlabel("DPA")
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax.set_ylabel(r"total defect density (atom$^{-1}$)")
ax.legend()
ax.set_title("Defect density vs DPA")
plt.tight_layout()

plt.savefig("plots/def_vs_dpa.pdf")
plt.show()
