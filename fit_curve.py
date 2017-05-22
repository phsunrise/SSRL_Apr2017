import numpy as np
import scipy.optimize 
from settings import Rlist, Rlist_colors, a0
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import helper
from matplotlib.widgets import Slider, Button
import os

runs = [3, 8, 9, 7] 

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
np.save("fit/C.npy", C)

for run in runs:
    fdata = np.load("fit/run%d_data.npz"%(run))
    sample = helper.getparam("samples", run)

    q = fdata['qarray']
    data = fdata['data']
    err = fdata['err']
    q4I = q**4*data/C
    q4I_err = q**4*err/C

    fig, ax = plt.subplots(1, 1, figsize=(15,7))
    plt.subplots_adjust(bottom=0.25)
    ax.errorbar(q, q4I, yerr=q4I_err, \
                ls='', color='r', marker='')
    ax.set_xlim(-0.7, 0.7)
    ax.set_ylim(0., 20.)

    ## range to be fitted
    fitrg = (-0.5, 0.5)
    indmin, indmax = np.searchsorted(q, fitrg)

    fit_ind = (2 if run == 7 else 0)
    q4I_th = []
    c0 = []
    for looptype in ['int', 'vac']:
        for R in Rlist: 
            ## load theoretical data
            _data = np.load("fit/R%d_%d_%s.npz"%(R, fit_ind, looptype))['q4I']
            ## multiply by form factor
            _data *= np.load("fit/W_ff.npz")['ff']**2
            q4I_th.append(_data)
            c0.append(10./np.max(_data[indmin:indmax]))
    q4I_th = np.array(q4I_th)
    c0 = np.array(c0)
    #if os.path.isfile("%s_cs.npy"%sample):
    #    print "reading initial coefficients from %s_cs.npy"%sample
    #    c0 = np.load("%s_cs.npy"%sample)[0]
    #c0 = np.array(c0)**0.5
    ## the curve fitting procedure is as follows:
    ## for an array c = [c5_int, c10_int, ..., c50_int, c5_vac, ..., c50_vac],
    ## calculate the theoretical q4I values, then calculate the diffrence from
    ## actual data, sum the squares weighted by 1/err^2
    q = q[indmin:indmax]
    q4I = q4I[indmin:indmax]
    q4I_err = q4I_err[indmin:indmax]
    q4I_th = q4I_th[:, indmin:indmax]
    def difsq(ind, *c):
        return np.abs(c).dot(q4I_th[:,ind])

    bounds = (-2.e-2, 2.e-2)
    res = scipy.optimize.curve_fit(difsq, np.arange(len(q4I)), q4I, \
                    p0=c0, sigma=q4I_err, bounds=bounds)
    for i in xrange(len(res[0])):
        print res[0][i], np.sqrt(res[1][i,i])
    print res[1]
    print "int:"
    for i_R, R in enumerate(Rlist):
        print "R = %3d:"%R, abs(res[0][i_R])
    print "vac:"
    for i_R, R in enumerate(Rlist):
        print "R = %3d:"%R, abs(res[0][i_R+len(Rlist)])

    l_sum, = ax.plot(q, np.abs(res[0]).dot(q4I_th), 'b-')
    #ax.plot(q, np.abs(c0).dot(q4I_th), 'g-')
    lines = []
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, np.abs(res[0][i_R])*q4I_th[i_R], \
                color=Rlist_colors[i_R], \
                ls=':', label='%3d, int, %.2e'%(R, abs(res[0][i_R])))
        lines.append(l)
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, np.abs(res[0][i_R+len(Rlist)])*q4I_th[i_R+len(Rlist)], \
            color=Rlist_colors[i_R], \
            ls='--', label='%3d, vac, %.2e'%(R, abs(res[0][i_R+len(Rlist)])))
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
        sliders.append(Slider(slider_axes[-1], "%d"%R, 0.0, 5.e-4/R**2, \
                       valinit=abs(res[0][i_R])))
    for i_R, R in enumerate(Rlist):
        slider_axes.append(plt.axes([0.45, 0.02+i_R*0.02, 0.3, 0.01], \
                           facecolor=axcolor))
        sliders.append(Slider(slider_axes[-1], "%d"%R, 0.0, 5.e-4/R**2, \
                       valinit=abs(res[0][i_R+len(Rlist)])))
    
    cs = abs(res[0][:])
    np.abs(res[0]).dot(q4I_th)
    def update(val):
        for i_R, R in enumerate(Rlist):
            cs[i_R] = sliders[i_R].val
            lines[i_R].set_ydata(cs[i_R]*q4I_th[i_R])
            cs[i_R+len(Rlist)] = sliders[i_R+len(Rlist)].val
            lines[i_R+len(Rlist)].set_ydata(sliders[i_R+len(Rlist)].val*q4I_th[i_R+len(Rlist)])
        l_sum.set_ydata(cs.dot(q4I_th))
        fig.canvas.draw_idle()
    for i_R, R in enumerate(Rlist):
        sliders[i_R].on_changed(update)
        sliders[i_R+len(Rlist)].on_changed(update)

    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    resetbutton = Button(resetax, 'Reset', color=axcolor, \
                         hovercolor='0.975')
    def reset(event):
        for i_R, R in enumerate(Rlist):
            sliders[i_R].reset()
            sliders[i_R+len(Rlist)].reset()
    resetbutton.on_clicked(reset)

    saveax = plt.axes([0.8, 0.07, 0.1, 0.04])
    savebutton = Button(saveax, 'Save', color=axcolor, \
                         hovercolor='0.975')
    def save(event):
        A_atom = np.sqrt(2.)/4.*a0**2 # each atom occupies sqrt(2)/4*a0^2 area on loop plane
        cs_int = cs[:len(Rlist)]
        cs_vac = cs[len(Rlist):]
        cs_int_err = np.sqrt(np.diag(res[1]))[:len(Rlist)]
        cs_vac_err = np.sqrt(np.diag(res[1]))[len(Rlist):]
        tot_int = np.sum(np.array(Rlist)**2*np.pi/A_atom*cs_int)
        tot_int_err = np.sum((np.array(Rlist)**2*np.pi/A_atom*cs_int_err)**2)**0.5
        tot_vac = np.sum(np.array(Rlist)**2*np.pi/A_atom*cs_vac)
        tot_vac_err = np.sum((np.array(Rlist)**2*np.pi/A_atom*cs_vac_err)**2)**0.5
        np.savez("fit/%s_cs.npz"%sample, cs_int=cs_int, cs_vac=cs_vac, cs_int_err=cs_int_err,\
                 cs_vac_err=cs_vac_err, tot_int=tot_int, tot_int_err=tot_int_err, tot_vac=tot_vac,\
                 tot_vac_err=tot_vac_err)
        print "saved to %s_cs.npz"%sample
    savebutton.on_clicked(save)

    fig.savefig("plots/%s_fit.pdf"%sample)
    plt.show()
