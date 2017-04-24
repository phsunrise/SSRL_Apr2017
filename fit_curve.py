import numpy as np
import scipy.optimize 
from settings import Rlist, Rlist_colors
import matplotlib.pyplot as plt
plt.rc('font', family='serif', size=12)
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import helper
from matplotlib.widgets import Slider, Button
import os

runs = [3, 8, 9, 7] 

for run in runs:
    fdata = np.load("fit/run%d_data.npz"%(run))
    sample = helper.getparam("samples", run)


    q = fdata['qarray']
    data = fdata['data']
    err = fdata['err']
    q4I = q**4*data
    q4I_err = q**4*err

    fig, ax = plt.subplots(1, 1, figsize=(15,7))
    plt.subplots_adjust(bottom=0.25)
    ax.errorbar(q, q4I, yerr=q4I_err, \
                ls='', color='r', marker='')
    #ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0., 0.2)

    ## range to be fitted
    fitrg = (-0.6, 0.6)
    indmin, indmax = np.searchsorted(q, fitrg)

    fit_ind = 2
    q4I_th = []
    c0 = []
    for looptype in ['int', 'vac']:
        for R in Rlist: 
            ## load theoretical data
            _data = np.load("fit/R%d_%d_%s.npz"%(R, fit_ind, looptype))['q4I']
            q4I_th.append(_data)
            c0.append(0.1/np.max(_data[indmin:indmax]))
    q4I_th = np.array(q4I_th)
    c0 = np.array(c0)
    if os.path.isfile("%s_cs.npy"%sample):
        print "reading initial coefficients from %s_cs.npy"%sample
        c0 = np.load("%s_cs.npy"%sample)
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

    bounds = (0., 2.e-2)
    res = scipy.optimize.curve_fit(difsq, np.arange(len(q4I)), q4I, \
                    p0=c0, sigma=q4I_err, bounds=bounds)
    print "int:"
    for i_R, R in enumerate(Rlist):
        print "R = %3d:"%R, res[0][i_R]
    print "vac:"
    for i_R, R in enumerate(Rlist):
        print "R = %3d:"%R, res[0][i_R+len(Rlist)]

    l_sum, = ax.plot(q, np.abs(res[0]).dot(q4I_th), 'b-')
    #ax.plot(q, np.abs(c0).dot(q4I_th), 'g-')
    lines = []
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, np.abs(res[0][i_R])*q4I_th[i_R], \
                color=Rlist_colors[i_R], \
                ls=':', label='%3d, int, %.2e'%(R, res[0][i_R]))
        lines.append(l)
    for i_R, R in enumerate(Rlist):
        l, = ax.plot(q, np.abs(res[0][i_R+len(Rlist)])*q4I_th[i_R+len(Rlist)], \
            color=Rlist_colors[i_R], \
            ls='--', label='%3d, vac, %.2e'%(R, res[0][i_R+len(Rlist)]))
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
        sliders.append(Slider(slider_axes[-1], "%d"%R, 0.0, 0.01/R**2, \
                       valinit=res[0][i_R]))
    for i_R, R in enumerate(Rlist):
        slider_axes.append(plt.axes([0.45, 0.02+i_R*0.02, 0.3, 0.01], \
                           facecolor=axcolor))
        sliders.append(Slider(slider_axes[-1], "%d"%R, 0.0, 0.01/R**2, \
                       valinit=res[0][i_R+len(Rlist)]))
    
    cs = res[0][:]
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
        np.save("%s_cs.npy"%sample, cs)
        print "saved to %s_cs.npy"%sample
    savebutton.on_clicked(save)

    fig.savefig("plots/%s_fit.pdf"%sample)
    plt.show()
