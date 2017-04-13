import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from settings import tthscan_filename, gamscan_filename

## tth scan
i_file = 0
maxinds = []
tths = []
while True:
    try:
        f = np.load("data_npz/%s_%04d.npz" % (tthscan_filename, i_file))
    except IOError:
        break
    data = f['data']
    tth = float(np.asscalar(f['tth']))
    maxinds.append(np.unravel_index(np.argmax(data), data.shape))
    tths.append(tth)

    i_file += 1

maxinds = np.array(maxinds)
tths = np.array(tths)

## select fit range
minind, maxind = np.searchsorted(tths, [66.5, 68.2])

## linear regression
plt.figure()
plt.plot(tths, maxinds[:,1], 'ko')
slope, intercept, r_value, p_value, std_err = stats.linregress(\
            tths[minind:maxind+1], maxinds[minind:maxind+1, 1])
plt.plot(tths, tths*slope+intercept, 'r--', label=r"$k_x=%f$"%slope)

plt.plot(tths, maxinds[:,0], 'ko')
slope, intercept, r_value, p_value, std_err = stats.linregress(\
            tths[minind:maxind+1], maxinds[minind:maxind+1, 0])
plt.plot(tths, tths*slope+intercept, 'y--', label=r"$k_y=%f$"%slope)

plt.xlabel("tth (deg)")
plt.ylabel("index")
plt.title("tth calibration")
plt.legend()

plt.savefig("plots/cal_tth.pdf")
plt.show()

## gam scan
i_file = 0
maxinds = []
gams = []
while True:
    try:
        f = np.load("data_npz/%s_%04d.npz" % (gamscan_filename, i_file))
    except IOError:
        break
    data = f['data']
    gam = float(np.asscalar(f['gam']))
    maxinds.append(np.unravel_index(np.argmax(data), data.shape))
    gams.append(gam)

    i_file += 1

maxinds = np.array(maxinds)
gams = np.array(gams)

## select fit range
minind, maxind = np.searchsorted(gams, [-1.9, 1.4])

## linear regression
plt.plot(gams, maxinds[:,1], 'ko')
slope, intercept, r_value, p_value, std_err = stats.linregress(\
            gams[minind:maxind+1], maxinds[minind:maxind+1, 1])
plt.plot(gams, gams*slope+intercept, 'r--', label=r"$k_x=%f$"%slope)

plt.plot(gams, maxinds[:,0], 'ko')
slope, intercept, r_value, p_value, std_err = stats.linregress(\
            gams[minind:maxind+1], maxinds[minind:maxind+1, 0])
plt.plot(gams, gams*slope+intercept, 'y--', label=r"$k_y=%f$"%slope)

plt.xlabel("gam (deg)")
plt.ylabel("index")
plt.title("gam calibration, tth=%f deg"%float(np.asscalar(f['tth'])))
plt.legend()

plt.savefig("plots/cal_gam.pdf")
plt.show()
