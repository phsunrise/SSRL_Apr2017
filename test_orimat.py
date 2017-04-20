import numpy as np
import helper
from orimat import angs_phifix

run = 3
orimat = np.load("orimats/%s.npy"%(helper.getparam("orimats", run)))
print helper.getparam("orimats", run)
print angs_phifix(2, 2, 0.025, 0., orimat)
