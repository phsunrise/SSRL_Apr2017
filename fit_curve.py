import numpy as np
import scipy.optimize 
from settings import Rlist
import matplotlib.pyplot as plt
import helper

runs = [3, 8, 9, 7] 

for run in runs:
    fdata = np.load("fit/run%d_data.npz"%(run))
    sample = helper.getparam("samples", run)


    q = fdata['qarray']
    data = fdata['data']
    err = fdata['err']
    q4I = q**4*data
    q4I_err = q**4*err

    fig = plt.figure(figsize=(15,7.5))
    ax = fig.add_subplot(1,1,1)
    ax.errorbar(q, q4I, yerr=q4I_err, \
                ls='', color='r', marker='')
    #ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0., 0.2)

    ## range to be fitted
    fitrg = (-0.5, 0.5)
    indmin, indmax = np.searchsorted(q, fitrg)

    fit_ind = 0
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

    ax.plot(q, np.abs(res[0]).dot(q4I_th), 'b-')
    #ax.plot(q, np.abs(c0).dot(q4I_th), 'g-')
    for i_R, R in enumerate(Rlist):
        ax.plot(q, np.abs(res[0][i_R])*q4I_th[i_R], \
                ls=':', label='%3d, int, %.2e'%(R, res[0][i_R]))
    for i_R, R in enumerate(Rlist):
        ax.plot(q, np.abs(res[0][i_R+len(Rlist)])*q4I_th[i_R+len(Rlist)], \
                ls='--', label='%3d, vac, %.2e'%(R, res[0][i_R+len(Rlist)]))

    ax.set_xlabel(r"$q(\AA^{-1})$")
    ax.set_ylabel(r"$c$")
    ax.set_title(sample)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    fig.savefig("plots/%s_fit.pdf"%sample)
    plt.show()
