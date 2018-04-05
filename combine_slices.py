import numpy as np
import helper
import matplotlib.pyplot as plt

plt.ion()
runs = [3, 8, 9, 7] 
inds = [0, 7] # [0,7] for -/+0.020 rlu, [1,6] for -/+0.015 rlu, 
              # [2,5] for -/+0.010 rlu, [3,4] for -/+0.005 rlu
suffix = "qperp_0p020"

colors =['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7,7), \
                               sharex=True, sharey=True)
for i_r, run in enumerate(runs):
    sample = helper.getparam("samples", run)
    datas = []
    errs = []
    for ind in inds:
        fdata0 = np.load("fit/run4_data_%d.npz"%(ind))
        qarray, data0, err0 = fdata0['qarray'], fdata0['data'], fdata0['err']
        fdata = np.load("fit/run%d_data_%d.npz"%(run, ind))
        data, err = fdata['data'], fdata['err']
        fmt = ('-' if ind==0 else ':')
        ax1.errorbar(qarray, qarray**4*(data-data0), \
                    yerr=qarray**4*(err**2+err0**2)**0.5, fmt=fmt, lw=0.8, \
                    color=colors[i_r], label="%s, %d"%(sample, ind))
        datas.append(data-data0)
        errs.append((err**2+err0**2)**0.5)
    
    ## plot average over two indices
    datas = np.array(datas)
    data = datas.mean(axis=0)
    errs = np.array(errs)
    err = ((np.abs(datas[0]-datas[1])/2.)**2 + (errs**2).sum(axis=0))**0.5
    ax2.errorbar(qarray, qarray**4*data, yerr=qarray**4*err, \
                 fmt='-', lw=0.8, color=colors[i_r], \
                 label="%s"%(sample))

    ## save data
    np.savez("fit/run%d_data_%s.npz"%(run, suffix), \
             qarray=qarray, data=data, err=err)

ax2.set_xlim(-0.7, 0.7)
ax2.set_ylim(0., 0.2)
ax1.legend()
ax2.legend()
ax2.set_xlabel(r"$q$ $(\AA^{-1})$")
ax1.set_ylabel(r"$q^4 I$")
ax2.set_ylabel(r"$q^4 I$")

fig.savefig("plots/q4I_0p020.png")
