import numpy as np
import scipy.optimize 
from settings import a0, hist_bincenters, hist_binedges, a0_reciprocal
from settings import Rlist, Rlist_colors, R_edges, R_barwidth
from settings import slices
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
plt.ioff()
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import helper
from matplotlib.widgets import Slider, Button
import os

#runs = [3, 8, 9, 7] 
run = 7 
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

for i_s, (yind, zind, qperp) in enumerate(slices):
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

    fig, ax = plt.subplots(1, 1, figsize=(15,7))
    plt.subplots_adjust(bottom=0.25)
    ax.errorbar(q, q4I, yerr=q4I_err, \
                ls='', color='r', marker='')
    ax.set_xlim(-0.7, 0.7)
    ax.set_ylim(0., 20.)

    # initial coefficients
    if os.path.isfile(filename_cs):
        print "reading initial coefficients from %s" % filename_cs
        _f = np.load(filename_cs)
        c_init = np.concatenate((_f['cs_int'], _f['cs_vac']))
        cR2_init = c_init * Rlist2
    else:
        cR2_init = np.ones(2*n_R)*1.e-8

    ## least-squares fitting procedure is as follows:
    ## for an array c = [c5_int, c10_int, ..., c50_int, c5_vac, ..., c50_vac],
    ## calculate the theoretical q4I values, then calculate the diffrence from
    ## actual data, sum the squares weighted by 1/err^2
    def func(cR2):
        c = np.abs(cR2) / Rlist2
        diff = np.abs(np.abs(c).dot(q4I_th) - q4I) / q4I_err
        # penalize "oscillating" concentrations
        c1 = cR2[:n_R]/Rlist**2/R_barwidth # interstitial
        c2 = cR2[n_R:]/Rlist**2/R_barwidth # vacancy
        inc1 = c1[1:n_R] - c1[0:n_R-1]
        inc2 = c2[1:n_R] - c2[0:n_R-1]
        signs1 = np.sign(inc1[0:n_R-2]*inc1[1:n_R-1])
        signs2 = np.sign(inc2[0:n_R-2]*inc2[1:n_R-1])
        ## signs[i] = 1 if c[i:i+3] is monotonic
        ##          = -1 if c[i:i+3] is not monotonic
        ## penalty if having more than one peak or valley
        ## the coefficient can be adjusted
        pen = 10. * max(np.sum(signs1<0)-1, 0)
        pen += 10. * max(np.sum(signs2<0)-1, 0)
        pen *= 0.
        ## also penalty if there are zeros
        pen += 100. * (np.sum(c1 <= 1.e-14) + np.sum(c2 <= 1.e-14))

        return diff + pen

    res0, cov, infodict, mesg, ier = scipy.optimize.leastsq(\
                func, cR2_init, full_output=True)
    ## res0 is c*R^2
    ## get covariance & error of coefficients
    s_sq = (infodict['fvec']**2).sum() / (len(infodict['fvec'])-len(res0))
    res0_err = np.diag(cov * s_sq) ** 0.5
    cs = np.abs(res0) / Rlist2
    cs_err = np.abs(res0_err) / Rlist2
    res = cs / np.concatenate((R_barwidth, R_barwidth))
    res_err = cs_err / np.concatenate((R_barwidth, R_barwidth))
    ## res is dc/dR

    print "int:"
    for i_R, R in enumerate(Rlist):
        print "R = %3d: c = %.2e, dc/dR = %.2e" % (\
                    R, cs[i_R], res[i_R])
    print "vac:"
    for i_R, R in enumerate(Rlist):
        print "R = %3d: c = %.2e, dc/dR = %.2e" % (\
                    R, cs[i_R+n_R], res[i_R+n_R])

    l_sum, = ax.plot(q, cs.dot(q4I_th), 'b-')
    lines = []
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, cs[i_R]*q4I_th[i_R], \
                color=Rlist_colors[i_R], \
                ls=':', label='%3d, int, %.2e'%(R, cs[i_R]))
        lines.append(l)
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, cs[i_R+n_R]*q4I_th[i_R+n_R], \
            color=Rlist_colors[i_R], \
            ls='--', label='%3d, vac, %.2e'%(R, cs[i_R+n_R]))
        lines.append(l)

    ax.set_xlabel(r"$q$ $(\AA^{-1})$")
    ax.set_ylabel(r"$c$")
    ax.set_title(sample)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    ## sliders
    axcolor = 'lightgoldenrodyellow'
    slider_axes = []
    sliders = []
    for i_R, R in enumerate(Rlist):
        slider_axes.append(plt.axes([0.05, 0.02+i_R*0.02, 0.3, 0.01], \
                           facecolor=axcolor))
        sliders.append(Slider(slider_axes[-1], "%d"%R, 0.0, 1.e-4/R**2, \
                       valinit=res[i_R]))
    for i_R, R in enumerate(Rlist):
        slider_axes.append(plt.axes([0.45, 0.02+i_R*0.02, 0.3, 0.01], \
                           facecolor=axcolor))
        sliders.append(Slider(slider_axes[-1], "%d"%R, 0.0, 1.e-4/R**2, \
                       valinit=res[i_R+n_R]))
    
    def update(val):
        for i_R, R in enumerate(Rlist):
            res[i_R] = sliders[i_R].val
            cs[i_R] = res[i_R] * R_barwidth[i_R]
            lines[i_R].set_ydata(cs[i_R]*q4I_th[i_R])
            res[i_R+n_R] = sliders[i_R+n_R].val
            cs[i_R+n_R] = res[i_R+n_R] * R_barwidth[i_R]
            lines[i_R+n_R].set_ydata(cs[i_R+n_R]*q4I_th[i_R+n_R])
        l_sum.set_ydata(cs.dot(q4I_th))
        fig.canvas.draw_idle()
    for i_R, R in enumerate(Rlist):
        sliders[i_R].on_changed(update)
        sliders[i_R+n_R].on_changed(update)

    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    resetbutton = Button(resetax, 'Reset', color=axcolor, \
                         hovercolor='0.975')
    def reset(event):
        for i_R, R in enumerate(Rlist):
            sliders[i_R].reset()
            sliders[i_R+n_R].reset()
    resetbutton.on_clicked(reset)

    saveax = plt.axes([0.8, 0.07, 0.1, 0.04])
    savebutton = Button(saveax, 'Save', color=axcolor, \
                         hovercolor='0.975')
    def save(event):
        cs_int = cs[:n_R]
        cs_vac = cs[n_R:]
        cs_int_err = cs_err[:n_R] 
        cs_vac_err = cs_err[n_R:]
        np.savez(filename_cs, cs_int=cs_int, cs_vac=cs_vac, \
                 cs_int_err=cs_int_err, cs_vac_err=cs_vac_err)
        print "saved to %s" % filename_cs
    savebutton.on_clicked(save)

    fitax = plt.axes([0.8, 0.115, 0.1, 0.04])
    fitbutton = Button(fitax, 'Fit', color=axcolor, \
                         hovercolor='0.975')
    def fit(event):
        global cs, cs_err, res, res_err
        res0, cov, infodict, mesg, ier = scipy.optimize.leastsq(\
                    func, res, full_output=True)
        ## res0 is c*R^2
        ## get covariance & error of coefficients
        s_sq = (infodict['fvec']**2).sum() / (len(infodict['fvec'])-len(res0))
        res0_err = np.diag(cov * s_sq) ** 0.5
        cs = np.abs(res0) / Rlist2
        cs_err = np.abs(res0_err) / Rlist2
        res = cs / np.concatenate((R_barwidth, R_barwidth))
        res_err = cs_err / np.concatenate((R_barwidth, R_barwidth))
        ## res is dc/dR
        ## update sliders
        for i_R, R in enumerate(Rlist):
            lines[i_R].set_ydata(cs[i_R]*q4I_th[i_R])
            sliders[i_R].set_val(res[i_R])
            lines[i_R+n_R].set_ydata(cs[i_R+n_R]*q4I_th[i_R+n_R])
            sliders[i_R+n_R].set_val(res[i_R+n_R])
        l_sum.set_ydata(cs.dot(q4I_th))
        fig.canvas.draw_idle()
        print "Fitting done"
    fitbutton.on_clicked(fit)

    fig.savefig("plots/%s_fit.pdf"%sample)
    plt.show()
