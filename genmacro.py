import os, sys
import numpy as np
from orimat import orimat_calc, angs_phifix
import ConfigParser 

## parsing config file
if len(sys.argv) < 2:
    config_filename = raw_input("Please enter config file name, enter q or ctrl+d to quit:\n")
else:
    config_filename = sys.argv[1]
Config = ConfigParser.ConfigParser()
Config.read(config_filename)

do_test = Config.getboolean("MODE", "do_test")
mode = Config.get("MODE", "mode")
use_angles = Config.getboolean("MODE", "use_angles")
scanpath = Config.get("PATHS", "scanpath")
imgpath = Config.get("PATHS", "imgpath")
checkfile = Config.get("PATHS", "checkfile")
newfile = Config.get("PATHS", "newfile")

peak = np.array(Config.get("SCAN PARAMS", "peak").split(',')).astype(float)
scandir_orig = np.array(Config.get("SCAN PARAMS", "scandir").split(',')).astype(float)
scandir_perp_orig = np.array(Config.get("SCAN PARAMS", "scandir_perp").split(',')).astype(float)
scanrange = Config.get("SCAN PARAMS", "scanrange").split(',')
scanrange_perp = Config.get("SCAN PARAMS", "scanrange_perp").split(',')
scanparams = [(float(scanrange[0]), float(scanrange[1]), int(scanrange[2])), \
              (float(scanrange_perp[0]), float(scanrange_perp[1]), int(scanrange_perp[2]))]

phi = float(Config.get("ANGLES", "phi"))
if use_angles:
    or0 = np.array(Config.get("ANGLES", "or0").split(',')).astype(float)
    hkl0 = np.array(Config.get("ANGLES", "hkl0").split(',')).astype(float)
    or1 = np.array(Config.get("ANGLES", "or1").split(',')).astype(float)
    hkl1 = np.array(Config.get("ANGLES", "hkl1").split(',')).astype(float)
    orimat = orimat_calc(or0, hkl0, or1, hkl1)
## END parsing

if not do_test: # must read times from times.npy
    times = np.load("times.npy")
    if len(times) != scanparams[0][2]:
        print "Error: times.npy array length does not agree with scan steps"
        print "In non-test mode, scan times must be provided in times.npy"
        print "If haven't done so, run in test mode first! Exiting..."
        sys.exit(1)
else:
    if mode != "1d":
        print "Test mode... 1d scan only!"
        mode = "1d"
peak = np.array(peak)
scandir = np.array(scandir_orig)/np.linalg.norm(scandir_orig) 
scandir_perp = np.array(scandir_perp_orig)/np.linalg.norm(scandir_perp_orig)
macroname = "macro%s"%mode
if use_angles:
    macroname += "_ang"
else:
    macroname += "_hkl"
if do_test:
    macroname += "_test"
macroname += ".txt"

## print out parameters
print "Parameters:"
if do_test:
    print "Test mode"
    print "1d scan, exposure time = 1s"
else:
    print "%s scan" % mode
if use_angles:
    print "Using motor angles"
    print "Primary peak:"
    print "\th, k, l = %.3f, %.3f, %.3f" % (hkl0[0], hkl0[1], hkl0[2])
    print "\ttth = %.3f, th = %.3f, chi = %.3f, phi = %.3f" % (\
                or0[0], or0[1], or0[2], or0[3])
    print "Secondary peak:"
    print "\th, k, l = %.3f, %.3f, %.3f" % (hkl1[0], hkl1[1], hkl1[2])
    print "\ttth = %.3f, th = %.3f, chi = %.3f, phi = %.3f" % (\
                or1[0], or1[1], or1[2], or1[3])
else:
    print "Using hkl values"
print "\nPhifix mode, phi = %.3f" % phi
print "Peak:", peak
print "Scan direction:", scandir_orig
print "Perpendicular scan direction", scandir_perp_orig
if mode == "1d":
    print "From %.3f to %.3f in %d steps" % (\
            scanparams[0][0], scanparams[0][1], scanparams[0][2])
elif mode == "2d":
    print "Parallel: from %.3f to %.3f in %d steps" % (\
            scanparams[0][0], scanparams[0][1], scanparams[0][2])
    print "Perpendicular: from %.3f to %.3f in %d steps" % (\
            scanparams[1][0], scanparams[1][1], scanparams[1][2])
print "Path for scan parameter file:", scanpath
print "Path to save image:", imgpath
print "Macro for checking:", checkfile
print ""
val = raw_input("Parameters okay? ")
if not val in ['yes', 'y', 'Y']:
    print "Aborting..."
    sys.exit(1)

## print q range
a0 = 3.1648
a0_reciprocal = 2.*np.pi/a0
print "q range: from %f to %f" % (scanparams[0][0]*a0_reciprocal, \
                scanparams[0][1]*a0_reciprocal)

## write the macro
totaltime = 0.
with open(macroname, 'w') as f:
    ## setups
    f.write("camrefresh\n")
    f.write("qdo %s\n\n" % checkfile)
    f.write("phifix %.3f\n\n" % phi)
    f.write("newfile %s\n" % scanpath)
    f.write("pd savepath %s\n" % imgpath)
    f.write("pd save\n\n")
    f.write("# DO NOT CHANGE\n")
    f.write("pd stop; sauto on; pd_abs_on; boff\n\n")
    f.write("plotselect normlz\n\n")

    ## go to the corners of scan range to check if 
    ## can be reached by motors
    print "CHECK if the motors can reach the corners"
    f.write("### CHECK if the motors can reach the corners ###\n")
    f.write("abs ins 1111\n")
    if mode == "2d":
        corners = [\
            peak + scandir*scanparams[0][0] + scandir_perp*scanparams[1][0],\
            peak + scandir*scanparams[0][0] + scandir_perp*scanparams[1][1],\
            peak + scandir*scanparams[0][1] + scandir_perp*scanparams[1][0],\
            peak + scandir*scanparams[0][1] + scandir_perp*scanparams[1][1]]
    elif mode == "1d":
        corners = [peak + scandir*scanparams[0][0],\
                   peak + scandir*scanparams[0][1]]
    else:
        print "Error: invalid mode! Exiting..."
        f.close()
        sys.exit(1)
        
    for i_corner, (h,k,l) in enumerate(corners):
        print "corner %d:" % (i_corner+1)
        if not use_angles:
            f.write("br %.3f %.3f %.3f\n" % (h,k,l))
            print "\th = %.3f, k = %.3f, l = %.3f" % (h,k,l)
        else:
            tth, th, chi = angs_phifix(h, k, l, phi, orimat)
            f.write("mv tth %.3f; " % tth)
            f.write("mv th %.3f; " % th)
            f.write("mv chi %.3f\n" % chi)
            print "\ttth = %.3f, th = %.3f, chi = %.3f, phi = %.3f" % (tth, th, chi, phi)
    f.write("\n")

    ## write each step
    f.write("### BEGIN scan ###\n")
    if mode == "2d":
        yarray = np.linspace(*scanparams[1])
    elif mode == "1d":
        yarray = [0.]

    step = 0
    for i_xx, xx in enumerate(np.linspace(*scanparams[0])):
        for yy in yarray:  
            f.write("# step %d\n" % step)
            h, k, l = peak + scandir*xx + scandir_perp*yy 
            if do_test:
                t = 1
            else:
                t = times[i_xx] 
            if not use_angles:
                f.write("br %.3f %.3f %.3f\n" % (h, k, l))
            else:
                tth, th, chi = angs_phifix(h, k, l, phi, orimat)
                f.write("mv tth %.3f\n" % tth)
                f.write("mv th %.3f\n" % th)
                f.write("mv chi %.3f\n" % chi)
            f.write("ct -1e5\n")
            if not use_angles:
                f.write("hklscan %.3f %.3f %.3f %.3f %.3f %.3f 1 %.2f\n\n" % (\
                        h, h, k, k, l, l, t))
            else:
                f.write("ascan tth %.3f %.3f 1 %.2f\n\n" % (tth, tth, t*0.5))
            step += 1
            totaltime += t

    ## post-scan stuff       
    f.write("# DO NOT CHANGE\n")
    f.write("pd_abs_off\n\n")
    f.write("pd nosave\n")
    f.write("boff\n")
    f.write("pd start 1; sopen\n")
    f.write("newfile %s\n" % newfile)
    f.write("qdo %s\n" % checkfile)
    f.write("camrefresh\n\n")
    f.write("### END ###")

print "Total time: %d seconds, or %.2f minutes, or %.2f hours" % (\
            totaltime, totaltime/60., totaltime/3600.)
print "Macro saved to file %s" % macroname
