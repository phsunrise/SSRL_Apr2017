import numpy as np

a0 = 3.1648
a0_reciprocal = 2.*np.pi/a0

plot_dir = "/home/phsun/Apr2017/plots/"
imshape = (195, 487)
centralpix = (130, 252)
R_det = 1.121 # detector distance in m
pixsize = 172.e-6 # pixel size in m
ar = [60, 192, 148, 348] # active region on the detector, due to slit
#ar = [110, 151, 232, 273] # active region on the detector, due to slit

### three directions
e0 = np.array([1.,1.,0.])/np.sqrt(2.)
e1 = np.array([0.,0.,1.])/np.sqrt(1.)
e2 = np.array([1.,-1.,0.])/np.sqrt(2.)
e_mat = np.array([e0, e1, e2]).T

### hkl histogramming information 
hist_range = [(-0.405, 0.405, 1621), # [110] # min, max, steps
              (-0.035, 0.035, 141),  # [001]
              (-0.035, 0.035, 141)]  # [1-10]
hist_bincenters = []
hist_binedges = []
hist_binwidths = []
for i in xrange(3):
    _min, _max, _n = hist_range[i]
    _d = (_max - _min) * 1. / (_n-1)
    hist_bincenters.append(np.linspace(_min, _max, _n))
    hist_binedges.append(np.linspace(_min-_d/2., _max+_d/2., _n+1))
    hist_binwidths.append(_d)

# calibration scans
tthscan_filename = "calscan_tth_1_scan2"
gamscan_filename = "calscan_gam_1_scan1"
