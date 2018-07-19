import numpy as np
from settings import a0, hist_bincenters, hist_binedges, a0_reciprocal
from settings import Rlist, Rlist_colors, R_edges, R_barwidth
from settings import slices
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.rcParams['xtick.top'] = plt.rcParams['ytick.right'] = True
plt.ion()
import helper
import os

runs = [3, 8, 9, 7] 
shapes = ['o', 'x', 's', '>']
q = hist_bincenters[0][:1620].reshape(162, 10).mean(axis=1) * a0_reciprocal
Rlist2 = np.concatenate((Rlist, Rlist))**2
n_R = len(Rlist)

## here to calculate the factor that converts intensity to electron units
## the factor is: (atom number density)/sin(th)*(re/R)^2 * L
##                      * (detector pixel area)
##                 = [rho/(183.84u)*(re/R)^2*A_pix] * [L/sin(th)]
##                 = [A1] * [A2]
## L is the depth considering ion bombardment depth and attenuation length
## A1 is th-independent, A2 is th-dependent
## For W, rho = 19.3 g/cm^3, mu/rho = 96.91 cm^2/g at 10keV, so mu = 0.1870 um^-1
## re = 2.8179 fm, R = 1.121 m
A1 = 1.1819e-14 # um^-1, coefficient before L/sin(th)

## see dpa.py for calculation of A2
A2 = np.load("fit/A2.npy")

P0 = 1.247e12 # incoming flux, cps
airT = 0.50077 # air transmission from sample to detector
C = A1*A2 * P0 * airT
## diffuse scattering should be S_diff = I_diff / C

## range to be fitted
fitrg = (-0.7, 0.7)
indmin, indmax = np.searchsorted(q, fitrg)
q = q[indmin:indmax]
C = C[indmin:indmax]
np.save("fit/q.npy", q)
np.save("fit/C.npy", C)

## load run 4 data to estimate error
intensities0 = np.zeros((len(slices), indmax-indmin))
for i_s, (yind, zind, qperp) in enumerate(slices):
    intensities0[i_s] = np.load("fit/run4_slice_%s.npy"%(i_s))
intensities_err = (intensities0.max(axis=0) - intensities0.min(axis=0))*0.5

fig, ax = plt.subplots(1, 1, figsize=(10, 3.5))
for i_run, run in enumerate(runs):
    sample = helper.getparam('samples', run)
    data = []
    data_err = []
    data_fit = []
    for i_s, (yind, zind, qperp) in enumerate(slices):
        if qperp != 'qperp_0p010': continue

        print "slice %d, yind = %d, zind = %d, %s" % (i_s, yind, zind, qperp)
        ## load theoretical data
        theory_dir = "fit/%s/" % qperp
        q4I_th = []
        for looptype in ['int', 'vac']:
            for R in Rlist: 
                ## load theoretical data
                _data = np.load(theory_dir+"R%d_0_%s.npz"%(R, looptype))['q4I']
                ## multiply by form factor
                ff = np.load("fit/W_ff.npz")['ff']
                _data *= ff**2
                q4I_th.append(_data)

        q4I_th = np.array(q4I_th)[:, indmin:indmax]

        filename_data = "fit/run%d_slice_%s.npy"%(run, i_s)
        filename_cs = "fit/run%d_slice_%s_cs.npz"%(run, i_s)
        intensities = np.load(filename_data)
        sample = helper.getparam("samples", run)

        q4I = q**4 * intensities / C
        q4I_err = q**4 * intensities_err / C

        #ax.errorbar(q, q4I, yerr=q4I_err, \
        #            ls='', color='r', marker='')
        data.append(q4I)
        data_err.append(q4I_err)

        # initial coefficients
        _f = np.load(filename_cs)
        cs = np.concatenate((_f['cs_int'], _f['cs_vac']))
        cR2 = cs * Rlist2

        #l_sum, = ax.plot(q, cs.dot(q4I_th), 'b-')
        data_fit.append(cs.dot(q4I_th))


    re = 2.8179e-5 # electron radius in Angstrom
    coeff = re**2 * 1.e9
    data = np.array(data) * coeff
    data_err = np.array(data_err).max(axis=0) * coeff
    #data_err *= 0
    #data_err = (data_err**2 + (0.5*(data.max(axis=0) - data.min(axis=0)) * coeff)**2)**0.5
    data_fit = np.array(data_fit) * coeff

    ax.errorbar(q[::2], data.mean(axis=0)[::2], yerr=data_err[::2], \
                c=Rlist_colors[i_run], marker=shapes[i_run], \
                markersize=6, markerfacecolor='none', ls='', \
                label=sample)
    ax.plot(q[::2], data_fit.mean(axis=0)[::2], c=Rlist_colors[i_run])

ax.set_xlim(-0.7, 0.7)
ax.set_ylim(0., 10.)
ax.set_xlabel(r"$q(220)$ $(\mathrm{\AA^{-1}})$")
ax.set_ylabel(r"$q^4 d\sigma/d\Omega$ $(10^{-9}\mathrm{\AA^{-2}})$")
ax.legend()
fig.savefig("plots/data_with_fit_all.pdf", bbox_inches='tight')
