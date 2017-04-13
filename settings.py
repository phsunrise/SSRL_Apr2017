import numpy as np

a0 = 3.1648
a0_reciprocal = 2.*np.pi/a0

plot_dir = "/scratch/users/phsun/SSRL_Nov16/plots/"
imshape = (195, 487)
centralpix = (130, 252)
ar = [23, 193, 205, 296] # active region on the detector, due to slit

### hkl histogramming information 
#bins = (201, 201, 201)
#hcoords = np.linspace(1.75, 2.25, bins[0])
#kcoords = np.linspace(1.75, 2.25, bins[1])
#lcoords = np.linspace(-0.25, 0.25, bins[2])
#histrange = ((hcoords[0]*1.5-hcoords[1]*0.5, hcoords[-1]*1.5-hcoords[-2]*0.5),
#             (kcoords[0]*1.5-kcoords[1]*0.5, kcoords[-1]*1.5-kcoords[-2]*0.5),
#             (lcoords[0]*1.5-lcoords[1]*0.5, lcoords[-1]*1.5-lcoords[-2]*0.5))

# calibration scans
tthscan_filename = "calscan_tth_1_scan2"
gamscan_filename = "calscan_gam_1_scan1"
